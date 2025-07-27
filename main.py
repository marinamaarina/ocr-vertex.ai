import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Análise de Documentos", layout="wide")

# Dados da planilha (substitua por sua fonte de dados real)
data = {
    "Nome do comprador": [
        "THAYSY ANGELICA SILVA SALGUEIRO (assinante do documento)",
        "ROSANA DE LIMA GROPEN",
        "VICTORIA CIPRIANO GROPEN",
        "EVANDRO VEIGA NEGRAO DE LIMA JUNIOR",
        "CARLOS ALBERTO CAMPOS DE ARAUJO",
        "CARLOS GROPEN JUNIOR"
    ],
    "Status": ["Correto (Vi)", "Parcialmente", "Parcialmente", "Correto (Vi)", "Correto (Vi)", "Parcialmente"],
    "Motivo Erro / Observação": [
        "Foram extraídos os nomes dos membros vinculados aos vendedores e doe",
        "Não extraiu a letra J do Sobrenome Gropen",
        "Não extraiu a letra J do Sobrenome Gropen",
        "",
        "",
        "Não extraiu a letra J do Sobrenome Gropen"
    ]
}

df = pd.DataFrame(data)

# Título da aplicação
st.title("Análise de Extração de Dados de Documentos")

# Filtros na sidebar
with st.sidebar:
    st.header("Filtros")
    
    # Filtro por status
    status_options = ["Todos"] + list(df["Status"].unique())
    selected_status = st.selectbox("Status", status_options)
    
    # Filtro por termo de busca
    search_term = st.text_input("Buscar por nome")

# Aplicar filtros
filtered_df = df.copy()
if selected_status != "Todos":
    filtered_df = filtered_df[filtered_df["Status"] == selected_status]
if search_term:
    filtered_df = filtered_df[filtered_df["Nome do comprador"].str.contains(search_term, case=False)]

# Exibir resultados
st.subheader("Resultados da Extração")

# Função para aplicar estilo aos dados com problemas
def highlight_partial(row):
    styles = [''] * len(row)
    if row["Status"] == "Parcialmente":
        styles = ['background-color: #ffcccc'] * len(row)  # Vermelho claro
    return styles

styled_df = filtered_df.style.apply(highlight_partial, axis=1)

# Mostrar tabela estilizada
st.dataframe(styled_df, use_container_width=True)

# Estatísticas
st.subheader("Estatísticas")
col1, col2 = st.columns(2)
with col1:
    st.metric("Total de Registros", len(df))
with col2:
    st.metric("Registros Parciais", len(df[df["Status"] == "Parcialmente"]))

# Observações
st.subheader("Observações Importantes")
st.info("""
1. Foram extraídos os nomes dos membros vinculados aos vendedores e doe
2. Não extraiu a letra J do Sobrenome Gropen
3. Observação: Nesse campo deveria dar a resposta somente nome da empresa e membros societários
""")
