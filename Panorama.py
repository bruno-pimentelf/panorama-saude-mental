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
st.title('Panorama da Saúde Mental -> 1º S 2024')

# Adicionar logo do Cactus na sidebar
st.sidebar.image('logo_cactus.png', width=200)
st.sidebar.markdown("*by: Bruno Pimentel*")

# Adicionar botão de reset
if st.sidebar.button("🔄 Redefinir Todos os Filtros"):
    # Limpar todos os valores do session_state
    for key in list(st.session_state.keys()):
        if key.startswith(('demo_', 'socio_', 'pessoal_', 'var_', 'quest_')):
            # Definir o valor padrão como ['Todos'] ao invés de apenas deletar
            st.session_state[key] = ['Todos']
    st.rerun()

st.sidebar.divider()

# Seção de filtros
st.sidebar.header("Filtros de Respostas")

# Organizar filtros em categorias
filtros_demografia = {
    'gender': 'Gênero',
    'age': 'Faixa Etária',
    'race': 'Raça',
    'region': 'Região',
    'state': 'Estado',
    'family_income': 'Renda Familiar',
    'religion': 'Religião',
    'gender_identity': 'Identidade de Gênero',
    'educational_level': 'Nível Educacional'
}

filtros_socioeconomico = {
    'receive_bolsa_familia': 'Recebe Bolsa Família',
    'employment': 'Emprego',
    'who_is_primarily_responsible_for_supporting_your_home': 'Responsável Principal pelo Sustento do Lar',
    'employed_or_looking_for_employment': 'Empregado ou Procurando Emprego'
}

filtros_pessoal = {
    'sexual_orientation': 'Orientação Sexual',
    'marital_status': 'Estado Civil',
    'have_kids': 'Tem Filhos',
    'age_of_youngest_kid': 'Idade do Filho Mais Novo',
    'ever_thought_you_should_stop_drinking': 'Já pensou que deveria parar de beber',
    'are_you_a_person_with_disability': 'Pessoa com Deficiência',
}

# Adicionar filtros para todas as colunas especificadas
filtros_variaveis = {
    'did_the_use_of_social_media_impact_mental_health': 'O uso de mídias sociais impactou sua saúde mental',
    'had_negative_experiences': 'Experiências Negativas com o Uso de Mídias Sociais',
    'when_started_using_social_networks': 'Quando começou a usar mídias sociais',
    'content_format': 'Formato de Conteúdo Visto',
    'what_time_of_the_day_do_use_social_media': 'Que horas do dia você usa mídias sociais'
}

# Função para extrair questões e opções de colunas JSON
def get_json_questions_and_options(column):
    questions = {}
    for item in data[column].dropna():
        if not item or item.isspace():
            continue
        try:
            json_data = json.loads(item.replace("'", '"'))
            for question in json_data:
                if question is None:
                    continue
                label = question['label']
                value = question['value']
                if label not in questions:
                    questions[label] = set()
                questions[label].add(value)
        except json.JSONDecodeError:
            continue
    return {k: ['Todos'] + sorted(list(v)) for k, v in questions.items()}

# Adicionar filtros para colunas JSON
json_columns = ['QSG12A', 'QSG12B', 'PHQ-9', 'during_last_weeks_how_many_times_you', 'how_much_do_you_agree_with_the_following_statementes', 'used_social_network_2ww']
json_filters = {}
for column in json_columns:
    json_filters[column] = get_json_questions_and_options(column)

# Criar filtros dinâmicos
filtered_data = data.copy()

# Função para atualizar a seleção removendo 'Todos' quando necessário
def update_selection(key):
    current_selection = st.session_state[key]
    if len(current_selection) > 1 and 'Todos' in current_selection:
        # Se houver mais de uma seleção e 'Todos' estiver entre elas,
        # remove 'Todos' da lista
        current_selection.remove('Todos')
        st.session_state[key] = current_selection
    elif len(current_selection) == 0:
        # Se não houver seleção, adiciona 'Todos'
        st.session_state[key] = ['Todos']

