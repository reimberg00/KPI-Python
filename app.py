import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração de Página
st.set_page_config(page_title="Dashboard Estratégia", layout="wide")

# --- CSS PARA DEIXAR IGUAL À IMAGEM (ESTILO DARK/PREMIUM) ---
st.markdown("""
    <style>
    /* Fundo escuro total */
    .stApp { background-color: #0B0E14; color: #E0E0E0; }
    
    /* Estilização dos Cards (Métricas) */
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 34, 0.7);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px;
        transition: transform 0.3s;
    }
    div[data-testid="stMetric"]:hover { transform: translateY(-5px); border-color: #00F294; }

    /* Customização dos textos das métricas */
    [data-testid="stMetricValue"] { font-size: 38px !important; color: #00F294 !important; font-family: 'Inter', sans-serif; }
    [data-testid="stMetricLabel"] { font-size: 14px !important; color: #8B949E !important; text-transform: uppercase; letter-spacing: 1px; }

    /* Estilo das Abas */
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] {
        color: #8B949E;
        background-color: transparent;
        font-weight: 600;
        border-bottom: 2px solid transparent;
    }
    .stTabs [aria-selected="true"] { color: #00F294 !important; border-bottom: 2px solid #00F294 !important; }

    /* Barra Lateral */
    [data-testid="stSidebar"] { background-color: #0D1117; border-right: 1px solid #30363D; }
    
    /* Títulos */
    h1, h2, h3 { font-family: 'Inter', sans-serif; font-weight: 700; color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES DE CARREGAMENTO ---
def load_data(file_name):
    try:
        if file_name.endswith('.xlsx'): df = pd.read_excel(file_name)
        else: df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

df_zc = load_data("Notas_ZC.xlsx")
df_qm = load_data("Notas_QM.xlsx")

# Cores e Template
CORES = {'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294', 'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'}

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("<br>", unsafe_allow_html=True)

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

# ABA 1: NOTAS ZC (REDUZIDO E LIMPO)
with tab1:
    if not df_zc.empty:
        st.subheader("🚀 Visão Geral ZC")
        c1, c2, c3 = st.columns([1, 1.5, 1]) # Ocupa o centro
        with c2:
            enc = len(df_zc[df_zc['Status sistema'] == 'ENCERRADO'])
            pen = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
            
            # Cards lado a lado
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("CONCLUÍDAS", enc)
            col_m2.metric("PENDENTES", pen)
            
            # Gráfico Minimalista
            df_z = pd.DataFrame({'Status': ['ENCERRADO', 'ABERTO'], 'Qtd': [enc, pen]})
            fig_zc = px.bar(df_z, x='Status', y='Qtd', text='Qtd', color='Status',
                            color_discrete_map=CORES, template="plotly_dark", height=300)
            fig_zc.update_traces(marker_line_width=0, textposition='outside', width=0.4)
            fig_zc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
                                 yaxis_visible=False, xaxis_title="", showlegend=False)
            st.plotly_chart(fig_zc, use_container_width=True)

# ABA 2: MEDIDAS QM (FIEL À IMAGEM)
with tab2:
    if not df_qm.empty:
        # Processamento QM
        df_qm['Status_Visual'] = df_qm['Status'].str.strip().map({'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'})
        
        st.subheader("🎯 Visão Geral QM")
        
        # Grid superior: Métricas e Rosca
        m1, m2, g1 = st.columns([1, 1, 2])
        
        total_e = len(df_qm[df_qm['Status'] == 'MEDE'])
        total_l = len(df_qm[df_qm['Status'] == 'MEDL'])
        
        m1.metric("ENCERRADAS", total_e)
        m2.metric("LIBERADAS", total_l)
        
        with g1:
            fig_pie = px.pie(names=['Encerradas', 'Liberadas'], values=[total_e, total_l],
                             hole=0.7, color=['Encerradas', 'Liberadas'],
                             color_discrete_map={'Encerradas': '#00F294', 'Liberadas': '#FF4B4B'})
            fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=200, 
                                  paper_bgcolor='rgba(0,0,0,0)', showlegend=True, template="plotly_dark")
            fig_pie.update_traces(textinfo='none') # Limpo igual à imagem
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("🔧 Produtividade Detalhada")
        
        df_u = df_qm.groupby(['Responsável', 'Status_Visual']).size().reset_index(name='Qtd')
        fig_u = px.bar(df_u, x='Responsável', y='Qtd', color='Status_Visual', text='Qtd',
                       barmode='group', color_discrete_map=CORES, template="plotly_dark")
        
        # Estilização das Barras para o estilo "Moderno"
        fig_u.update_traces(marker_line_width=0, textposition='outside')
        fig_u.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)', 
            xaxis_tickangle=-45,
            yaxis_visible=False, # Eixo Y oculto para visual mais limpo
            bargap=0.3
        )
        st.plotly_chart(fig_u, use_container_width=True)
