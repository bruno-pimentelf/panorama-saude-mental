import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np

# Carregar os dados
data = pd.read_csv('BaseGeral.csv')

# Título da aplicação
st.title('Panorama da Saúde Mental - Filtros e Cálculos')

# Adicionar logo do Cactus na sidebar
st.sidebar.image('logo_cactus.png', width=200)
st.sidebar.markdown("*by: Bruno Pimentel*")

# Seção de filtros
st.sidebar.header("Filtros de Respostas")

# Adicionar filtros para todas as colunas especificadas
filtros = {
    'religion': 'Religião',
    'gender': 'Gênero',
    'educational_level': 'Nível Educacional',
    'age': 'Faixa Etária',
    'family_income': 'Renda Familiar',
    'receive_bolsa_familia': 'Recebe Bolsa Família',
    'race': 'Raça',
    'ever_thought_you_should_stop_drinking': 'Já pensou que deveria parar de beber',
    'marital_status': 'Estado Civil',
    'gender_identity': 'Identidade de Gênero',
    'have_kids': 'Tem Filhos',
    'age_of_youngest_kid': 'Idade do Filho Mais Novo',
    'sexual_orientation': 'Orientação Sexual',
    'employed_or_looking_for_employment': 'Empregado ou Procurando Emprego',
    'employment': 'Emprego',
    'are_you_a_person_with_disability': 'Pessoa com Deficiência',
    'who_is_primarily_responsible_for_supporting_your_home': 'Responsável Principal pelo Sustento do Lar'
}

# Função para extrair questões e opções de colunas JSON
def get_json_questions_and_options(column):
    questions = {}
    for item in data[column].dropna():
        try:
            json_data = json.loads(item.replace("'", '"'))
            for question in json_data:
                label = question['label']
                value = question['value']
                if label not in questions:
                    questions[label] = set()
                questions[label].add(value)
        except:
            pass
    return {k: ['Todos'] + list(v) for k, v in questions.items()}

# Adicionar filtros para colunas JSON
json_columns = ['QSG12A', 'QSG12B', 'PHQ-9', 'during_last_weeks_how_many_times_you']
json_filters = {}
for column in json_columns:
    json_filters[column] = get_json_questions_and_options(column)

# Criar filtros dinâmicos
filtered_data = data.copy()
for col, label in filtros.items():
    options = ['Todos'] + list(data[col].unique())
    selected = st.sidebar.multiselect(label, options, default='Todos')
    if 'Todos' not in selected:
        filtered_data = filtered_data[filtered_data[col].isin(selected)]

# Adicionar filtros para colunas JSON
for column, questions in json_filters.items():
    st.sidebar.subheader(f"Questionário {column}")
    for question, options in questions.items():
        selected = st.sidebar.selectbox(question, options)
        if selected != 'Todos':
            filtered_data = filtered_data[filtered_data[column].apply(
                lambda x: any(item['label'] == question and item['value'] == selected 
                              for item in json.loads(x.replace("'", '"')))
            )]

# Função para calcular o ICASM de forma segura
def calcular_icasm_seguro(df):
    try:
        return (df['atlas_mh_index'] * df['weight']).sum() / df['weight'].sum()
    except ZeroDivisionError:
        return np.nan

# Função para exibir mensagem de erro de forma elegante
def exibir_erro(mensagem):
    st.error(f"Ops! Ocorreu um problema: {mensagem}")
    st.info("Tente ajustar seus filtros ou selecionar diferentes opções.")

# Cálculo da porcentagem ponderada e ICASM
try:
    total_weight = data['weight'].sum()
    filtered_weight = filtered_data['weight'].sum()
    percentage = (filtered_weight / total_weight) * 100
    icasm = calcular_icasm_seguro(filtered_data)

    # Exibir resultados
    st.header("Resultados")
    if np.isnan(percentage) or np.isnan(icasm):
        exibir_erro("Não foi possível calcular os resultados com os filtros atuais.")
    else:
        st.markdown(f"<h4>Porcentagem de respondentes: {percentage:.2f}%</h4>", unsafe_allow_html=True)
        st.markdown(f"<h4>ICASM dos respondentes: {icasm:.2f}</h4>", unsafe_allow_html=True)
