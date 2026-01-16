import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página e Tema
st.set_page_config(page_title="Dashboard Estratégia", layout="wide")

# --- ESTILIZAÇÃO CSS (MODERNO/DARK) ---
st.markdown("""
    <style>
    /* Fundo principal azul-noite */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Estilização dos Cards de Métrica */
    div[data-testid="stMetric"] {
        background-color: #161B22;
        padding: 15px;
        border-radius: 12px;
        border: 1px solid #30363D;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.5);
    }
    [data-testid="stMetricValue"] { font-size: 32px; font-weight: bold; color: #00F294 !important; }
    [data-testid="stMetricLabel"] { font-size: 16px; color: #ADB5BD !important; }
    
    /* Abas estilizadas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #161B22;
        border-radius: 8px 8px 0px 0px;
        color: white;
    }
    .stTabs [aria-selected="true"] { background-color: #00F294 !important; color: #000 !important; }

    /* Divisores */
    hr { border: 0.1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("---")

# --- FUNÇÕES DE CARREGAMENTO ---
def load_data(file_name):
    try:
        if file_name.endswith('.xlsx'): df = pd.read_excel(file_name)
        else: df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

# Carregamento
df_zc = load_data("Notas_ZC.xlsx")
df_qm = load_data("Notas_QM.xlsx")

# Configuração de Cores e Tema dos Gráficos
CORES_MAP = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'
}
TEMPLATE_GRAFICO = "plotly_dark"

# --- PROCESSAMENTO ZC ---
if not df_zc.empty:
    col_data_zc = "Data encermto."
    if col_data_zc in df_zc.columns:
        df_zc['Data_Ref'] = pd.to_datetime(df_zc[col_data_zc], errors='coerce')
    else:
        df_zc['Data_Ref'] = pd.to_datetime(df_zc.iloc[:, 6], errors='coerce')

# --- PROCESSAMENTO QM ---
if not df_qm.empty:
    df_qm['Data_Ref'] = pd.to_datetime(df_qm['Modificado em'], errors='coerce')
    map_status = {'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'}
    df_qm['Status_Visual'] = df_qm['Status'].astype(str).str.strip().map(map_status)
    
    usuarios_remover = ['ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197']
    df_qm = df_qm[~df_qm['Responsável'].astype(str).str.strip().isin(usuarios_remover)]

# --- BARRA LATERAL ---
st.sidebar.title("📅 Filtros de Período")

df_zc_f = df_zc.copy()
if not df_zc.empty and 'Data_Ref' in df_zc.columns:
    df_zc_valid = df_zc.dropna(subset=['Data_Ref'])
    if not df_zc_valid.empty:
        min_z, max_z = df_zc_valid['Data_Ref'].min().date(), df_zc_valid['Data_Ref'].max().date()
        int_zc = st.sidebar.date_input("Período ZC:", [min_z, max_z], key="zc_date")
        if len(int_zc) == 2:
            df_zc_f = df_zc[(df_zc['Data_Ref'].dt.date >= int_zc[0]) & (df_zc['Data_Ref'].dt.date <= int_zc[1])]

df_qm_f = df_qm.copy()
if not df_qm.empty and 'Data_Ref' in df_qm.columns:
    df_qm_valid = df_qm.dropna(subset=['Data_Ref'])
    if not df_qm_valid.empty:
        min_q, max_q = df_qm_valid['Data_Ref'].min().date(), df_qm_valid['Data_Ref'].max().date()
        int_qm = st.sidebar.date_input("Período QM:", [min_q, max_q], key="qm_date")
        if len(int_qm) == 2:
            df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= int_qm[0]) & (df_qm['Data_Ref'].dt.date <= int_qm[1])]

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

# ABA 1: NOTAS ZC (PROPORÇÃO MENOR)
with tab1:
    if not df_zc_f.empty:
        st.subheader("🚀 Performance de Manutenção")
        
        # Centralizando e reduzindo a largura com colunas
        c_vazia1, col_central, c_vazia2 = st.columns([1, 2, 1])
        
        with col_central:
            enc = len(df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO'])
            pen = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
            
            mc1, mc2 = st.columns(2)
            mc1.metric("Concluídas", enc)
            mc2.metric("Pendentes", pen)
            
            df_z_p = pd.DataFrame({'Status': ['ENCERRADO', 'ABERTO'], 'Qtd': [enc, pen]})
            fig_zc = px.bar(df_z_p, x='Status', y='Qtd', text='Qtd', color='Status',
                            color_discrete_map=CORES_MAP, template=TEMPLATE_GRAFICO, height=300)
            fig_zc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
            st.plotly_chart(fig_zc, use_container_width=True)
    else:
        st.warning("Dados ZC indisponíveis.")

# ABA 2: MEDIDAS QM (VISUAL MODERNO)
with tab2:
    if not df_qm_f.empty:
        st.subheader("🎯 Visão Geral da Qualidade")
        
        # Grid de Topo
        col_m1, col_m2, col_g1 = st.columns([1, 1, 2])
        
        df_geral = df_qm_f['Status_Visual'].value_counts().reset_index()
        df_geral.columns = ['Status', 'Total']
        
        t_enc = df_geral[df_geral['Status'] == 'Medida Encerrada']['Total'].sum()
        t_lib = df_geral[df_geral['Status'] == 'Medida Liberada']['Total'].sum()
        
        with col_m1: st.metric("Encerradas", int(t_enc))
        with col_m2: st.metric("Liberadas", int(t_lib))
        with col_g1:
            fig_pie = px.pie(df_geral, values='Total', names='Status', hole=0.6,
                             color='Status', color_discrete_map=CORES_MAP, template=TEMPLATE_GRAFICO, height=220)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🔧 Produtividade Detalhada")
        
        df_u = df_qm_f.groupby(['Responsável', 'Status_Visual']).size().reset_index(name='Qtd')
        fig_u = px.bar(df_u, x='Responsável', y='Qtd', color='Status_Visual', text='Qtd',
                       barmode='group', color_discrete_map=CORES_MAP, template=TEMPLATE_GRAFICO)
        fig_u.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-45)
        st.plotly_chart(fig_u, use_container_width=True)
