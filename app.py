import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_settings(ticker_dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(ticker_dict, f)
    except:
        pass # Verhindert Fehler in der Cloud

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

st.set_page_config(page_title="Brokkoli Aktien-Monitor", layout="wide")

saved_tickers = load_settings()

st.title("📊 Brokkoli Aktien-Monitor Pro")

with st.sidebar:
    st.header("Konfiguration")
    # Erweiterte Zeitspanne
    period = st.selectbox("Zeitraum", options=["1mo", "1y", "3y"], 
                         format_func=lambda x: "1 Monat" if x=="1mo" else "1 Jahr" if x=="1y" else "3 Jahre")
    
    st.divider()
    tickers_input = []
    current_input_values = {}
    for i in range(20):
        key = f"ticker_{i}"
        val = st.text_input(f"Stock {i+1}", value=saved_tickers.get(key, ""), key=key)
        current_input_values[key] = val.strip()
        if val.strip():
            tickers_input.append(val.strip().upper())

if tickers_input:
    save_settings(current_input_values)
    cols = st.columns(2, gap="small")
    
    for idx, ticker in enumerate(tickers_input):
        with cols[idx % 2]:
            try:
                t_obj = yf.Ticker(ticker)
                # Lade genug Daten für den SMA200 und den gewählten Zeitraum
                data = t_obj.history(period="4y") 
                if data.empty: continue

                info = t_obj.info
                name = (info.get('shortName') or ticker)[:25]
                
                # Berechnungen
                data['SMA200'] = data['Close'].rolling(window=200).mean()
                data['RSI'] = calculate_rsi(data['Close'])
                
                curr_price = data['Close'].iloc[-1]
                curr_sma = data['SMA200'].iloc[-1]
                curr_rsi = data['RSI'].iloc[-1]
                dist_sma = ((curr_price - curr_sma) / curr_sma) * 100
                
                rsi_signal = "🟢" if curr_rsi < 35 else "🔴" if curr_rsi > 65 else "⚪"
                trend_signal = "✅" if curr_price > curr_sma else "❌"
                
                st.markdown(f"#### {ticker} | {name}")
                
                # Zeitraum-Filter für den Plot
                if period == "1mo": plot_data = data.tail(30)
                elif period == "1y": plot_data = data.tail(252)
                else: plot_data = data.tail(252 * 3) # 3 Jahre

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Close'], name='Kurs', line=dict(color='#00d1ff', width=2)))
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['SMA200'], name='200d', line=dict(color='red', dash='dot', width=1.5)))
                
                fig.update_layout(height=260, template="plotly_dark", showlegend=False, 
                                  margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False))
                
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f"**P:** {curr_price:.2f} | **RSI:** {curr_rsi:.1f} {rsi_signal} | **200d:** {dist_sma:+.1f}% {trend_signal}")
                
                # --- NEU: NEWS TICKER ---
                with st.expander(f"📰 News zu {ticker}"):
                    news = t_obj.news[:3] # Die letzten 3 Schlagzeilen
                    if news:
                        for item in news:
                            st.markdown(f"**[{item['title']}]({item['link']})**")
                            st.caption(f"Quelle: {item.get('publisher', 'Unbekannt')}")
                    else:
                        st.write("Keine aktuellen News gefunden.")
                
                st.divider()

            except Exception as e:
                st.error(f"Fehler bei {ticker}")
else:
    st.info("👈 Bitte gib Ticker in der Sidebar ein.")
