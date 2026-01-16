import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Manutenção Integrado", layout="wide")

# Estilos CSS para Metricas
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
        col_ref = "Data encermto."
        if col_ref in df.columns:
            df['Data_Ref'] = pd.to_datetime(df[col_ref], errors='coerce')
        return df
    except:
        return pd.DataFrame()

def load_qm():
    try:
        df = pd.read_excel("Notas_QM.xlsx")
        # Referência: Dta.criação
        df['Data_Ref'] = pd.to_datetime(df['Dta.criação'], errors='coerce')
        
        # Tradução dos Status
        map_status = {'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'}
        df['Status_Visual'] = df['Status'].map(map_status)
        
        # Filtro de Exclusão de Usuários
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

# Cores Neon
CORES_MAP = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'
}

# --- FILTRO LATERAL (APENAS PARA QM) ---
st.sidebar.header("📅 Filtros QM")
if not df_qm.empty:
    min_d = df_qm['Data_Ref'].min().date()
    max_d = df_qm['Data_Ref'].max().date()
    
    intervalo_qm = st.sidebar.date_input(
        "Período (QM):",
        value=[min_d, max_d],
        min_value=min_d,
        max_value=max_d
    )

    if len(intervalo_qm) == 2:
        d_inicio, d_fim = intervalo_qm
        df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= d_inicio) & (df_qm['Data_Ref'].dt.date <= d_fim)]
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
        
        # Cálculo das métricas
        abertas_zc = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
        encerradas_zc = len(df_zc[df_zc['Status sistema'] == 'ENCERRADO'])
        
        # --- AJUSTE 1: Inversão de Posição ---
        # Coluna 1 agora mostra Concluídas, Coluna 2 mostra Pendentes
        c1, c2 = st.columns(2)
        c1.metric("Concluídas", encerradas_zc)
        c2.metric("Pendentes", abertas_zc)
        # ------------------------------------

        # Gráfico de Barras
        df_zc_bar = df_zc['Status sistema'].value_counts().reset_index()
        df_zc_bar.columns = ['Status', 'Qtd']
        fig_z1 = px.bar(df_zc_bar, x='Status', y='Qtd', text='Qtd', color='Status',
                        color_discrete_map=CORES_MAP, title="Volume Total ZC")
        
        # --- AJUSTE 2: Barras menores (width=0.2) ---
        fig_z1.update_traces(width=0.2, textposition='outside')
        # -------------------------------------------
        
        fig_z1.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False, yaxis_visible=False)
        st.plotly_chart(fig_z1, use_container_width=True)
    else:
        st.error("Sem dados ZC.")

# --- ABA 2: MEDIDAS QM ---
with tab2:
    if not df_qm_f.empty:
        st.subheader("🔧 Indicadores QM")

        # 1. Gráfico de Produtividade por Usuário
        df_user_qm = df_qm_f.groupby(['Modificado por', 'Status_Visual']).size().reset_index(name='Qtd')
        fig_q1 = px.bar(df_user_qm, x='Modificado por', y='Qtd', color='Status_Visual', text='Qtd',
                        barmode='group', color_discrete_map=CORES_MAP, title="Produtividade por Usuário")
        
        # Ajustei aqui também para 0.2 para manter o padrão
        fig_q1.update_traces(width=0.2, textposition='outside')
        
        fig_q1.update_layout(plot_bgcolor='rgba(0,0,0,0)', bargap=0.5, xaxis_tickangle=-45)
        st.plotly_chart(fig_q1, use_container_width=True)
        
        st.markdown("---")

        # 2. GRÁFICO DE EVOLUÇÃO DE MEDIDAS FECHADAS
        st.subheader("📈 Evolução de Medidas Fechadas")
        
        col_freq, col_vazio = st.columns([1, 3])
        with col_freq:
            freq_q = st.radio("Visualizar evolução por:", ["Semana", "Mês"], horizontal=True)
        
        df_fechadas = df_qm_f[df_qm_f['Status'] == 'MEDE'].copy()
        
        if not df_fechadas.empty:
            periodo_char = "W" if "Semana" in freq_q else "M"
            df_fechadas['Periodo'] = df_fechadas['Data_Ref'].dt.to_period(periodo_char).dt.to_timestamp()
            
            df_evolucao = df_fechadas.groupby('Periodo').size().reset_index(name='Qtd')
            
            fig_q2 = px.line(
                df_evolucao, x='Periodo', y='Qtd', text='Qtd', markers=True, 
                title=f"Quantidade de Medidas Fechadas ({freq_q})",
                color_discrete_sequence=['#00F294']
            )
            
            formato_data = "%d/%m" if "Semana" in freq_q else "%b/%Y"
            passo_tick = 604800000 if "Semana" in freq_q else "M1"
            
            fig_q2.update_xaxes(
                tickformat=formato_data, dtick=passo_tick, showgrid=True, 
                gridcolor='rgba(255,255,255,0.1)', tickangle=-45
            )
            
            fig_q2.update_traces(textposition="top center", line_shape='spline', line_width=3, marker_size=8)
            fig_q2.update_layout(
                plot_bgcolor='rgba(0,0,0,0)', yaxis_visible=False, 
                xaxis_title="", margin=dict(t=50, l=10, r=10, b=10)
            )
            
            st.plotly_chart(fig_q2, use_container_width=True)
        else:
            st.info("Nenhuma medida encerrada encontrada neste período.")
    else:
        st.warning("Sem dados QM para o filtro selecionado.")
