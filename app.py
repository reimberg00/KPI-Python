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

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("---")

# --- FUNÇÕES DE CARREGAMENTO ---
def load_zc():
    try:
        # Ajuste para ler o arquivo correto (Excel ou CSV conforme seu ambiente)
        df = pd.read_excel("Notas_ZC.xlsx")
        col_ref = "Data encermto."
        if col_ref in df.columns:
            df['Data_Ref'] = pd.to_datetime(df[col_ref], errors='coerce')
        return df
    except:
        return pd.DataFrame()

def load_qm():
    try:
        # Carregando o arquivo (ajustado para o nome do seu CSV/Excel)
        df = pd.read_csv("Notas_QM.xlsx - Planilha1.csv") 
        
        # CRITÉRIO NOVO: Usar "Modificado em" como referência de data
        df['Data_Ref'] = pd.to_datetime(df['Modificado em'], errors='coerce')
        
        # Mapeamento de Status
        map_status = {'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'}
        df['Status_Visual'] = df['Status'].map(map_status)
        
        # Lista de usuários que não pertencem à equipe de estratégia
        usuarios_remover = [
            'ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 
            'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197'
        ]
        
        # Filtramos os usuários na coluna 'Responsável' conforme sua sugestão
        df = df[~df['Responsável'].isin(usuarios_remover)]
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar QM: {e}")
        return pd.DataFrame()

# Carregamento
df_zc = load_zc()
df_qm = load_qm()

# Cores
CORES_MAP = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'
}

# --- BARRA LATERAL ---
st.sidebar.title("Filtros")

# 1. Filtro ZC
st.sidebar.header("📅 Notas ZC (Manutenção)")
if not df_zc.empty:
    min_z = df_zc['Data_Ref'].min().date()
    max_z = df_zc['Data_Ref'].max().date()
    intervalo_zc = st.sidebar.date_input("Período de Encerramento:", value=[min_z, max_z], key="data_zc")
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
    # Remove datas nulas para não dar erro no seletor
    df_qm_valid = df_qm.dropna(subset=['Data_Ref'])
    min_q = df_qm_valid['Data_Ref'].min().date()
    max_q = df_qm_valid['Data_Ref'].max().date()
    
    intervalo_qm = st.sidebar.date_input(
        "Período de Modificação:", # Nome atualizado
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

# --- ABA 1: NOTAS ZC (Mantida) ---
with tab1:
    if not df_zc.empty:
        st.subheader("🚀 Performance ZC")
        abertas_zc = len(df_zc[df_zc['Status sistema'] == 'ABERTO'])
        encerradas_zc = len(df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO'])
        
        c1, c2 = st.columns(2)
        c1.metric("Concluídas (No Período)", encerradas_zc)
        c2.metric("Pendentes (Total Backlog)", abertas_zc)

        df_fechadas_periodo = df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO']
        df_abertas_total = df_zc[df_zc['Status sistema'] == 'ABERTO']
        df_grafico = pd.concat([df_fechadas_periodo, df_abertas_total])
        df_zc_bar = df_grafico['Status sistema'].value_counts().reset_index()
        df_zc_bar.columns = ['Status', 'Qtd']

        fig_z1 = px.bar(df_zc_bar, x='Status', y='Qtd', text='Qtd', color='Status',
                        color_discrete_map=CORES_MAP, title="Volume: Entregue vs Pendente", height=350)
        fig_z1.update_traces(width=0.2, textposition='outside')
        fig_z1.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_z1, use_container_width=True)

# --- ABA 2: MEDIDAS QM (ATUALIZADA) ---
with tab2:
    if not df_qm_f.empty:
        st.subheader("🔧 Indicadores QM (Por Responsável)")

        # CRITÉRIO NOVO: Agrupar por 'Responsável' em vez de 'Modificado por'
        df_user_qm = df_qm_f.groupby(['Responsável', 'Status_Visual']).size().reset_index(name='Qtd')
        
        # Ordenação para melhor visualização
        df_user_qm = df_user_qm.sort_values(by='Qtd', ascending=False)

        fig_q1 = px.bar(df_user_qm, 
                        x='Responsável', 
                        y='Qtd', 
                        color='Status_Visual', 
                        text='Qtd',
                        barmode='group', 
                        color_discrete_map=CORES_MAP, 
                        title="Produtividade por Responsável (Filtro: Data de Modificação)")
        
        fig_q1.update_traces(textposition='outside')
        fig_q1.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            bargap=0.3, 
            xaxis_tickangle=-45,
            yaxis_title="Quantidade de Medidas"
        )
        st.plotly_chart(fig_q1, use_container_width=True)
        
        st.markdown("---")

        # Gráfico Evolução Fechadas
        st.subheader("📈 Evolução de Medidas Fechadas")
        df_fechadas = df_qm_f[df_qm_f['Status'] == 'MEDE'].copy()
        
        if not df_fechadas.empty:
            # Agrupamento temporal baseado na data de modificação
            df_fechadas['Periodo'] = df_fechadas['Data_Ref'].dt.to_period('W').dt.to_timestamp()
            df_evolucao = df_fechadas.groupby('Periodo').size().reset_index(name='Qtd')
            
            fig_q2 = px.line(df_evolucao, x='Periodo', y='Qtd', text='Qtd', markers=True, 
                             color_discrete_sequence=['#00F294'])
            
            fig_q2.update_traces(textposition="top center", line_shape='spline', line_width=3)
            fig_q2.update_layout(plot_bgcolor='rgba(0,0,0,0)', yaxis_visible=False)
            st.plotly_chart(fig_q2, use_container_width=True)
        else:
            st.info("Nenhuma medida encerrada (MEDE) encontrada no período selecionado.")
    else:
        st.warning("Sem dados QM para o período selecionado.")
