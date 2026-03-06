import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool, add_stock, remove_stock, get_industries
from utils.data_fetcher import get_realtime_quote, get_stock_market_cap, search_stock_by_name
from utils.technical import calculate_all_indicators
from utils.scoring import calculate_technical_score, get_score_color
from utils.data_fetcher import get_stock_data

st.title("📈 组合概览")

# ========== 筛选和排序工具栏 ==========
st.subheader("🔧 筛选与排序")

col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    # 行业筛选
    all_industries = ["全部"] + get_industries()
    selected_industry = st.selectbox("按行业筛选", all_industries)

with col_filter2:
    # 排序方式
    sort_by = st.selectbox("排序方式", [
        "默认", 
        "市值从大到小", 
        "市值从小到大",
        "技术分从高到低",
        "技术分从低到高"
    ])

with col_filter3:
    # 显示统计
    stock_pool = load_stock_pool()
    st.metric("持仓数量", f"{len(stock_pool)} 只")

# ========== 添加股票区域 ==========
st.divider()
st.subheader("➕ 添加股票")

col_add1, col_add2 = st.columns([2, 1])

with col_add1:
    # 按名称搜索
    with st.form("search_stock_form", clear_on_submit=True):
        search_name = st.text_input("输入股票名称或简称", placeholder="如: 茅台、宁德、平安")
        
        # 行业由用户自己定义输入
        industry_input = st.text_input("所属行业（自定义）", placeholder="如: 白酒、新能源、金融")
        
        if st.form_submit_button("🔍 搜索并添加", use_container_width=True):
            if search_name:
                with st.spinner("搜索中..."):
                    code, full_name, _ = search_stock_by_name(search_name)
                    if code:
                        success, msg = add_stock(code, full_name, industry_input)
                        if success:
                            st.success(f"✅ 添加成功: {full_name} ({code}) - 行业: {industry_input}")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error(f"未找到 '{search_name}'，请检查名称")
            else:
                st.error("请输入股票名称")

with col_add2:
    # 手动输入（备用）
    with st.expander("手动输入代码"):
        with st.form("manual_add_form", clear_on_submit=True):
            manual_code = st.text_input("股票代码", placeholder="600519")
            manual_name = st.text_input("股票名称", placeholder="贵州茅台")
            manual_industry = st.text_input("所属行业", placeholder="白酒")
            
            if st.form_submit_button("添加"):
                if manual_code and manual_name and len(manual_code) == 6:
                    success, msg = add_stock(manual_code, manual_name, manual_industry)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

# ========== 当前持仓表格 ==========
st.divider()
st.subheader("📊 当前持仓")

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
            "行业": stock.get("industry", "未分类")  # 显示用户定义的行业
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
        
        # 获取市值（数值，用于排序）
        market_cap_value = 0
        if market_cap_df is not None and not market_cap_df.empty:
            cap_row = market_cap_df[market_cap_df["代码"] == code]
            if not cap_row.empty:
                try:
                    mv = float(cap_row.iloc[0].get('总市值', 0))
                    market_cap_value = mv
                    # 转换为亿显示
                    row_data["市值(亿)"] = f"{mv/10000:.1f}"
                except:
                    row_data["市值(亿)"] = "-"
            else:
                row_data["市值(亿)"] = "-"
        else:
            row_data["市值(亿)"] = "-"
        
        # 保存市值数值用于排序
        row_data["_市值数值"] = market_cap_value
        
        # 计算技术打分
        score_value = 50  # 默认分
        try:
            df = get_stock_data(code, lookback=60)
            if df is not None and not df.empty:
                df = calculate_all_indicators(df)
                score, reason = calculate_technical_score(df)
                score_value = score
                row_data["技术分"] = f"{get_score_color(score)} {score}"
                row_data["_分数数值"] = score
            else:
                row_data["技术分"] = "-"
                row_data["_分数数值"] = 0
        except:
            row_data["技术分"] = "-"
            row_data["_分数数值"] = 0
        
        display_data.append(row_data)
    
    # 转换为DataFrame
    df_display = pd.DataFrame(display_data)
    
    # === 行业筛选 ===
    if selected_industry != "全部":
        df_display = df_display[df_display["行业"] == selected_industry]
    
    # === 排序 ===
    if sort_by == "市值从大到小":
        df_display = df_display.sort_values("_市值数值", ascending=False)
    elif sort_by == "市值从小到大":
        df_display = df_display.sort_values("_市值数值", ascending=True)
    elif sort_by == "技术分从高到低":
        df_display = df_display.sort_values("_分数数值", ascending=False)
    elif sort_by == "技术分从低到高":
        df_display = df_display.sort_values("_分数数值", ascending=True)
    
    # 删除用于排序的临时列
    df_display = df_display.drop(columns=["_市值数值", "_分数数值"], errors="ignore")
    
    # 显示表格
    if not df_display.empty:
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # 显示行业分布统计
        st.divider()
        st.subheader("📈 行业分布")
        
        industry_counts = df_display["行业"].value_counts()
        col_stats = st.columns(min(len(industry_counts), 4))
        
        for idx, (industry, count) in enumerate(industry_counts.items()):
            with col_stats[idx % 4]:
                st.metric(industry, f"{count} 只")
    else:
        st.info("该行业下没有股票")
    
    # 删除功能
    st.divider()
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
