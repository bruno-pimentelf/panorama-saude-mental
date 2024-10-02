import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np

# Configuração do modo amplo
st.set_page_config(layout="wide", page_title="Panorama da Saúde Mental", page_icon="🌵", initial_sidebar_state="expanded")

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
    'gender': 'Gênero',
    'age': 'Faixa Etária',
    'race': 'Raça',
    'region': 'Região',
    'state': 'Estado',
    'family_income': 'Renda Familiar',
    'religion': 'Religião',
    'gender_identity': 'Identidade de Gênero',
    'educational_level': 'Nível Educacional',
    'receive_bolsa_familia': 'Recebe Bolsa Família',
    'employment': 'Emprego',
    'who_is_primarily_responsible_for_supporting_your_home': 'Responsável Principal pelo Sustento do Lar',
    'employed_or_looking_for_employment': 'Empregado ou Procurando Emprego',
    'sexual_orientation': 'Orientação Sexual',
    'marital_status': 'Estado Civil',
    'have_kids': 'Tem Filhos',
    'age_of_youngest_kid': 'Idade do Filho Mais Novo',
    'ever_thought_you_should_stop_drinking': 'Já pensou que deveria parar de beber',
    'are_you_a_person_with_disability': 'Pessoa com Deficiência',
}

filtros_variaveis = {
    'did_the_use_of_social_media_impact_mental_health': 'O uso de mídias sociais impactou sua saúde mental',
    'had_negative_experiences': 'Experiências Negativas com o Uso de Mídias Sociais',
    'when_started_using_social_networks': 'Quando começou a usar mídias sociais',
    'content_format': 'Formato de Conteúdo Visto',
    'what_time_of_the_day_do_use_social_media': 'Que horas do dia você usa mídias sociais',
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
json_columns = ['QSG12A', 'QSG12B', 'PHQ-9', 'during_last_weeks_how_many_times_you', 'how_much_do_you_agree_with_the_following_statementes']
json_filters = {}
for column in json_columns:
    json_filters[column] = get_json_questions_and_options(column)

# Criar filtros dinâmicos
filtered_data = data.copy()

# Módulo Fixo
st.sidebar.subheader("Módulo Fixo")
for col, label in filtros.items():
    options = ['Todos'] + list(data[col].unique())
    selected = st.sidebar.multiselect(label, options, default='Todos')
    if 'Todos' not in selected:
        filtered_data = filtered_data[filtered_data[col].isin(selected)]

st.sidebar.divider()

# Módulo Variável
st.sidebar.subheader("Módulo Variável")
for col, label in filtros_variaveis.items():
    options = ['Todos'] + list(data[col].unique())
    selected = st.sidebar.multiselect(label, options, default='Todos')
    if 'Todos' not in selected:
        filtered_data = filtered_data[filtered_data[col].isin(selected)]

# Adicionar filtros para colunas JSON
for column, questions in json_filters.items():
    st.sidebar.subheader(f"Questionário {column}")
    for question, options in questions.items():
        selected = st.sidebar.multiselect(question, options, default='Todos')
        if 'Todos' not in selected:
            filtered_data = filtered_data[filtered_data[column].apply(
                lambda x: any(item['label'] == question and item['value'] in selected 
                              for item in json.loads(x.replace("'", '"')))
            )]

# Adicionar seleção de métrica na tela principal
st.subheader("Seleção de Métrica")
metric_options = {
    "ICASM": "atlas_mh_index",
    "Vitalidade": "depression_index",
    "Confiança": "confidence_index",
    "Foco": "dysfunction_index"
}
selected_metric = st.selectbox("Escolha a métrica a ser exibida:", list(metric_options.keys()))

# Função para calcular a métrica selecionada
def calcular_metrica_seguro(df, metric_column):
    try:
        return round((df[metric_column] * df['weight']).sum() / df['weight'].sum())
    except Exception as e:
        st.error(f"Erro ao calcular a métrica: {str(e)}")
        return None

# Cálculo da porcentagem ponderada e métrica selecionada
try:
    total_weight = data['weight'].sum()
    filtered_weight = filtered_data['weight'].sum()
    percentage = (filtered_weight / total_weight) * 100
    metric_value = calcular_metrica_seguro(filtered_data, metric_options[selected_metric])

    # Exibir resultados
    st.header("Resultados")
    if np.isnan(percentage) or metric_value is None:
        st.error("Não foi possível calcular os resultados com os filtros atuais.")
    else:
        st.markdown(f"<h4>Porcentagem de respondentes: {percentage:.1f}%</h4>", unsafe_allow_html=True)
        st.markdown(f"<h4>{selected_metric} dos respondentes: {metric_value}</h4>", unsafe_allow_html=True)
except Exception as e:
    st.error(f"Erro ao calcular resultados: {str(e)}")

st.divider()

# Adicionar seleção para o filtro secundário na tela principal
st.subheader("Filtro Secundário")
secondary_filter_options = list(filtros.values()) + list(filtros_variaveis.values()) + [f"Questionário {col}" for col in json_columns]
secondary_filter = st.selectbox("Selecione o filtro secundário", [''] + secondary_filter_options)

# Adicionar seleção de métrica para o filtro secundário
secondary_metric = st.selectbox("Escolha a métrica para o filtro secundário:", list(metric_options.keys()), index=list(metric_options.keys()).index(selected_metric))

# Adicionar opção para inverter o gráfico
inverter_grafico = st.checkbox("Inverter gráfico (métricas como barras principais)")

# Cálculo do filtro secundário
if secondary_filter:
    try:
        if secondary_filter in filtros.values() or secondary_filter in filtros_variaveis.values():
            secondary_column = [col for col, label in {**filtros, **filtros_variaveis}.items() if label == secondary_filter][0]
            secondary_options = filtered_data[secondary_column].unique()
            secondary_percentages = {}
            secondary_metric_values = {}
            for option in secondary_options:
                secondary_filtered = filtered_data[filtered_data[secondary_column] == option]
                secondary_weight = secondary_filtered['weight'].sum()
                secondary_percentage = (secondary_weight / filtered_weight) * 100
                secondary_percentages[option] = secondary_percentage
                secondary_metric_values[option] = calcular_metrica_seguro(secondary_filtered, metric_options[secondary_metric])
        else:
            json_column = secondary_filter.split()[-1]
            secondary_options = []
            secondary_percentages = {}
            secondary_metric_values = {}
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
                        secondary_metric_values[f"{question}: {option}"] = calcular_metrica_seguro(secondary_filtered, metric_options[secondary_metric])
                        secondary_options.append(f"{question}: {option}")

        st.subheader(f"Distribuição por {secondary_filter}")
        
        # Criar o gráfico de barras
        fig = go.Figure()
        
        if inverter_grafico:
            # Métricas como barras principais
            fig.add_trace(go.Bar(
                x=list(secondary_percentages.keys()),
                y=list(secondary_metric_values.values()),
                text=[f"{value}" for value in secondary_metric_values.values()],
                textposition='auto',
                name=secondary_metric,
                marker_color="#368a50"
            ))
            
            # Adicionar texto da porcentagem
            for i, (option, metric_value) in enumerate(secondary_metric_values.items()):
                fig.add_annotation(
                    x=option,
                    y=metric_value,
                    text=f"Porcentagem: {secondary_percentages[option]:.1f}%",
                    showarrow=False,
                    yshift=25
                )
            
            # Configurar o layout
            fig.update_layout(
                title=f"Distribuição por {secondary_filter}",
                xaxis_title=secondary_filter,
                yaxis_title=secondary_metric,
                bargap=0.2,
                height=500
            )
        else:
            # Porcentagens como barras principais (código original)
            fig.add_trace(go.Bar(
                x=list(secondary_percentages.keys()),
                y=list(secondary_percentages.values()),
                text=[f"{value:.1f}%" for value in secondary_percentages.values()],
                textposition='auto',
                name='Porcentagem',
                marker_color="#368a50"
            ))
            
            # Adicionar texto da métrica selecionada
            for i, (option, percentage) in enumerate(secondary_percentages.items()):
                fig.add_annotation(
                    x=option,
                    y=percentage,
                    text=f"{secondary_metric}: {secondary_metric_values[option]}",
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
            st.write(f"**{option}:** {secondary_percentages[option]:.1f}% | {secondary_metric}: {secondary_metric_values[option]}")
    except Exception as e:
        st.error(f"Erro ao processar o filtro secundário: {str(e)}")

st.divider()