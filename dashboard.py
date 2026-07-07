# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "streamlit>=1.49",
#     "pandas>=2.0",
#     "plotly>=5.20",
# ]
# ///
"""
Dashboard — Comitê de Inovação e Inteligência Artificial do MPPA
Estatística de uso do Microsoft Copilot

Execução (com uv):  uv run dashboard.py
Os 5 arquivos CSV devem estar na mesma pasta deste script.
"""

import re
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.runtime

# Permite executar diretamente com "uv run dashboard.py":
# se não estiver dentro do runtime do Streamlit, relança via CLI.
if __name__ == "__main__" and not streamlit.runtime.exists():
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", __file__] + sys.argv[1:]
    sys.exit(stcli.main())

# ----------------------------------------------------------------------------
# Configuração geral
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Uso do Copilot — MPPA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PASTA = Path(__file__).parent
CORES = px.colors.qualitative.Set2
COR_PRINCIPAL = "#7A0C1B"  # vermelho escuro institucional
COR_SECUNDARIA = "#1f6f8b"

st.markdown(
    """
    <style>
    .cabecalho-mppa {
        background: linear-gradient(135deg, #7A0C1B 0%, #4A0710 100%);
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;       /* alinhamento vertical */
        gap: 1rem;
        min-height: 84px;
    }
    .logo-mppa {
        width: clamp(52px, 8vw, 72px);
        height: auto;
        flex-shrink: 0;
    }
    .textos-mppa {
        display: flex;
        flex-direction: column;
        justify-content: center;   /* centraliza verticalmente */
        flex: 1;
        text-align: center;
    }
    .titulo-mppa {
        font-size: clamp(1.05rem, 3.2vw, 1.7rem);
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        line-height: 1.3;
    }
    .subtitulo-mppa {
        font-size: clamp(0.78rem, 2vw, 1rem);
        font-weight: 400;
        color: #F2D9DD;
        margin: 0.25rem 0 0 0;
        line-height: 1.2;
    }
    .stTabs [data-baseweb="tab-list"] {
        overflow-x: auto;
        flex-wrap: nowrap;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        white-space: nowrap;
        font-size: 0.9rem;
    }
    [data-testid="stMetricValue"] { font-size: clamp(1.1rem, 3vw, 1.6rem); }
    [data-testid="stMetricLabel"] { font-size: clamp(0.7rem, 2vw, 0.85rem); }
    div.block-container { padding-top: 1.5rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

def _logo_base64():
    """Procura logo.png (ou .jpg/.jpeg) na pasta e devolve tag <img> em base64."""
    import base64
    for nome in ("logo.png", "logo.jpg", "logo.jpeg"):
        arq = PASTA / nome
        if arq.exists():
            mime = "png" if nome.endswith("png") else "jpeg"
            b64 = base64.b64encode(arq.read_bytes()).decode()
            return f'<img class="logo-mppa" src="data:image/{mime};base64,{b64}" alt="Logo CiiA/MPPA">'
    return ""


st.markdown(
    '<div class="cabecalho-mppa">'
    + _logo_base64() +
    '<div class="textos-mppa">'
    '<p class="titulo-mppa">Comitê de Inovação e Inteligência Artificial do MPPA</p>'
    '<p class="subtitulo-mppa">Estatística de uso do Microsoft Copilot</p>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# Utilitários (formatos pt-BR)
# ----------------------------------------------------------------------------
MESES = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}


def data_ptbr(valor):
    """Converte '7 de jul. de 2026' em Timestamp."""
    if pd.isna(valor):
        return pd.NaT
    m = re.match(r"(\d{1,2}) de (\w{3})\.? de (\d{4})", str(valor).strip())
    if not m:
        return pd.to_datetime(valor, errors="coerce")
    dia, mes, ano = int(m.group(1)), MESES.get(m.group(2).lower()), int(m.group(3))
    if mes is None:
        return pd.NaT
    return pd.Timestamp(ano, mes, dia)


def numero_ptbr(valor):
    """Converte '1.320' (milhar pt-BR) em inteiro."""
    if pd.isna(valor):
        return 0
    s = str(valor).strip().replace(".", "").replace(",", ".")
    try:
        return int(float(s))
    except ValueError:
        return 0


def fmt(n):
    """1320 -> '1.320' (padrão brasileiro)."""
    return f"{int(n):,}".replace(",", ".")


@st.cache_data(show_spinner="Carregando dados...")
def carregar():
    dados = {}

    df = pd.read_csv(PASTA / "agentes.csv", dtype=str)
    for c in ["Usuários ativos (licenciados)", "Usuários ativos (não licenciados)",
              "Respostas enviadas aos usuários"]:
        df[c] = df[c].map(numero_ptbr)
    df["Data da última atividade (UTC)"] = df["Data da última atividade (UTC)"].map(data_ptbr)
    dados["agentes"] = df

    df = pd.read_csv(PASTA / "usuarios-e-agentes.csv", dtype=str)
    df["Respostas enviadas aos usuários"] = df["Respostas enviadas aos usuários"].map(numero_ptbr)
    df["Data da última atividade (UTC)"] = df["Data da última atividade (UTC)"].map(data_ptbr)
    dados["usuarios_agentes"] = df

    df = pd.read_csv(PASTA / "usuarios-uso-agentes.csv", dtype=str)
    for c in ["Número de agentes usados", "Respostas de agente recebidas"]:
        df[c] = df[c].map(numero_ptbr)
    df["Data da última atividade (UTC)"] = df["Data da última atividade (UTC)"].map(data_ptbr)
    dados["uso_por_usuario"] = df

    df = pd.read_csv(PASTA / "uso-copilot-chat.csv")
    for c in df.columns:
        if "date" in c.lower() or "Last activity" in c:
            df[c] = pd.to_datetime(df[c], errors="coerce")
    dados["chat"] = df

    df = pd.read_csv(PASTA / "uso-copilot.csv")
    for c in df.columns:
        if "Date" in c or "date" in c.lower():
            df[c] = pd.to_datetime(df[c], errors="coerce")
    dados["copilot"] = df

    return dados


# ----------------------------------------------------------------------------
# Componentes reutilizáveis
# ----------------------------------------------------------------------------
def filtro_periodo(df, coluna, key, rotulo="Período da última atividade"):
    """Slider de intervalo de datas. Retorna df filtrado (mantém NaT fora do filtro apenas se intervalo completo)."""
    serie = df[coluna].dropna()
    if serie.empty:
        return df
    dmin, dmax = serie.min().date(), serie.max().date()
    if dmin == dmax:
        return df
    ini, fim = st.slider(rotulo, min_value=dmin, max_value=dmax,
                         value=(dmin, dmax), format="DD/MM/YYYY", key=key)
    completo = (ini == dmin and fim == dmax)
    if completo:
        return df
    mask = df[coluna].dt.date.between(ini, fim)
    return df[mask.fillna(False)]


def grafico_barras(df, x, y, titulo, cor=COR_PRINCIPAL):
    fig = px.bar(df, x=x, y=y, orientation="h", title=titulo, text_auto=True)
    fig.update_traces(marker_color=cor)
    fig.update_layout(
        margin=dict(l=10, r=10, t=45, b=10),
        height=max(340, 30 * max(len(df), 1) + 90),
        yaxis_title=None, xaxis_title=None,
        yaxis=dict(autorange="reversed"),
        title_font_size=15,
    )
    return fig


def tabela(df, key):
    busca = st.text_input("🔍 Busca livre na tabela", key=f"busca_{key}",
                          placeholder="Digite para filtrar linhas...")
    v = df
    if busca:
        mask = df.astype(str).apply(
            lambda col: col.str.contains(busca, case=False, na=False)).any(axis=1)
        v = df[mask]
    st.dataframe(v, width="stretch", hide_index=True, height=420)
    st.caption(f"{fmt(len(v))} de {fmt(len(df))} registros")
    st.download_button("⬇️ Baixar dados filtrados (CSV)",
                       v.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"{key}_filtrado.csv", mime="text/csv",
                       key=f"dl_{key}")


def sem_dados(df):
    if df.empty:
        st.warning("Nenhum registro corresponde aos filtros selecionados.")
        return True
    return False


try:
    d = carregar()
except FileNotFoundError as e:
    st.error(f"Arquivo não encontrado: {e}. Coloque os 5 CSVs na mesma pasta do dashboard.py.")
    st.stop()

# ----------------------------------------------------------------------------
# Abas — uma por arquivo
# ----------------------------------------------------------------------------
abas = st.tabs([
    "🤖 Agentes",
    "👥 Usuários e Agentes",
    "📈 Uso de Agentes por Usuário",
    "💬 Copilot Chat",
    "🧩 Copilot M365",
])

# ============================== ABA 1: agentes.csv ==========================
with abas[0]:
    df0 = d["agentes"]
    st.subheader("Agentes disponíveis")
    st.caption("Fonte: agentes.csv")

    with st.expander("🔎 Filtros", expanded=False):
        f1, f2 = st.columns(2)
        with f1:
            tipos = sorted(df0["Tipo de criador"].dropna().unique())
            sel_tipo = st.multiselect("Tipo de criador", tipos, default=[], key="ag_tipo",
                                      placeholder="Todos")
            nome = st.text_input("Nome do agente contém", key="ag_nome")
        with f2:
            max_resp = int(df0["Respostas enviadas aos usuários"].max())
            min_resp = st.number_input("Mínimo de respostas enviadas", 0, max_resp, 0,
                                       key="ag_minresp")
            so_ativos = st.checkbox("Somente agentes com usuários ativos", key="ag_ativos")
        df0f = df0.copy()
        if sel_tipo:
            df0f = df0f[df0f["Tipo de criador"].isin(sel_tipo)]
        if nome:
            df0f = df0f[df0f["Nome do agente"].str.contains(nome, case=False, na=False)]
        if min_resp > 0:
            df0f = df0f[df0f["Respostas enviadas aos usuários"] >= min_resp]
        if so_ativos:
            df0f = df0f[(df0f["Usuários ativos (licenciados)"]
                         + df0f["Usuários ativos (não licenciados)"]) > 0]
        df0f = filtro_periodo(df0f, "Data da última atividade (UTC)", "ag_periodo")

    df = df0f
    if not sem_dados(df):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Agentes", fmt(len(df)))
        c2.metric("Respostas enviadas", fmt(df["Respostas enviadas aos usuários"].sum()))
        c3.metric("Usuários ativos (licenciados)", fmt(df["Usuários ativos (licenciados)"].sum()))
        c4.metric("Usuários ativos (não licenc.)", fmt(df["Usuários ativos (não licenciados)"].sum()))

        top = (df.nlargest(15, "Respostas enviadas aos usuários")
                 [["Nome do agente", "Respostas enviadas aos usuários"]])
        st.plotly_chart(
            grafico_barras(top, "Respostas enviadas aos usuários", "Nome do agente",
                           "Top 15 agentes por respostas enviadas"),
            width="stretch")

        tipo = df["Tipo de criador"].value_counts().reset_index()
        tipo.columns = ["Tipo de criador", "Quantidade"]
        fig = px.pie(tipo, values="Quantidade", names="Tipo de criador",
                     title="Agentes por tipo de criador", hole=0.45,
                     color_discrete_sequence=CORES)
        fig.update_layout(margin=dict(l=10, r=10, t=45, b=10), height=340, title_font_size=15)
        st.plotly_chart(fig, width="stretch")

        tabela(df, "agentes")

# ======================= ABA 2: usuarios-e-agentes.csv ======================
with abas[1]:
    df0 = d["usuarios_agentes"]
    st.subheader("Relação usuários × agentes")
    st.caption("Fonte: usuarios-e-agentes.csv")

    with st.expander("🔎 Filtros", expanded=False):
        f1, f2 = st.columns(2)
        with f1:
            agentes_lista = sorted(df0["Nome do agente"].dropna().unique())
            sel_ag = st.multiselect("Agente", agentes_lista, default=[], key="ua_agente",
                                    placeholder="Todos")
            usuario = st.text_input("Usuário (e-mail) contém", key="ua_usuario")
        with f2:
            max_r = int(df0["Respostas enviadas aos usuários"].max())
            min_r = st.number_input("Mínimo de respostas", 0, max_r, 0, key="ua_minresp")
        df0f = df0.copy()
        if sel_ag:
            df0f = df0f[df0f["Nome do agente"].isin(sel_ag)]
        if usuario:
            df0f = df0f[df0f["Nome de usuário"].str.contains(usuario, case=False, na=False)]
        if min_r > 0:
            df0f = df0f[df0f["Respostas enviadas aos usuários"] >= min_r]
        df0f = filtro_periodo(df0f, "Data da última atividade (UTC)", "ua_periodo")

    df = df0f
    if not sem_dados(df):
        c1, c2, c3 = st.columns(3)
        c1.metric("Pares usuário-agente", fmt(len(df)))
        c2.metric("Usuários distintos", fmt(df["Nome de usuário"].nunique()))
        c3.metric("Agentes distintos", fmt(df["Nome do agente"].nunique()))

        top_ag = (df.groupby("Nome do agente")["Respostas enviadas aos usuários"]
                    .sum().nlargest(15).reset_index())
        st.plotly_chart(
            grafico_barras(top_ag, "Respostas enviadas aos usuários", "Nome do agente",
                           "Top 15 agentes por respostas"),
            width="stretch")

        top_us = (df.groupby("Nome de usuário")["Respostas enviadas aos usuários"]
                    .sum().nlargest(15).reset_index())
        st.plotly_chart(
            grafico_barras(top_us, "Respostas enviadas aos usuários", "Nome de usuário",
                           "Top 15 usuários por respostas recebidas", cor=COR_SECUNDARIA),
            width="stretch")

        tabela(df, "usuarios_agentes")

# ===================== ABA 3: usuarios-uso-agentes.csv ======================
with abas[2]:
    df0 = d["uso_por_usuario"]
    st.subheader("Uso de agentes por usuário")
    st.caption("Fonte: usuarios-uso-agentes.csv")

    with st.expander("🔎 Filtros", expanded=False):
        f1, f2 = st.columns(2)
        with f1:
            usuario = st.text_input("Usuário (nome ou e-mail) contém", key="uu_usuario")
            max_n = int(df0["Número de agentes usados"].max())
            faixa_ag = st.slider("Número de agentes usados", 1, max_n, (1, max_n),
                                 key="uu_nagentes")
        with f2:
            max_r = int(df0["Respostas de agente recebidas"].max())
            min_r = st.number_input("Mínimo de respostas recebidas", 0, max_r, 0,
                                    key="uu_minresp")
        df0f = df0.copy()
        if usuario:
            m = (df0f["Nome de usuário"].str.contains(usuario, case=False, na=False)
                 | df0f["Nome de exibição"].str.contains(usuario, case=False, na=False))
            df0f = df0f[m]
        df0f = df0f[df0f["Número de agentes usados"].between(*faixa_ag)]
        if min_r > 0:
            df0f = df0f[df0f["Respostas de agente recebidas"] >= min_r]
        df0f = filtro_periodo(df0f, "Data da última atividade (UTC)", "uu_periodo")

    df = df0f
    if not sem_dados(df):
        c1, c2, c3 = st.columns(3)
        c1.metric("Usuários", fmt(len(df)))
        c2.metric("Respostas recebidas (total)", fmt(df["Respostas de agente recebidas"].sum()))
        c3.metric("Média de agentes por usuário", f'{df["Número de agentes usados"].mean():.1f}')

        top = (df.nlargest(15, "Respostas de agente recebidas")
                 [["Nome de exibição", "Respostas de agente recebidas"]])
        st.plotly_chart(
            grafico_barras(top, "Respostas de agente recebidas", "Nome de exibição",
                           "Top 15 usuários por respostas de agente recebidas"),
            width="stretch")

        dist = df["Número de agentes usados"].value_counts().sort_index().reset_index()
        dist.columns = ["Número de agentes usados", "Usuários"]
        fig = px.bar(dist, x="Número de agentes usados", y="Usuários",
                     title="Distribuição: quantos agentes cada usuário utiliza",
                     text_auto=True)
        fig.update_traces(marker_color=COR_SECUNDARIA)
        fig.update_layout(margin=dict(l=10, r=10, t=45, b=10), height=340, title_font_size=15)
        st.plotly_chart(fig, width="stretch")

        tabela(df, "uso_por_usuario")

# ========================= ABA 4: uso-copilot-chat.csv ======================
with abas[3]:
    df0 = d["chat"]
    st.subheader("Uso do Copilot Chat")
    st.caption("Fonte: uso-copilot-chat.csv · Período do relatório: 180 dias")

    APPS_CHAT = {
        "M365 Copilot (app)": "Last activity date of Microsoft 365 Copilot (app) (UTC)",
        "Word": "Last activity date of Word (UTC)",
        "Excel": "Last activity date of Excel (UTC)",
        "PowerPoint": "Last activity date of PowerPoint (UTC)",
        "OneNote": "Last activity date of OneNote (UTC)",
        "Edge": "Last activity date of Edge (UTC)",
        "Teams": "Last activity date of Teams (UTC)",
        "Outlook": "Last activity date of Outlook (UTC)",
        "Copilot Web": "Last activity date of Copilot.cloud.microsoft (UTC)",
    }

    with st.expander("🔎 Filtros", expanded=False):
        f1, f2 = st.columns(2)
        with f1:
            usuario = st.text_input("Usuário (nome ou e-mail) contém", key="ch_usuario")
            min_p = st.number_input("Mínimo de prompts enviados", 0,
                                    int(df0["Prompts submitted"].max()), 0, key="ch_minp")
        with f2:
            max_d = int(df0["Active usage days"].max())
            faixa_dias = st.slider("Dias de uso ativo", 0, max_d, (0, max_d), key="ch_dias")
            sel_apps = st.multiselect("Com atividade no aplicativo",
                                      list(APPS_CHAT.keys()), default=[],
                                      key="ch_apps", placeholder="Qualquer")
        df0f = df0.copy()
        if usuario:
            m = (df0f["Display name"].str.contains(usuario, case=False, na=False)
                 | df0f["User principal name"].str.contains(usuario, case=False, na=False))
            df0f = df0f[m]
        if min_p > 0:
            df0f = df0f[df0f["Prompts submitted"] >= min_p]
        df0f = df0f[df0f["Active usage days"].between(*faixa_dias)]
        for app in sel_apps:
            df0f = df0f[df0f[APPS_CHAT[app]].notna()]
        df0f = filtro_periodo(df0f, "Last activity date", "ch_periodo")

    df = df0f
    if not sem_dados(df):
        ativos = df[df["Prompts submitted"] > 0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Usuários", fmt(len(df)))
        c2.metric("Com atividade", fmt(len(ativos)))
        c3.metric("Prompts enviados", fmt(df["Prompts submitted"].sum()))
        c4.metric("Média de dias ativos", f'{df["Active usage days"].mean():.1f}')

        top = df.nlargest(15, "Prompts submitted")[["Display name", "Prompts submitted"]]
        st.plotly_chart(
            grafico_barras(top, "Prompts submitted", "Display name",
                           "Top 15 usuários por prompts enviados"),
            width="stretch")

        atv = df.dropna(subset=["Last activity date"]).copy()
        if not atv.empty:
            atv["Mês"] = atv["Last activity date"].dt.to_period("M").astype(str)
            mensal = atv.groupby("Mês").size().reset_index(name="Usuários")
            fig = px.line(mensal, x="Mês", y="Usuários", markers=True,
                          title="Usuários por mês de última atividade")
            fig.update_traces(line_color=COR_PRINCIPAL)
            fig.update_layout(margin=dict(l=10, r=10, t=45, b=10), height=340,
                              title_font_size=15)
            st.plotly_chart(fig, width="stretch")

        uso_app = pd.DataFrame({
            "Aplicativo": list(APPS_CHAT.keys()),
            "Usuários com atividade": [df[c].notna().sum() for c in APPS_CHAT.values()],
        }).sort_values("Usuários com atividade", ascending=False)
        st.plotly_chart(
            grafico_barras(uso_app, "Usuários com atividade", "Aplicativo",
                           "Usuários com atividade por aplicativo", cor=COR_SECUNDARIA),
            width="stretch")

        tabela(df, "chat")

# =========================== ABA 5: uso-copilot.csv =========================
with abas[4]:
    df0 = d["copilot"]
    st.subheader("Uso do Microsoft 365 Copilot (licenciados)")
    st.caption("Fonte: uso-copilot.csv · Período do relatório: 180 dias")

    APPS_M365 = {
        "Copilot Chat (trabalho)": "Last activity date of Copilot Chat (work) (UTC)",
        "Copilot Chat (web)": "Last activity date of Copilot Chat (web) (UTC)",
        "Teams": "Last activity date of Teams Copilot (UTC)",
        "Word": "Last activity date of Word Copilot (UTC)",
        "Excel": "Last activity date of Excel Copilot (UTC)",
        "PowerPoint": "Last activity date of PowerPoint Copilot (UTC)",
        "Outlook": "Last activity date of Outlook Copilot (UTC)",
        "OneNote": "Last activity date of OneNote Copilot (UTC)",
        "Loop": "Last activity date of Loop Copilot (UTC)",
        "M365 Copilot (app)": "Last activity date of Microsoft 365 Copilot (app) (UTC)",
        "Edge": "Last activity date of Edge (UTC)",
        "Agentes": "Last activity date of Copilot Agent (UTC)",
    }

    with st.expander("🔎 Filtros", expanded=False):
        f1, f2 = st.columns(2)
        with f1:
            usuario = st.text_input("Usuário (nome ou e-mail) contém", key="cp_usuario")
            min_p = st.number_input("Mínimo de prompts (todos os apps)", 0,
                                    int(df0["Prompts submitted for All Apps"].max()), 0,
                                    key="cp_minp")
        with f2:
            max_d = int(df0["Active Usage Days for All Apps"].max())
            faixa_dias = st.slider("Dias de uso ativo", 0, max_d, (0, max_d), key="cp_dias")
            sel_apps = st.multiselect("Com atividade no aplicativo",
                                      list(APPS_M365.keys()), default=[],
                                      key="cp_apps", placeholder="Qualquer")
        df0f = df0.copy()
        if usuario:
            m = (df0f["Display Name"].str.contains(usuario, case=False, na=False)
                 | df0f["User Principal Name"].str.contains(usuario, case=False, na=False))
            df0f = df0f[m]
        if min_p > 0:
            df0f = df0f[df0f["Prompts submitted for All Apps"] >= min_p]
        df0f = df0f[df0f["Active Usage Days for All Apps"].between(*faixa_dias)]
        for app in sel_apps:
            df0f = df0f[df0f[APPS_M365[app]].notna()]
        df0f = filtro_periodo(df0f, "Last Activity Date", "cp_periodo")

    df = df0f
    if not sem_dados(df):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Usuários licenciados", fmt(len(df)))
        c2.metric("Prompts (todos os apps)", fmt(df["Prompts submitted for All Apps"].sum()))
        c3.metric("Prompts Chat (trabalho)",
                  fmt(df["Prompts submitted for Copilot Chat (work)"].sum()))
        c4.metric("Média de dias ativos",
                  f'{df["Active Usage Days for All Apps"].mean():.1f}')

        top = df.nlargest(15, "Prompts submitted for All Apps")[
            ["Display Name", "Prompts submitted for All Apps"]]
        st.plotly_chart(
            grafico_barras(top, "Prompts submitted for All Apps", "Display Name",
                           "Top 15 usuários por prompts (todos os apps)"),
            width="stretch")

        uso_app = pd.DataFrame({
            "Aplicativo": list(APPS_M365.keys()),
            "Usuários com atividade": [df[c].notna().sum() for c in APPS_M365.values()],
        }).sort_values("Usuários com atividade", ascending=False)
        st.plotly_chart(
            grafico_barras(uso_app, "Usuários com atividade", "Aplicativo",
                           "Usuários com atividade por aplicativo"),
            width="stretch")

        comp = pd.DataFrame({
            "Origem": ["Chat (trabalho)", "Chat (web)"],
            "Prompts": [df["Prompts submitted for Copilot Chat (work)"].sum(),
                        df["Prompts submitted for Copilot Chat (web)"].sum()],
        })
        fig = px.pie(comp, values="Prompts", names="Origem", hole=0.45,
                     title="Prompts no Chat: trabalho × web",
                     color_discrete_sequence=CORES)
        fig.update_layout(margin=dict(l=10, r=10, t=45, b=10), height=320,
                          title_font_size=15)
        st.plotly_chart(fig, width="stretch")

        tabela(df, "copilot")

st.divider()
st.caption("Dados extraídos dos relatórios de uso do Microsoft Copilot.")
# fim
