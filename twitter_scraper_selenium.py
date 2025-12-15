#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Twitter (X) Scraper using Selenium
自动化爬取推特搜索结果并保存为 JSONL 格式
支持断点续爬和去重机制
"""

import jsonlines
import logging
import time
import urllib.parse
from pathlib import Path
from typing import Dict, List, Set, Optional

from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('twitter_scraper.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TwitterScraper:
    """推特爬虫类，使用 Selenium 进行自动化爬取"""
    
    def __init__(self, edge_profile_path: Optional[str] = None, headless: bool = False):
        """
        初始化推特爬虫
        
        Args:
            edge_profile_path: Edge浏览器用户配置路径，用于保持登录态
            headless: 是否使用无头模式
        """
        self.edge_profile_path = edge_profile_path
        self.headless = headless
        self.driver = None
        self.wait = None
        self.scraped_tweets: Set[str] = set()  # 已爬取推文的唯一标识
        self.output_dir = Path("twitter_data")
        self.output_dir.mkdir(exist_ok=True)
        
    def setup_driver(self):
        """配置并启动 Edge 浏览器"""
        logger.info("正在设置 Edge 浏览器...")
        
        edge_options = Options()
        
        # 加载用户配置以保持登录态
        if self.edge_profile_path:
            edge_options.add_argument(f"user-data-dir={self.edge_profile_path}")
            logger.info(f"使用用户配置: {self.edge_profile_path}")
        
        # 无头模式
        if self.headless:
            edge_options.add_argument("--headless")
            
        # 其他优化选项
        edge_options.add_argument("--disable-blink-features=AutomationControlled")
        edge_options.add_argument("--disable-dev-shm-usage")
        edge_options.add_argument("--no-sandbox")
        edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        edge_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Edge(options=edge_options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("Edge 浏览器启动成功")
        except Exception as e:
            logger.error(f"启动 Edge 浏览器失败: {e}")
            raise
    
    def generate_search_url(self, query: str, search_type: str = "top") -> str:
        """
        生成推特搜索 URL
        
        Args:
            query: 搜索关键词
            search_type: 搜索类型 (top, latest, people, photos, videos)
            
        Returns:
            完整的搜索URL
        """
        encoded_query = urllib.parse.quote(query)
        url = f"https://x.com/search?q={encoded_query}&src=typed_query&f={search_type}"
        logger.info(f"生成搜索URL: {url}")
        return url
    
    def load_existing_tweets(self, filename: str) -> Set[str]:
        """
        从已有的 JSONL 文件中加载已爬取的推文ID（用于去重）
        
        Args:
            filename: JSONL文件路径
            
        Returns:
            已爬取推文的唯一标识集合
        """
        tweets = set()
        filepath = self.output_dir / filename
        
        if filepath.exists():
            try:
                with jsonlines.open(filepath, mode='r') as reader:
                    for tweet in reader:
                        # 使用 username + timestamp 作为唯一标识
                        unique_id = f"{tweet.get('username', '')}_{tweet.get('timestamp', '')}"
                        tweets.add(unique_id)
                logger.info(f"从 {filename} 加载了 {len(tweets)} 条已存在的推文")
            except Exception as e:
                logger.error(f"加载已有推文失败: {e}")
        
        return tweets
    
    def click_show_more_buttons(self):
        """点击所有 '显示更多' 按钮以展开完整推文内容"""
        try:
            show_more_buttons = self.driver.find_elements(
                By.XPATH, 
                "//span[contains(text(), '显示更多') or contains(text(), 'Show more')]"
            )
            
            for button in show_more_buttons:
                try:
                    # 滚动到按钮位置并点击
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(0.3)
                    button.click()
                    time.sleep(0.3)
                except Exception as e:
                    logger.debug(f"点击显示更多按钮失败: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"查找显示更多按钮时出错: {e}")
    
    def extract_tweet_data(self, article) -> Optional[Dict]:
        """
        从推文元素中提取数据
        
        Args:
            article: 推文的 article 元素
            
        Returns:
            包含推文数据的字典，如果提取失败返回 None
        """
        try:
            tweet_data = {}
            
            # 提取用户名 (@username)
            try:
                username_elem = article.find_element(
                    By.XPATH, 
                    ".//div[@data-testid='User-Name']//a[contains(@href, '/')]"
                )
                username = username_elem.get_attribute("href").split("/")[-1]
                tweet_data['username'] = f"@{username}"
            except NoSuchElementException:
                logger.debug("未找到用户名")
                tweet_data['username'] = ""
            
            # 提取显示名称
            try:
                name_elem = article.find_element(
                    By.XPATH,
                    ".//div[@data-testid='User-Name']//span[contains(@class, 'css-')]"
                )
                tweet_data['name'] = name_elem.text
            except NoSuchElementException:
                logger.debug("未找到显示名称")
                tweet_data['name'] = ""
            
            # 提取时间戳
            try:
                time_elem = article.find_element(By.XPATH, ".//time")
                timestamp = time_elem.get_attribute("datetime")
                tweet_data['timestamp'] = timestamp
            except NoSuchElementException:
                logger.debug("未找到时间戳")
                tweet_data['timestamp'] = ""
            
            # 提取推文内容
            try:
                content_elem = article.find_element(
                    By.XPATH,
                    ".//div[@data-testid='tweetText']"
                )
                tweet_data['content'] = content_elem.text
            except NoSuchElementException:
                logger.debug("未找到推文内容")
                tweet_data['content'] = ""
            
            # 提取图片URL
            try:
                image_elems = article.find_elements(
                    By.XPATH,
                    ".//div[@data-testid='tweetPhoto']//img"
                )
                image_urls = [img.get_attribute("src") for img in image_elems if img.get_attribute("src")]
                tweet_data['image'] = image_urls[0] if image_urls else ""
            except Exception:
                tweet_data['image'] = ""
            
            # 提取互动数据
            # 点赞数
            try:
                likes_elem = article.find_element(
                    By.XPATH,
                    ".//button[@data-testid='like']//span"
                )
                likes_text = likes_elem.text
                tweet_data['likes'] = self._parse_number(likes_text)
            except (NoSuchElementException, ValueError):
                tweet_data['likes'] = 0
            
            # 转发数
            try:
                retweets_elem = article.find_element(
                    By.XPATH,
                    ".//button[@data-testid='retweet']//span"
                )
                retweets_text = retweets_elem.text
                tweet_data['retweets'] = self._parse_number(retweets_text)
            except (NoSuchElementException, ValueError):
                tweet_data['retweets'] = 0
            
            # 检查是否有必要字段
            if not tweet_data.get('username') or not tweet_data.get('timestamp'):
                return None
                
            return tweet_data
            
        except StaleElementReferenceException:
            logger.debug("元素已过期")
            return None
        except Exception as e:
            logger.error(f"提取推文数据时出错: {e}")
            return None
    
    def _parse_number(self, text: str) -> int:
        """
        解析推特显示的数字（如 1.5K, 2.3M）
        
        Args:
            text: 数字文本
            
        Returns:
            解析后的整数
        """
        if not text:
            return 0
        
        text = text.strip().upper()
        
        try:
            if 'K' in text:
                return int(float(text.replace('K', '')) * 1000)
            elif 'M' in text:
                return int(float(text.replace('M', '')) * 1000000)
            else:
                return int(text.replace(',', ''))
        except ValueError:
            return 0
    
    def scroll_and_load(self, scroll_pause_time: float = 2.0, max_scrolls: int = 50):
        """
        滚动页面以加载更多推文
        
        Args:
            scroll_pause_time: 每次滚动后的等待时间
            max_scrolls: 最大滚动次数
        """
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scroll_count = 0
        
        while scroll_count < max_scrolls:
            # 滚动到页面底部
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)
            
            # 点击显示更多按钮
            self.click_show_more_buttons()
            
            # 计算新的滚动高度
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                logger.info("已到达页面底部")
                break
                
            last_height = new_height
            scroll_count += 1
            logger.info(f"已滚动 {scroll_count} 次")
    
    def scrape_query(self, query: str, description: str, max_tweets: int = 2000) -> int:
        """
        爬取指定查询的推文
        
        Args:
            query: 搜索查询
            description: 查询描述（用于文件名）
            max_tweets: 最大爬取推文数
            
        Returns:
            新爬取的推文数量
        """
        # 生成文件名（使用查询描述的安全版本）
        safe_description = "".join(
            c if c.isalnum() or c in (' ', '_', '-') else '_' 
            for c in description
        ).strip().replace(' ', '_')
        filename = f"{safe_description}.jsonl"
        filepath = self.output_dir / filename
        
        # 加载已有推文以实现去重
        self.scraped_tweets = self.load_existing_tweets(filename)
        initial_count = len(self.scraped_tweets)
        
        logger.info(f"开始爬取查询: {description}")
        logger.info(f"查询语句: {query}")
        logger.info(f"输出文件: {filepath}")
        logger.info(f"已有推文数: {initial_count}")
        
        # 访问搜索页面
        search_url = self.generate_search_url(query)
        self.driver.get(search_url)
        time.sleep(5)  # 等待页面加载
        
        new_tweets_count = 0
        consecutive_no_new = 0
        max_consecutive_no_new = 3
        
        try:
            with jsonlines.open(filepath, mode='a') as writer:
                while new_tweets_count < max_tweets:
                    # 滚动加载更多推文
                    self.scroll_and_load(scroll_pause_time=2.0, max_scrolls=5)
                    
                    # 点击所有显示更多按钮
                    self.click_show_more_buttons()
                    time.sleep(1)
                    
                    # 查找所有推文
                    articles = self.driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
                    logger.info(f"找到 {len(articles)} 个推文元素")
                    
                    batch_new = 0
                    for article in articles:
                        if new_tweets_count >= max_tweets:
                            break
                        
                        # 提取推文数据
                        tweet_data = self.extract_tweet_data(article)
                        
                        if tweet_data:
                            # 生成唯一ID
                            unique_id = f"{tweet_data['username']}_{tweet_data['timestamp']}"
                            
                            # 检查是否已爬取
                            if unique_id not in self.scraped_tweets:
                                # 写入文件
                                writer.write(tweet_data)
                                self.scraped_tweets.add(unique_id)
                                new_tweets_count += 1
                                batch_new += 1
                                
                                logger.info(
                                    f"新推文 [{new_tweets_count}/{max_tweets}]: "
                                    f"{tweet_data['username']} - {tweet_data['timestamp'][:10]}"
                                )
                    
                    # 如果连续多次没有新推文，可能已到底部
                    if batch_new == 0:
                        consecutive_no_new += 1
                        logger.info(f"本次滚动未发现新推文 ({consecutive_no_new}/{max_consecutive_no_new})")
                        if consecutive_no_new >= max_consecutive_no_new:
                            logger.info("连续多次未发现新推文，停止爬取")
                            break
                    else:
                        consecutive_no_new = 0
                    
                    time.sleep(2)
        
        except Exception as e:
            logger.error(f"爬取过程中出错: {e}")
        
        logger.info(f"查询 '{description}' 完成，新爬取 {new_tweets_count} 条推文")
        return new_tweets_count
    
    def scrape_queries(self, queries: List[Dict]):
        """
        批量爬取多个查询
        
        Args:
            queries: 查询列表，每个查询包含 'query' 和 'description' 字段
        """
        logger.info(f"开始批量爬取，共 {len(queries)} 个查询")
        
        for i, query_dict in enumerate(queries, 1):
            query = query_dict['query']
            description = query_dict['description']
            
            logger.info(f"\n{'='*60}")
            logger.info(f"处理查询 [{i}/{len(queries)}]: {description}")
            logger.info(f"{'='*60}")
            
            try:
                self.scrape_query(query, description, max_tweets=2000)
            except Exception as e:
                logger.error(f"查询 '{description}' 失败: {e}")
                continue
            
            # 每个查询之间暂停一下
            if i < len(queries):
                logger.info("等待5秒后继续下一个查询...")
                time.sleep(5)
        
        logger.info("\n所有查询处理完成！")
    
    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            logger.info("浏览器已关闭")


def main():
    """主函数"""
    # 查询列表
    queries = [
        {
            "query": "韩国 (总统 OR 选举 OR 国会 OR 示威 OR 对朝 OR 军演 OR 美韩同盟) -is:retweet lang:zh",
            "description": "South Korea politics/security (Chinese)"
        },
        # 可以添加更多查询
    ]
    
    # Edge 浏览器用户配置路径（根据实际情况修改）
    # Windows 示例: r"C:\Users\YourUsername\AppData\Local\Microsoft\Edge\User Data"
    # 如果不需要保持登录态，可以设置为 None
    edge_profile_path = None
    
    # 创建爬虫实例
    scraper = TwitterScraper(edge_profile_path=edge_profile_path, headless=False)
    
    try:
        # 设置浏览器
        scraper.setup_driver()
        
        # 爬取所有查询
        scraper.scrape_queries(queries)
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
    finally:
        # 关闭浏览器
        scraper.close()


if __name__ == "__main__":
    main()
