import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(code, period="daily", start_date=None, end_date=None):
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
    if end_date is None:
        end_date = datetime.now().strftime("%Y%m%d")
    
    try:
        df = ak.stock_zh_a_hist(symbol=code, period=period, 
                                start_date=start_date, end_date=end_date, adjust="qfq")
        
        if df is not None and not df.empty:
            df.columns = ["date", "open", "close", "high", "low", "volume", 
                         "amount", "amplitude", "pct_change", "change_amount", "turnover"]
            df["date"] = pd.to_datetime(df["date"])
            return df
        return None
    except Exception as e:
        print(f"获取股票 {code} 数据失败: {e}")
        return None

def get_realtime_quote(codes):
    try:
        df = ak.stock_zh_a_spot_em()
        result = df[df["代码"].isin(codes)]
        return result
    except Exception as e:
        print(f"获取实时行情失败: {e}")
        return None

def get_stock_name(code):
    try:
        df = ak.stock_zh_a_spot_em()
        name = df[df["代码"] == code]["名称"].values
        return name[0] if len(name) > 0 else code
    except:
        return code
