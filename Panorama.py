import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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

# Criar filtros dinâmicos
filtered_data = data.copy()
for col, label in filtros.items():
    options = ['Todos'] + list(data[col].unique())
    selected = st.sidebar.multiselect(label, options, default='Todos')
    if 'Todos' not in selected:
        filtered_data = filtered_data[filtered_data[col].isin(selected)]

# Cálculo da porcentagem ponderada
total_weight = data['weight'].sum()
filtered_weight = filtered_data['weight'].sum()
percentage = (filtered_weight / total_weight) * 100

# Cálculo do ICASM (média ponderada da coluna atlas_mh_index)
icasm = (filtered_data['atlas_mh_index'] * filtered_data['weight']).sum() / filtered_weight

# Exibir resultados
st.header("Resultados")
st.markdown(f"<h4>Porcentagem de respondentes: {percentage:.2f}%</h4>", unsafe_allow_html=True)
st.markdown(f"<h4>ICASM dos respondentes: {icasm:.2f}</h4>", unsafe_allow_html=True)

st.divider()

# Adicionar seleção para o filtro secundário na tela principal
st.subheader("Filtro Secundário")
secondary_filter = st.selectbox("Selecione o filtro secundário", [''] + list(filtros.values()))

# Cálculo do filtro secundário
if secondary_filter:
    secondary_column = [col for col, label in filtros.items() if label == secondary_filter][0]
    secondary_options = filtered_data[secondary_column].unique()
    secondary_percentages = {}
    secondary_icasm = {}
    for option in secondary_options:
        secondary_filtered = filtered_data[filtered_data[secondary_column] == option]
        secondary_weight = secondary_filtered['weight'].sum()
        secondary_percentage = (secondary_weight / filtered_weight) * 100
        secondary_percentages[option] = secondary_percentage
        
        # Cálculo do ICASM para cada subdivisão
        secondary_icasm[option] = (secondary_filtered['atlas_mh_index'] * secondary_filtered['weight']).sum() / secondary_weight

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

st.divider()

# Mostrar tabela de dados filtrados
st.write("### Dados Filtrados")
st.dataframe(filtered_data)
