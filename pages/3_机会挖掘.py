import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool
from utils.data_fetcher import get_stock_data
from utils.technical import calculate_all_indicators
from utils.pattern import analyze_all_patterns

st.title("🔍 机会挖掘")

st.markdown("通过技术分析识别投资机会")

scan_all = st.checkbox("扫描整个股票池", value=True)

if scan_all:
    scan_codes = [s["code"] for s in load_stock_pool()]
else:
    stock_pool = load_stock_pool()
    options = [f"{s['code']} - {s['name']}" for s in stock_pool]
    selected = st.selectbox("选择股票", options)
    scan_codes = [selected.split(" - ")[0]]

pattern_filter = st.multiselect("形态筛选", 
    ["杯柄形态", "RSI超卖反弹"], 
    default=["杯柄形态"])

if st.button("开始扫描", type="primary"):
    progress = st.progress(0)
    results = []
    
    for i, code in enumerate(scan_codes):
        progress.progress((i + 1) / len(scan_codes))
        df = get_stock_data(code, lookback=120)
        if df is None:
            continue
        
        df = calculate_all_indicators(df)
        patterns = analyze_all_patterns(df)
        
        signals = []
        if "杯柄形态" in pattern_filter and patterns["cup_handle"][0]:
            signals.append(f"杯柄形态 ({patterns['cup_handle'][1]}%)")
        
        rsi = patterns["rsi"]
        if "RSI超卖反弹" in pattern_filter and "超卖" in rsi["description"]:
            signals.append(rsi["description"])
        
        if signals:
            results.append({
                "code": code,
                "signals": signals
            })
    
    progress.empty()
    
    if results:
        st.success(f"发现 {len(results)} 个机会")
        for r in results:
            st.write(f"**{r['code']}**: {', '.join(r['signals'])}")
    else:
        st.info("未发现符合条件的股票")
