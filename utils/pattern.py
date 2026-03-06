import pandas as pd
import numpy as np

def detect_cup_and_handle(df, lookback=60):
    """
    检测杯柄形态
    
    返回: (is_pattern, confidence, description)
    """
    if len(df) < lookback:
        return False, 0, "数据不足"
    
    recent_data = df.tail(lookback).copy()
    highs = recent_data["high"].values
    lows = recent_data["low"].values
    closes = recent_data["close"].values
    
    # 找最高点（杯口左侧）
    max_idx = np.argmax(highs[:len(highs)//2])
    cup_left_high = highs[max_idx]
    
    # 找最低点（杯底）
    min_idx = np.argmin(lows[max_idx:max_idx+len(lows)//3]) + max_idx
    cup_bottom = lows[min_idx]
    
    # 杯深应在12-35%之间
    cup_depth = (cup_left_high - cup_bottom) / cup_left_high
    if cup_depth < 0.12 or cup_depth > 0.40:
        return False, 0, f"杯深 {cup_depth:.1%} 不符合要求(12-40%)"
    
    # 找手柄低点
    if min_idx + 5 >= len(lows):
        return False, 0, "手柄部分数据不足"
    
    handle_lows = lows[min_idx:min_idx+10]
    handle_low = np.min(handle_lows)
    
    # 手柄应在杯上半部
    if handle_low < cup_bottom + (cup_left_high - cup_bottom) * 0.4:
        return False, 0, "手柄位置过低"
    
    # 检查是否突破
    current_price = closes[-1]
    breakout_level = cup_left_high * 0.98
    
    if current_price > breakout_level:
        confidence = min(100, int((cup_depth / 0.30) * 50 + 50))
        return True, confidence, f"杯柄形态确认，突破杯口! 杯深{cup_depth:.1%}"
    elif current_price > handle_low * 1.03:
        confidence = min(80, int((cup_depth / 0.30) * 40 + 30))
        return True, confidence, f"杯柄形态形成中，等待突破 杯深{cup_depth:.1%}"
    
    return False, 0, "未形成有效杯柄形态"

def detect_rsi_signals(df, overbought=70, oversold=30):
    if "RSI" not in df.columns or df["RSI"].isna().all():
        return {"signal": "none", "value": None, "description": "RSI数据不足"}
    
    current_rsi = df["RSI"].iloc[-1]
    prev_rsi = df["RSI"].iloc[-2] if len(df) > 1 else current_rsi
    
    if prev_rsi < oversold and current_rsi >= oversold:
        return {"signal": "oversold_bounce", "value": current_rsi, "description": f"RSI超卖反弹 ({current_rsi:.1f}上穿{oversold})"}
    
    if prev_rsi > overbought and current_rsi <= overbought:
        return {"signal": "overbought_pullback", "value": current_rsi, "description": f"RSI超买回调 ({current_rsi:.1f}下穿{overbought})"}
    
    if current_rsi < oversold:
        return {"signal": "oversold", "value": current_rsi, "description": f"RSI超卖区 ({current_rsi:.1f} < {oversold})"}
    
    if current_rsi > overbought:
        return {"signal": "overbought", "value": current_rsi, "description": f"RSI超买区 ({current_rsi:.1f} > {overbought})"}
    
    return {"signal": "neutral", "value": current_rsi, "description": f"RSI中性区 ({current_rsi:.1f})"}

def analyze_all_patterns(df):
    return {
        "cup_handle": detect_cup_and_handle(df),
        "rsi": detect_rsi_signals(df)
    }
