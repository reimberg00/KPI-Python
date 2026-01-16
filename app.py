import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Estratégia", layout="wide")

# --- ESTILIZAÇÃO CSS (IGUAL À IMAGEM - DARK, PREMIUM E NEGRITO) ---
st.markdown("""
    <style>
    /* Fundo Totalmente Escuro */
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    
    /* Estilização dos Cards (Glassmorphism) */
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.85);
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 148, 0.25);
        padding: 20px;
        box-shadow: 0px 8px 16px rgba(0,0,0,0.6);
    }
    
    /* Fontes em NEGRITO EXTREMO */
    [data-testid="stMetricValue"] { 
        font-size: 44px !important; 
        font-weight: 900 !important; 
        color: #00F294 !important; 
    }
    [data-testid="stMetricLabel"] { 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        color: #ADB5BD !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Abas em Negrito */
    .stTabs [data-baseweb="tab"] {
        font-weight: 800 !important;
        font-size: 18px !important;
        color: #8B949E;
    }
    .stTabs [aria-selected="true"] { color: #00F294 !important; border-bottom: 3px solid #00F294 !important; }

    /* Títulos em Negrito */
    h1, h2, h3 { font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO INTELIGENTE ---
def carregar_dados(caminho_base):
    # Tenta XLSX primeiro, depois CSV
    for ext in ['.xlsx', '.csv']:
        arq = caminho_base + ext
        if os.path.exists(arq):
            try:
                if ext == '.xlsx':
                    df = pd.read_excel(arq)
                else:
                    df = pd.read_csv(arq, sep=None, engine='python', encoding='latin1')
                df.columns = df.columns.str.strip() # Remove espaços dos nomes
                return df
            except:
                continue
    # Caso específico para o arquivo de teste que você enviou
    if "Notas_QM" in caminho_base and os.path.exists("Notas_QM.xlsx - Planilha1.csv"):
        df = pd.read_csv("Notas_QM.xlsx - Planilha1.csv", sep=',', encoding='utf-8')
        df.columns = df.columns.str.strip()
        return df
    return pd.DataFrame()

# Carregar arquivos
df_zc = carregar_dados("Notas_ZC")
df_qm = carregar_dados("Notas_QM")

# Cores do Dashboard
MAPA_CORES = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encurrada': '#00F294', # Ajustado para o nome comum
    'Medida Encerrada': '#00F294'
}

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("<br>", unsafe_allow_html=True)

# --- PROCESSAMENTO ZC ---
if not df_zc.empty:
    col_data = "Data encermto." if "Data encermto." in df_zc.columns else df_zc.columns[0]
    df_zc['Data_Ref'] = pd.to_datetime(df_zc[col_data], errors='coerce')

# --- PROCESSAMENTO QM ---
if not df_qm.empty:
    col_data_q = "Modificado em" if "Modificado em" in df_qm.columns else "Dta.criação"
    df_qm['Data_Ref'] = pd.to_datetime(df_qm[col_data_q], errors='coerce')
    
    if 'Status' in df_qm.columns:
        df_qm['Status_Visual'] = df_qm['Status'].str.strip().map({'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'})
    
    # Filtro de Equipe
    equipe_remover = ['ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197']
    col_resp = "Responsável" if "Responsável" in df_qm.columns else "Modificado por"
    df_qm = df_qm[~df_qm[col_resp].astype(str).str.strip().isin(equipe_remover)]

# --- BARRA LATERAL ---
st.sidebar.header("📅 Filtros de Período")
df_zc_f, df_qm_f = df_zc.copy(), df_qm.copy()

if not df_zc.empty and not df_zc['Data_Ref'].isnull().all():
    sel_zc = st.sidebar.date_input("Notas ZC:", [df_zc['Data_Ref'].min().date(), df_zc['Data_Ref'].max().date()], key="z")
    if len(sel_zc) == 2:
        df_zc_f = df_zc[(df_zc['Data_Ref'].dt.date >= sel_zc[0]) & (df_zc['Data_Ref'].dt.date <= sel_zc[1])]

if not df_qm.empty and not df_qm['Data_Ref'].isnull().all():
    sel_qm = st.sidebar.date_input("Medidas QM:", [df_qm['Data_Ref'].min().date(), df_qm['Data_Ref'].max().date()], key="q")
    if len(sel_qm) == 2:
        df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= sel_qm[0]) & (df_qm['Data_Ref'].dt.date <= sel_qm[1])]

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

with tab1:
    if not df_zc_f.empty:
        st.subheader("🚀 Performance ZC")
        # Layout centralizado e menor
        l1, central, l3 = st.columns([1, 1.5, 1])
        with central:
            col_st = 'Status sistema' if 'Status sistema' in df_zc_f.columns else df_zc_f.columns[3]
            enc = len(df_zc_f[df_zc_f[col_st] == 'ENCERRADO'])
            pen = len(df_zc[df_zc[col_st] == 'ABERTO'])
            
            c1, c2 = st.columns(2)
            c1.metric("CONCLUÍDAS", enc)
            c2.metric("PENDENTES", pen)
            
            fig_zc = px.bar(x=['ENCERRADO', 'ABERTO'], y=[enc, pen], text=[enc, pen],
                            color=['ENCERRADO', 'ABERTO'], color_discrete_map=MAPA_CORES, template="plotly_dark", height=320)
            fig_zc.update_traces(textfont=dict(size=18, font_weight="bold"), textposition='outside', width=0.3)
            fig_zc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_visible=False,
                                 xaxis=dict(tickfont=dict(size=14, font_weight="bold"), title=""))
            st.plotly_chart(fig_zc, use_container_width=True)
    else:
        st.warning("Aguardando arquivo Notas_ZC.xlsx")

with tab2:
    if not df_qm_f.empty:
        st.subheader("🎯 Visão Geral QM")
        m1, m2, g1 = st.columns([1, 1, 2])
        
        t_enc = len(df_qm_f[df_qm_f['Status'] == 'MEDE'])
        t_lib = len(df_qm_f[df_qm_f['Status'] == 'MEDL'])
        
        m1.metric("ENCERRADAS", t_enc)
        m2.metric("LIBERADAS", t_lib)
        
        with g1:
            fig_pie = px.pie(names=['Encerradas', 'Liberadas'], values=[t_enc, t_lib],
                             hole=0.6, color=['Encerradas', 'Liberadas'],
                             color_discrete_map={'Encerradas': '#00F294', 'Liberadas': '#FF4B4B'},
                             template="plotly_dark", height=230)
            fig_pie.update_layout(margin=dict(t=10, b=10), legend=dict(font=dict(font_weight="bold")))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.subheader("🔧 Produtividade por Responsável")
        
        c_resp_qm = "Responsável" if "Responsável" in df_qm_f.columns else df_qm_f.columns[4]
        df_agrup = df_qm_f.groupby([c_resp_qm, 'Status_Visual']).size().reset_index(name='Qtd')
        
        fig_qm = px.bar(df_agrup, x=c_resp_qm, y='Qtd', color='Status_Visual', text='Qtd',
                        barmode='group', color_discrete_map=MAPA_CORES, template="plotly_dark")
        fig_qm.update_traces(textfont=dict(size=14, font_weight="bold"), textposition='outside')
        fig_qm.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                             xaxis=dict(tickfont=dict(font_weight="bold"), tickangle=-45, title=""), 
                             yaxis_visible=False, bargap=0.3)
        st.plotly_chart(fig_qm, use_container_width=True)
    else:
        st.warning("Aguardando arquivo Notas_QM.xlsx")
