# Stock Price Lookup

A small Python app that retrieves the latest available stock price for a ticker entered by the user.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL shown by Streamlit, enter a ticker such as `AAPL`, and select **Get current price**.

The app uses Yahoo Finance through `yfinance`. Quotes may be delayed depending on the exchange and data source.
