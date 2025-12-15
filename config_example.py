# Twitter 爬虫配置示例
# 复制此文件为 config.py 并修改为实际配置

# Edge 浏览器用户配置路径
# Windows 示例: r"C:\Users\YourUsername\AppData\Local\Microsoft\Edge\User Data"
# macOS 示例: "/Users/YourUsername/Library/Application Support/Microsoft Edge"
# Linux 示例: "/home/YourUsername/.config/microsoft-edge"
# 如果不需要保持登录态，设置为 None
EDGE_PROFILE_PATH = None

# 是否使用无头模式（后台运行，不显示浏览器窗口）
HEADLESS = False

# 每个查询的最大爬取推文数
MAX_TWEETS_PER_QUERY = 2000

# 滚动加载参数
SCROLL_PAUSE_TIME = 2.0  # 每次滚动后的等待时间（秒）
MAX_SCROLLS = 50  # 最大滚动次数

# 查询列表
QUERIES = [
    {
        "query": "韩国 (总统 OR 选举 OR 国会 OR 示威 OR 对朝 OR 军演 OR 美韩同盟) -is:retweet lang:zh",
        "description": "South Korea politics/security (Chinese)"
    },
    # 添加更多查询...
    # {
    #     "query": "日本 (首相 OR 选举 OR 政治) -is:retweet lang:zh",
    #     "description": "Japan politics (Chinese)"
    # },
]

# 输出目录
OUTPUT_DIR = "twitter_data"

# 日志配置
LOG_FILE = "twitter_scraper.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
