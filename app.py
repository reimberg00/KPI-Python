import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Estratégia", layout="wide")

# --- ESTILIZAÇÃO CSS PREMIUM (FOCO EM NEGRITO E VISIBILIDADE) ---
st.markdown("""
    <style>
    .stApp { background-color: #0B0E14; color: #FFFFFF; }
    
    /* Cards de Métrica */
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.8);
        border-radius: 15px;
        border: 1px solid rgba(0, 242, 148, 0.3);
        padding: 20px;
    }
    
    /* Textos em NEGRITO EXTREMO */
    [data-testid="stMetricValue"] { 
        font-size: 42px !important; 
        font-weight: 900 !important; 
        color: #00F294 !important; 
    }
    [data-testid="stMetricLabel"] { 
        font-size: 16px !important; 
        font-weight: 800 !important; 
        color: #ADB5BD !important;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 800 !important;
        font-size: 18px !important;
    }
    h1, h2, h3 { font-weight: 900 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE CARREGAMENTO ROBUSTA ---
def load_file(name):
    try:
        # Tenta Excel, depois CSV
        try:
            df = pd.read_excel(name)
        except:
            # Se falhar Excel, tenta CSV (comum em exportações do SAP)
            df = pd.read_csv(name, sep=None, engine='python', on_bad_lines='skip')
        
        # Limpeza essencial
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

# Tenta carregar os arquivos (ajustado para os nomes padrão)
df_zc = load_file("Notas_ZC.xlsx")
df_qm = load_file("Notas_QM.xlsx")

# Se o Notas_QM.xlsx não existir, tenta o nome que o sistema costuma gerar no upload
if df_qm.empty:
    df_qm = load_file("Notas_QM.xlsx - Planilha1.csv")

# Cores do Dashboard
CORES = {'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294', 'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'}

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("---")

# --- PROCESSAMENTO SEGURO ---
# ZC
if not df_zc.empty:
    col_data_zc = "Data encermto."
    if col_data_zc in df_zc.columns:
        df_zc['Data_Ref'] = pd.to_datetime(df_zc[col_data_zc], errors='coerce')
    else:
        df_zc['Data_Ref'] = pd.to_datetime(df_zc.iloc[:, 0], errors='coerce') # Fallback

# QM
if not df_qm.empty:
    # Ajusta data usando "Modificado em" ou similar
    col_data_qm = "Modificado em" if "Modificado em" in df_qm.columns else "Dta.criação"
    df_qm['Data_Ref'] = pd.to_datetime(df_qm[col_data_qm], errors='coerce')
    
    # Mapeamento de Status
    if 'Status' in df_qm.columns:
        df_qm['Status_Visual'] = df_qm['Status'].str.strip().map({'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'})
    
    # Filtro de Usuários
    usuarios_remover = ['ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197']
    col_resp = "Responsável" if "Responsável" in df_qm.columns else "Modificado por"
    df_qm = df_qm[~df_qm[col_resp].astype(str).str.strip().isin(usuarios_remover)]

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("📅 Filtros")
df_zc_f = df_zc.copy()
df_qm_f = df_qm.copy()

if not df_zc.empty and 'Data_Ref' in df_zc.columns:
    val_zc = df_zc.dropna(subset=['Data_Ref'])
    if not val_zc.empty:
        int_zc = st.sidebar.date_input("Período ZC:", [val_zc['Data_Ref'].min().date(), val_zc['Data_Ref'].max().date()], key="z")
        if isinstance(int_zc, list) and len(int_zc) == 2:
            df_zc_f = df_zc[(df_zc['Data_Ref'].dt.date >= int_zc[0]) & (df_zc['Data_Ref'].dt.date <= int_zc[1])]

if not df_qm.empty and 'Data_Ref' in df_qm.columns:
    val_qm = df_qm.dropna(subset=['Data_Ref'])
    if not val_qm.empty:
        int_qm = st.sidebar.date_input("Período QM:", [val_qm['Data_Ref'].min().date(), val_qm['Data_Ref'].max().date()], key="q")
        if isinstance(int_qm, list) and len(int_qm) == 2:
            df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= int_qm[0]) & (df_qm['Data_Ref'].dt.date <= int_qm[1])]

# --- CONSTRUÇÃO DAS ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

with tab1:
    if not df_zc_f.empty and 'Status sistema' in df_zc_f.columns:
        st.subheader("🚀 Performance ZC")
        c_l1, col_c, c_l2 = st.columns([1, 1.5, 1]) # Proporção reduzida
        with col_c:
            enc = len(df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO'])
            pen = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
            m1, m2 = st.columns(2)
            m1.metric("CONCLUÍDAS", enc)
            m2.metric("PENDENTES", pen)
            
            df_p = pd.DataFrame({'Status': ['ENCERRADO', 'ABERTO'], 'Qtd': [enc, pen]})
            fig_zc = px.bar(df_p, x='Status', y='Qtd', text='Qtd', color='Status',
                            color_discrete_map=CORES, template="plotly_dark", height=350)
            fig_zc.update_traces(textfont=dict(size=18, font_weight="bold"), textposition='outside', width=0.4)
            fig_zc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', yaxis_visible=False,
                                 xaxis=dict(tickfont=dict(size=14, font_weight="bold")))
            st.plotly_chart(fig_zc, use_container_width=True)
    else:
        st.warning("Aguardando arquivo Notas_ZC.xlsx ou coluna 'Status sistema' não encontrada.")

with tab2:
    if not df_qm_f.empty and 'Status_Visual' in df_qm_f.columns:
        st.subheader("🎯 Visão Geral QM")
        col_m1, col_m2, col_g1 = st.columns([1, 1, 2])
        
        t_enc = len(df_qm_f[df_qm_f['Status'] == 'MEDE'])
        t_lib = len(df_qm_f[df_qm_f['Status'] == 'MEDL'])
        
        col_m1.metric("ENCERRADAS", t_enc)
        col_m2.metric("LIBERADAS", t_lib)
        
        with col_g1:
            fig_pie = px.pie(names=['Encerradas', 'Liberadas'], values=[t_enc, t_lib],
                             hole=0.6, color=['Encerradas', 'Liberadas'],
                             color_discrete_map={'Encerradas': '#00F294', 'Liberadas': '#FF4B4B'},
                             template="plotly_dark", height=230)
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), legend=dict(font=dict(font_weight="bold")))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        st.subheader("🔧 Produtividade Detalhada")
        
        col_resp_final = "Responsável" if "Responsável" in df_qm_f.columns else "Modificado por"
        df_u = df_qm_f.groupby([col_resp_final, 'Status_Visual']).size().reset_index(name='Qtd')
        
        fig_qm = px.bar(df_u, x=col_resp_final, y='Qtd', color='Status_Visual', text='Qtd',
                        barmode='group', color_discrete_map=CORES, template="plotly_dark")
        fig_qm.update_traces(textfont=dict(size=14, font_weight="bold"), textposition='outside')
        fig_qm.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                             xaxis=dict(tickfont=dict(font_weight="bold"), tickangle=-45), 
                             yaxis_visible=False, bargap=0.3)
        st.plotly_chart(fig_qm, use_container_width=True)
    else:
        st.warning("Aguardando arquivo Notas_QM.xlsx com colunas 'Status' e 'Responsável'.")
