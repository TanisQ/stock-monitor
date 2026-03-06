import streamlit as st
import sys
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool
from utils.data_fetcher import get_stock_data
from utils.technical import calculate_all_indicators

st.title("📉 个股分析")

stock_pool = load_stock_pool()
if not stock_pool:
    st.warning("股票池为空")
    st.stop()

stock_options = [f"{s['code']} - {s['name']}" for s in stock_pool]
selected = st.selectbox("选择股票", stock_options)
selected_code = selected.split(" - ")[0]

col1, col2, col3 = st.columns(3)
with col1:
    period = st.selectbox("周期", ["daily", "weekly", "monthly"], 
                         format_func=lambda x: {"daily": "日线", "weekly": "周线", "monthly": "月线"}[x])
with col2:
    lookback = st.selectbox("回看周期", [30, 60, 90, 120], index=2)
with col3:
    show_indicators = st.multiselect("显示指标", ["MA", "BOLL", "RSI", "MACD"], default=["MA", "RSI"])

if st.button("获取数据", type="primary"):
    with st.spinner("加载中..."):
        df = get_stock_data(selected_code, period=period)
        if df is not None and not df.empty:
            df = df.tail(lookback).copy()
            df = calculate_all_indicators(df)
            
            fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                               row_heights=[0.6, 0.2, 0.2])
            
            # K线
            fig.add_trace(go.Candlestick(x=df["date"], open=df["open"], high=df["high"], 
                                        low=df["low"], close=df["close"], name="K线"), row=1, col=1)
            
            # MA
            if "MA" in show_indicators:
                for ma, color in [(5, "orange"), (10, "blue"), (20, "purple")]:
                    fig.add_trace(go.Scatter(x=df["date"], y=df[f"MA{ma}"], 
                                            name=f"MA{ma}", line=dict(color=color)), row=1, col=1)
            
            fig.update_layout(height=800, showlegend=True, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            latest = df.iloc[-1]
            st.metric("收盘价", f"{latest['close']:.2f}")
        else:
            st.error("获取数据失败")
