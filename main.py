import streamlit as st
import pandas as pd

# Upload do arquivo
uploaded_file = st.file_uploader("Envie a planilha com os testes", type=["csv", "xlsx"])

if uploaded_file:
    # Detectar se é CSV ou Excel
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Selecionar o teste
    teste_opcao = st.selectbox("Escolha o teste para visualizar", sorted(df['Teste'].unique()))

    # Filtrar os dados pelo teste escolhido
    df_filtrado = df[df['Teste'] == teste_opcao]

    st.write(f"Resultados para o Teste {teste_opcao}:")
    st.dataframe(df_filtrado)
else:
    st.info("Envie uma planilha com colunas como: Teste, Temperatura, Top-P, Pergunta, Resposta.")
