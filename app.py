import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Manutenção Integrado", layout="wide")

# --- CSS PARA FORMATAR AS MÉTRICAS DO STREAMLIT (TEXTO GRANDE, BRANCO E NEGRITO) ---
st.markdown("""
    <style>
    /* Estilo dos números das métricas */
    [data-testid="stMetricValue"] { 
        font-size: 45px !important; 
        font-weight: 900 !important; 
        color: #FFFFFF !important; 
    }
    /* Estilo dos rótulos (labels) das métricas */
    [data-testid="stMetricLabel"] { 
        font-size: 20px !important; 
        font-weight: 800 !important; 
        color: #FFFFFF !important; 
    }
    /* Títulos de abas e headers */
    .stTabs [data-baseweb="tab"] { font-weight: 800 !important; font-size: 18px !important; }
    h1, h2, h3 { font-weight: 900 !important; color: #FFFFFF !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("---")

# --- FUNÇÕES DE CARREGAMENTO ---
def load_data(file_name):
    try:
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(file_name)
        else:
            df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {file_name}: {e}")
        return pd.DataFrame()

df_zc = load_data("Notas_ZC.xlsx")
df_qm = load_data("Notas_QM.xlsx")

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
    
    usuarios_remover = [
        'ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 
        'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197'
    ]
    df_qm = df_qm[~df_qm['Responsável'].astype(str).str.strip().isin(usuarios_remover)]

# --- BARRA LATERAL ---
st.sidebar.title("Filtros de Período")
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

tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

# ABA 1: NOTAS ZC
with tab1:
    if not df_zc_f.empty:
        st.subheader("🚀 Performance ZC")
        enc = len(df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO'])
        pen = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
        
        c1, c2 = st.columns(2)
        c1.metric("CONCLUÍDAS", enc)
        c2.metric("PENDENTES", pen)
        
        df_zc_plot = pd.DataFrame({'Status': ['ENCERRADO', 'ABERTO'], 'Qtd': [enc, pen]})
        fig_zc = px.bar(df_zc_plot, x='Status', y='Qtd', text='Qtd', color='Status',
                        color_discrete_map=CORES_MAP, template="plotly_dark")
        
        # --- FORMATAÇÃO DOS DADOS NO GRÁFICO ZC ---
        fig_zc.update_traces(
            textfont=dict(size=22, color='white', family='Arial Black'),
            textposition='outside'
        )
        fig_zc.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(size=18, color='white', family='Arial Black'), title=""),
            yaxis_visible=False
        )
        st.plotly_chart(fig_zc, use_container_width=True)

# ABA 2: MEDIDAS QM
with tab2:
    if not df_qm_f.empty:
        st.subheader("🎯 Visão Geral QM")
        df_geral_qm = df_qm_f['Status_Visual'].value_counts().reset_index()
        df_geral_qm.columns = ['Status', 'Total']
        
        col_m1, col_m2, col_g1 = st.columns([1, 1, 2])
        t_e = df_geral_qm[df_geral_qm['Status'] == 'Medida Encerrada']['Total'].sum()
        t_l = df_geral_qm[df_geral_qm['Status'] == 'Medida Liberada']['Total'].sum()
        
        with col_m1: st.metric("ENCERRADAS", int(t_e))
        with col_m2: st.metric("LIBERADAS", int(t_l))
        
        with col_g1:
            fig_donut = px.pie(df_geral_qm, values='Total', names='Status', hole=0.5,
                               color='Status', color_discrete_map=CORES_MAP, height=280, template="plotly_dark")
            
            # --- FORMATAÇÃO DOS DADOS NO GRÁFICO DONUT ---
            fig_donut.update_traces(
                textinfo='percent+label',
                textfont=dict(size=18, color='white', family='Arial Black')
            )
            fig_donut.update_layout(showlegend=False, margin=dict(t=30, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("---")
        st.subheader("🔧 Produtividade Detalhada por Responsável")
        df_u = df_qm_f.groupby(['Responsável', 'Status_Visual']).size().reset_index(name='Qtd')
        df_u = df_u.sort_values(by='Qtd', ascending=False)

        fig_qm = px.bar(df_u, x='Responsável', y='Qtd', color='Status_Visual', text='Qtd',
                        barmode='group', color_discrete_map=CORES_MAP, template="plotly_dark")
        
        # --- FORMATAÇÃO DOS DADOS NO GRÁFICO DE BARRAS QM ---
        fig_qm.update_traces(
            textfont=dict(size=18, color='white', family='Arial Black'),
            textposition='outside'
        )
        fig_qm.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(size=14, color='white', family='Arial Black'), title=""),
            yaxis_visible=False,
            legend=dict(font=dict(size=14, color='white', family='Arial Black'))
        )
        st.plotly_chart(fig_qm, use_container_width=True)
