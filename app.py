import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Estratégia", layout="wide")

# --- ESTILIZAÇÃO CSS (MODERNO, DARK E NEGRITO) ---
st.markdown("""
    <style>
    /* Fundo Escuro */
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    
    /* Estilização dos Cards (Métricas) */
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.8);
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 148, 0.3);
        padding: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    
    /* Textos das Métricas em NEGRITO */
    [data-testid="stMetricValue"] { 
        font-size: 40px !important; 
        font-weight: 900 !important; 
        color: #00F294 !important; 
    }
    [data-testid="stMetricLabel"] { 
        font-size: 16px !important; 
        font-weight: 700 !important; 
        color: #ADB5BD !important;
        text-transform: uppercase;
    }

    /* Estilo das Abas */
    .stTabs [data-baseweb="tab"] {
        font-weight: 800 !important;
        font-size: 16px;
        color: #8B949E;
    }
    .stTabs [aria-selected="true"] { color: #00F294 !important; border-bottom: 2px solid #00F294 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0D1117; }
    
    /* Títulos */
    h1, h2, h3 { font-weight: 800 !important; }
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

df_zc = load_data("Notas_ZC.xlsx")
df_qm = load_data("Notas_QM.xlsx")

# Cores e Configurações
CORES_MAP = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'
}

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
        int_zc = st.sidebar.date_input("Período ZC:", [df_zc_valid['Data_Ref'].min().date(), df_zc_valid['Data_Ref'].max().date()], key="zc_date")
        if len(int_zc) == 2:
            df_zc_f = df_zc[(df_zc['Data_Ref'].dt.date >= int_zc[0]) & (df_zc['Data_Ref'].dt.date <= int_zc[1])]

df_qm_f = df_qm.copy()
if not df_qm.empty and 'Data_Ref' in df_qm.columns:
    df_qm_valid = df_qm.dropna(subset=['Data_Ref'])
    if not df_qm_valid.empty:
        int_qm = st.sidebar.date_input("Período QM:", [df_qm_valid['Data_Ref'].min().date(), df_qm_valid['Data_Ref'].max().date()], key="qm_date")
        if len(int_qm) == 2:
            df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= int_qm[0]) & (df_qm['Data_Ref'].dt.date <= int_qm[1])]

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

# --- ABA 1: NOTAS ZC (PROPORÇÃO REDUZIDA) ---
with tab1:
    if not df_zc_f.empty:
        st.subheader("🚀 Performance ZC")
        
        # Uso de colunas vazias nas laterais para achatar o gráfico no meio
        c_lado1, col_centro, c_lado2 = st.columns([1, 1.5, 1])
        
        with col_centro:
            enc = len(df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO'])
            pen = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
            
            # Cards de métrica
            m1, m2 = st.columns(2)
            m1.metric("CONCLUÍDAS", enc)
            m2.metric("PENDENTES", pen)
            
            df_p = pd.DataFrame({'Status': ['ENCERRADO', 'ABERTO'], 'Qtd': [enc, pen]})
            fig_zc = px.bar(df_p, x='Status', y='Qtd', text='Qtd', color='Status',
                            color_discrete_map=CORES_MAP, template="plotly_dark", height=300)
            
            # Formatação de texto em NEGRITO no gráfico
            fig_zc.update_traces(textfont=dict(size=16, font_weight="bold"), textposition='outside', width=0.4)
            fig_zc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                 yaxis_visible=False, xaxis=dict(tickfont=dict(size=14, font_weight="bold")))
            st.plotly_chart(fig_zc, use_container_width=True)

# --- ABA 2: MEDIDAS QM ---
with tab2:
    if not df_qm_f.empty:
        st.subheader("🎯 Visão Geral QM")
        
        col_m1, col_m2, col_g1 = st.columns([1, 1, 2])
        
        df_geral = df_qm_f['Status_Visual'].value_counts().reset_index()
        df_geral.columns = ['Status', 'Total']
        
        t_enc = df_geral[df_geral['Status'] == 'Medida Encerrada']['Total'].sum()
        t_lib = df_geral[df_geral['Status'] == 'Medida Liberada']['Total'].sum()
        
        with col_m1: st.metric("ENCERRADAS", int(t_enc))
        with col_m2: st.metric("LIBERADAS", int(t_lib))
        
        with col_g1:
            fig_pie = px.pie(df_geral, values='Total', names='Status', hole=0.6,
                             color='Status', color_discrete_map=CORES_MAP, template="plotly_dark", height=220)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True,
                                  legend=dict(font=dict(font_weight="bold")))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.subheader("🔧 Produtividade Detalhada")
        
        df_u = df_qm_f.groupby(['Responsável', 'Status_Visual']).size().reset_index(name='Qtd')
        df_u = df_u.sort_values(by='Qtd', ascending=False)

        fig_qm = px.bar(df_u, x='Responsável', y='Qtd', color='Status_Visual', text='Qtd',
                        barmode='group', color_discrete_map=CORES_MAP, template="plotly_dark")
        
        # Números e eixos em NEGRITO
        fig_qm.update_traces(textfont=dict(size=14, font_weight="bold"), textposition='outside')
        fig_qm.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                             xaxis=dict(tickfont=dict(font_weight="bold"), tickangle=-45), 
                             yaxis_visible=False, bargap=0.3)
        st.plotly_chart(fig_qm, use_container_width=True)
