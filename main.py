import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# Configurações da página
st.set_page_config(
    page_title="Análise de Testes OCR + LLM",
    layout="wide",
    page_icon="🔍"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .highlight-red {
        background-color: #ffcccc;
    }
    .highlight-orange {
        background-color: #ffe6cc;
    }
    .highlight-blue {
        background-color: #cce0ff;
    }
    .metric-card {
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
    .metric-title {
        font-size: 14px;
        color: #666;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Formato não suportado. Use CSV ou Excel.")
            return None
        
        # Limpeza básica dos dados
        df['Correto (✓/X)'] = df['Correto (✓/X)'].str.strip()
        df['Teste'] = df['Teste'].astype(str)
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

# Função para aplicar destaque
def highlight_errors(row):
    status = row['Correto (✓/X)']
    styles = [''] * len(row)
    
    if pd.isna(status):
        return styles
    
    if 'Incorreto' in status or 'Errado' in status:
        styles = ['background-color: #ffcccc'] * len(row)  # Vermelho
    elif 'Parcialmente' in status:
        styles = ['background-color: #ffe6cc'] * len(row)  # Laranja
    elif 'Não extraiu' in status:
        styles = ['background-color: #cce0ff'] * len(row)  # Azul
    
    return styles

# Interface principal
st.title("🔍 Análise de Testes OCR + LLM (Vertex AI)")
st.markdown("Visualização interativa dos resultados dos testes de extração de dados")

# Upload de arquivo
uploaded_file = st.file_uploader(
    "📤 Carregue o arquivo de resultados (CSV ou Excel)",
    type=['csv', 'xlsx', 'xls'],
    key="file_uploader"
)

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        # Sidebar - Filtros
        st.sidebar.header("🔍 Filtros")
        
        # Filtro por teste
        test_options = ["Todos"] + sorted(df['Teste'].unique())
        selected_test = st.sidebar.selectbox("Teste", test_options)
        
        # Filtro por pergunta
        question_options = ["Todos"] + sorted(df['Perguntas '].dropna().unique())
        selected_question = st.sidebar.selectbox("Pergunta", question_options)
        
        # Filtro por status
        status_options = ["Todos"] + sorted(df['Correto (✓/X)'].dropna().unique())
        selected_status = st.sidebar.selectbox("Status", status_options)
        
        # Filtro por temperatura
        temp_min, temp_max = st.sidebar.slider(
            "Intervalo de Temperatura",
            min_value=float(df['Temperatura'].min()),
            max_value=float(df['Temperatura'].max()),
            value=(float(df['Temperatura'].min()), float(df['Temperatura'].max()))
        )
        
        # Aplicar filtros
        filtered_df = df.copy()
        if selected_test != "Todos":
            filtered_df = filtered_df[filtered_df['Teste'] == selected_test]
        if selected_question != "Todos":
            filtered_df = filtered_df[filtered_df['Perguntas '] == selected_question]
        if selected_status != "Todos":
            filtered_df = filtered_df[filtered_df['Correto (✓/X)'] == selected_status]
        filtered_df = filtered_df[
            (filtered_df['Temperatura'] >= temp_min) & 
            (filtered_df['Temperatura'] <= temp_max)
        ]
        
        # Métricas principais
        st.header("📊 Métricas Gerais")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card"><div class="metric-title">Total de Testes</div><div class="metric-value">{}</div></div>'.format(
                len(df)), unsafe_allow_html=True)
        
        with col2:
            correct = len(df[df['Correto (✓/X)'] == 'Correto'])
            st.markdown('<div class="metric-card"><div class="metric-title">Corretos</div><div class="metric-value" style="color: #2ecc71;">{} ({:.1f}%)</div></div>'.format(
                correct, (correct/len(df))*100), unsafe_allow_html=True)
        
        with col3:
            partial = len(df[df['Correto (✓/X)'].str.contains('Parcialmente', na=False)])
            st.markdown('<div class="metric-card"><div class="metric-title">Parciais</div><div class="metric-value" style="color: #f39c12;">{} ({:.1f}%)</div></div>'.format(
                partial, (partial/len(df))*100), unsafe_allow_html=True)
        
        with col4:
            incorrect = len(df[df['Correto (✓/X)'].str.contains('Incorreto|Errado', na=False)])
            st.markdown('<div class="metric-card"><div class="metric-title">Incorretos</div><div class="metric-value" style="color: #e74c3c;">{} ({:.1f}%)</div></div>'.format(
                incorrect, (incorrect/len(df))*100), unsafe_allow_html=True)
        
        # Visualizações
        st.header("📈 Visualizações")
        
        tab1, tab2, tab3 = st.tabs(["Distribuição por Status", "Desempenho por Pergunta", "Efeito da Temperatura"])
        
        with tab1:
            fig1 = px.pie(
                df, 
                names='Correto (✓/X)', 
                title='Distribuição dos Resultados por Status',
                color_discrete_map={
                    'Correto': '#2ecc71',
                    'Parcialmente': '#f39c12',
                    'Incorreto': '#e74c3c',
                    'Errado': '#e74c3c',
                    'Não extraiu': '#3498db'
                }
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with tab2:
            fig2 = px.bar(
                df.groupby(['Perguntas ', 'Correto (✓/X)']).size().reset_index(name='Contagem'),
                x='Perguntas ',
                y='Contagem',
                color='Correto (✓/X)',
                title='Desempenho por Tipo de Pergunta',
                color_discrete_map={
                    'Correto': '#2ecc71',
                    'Parcialmente': '#f39c12',
                    'Incorreto': '#e74c3c',
                    'Errado': '#e74c3c',
                    'Não extraiu': '#3498db'
                }
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab3:
            fig3 = px.scatter(
                df,
                x='Temperatura',
                y='Top-P',
                color='Correto (✓/X)',
                title='Desempenho por Configuração de Temperatura e Top-P',
                color_discrete_map={
                    'Correto': '#2ecc71',
                    'Parcialmente': '#f39c12',
                    'Incorreto': '#e74c3c',
                    'Errado': '#e74c3c',
                    'Não extraiu': '#3498db'
                }
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # Tabela de resultados
        st.header("📋 Resultados Detalhados")
        
        # Aplicar destaque
        styled_df = filtered_df.style.apply(highlight_errors, axis=1)
        
        # Mostrar tabela
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=600,
            column_config={
                "Valor extraído": st.column_config.TextColumn(width="large"),
                "Motivo Erro / Observação": st.column_config.TextColumn(width="large")
            }
        )
        
        # Análise de erros
        if len(filtered_df[filtered_df['Correto (✓/X)'].str.contains('Incorreto|Parcialmente|Errado', na=False)]) > 0:
            st.header("🔴 Análise de Erros")
            
            errors_df = filtered_df[
                filtered_df['Correto (✓/X)'].str.contains('Incorreto|Parcialmente|Errado', na=False)
            ][['Perguntas ', 'Valor extraído', 'Motivo Erro / Observação']]
            
            for idx, row in errors_df.iterrows():
                with st.expander(f"Erro em: {row['Perguntas ']}", expanded=False):
                    st.markdown(f"**Valor extraído:**\n\n{row['Valor extraído']}")
                    st.markdown(f"**Problema identificado:**\n\n{row['Motivo Erro / Observação']}")
        
        # Botão para download
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Baixar Resultados Filtrados (Excel)",
            data=output.getvalue(),
            file_name="resultados_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
else:
    st.info("ℹ️ Por favor, carregue o arquivo de resultados para começar a análise.")
    st.markdown("""
    ### Exemplo de estrutura esperada:
    - Coluna `Teste`: Identificador do teste (A, B, C, etc.)
    - Coluna `Temperatura`: Valor de temperatura usado no teste
    - Coluna `Top-P`: Valor de Top-P usado no teste
    - Coluna `Perguntas`: Tipo de pergunta/extração realizada
    - Coluna `Valor extraído`: Resultado da extração
    - Coluna `Correto (✓/X)`: Status do resultado (Correto, Parcialmente, Incorreto, etc.)
    - Coluna `Motivo Erro / Observação`: Detalhes sobre os erros encontrados
    """)