# Substituir a função ensure_todos anterior por esta nova função
def ensure_todos(key):
    if len(st.session_state[key]) == 0:
        st.session_state[key] = ['Todos']
    else:
        update_selection(key)

# Criar filtros usando accordions
with st.sidebar.expander("📊 Dados Demográficos", expanded=False):
    for col, label in filtros_demografia.items():
        options = ['Todos'] + list(data[col].unique())
        selected = st.multiselect(
            label, 
            options, 
            default='Todos', 
            key=f"demo_{col}",
            on_change=ensure_todos,
            args=(f"demo_{col}",)
        )
        if 'Todos' not in selected:
            filtered_data = filtered_data[filtered_data[col].isin(selected)]

with st.sidebar.expander("💰 Dados Socioeconômicos", expanded=False):
    for col, label in filtros_socioeconomico.items():
        options = ['Todos'] + list(data[col].unique())
        selected = st.multiselect(
            label, 
            options, 
            default='Todos', 
            key=f"socio_{col}",
            on_change=ensure_todos,
            args=(f"socio_{col}",)
        )
        if 'Todos' not in selected:
            filtered_data = filtered_data[filtered_data[col].isin(selected)]

with st.sidebar.expander("👤 Dados Pessoais", expanded=False):
    for col, label in filtros_pessoal.items():
        options = ['Todos'] + list(data[col].unique())
        selected = st.multiselect(
            label, 
            options, 
            default='Todos', 
            key=f"pessoal_{col}",
            on_change=ensure_todos,
            args=(f"pessoal_{col}",)
        )
        if 'Todos' not in selected:
            filtered_data = filtered_data[filtered_data[col].isin(selected)]

st.sidebar.divider()

# Módulo Variável em accordion
with st.sidebar.expander("📱 Módulo Variável - Mídias Sociais", expanded=False):
    for col, label in filtros_variaveis.items():
        options = ['Todos'] + list(data[col].unique())
        selected = st.multiselect(
            label, 
            options, 
            default='Todos', 
            key=f"var_{col}",
            on_change=ensure_todos,
            args=(f"var_{col}",)
        )
        if 'Todos' not in selected:
            filtered_data = filtered_data[filtered_data[col].isin(selected)]

# Questionários em accordions separados
for column, questions in json_filters.items():
    with st.sidebar.expander(f"📝 Questionário {column}", expanded=False):
        for question, options in questions.items():
            selected = st.multiselect(
                question, 
                options, 
                default='Todos', 
                key=f"quest_{column}_{question}",
                on_change=ensure_todos,
                args=(f"quest_{column}_{question}",)
            )
            if 'Todos' not in selected:
                filtered_data = filtered_data[filtered_data[column].apply(
                    lambda x: isinstance(x, str) and any(item is not None and item['label'] == question and item['value'] in selected 
                                                         for item in json.loads(x.replace("'", '"')) if x and not x.isspace())
                )]

# Remover a seleção de métrica na tela principal
metric_options = {
    "ICASM": "atlas_mh_index",
    "Vitalidade": "depression_index",
    "Confiança": "confidence_index",
    "Foco": "dysfunction_index"
}

# Função para calcular a métrica selecionada
def calcular_metrica_seguro(df, metric_column):
    try:
        return round((df[metric_column] * df['weight']).sum() / df['weight'].sum())
    except Exception as e:
        st.error(f"Erro ao calcular a métrica: {str(e)}")
        return None
# Adicionar exibição dos filtros ativos
st.subheader("Filtros Ativos")
filtros_ativos = []

# Verificar filtros demográficos
for col, label in filtros_demografia.items():
    selected = st.session_state.get(f"demo_{col}", [])
    if selected and 'Todos' not in selected:
        filtros_ativos.append(f"{label}: {', '.join(selected)}")

# Verificar filtros socioeconômicos
for col, label in filtros_socioeconomico.items():
    selected = st.session_state.get(f"socio_{col}", [])
    if selected and 'Todos' not in selected:
        filtros_ativos.append(f"{label}: {', '.join(selected)}")

