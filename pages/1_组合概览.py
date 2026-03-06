import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool, add_stock, remove_stock, save_stock_pool
from utils.data_fetcher import get_realtime_quote, get_stock_name

st.title("📈 组合概览")

# 股票池管理区域
st.subheader("📊 股票池管理")

col1, col2 = st.columns([3, 1])

with col1:
    # 显示当前持仓
    stock_pool = load_stock_pool()
    
    if stock_pool:
        st.write(f"**当前持仓 ({len(stock_pool)} 只):**")
        
        # 获取实时数据
        codes = [s["code"] for s in stock_pool]
        realtime_df = get_realtime_quote(codes)
        
        display_data = []
        for stock in stock_pool:
            code = stock["code"]
            row_data = {
                "代码": code,
                "名称": stock["name"],
                "行业": stock.get("category", "-")
            }
            
            if realtime_df is not None and not realtime_df.empty:
                stock_rt = realtime_df[realtime_df["代码"] == code]
                if not stock_rt.empty:
                    rt = stock_rt.iloc[0]
                    row_data["最新价"] = f"{rt.get('最新价', '-'):.2f}" if pd.notna(rt.get('最新价')) else "-"
                    row_data["涨跌幅"] = f"{rt.get('涨跌幅', '-'):.2f}%" if pd.notna(rt.get('涨跌幅')) else "-"
                else:
                    row_data["最新价"] = "-"
                    row_data["涨跌幅"] = "-"
            else:
                row_data["最新价"] = "-"
                row_data["涨跌幅"] = "-"
            
            display_data.append(row_data)
        
        df_display = pd.DataFrame(display_data)
        
        # 显示表格
        st.dataframe(df_display, use_container_width=True, hide_index=True)
    else:
        st.info("股票池为空，请添加股票")

with col2:
    # 添加股票
    st.subheader("➕ 添加股票")
    with st.form("add_stock_form", clear_on_submit=True
        new_code = st.text_input("股票代码", placeholder="如: 600426")
        new_name = st.text_input("股票名称", placeholder="如: 华鲁恒升")
        new_category = st.text_input("所属行业", placeholder="如: 化工")
        
        submitted = st.form_submit_button("添加", use_container_width=True)
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
    
    # 删除股票
    st.subheader("🗑️ 删除股票")
    if stock_pool:
        codes_to_remove = [f"{s['code']} - {s['name']}" for s in stock_pool]
        selected = st.selectbox("选择要删除的股票", codes_to_remove)
        
        if st.button("删除", type="secondary", use_container_width=True):
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
            up_df = realtime_df[realtime_df["涨跌幅"] > 0].sort_values("涨跌幅", ascending=False)
            if not up_df.empty:
                for idx, row in up_df.head(5).iterrows():
                    st.markdown(f"**{row.get('名称', row['代码'])}** ({row['代码']}) +{row['涨跌幅']:.2f}%")
        except:
            st.info("暂无涨幅数据")
    
    with col_down:
        st.markdown("**🟢 跌幅榜**")
        try:
            down_df = realtime_df[realtime_df["涨跌幅"] < 0].sort_values("涨跌幅")
            if not down_df.empty:
                for idx, row in down_df.head(5).iterrows():
                    st.markdown(f"**{row.get('名称', row['代码'])}** ({row['代码']}) {row['涨跌幅']:.2f}%")
        except:
            st.info("暂无跌幅数据")
else:
    st.info("暂无实时行情数据")
