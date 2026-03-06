import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="股票K线挖掘监测系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 股票K线挖掘监测系统")

st.markdown("""
## 欢迎使用

本系统提供以下功能：

### 📈 组合概览
- 股票池管理（添加/删除股票）
- 实时行情监控
- 涨跌幅排行

### 📉 个股分析
- K线图展示
- 技术指标（MA、RSI、MACD、布林带）
- 历史数据回溯

### 🔍 机会挖掘
- **杯柄形态**识别
- **RSI超买超卖**信号
- **量价关系**分析
- 形态筛选器
""")

from config import load_stock_pool

st.sidebar.header("📋 当前股票池")
stock_pool = load_stock_pool()

if stock_pool:
    for stock in stock_pool:
        st.sidebar.text(f"{stock['code']} - {stock['name']}")
else:
    st.sidebar.info("股票池为空")

st.sidebar.markdown(f"**共 {len(stock_pool)} 只股票**")