# Verificar filtros pessoais
for col, label in filtros_pessoal.items():
    selected = st.session_state.get(f"pessoal_{col}", [])
    if selected and 'Todos' not in selected:
        filtros_ativos.append(f"{label}: {', '.join(selected)}")

# Verificar filtros de variáveis
for col, label in filtros_variaveis.items():
    selected = st.session_state.get(f"var_{col}", [])
    if selected and 'Todos' not in selected:
        filtros_ativos.append(f"{label}: {', '.join(selected)}")

# Verificar filtros dos questionários
for column, questions in json_filters.items():
    for question in questions:
        selected = st.session_state.get(f"quest_{column}_{question}", [])
        if selected and 'Todos' not in selected:
            filtros_ativos.append(f"{question}: {', '.join(selected)}")

if filtros_ativos:
    for filtro in filtros_ativos:
        st.write(f"• {filtro}")
else:
    st.write("Nenhum filtro ativo - mostrando todos os dados")

st.divider()
st.header("Resultados")
# Cálculo da porcentagem ponderada e todas as métricas
try:
    total_weight = data['weight'].sum()
    filtered_weight = filtered_data['weight'].sum()
    percentage = (filtered_weight / total_weight) * 100

    # Criar colunas para exibir as métricas
    cols = st.columns(len(metric_options))
    
    for i, (metric_name, metric_column) in enumerate(metric_options.items()):
        metric_value = calcular_metrica_seguro(filtered_data, metric_column)
        with cols[i]:
            st.metric(label=metric_name, value=metric_value)

    if np.isnan(percentage):
        st.error("Não foi possível calcular os resultados com os filtros atuais.")
    else:
        st.markdown(f"<h4>Porcentagem de respondentes: {percentage:.1f}%</h4>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Erro ao calcular resultados: {str(e)}")

st.divider()

# Adicionar seleção para o filtro secundário na tela principal
st.subheader("Filtro Secundário")
secondary_filter_options = list(filtros_demografia.values()) + list(filtros_socioeconomico.values()) + list(filtros_pessoal.values()) + list(filtros_variaveis.values()) + [f"Questionário {col}" for col in json_columns]
secondary_filter = st.selectbox("Selecione o filtro secundário", [''] + secondary_filter_options)

# Criar duas colunas para as opções do gráfico
col1, col2, col3 = st.columns(3)

with col1:
    # Adicionar seleção de métrica para o filtro secundário
    secondary_metric = st.selectbox("Escolha a métrica para o filtro secundário:", list(metric_options.keys()), index=0)
    # Adicionar opção para inverter o gráfico
    inverter_grafico = st.checkbox("Inverter gráfico (métricas como barras principais)")

with col2:
    # Adicionar seletor de cor
    graph_color = st.color_picker("Escolha a cor do gráfico", "#368a50")
    # Adicionar opção de orientação do gráfico
    orientacao = st.selectbox("Orientação do gráfico", ["Vertical", "Horizontal"])

with col3:
    # Adicionar controle de altura do gráfico
    altura_grafico = st.slider("Altura do gráfico", 400, 1000, 500, 50)
    # Adicionar opção de mostrar grade
    mostrar_grade = st.checkbox("Mostrar linhas de grade", value=False)

