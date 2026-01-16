import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Manutenção Integrado", layout="wide")

# --- ESTILIZAÇÃO CSS PARA AS MÉTRICAS DO STREAMLIT ---
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 35px; font-weight: bold; color: #FFFFFF; }
    [data-testid="stMetricLabel"] { font-size: 18px; font-weight: bold; color: #FFFFFF; }
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
    usuarios_remover = ['ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197']
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
        encerradas = len(df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO'])
        pendentes = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
        
        c1, c2 = st.columns(2)
        c1.metric("Concluídas (No Período)", encerradas)
        c2.metric("Pendentes (Total Backlog)", pendentes)
        
        df_zc_plot = pd.DataFrame({'Status': ['ENCERRADO', 'ABERTO'], 'Qtd': [encerradas, pendentes]})
        
        fig_zc = px.bar(df_zc_plot, x='Status', y='Qtd', text='Qtd', color='Status',
                        color_discrete_map=CORES_MAP, title="Volume ZC: Entregue vs Pendente")
        
        # --- FORMATAÇÃO DO GRÁFICO ZC ---
        fig_zc.update_traces(
            textposition='outside',
            textfont=dict(size=18, color='white', family='Arial black') # Números em cima das barras
        )
        fig_zc.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            xaxis=dict(tickfont=dict(size=16, color='white', family='Arial black')), # Texto do Eixo X
            font=dict(color='white', weight='bold')
        )
        st.plotly_chart(fig_zc, use_container_width=True)

# ABA 2: MEDIDAS QM
with tab2:
    if not df_qm_f.empty:
        st.subheader("🎯 Visão Geral QM")
        df_geral_qm = df_qm_f['Status_Visual'].value_counts().reset_index()
        df_geral_qm.columns = ['Status', 'Total']
        
        col_m1, col_m2, col_g1 = st.columns([1, 1, 2])
        total_encerradas = df_geral_qm[df_geral_qm['Status'] == 'Medida Encerrada']['Total'].sum()
        total_liberadas = df_geral_qm[df_geral_qm['Status'] == 'Medida Liberada']['Total'].sum()
        
        with col_m1: st.metric("Total Encerradas", int(total_encerradas))
        with col_m2: st.metric("Total Liberadas", int(total_liberadas))
        
        with col_g1:
            fig_donut = px.pie(df_geral_qm, values='Total', names='Status', hole=0.5,
                               color='Status', color_discrete_map=CORES_MAP, height=250)
            
            # --- FORMATAÇÃO DO GRÁFICO DONUT ---
            fig_donut.update_traces(
                textinfo='percent+label',
                textfont=dict(size=16, color='white', family='Arial black')
            )
            fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("---")
        st.subheader("🔧 Produtividade Detalhada por Responsável")
        df_user_qm = df_qm_f.groupby(['Responsável', 'Status_Visual']).size().reset_index(name='Qtd')
        df_user_qm = df_user_qm.sort_values(by='Qtd', ascending=False)

        fig_qm_barra = px.bar(df_user_qm, x='Responsável', y='Qtd', color='Status_Visual', text='Qtd',
                              barmode='group', color_discrete_map=CORES_MAP)
        
        # --- FORMATAÇÃO DO GRÁFICO POR RESPONSÁVEL ---
        fig_qm_barra.update_traces(
            textposition='outside',
            textfont=dict(size=16, color='white', family='Arial black') # Números em negrito
        )
        fig_qm_barra.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(size=14, color='white', family='Arial black')), # Nomes embaixo
            legend=dict(font=dict(size=14, color='white', family='Arial black')), # Legenda lateral
            margin=dict(t=20)
        )
        st.plotly_chart(fig_qm_barra, use_container_width=True)
    else:
        st.warning("Sem dados QM para exibir.")
