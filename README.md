# scrape_social_media
数据科学实验一作业

## 推特 (X) 自动爬取工具

基于 Selenium 的推特自动化爬虫，支持关键词搜索、断点续爬、自动去重和 JSONL 格式存储。

### 功能特性

1. **搜索链接生成**: 根据查询关键词自动生成推特搜索 URL
2. **完整数据提取**: 
   - 用户名 (@username)
   - 显示名称 (name)
   - 时间戳 (timestamp)
   - 完整推文内容 (content)
   - 图片URL (image)
   - 点赞数 (likes)
   - 转发数 (retweets)
3. **智能内容加载**: 自动点击"显示更多"按钮展开完整推文内容
4. **断点续爬**: 支持中断后继续爬取，不会重复爬取已有数据
5. **自动去重**: 基于用户名+时间戳的唯一性标识实现去重
6. **滚动加载**: 自动滚动页面加载更多推文
7. **JSONL 格式**: 每条推文一行，方便增量写入和读取
8. **异常处理**: 完善的错误处理和日志记录机制
9. **Edge 浏览器**: 支持加载用户 Profile 保持登录态

### 安装依赖

```bash
pip install -r requirements.txt
```

**依赖说明**:
- `selenium>=4.15.0`: 浏览器自动化框架
- `jsonlines>=4.0.0`: JSONL 格式文件读写

**浏览器驱动**:
- 需要安装 Microsoft Edge 浏览器
- Selenium 4.x 会自动下载和管理浏览器驱动

### 使用方法

#### 1. 基本使用

```python
python twitter_scraper_selenium.py
```

#### 2. 配置查询

编辑 `twitter_scraper_selenium.py` 文件中的 `queries` 列表：

```python
queries = [
    {
        "query": "韩国 (总统 OR 选举 OR 国会 OR 示威 OR 对朝 OR 军演 OR 美韩同盟) -is:retweet lang:zh",
        "description": "South Korea politics/security (Chinese)"
    },
    {
        "query": "日本 (首相 OR 选举) -is:retweet lang:zh",
        "description": "Japan politics (Chinese)"
    },
    # 添加更多查询...
]
```

**查询语法说明**:
- `OR`: 逻辑或，匹配任一关键词
- `-is:retweet`: 排除转推
- `lang:zh`: 限定中文推文
- 括号用于分组条件

#### 3. 配置 Edge 用户配置（可选）

如需保持登录态，设置 Edge 用户配置路径：

```python
# Windows 示例
edge_profile_path = r"C:\Users\YourUsername\AppData\Local\Microsoft\Edge\User Data"

# macOS 示例
edge_profile_path = "/Users/YourUsername/Library/Application Support/Microsoft Edge"

# Linux 示例
edge_profile_path = "/home/YourUsername/.config/microsoft-edge"
```

**注意**: 使用用户配置前请确保 Edge 浏览器已关闭。

#### 4. 调整爬取参数

```python
# 创建爬虫实例
scraper = TwitterScraper(
    edge_profile_path=edge_profile_path,  # 用户配置路径
    headless=False  # 是否使用无头模式
)

# 爬取时设置最大推文数
scraper.scrape_query(query, description, max_tweets=2000)
```

### 输出格式

数据保存在 `twitter_data/` 目录下，每个查询对应一个 `.jsonl` 文件。

**文件命名**: 基于查询的 `description` 字段，例如：
- `South_Korea_politics_security__Chinese_.jsonl`

**数据格式** (每行一个 JSON 对象):
```json
{
  "username": "@tanakaseiji15",
  "name": "爆裂大和魂",
  "timestamp": "2025-12-13T11:52:34.000Z",
  "content": "韩国总统尹锡悦宣布紧急戒严令...",
  "image": "https://pbs.twimg.com/media/...",
  "likes": 33328,
  "retweets": 7470
}
```

### 断点续爬

程序会自动检测已有的 `.jsonl` 文件：
- 加载已爬取推文的唯一标识（username + timestamp）
- 跳过已存在的推文，只爬取新推文
- 支持任意时间中断和恢复

### 日志

程序运行时会生成两份日志：
1. **控制台输出**: 实时显示爬取进度
2. **日志文件**: `twitter_scraper.log`，记录详细的运行信息和错误

### 注意事项

1. **登录要求**: 推特可能要求登录才能查看搜索结果，建议配置 Edge 用户配置
2. **速率限制**: 推特有访问频率限制，建议在查询间添加延迟
3. **反爬虫**: 频繁爬取可能触发验证码或封禁，请合理控制爬取速度
4. **数据准确性**: 推文互动数据（点赞、转发）会实时变化
5. **网络稳定**: 需要稳定的网络连接访问推特

### 故障排除

**问题**: 浏览器无法启动
- 检查 Edge 浏览器是否已安装
- 检查 Selenium 版本是否 >= 4.15.0
- 如使用用户配置，确保 Edge 浏览器已关闭

**问题**: 无法找到推文元素
- 推特页面结构可能已更新，需要调整 XPath 选择器
- 检查是否需要登录才能查看内容

**问题**: 爬取速度慢
- 调整 `scroll_pause_time` 参数（减小等待时间）
- 调整 `max_scrolls` 参数（增加单次滚动次数）

**问题**: 出现重复数据
- 检查 `username` 和 `timestamp` 是否正确提取
- 查看日志文件确认去重逻辑是否正常工作

### 许可证

本项目仅用于学习和研究目的，请遵守推特服务条款和相关法律法规。
