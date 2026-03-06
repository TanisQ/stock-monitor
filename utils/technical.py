import pandas as pd
import numpy as np

def calculate_ma(df, periods=[5, 10, 20, 60]):
    for period in periods:
        df[f"MA{period}"] = df["close"].rolling(window=period).mean()
    return df

def calculate_rsi(df, period=14):
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

def calculate_macd(df, fast=12, slow=26, signal=9):
    ema_fast = df["close"].ewm(span=fast).mean()
    ema_slow = df["close"].ewm(span=slow).mean()
    df["MACD"] = ema_fast - ema_slow
    df["MACD_Signal"] = df["MACD"].ewm(span=signal).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    return df

def calculate_bollinger(df, period=20, std_dev=2):
    df["BOLL_MID"] = df["close"].rolling(window=period).mean()
    df["BOLL_STD"] = df["close"].rolling(window=period).std()
    df["BOLL_UP"] = df["BOLL_MID"] + (df["BOLL_STD"] * std_dev)
    df["BOLL_DOWN"] = df["BOLL_MID"] - (df["BOLL_STD"] * std_dev)
    return df

def calculate_all_indicators(df):
    df = calculate_ma(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_bollinger(df)
    return df
