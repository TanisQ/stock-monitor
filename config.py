import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STOCK_POOL_FILE = os.path.join(DATA_DIR, "stock_pool.json")

os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_STOCK_POOL = [
    {"code": "600426", "name": "华鲁恒升", "industry": "化工"},
    {"code": "000001", "name": "平安银行", "industry": "银行"},
    {"code": "300750", "name": "宁德时代", "industry": "新能源"},
]

def load_stock_pool():
    """加载股票池"""
    if os.path.exists(STOCK_POOL_FILE):
        with open(STOCK_POOL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_STOCK_POOL.copy()

def save_stock_pool(stock_pool):
    """保存股票池"""
    with open(STOCK_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(stock_pool, f, ensure_ascii=False, indent=2)

def add_stock(code, name, industry=""):
    """添加股票"""
    stock_pool = load_stock_pool()
    for stock in stock_pool:
        if stock["code"] == code:
            return False, f"股票 {code} 已存在"
    
    stock_pool.append({
        "code": code,
        "name": name,
        "industry": industry  # 用户自己定义的行业
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
    """获取所有行业分类（用于筛选）"""
    stock_pool = load_stock_pool()
    industries = list(set([s.get("industry", "未分类") for s in stock_pool if s.get("industry")]))
    return sorted(industries)
