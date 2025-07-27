import streamlit as st
import pandas as pd
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Analisador OCR/LLM",
    layout="wide",
    page_icon="🧠"
)

# CSS personalizado
st.markdown("""
<style>
    .error { background-color: #ffcccc; border-left: 4px solid #ff0000; padding: 8px; }
    .warning { background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 8px; }
    .success { background-color: #d4edda; border-left: 4px solid #28a745; padding: 8px; }
    .metric-box {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file):
    """Carrega dados do arquivo CSV ou Excel"""
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file, encoding='utf-8')
        return pd.read_excel(file)
    except Exception as e:
        st.error(f"Erro ao carregar: {str(e)}")
        return None

def apply_style(val, status):
    """Aplica estilo condicional baseado no status"""
    if pd.isna(status): return val
    if 'incorreto' in str(status).lower(): return f'<div class="error">{val}</div>'
    if 'parcial' in str(status).lower(): return f'<div class="warning">{val}</div>'
    if 'correto' in str(status).lower(): return f'<div class="success">{val}</div>'
    return val

# Interface principal
st.title("🧠 Analisador de Testes OCR/LLM")
st.caption("Relatório completo de validação dos testes")

# Upload do arquivo
uploaded_file = st.file_uploader("Suba seu arquivo (CSV ou Excel)", type=['csv','xlsx'])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        # Sidebar - Filtros
        st.sidebar.header("⚙️ Filtros")
        
        # Filtros dinâmicos
        filters = {}
        for col in ['Teste', 'Perguntas', 'Status']:
            if col in df.columns:
                options = ["Todos"] + sorted(df[col].dropna().unique())
                selected = st.sidebar.selectbox(f"Filtrar por {col}", options)
                if selected != "Todos":
                    filters[col] = selected
        
        # Aplicar filtros
        filtered_df = df.copy()
        for col, val in filters.items():
            filtered_df = filtered_df[filtered_df[col] == val]
        
        # Métricas (3 colunas)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-box"><b>Total de Testes</b><br><h3>{}</h3></div>'.format(
                len(df)), unsafe_allow_html=True)
        
        with col2:
            if 'Status' in df.columns:
                correct = len(df[df['Status'].str.contains('correto', case=False, na=False)])
                st.markdown('<div class="metric-box"><b>Corretos</b><br><h3>{} ({:.0f}%)</h3></div>'.format(
                    correct, (correct/len(df))*100), unsafe_allow_html=True)
        
        with col3:
            if 'Status' in df.columns:
                issues = len(df[~df['Status'].str.contains('correto', case=False, na=False)])
                st.markdown('<div class="metric-box"><b>Com problemas</b><br><h3>{} ({:.0f}%)</h3></div>'.format(
                    issues, (issues/len(df))*100), unsafe_allow_html=True)

        # Tabela interativa
        st.subheader("📊 Resultados Detalhados")
        
        if not filtered_df.empty:
            # Aplicar estilos
            styled_df = filtered_df.copy()
            if 'Status' in df.columns:
                for col in ['Valor extraído', 'Motivo Erro / Observação']:
                    if col in styled_df.columns:
                        styled_df[col] = styled_df.apply(
                            lambda x: apply_style(x[col], x['Status']), axis=1)
            
            # Mostrar tabela
            st.markdown(styled_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            
            # Botão de download
            excel_buffer = BytesIO()
            filtered_df.to_excel(excel_buffer, index=False)
            st.download_button(
                label="⬇️ Exportar para Excel",
                data=excel_buffer.getvalue(),
                file_name="resultados_analise.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.warning("Nenhum resultado encontrado com os filtros atuais")

        # Análise de erros (se aplicável)
        if 'Status' in df.columns and 'Motivo Erro / Observação' in df.columns:
            errors = df[~df['Status'].str.contains('correto', case=False, na=False)]
            if not errors.empty:
                st.subheader("🔍 Análise Detalhada de Problemas")
                
                for idx, row in errors.iterrows():
                    with st.expander(f"{row.get('Perguntas', 'Pergunta')} - {row.get('Status', 'Status')}", False):
                        cols = st.columns([1,2])
                        with cols[0]:
                            st.markdown("**Valor Extraído:**")
                            st.write(row.get('Valor extraído', ''))
                        with cols[1]:
                            st.markdown("**Problema Identificado:**")
                            st.write(row.get('Motivo Erro / Observação', 'Sem detalhes'))
else:
    st.info("👉 Por favor, faça upload do arquivo de resultados para iniciar a análise")

# Rodapé
st.markdown("---")
st.caption("Relatório gerado automaticamente - © 2023 Análise OCR/LLM")
