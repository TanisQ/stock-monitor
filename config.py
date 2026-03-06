import json
import os
import requests
import base64

# GitHub 配置
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "TanisQ/stock-monitor"
GITHUB_FILE_PATH = "data/stock_pool.json"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

# 本地缓存
_local_cache = None
_file_sha = None

def _get_file_sha():
    """获取 GitHub 文件的 SHA"""
    global _file_sha
    if _file_sha:
        return _file_sha
    
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            _file_sha = response.json().get("sha")
            return _file_sha
    except:
        pass
    return None

def load_stock_pool():
    """从 GitHub 加载股票池"""
    global _local_cache
    
    if _local_cache is not None:
        return _local_cache
    
    try:
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(GITHUB_API_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.json().get("content", "")
            decoded = base64.b64decode(content).decode('utf-8')
            data = json.loads(decoded)
            if data and isinstance(data, list):
                _local_cache = data
                return data
    except Exception as e:
        print(f"加载失败: {e}")
    
    # 默认股票池
    default = [
        {"code": "600426", "name": "华鲁恒升", "industry": "化工"},
        {"code": "600276", "name": "恒瑞医药", "industry": "医药"},
        {"code": "000963", "name": "华东医药", "industry": "医药"},
        {"code": "002262", "name": "恩华药业", "industry": "医药"}
    ]
    _local_cache = default
    return default

def save_stock_pool_to_github(stock_pool):
    """保存到 GitHub"""
    global _local_cache, _file_sha
    
    try:
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Content-Type": "application/json"
        }
        
        sha = _get_file_sha()
        
        content = json.dumps(stock_pool, ensure_ascii=False, indent=2)
        encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            "message": "Update stock pool via app",
            "content": encoded,
            "sha": sha
        }
        
        response = requests.put(GITHUB_API_URL, headers=headers, json=data, timeout=10)
        
        if response.status_code in [200, 201]:
            _local_cache = stock_pool
            _file_sha = response.json().get("content", {}).get("sha")
            return True
        else:
            print(f"GitHub API 错误: {response.status_code}")
            return False
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
    
    if save_stock_pool_to_github(stock_pool):
        return True, f"添加成功: {name} ({code})"
    else:
        stock_pool.pop()
        return False, "添加失败，请重试"

def remove_stock(code):
    """删除股票"""
    stock_pool = load_stock_pool()
    original_len = len(stock_pool)
    
    removed = None
    for i, stock in enumerate(stock_pool):
        if stock["code"] == code:
            removed = stock_pool.pop(i)
            break
    
    if len(stock_pool) < original_len:
        if save_stock_pool_to_github(stock_pool):
            return True, f"删除成功: {removed.get('name', '')} ({code})"
        else:
            stock_pool.append(removed)
            return False, "删除失败，请重试"
    
    return False, f"股票 {code} 不存在"

def get_industries():
    """获取行业列表"""
    try:
        stock_pool = load_stock_pool()
        if not stock_pool:
            return []
        industries = list(set([s.get("industry", "未分类") for s in stock_pool if s.get("industry")]))
        return sorted(industries)
    except:
        return []
