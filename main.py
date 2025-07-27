import streamlit as st
import pandas as pd

st.title("Análise de Extração Vertex AI")

uploaded_file = st.file_uploader("Faça upload do arquivo CSV com os dados de extração", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Renomeia as colunas para nomes mais simples/internos
    df = df.rename(columns={
        "Perguntas ": "Pergunta",
        "Valor extraído": "Resposta",
        "Correto (✓/X)": "Status",
        "Motivo Erro / Observação": "Observação"
    })

    expected_cols = ["Teste", "Temperatura", "Top-P", "Pergunta", "Resposta", "Status", "Observação"]
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Faltam colunas no arquivo: {missing_cols}")
    else:
        df["Temperatura"] = df["Temperatura"].astype(float)
        df["Top-P"] = df["Top-P"].astype(float)

        temperatura_filter = st.selectbox("Selecione Temperatura:", sorted(df["Temperatura"].unique()))
        top_p_filter = st.selectbox("Selecione Top-P:", sorted(df["Top-P"].unique()))
        pergunta_filter = st.selectbox("Selecione a Pergunta:", df["Pergunta"].unique())

        filtered_df = df[
            (df["Temperatura"] == temperatura_filter) & 
            (df["Top-P"] == top_p_filter) & 
            (df["Pergunta"] == pergunta_filter)
        ]

        if filtered_df.empty:
            st.warning("Nenhum resultado para os filtros selecionados.")
        else:
            for idx, row in filtered_df.iterrows():
                st.markdown(f"### Teste: {row['Teste']}")
                st.markdown(f"**Status:** {row['Status']}")
                st.markdown("**Resposta Extraída:**")
                st.text(row["Resposta"])
                st.markdown("**Observações:**")
                st.text(row["Observação"])
                st.markdown("---")
else:
    st.info("Aguarde o upload do arquivo CSV para carregar os dados.")


