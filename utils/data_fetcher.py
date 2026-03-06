import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# Tushare API
TUSHARE_TOKEN = "a3db774610e6a034fa51634e408db87373bf24e205abf64c7d1f37f0"
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

def get_stock_data(code, period="daily", start_date=None, end_date=None):
    """获取股票历史数据"""
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    
    try:
        # 转换代码格式
        if code.startswith("6"):
            ts_code = f"{code}.SH"
        else:
            ts_code = f"{code}.SZ"
        
        df = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df is not None and not df.empty:
            df = df.sort_values("trade_date")
            df.columns = ["ts_code", "date", "open", "high", "low", "close", "pre_close", 
                         "change", "pct_change", "volume", "amount"]
            df["date"] = pd.to_datetime(df["date"])
            return df
        return None
    except Exception as e:
        print(f"获取股票 {code} 数据失败: {e}")
        return None

def get_realtime_quote(codes):
    """获取实时行情"""
    try:
        ts_codes = []
        for code in codes:
            if code.startswith("6"):
                ts_codes.append(f"{code}.SH")
            else:
                ts_codes.append(f"{code}.SZ")
        
        # 获取日线数据作为实时价格
        df = pro.daily(ts_code=",".join(ts_codes), 
                      trade_date=datetime.now().strftime("%Y%m%d"))
        
        if df is not None and not df.empty:
            df = df.rename(columns={
                "ts_code": "代码",
                "close": "最新价",
                "pct_change": "涨跌幅"
            })
            df["代码"] = df["代码"].str.replace(".SH", "").str.replace(".SZ", "")
            return df
        return None
    except Exception as e:
        print(f"获取实时行情失败: {e}")
        return None

def search_stock_by_name(name):
    """根据名称搜索股票"""
    try:
        df = pro.stock_basic(exchange='', list_status='L')
        result = df[df['name'].str.contains(name, na=False)]
        if not result.empty:
            row = result.iloc[0]
            code = row['symbol']
            full_name = row['name']
            return code, full_name, None
        return None, None, None
    except Exception as e:
        print(f"搜索失败: {e}")
        return None, None, None
