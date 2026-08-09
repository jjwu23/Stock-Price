"""Simple current stock-price lookup app."""

from datetime import datetime

import streamlit as st
import yfinance as yf


st.set_page_config(
    page_title="Stock Price Lookup!!!",
    page_icon="📈",
    layout="centered",
)


@st.cache_data(ttl=60, show_spinner=False)
def get_quote(ticker_symbol: str) -> dict:
    """Fetch the latest available quote and company name from Yahoo Finance."""
    ticker = yf.Ticker(ticker_symbol)

    # fast_info is lighter and more reliable for the latest market price than
    # downloading a full historical data window.
    try:
        fast_info = ticker.fast_info
        price = fast_info.get("lastPrice")
        previous_close = fast_info.get("previousClose")
        currency = fast_info.get("currency", "USD")
    except Exception:
        price = previous_close = None
        currency = "USD"

    if price is None:
        history = ticker.history(period="5d", auto_adjust=False)
        if history.empty:
            raise ValueError(f"No quote data found for {ticker_symbol}.")
        price = float(history["Close"].dropna().iloc[-1])
        previous_close = (
            float(history["Close"].dropna().iloc[-2])
            if len(history["Close"].dropna()) > 1
            else None
        )

    company_name = ticker_symbol
    try:
        company_name = ticker.info.get("longName") or ticker.info.get("shortName") or ticker_symbol
    except Exception:
        pass

    change = None
    change_percent = None
    if previous_close:
        change = float(price) - float(previous_close)
        change_percent = change / float(previous_close) * 100

    return {
        "symbol": ticker_symbol,
        "name": company_name,
        "price": float(price),
        "change": change,
        "change_percent": change_percent,
        "currency": currency,
        "updated_at": datetime.now().astimezone().strftime("%b %-d, %Y at %-I:%M %p %Z"),
    }


st.title("📈 Stock Price Lookup...")
st.caption("Get the latest available market price for a stock ticker.")

with st.form("quote_form"):
    ticker_input = st.text_input(
        "Ticker symbol",
        value="AAPL",
        max_chars=10,
        placeholder="e.g. MSFT, TSLA, NVDA",
    )
    submitted = st.form_submit_button("Get current price", type="primary", use_container_width=True)

if submitted:
    symbol = ticker_input.strip().upper()
    if not symbol:
        st.warning("Enter a ticker symbol to look up.")
    elif not symbol.replace("-", "").replace(".", "").isalnum():
        st.warning("Use a valid ticker symbol, such as AAPL or BRK-B.")
    else:
        with st.spinner(f"Looking up {symbol}..."):
            try:
                quote = get_quote(symbol)
            except Exception as exc:
                st.error(f"Could not retrieve a quote for {symbol}. Check the symbol and try again.")
                st.caption(f"Details: {exc}")
            else:
                st.subheader(quote["name"])
                st.caption(quote["symbol"])

                price_column, change_column = st.columns(2)
                price_column.metric(
                    "Latest price",
                    f"{quote['currency']} {quote['price']:,.2f}",
                )
                if quote["change"] is not None:
                    change_column.metric(
                        "Day change",
                        f"{quote['change']:+,.2f}",
                        f"{quote['change_percent']:+.2f}%",
                    )
                else:
                    change_column.metric("Day change", "Unavailable")

                st.caption(f"Last available quote: {quote['updated_at']}. Data provided by Yahoo Finance.")

st.divider()
st.caption("Quotes may be delayed depending on the exchange and data source.")
