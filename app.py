import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Manutenção Integrado", layout="wide")

# Estilos CSS
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #00F294; }
    [data-testid="stMetricDelta"] { font-size: 16px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Gestão de Notas e Medidas SAP")
st.markdown("---")

# --- FUNÇÕES DE CARREGAMENTO ---
def load_zc():
    try:
        df = pd.read_excel("Notas_ZC.xlsx")
        # Referência: Coluna G "Data encermto."
        col_ref = "Data encermto."
        if col_ref in df.columns:
            df['Data_Ref'] = pd.to_datetime(df[col_ref], errors='coerce')
        return df
    except:
        return pd.DataFrame()

def load_qm():
    try:
        df = pd.read_excel("Notas_QM.xlsx")
        df['Data_Ref'] = pd.to_datetime(df['Dta.criação'], errors='coerce')
        
        map_status = {'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'}
        df['Status_Visual'] = df['Status'].map(map_status)
        
        usuarios_remover = [
            'ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 
            'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO'
        ]
        df = df[~df['Modificado por'].isin(usuarios_remover)]
        return df
    except:
        return pd.DataFrame()

# Carregamento
df_zc = load_zc()
df_qm = load_qm()

# Cores
CORES_MAP = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'
}

# --- BARRA LATERAL (AGORA COM DOIS FILTROS DE DATA) ---
st.sidebar.title("Filtros")

# 1. Filtro ZC
st.sidebar.header("📅 Notas ZC (Manutenção)")
if not df_zc.empty:
    # Pega data min/max para o padrão
    min_z = df_zc['Data_Ref'].min().date()
    max_z = df_zc['Data_Ref'].max().date()
    
    # Seletor de Data ZC
    intervalo_zc = st.sidebar.date_input(
        "Período de Encerramento:",
        value=[min_z, max_z],
        min_value=min_z,
        max_value=max_z,
        key="data_zc" # Chave única para não confundir com o outro
    )

    # Aplica o filtro ZC
    if len(intervalo_zc) == 2:
        inicio_z, fim_z = intervalo_zc
        df_zc_f = df_zc[(df_zc['Data_Ref'].dt.date >= inicio_z) & (df_zc['Data_Ref'].dt.date <= fim_z)]
    else:
        df_zc_f = df_zc
else:
    df_zc_f = pd.DataFrame()

st.sidebar.markdown("---")

# 2. Filtro QM
st.sidebar.header("📅 Medidas QM (Qualidade)")
if not df_qm.empty:
    min_q = df_qm['Data_Ref'].min().date()
    max_q = df_qm['Data_Ref'].max().date()
    
    intervalo_qm = st.sidebar.date_input(
        "Período de Criação:",
        value=[min_q, max_q],
        min_value=min_q,
        max_value=max_q,
        key="data_qm"
    )

    if len(intervalo_qm) == 2:
        inicio_q, fim_q = intervalo_qm
        df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= inicio_q) & (df_qm['Data_Ref'].dt.date <= fim_q)]
    else:
        df_qm_f = df_qm
else:
    df_qm_f = pd.DataFrame()

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

# --- ABA 1: NOTAS ZC ---
with tab1:
    if not df_zc.empty:
        st.subheader("🚀 Performance ZC")
        
        # --- CORREÇÃO DA LÓGICA DE FILTRO ---
        # 1. Pendentes: Usamos o df_zc ORIGINAL (sem filtro de data) para ver todo o backlog
        abertas_zc = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
        
        # 2. Encerradas: Usamos o df_zc_f (COM filtro) para ver a produção do período
        encerradas_zc = len(df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO'])
        
        # Métricas
        c1, c2 = st.columns(2)
        c1.metric("Concluídas (No Período)", encerradas_zc)
        c2.metric("Pendentes (Total Backlog)", abertas_zc)

        # --- PREPARAÇÃO DO GRÁFICO MISTO ---
        # Queremos mostrar no gráfico: As fechadas do mês VS O total de abertas
        df_fechadas_periodo = df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO']
        df_abertas_total = df_zc[df_zc['Status sistema'] == 'ABERTO']
        
        # Juntamos os dois grupos para o gráfico
        df_grafico = pd.concat([df_fechadas_periodo, df_abertas_total])
        
        # Montagem dos dados para o Plotly
        df_zc_bar = df_grafico['Status sistema'].value_counts().reset_index()
        df_zc_bar.columns = ['Status', 'Qtd']

        # Margem para o número não cortar
        max_val = df_zc_bar['Qtd'].max()
        margem = max_val * 1.2 if max_val > 0 else 10

        fig_z1 = px.bar(df_zc_bar, x='Status', y='Qtd', text='Qtd', color='Status',
                        color_discrete_map=CORES_MAP, title="Volume: Entregue vs Pendente", height=350)
        
        fig_z1.update_yaxes(range=[0, margem], visible=False)
        fig_z1.update_traces(width=0.2, textposition='outside')
        fig_z1.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=40, b=0))
        
        st.plotly_chart(fig_z1, use_container_width=True)
    else:
        st.warning(f"Sem dados ZC carregados.")

# --- ABA 2: MEDIDAS QM ---
with tab2:
    if not df_qm_f.empty:
        st.subheader("🔧 Indicadores QM")

        # Gráfico Produtividade
        df_user_qm = df_qm_f.groupby(['Modificado por', 'Status_Visual']).size().reset_index(name='Qtd')
        fig_q1 = px.bar(df_user_qm, x='Modificado por', y='Qtd', color='Status_Visual', text='Qtd',
                        barmode='group', color_discrete_map=CORES_MAP, title="Produtividade por Usuário")
        
        fig_q1.update_traces(width=0.2, textposition='outside')
        fig_q1.update_layout(plot_bgcolor='rgba(0,0,0,0)', bargap=0.5, xaxis_tickangle=-45)
        st.plotly_chart(fig_q1, use_container_width=True)
        
        st.markdown("---")

        # Gráfico Evolução Fechadas
        st.subheader("📈 Evolução de Medidas Fechadas")
        col_freq, _ = st.columns([1, 3])
        with col_freq:
            freq_q = st.radio("Agrupar por:", ["Semana", "Mês"], horizontal=True)
        
        df_fechadas = df_qm_f[df_qm_f['Status'] == 'MEDE'].copy()
        
        if not df_fechadas.empty:
            periodo_char = "W" if "Semana" in freq_q else "M"
            df_fechadas['Periodo'] = df_fechadas['Data_Ref'].dt.to_period(periodo_char).dt.to_timestamp()
            df_evolucao = df_fechadas.groupby('Periodo').size().reset_index(name='Qtd')
            
            fig_q2 = px.line(df_evolucao, x='Periodo', y='Qtd', text='Qtd', markers=True, 
                             color_discrete_sequence=['#00F294'])
            
            fmt_data = "%d/%m" if "Semana" in freq_q else "%b/%Y"
            dtick_val = 604800000 if "Semana" in freq_q else "M1"
            
            fig_q2.update_xaxes(tickformat=fmt_data, dtick=dtick_val, showgrid=True, 
                                gridcolor='rgba(255,255,255,0.1)', tickangle=-45)
            fig_q2.update_traces(textposition="top center", line_shape='spline', line_width=3)
            fig_q2.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis_visible=False, xaxis_title="", margin=dict(t=30))
            
            st.plotly_chart(fig_q2, use_container_width=True)
        else:
            st.info("Nenhuma medida fechada neste período.")
    else:
        st.warning("Sem dados QM.")
