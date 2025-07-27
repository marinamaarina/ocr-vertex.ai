import streamlit as st
import pandas as pd
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
        padding: 2px;
        border-radius: 4px;
    }
    .highlight-orange {
        background-color: #ffe6cc;
        padding: 2px;
        border-radius: 4px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def load_data(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        elif uploaded_file.name.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Formato não suportado. Use CSV ou Excel.")
            return None
        
        # Limpeza básica dos dados
        if 'Correto (✓/X)' in df.columns:
            df['Status'] = df['Correto (✓/X)'].str.strip()
        return df
    
    except Exception as e:
        st.error(f"Erro ao carregar arquivo: {str(e)}")
        return None

# Função para aplicar destaque
def highlight_text(text, status):
    if pd.isna(status):
        return text
    if 'Incorreto' in str(status) or 'Errado' in str(status):
        return f'<span class="highlight-red">{text}</span>'
    elif 'Parcialmente' in str(status):
        return f'<span class="highlight-orange">{text}</span>'
    return text

# Interface principal
st.title("🔍 Análise de Testes OCR + LLM")
st.markdown("Visualização dos resultados sem uso do Plotly")

# Upload de arquivo
uploaded_file = st.file_uploader(
    "📤 Carregue o arquivo de resultados (CSV ou Excel)",
    type=['csv', 'xlsx', 'xls']
)

if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    if df is not None:
        # Sidebar - Filtros
        st.sidebar.header("🔍 Filtros")
        
        # Filtro por teste
        if 'Teste' in df.columns:
            test_options = ["Todos"] + sorted(df['Teste'].unique())
            selected_test = st.sidebar.selectbox("Teste", test_options)
        
        # Filtro por pergunta
        if 'Perguntas ' in df.columns:
            question_options = ["Todos"] + sorted(df['Perguntas '].dropna().unique())
            selected_question = st.sidebar.selectbox("Pergunta", question_options)
        
        # Filtro por status
        if 'Status' in df.columns:
            status_options = ["Todos"] + sorted(df['Status'].dropna().unique())
            selected_status = st.sidebar.selectbox("Status", status_options)
        
        # Aplicar filtros
        filtered_df = df.copy()
        if 'Teste' in df.columns and selected_test != "Todos":
            filtered_df = filtered_df[filtered_df['Teste'] == selected_test]
        if 'Perguntas ' in df.columns and selected_question != "Todos":
            filtered_df = filtered_df[filtered_df['Perguntas '] == selected_question]
        if 'Status' in df.columns and selected_status != "Todos":
            filtered_df = filtered_df[filtered_df['Status'] == selected_status]

        # Métricas principais
        st.header("📊 Métricas Gerais")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card"><b>Total de Testes</b><br>{}<div>'.format(
                len(df)), unsafe_allow_html=True)
        
        with col2:
            if 'Status' in df.columns:
                correct = len(df[df['Status'] == 'Correto'])
                st.markdown('<div class="metric-card"><b>Corretos</b><br>{} ({:.1f}%)<div>'.format(
                    correct, (correct/len(df))*100), unsafe_allow_html=True)
        
        with col3:
            if 'Status' in df.columns:
                errors = len(df[df['Status'].str.contains('Incorreto|Errado|Parcialmente', na=False)])
                st.markdown('<div class="metric-card"><b>Com problemas</b><br>{} ({:.1f}%)<div>'.format(
                    errors, (errors/len(df))*100), unsafe_allow_html=True)

        # Visualização de dados alternativa
        st.header("📋 Resultados Detalhados")
        
        # Mostrar tabela com destaque
        if not filtered_df.empty:
            # Aplicar formatação HTML
            formatted_df = filtered_df.copy()
            if 'Status' in df.columns:
                for col in formatted_df.columns:
                    if formatted_df[col].dtype == 'object':
                        formatted_df[col] = formatted_df.apply(
                            lambda x: highlight_text(str(x[col]), x['Status']), axis=1)
            
            st.markdown(formatted_df.to_html(escape=False, index=False), unsafe_allow_html=True)
        else:
            st.warning("Nenhum resultado encontrado com os filtros selecionados")

        # Análise de erros
        if 'Status' in df.columns and 'Motivo Erro / Observação' in df.columns:
            error_df = df[df['Status'].str.contains('Incorreto|Errado|Parcialmente', na=False)]
            if not error_df.empty:
                st.header("🔴 Análise de Erros")
                
                for idx, row in error_df.iterrows():
                    with st.expander(f"Problema em: {row.get('Perguntas ', '')}", expanded=False):
                        st.markdown(f"**Valor extraído:**\n\n{row.get('Valor extraído', '')}")
                        st.markdown(f"**Problema:**\n\n{row.get('Motivo Erro / Observação', '')}")

        # Botão para download
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Baixar Resultados Filtrados",
            data=output.getvalue(),
            file_name="resultados_filtrados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
else:
    st.info("ℹ️ Por favor, carregue o arquivo de resultados para começar.")
