#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter 爬虫使用示例
演示不同的配置和使用场景
"""

from twitter_scraper_selenium import TwitterScraper

# ============================================================================
# 示例 1: 基本使用（不使用用户配置）
# ============================================================================
def example_basic():
    """基本使用示例"""
    print("=" * 60)
    print("示例 1: 基本使用")
    print("=" * 60)
    
    queries = [
        {
            "query": "韩国 (总统 OR 选举 OR 国会 OR 示威 OR 对朝 OR 军演 OR 美韩同盟) -is:retweet lang:zh",
            "description": "South Korea politics/security (Chinese)"
        },
    ]
    
    scraper = TwitterScraper(edge_profile_path=None, headless=False)
    
    try:
        scraper.setup_driver()
        scraper.scrape_queries(queries)
    finally:
        scraper.close()


# ============================================================================
# 示例 2: 使用用户配置保持登录态
# ============================================================================
def example_with_profile():
    """使用 Edge 用户配置示例"""
    print("=" * 60)
    print("示例 2: 使用用户配置保持登录态")
    print("=" * 60)
    
    # 根据操作系统设置用户配置路径
    # Windows:
    # edge_profile_path = r"C:\Users\YourUsername\AppData\Local\Microsoft\Edge\User Data"
    # macOS:
    # edge_profile_path = "/Users/YourUsername/Library/Application Support/Microsoft Edge"
    # Linux:
    # edge_profile_path = "/home/YourUsername/.config/microsoft-edge"
    
    edge_profile_path = None  # 请替换为实际路径
    
    queries = [
        {
            "query": "日本 (首相 OR 选举 OR 政治) -is:retweet lang:zh",
            "description": "Japan politics (Chinese)"
        },
    ]
    
    scraper = TwitterScraper(edge_profile_path=edge_profile_path, headless=False)
    
    try:
        scraper.setup_driver()
        scraper.scrape_queries(queries)
    finally:
        scraper.close()


# ============================================================================
# 示例 3: 批量爬取多个查询
# ============================================================================
def example_multiple_queries():
    """批量爬取多个查询示例"""
    print("=" * 60)
    print("示例 3: 批量爬取多个查询")
    print("=" * 60)
    
    queries = [
        {
            "query": "韩国 (总统 OR 选举 OR 国会 OR 示威 OR 对朝 OR 军演 OR 美韩同盟) -is:retweet lang:zh",
            "description": "South Korea politics/security (Chinese)"
        },
        {
            "query": "日本 (首相 OR 选举 OR 政治) -is:retweet lang:zh",
            "description": "Japan politics (Chinese)"
        },
        {
            "query": "美国 (总统 OR 选举 OR 国会) -is:retweet lang:zh",
            "description": "USA politics (Chinese)"
        },
    ]
    
    scraper = TwitterScraper(edge_profile_path=None, headless=False)
    
    try:
        scraper.setup_driver()
        scraper.scrape_queries(queries)
    finally:
        scraper.close()


# ============================================================================
# 示例 4: 自定义参数爬取单个查询
# ============================================================================
def example_custom_params():
    """自定义参数示例"""
    print("=" * 60)
    print("示例 4: 自定义参数爬取")
    print("=" * 60)
    
    scraper = TwitterScraper(edge_profile_path=None, headless=False)
    
    try:
        scraper.setup_driver()
        
        # 自定义最大推文数
        query = "人工智能 (AI OR ChatGPT OR 机器学习) -is:retweet lang:zh"
        description = "AI and Machine Learning (Chinese)"
        
        scraper.scrape_query(query, description, max_tweets=500)
        
    finally:
        scraper.close()


# ============================================================================
# 示例 5: 无头模式运行（后台运行）
# ============================================================================
def example_headless():
    """无头模式示例"""
    print("=" * 60)
    print("示例 5: 无头模式运行")
    print("=" * 60)
    
    queries = [
        {
            "query": "区块链 (比特币 OR 以太坊 OR NFT) -is:retweet lang:zh",
            "description": "Blockchain (Chinese)"
        },
    ]
    
    # 使用无头模式（浏览器在后台运行，不显示窗口）
    scraper = TwitterScraper(edge_profile_path=None, headless=True)
    
    try:
        scraper.setup_driver()
        scraper.scrape_queries(queries)
    finally:
        scraper.close()


if __name__ == "__main__":
    # 选择要运行的示例
    print("\n请选择要运行的示例:")
    print("1. 基本使用")
    print("2. 使用用户配置保持登录态")
    print("3. 批量爬取多个查询")
    print("4. 自定义参数爬取")
    print("5. 无头模式运行")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    if choice == "1":
        example_basic()
    elif choice == "2":
        example_with_profile()
    elif choice == "3":
        example_multiple_queries()
    elif choice == "4":
        example_custom_params()
    elif choice == "5":
        example_headless()
    else:
        print("无效选项，运行默认示例（示例1）")
        example_basic()
