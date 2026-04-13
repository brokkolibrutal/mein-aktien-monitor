import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_settings(ticker_dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(ticker_dict, f)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Konfiguration für 2026er Version
st.set_page_config(page_title="Aktien-Monitor Pro v26", layout="wide")

saved_tickers = load_settings()

st.title("📊 Aktien-Monitor Pro (v26.0.1)")

with st.sidebar:
    st.header("Watchlist")
    period = st.selectbox("Zeitraum", options=["1mo", "1y"], format_func=lambda x: "1 Monat" if x=="1mo" else "1 Jahr")
    st.divider()
    tickers_input = []
    current_input_values = {}
    for i in range(20):
        key = f"ticker_{i}"
        val = st.text_input(f"Stock {i+1}", value=saved_tickers.get(key, ""), key=key)
        current_input_values[key] = val.strip()
        if val.strip():
            tickers_input.append(val.strip())

if tickers_input:
    save_settings(current_input_values)
    
    # Grid-Layout für maximale Übersicht
    cols = st.columns(2, gap="small")
    
    for idx, ticker in enumerate(tickers_input):
        with cols[idx % 2]:
            try:
                t_obj = yf.Ticker(ticker)
                data = t_obj.history(period="2y")
                if data.empty: continue

                info = t_obj.info
                name = (info.get('shortName') or "Unbekannt")[:22]
                
                # Berechnungen
                data['SMA200'] = data['Close'].rolling(window=200).mean()
                data['RSI'] = calculate_rsi(data['Close'])
                
                curr_price = data['Close'].iloc[-1]
                curr_sma = data['SMA200'].iloc[-1]
                curr_rsi = data['RSI'].iloc[-1]
                dist_sma = ((curr_price - curr_sma) / curr_sma) * 100
                
                # Signale
                rsi_signal = "🟢" if curr_rsi < 35 else "🔴" if curr_rsi > 65 else "⚪"
                trend_signal = "✅" if curr_price > curr_sma else "❌"
                
                # Header & Metriken kompakt in einer Zeile
                st.markdown(f"#### {ticker} | {name}")
                
                # Plotly Chart
                fig = go.Figure()
                plot_data = data.tail(30) if period == "1mo" else data.tail(252)
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Close'], name='Kurs', line=dict(color='#00d1ff', width=2)))
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['SMA200'], name='200d', line=dict(color='red', dash='dot', width=1.5)))
                
                fig.update_layout(
                    height=260, 
                    template="plotly_dark", 
                    showlegend=False, 
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=0, r=0, t=10, b=0),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
                )
                
                # Das neue width="stretch" aus v26
                st.plotly_chart(fig, width="stretch")

                # Info-Leiste
                st.markdown(f"**P:** {curr_price:.2f} | **RSI:** {curr_rsi:.1f} {rsi_signal} | **200d:** {dist_sma:+.1f}% {trend_signal}")
                st.divider()

            except Exception:
                st.error(f"Fehler: {ticker}")
else:
    st.info("👈 Bitte gib links in der Sidebar deine Aktien-Ticker ein.")