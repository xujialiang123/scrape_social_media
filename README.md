# scrape_social_media
数据科学实验一作业

## 项目简介 / Project Overview

本项目用于爬取Twitter（现X平台）上关于国内外局势的数据，重点关注2025年的热点话题。项目提供了两种不同的实现方式：
- 使用 **tweepy** 库（需要Twitter API凭证）
- 使用 **snscrape** 库（无需API凭证）

This project scrapes Twitter (now X platform) data about domestic and international situations, focusing on trending topics from 2025. Two implementations are provided:
- Using **tweepy** library (requires Twitter API credentials)
- Using **snscrape** library (no API credentials needed)

## 功能特点 / Features

- ✅ 爬取关于中国、美国、日本等国家的国内局势数据
- ✅ 爬取国际关系和地缘政治相关数据
- ✅ 专注于2025年的数据
- ✅ 按互动量（点赞、转发、回复）排序，优先展示热点话题
- ✅ 支持多语言（中文、英文、日文）
- ✅ 数据导出为CSV和JSON格式
- ✅ 两种实现方式可选

## 安装依赖 / Installation

```bash
pip install -r requirements.txt
```

### 依赖包 / Dependencies

- `tweepy>=4.14.0` - Twitter API官方Python库
- `snscrape>=0.7.0` - 无需API的Twitter爬虫库
- `pandas>=2.0.0` - 数据处理和分析

## 使用方法 / Usage

### 方法1：使用 tweepy (推荐用于小规模、实时数据)

**优点**：
- 官方支持，更稳定
- 支持实时数据
- 提供丰富的用户信息

**缺点**：
- 需要申请Twitter开发者账号和API凭证
- 有速率限制
- 免费版本功能受限
- **重要**：`search_recent_tweets` API仅能搜索过去7天的数据
  - 如需2025年历史数据，需要Academic Research访问权限（Full Archive Search）
  - 或者在2025年实际运行此脚本

#### 1.1 获取Twitter API凭证

1. 访问 [Twitter Developer Portal](https://developer.twitter.com/)
2. 创建开发者账号
3. 创建一个新的App
4. 获取 Bearer Token

#### 1.2 设置环境变量

```bash
export TWITTER_BEARER_TOKEN='your_bearer_token_here'
```

或在代码中直接传入：

```python
scraper = TwitterScraperTweepy(bearer_token='your_token')
```

#### 1.3 运行爬虫

```bash
python twitter_scraper_tweepy.py
```

### 方法2：使用 snscrape (推荐用于大规模数据)

**优点**：
- 无需API凭证
- 无速率限制
- 可以爬取历史数据
- 更简单快速

**缺点**：
- 非官方工具，可能不稳定
- 依赖于Twitter网页结构（可能随时失效）

#### 2.1 直接运行

```bash
python twitter_scraper_snscrape.py
```

## 搜索主题 / Search Topics

项目爬取以下主题的数据：

### 国内局势 / Domestic Situations
- 🇨🇳 中国政治、经济、社会
- 🇺🇸 美国政治、经济、社会
- 🇯🇵 日本政治、经济、社会
- 🇪🇺 欧盟局势
- 🇷🇺 俄罗斯国际关系
- 🇮🇳 印度局势

### 国际关系 / International Relations
- 国际局势
- 亚洲地缘政治
- 多国关系

## 输出文件 / Output Files

运行成功后会生成以下文件：

### tweepy版本：
- `twitter_data_tweepy_2025.csv` - CSV格式数据
- `twitter_data_tweepy_2025.json` - JSON格式数据

### snscrape版本：
- `twitter_data_snscrape_2025.csv` - CSV格式数据
- `twitter_data_snscrape_2025.json` - JSON格式数据

## 数据字段 / Data Fields

### tweepy输出字段：
- `id` - 推文ID
- `text` - 推文内容
- `created_at` - 创建时间
- `author_username` - 作者用户名
- `author_name` - 作者显示名称
- `author_verified` - 是否认证用户
- `language` - 语言
- `retweet_count` - 转发数
- `reply_count` - 回复数
- `like_count` - 点赞数
- `quote_count` - 引用数
- `engagement_score` - 互动分数

### snscrape输出字段：
- `id` - 推文ID
- `url` - 推文URL
- `date` - 发布日期
- `username` - 用户名
- `display_name` - 显示名称
- `user_verified` - 是否认证
- `user_followers` - 粉丝数
- `text` - 推文内容
- `retweet_count` - 转发数
- `reply_count` - 回复数
- `like_count` - 点赞数
- `quote_count` - 引用数
- `language` - 语言
- `hashtags` - 话题标签
- `engagement_score` - 互动分数

## 参考资料 / References

- [Mastering Twitter Scraping](https://www.rapidseedbox.com/blog/mastering-twitter-scraping)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [snscrape GitHub](https://github.com/JustAnotherArchivist/snscrape)

## 注意事项 / Notes

1. **日期限制**：本项目专注于2025年的数据。如果在2025年之前运行，可能需要调整日期参数。
2. **速率限制**：使用tweepy时注意API速率限制。代码已设置自动等待。
3. **合规使用**：请遵守Twitter的使用条款和当地法律法规。
4. **数据隐私**：爬取的数据仅限于公开可见的内容。

## 代码结构 / Code Structure

```
scrape_social_media/
├── requirements.txt              # 依赖包
├── twitter_scraper_tweepy.py    # tweepy实现
├── twitter_scraper_snscrape.py  # snscrape实现
├── examples.py                   # 使用示例
└── README.md                     # 说明文档
```

## 使用示例 / Examples

提供了 `examples.py` 文件展示如何使用这两个爬虫：

```bash
# 运行所有示例
python examples.py

# 只运行tweepy示例
python examples.py tweepy

# 只运行snscrape示例
python examples.py snscrape

# 运行自定义实现示例
python examples.py custom
```

示例包括：
1. **基础使用** - 如何初始化和运行爬虫
2. **自定义查询** - 如何使用自定义搜索词
3. **数据处理** - 如何分析和筛选结果
4. **保存数据** - 如何导出为CSV/JSON

## 示例输出 / Example Output

```
=============================================================
Twitter Scraper using snscrape
Scraping domestic and international situation data for 2025
=============================================================

Query 1/13: China domestic situation (Chinese)
Scraping query: 中国 (政治 OR 经济 OR 社会) since:2025-01-01
Scraped 100 tweets
Total tweets collected so far: 100

...

=============================================================
Scraping completed!
Total unique tweets scraped: 1200
Date range: 2025-01-01 to 2025-12-13
Average engagement score: 245.32
Max engagement score: 15430
=============================================================
```

## 故障排除 / Troubleshooting

### tweepy问题

**问题：401 Unauthorized**
- 检查Bearer Token是否正确
- 确认Token权限足够

**问题：429 Too Many Requests**
- 等待速率限制重置
- 减少max_results参数

### snscrape问题

**问题：没有返回数据**
- 检查网络连接
- 确认日期范围正确
- Twitter可能更新了页面结构

**问题：ModuleNotFoundError**
- 重新安装：`pip install snscrape --upgrade`

## 许可证 / License

本项目为教育用途，请遵守Twitter使用条款。

## 贡献 / Contributing

欢迎提交Issue和Pull Request！
