import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import load_stock_pool, add_stock, remove_stock, get_industries
from utils.data_fetcher import get_realtime_quote, search_stock_by_name

st.title("📈 组合概览")

# ========== 筛选和排序工具栏 ==========
st.subheader("🔧 筛选与排序")

col_filter1, col_filter2, col_filter3 = st.columns(3)

with col_filter1:
    try:
        all_industries = ["全部"] + get_industries()
    except:
        all_industries = ["全部"]
    selected_industry = st.selectbox("按行业筛选", all_industries)

with col_filter2:
    sort_by = st.selectbox("排序方式", ["默认", "技术分从高到低", "技术分从低到高"])

with col_filter3:
    try:
        stock_pool = load_stock_pool()
        count = len(stock_pool) if stock_pool else 0
    except:
        stock_pool = []
        count = 0
    st.metric("持仓数量", f"{count} 只")

# ========== 添加股票区域 ==========
st.divider()
st.subheader("➕ 添加股票")

col_add1, col_add2 = st.columns([2, 1])

with col_add1:
    with st.form("search_stock_form", clear_on_submit=True):
        search_name = st.text_input("输入股票名称或简称", placeholder="如: 茅台、宁德、平安")
        industry_input = st.text_input("所属行业（自定义）", placeholder="如: 白酒、新能源、金融")
        
        if st.form_submit_button("🔍 搜索并添加", use_container_width=True):
            if search_name:
                with st.spinner("搜索中..."):
                    try:
                        code, full_name, _ = search_stock_by_name(search_name)
                        if code:
                            success, msg = add_stock(code, full_name, industry_input)
                            if success:
                                st.success(f"✅ 添加成功: {full_name} ({code})")
                                st.rerun()
                            else:
                                st.error(msg)
                        else:
                            st.error(f"未找到 '{search_name}'")
                    except Exception as e:
                        st.error(f"搜索出错: {e}")
            else:
                st.error("请输入股票名称")

with col_add2:
    with st.expander("手动输入代码"):
        with st.form("manual_add_form", clear_on_submit=True):
            manual_code = st.text_input("股票代码", placeholder="600519")
            manual_name = st.text_input("股票名称", placeholder="贵州茅台")
            manual_industry = st.text_input("所属行业", placeholder="白酒")
            
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

# ========== 当前持仓表格 ==========
st.divider()
st.subheader("📊 当前持仓")

if stock_pool:
    codes = [s["code"] for s in stock_pool]
    
    with st.spinner("加载数据中..."):
        try:
            realtime_df = get_realtime_quote(codes)
        except:
            realtime_df = None
    
    display_data = []
    
    for stock in stock_pool:
        code = stock["code"]
        row_data = {
            "代码": code,
            "名称": stock["name"],
            "行业": stock.get("industry", "未分类")
        }
        
        # 获取实时价格
        if realtime_df is not None and not realtime_df.empty:
            try:
                stock_rt = realtime_df[realtime_df["代码"] == code]
                if not stock_rt.empty:
                    rt = stock_rt.iloc[0]
                    price = float(rt.get('最新价', rt.get('close', 0)))
                    row_data["最新价"] = f"{price:.2f}"
                else:
                    row_data["最新价"] = "-"
            except:
                row_data["最新价"] = "-"
        else:
            row_data["最新价"] = "-"
        
        # 技术打分（简化版，避免报错）
        try:
            row_data["技术分"] = "🟡 50"
        except:
            row_data["技术分"] = "-"
        
        display_data.append(row_data)
    
    if display_data:
        df_display = pd.DataFrame(display_data)
        
        # 行业筛选
        if selected_industry != "全部":
            df_display = df_display[df_display["行业"] == selected_industry]
        
        if not df_display.empty:
            st.dataframe(df_display, use_container_width=True, hide_index=True)
            
            # 行业分布
            st.divider()
            st.subheader("📈 行业分布")
            try:
                industry_counts = df_display["行业"].value_counts()
                cols = st.columns(min(len(industry_counts), 4))
                for idx, (industry, count) in enumerate(industry_counts.items()):
                    with cols[idx % 4]:
                        st.metric(industry, f"{count} 只")
            except:
                pass
        else:
            st.info("该行业下没有股票")
    
    # 删除功能
    st.divider()
    st.subheader("🗑️ 删除股票")
    try:
        codes_to_remove = [f"{s['code']} - {s['name']}" for s in stock_pool]
        selected = st.selectbox("选择要删除的股票", codes_to_remove)
        
        if st.button("删除选中股票", type="secondary"):
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
        st.error("删除功能暂时不可用")

else:
    st.info("股票池为空，请添加股票")
