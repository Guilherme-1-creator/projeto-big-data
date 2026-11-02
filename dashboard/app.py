import os
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Representatividade Política - ODS 18 & ODS 5",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CONEXÃO COM A BASE DE DADOS E CARREGAMENTO (CACHE)
# ==============================================================================
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    st.error(
        "A variável DATABASE_URL não foi encontrada no ficheiro .env. Verifique"
        " as suas configurações."
    )
    st.stop()


@st.cache_resource
def get_database_engine():
    return create_engine(DATABASE_URL)


@st.cache_data(ttl=3600)
def carregar_dados():
    engine = get_database_engine()
    query = """
    SELECT 
        ano_eleicao, 
        sg_uf, 
        ds_cargo, 
        ds_cor_raca, 
        ds_genero, 
        sg_partido,
        ds_sit_tot_turno,
        CASE 
            WHEN UPPER(ds_sit_tot_turno) IN ('ELEITO', 'ELEITO POR QP', 'ELEITO POR MÉDIA') THEN 'Eleito'
            ELSE 'Não Eleito'
        END AS status_eleicao
    FROM candidatos_historico;
    """
    df = pd.read_sql(query, engine)

    # Tratamento de valores ausentes
    df["ds_cor_raca"] = df["ds_cor_raca"].fillna("NÃO DECLAROU")
    df["ds_genero"] = df["ds_genero"].fillna("NÃO DECLAROU")

    # Mapeamento de Regiões do Brasil
    regioes = {
        "Norte": ["AC", "AP", "AM", "PA", "RO", "RR", "TO"],
        "Nordeste": [
            "AL",
            "BA",
            "CE",
            "MA",
            "PB",
            "PE",
            "PI",
            "RN",
            "SE",
        ],
        "Centro-Oeste": ["DF", "GO", "MT", "MS"],
        "Sudeste": ["ES", "MG", "RJ", "SP"],
        "Sul": ["PR", "RS", "SC"],
    }

    def obter_regiao(uf):
        for regiao, ufs in regioes.items():
            if uf in ufs:
                return regiao
        return "Nacional/Outros"

    df["regiao"] = df["sg_uf"].apply(obter_regiao)

    return df


with st.spinner("A carregar dados do PostgreSQL na Aiven..."):
    df = carregar_dados()

# ==============================================================================
# 3. CABEÇALHO PRINCIPAL
# ==============================================================================
st.title(
    "Mapeamento da Representatividade Política no Brasil (2014 - 2022)"
)
st.markdown(
    "Análise interseccional sobre a participação étnico-racial e de género na"
    " política brasileira, alinhada às diretrizes da **ODS 18 (Igualdade"
    " Étnico-Racial)** e **ODS 5 (Igualdade de Género)**."
)

# ==============================================================================
# 4. BARRA LATERAL (FILTROS DINÂMICOS CRUZADOS)
# ==============================================================================
st.sidebar.header(" Filtros Globais Cruzados")

anos_disponiveis = sorted(df["ano_eleicao"].unique())
anos_selecionados = st.sidebar.multiselect(
    "1. Ano Eleitoral", options=anos_disponiveis, default=anos_disponiveis
)

regioes_disponiveis = sorted(df["regiao"].unique())
regioes_selecionadas = st.sidebar.multiselect(
    "2. Região", options=regioes_disponiveis, default=regioes_disponiveis
)

ufs_disponiveis = sorted(
    df[df["regiao"].isin(regioes_selecionadas)]["sg_uf"].unique()
)
ufs_selecionadas = st.sidebar.multiselect(
    "3. Estado (UF)", options=ufs_disponiveis, default=ufs_disponiveis
)

generos_disponiveis = sorted(df["ds_genero"].unique())
generos_selecionados = st.sidebar.multiselect(
    "4. Sexo / Gênero",
    options=generos_disponiveis,
    default=generos_disponiveis,
)

racas_disponiveis = sorted(df["ds_cor_raca"].unique())
racas_selecionadas = st.sidebar.multiselect(
    "5. Raça / Cor", options=racas_disponiveis, default=racas_disponiveis
)

cargos_disponiveis = sorted(df["ds_cargo"].unique())
cargos_selecionados = st.sidebar.multiselect(
    "6. Cargo Político", options=cargos_disponiveis, default=cargos_disponiveis
)

# Aplicação de Todos os Filtros Cruzados
df_filtrado = df[
    (df["ano_eleicao"].isin(anos_selecionados))
    & (df["regiao"].isin(regioes_selecionadas))
    & (df["sg_uf"].isin(ufs_selecionadas))
    & (df["ds_genero"].isin(generos_selecionados))
    & (df["ds_cor_raca"].isin(racas_selecionadas))
    & (df["ds_cargo"].isin(cargos_selecionados))
]

if df_filtrado.empty:
    st.warning(
        "Nenhum registo encontrado para a combinação de filtros selecionada."
    )
    st.stop()

