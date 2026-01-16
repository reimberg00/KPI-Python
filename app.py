import streamlit as st
import pandas as pd
import plotly.express as px

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

    /* Esconder o menu padrão do Streamlit para um visual mais limpo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO "À PROVA DE FALHAS" ---
def safe_load(file_path):
    try:
        if file_path.endswith('.xlsx'):
            return pd.read_excel(file_path).rename(columns=lambda x: x.strip())
        else:
            # Tenta ler CSV com diferentes codificações comuns em arquivos de sistema
            for encoding in ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']:
                try:
                    df = pd.read_csv(file_path, sep=None, engine='python', encoding=encoding)
                    df.columns = df.columns.str.strip()
                    return df
                except:
                    continue
        return pd.DataFrame()
    except:
        return pd.DataFrame()

# Tenta carregar os arquivos (ajustando para o seu ambiente)
df_zc = safe_load("Notas_ZC.xlsx")
# Tenta o Excel e o CSV enviado para QM
df_qm = safe_load("Notas_QM.xlsx")
if df_qm.empty:
    df_qm = safe_load("Notas_QM.xlsx - Planilha1.csv")

# Definição de Cores Consistentes
MAPA_CORES = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'
}

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("<br>", unsafe_allow_html=True)

# --- TRATAMENTO DOS DADOS ---
# ZC
if not df_zc.empty:
    c_data = "Data encermto." if "Data encermto." in df_zc.columns else df_zc.columns[0]
    df_zc['Data_Ref'] = pd.to_datetime(df_zc[c_data], errors='coerce')

# QM
if not df_qm.empty:
    c_data_q = "Modificado em" if "Modificado em" in df_qm.columns else "Dta.criação"
    df_qm['Data_Ref'] = pd.to_datetime(df_qm[c_data_q], errors='coerce')
    
    if 'Status' in df_qm.columns:
        df_qm['Status_Visual'] = df_qm['Status'].str.strip().map({'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'})
    
    equipe_remover = ['ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197']
    c_resp = "Responsável" if "Responsável" in df_qm.columns else df_qm.columns[4]
    df_qm = df_qm[~df_qm[c_resp].astype(str).str.strip().isin(equipe_remover)]

# --- FILTROS LATERAIS ---
st.sidebar.header("📅 Período de Análise")
df_zc_f, df_qm_f = df_zc.copy(), df_qm.copy()

if not df_zc.empty:
    try:
        limites = [df_zc['Data_Ref'].min().date(), df_zc['Data_Ref'].max().date()]
        data_zc = st.sidebar.date_input("Notas ZC:", limites, key="filter_zc")
        if len(data_zc) == 2:
            df_zc_f = df_zc[(df_zc['Data_Ref'].dt.date >= data_zc[0]) & (df_zc['Data_Ref'].dt.date <= data_zc[1])]
    except: pass

if not df_qm.empty:
    try:
        limites_q = [df_qm['Data_Ref'].min().date(), df_qm['Data_Ref'].max().date()]
        data_qm = st.sidebar.date_input("Medidas QM:", limites_q, key="filter_qm")
        if len(data_qm) == 2:
            df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= data_qm[0]) & (df_qm['Data_Ref'].dt.date <= data_qm[1])]
    except: pass

# --- INTERFACE ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

with tab1:
    if not df_zc_f.empty:
        st.subheader("🚀 Performance ZC")
        c1, c_central, c3 = st.columns([1, 1.5, 1]) # Reduz a largura do gráfico
        with c_central:
            s_col = 'Status sistema' if 'Status sistema' in df_zc_f.columns else df_zc_f.columns[3]
            enc = len(df_zc_f[df_zc_f[s_col] == 'ENCERRADO'])
            pen = len(df_zc[df_zc[s_col] == 'ABERTO'])
            
            mc1, mc2 = st.columns(2)
            mc1.metric("CONCLUÍDAS", enc)
            mc2.metric("PENDENTES", pen)
            
            fig_zc = px.bar(x=['ENCERRADO', 'ABERTO'], y=[enc, pen], text=[enc, pen],
                            color=['ENCERRADO', 'ABERTO'], color_discrete_map=MAPA_CORES, template="plotly_dark", height=320)
            fig_zc.update_traces(textfont=dict(size=18, font_weight="bold"), textposition='outside', width=0.4)
            fig_zc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_visible=False,
                                 xaxis=dict(tickfont=dict(size=14, font_weight="bold"), title=""))
            st.plotly_chart(fig_zc, use_container_width=True)
    else:
        st.warning("Aguardando carregamento dos dados ZC.")

with tab2:
    if not df_qm_f.empty:
        st.subheader("🎯 Visão Geral QM")
        m1, m2, g1 = st.columns([1, 1, 2])
        
        # Filtragem segura para as métricas
        val_e = len(df_qm_f[df_qm_f['Status'] == 'MEDE'])
        val_l = len(df_qm_f[df_qm_f['Status'] == 'MEDL'])
        
        m1.metric("ENCERRADAS", val_e)
        m2.metric("LIBERADAS", val_l)
        
        with g1:
            fig_pie = px.pie(names=['Encerradas', 'Liberadas'], values=[val_e, val_l],
                             hole=0.6, color=['Encerradas', 'Liberadas'],
                             color_discrete_map={'Encerradas': '#00F294', 'Liberadas': '#FF4B4B'},
                             template="plotly_dark", height=230)
            fig_pie.update_layout(margin=dict(t=10, b=10), legend=dict(font=dict(font_weight="bold")))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.subheader("🔧 Produtividade Detalhada por Responsável")
        
        c_r = "Responsável" if "Responsável" in df_qm_f.columns else df_qm_f.columns[4]
        df_agrupado = df_qm_f.groupby([c_r, 'Status_Visual']).size().reset_index(name='Qtd')
        
        fig_qm = px.bar(df_agrupado, x=c_r, y='Qtd', color='Status_Visual', text='Qtd',
                        barmode='group', color_discrete_map=MAPA_CORES, template="plotly_dark")
        fig_qm.update_traces(textfont=dict(size=14, font_weight="bold"), textposition='outside')
        fig_qm.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                             xaxis=dict(tickfont=dict(font_weight="bold"), tickangle=-45, title=""), 
                             yaxis_visible=False, bargap=0.3)
        st.plotly_chart(fig_qm, use_container_width=True)
    else:
        st.warning("Aguardando carregamento dos dados QM.")
