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
        pass 

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
                # Daten laden (4 Jahre, um 3 Jahre + SMA200 abzudecken)
                data = t_obj.history(period="4y") 
                if data.empty: 
                    st.error(f"Keine Daten für {ticker}")
                    continue

                info = t_obj.info
                name = (info.get('shortName') or ticker)[:25]
                
                data['SMA200'] = data['Close'].rolling(window=200).mean()
                data['RSI'] = calculate_rsi(data['Close'])
                
                curr_price = data['Close'].iloc[-1]
                curr_sma = data['SMA200'].iloc[-1]
                curr_rsi = data['RSI'].iloc[-1]
                dist_sma = ((curr_price - curr_sma) / curr_sma) * 100
                
                rsi_signal = "🟢" if curr_rsi < 35 else "🔴" if curr_rsi > 65 else "⚪"
                trend_signal = "✅" if curr_price > curr_sma else "❌"
                
                st.markdown(f"#### {ticker} | {name}")
                
                # Plot-Zeitraum filtern
                if period == "1mo": plot_data = data.tail(30)
                elif period == "1y": plot_data = data.tail(252)
                else: plot_data = data.tail(252 * 3)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Close'], name='Kurs', line=dict(color='#00d1ff', width=2)))
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['SMA200'], name='200d', line=dict(color='red', dash='dot', width=1.5)))
                
                fig.update_layout(height=260, template="plotly_dark", showlegend=False, 
                                  margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False))
                
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{ticker}")
                st.markdown(f"**P:** {curr_price:.2f} | **RSI:** {curr_rsi:.1f} {rsi_signal} | **200d:** {dist_sma:+.1f}% {trend_signal}")
                
                # News Sektion mit verbesserter Titelsuche
                try:
                    with st.expander(f"📰 News zu {ticker}"):
                        stock_news = t_obj.news
                        if stock_news:
                            for item in stock_news[:3]:
                                n_title = item.get('title') or item.get('headline') or item.get('text') or "Schlagzeile verfügbar"
                                n_link = item.get('link') or item.get('url') or "#"
                                n_pub = item.get('publisher') or item.get('source') or "Quelle"
                                st.markdown(f"**[{n_title}]({n_link})**")
                                st.caption(f"Quelle: {n_pub}")
                        else:
                            st.write("Keine aktuellen News gefunden.")
                except:
                    st.write("News-Schnittstelle momentan blockiert.")
                
                st.divider()

            except Exception as e:
                st.error(f"Fehler bei {ticker}")
else:
    st.info("👈 Bitte gib Ticker in der Sidebar ein.")import streamlit as st
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
        pass 

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
                # Genug Daten laden (4 Jahre für 3 Jahre Plot + SMA200 Vorlauf)
                data = t_obj.history(period="4y") 
                if data.empty: 
                    st.error(f"Keine Daten für {ticker}")
                    continue

                info = t_obj.info
                name = (info.get('shortName') or ticker)[:25]
                
                data['SMA200'] = data['Close'].rolling(window=200).mean()
                data['RSI'] = calculate_rsi(data['Close'])
                
                curr_price = data['Close'].iloc[-1]
                curr_sma = data['SMA200'].iloc[-1]
                curr_rsi = data['RSI'].iloc[-1]
                dist_sma = ((curr_price - curr_sma) / curr_sma) * 100
                
                rsi_signal = "🟢" if curr_rsi < 35 else "🔴" if curr_rsi > 65 else "⚪"
                trend_signal = "✅" if curr_price > curr_sma else "❌"
                
                st.markdown(f"#### {ticker} | {name}")
                
                if period == "1mo": plot_data = data.tail(30)
                elif period == "1y": plot_data = data.tail(252)
                else: plot_data = data.tail(252 * 3)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['Close'], name='Kurs', line=dict(color='#00d1ff', width=2)))
                fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['SMA200'], name='200d', line=dict(color='red', dash='dot', width=1.5)))
                
                fig.update_layout(height=260, template="plotly_dark", showlegend=False, 
                                  margin=dict(l=0, r=0, t=10, b=0), xaxis=dict(showgrid=False))
                
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{ticker}")
                st.markdown(f"**P:** {curr_price:.2f} | **RSI:** {curr_rsi:.1f} {rsi_signal} | **200d:** {dist_sma:+.1f}% {trend_signal}")
                
                # News Sektion mit Fehlerschutz
                try:
                    with st.expander(f"📰 News zu {ticker}"):
                        stock_news = t_obj.news
                        if stock_news:
                            for item in stock_news[:3]:
                                n_title = item.get('title', 'Kein Titel')
                                n_link = item.get('link', '#')
                                n_pub = item.get('publisher', 'Unbekannt')
                                st.markdown(f"**[{n_title}]({n_link})**")
                                st.caption(f"Quelle: {n_pub}")
                        else:
                            st.write("Keine News verfügbar.")
                except:
                    st.write("News-Schnittstelle antwortet nicht.")
                
                st.divider()

            except Exception as e:
                st.error(f"Fehler bei {ticker}: {e}")
else:
    st.info("👈 Bitte gib Ticker in der Sidebar ein.")
