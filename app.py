import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Estratégia", layout="wide")

# --- ESTILIZAÇÃO CSS (VISUAL IGUAL À IMAGEM - DARK & NEGRITO) ---
st.markdown("""
    <style>
    /* Fundo Escuro Total */
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    
    /* Cards de Métrica (Estilo Glassmorphism) */
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.9);
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 148, 0.3);
        padding: 20px;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.7);
    }
    
    /* Fontes em NEGRITO EXTREMO */
    [data-testid="stMetricValue"] { 
        font-size: 45px !important; 
        font-weight: 900 !important; 
        color: #00F294 !important; 
    }
    [data-testid="stMetricLabel"] { 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        color: #ADB5BD !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* Abas em Negrito e Verde Neon */
    .stTabs [data-baseweb="tab"] {
        font-weight: 900 !important;
        font-size: 18px !important;
        color: #8B949E;
    }
    .stTabs [aria-selected="true"] { color: #00F294 !important; border-bottom: 4px solid #00F294 !important; }

    /* Títulos Principais */
    h1, h2, h3 { font-weight: 900 !important; font-family: 'Inter', sans-serif; }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0D1117; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO INTELIGENTE (EVITA QUEBRAS) ---
def load_smart_data(base_name):
    # Lista de possíveis nomes de arquivo que o sistema pode ter
    possibilidades = [
        f"{base_name}.xlsx", f"{base_name}.csv", 
        f"{base_name}.xlsx - Planilha1.csv", f"{base_name.lower()}.xlsx"
    ]
    for arq in possibilidades:
        if os.path.exists(arq):
            try:
                if arq.endswith('.xlsx'):
                    df = pd.read_excel(arq)
                else:
                    df = pd.read_csv(arq, sep=None, engine='python', encoding='latin1')
                df.columns = df.columns.str.strip() # Remove espaços nos nomes das colunas
                return df
            except: continue
    return pd.DataFrame()

# Carregamento dos dados
df_zc = load_smart_data("Notas_ZC")
df_qm = load_smart_data("Notas_QM")

# Cores Neon
CORES_DASH = {'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294', 'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'}

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("---")

# --- TRATAMENTO SEGURO DE DADOS ---
if not df_zc.empty:
    col_d = "Data encermto." if "Data encermto." in df_zc.columns else df_zc.columns[0]
    df_zc['Data_Ref'] = pd.to_datetime(df_zc[col_d], errors='coerce')

if not df_qm.empty:
    col_dq = "Modificado em" if "Modificado em" in df_qm.columns else "Dta.criação"
    df_qm['Data_Ref'] = pd.to_datetime(df_qm[col_dq], errors='coerce')
    
    # Mapeamento de Status QM
    if 'Status' in df_qm.columns:
        df_qm['Status_Visual'] = df_qm['Status'].str.strip().map({'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'})
    
    # Filtro de Equipe (Responsável)
    equipe_ignorar = ['ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197']
    col_resp = "Responsável" if "Responsável" in df_qm.columns else "Modificado por"
    df_qm = df_qm[~df_qm[col_resp].astype(str).str.strip().isin(equipe_ignorar)]

# --- BARRA LATERAL ---
st.sidebar.header("📅 Filtros de Data")
df_zc_f, df_qm_f = df_zc.copy(), df_qm.copy()

def filter_date(df, key):
    if not df.empty and 'Data_Ref' in df.columns:
        df_v = df.dropna(subset=['Data_Ref'])
        if not df_v.empty:
            sel = st.sidebar.date_input(f"Período {key}:", [df_v['Data_Ref'].min().date(), df_v['Data_Ref'].max().date()], key=key)
            if len(sel) == 2:
                return df[(df['Data_Ref'].dt.date >= sel[0]) & (df['Data_Ref'].dt.date <= sel[1])]
    return df

df_zc_f = filter_date(df_zc_f, "ZC")
df_qm_f = filter_date(df_qm_f, "QM")

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

# ABA 1: NOTAS ZC (PROPORÇÃO REDUZIDA)
with tab1:
    if not df_zc_f.empty:
        st.subheader("🚀 Performance de Manutenção")
        l_v, central, r_v = st.columns([1, 1.5, 1]) # Mantém o gráfico centralizado e menor
        with central:
            col_st = 'Status sistema' if 'Status sistema' in df_zc_f.columns else df_zc_f.columns[3]
            enc = len(df_zc_f[df_zc_f[col_st] == 'ENCERRADO'])
            pen = len(df_zc[df_zc[col_st] == 'ABERTO']) # Backlog total
            
            m_c1, m_c2 = st.columns(2)
            m_c1.metric("CONCLUÍDAS", enc)
            m_c2.metric("PENDENTES", pen)
            
            fig_zc = px.bar(x=['ENCERRADO', 'ABERTO'], y=[enc, pen], text=[enc, pen],
                            color=['ENCERRADO', 'ABERTO'], color_discrete_map=CORES_DASH, template="plotly_dark", height=350)
            fig_zc.update_traces(textfont=dict(size=20, font_weight="bold"), textposition='outside', width=0.3)
            fig_zc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_visible=False,
                                 xaxis=dict(tickfont=dict(size=14, font_weight="bold"), title=""))
            st.plotly_chart(fig_zc, use_container_width=True)
    else: st.warning("Aguardando arquivo Notas_ZC.xlsx")

# ABA 2: MEDIDAS QM (VISUAL PREMIUM)
with tab2:
    if not df_qm_f.empty:
        st.subheader("🎯 Visão Geral da Qualidade")
        
        c_m1, c_m2, c_g1 = st.columns([1, 1, 2])
        t_e = len(df_qm_f[df_qm_f['Status'] == 'MEDE'])
        t_l = len(df_qm_f[df_qm_f['Status'] == 'MEDL'])
        
        c_m1.metric("ENCERRADAS", t_e)
        c_m2.metric("LIBERADAS", t_l)
        
        with c_g1:
            fig_pie = px.pie(names=['Encerradas', 'Liberadas'], values=[t_e, t_l], hole=0.7,
                             color=['Encerradas', 'Liberadas'], color_discrete_map={'Encerradas': '#00F294', 'Liberadas': '#FF4B4B'},
                             template="plotly_dark", height=230)
            fig_pie.update_layout(margin=dict(t=10, b=10, l=0, r=0), legend=dict(font=dict(font_weight="bold", size=14)))
            fig_pie.update_traces(textinfo='none') # Limpo igual à imagem
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.subheader("🔧 Produtividade Detalhada por Responsável")
        
        c_resp_final = "Responsável" if "Responsável" in df_qm_f.columns else df_qm_f.columns[4]
        df_agrup = df_qm_f.groupby([c_resp_final, 'Status_Visual']).size().reset_index(name='Qtd')
        df_agrup = df_agrup.sort_values(by='Qtd', ascending=False)

        fig_qm = px.bar(df_agrup, x=c_resp_final, y='Qtd', color='Status_Visual', text='Qtd',
                        barmode='group', color_discrete_map=CORES_DASH, template="plotly_dark")
        
        fig_qm.update_traces(textfont=dict(size=15, font_weight="bold"), textposition='outside')
        fig_qm.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                             xaxis=dict(tickfont=dict(font_weight="bold", size=12), tickangle=-45, title=""), 
                             yaxis_visible=False, bargap=0.3)
        st.plotly_chart(fig_qm, use_container_width=True)
    else: st.warning("Aguardando arquivo Notas_QM.xlsx")
