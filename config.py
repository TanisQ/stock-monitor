import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
STOCK_POOL_FILE = os.path.join(DATA_DIR, "stock_pool.json")

os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_STOCK_POOL = [
    {"code": "600426", "name": "华鲁恒升", "category": "化工"},
    {"code": "000001", "name": "平安银行", "category": "银行"},
    {"code": "300750", "name": "宁德时代", "category": "新能源"},
]

def load_stock_pool():
    if os.path.exists(STOCK_POOL_FILE):
        with open(STOCK_POOL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_STOCK_POOL.copy()

def save_stock_pool(stock_pool):
    with open(STOCK_POOL_FILE, "w", encoding="utf-8") as f:
        json.dump(stock_pool, f, ensure_ascii=False, indent=2)

def add_stock(code, name, category=""):
    stock_pool = load_stock_pool()
    for stock in stock_pool:
        if stock["code"] == code:
            return False, f"股票 {code} 已存在"
    stock_pool.append({"code": code, "name": name, "category": category})
    save_stock_pool(stock_pool)
    return True, f"股票 {code} {name} 添加成功"

def remove_stock(code):
    stock_pool = load_stock_pool()
    original_len = len(stock_pool)
    stock_pool = [s for s in stock_pool if s["code"] != code]
    if len(stock_pool) < original_len:
        save_stock_pool(stock_pool)
        return True, f"股票 {code} 删除成功"
    return False, f"股票 {code} 不存在"