# ==============================================================================
# 5. KPIS ANALÍTICOS CHAVE (MÍNIMO 4)
# ==============================================================================
total_candidatos = len(df_filtrado)
total_eleitos = len(df_filtrado[df_filtrado["status_eleicao"] == "Eleito"])
taxa_conversao_geral = (
    (total_eleitos / total_candidatos * 100) if total_candidatos > 0 else 0
)

# Cálculo da Representatividade Negra (Pretos + Pardos)
candidatos_negros = len(
    df_filtrado[df_filtrado["ds_cor_raca"].isin(["PRETA", "PARDA"])]
)
pct_negros_cand = (
    (candidatos_negros / total_candidatos * 100) if total_candidatos > 0 else 0
)

eleitos_negros = len(
    df_filtrado[
        (df_filtrado["ds_cor_raca"].isin(["PRETA", "PARDA"]))
        & (df_filtrado["status_eleicao"] == "Eleito")
    ]
)
pct_negros_eleitos = (
    (eleitos_negros / total_eleitos * 100) if total_eleitos > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("1. Total de Candidaturas", f"{total_candidatos:,}")
col2.metric("2. Total de Eleitos", f"{total_eleitos:,}")
col3.metric("3. Taxa Geral de Eleição", f"{taxa_conversao_geral:.2f}%")
col4.metric(
    "4. % Eleitos Negros (Pretos/Pardos)",
    f"{pct_negros_eleitos:.1f}%",
    delta=f"{pct_negros_eleitos - pct_negros_cand:.1f}% vs Candidaturas",
)

st.divider()

# ==============================================================================
# 6. ESTRUTURA POR ABAS E RECURSOS INTERATIVOS
# ==============================================================================
tab_raca, tab_interseccional, tab_evolucao, tab_drilldown = st.tabs([
    " Étnico-Racial (ODS 18)",
    " Interseccionalidade (ODS 18 + ODS 5)",
    " Evolução Histórica (2014-2022)",
    " Drill-Down & Alternador de Métricas",
])

# ------------------------------------------------------------------------------
# ABA 1: Étnico-Racial (Alternador de Visão Absoluto vs Percentual)
# ------------------------------------------------------------------------------
with tab_raca:
    st.subheader("Análise Étnico-Racial das Candidaturas e Eleições")

    tipo_visao = st.radio(
        "Alternador de Escala Visual:",
        ["Volume Absoluto", "Proporção Percentual (100%)"],
        horizontal=True,
        key="radio_raca",
    )

    norm_config = (
        "percent" if tipo_visao == "Proporção Percentual (100%)" else None
    )
    mode_config = (
        "stack" if tipo_visao == "Proporção Percentual (100%)" else "group"
    )
    label_y = "Percentagem (%)" if norm_config else "Quantidade de Pessoas"

    col_left, col_right = st.columns([1.2, 0.8])

    with col_left:
        df_raca_status = (
            df_filtrado.groupby(["ds_cor_raca", "status_eleicao"])
            .size()
            .reset_index(name="quantidade")
        )

        fig_raca = px.bar(
            df_raca_status,
            x="ds_cor_raca",
            y="quantidade",
            color="status_eleicao",
            barmode=mode_config,
            title=f"Distribuição por Raça/Cor ({tipo_visao})",
            labels={
                "ds_cor_raca": "Raça/Cor",
                "quantidade": label_y,
                "status_eleicao": "Resultado",
            },
            color_discrete_map={"Eleito": "#27ae60", "Não Eleito": "#c0392b"},
        )

        if norm_config:
            fig_raca.update_layout(barnorm=norm_config, yaxis_ticksuffix="%")

        st.plotly_chart(fig_raca, use_container_width=True)

    with col_right:
        df_taxa_raca = (
            df_filtrado.groupby("ds_cor_raca")
            .agg(
                total_cand=("status_eleicao", "count"),
                total_eleito=(
                    "status_eleicao",
                    lambda x: (x == "Eleito").sum(),
                ),
            )
            .reset_index()
        )

        df_taxa_raca["Taxa de Conversão (%)"] = (
            df_taxa_raca["total_eleito"] / df_taxa_raca["total_cand"] * 100
        ).round(2)

        st.markdown("#### Indicadores de Eficiência Eleitoral Racial")
        st.dataframe(
            df_taxa_raca.sort_values(
                by="Taxa de Conversão (%)", ascending=False
            ),
            use_container_width=True,
            hide_index=True,
        )

# ------------------------------------------------------------------------------
# ABA 2: Interseccionalidade (Raça x Gênero)
# ------------------------------------------------------------------------------
with tab_interseccional:
    st.subheader("Análise Interseccional: Raça/Cor vs. Gênero")

    df_matriz = (
        df_filtrado.groupby(["ds_cor_raca", "ds_genero"])
        .agg(
            candidatos=("status_eleicao", "count"),
            eleitos=("status_eleicao", lambda x: (x == "Eleito").sum()),
        )
        .reset_index()
    )
    df_matriz["Taxa de Sucesso (%)"] = (
        df_matriz["eleitos"] / df_matriz["candidatos"] * 100
    ).round(2)

    df_pivot = df_matriz.pivot(
        index="ds_cor_raca", columns="ds_genero", values="Taxa de Sucesso (%)"
    )

    fig_heatmap = px.imshow(
        df_pivot,
        text_auto=True,
        color_continuous_scale="Viridis",
        title="Heatmap: Taxa de Eleição (%) por Cruzamento Interseccional",
        labels=dict(x="Gênero", y="Raça/Cor", color="Taxa (%)"),
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ------------------------------------------------------------------------------
# ABA 3: Evolução Histórica
# ------------------------------------------------------------------------------
with tab_evolucao:
    st.subheader("Evolução Temporal da Representatividade (2014 - 2022)")

    df_evo = (
        df_filtrado[df_filtrado["status_eleicao"] == "Eleito"]
        .groupby(["ano_eleicao", "ds_cor_raca"])
        .size()
        .reset_index(name="eleitos")
    )

    fig_line = px.line(
        df_evo,
        x="ano_eleicao",
        y="eleitos",
        color="ds_cor_raca",
        markers=True,
        title="Evolução do Número de Eleitos por Raça/Cor ao Longo dos Anos",
        labels={
            "ano_eleicao": "Ano Eleitoral",
            "eleitos": "Total de Eleitos",
            "ds_cor_raca": "Raça/Cor",
        },
    )
    fig_line.update_xaxes(type="category")
    st.plotly_chart(fig_line, use_container_width=True)

# ------------------------------------------------------------------------------
# ABA 4: Drill-Down & Alternador Dinâmico de Métricas
# ------------------------------------------------------------------------------
with tab_drilldown:
    st.subheader("Análise Territorial: Drill-Down e Alternador Estatístico")

    col_control1, col_control2 = st.columns(2)

    with col_control1:
        nivel_drill = st.selectbox(
            "Nível de Detalhamento Geográfico (Drill-Down):",
            options=["Por Região", "Por Estado (UF)"],
            index=0,
        )

    with col_control2:
        tipo_metrica = st.radio(
            "Alternador de Métrica Estatística:",
            options=["Total Absoluto de Eleitos", "Média de Eleitos"],
            horizontal=True,
        )

    campo_geo = "regiao" if nivel_drill == "Por Região" else "sg_uf"
    df_base_eleitos = df_filtrado[df_filtrado["status_eleicao"] == "Eleito"]

    if tipo_metrica == "Total Absoluto de Eleitos":
        df_geo = (
            df_base_eleitos.groupby([campo_geo, "ds_cor_raca"])
            .size()
            .reset_index(name="valor_metrica")
        )
        titulo_grafico = (
            f"Total Absoluto de Eleitos por Raça/Cor ({nivel_drill})"
        )
        label_y_geo = "Total de Eleitos"
    else:
        # Lógica corrigida para evitar colisão de colunas no reset_index
        if campo_geo == "regiao":
            # Média de eleitos por Estado (UF) em cada Região
            df_geo_count = (
                df_base_eleitos.groupby(["regiao", "sg_uf", "ds_cor_raca"])
                .size()
                .reset_index(name="qtd")
            )
            df_geo = (
                df_geo_count.groupby(["regiao", "ds_cor_raca"])["qtd"]
                .mean()
                .reset_index(name="valor_metrica")
            )
            titulo_grafico = (
                "Média de Eleitos por Estado/UF dentro de cada Região"
            )
        else:
            # Média de eleitos por Ano Eleitoral em cada Estado (UF)
            df_geo_count = (
                df_base_eleitos.groupby(["sg_uf", "ano_eleicao", "ds_cor_raca"])
                .size()
                .reset_index(name="qtd")
            )
            df_geo = (
                df_geo_count.groupby(["sg_uf", "ds_cor_raca"])["qtd"]
                .mean()
                .reset_index(name="valor_metrica")
            )
            titulo_grafico = (
                "Média de Eleitos por Ano Eleitoral em cada Estado (UF)"
            )

        df_geo["valor_metrica"] = df_geo["valor_metrica"].round(2)
        label_y_geo = "Média de Eleitos"

    fig_drill = px.bar(
        df_geo,
        x=campo_geo,
        y="valor_metrica",
        color="ds_cor_raca",
        barmode="group",
        title=titulo_grafico,
        labels={
            campo_geo: (
                "Região" if nivel_drill == "Por Região" else "Estado (UF)"
            ),
            "valor_metrica": label_y_geo,
            "ds_cor_raca": "Raça/Cor",
        },
    )
    st.plotly_chart(fig_drill, use_container_width=True)