except Exception as e:
    exibir_erro(f"Erro ao calcular resultados: {str(e)}")

st.divider()

# Adicionar seleção para o filtro secundário na tela principal
st.subheader("Filtro Secundário")
secondary_filter_options = list(filtros.values()) + [f"Questionário {col}" for col in json_columns]
secondary_filter = st.selectbox("Selecione o filtro secundário", [''] + secondary_filter_options)

# Cálculo do filtro secundário
if secondary_filter:
    try:
        if secondary_filter in filtros.values():
            secondary_column = [col for col, label in filtros.items() if label == secondary_filter][0]
            secondary_options = filtered_data[secondary_column].unique()
            secondary_percentages = {}
            secondary_icasm = {}
            for option in secondary_options:
                secondary_filtered = filtered_data[filtered_data[secondary_column] == option]
                secondary_weight = secondary_filtered['weight'].sum()
                secondary_percentage = (secondary_weight / filtered_weight) * 100
                secondary_percentages[option] = secondary_percentage
                secondary_icasm[option] = (secondary_filtered['atlas_mh_index'] * secondary_filtered['weight']).sum() / secondary_weight
        else:
            json_column = secondary_filter.split()[-1]
            secondary_options = []
            secondary_percentages = {}
            secondary_icasm = {}
            for question in json_filters[json_column]:
                for option in json_filters[json_column][question]:
                    if option != 'Todos':
                        secondary_filtered = filtered_data[filtered_data[json_column].apply(
                            lambda x: any(item['label'] == question and item['value'] == option 
                                          for item in json.loads(x.replace("'", '"')))
                        )]
                        secondary_weight = secondary_filtered['weight'].sum()
                        secondary_percentage = (secondary_weight / filtered_weight) * 100
                        secondary_percentages[f"{question}: {option}"] = secondary_percentage
                        secondary_icasm[f"{question}: {option}"] = (secondary_filtered['atlas_mh_index'] * secondary_filtered['weight']).sum() / secondary_weight
                        secondary_options.append(f"{question}: {option}")

        st.subheader(f"Distribuição por {secondary_filter}")
        
        # Criar o gráfico de barras
        fig = go.Figure()
        
        # Adicionar barras
        fig.add_trace(go.Bar(
            x=list(secondary_percentages.keys()),
            y=list(secondary_percentages.values()),
            text=[f"{value:.2f}%" for value in secondary_percentages.values()],
            textposition='auto',
            name='Porcentagem'
        ))
        
        # Adicionar texto do ICASM
        for i, (option, percentage) in enumerate(secondary_percentages.items()):
            fig.add_annotation(
                x=option,
                y=percentage,
                text=f"ICASM: {secondary_icasm[option]:.2f}",
                showarrow=False,
                yshift=25
            )
        
        # Configurar o layout
        fig.update_layout(
            title=f"Distribuição por {secondary_filter}",
            xaxis_title=secondary_filter,
            yaxis_title="Porcentagem",
            bargap=0.2,
            height=500
        )
        
        # Exibir o gráfico
        st.plotly_chart(fig)

        # Exibir os dados em formato de texto
        for option in secondary_options:
            st.write(f"**{option}:** {secondary_percentages[option]:.2f}% | ICASM: {secondary_icasm[option]:.2f}")
    except Exception as e:
        exibir_erro(f"Erro ao processar o filtro secundário: {str(e)}")

st.divider()

# Mostrar tabela de dados filtrados
st.write("### Dados Filtrados")
if filtered_data.empty:
    st.warning("Nenhum dado encontrado com os filtros atuais.")
else:
    st.dataframe(filtered_data)