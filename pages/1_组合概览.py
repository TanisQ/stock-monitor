import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool, add_stock, remove_stock
from utils.data_fetcher import get_realtime_quote

st.title("📈 组合概览")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("当前股票池")
    stock_pool = load_stock_pool()
    
    if stock_pool:
        codes = [s["code"] for s in stock_pool]
        realtime_df = get_realtime_quote(codes)
        
        if realtime_df is not None and not realtime_df.empty:
            display_data = []
            for stock in stock_pool:
                code = stock["code"]
                stock_data = realtime_df[realtime_df["代码"] == code]
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    display_data.append({
                        "代码": code,
                        "名称": stock["name"],
                        "最新价": f"{row['最新价']:.2f}",
                        "涨跌幅": f"{row['涨跌幅']:.2f}%"
                    })
            
            import pandas as pd
            df_display = pd.DataFrame(display_data)
            st.dataframe(df_display, use_container_width=True)
        else:
            for stock in stock_pool:
                st.text(f"{stock['code']} - {stock['name']}")
    else:
        st.info("股票池为空")

with col2:
    st.subheader("添加股票")
    with st.form("add_stock"):
        new_code = st.text_input("股票代码", placeholder="如: 600426")
        new_name = st.text_input("股票名称", placeholder="如: 华鲁恒升")
        if st.form_submit_button("添加"):
            if new_code and new_name:
                success, msg = add_stock(new_code, new_name)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