# Cálculo do filtro secundário
if secondary_filter:
    try:
        if secondary_filter in filtros_demografia.values() or secondary_filter in filtros_socioeconomico.values() or secondary_filter in filtros_pessoal.values() or secondary_filter in filtros_variaveis.values():
            secondary_column = [col for col, label in {**filtros_demografia, **filtros_socioeconomico, **filtros_pessoal, **filtros_variaveis}.items() if label == secondary_filter][0]
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
                x=list(secondary_percentages.keys()) if orientacao == "Vertical" else list(secondary_metric_values.values()),
                y=list(secondary_metric_values.values()) if orientacao == "Vertical" else list(secondary_percentages.keys()),
                text=[f"{value}" for value in secondary_metric_values.values()],
                textposition='auto',
                name=secondary_metric,
                marker_color=graph_color,
                orientation='v' if orientacao == "Vertical" else 'h',
                textfont=dict(size=14)
            ))
            
            # Ajustar posicionamento das anotações
            for i, (option, metric_value) in enumerate(secondary_metric_values.items()):
                y_position = metric_value if orientacao == "Vertical" else option
                if orientacao == "Vertical":
                    y_shift = 45
                    x_shift = 0
                else:
                    y_shift = 0  # Remover deslocamento vertical no modo horizontal
                    x_shift = 80
                
                fig.add_annotation(
                    x=option if orientacao == "Vertical" else metric_value,
                    y=y_position,
                    text=f"Porcentagem: {secondary_percentages[option]:.1f}%",
                    showarrow=False,
                    yshift=y_shift,
                    xshift=x_shift,
                    font=dict(size=12),
                    align='left' if orientacao == "Horizontal" else 'center'
                )
        else:
            # Porcentagens como barras principais
            fig.add_trace(go.Bar(
                x=list(secondary_percentages.keys()) if orientacao == "Vertical" else list(secondary_percentages.values()),
                y=list(secondary_percentages.values()) if orientacao == "Vertical" else list(secondary_percentages.keys()),
                text=[f"{value:.1f}%" for value in secondary_percentages.values()],
                textposition='auto',
                name='Porcentagem',
                marker_color=graph_color,
                orientation='v' if orientacao == "Vertical" else 'h',
                textfont=dict(size=14)
            ))
            
            # Ajustar posicionamento das anotações
            for i, (option, percentage) in enumerate(secondary_percentages.items()):
                y_position = percentage if orientacao == "Vertical" else option
                if orientacao == "Vertical":
                    y_shift = 45
                    x_shift = 0
                else:
                    y_shift = 0  # Remover deslocamento vertical no modo horizontal
                    x_shift = 80
                
                fig.add_annotation(
                    x=option if orientacao == "Vertical" else percentage,
                    y=y_position,
                    text=f"{secondary_metric}: {secondary_metric_values[option]}",
                    showarrow=False,
                    yshift=y_shift,
                    xshift=x_shift,
                    font=dict(size=12),
                    align='left' if orientacao == "Horizontal" else 'center'
                )
        
        # Configurar o layout
        fig.update_layout(
            title=f"Distribuição por {secondary_filter}",
            xaxis_title=secondary_filter if orientacao == "Vertical" else (secondary_metric if inverter_grafico else "Porcentagem"),
            yaxis_title=secondary_metric if inverter_grafico else "Porcentagem" if orientacao == "Vertical" else secondary_filter,
            bargap=0.2,
            height=altura_grafico,
            plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
            paper_bgcolor='rgba(0,0,0,0)',  # Fundo do papel transparente
            xaxis=dict(
                showgrid=mostrar_grade,
                gridwidth=1,
                gridcolor='rgba(128, 128, 128, 0.2)',  # Cinza semi-transparente
                zeroline=False,
                showline=True,
                linewidth=1,
                linecolor='rgba(128, 128, 128, 0.2)'
            ),
            yaxis=dict(
                showgrid=mostrar_grade,
                gridwidth=1,
                gridcolor='rgba(128, 128, 128, 0.2)',  # Cinza semi-transparente
                zeroline=False,
                showline=True,
                linewidth=1,
                linecolor='rgba(128, 128, 128, 0.2)'
            )
        )
        
        # Exibir o gráfico
        st.plotly_chart(fig)

        # Exibir os dados em formato de texto
        for option in secondary_options:
            st.write(f"**{option}:** {secondary_percentages[option]:.1f}% | {secondary_metric}: {secondary_metric_values[option]}")
    except Exception as e:
        st.error(f"Erro ao processar o filtro secundário: {str(e)}")

st.divider()