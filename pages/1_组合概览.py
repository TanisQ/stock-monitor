import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool, add_stock, remove_stock, get_industries
from utils.data_fetcher import get_realtime_quote, search_stock_by_name

st.title("📈 组合概览")

# 加载股票池
try:
    stock_pool = load_stock_pool()
except:
    stock_pool = []

# 筛选和排序
st.subheader("🔧 筛选与排序")
col1, col2, col3 = st.columns(3)

with col1:
    try:
        industries = ["全部"] + get_industries()
    except:
        industries = ["全部"]
    selected_industry = st.selectbox("按行业筛选", industries)

with col2:
    sort_option = st.selectbox("排序方式", ["默认", "按名称", "按代码"])

with col3:
    st.metric("持仓数量", f"{len(stock_pool)} 只")

# 添加股票
st.divider()
st.subheader("➕ 添加股票")

col_add1, col_add2 = st.columns([2, 1])

with col_add1:
    with st.form("add_form", clear_on_submit=True):
        search_name = st.text_input("股票名称", placeholder="如: 贵州茅台、宁德时代")
        industry = st.text_input("所属行业", placeholder="如: 白酒、新能源")
        
        if st.form_submit_button("🔍 搜索并添加", use_container_width=True):
            if search_name:
                with st.spinner("搜索中..."):
                    try:
                        code, full_name, _ = search_stock_by_name(search_name)
                        if code:
                            success, msg = add_stock(code, full_name, industry)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.error(f"未找到 '{search_name}'")
                    except Exception as e:
                        st.error(f"出错: {e}")
            else:
                st.error("请输入股票名称")

with col_add2:
    with st.expander("手动添加"):
        with st.form("manual_form", clear_on_submit=True):
            manual_code = st.text_input("代码", placeholder="600519")
            manual_name = st.text_input("名称", placeholder="贵州茅台")
            manual_industry = st.text_input("行业", placeholder="白酒")
            
            if st.form_submit_button("添加"):
                if manual_code and manual_name and len(manual_code) == 6:
                    try:
                        success, msg = add_stock(manual_code, manual_name, manual_industry)
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                    except Exception as e:
                        st.error(f"添加失败: {e}")

# 显示持仓
st.divider()
st.subheader("📊 当前持仓")

if stock_pool:
    # 获取实时数据
    codes = [s["code"] for s in stock_pool]
    try:
        realtime_df = get_realtime_quote(codes)
    except:
        realtime_df = None
    
    # 准备显示数据
    display_data = []
    for stock in stock_pool:
        code = stock["code"]
        row = {
            "代码": code,
            "名称": stock["name"],
            "行业": stock.get("industry", "-")
        }
        
        # 获取价格
        if realtime_df is not None and not realtime_df.empty:
            try:
                match = realtime_df[realtime_df["代码"] == code]
                if not match.empty:
                    price = match.iloc[0].get("最新价", "-")
                    row["最新价"] = f"{float(price):.2f}" if price != "-" else "-"
                else:
                    row["最新价"] = "-"
            except:
                row["最新价"] = "-"
        else:
            row["最新价"] = "-"
        
        display_data.append(row)
    
    # 筛选
    if selected_industry != "全部":
        display_data = [d for d in display_data if d["行业"] == selected_industry]
    
    # 显示表格
    if display_data:
        import pandas as pd
        df = pd.DataFrame(display_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 行业统计
        st.subheader("📈 行业分布")
        try:
            from collections import Counter
            industry_counts = Counter([d["行业"] for d in display_data if d["行业"] != "-"])
            cols = st.columns(min(len(industry_counts), 4))
            for idx, (ind, count) in enumerate(industry_counts.items()):
                with cols[idx % 4]:
                    st.metric(ind, f"{count} 只")
        except:
            pass
    else:
        st.info("该行业下没有股票")
    
    # 删除功能
    st.divider()
    st.subheader("🗑️ 删除股票")
    try:
        options = [f"{s['code']} - {s['name']}" for s in stock_pool]
        selected = st.selectbox("选择股票", options)
        
        if st.button("删除", type="secondary"):
            code = selected.split(" - ")[0]
            try:
                success, msg = remove_stock(code)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
            except Exception as e:
                st.error(f"删除失败: {e}")
    except:
        st.error("删除功能出错")

else:
    st.info("股票池为空，请添加股票")
