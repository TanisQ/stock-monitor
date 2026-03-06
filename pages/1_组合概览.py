import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool, add_stock, remove_stock
from utils.data_fetcher import get_realtime_quote, get_stock_market_cap, search_stock_by_name
from utils.technical import calculate_all_indicators
from utils.scoring import calculate_technical_score, get_score_color
from utils.data_fetcher import get_stock_data

st.title("📈 组合概览")

# ========== 添加股票区域 ==========
st.subheader("➕ 添加股票")

col1, col2 = st.columns([3, 1])

with col1:
    # 方式1：按名称搜索（推荐）
    with st.form("search_stock_form", clear_on_submit=True):
        search_name = st.text_input("输入股票名称或简称", placeholder="如: 茅台、宁德、平安")
        tags_input = st.text_input("行业标签（用逗号分隔）", placeholder="如: 白酒,价值投资,龙头")
        
        if st.form_submit_button("🔍 搜索并添加", use_container_width=True):
            if search_name:
                with st.spinner("搜索中..."):
                    code, full_name, industry = search_stock_by_name(search_name)
                    if code:
                        # 合并标签：行业 + 用户输入
                        all_tags = industry
                        if tags_input:
                            all_tags = f"{industry},{tags_input}" if industry else tags_input
                        
                        success, msg = add_stock(code, full_name, all_tags)
                        if success:
                            st.success(f"✅ 添加成功: {full_name} ({code})")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error(f"未找到 '{search_name}'，请检查名称")
            else:
                st.error("请输入股票名称")

with col2:
    # 方式2：手动输入代码（备用）
    with st.expander("手动输入代码"):
        with st.form("manual_add_form", clear_on_submit=True):
            manual_code = st.text_input("股票代码", placeholder="600519")
            manual_name = st.text_input("股票名称", placeholder="贵州茅台")
            manual_tags = st.text_input("标签", placeholder="白酒,龙头")
            
            if st.form_submit_button("添加"):
                if manual_code and manual_name and len(manual_code) == 6:
                    success, msg = add_stock(manual_code, manual_name, manual_tags)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

# ========== 当前持仓区域 ==========
st.divider()
st.subheader("📊 当前持仓")

stock_pool = load_stock_pool()

if stock_pool:
    # 获取数据
    codes = [s["code"] for s in stock_pool]
    
    with st.spinner("加载数据中..."):
        realtime_df = get_realtime_quote(codes)
        market_cap_df = get_stock_market_cap(codes)
    
    # 构建显示数据
    display_data = []
    
    for stock in stock_pool:
        code = stock["code"]
        row_data = {
            "代码": code,
            "名称": stock["name"],
            "标签": stock.get("tags", "-")
        }
        
        # 获取实时价格
        if realtime_df is not None and not realtime_df.empty:
            stock_rt = realtime_df[realtime_df["代码"] == code]
            if not stock_rt.empty:
                rt = stock_rt.iloc[0]
                try:
                    price = float(rt.get('最新价', rt.get('close', 0)))
                    row_data["最新价"] = f"{price:.2f}"
                except:
                    row_data["最新价"] = "-"
            else:
                row_data["最新价"] = "-"
        else:
            row_data["最新价"] = "-"
        
        # 获取市值
        if market_cap_df is not None and not market_cap_df.empty:
            cap_row = market_cap_df[market_cap_df["代码"] == code]
            if not cap_row.empty:
                try:
                    mv = float(cap_row.iloc[0].get('总市值', 0))
                    # 转换为亿
                    row_data["市值(亿)"] = f"{mv/10000:.1f}"
                except:
                    row_data["市值(亿)"] = "-"
            else:
                row_data["市值(亿)"] = "-"
        else:
            row_data["市值(亿)"] = "-"
        
        # 计算技术打分
        try:
            df = get_stock_data(code, lookback=60)
            if df is not None and not df.empty:
                df = calculate_all_indicators(df)
                score, reason = calculate_technical_score(df)
                row_data["技术分"] = f"{get_score_color(score)} {score}"
                row_data["评分说明"] = reason
            else:
                row_data["技术分"] = "-"
                row_data["评分说明"] = "无数据"
        except:
            row_data["技术分"] = "-"
            row_data["评分说明"] = "计算失败"
        
        display_data.append(row_data)
    
    # 显示表格
    df_display = pd.DataFrame(display_data)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    # 删除功能
    st.subheader("🗑️ 删除股票")
    col_del, _ = st.columns([1, 3])
    with col_del:
        codes_to_remove = [f"{s['code']} - {s['name']}" for s in stock_pool]
        selected = st.selectbox("选择要删除的股票", codes_to_remove, key="delete_select")
        
        if st.button("删除选中股票", type="secondary"):
            code = selected.split(" - ")[0]
            success, msg = remove_stock(code)
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

else:
    st.info("股票池为空，请添加股票")

# ========== 统计信息 ==========
st.divider()
if stock_pool:
    total_stocks = len(stock_pool)
    st.metric("持仓数量", f"{total_stocks} 只")
