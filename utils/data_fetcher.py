import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# 设置 Tushare API
TUSHARE_TOKEN = "a3db774610e6a034fa51634e408db87373bf24e205abf64c7d1f37f0"
ts.set_token(TUSHARE_TOKEN)
pro = ts.pro_api()

def get_stock_data(code, period="daily", start_date=None, end_date=None):
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
    try:
        # Tushare 实时行情
        ts_codes = []
        for code in codes:
            if code.startswith("6"):
                ts_codes.append(f"{code}.SH")
            else:
                ts_codes.append(f"{code}.SZ")
        
        df = pro.daily_basic(ts_code=",".join(ts_codes), trade_date=datetime.now().strftime("%Y%m%d"))
        if df is not None and not df.empty:
            df = df.rename(columns={
                "ts_code": "代码",
                "close": "最新价",
                "pct_change": "涨跌幅",
                "change": "涨跌额",
                "vol": "成交量"
            })
            df["代码"] = df["代码"].str.replace(".SH", "").str.replace(".SZ", "")
            return df
        return None
    except Exception as e:
        print(f"获取实时行情失败: {e}")
        return None

def get_stock_name(code):
    try:
        df = pro.stock_basic(ts_code=f"{code}.SZ" if code.startswith(("0", "3")) else f"{code}.SH")
        return df["name"].values[0] if not df.empty else code
    except:
        return code

def search_stock_by_name(name):
    """根据股票名称搜索股票代码"""
    try:
        # 获取所有股票列表
        df = pro.stock_basic(exchange='', list_status='L', 
                            fields='ts_code,symbol,name,industry')
        # 模糊搜索
        result = df[df['name'].str.contains(name, na=False)]
        if not result.empty:
            row = result.iloc[0]
            code = row['symbol']
            full_name = row['name']
            industry = row['industry'] if pd.notna(row['industry']) else "其他"
            return code, full_name, industry
        return None, None, None
    except Exception as e:
        print(f"搜索股票失败: {e}")
        return None, None, None

def get_stock_market_cap(codes):
    """获取股票市值"""
    try:
        ts_codes = []
        for code in codes:
            if code.startswith("6"):
                ts_codes.append(f"{code}.SH")
            else:
                ts_codes.append(f"{code}.SZ")
        
        # 获取每日指标（包含市值）
        df = pro.daily_basic(ts_code=",".join(ts_codes), 
                            trade_date=datetime.now().strftime("%Y%m%d"),
                            fields='ts_code,total_mv,circ_mv')
        
        if df is not None and not df.empty:
            df['代码'] = df['ts_code'].str.replace('.SH', '').str.replace('.SZ', '')
            df['总市值'] = df['total_mv']  # 单位：万元
            return df[[['代码', '总市值', '流通市值']]
        return None
    except Exception as e:
        print(f"获取市值失败: {e}")
        return None
