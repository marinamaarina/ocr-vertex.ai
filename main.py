import streamlit as st
import pandas as pd

st.set_page_config(page_title="Validação Vertex AI", layout="wide")

st.title("🧪 Análise de Extração - Vertex AI")
st.markdown("**Responsável:** Marina &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; Configuração: Temperatura 0.1 | Top-P 1.0")

# 📁 Upload do Arquivo
uploaded_file = st.file_uploader("📤 Faça upload do documento para análise", type=["pdf", "docx", "txt"])

if uploaded_file:
    st.success("Arquivo carregado com sucesso!")
    # Aqui você pode incluir a lógica de leitura do conteúdo
    # Para demonstração, vamos usar resultados simulados

    st.subheader("📋 Tabela de Resultados")
    data = {
        "Pergunta": [
            "Nome do comprador?",
            "CPF ou CNPJ do comprador?",
            "Membros societários compradores?",
            "Nome do vendedor?",
            "Membros societários vendedores?",
            "CPF ou CNPJ do vendedor?"
        ],
        "Valor Extraído": [
            "Mistura nomes de membros dos vendedores",
            "Informações mistas e erradas",
            "Repetição de nome da empresa RGZS",
            "RGZS CENTENÁRIO DE EMPREENDIMENTOS LTDA.",
            "RGZS e CNPJs repetidos",
            "CNPJs da empresa RGZS"
        ],
        "Avaliação": [
            "❌ Parcial",
            "❌ Incorreto",
            "❌ Incorreto",
            "⚠️ Parcial",
            "❌ Incorreto",
            "❌ Incorreto"
        ]
    }

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    st.subheader("🔴 Painel de Erros")
    st.markdown("""
    <div style='background-color:#ffe6e6; padding:15px; border-radius:10px'>
    <b>⚠️ Principais falhas:</b><br>
    • Confusão entre compradores e vendedores.<br>
    • Membros societários não identificados.<br>
    • Dados pessoais e empresariais misturados.<br>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("✅ Recomendações")
    st.markdown("""
    - Ajustar o prompt de extração com instruções mais claras.  
    - Testar com outras configurações de temperatura.  
    - Usar documentos variados para teste de consistência.  
    """)
else:
    st.info("Por favor, envie um arquivo para iniciar a análise.")
