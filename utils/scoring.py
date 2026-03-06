import pandas as pd
import numpy as np

def calculate_technical_score(df):
    """
    计算技术打分 (0-100分)
    基于：趋势、动量、波动率
    """
    if df is None or df.empty or len(df) < 20:
        return 50, "数据不足"
    
    score = 50  # 基础分
    reasons = []
    
    latest = df.iloc[-1]
    
    # 1. 趋势得分 (MA20方向)
    if 'MA20' in df.columns and not df['MA20'].isna().all():
        ma20_trend = df['MA20'].iloc[-1] - df['MA20'].iloc[-5]
        if ma20_trend > 0:
            score += 10
            reasons.append("MA20向上")
        else:
            score -= 10
            reasons.append("MA20向下")
    
    # 2. 动量得分 (RSI)
    if 'RSI' in df.columns and not pd.isna(latest['RSI']):
        rsi = latest['RSI']
        if 40 <= rsi <= 60:
            score += 5
            reasons.append("RSI中性健康")
        elif rsi > 70:
            score -= 5
            reasons.append("RSI超买")
        elif rsi < 30:
            score += 15
            reasons.append("RSI超卖反弹")
    
    # 3. 价格位置 (相对MA20)
    if 'MA20' in df.columns and not pd.isna(latest['MA20']):
        if latest['close'] > latest['MA20']:
            score += 10
            reasons.append("价格在MA20之上")
        else:
            score -= 10
            reasons.append("价格在MA20之下")
    
    # 限制分数范围
    score = max(0, min(100, score))
    
    return score, "，".join(reasons) if reasons else "中性"

def get_score_color(score):
    """根据分数返回颜色"""
    if score >= 80:
        return "🟢"
    elif score >= 60:
        return "🟡"
    elif score >= 40:
        return "🟠"
    else:
        return "🔴"
