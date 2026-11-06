import time
from alpha_vantage.timeseries import TimeSeries
import matplotlib.pyplot as plt
import pandas as pd
import requests
import streamlit as st

# 1. Configuração da página
st.set_page_config(
    page_title="DashCryptoStox", page_icon="📈", layout="wide"
)

# Chave pessoal da Alpha Vantage
ALPHA_VANTAGE_KEY = "JNCHBH9UKS1UN32Y"

# 2. CSS Customizado - Fundo mais claro e substituição total dos fundos brancos por azul claro
st.markdown(
    """
    <style>
    header, footer, #MainMenu { visibility: hidden; }

    /* Fundo geral da aplicação mais claro e moderno (#132238) */
    .stApp {
        background-color: #132238 !important;
        color: #f8fafc !important;
    }

    /* Barra Lateral */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155 !important;
    }
    [data-testid="stSidebar"] * {
        color: #cbd5e1 !important;
    }
    
    div[data-baseweb="radio"] div {
        background-color: transparent !important;
    }
    [data-testid="stSidebar"] label {
        background-color: transparent !important;
        color: #cbd5e1 !important;
    }
    [data-testid="stSidebar"] label:hover {
        color: #38bdf8 !important;
    }

    /* Botão "+ Adicionar Ativo" no Topo */
    [data-testid="stPopover"] button, 
    div[data-testid="stPopover"] > button {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    [data-testid="stPopover"] button:hover, 
    div[data-testid="stPopover"] > button:hover {
        background-color: #334155 !important;
        color: #ffffff !important;
        border-color: #ffffff !important;
    }
    
    div[data-testid="stPopoverBody"] {
        background-color: #1e293b !important;
        border: 1px solid #38bdf8 !important;
    }

    /* Inputs e Selectboxes - Removendo todo o fundo branco indesejado */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    input, 
    div[data-baseweb="popover"] div {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
    }
    
    /* Elimina o fundo branco externo das caixas de seleção mostrado na imagem */
    div.stSelectbox > div > div {
        background-color: #1e293b !important;
        border: 1px solid #38bdf8 !important;
    }
    
    div[data-baseweb="select"] * {
        color: #ffffff !important;
        background-color: #1e293b !important;
    }
    
    /* Dropdowns abertos do Streamlit */
    ul[data-baseweb="menu"] {
        background-color: #1e293b !important;
    }
    ul[data-baseweb="menu"] li {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }
    ul[data-baseweb="menu"] li:hover {
        background-color: #334155 !important;
    }

    svg {
        fill: #38bdf8 !important;
    }

    /* Estilização dos Cards */
    .card-title {
        font-size: 11px;
        font-weight: 700;
        color: #38bdf8;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .card-price {
        font-size: 20px;
        font-weight: 700;
        color: #ffffff;
        margin: 4px 0;
    }
    .card-change {
        font-size: 13px;
        font-weight: 600;
    }

    /* Botão '✕' de Remover nos Cards */
    .stButton > button {
        background-color: transparent !important;
        color: #94a3b8 !important;
        border: none !important;
        font-size: 13px !important;
        padding: 0 !important;
        line-height: 1 !important;
    }
    .stButton > button:hover {
        color: #ef4444 !important;
    }

    /* Botão "Confirmar Adição" em Destaque Azul Claro */
    button[kind="secondary"], div.stButton > button {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    button[kind="secondary"]:hover, div.stButton > button:hover {
        background-color: #38bdf8 !important;
        color: #132238 !important;
    }

    /* Botão Azul Claro do Simulador */
    div.stButton > button[key="btn_calc"] {
        background-color: #38bdf8 !important;
        color: #132238 !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
        font-weight: 700 !important;
        border: none !important;
    }
    div.stButton > button[key="btn_calc"]:hover {
        background-color: #0ea5e9 !important;
        color: #ffffff !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# 3. Estado da sessão
if "tracked_assets" not in st.session_state:
    st.session_state.tracked_assets = [
        {"id": "solana", "type": "crypto"},
        {"id": "binancecoin", "type": "crypto"},
        {"id": "ethereum", "type": "crypto"},
        {"id": "ripple", "type": "crypto"},
        {"id": "tesla-xstock", "type": "stock"},
        {"id": "apple-xstock", "type": "stock"},
    ]

if "last_known_prices" not in st.session_state:
    st.session_state.last_known_prices = {}

FALLBACK_USD_BRL = 5.5

FALLBACK_COINS = [
    # Criptomoedas
    {"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC", "type": "crypto"},
    {"id": "ethereum", "name": "Ethereum", "symbol": "ETH", "type": "crypto"},
    {
        "id": "binancecoin",
        "name": "Binance Coin",
        "symbol": "BNB",
        "type": "crypto",
    },
    {"id": "solana", "name": "Solana", "symbol": "SOL", "type": "crypto"},
    {"id": "ripple", "name": "Ripple", "symbol": "XRP", "type": "crypto"},
    {"id": "cardano", "name": "Cardano", "symbol": "ADA", "type": "crypto"},
    {"id": "dogecoin", "name": "Dogecoin", "symbol": "DOGE", "type": "crypto"},
    {"id": "polkadot", "name": "Polkadot", "symbol": "DOT", "type": "crypto"},
    {"id": "sui", "name": "Sui", "symbol": "SUI", "type": "crypto"},
    {
        "id": "avalanche-2",
        "name": "Avalanche",
        "symbol": "AVAX",
        "type": "crypto",
    },
    {"id": "chainlink", "name": "Chainlink", "symbol": "LINK", "type": "crypto"},
    {"id": "uniswap", "name": "Uniswap", "symbol": "UNI", "type": "crypto"},
    {"id": "litecoin", "name": "Litecoin", "symbol": "LTC", "type": "crypto"},
    {"id": "stellar", "name": "Stellar", "symbol": "XLM", "type": "crypto"},
    {"id": "cosmos", "name": "Cosmos", "symbol": "ATOM", "type": "crypto"},
    {"id": "monero", "name": "Monero", "symbol": "XMR", "type": "crypto"},
    {"id": "shiba-inu", "name": "Shiba Inu", "symbol": "SHIB", "type": "crypto"},
    {
        "id": "ethereum-classic",
        "name": "Ethereum Classic",
        "symbol": "ETC",
        "type": "crypto",
    },
    # Ações Globais
    {
        "id": "tesla-xstock",
        "name": "Tesla Stock",
        "symbol": "TSLA",
        "type": "stock",
    },
    {
        "id": "apple-xstock",
        "name": "Apple Stock",
        "symbol": "AAPL",
        "type": "stock",
    },
    {
        "id": "nvidia-xstock",
        "name": "NVIDIA Stock",
        "symbol": "NVDA",
        "type": "stock",
    },
    {
        "id": "microsoft-xstock",
        "name": "Microsoft Stock",
        "symbol": "MSFT",
        "type": "stock",
    },
    {
        "id": "amazon-xstock",
        "name": "Amazon Stock",
        "symbol": "AMZN",
        "type": "stock",
    },
    {
        "id": "google-xstock",
        "name": "Google Stock",
        "symbol": "GOOGL",
        "type": "stock",
    },
    {
        "id": "netflix-xstock",
        "name": "Netflix Stock",
        "symbol": "NFLX",
        "type": "stock",
    },
    {"id": "meta-xstock", "name": "Meta Stock", "symbol": "META", "type": "stock"},
    {
        "id": "coca-cola-xstock",
        "name": "Coca-Cola Stock",
        "symbol": "KO",
        "type": "stock",
    },
    {
        "id": "intel-xstock",
        "name": "Intel Stock",
        "symbol": "INTC",
        "type": "stock",
    },
    {"id": "amd-xstock", "name": "AMD Stock", "symbol": "AMD", "type": "stock"},
]

GLOBAL_TICKER_MAP = {
    "tesla-xstock": "TSLA",
    "apple-xstock": "AAPL",
    "nvidia-xstock": "NVDA",
    "microsoft-xstock": "MSFT",
    "amazon-xstock": "AMZN",
    "google-xstock": "GOOGL",
    "netflix-xstock": "NFLX",
    "meta-xstock": "META",
    "coca-cola-xstock": "KO",
    "intel-xstock": "INTC",
    "amd-xstock": "AMD",
}

FALLBACK_PRICES = {
    "tesla-xstock": 385.19,
    "apple-xstock": 230.00,
    "nvidia-xstock": 135.00,
    "microsoft-xstock": 420.00,
    "amazon-xstock": 257.45,
    "google-xstock": 282.57,
    "netflix-xstock": 66.50,
    "meta-xstock": 500.00,
    "coca-cola-xstock": 95.57,
    "intel-xstock": 22.00,
    "amd-xstock": 140.00,
}


# 4. Mapeamento Alpha Vantage para Ações
@st.cache_data(ttl=60)
def fetch_stock_alpha_vantage(coin_id, currency):
    t_symbol = GLOBAL_TICKER_MAP.get(coin_id, "TSLA")
    try:
        ts = TimeSeries(key=ALPHA_VANTAGE_KEY, output_format="pandas")
        data, _ = ts.get_daily(symbol=t_symbol)
        if not data.empty:
            price_usd = float(data["4. close"].iloc[0])
            prev_price = float(data["4. close"].iloc[1])
            change = (
                ((price_usd - prev_price) / prev_price) * 100
                if prev_price > 0
                else 0.0
            )
            price = (
                price_usd if currency == "usd" else price_usd * FALLBACK_USD_BRL
            )
            return {currency: price, f"{currency}_24h_change": change}
    except Exception:
        pass

    p_usd = FALLBACK_PRICES.get(coin_id, 100.0)
    p = p_usd if currency == "usd" else p_usd * FALLBACK_USD_BRL
    return {currency: p, f"{currency}_24h_change": 0.5}


def fetch_single_asset_fallback(coin_id, currency):
    if "-xstock" in coin_id:
        return fetch_stock_alpha_vantage(coin_id, currency)

    clean_id = coin_id.lower().replace("-xstock", "")
    if clean_id == "avalanche-2":
        clean_id = "avalanche"

    try:
        res = requests.get(
            f"https://api.coincap.io/v2/assets/{clean_id}", timeout=5
        )
        if res.status_code == 200:
            data = res.json().get("data", {})
            price_usd = float(data.get("priceUsd", 0))
            change = float(data.get("changePercent24Hr", 0))
            price = (
                price_usd if currency == "usd" else price_usd * FALLBACK_USD_BRL
            )
            return {currency: price, f"{currency}_24h_change": change}
    except Exception:
        pass

    if coin_id in st.session_state.last_known_prices:
        return st.session_state.last_known_prices[coin_id]

    return {currency: 0.0, f"{currency}_24h_change": 0.0}


@st.cache_data(ttl=60)
def load_market_data(ids_str, currency):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies={currency}&include_24hr_change=true"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}


# 5. Barra Lateral (Sidebar)
st.sidebar.markdown(
    "<h2 style='color: #ffffff !important; font-size: 20px; margin-bottom: 24px;'>DashCryptoStox</h2>",
    unsafe_allow_html=True,
)

menu_opcao = st.sidebar.radio(
    "Navegação", ["Visão Geral", "Criptos", "Ações"]
)
category_map = {"Visão Geral": "all", "Criptos": "crypto", "Ações": "stock"}
current_category = category_map[menu_opcao]

st.sidebar.markdown("---")
st.sidebar.markdown("### Configurações")
currency_choice = st.sidebar.selectbox(
    "Moeda:", options=["USD ($)", "BRL (R$)"]
)
preferred_currency = "brl" if "BRL" in currency_choice else "usd"
symbol = "R$" if preferred_currency == "brl" else "$"

# 6. Cabeçalho + Botão "+ Adicionar Ativo"
col_title, col_add_btn = st.columns([4, 1])
with col_title:
    st.markdown(
        "<h1 style='color: #ffffff; font-size: 24px; margin: 0;'>Painel Financeiro</h1>",
        unsafe_allow_html=True,
    )

with col_add_btn:
    with st.popover("+ Adicionar Ativo"):
        st.markdown(
            "<p style='color: #38bdf8; font-size: 13px; font-weight: 600; margin-bottom: 4px;'>Selecione o Ativo:</p>",
            unsafe_allow_html=True,
        )
        selected_to_add = st.selectbox(
            "Pesquisar ativo",
            options=[c["id"] for c in FALLBACK_COINS],
            format_func=lambda x: f"{x.upper()}",
            label_visibility="collapsed",
            key="select_add_asset",
        )
        if st.button("Confirmar Adição", key="btn_confirm_add"):
            if selected_to_add:
                coin = next(
                    c for c in FALLBACK_COINS if c["id"] == selected_to_add
                )
                if not any(
                    a["id"] == coin["id"]
                    for a in st.session_state.tracked_assets
                ):
                    st.session_state.tracked_assets.append(
                        {"id": coin["id"], "type": coin["type"]}
                    )
                    st.success(f"{coin['id'].upper()} adicionado!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.warning("Ativo já está na lista.")

st.markdown("<br>", unsafe_allow_html=True)

# 7. Cards de Ativos
filtered_assets = [
    a
    for a in st.session_state.tracked_assets
    if current_category == "all" or a["type"] == current_category
]

ids_list = ",".join(
    [
        a["id"]
        for a in st.session_state.tracked_assets
        if "-xstock" not in a["id"]
    ]
)
market_data = load_market_data(ids_list, preferred_currency) or {}

if filtered_assets:
    cols = st.columns(6)
    for index, asset in enumerate(filtered_assets):
        coin_id = asset["id"]

        if "-xstock" in coin_id:
            info = fetch_stock_alpha_vantage(coin_id, preferred_currency)
        else:
            info = market_data.get(coin_id)
            if not info or preferred_currency not in info:
                info = fetch_single_asset_fallback(coin_id, preferred_currency)

        price = info.get(preferred_currency, 0.0)
        change = info.get(f"{preferred_currency}_24h_change", 0.0)
        is_positive = change >= 0
        color_change = "#10b981" if is_positive else "#ef4444"
        sign = "+" if is_positive else ""

        st.session_state.last_known_prices[coin_id] = info

        with cols[index % 6]:
            c_head, c_del = st.columns([4, 1])
            with c_head:
                st.markdown(
                    f"<div class='card-title'>{coin_id.upper()}</div>",
                    unsafe_allow_html=True,
                )
            with c_del:
                if st.button("✕", key=f"del_{coin_id}"):
                    st.session_state.tracked_assets = [
                        a
                        for a in st.session_state.tracked_assets
                        if a["id"] != coin_id
                    ]
                    st.rerun()

            st.markdown(
                f"""
                <div style="background-color: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 16px;">
                    <div class="card-price">{symbol} {price:,.2f}</div>
                    <div class="card-change" style="color: {color_change};">{sign}{change:.2f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# 8. Gráfico Histórico com Seletor de Ativo e Períodos (24h, 7D, 1M, 1A) + Fallback Seguro
st.markdown("<br>", unsafe_allow_html=True)

col_h_title, col_h_sel, col_h_per = st.columns([2, 2, 2])
with col_h_title:
    st.markdown(
        "<h2 style='color: #ffffff; font-size: 18px; margin-top: 8px;'>Histórico do Ativo</h2>",
        unsafe_allow_html=True,
    )

with col_h_sel:
    all_tracked_ids = [a["id"] for a in st.session_state.tracked_assets]
    chart_asset = st.selectbox(
        "Selecione o ativo para o gráfico:",
        options=all_tracked_ids,
        format_func=lambda x: x.upper(),
        key="chart_asset_selector",
        label_visibility="collapsed",
    )

with col_h_per:
    periodo = st.selectbox(
        "Período:",
        options=["24h", "7D", "1M", "1A"],
        key="chart_period_selector",
        label_visibility="collapsed",
    )

periodo_dias_map = {"24h": 1, "7D": 7, "1M": 30, "1A": 365}
dias_solicitados = periodo_dias_map.get(periodo, 1)


@st.cache_data(ttl=60)
def fetch_chart_data(coin_id, currency, days=1):
    prices = []
    try:
        if "-xstock" in coin_id:
            t_symbol = GLOBAL_TICKER_MAP.get(coin_id, "TSLA")
            ts = TimeSeries(key=ALPHA_VANTAGE_KEY, output_format="pandas")
            data, _ = ts.get_daily(symbol=t_symbol)
            if not data.empty:
                limit_rows = (
                    2
                    if days <= 1
                    else (
                        7
                        if days <= 7
                        else (30 if days <= 30 else min(len(data), 365))
                    )
                )
                subset = data.head(limit_rows).iloc[::-1]
                for idx, row in subset.iterrows():
                    p = (
                        row["4. close"]
                        if currency == "usd"
                        else row["4. close"] * FALLBACK_USD_BRL
                    )
                    prices.append([int(idx.timestamp() * 1000), p])
        else:
            clean_id = coin_id.lower()
            if clean_id == "avalanche-2":
                clean_id = "avalanche"
            else:
                clean_id = clean_id.replace("-xstock", "")

            url = f"https://api.coingecko.com/api/v3/coins/{clean_id}/market_chart?vs_currency={currency}&days={days}"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data_json = res.json()
                if "prices" in data_json:
                    prices = data_json.get("prices", [])
    except Exception:
        pass

    if not prices:
        base_p = FALLBACK_PRICES.get(coin_id, 100.0)
        if "-xstock" not in coin_id and coin_id in st.session_state.last_known_prices:
            base_p = st.session_state.last_known_prices[coin_id].get("usd", 100.0)
        
        if currency == "brl":
            base_p *= FALLBACK_USD_BRL

        now_ms = int(time.time() * 1000)
        step_ms = 86400000 if days > 1 else 3600000
        num_points = days if days > 1 else 24
        
        import random
        curr = base_p * 0.98
        for i in range(num_points):
            t_stamp = now_ms - ((num_points - 1 - i) * step_ms)
            curr += (random.random() - 0.48) * (base_p * 0.01)
            prices.append([t_stamp, curr])

    return prices


prices_history = fetch_chart_data(
    chart_asset, preferred_currency, dias_solicitados
)

if prices_history:
    df_chart = pd.DataFrame(prices_history, columns=["timestamp", "price"])
    df_chart["timestamp"] = pd.to_datetime(df_chart["timestamp"], unit="ms")

    fig, ax = plt.subplots(figsize=(10, 3.5))
    fig.patch.set_facecolor("#132238")
    ax.set_facecolor("#1e293b")

    ax.plot(
        df_chart["timestamp"],
        df_chart["price"],
        color="#38bdf8",
        linewidth=1.8,
    )

    ax.tick_params(colors="#94a3b8", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#334155")

    ax.grid(True, color="#334155", linestyle="--", linewidth=0.5)

    st.pyplot(fig)
else:
    st.info(f"Carregando histórico para {chart_asset.upper()}...")

# 9. Simulador de Carteira
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="background-color: #1e293b; padding: 16px 20px; border-radius: 8px; border: 1px solid #334155;">
        <h3 style="color: #ffffff; font-size: 16px; margin: 0 0 14px 0;">Simulador de Carteira</h3>
    </div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns([2, 2, 1.5, 3])
with c1:
    calc_asset = st.selectbox(
        "Ativo:",
        options=[a["id"] for a in st.session_state.tracked_assets],
        key="calc_sel",
    )
with c2:
    calc_amount = st.number_input(
        "Quantidade:", min_value=0.0, value=0.5, step=0.1
    )
with c3:
    st.markdown("<br>", unsafe_allow_html=True)
    btn_calc = st.button("Calcular Saldo", key="btn_calc")

with c4:
    st.markdown("<br>", unsafe_allow_html=True)
    info_calc = market_data.get(calc_asset) or fetch_single_asset_fallback(
        calc_asset, preferred_currency
    )
    asset_price = info_calc.get(preferred_currency, 0.0)
    total_val = asset_price * calc_amount
    st.markdown(
        f"<div style='text-align: right; color: #ffffff; font-weight: 700; font-size: 16px;'>Valor Total Estimado: <span style='color: #38bdf8;'>{symbol} {total_val:,.2f}</span></div>",
        unsafe_allow_html=True,
    )