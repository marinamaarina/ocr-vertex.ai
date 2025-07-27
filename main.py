import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

# Configuração Premium
st.set_page_config(
    page_title="OCR/LLM Analytics Pro",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# CSS Avançado
st.markdown("""
<style>
    :root {
        --primary: #4a6bdf;
        --secondary: #f0f2f6;
        --success: #28a745;
        --danger: #dc3545;
        --warning: #fd7e14;
    }
    
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 5px solid var(--primary);
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-title {
        color: #6c757d;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        color: var(--primary);
        font-size: 28px;
        font-weight: 700;
        margin: 5px 0;
    }
    .error-card {
        border-left-color: var(--danger) !important;
    }
    .success-card {
        border-left-color: var(--success) !important;
    }
    .warning-card {
        border-left-color: var(--warning) !important;
    }
    .stProgress > div > div > div > div {
        background-color: var(--primary);
    }
    .st-eb {
        background-color: var(--secondary);
    }
    .report-view-container {
        background-color: #f9fafc;
    }
</style>
""", unsafe_allow_html=True)

# Funções Premium
@st.cache_data
def load_data(file):
    """Carrega dados com tratamento avançado"""
    try:
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        
        # Pré-processamento
        df['Data'] = pd.to_datetime(df.get('Data', datetime.now()))
        if 'Status' not in df.columns:
            df['Status'] = df.get('Correto (✓/X)', 'Não avaliado')
            
        return df.sort_values('Data', ascending=False)
    except Exception as e:
        st.error(f"Erro na carga: {str(e)}")
        return None

def create_scorecard(title, value, delta=None, variant="primary"):
    """Cria cards de métricas profissionais"""
    color_map = {
        "primary": "#4a6bdf",
        "success": "#28a745",
        "danger": "#dc3545",
        "warning": "#fd7e14"
    }
    
    return f"""
    <div class="metric-card {' '.join([variant+'-card' if variant else ''])}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {f'<div style="color: {color_map.get(variant)}; font-size: 12px;">{delta}</div>' if delta else ''}
    </div>
    """

# Header Premium
col1, col2 = st.columns([3,1])
with col1:
    st.title("📈 OCR/LLM Analytics Pro")
    st.markdown("**Business Intelligence** para validação de modelos")
with col2:
    st.image("https://via.placeholder.com/150x50?text=LOGO", width=150)

# Upload com estilo
with st.expander("📤 ÁREA DE CARGA DE DADOS", expanded=True if 'df' not in st.session_state else False):
    uploaded_file = st.file_uploader(
        "Selecione o arquivo de resultados", 
        type=['csv','xlsx'],
        help="Arquivos devem conter colunas: Teste, Perguntas, Status"
    )
    
    if uploaded_file and 'df' not in st.session_state:
        with st.spinner('Processando dados premium...'):
            st.session_state.df = load_data(uploaded_file)
            st.success("Dados carregados com sucesso!")

# Dashboard Principal
if 'df' in st.session_state:
    df = st.session_state.df
    
    # Filtros Avançados
    st.sidebar.header("🔍 Filtros Dinâmicos")
    
    # Filtro temporal
    if 'Data' in df.columns:
        min_date = df['Data'].min().date()
        max_date = df['Data'].max().date()
        date_range = st.sidebar.date_input(
            "Período",
            [min_date, max_date],
            min_date=min_date,
            max_date=max_date
        )
    
    # Filtros dinâmicos
    filter_cols = [c for c in ['Teste', 'Perguntas', 'Status'] if c in df.columns]
    filters = {}
    for col in filter_cols:
        filters[col] = st.sidebar.multiselect(
            f"Filtrar {col}",
            options=df[col].unique(),
            default=df[col].unique()
        )
    
    # Aplicar filtros
    filtered_df = df.copy()
    if 'Data' in df.columns:
        filtered_df = filtered_df[
            (filtered_df['Data'].dt.date >= date_range[0]) & 
            (filtered_df['Data'].dt.date <= date_range[1])
        ]
    for col, values in filters.items():
        filtered_df = filtered_df[filtered_df[col].isin(values)]
    
    # Scorecards
    st.header("📊 Business Metrics")
    cols = st.columns(4)
    
    with cols[0]:
        st.markdown(create_scorecard(
            "Total de Testes",
            len(filtered_df),
            variant="primary"
        ), unsafe_allow_html=True)
    
    with cols[1]:
        correct = len(filtered_df[filtered_df['Status'].str.contains('correto', case=False, na=False)])
        st.markdown(create_scorecard(
            "Taxa de Acerto",
            f"{correct/len(filtered_df):.1%}",
            f"+{correct} casos" if correct > 0 else "",
            variant="success"
        ), unsafe_allow_html=True)
    
    with cols[2]:
        errors = len(filtered_df[filtered_df['Status'].str.contains('incorreto|errado', case=False, na=False)])
        st.markdown(create_scorecard(
            "Erros Críticos",
            errors,
            f"{errors/len(filtered_df):.1%} do total" if errors > 0 else "",
            variant="danger"
        ), unsafe_allow_html=True)
    
    with cols[3]:
        partial = len(filtered_df[filtered_df['Status'].str.contains('parcial', case=False, na=False)])
        st.markdown(create_scorecard(
            "Casos Parciais",
            partial,
            f"Revisão necessária" if partial > 0 else "",
            variant="warning"
        ), unsafe_allow_html=True)
    
    # Análise Temporal
    if 'Data' in df.columns:
        st.header("📅 Tendência Temporal")
        trend_data = filtered_df.groupby(filtered_df['Data'].dt.date)['Status'].value_counts().unstack()
        st.area_chart(trend_data.fillna(0), use_container_width=True)
    
    # Tabela Interativa
    st.header("🔍 Análise Detalhada")
    
    # Agrupamento inteligente
    group_by = st.selectbox(
        "Agrupar por",
        [None] + [c for c in filtered_df.columns if c not in ['Valor extraído', 'Motivo Erro / Observação']]
    )
    
    if group_by:
        grouped_data = filtered_df.groupby(group_by).agg({
            'Status': lambda x: (x.str.contains('correto', case=False)).mean()
        }).rename(columns={'Status': 'Taxa de Acerto'})
        
        st.dataframe(
            grouped_data.style.format({'Taxa de Acerto': '{:.1%}'}),
            use_container_width=True
        )
    else:
        st.dataframe(
            filtered_df.style.applymap(
                lambda x: 'background-color: #ffcccc' if 'incorreto' in str(x).lower() else (
                    'background-color: #fff3cd' if 'parcial' in str(x).lower() else ''
                ),
                subset=['Status']
            ),
            height=600,
            use_container_width=True
        )
    
    # Exportação Avançada
    st.markdown("---")
    st.header("📤 Exportação de Resultados")
    
    export_cols = st.multiselect(
        "Selecione colunas para exportar",
        filtered_df.columns,
        default=filtered_df.columns.tolist()
    )
    
    export_format = st.radio(
        "Formato de exportação",
        ["Excel", "CSV"],
        horizontal=True
    )
    
    if st.button("Gerar Relatório"):
        with st.spinner("Preparando arquivo premium..."):
            buffer = BytesIO()
            if export_format == "Excel":
                filtered_df[export_cols].to_excel(buffer, index=False)
                st.download_button(
                    label="⬇️ Download Excel",
                    data=buffer.getvalue(),
                    file_name=f"relatorio_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                filtered_df[export_cols].to_csv(buffer, index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=buffer.getvalue(),
                    file_name=f"relatorio_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

# Rodapé Premium
st.markdown("---")
footer_cols = st.columns(3)
with footer_cols[1]:
    st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 12px;">
        <p>OCR/LLM Analytics Pro | Versão 2.0</p>
        <p>© 2023 AI Solutions - Todos os direitos reservados</p>
    </div>
    """, unsafe_allow_html=True)
