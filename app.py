import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Manutenção Integrado", layout="wide")

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("---")

# --- FUNÇÕES DE CARREGAMENTO ---
def load_data(file_name):
    try:
        # Tenta ler como Excel, se falhar tenta como CSV
        if file_name.endswith('.xlsx'):
            df = pd.read_excel(file_name)
        else:
            df = pd.read_csv(file_name)
        
        df.columns = df.columns.str.strip() # Remove espaços dos nomes das colunas
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {file_name}: {e}")
        return pd.DataFrame()

# Carregamento dos arquivos (Ajuste os nomes se necessário)
df_zc = load_data("Notas_ZC.xlsx")
df_qm = load_data("Notas_QM.xlsx")

# Cores
CORES_MAP = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'
}

# --- PROCESSAMENTO ZC ---
if not df_zc.empty:
    # Ajuste de data para ZC (Coluna G: Data encermto.)
    col_data_zc = "Data encermto."
    if col_data_zc in df_zc.columns:
        df_zc['Data_Ref'] = pd.to_datetime(df_zc[col_data_zc], errors='coerce')
    else:
        # Caso o nome da coluna seja diferente na sua planilha
        st.warning(f"Coluna '{col_data_zc}' não encontrada em Notas_ZC.xlsx")
        df_zc['Data_Ref'] = pd.to_datetime(df_zc.iloc[:, 6], errors='coerce') # Tenta pela 7ª coluna

# --- PROCESSAMENTO QM ---
if not df_qm.empty:
    # Data de referência pela coluna "Modificado em" (Coluna G)
    df_qm['Data_Ref'] = pd.to_datetime(df_qm['Modificado em'], errors='coerce')
    
    # Mapeamento de Status
    map_status = {'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'}
    df_qm['Status_Visual'] = df_qm['Status'].astype(str).str.strip().map(map_status)
    
    # Filtro de Usuários (Removendo quem não é da estratégia da coluna Responsável)
    usuarios_remover = [
        'ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 
        'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197'
    ]
    df_qm = df_qm[~df_qm['Responsável'].astype(str).str.strip().isin(usuarios_remover)]

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("Filtros de Período")

# Filtro de Data para ZC
df_zc_f = df_zc.copy()
if not df_zc.empty and 'Data_Ref' in df_zc.columns:
    df_zc_valid = df_zc.dropna(subset=['Data_Ref'])
    if not df_zc_valid.empty:
        min_z, max_z = df_zc_valid['Data_Ref'].min().date(), df_zc_valid['Data_Ref'].max().date()
        int_zc = st.sidebar.date_input("Período ZC (Encerramento):", [min_z, max_z], key="zc_date")
        if len(int_zc) == 2:
            df_zc_f = df_zc[(df_zc['Data_Ref'].dt.date >= int_zc[0]) & (df_zc['Data_Ref'].dt.date <= int_zc[1])]

# Filtro de Data para QM
df_qm_f = df_qm.copy()
if not df_qm.empty and 'Data_Ref' in df_qm.columns:
    df_qm_valid = df_qm.dropna(subset=['Data_Ref'])
    if not df_qm_valid.empty:
        min_q, max_q = df_qm_valid['Data_Ref'].min().date(), df_qm_valid['Data_Ref'].max().date()
        int_qm = st.sidebar.date_input("Período QM (Modificação):", [min_q, max_q], key="qm_date")
        if len(int_qm) == 2:
            df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= int_qm[0]) & (df_qm['Data_Ref'].dt.date <= int_qm[1])]

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

# ABA 1: NOTAS ZC
with tab1:
    if not df_zc_f.empty:
        st.subheader("🚀 Performance ZC")
        
        # Lógica de contagem
        encerradas = len(df_zc_f[df_zc_f['Status sistema'] == 'ENCERRADO'])
        pendentes = len(df_zc[df_zc['Status sistema'] == 'ABERTO']) # Backlog total
        
        c1, c2 = st.columns(2)
        c1.metric("Concluídas (No Período)", encerradas)
        c2.metric("Pendentes (Total Backlog)", pendentes)
        
        # Gráfico ZC
        df_zc_plot = pd.DataFrame({
            'Status': ['ENCERRADO', 'ABERTO'],
            'Qtd': [encerradas, pendentes]
        })
        
        fig_zc = px.bar(df_zc_plot, x='Status', y='Qtd', text='Qtd', color='Status',
                        color_discrete_map=CORES_MAP, title="Volume ZC: Entregue vs Pendente")
        fig_zc.update_traces(textposition='outside')
        fig_zc.update_layout(plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_zc, use_container_width=True)
    else:
        st.warning("Dados ZC não encontrados ou filtro sem resultados.")

# --- ABA 2: MEDIDAS QM ---
with tab2:
    if not df_qm_f.empty:
        st.subheader("🎯 Visão Geral QM")
        
        # 1. Preparação dos dados para o gráfico Geral
        df_geral_qm = df_qm_f['Status_Visual'].value_counts().reset_index()
        df_geral_qm.columns = ['Status', 'Total']
        
        # 2. Layout de Topo: Métricas e Gráfico de Rosca
        col_m1, col_m2, col_g1 = st.columns([1, 1, 2])
        
        # Cálculo das métricas para os cards
        total_encerradas = df_geral_qm[df_geral_qm['Status'] == 'Medida Encerrada']['Total'].sum()
        total_liberadas = df_geral_qm[df_geral_qm['Status'] == 'Medida Liberada']['Total'].sum()
        
        with col_m1:
            st.metric("Total Encerradas", int(total_encerradas))
        with col_m2:
            st.metric("Total Liberadas", int(total_liberadas))
            
        with col_g1:
            # Gráfico de Rosca (Donut)
            fig_donut = px.pie(
                df_geral_qm, 
                values='Total', 
                names='Status', 
                hole=0.5,
                color='Status',
                color_discrete_map=CORES_MAP,
                height=250
            )
            fig_donut.update_traces(textinfo='percent+label')
            fig_donut.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_donut, use_container_width=True)

        st.markdown("---")
        
        # 3. Gráfico por Responsável (O detalhamento que já funcionava)
        st.subheader("🔧 Produtividade Detalhada por Responsável")
        
        df_user_qm = df_qm_f.groupby(['Responsável', 'Status_Visual']).size().reset_index(name='Qtd')
        df_user_qm = df_user_qm.sort_values(by='Qtd', ascending=False)

        fig_qm_barra = px.bar(
            df_user_qm, 
            x='Responsável', 
            y='Qtd', 
            color='Status_Visual', 
            text='Qtd',
            barmode='group',
            color_discrete_map=CORES_MAP
        )
        
        fig_qm_barra.update_traces(textposition='outside')
        fig_qm_barra.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', 
            xaxis_tickangle=-45,
            margin=dict(t=20)
        )
        st.plotly_chart(fig_qm_barra, use_container_width=True)
        
    else:
        st.warning("Sem dados QM para exibir (verifique os filtros ou os arquivos).")
