import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool, add_stock, remove_stock, save_stock_pool
from utils.data_fetcher import get_realtime_quote, get_stock_name

st.title("📈 组合概览")

# 股票池管理
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("当前股票池")
    stock_pool = load_stock_pool()
    
    if stock_pool:
        # 获取实时行情
        codes = [s["code"] for s in stock_pool]
        realtime_df = get_realtime_quote(codes)
        
        if realtime_df is not None and not realtime_df.empty:
            # 合并股票池信息和实时行情
            display_data = []
            for stock in stock_pool:
                code = stock["code"]
                stock_data = realtime_df[realtime_df["代码"] == code]
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    # 安全获取字段
                    try:
                        latest_price = row.get('最新价', row.get('close', '-'))
                        change_pct = row.get('涨跌幅', row.get('pct_change', 0))
                        change_amt = row.get('涨跌额', row.get('change', 0))
                        volume = row.get('成交量', row.get('vol', 0))
                        
                        display_data.append({
                            "代码": code,
                            "名称": stock["name"],
                            "最新价": f"{float(latest_price):.2f}" if pd.notna(latest_price) else "-",
                            "涨跌幅": f"{float(change_pct):.2f}%" if pd.notna(change_pct) else "-",
                            "涨跌额": f"{float(change_amt):.2f}" if pd.notna(change_amt) else "-",
                            "成交量": f"{float(volume)/10000:.0f}万" if pd.notna(volume) else "-",
                            "所属行业": stock.get("category", "-")
                        })
                    except Exception as e:
                        # 如果获取字段失败，只显示基本信息
                        display_data.append({
                            "代码": code,
                            "名称": stock["name"],
                            "最新价": "-",
                            "涨跌幅": "-",
                            "涨跌额": "-",
                            "成交量": "-",
                            "所属行业": stock.get("category", "-")
                        })
            
            df_display = pd.DataFrame(display_data)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("实时行情获取失败，显示股票列表")
            for stock in stock_pool:
                st.text(f"{stock['code']} - {stock['name']}")
    else:
        st.info("股票池为空，请添加股票")

with col2:
    st.subheader("添加股票")
    with st.form("add_stock_form", clear_on_submit=True):
        new_code = st.text_input("股票代码", placeholder="如: 600426")
        new_name = st.text_input("股票名称", placeholder="如: 华鲁恒升")
        new_category = st.text_input("所属行业", placeholder="如: 化工")
        
        submitted = st.form_submit_button("➕ 添加", use_container_width=True)
        if submitted:
            if new_code and new_name:
                if len(new_code) == 6 and new_code.isdigit():
                    success, msg = add_stock(new_code, new_name, new_category)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.error("股票代码应为6位数字")
            else:
                st.error("请填写股票代码和名称")
    
    st.divider()
    
    st.subheader("删除股票")
    if stock_pool:
        codes_to_remove = [f"{s['code']} - {s['name']}" for s in stock_pool]
        selected = st.selectbox("选择要删除的股票", codes_to_remove)
        
        if st.button("🗑️ 删除", type="secondary", use_container_width=True):
            code = selected.split(" - ")[0]
            success, msg = remove_stock(code)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    else:
        st.info("股票池为空")

# 涨跌幅排行
st.divider()
st.subheader("📊 涨跌幅排行")

if stock_pool and realtime_df is not None and not realtime_df.empty:
    col_up, col_down = st.columns(2)
    
    with col_up:
        st.markdown("**🔴 涨幅榜**")
        try:
            # 尝试获取涨跌幅字段
            if '涨跌幅' in realtime_df.columns:
                up_df = realtime_df[realtime_df["涨跌幅"] > 0].sort_values("涨跌幅", ascending=False)
            elif 'pct_change' in realtime_df.columns:
                up_df = realtime_df[realtime_df["pct_change"] > 0].sort_values("pct_change", ascending=False)
            else:
                up_df = pd.DataFrame()
            
            if not up_df.empty:
                for idx, row in up_df.head(5).iterrows():
                    code = row['代码']
                    name = row.get('名称', code)
                    change = row.get('涨跌幅', row.get('pct_change', 0))
                    st.markdown(f"**{name}** ({code}) +{float(change):.2f}%")
        except Exception as e:
            st.info("暂无涨幅数据")
    
    with col_down:
        st.markdown("**🟢 跌幅榜**")
        try:
            if '涨跌幅' in realtime_df.columns:
                down_df = realtime_df[realtime_df["涨跌幅"] < 0].sort_values("涨跌幅")
            elif 'pct_change' in realtime_df.columns:
                down_df = realtime_df[realtime_df["pct_change"] < 0].sort_values("pct_change")
            else:
                down_df = pd.DataFrame()
            
            if not down_df.empty:
                for idx, row in down_df.head(5).iterrows():
                    code = row['代码']
                    name = row.get('名称', code)
                    change = row.get('涨跌幅', row.get('pct_change', 0))
                    st.markdown(f"**{name}** ({code}) {float(change):.2f}%")
        except Exception as e:
            st.info("暂无跌幅数据")
else:
    st.info("暂无涨跌幅排行数据")
