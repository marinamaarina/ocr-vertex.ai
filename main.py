import streamlit as st
import pandas as pd

# Dados dos testes
dados_teste = pd.DataFrame({
    "Teste": ["A", "B", "C", "D", "E", "F"],
    "Temperatura": [0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
    "Top-P": [1.0, 1.0, 0.95, 0.9, 0.8, 0.7]
})

# Dicionário com perguntas e respostas por teste
respostas = {
    "A": {
        "perguntas": ["O que é inteligência artificial?", "Como funciona o machine learning?"],
        "respostas": ["IA é a simulação da inteligência humana por máquinas.", "Machine learning usa algoritmos que aprendem com dados."]
    },
    "B": {
        "perguntas": ["O que é Python?", "Para que serve o Pandas?"],
        "respostas": ["Python é uma linguagem de programação.", "Pandas é uma biblioteca para análise de dados."]
    },
    "C": {
        "perguntas": ["O que é uma rede neural?"],
        "respostas": ["É um modelo inspirado no cérebro humano que aprende padrões."]
    },
    "D": {
        "perguntas": ["Qual a diferença entre IA e aprendizado de máquina?"],
        "respostas": ["IA é o conceito mais amplo, aprendizado de máquina é uma aplicação da IA."]
    },
    "E": {
        "perguntas": ["O que é o ChatGPT?"],
        "respostas": ["É um modelo de linguagem treinado para gerar respostas em linguagem natural."]
    },
    "F": {
        "perguntas": ["Explique o conceito de overfitting."],
        "respostas": ["É quando um modelo aprende os dados de treino tão bem que vai mal nos dados novos."]
    }
}

# Interface Streamlit
st.title("Visualização dos Testes")

# Seleção de teste
teste_selecionado = st.selectbox("Selecione o teste:", dados_teste["Teste"])

# Mostrar parâmetros do teste
st.subheader("Parâmetros do Teste")
teste_row = dados_teste[dados_teste["Teste"] == teste_selecionado]
st.write(teste_row)

# Mostrar perguntas e respostas
st.subheader("Perguntas e Respostas")
qa = respostas.get(teste_selecionado, {"perguntas": [], "respostas": []})
for i, (pergunta, resposta) in enumerate(zip(qa["perguntas"], qa["respostas"]), 1):
    st.markdown(f"**Pergunta {i}:** {pergunta}")
    st.markdown(f"**Resposta {i}:** {resposta}")
