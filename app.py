import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard Manutenção Integrado", layout="wide")

st.title("📊 Indicadores Equipe de Estratégia")
st.markdown("---")

# --- FUNÇÕES DE CARREGAMENTO (NOMES DE ARQUIVOS CORRIGIDOS) ---
def load_zc():
    try:
        # Nome exato da sua planilha de manutenção
        df = pd.read_excel("Notas_ZC.xlsx")
        
        # Limpa nomes de colunas
        df.columns = df.columns.str.strip()
        
        col_ref = "Data encermto."
        if col_ref in df.columns:
            df['Data_Ref'] = pd.to_datetime(df[col_ref], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar Notas_ZC.xlsx: {e}")
        return pd.DataFrame()

def load_qm():
    try:
        # Nome exato da sua planilha de qualidade
        # Se o seu arquivo for .xlsx, use read_excel. Se for .csv, use read_csv
        df = pd.read_excel("Notas_QM.xlsx") 
        
        # Limpa espaços invisíveis nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        # CRITÉRIOS ACORDADOS:
        # 1. Data de referência pela coluna "Modificado em"
        df['Data_Ref'] = pd.to_datetime(df['Modificado em'], errors='coerce')
        
        # 2. Mapeamento de Status (Coluna D)
        map_status = {'MEDL': 'Medida Liberada', 'MEDE': 'Medida Encerrada'}
        df['Status_Visual'] = df['Status'].astype(str).str.strip().map(map_status)
        
        # 3. Filtro de Usuários (removendo quem não é da estratégia)
        usuarios_remover = [
            'ABORIN', 'SANT1733', 'WILL8526', 'MORE4174', 'VIEI2975', 
            'HORSIM', 'PINT5850', 'MOLL2381', 'SANC8196', 'RAUL1806', 'FVALERIO', 'GUIM1197'
        ]
        
        # Filtrando pela coluna "Responsável" (Coluna E)
        df = df[~df['Responsável'].astype(str).str.strip().isin(usuarios_remover)]
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar Notas_QM.xlsx: {e}")
        return pd.DataFrame()

# Carregamento dos dados
df_zc = load_zc()
df_qm = load_qm()

# Dicionário de Cores para consistência
CORES_MAP = {
    'ABERTO': '#FF4B4B', 'ENCERRADO': '#00F294',
    'Medida Liberada': '#FF4B4B', 'Medida Encerrada': '#00F294'
}

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("Filtros de Data")

# Filtro QM
if not df_qm.empty:
    df_qm_valid = df_qm.dropna(subset=['Data_Ref'])
    if not df_qm_valid.empty:
        min_q = df_qm_valid['Data_Ref'].min().date()
        max_q = df_qm_valid['Data_Ref'].max().date()
        
        intervalo_qm = st.sidebar.date_input(
            "Período QM (Modificado em):",
            value=[min_q, max_q],
            key="data_qm"
        )
        
        if len(intervalo_qm) == 2:
            i, f = intervalo_qm
            df_qm_f = df_qm[(df_qm['Data_Ref'].dt.date >= i) & (df_qm['Data_Ref'].dt.date <= f)]
        else:
            df_qm_f = df_qm
    else:
        df_qm_f = df_qm
else:
    df_qm_f = pd.DataFrame()

# --- ABAS ---
tab1, tab2 = st.tabs(["📝 NOTAS ZC", "🔧 MEDIDAS QM"])

with tab2:
    if not df_qm_f.empty:
        st.subheader("🔧 Produtividade por Responsável (QM)")
        
        # Agrupamento por Responsável (Coluna E) e Status (Coluna D)
        df_user_qm = df_qm_f.groupby(['Responsável', 'Status_Visual']).size().reset_index(name='Qtd')
        df_user_qm = df_user_qm.sort_values(by='Qtd', ascending=False)

        fig_q1 = px.bar(
            df_user_qm, 
            x='Responsável', 
            y='Qtd', 
            color='Status_Visual', 
            text='Qtd',
            barmode='group',
            color_discrete_map=CORES_MAP
        )
        
        fig_q1.update_traces(textposition='outside')
        fig_q1.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis_tickangle=-45)
        st.plotly_chart(fig_q1, use_container_width=True)
    else:
        st.warning("Aguardando carregamento dos dados ou filtro sem resultados.")
