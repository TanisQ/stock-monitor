import json
import os
import requests

# 从 GitHub 读取股票池
GITHUB_RAW_URL = "https://raw.githubusercontent.com/TanisQ/stock-monitor/main/data/stock_pool.json"
LOCAL_POOL_FILE = "/tmp/stock_pool.json"

def load_stock_pool():
    """加载股票池"""
    try:
        # 优先从 GitHub 获取
        response = requests.get(GITHUB_RAW_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data and isinstance(data, list):
                # 保存到本地临时文件
                with open(LOCAL_POOL_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                return data
    except Exception as e:
        print(f"从GitHub加载失败: {e}")
    
    # 使用本地文件
    try:
        if os.path.exists(LOCAL_POOL_FILE):
            with open(LOCAL_POOL_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data and isinstance(data, list):
                    return data
    except:
        pass
    
    # 默认股票池
    return [
        {"code": "600426", "name": "华鲁恒升", "industry": "化工"},
        {"code": "600276", "name": "恒瑞医药", "industry": "医药"},
        {"code": "000963", "name": "华东医药", "industry": "医药"},
        {"code": "002262", "name": "恩华药业", "industry": "医药"}
    ]

def save_stock_pool(stock_pool):
    """保存股票池到本地"""
    try:
        with open(LOCAL_POOL_FILE, "w", encoding="utf-8") as f:
            json.dump(stock_pool, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False

def add_stock(code, name, industry=""):
    """添加股票"""
    stock_pool = load_stock_pool()
    for stock in stock_pool:
        if stock["code"] == code:
            return False, f"股票 {code} 已存在"
    
    stock_pool.append({
        "code": code,
        "name": name,
        "industry": industry
    })
    save_stock_pool(stock_pool)
    return True, f"股票 {code} {name} 添加成功"

def remove_stock(code):
    """删除股票"""
    stock_pool = load_stock_pool()
    original_len = len(stock_pool)
    stock_pool = [s for s in stock_pool if s["code"] != code]
    
    if len(stock_pool) < original_len:
        save_stock_pool(stock_pool)
        return True, f"股票 {code} 删除成功"
    return False, f"股票 {code} 不存在"

def get_industries():
    """获取所有行业分类"""
    try:
        stock_pool = load_stock_pool()
        if not stock_pool:
            return []
        industries = list(set([s.get("industry", "未分类") for s in stock_pool if s.get("industry")]))
        return sorted(industries)
    except:
        return []
