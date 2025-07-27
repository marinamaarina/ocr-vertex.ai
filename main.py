import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Configuração da Página
st.set_page_config(
    page_title="OCR/LLM Analytics Pro",
    layout="wide",
    page_icon="📊"
)

# CSS Personalizado
st.markdown("""
<style>
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .error-highlight {
        background-color: #ffdddd;
        border-left: 3px solid #ff0000;
        padding: 5px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file):
    """Carrega dados com tratamento robusto"""
    try:
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        
        # Conversão segura de datas
        if 'Data' in df.columns:
            df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
            df = df.dropna(subset=['Data'])
        
        return df
    except Exception as e:
        st.error(f"Erro na carga de dados: {str(e)}")
        return None

def safe_date_filter(df, date_col, date_range):
    """Filtro temporal com tratamento de erros"""
    try:
        if date_col in df.columns:
            mask = (df[date_col].dt.date >= date_range[0]) & (df[date_col].dt.date <= date_range[1])
            return df[mask]
        return df
    except Exception:
        return df

# Interface Principal
st.title("📊 OCR/LLM Analytics Pro")

uploaded_file = st.file_uploader("Carregue seu arquivo de resultados", type=['csv', 'xlsx'])

if uploaded_file:
    df = load_data(uploaded_file)
    
    if df is not None:
        # Filtros na Sidebar
        st.sidebar.header("Filtros")
        
        # Filtro Temporal Seguro
        if 'Data' in df.columns:
            min_date = df['Data'].min().date()
            max_date = df['Data'].max().date()
            
            try:
                date_range = st.sidebar.date_input(
                    "Período",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
                
                if len(date_range) == 2:
                    df = safe_date_filter(df, 'Data', date_range)
            except Exception as e:
                st.sidebar.warning("Erro no filtro de data. Mostrando todos os dados.")
        
        # Outros Filtros
        if 'Status' in df.columns:
            status_options = df['Status'].unique()
            selected_status = st.sidebar.multiselect(
                "Status",
                options=status_options,
                default=status_options
            )
            df = df[df['Status'].isin(selected_status)]
        
        # Visualização dos Dados
        st.dataframe(
            df.style.applymap(
                lambda x: 'background-color: #ffdddd' if 'incorreto' in str(x).lower() else '',
                subset=['Status']
            ),
            height=600,
            use_container_width=True
        )

        # Botão de Exportação
        output = BytesIO()
        df.to_excel(output, index=False)
        st.download_button(
            label="Exportar para Excel",
            data=output.getvalue(),
            file_name="resultados_analise.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Rodapé
st.markdown("---")
st.caption("Relatório gerado em: " + datetime.now().strftime("%d/%m/%Y %H:%M"))
