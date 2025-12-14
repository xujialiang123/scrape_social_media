#!/usr/bin/env python3
"""
Twitter Scraper using snscrape Library
Scrapes Twitter data about domestic and international situations
Focus on topics related to China, Japan, Korea, US, EU
Outputs JSONL for LLM training
"""

import snscrape.modules.twitter as sntwitter
import pandas as pd
import json


class TwitterScraperSnscrape:
    """
    Twitter scraper using snscrape library.
    """

    def __init__(self):
        print("Initializing Twitter scraper using snscrape...")
        print("Note: snscrape doesn't require API credentials")

    def get_search_queries(self):
        """
        Search queries using Twitter advanced search operators.
        Ensures only Chinese/English and excludes retweets.

        Returns:
            list[dict]: {query, description}
        """
        queries = [
            # China
            {"query": "中国 (外交 OR 国防 OR 军演 OR 台海 OR 南海 OR 制裁 OR 关税 OR 芯片 OR 反制) -is:retweet lang:zh",
             "description": "China CN (foreign/defense/economy)"},
            {"query": "中美 (关系 OR 对抗 OR 会谈 OR 竞争 OR 制裁 OR 科技战 OR 贸易战) -is:retweet lang:zh",
             "description": "US-China relations (Chinese)"},
            {"query": "China (foreign policy OR defense OR military drill OR Taiwan OR South China Sea OR sanctions OR tariff OR semiconductor) -is:retweet lang:en",
             "description": "China EN (foreign/defense/economy)"},
            {"query": "US China (relations OR tensions OR sanctions OR trade war OR tech war) -is:retweet lang:en",
             "description": "US-China relations (English)"},

            # Japan
            {"query": "日本 (安保 OR 自卫队 OR 防卫预算 OR 修宪 OR 台海) -is:retweet lang:zh",
             "description": "Japan security (Chinese)"},
            {"query": "Japan (security OR Self-Defense Forces OR defense budget OR constitutional revision OR Taiwan) -is:retweet lang:en",
             "description": "Japan security (English)"},

            # Korea (ROK + DPRK)
            {"query": "韩国 (总统 OR 选举 OR 国会 OR 示威 OR 对朝 OR 军演 OR 美韩同盟) -is:retweet lang:zh",
             "description": "South Korea politics/security (Chinese)"},
            {"query": "朝鲜 (核试验 OR 导弹 OR 半岛局势 OR 美韩军演) -is:retweet lang:zh",
             "description": "North Korea (Chinese)"},
            {"query": "South Korea (election OR parliament OR protest OR security OR alliance) -is:retweet lang:en",
             "description": "South Korea politics/security (English)"},
            {"query": "North Korea (missile OR nuclear test OR Korean peninsula OR deterrence) -is:retweet lang:en",
             "description": "North Korea (English)"},

            # US
            {"query": "美国 (大选 OR 国会 OR 政府关门 OR 制裁 OR 对华 OR 对俄 OR 对伊朗) -is:retweet lang:zh",
             "description": "US politics/foreign policy (Chinese)"},
            {"query": "US (election OR Congress OR shutdown OR sanctions OR China OR Russia OR Iran) -is:retweet lang:en",
             "description": "US politics/foreign policy (English)"},
            {"query": "US (Indo-Pacific strategy OR AUKUS OR NATO OR deterrence) -is:retweet lang:en",
             "description": "US strategy (English)"},

            # EU / Europe
            {"query": "欧盟 (制裁 OR 对俄 OR 对华 OR 关税 OR 芯片 OR 供应链 OR 防务) -is:retweet lang:zh",
             "description": "EU policy (Chinese)"},
            {"query": "欧洲 (俄乌 OR 乌克兰 OR 北约 OR 军援 OR 能源安全) -is:retweet lang:zh",
             "description": "Europe Ukraine/NATO (Chinese)"},
            {"query": "European Union (sanctions OR Russia OR China OR tariff OR supply chain OR defense) -is:retweet lang:en",
             "description": "EU policy (English)"},
            {"query": "Europe (Ukraine OR Russia OR NATO OR military aid OR energy security) -is:retweet lang:en",
             "description": "Europe Ukraine/NATO (English)"},

            # Global geopolitics
            {"query": "国际局势 (俄乌 OR 以色列 OR 巴勒斯坦 OR 红海 OR 航运 OR 军事升级) -is:retweet lang:zh",
             "description": "Global security hotspots (Chinese)"},
            {"query": "geopolitics (Indo-Pacific OR Asia OR conflict OR crisis) -is:retweet lang:en",
             "description": "Geopolitics (English)"},
        ]
        return queries

    def scrape_tweets(self, query, max_results=200, start_date="2025-01-01", end_date=None):
        """
        Scrape tweets based on a search query string. The query string can include
        Twitter advanced search operators like lang:, since:, until:.

        We append since/until operators here to ensure date filtering.

        Returns:
            list[dict]
        """
        tweets_data = []

        if end_date:
            search_query = f"{query} since:{start_date} until:{end_date}"
        else:
            search_query = f"{query} since:{start_date}"

        print(f"Scraping query: {search_query}")

        tweet_count = 0
        try:
            for tweet in sntwitter.TwitterSearchScraper(search_query).get_items():
                if tweet_count >= max_results:
                    break

                tweet_dict = {
                    "id": tweet.id,
                    "url": tweet.url,
                    "date": str(tweet.date),
                    "username": tweet.user.username,
                    "display_name": tweet.user.displayname,
                    "user_verified": getattr(tweet.user, "verified", False) or False,
                    "user_followers": getattr(tweet.user, "followersCount", 0) or 0,
                    "text": getattr(tweet, "rawContent", None) or getattr(tweet, "content", ""),
                    "reply_count": getattr(tweet, "replyCount", 0) or 0,
                    "retweet_count": getattr(tweet, "retweetCount", 0) or 0,
                    "like_count": getattr(tweet, "likeCount", 0) or 0,
                    "quote_count": getattr(tweet, "quoteCount", 0) or 0,
                    "language": getattr(tweet, "lang", None),
                    "hashtags": list(tweet.hashtags) if getattr(tweet, "hashtags", None) else [],
                    "query": query,
                    "source": "snscrape",
                }

                # Fallback language filter: keep only zh/en
                lang = tweet_dict.get("language")
                if lang not in (None, "zh", "en"):
                    continue

                tweets_data.append(tweet_dict)
                tweet_count += 1

            print(f"Scraped {len(tweets_data)} tweets")
        except Exception as e:
            print(f"Error scraping tweets for query '{query}': {e}")

        return tweets_data

    def scrape_all_queries(self, max_results_per_query=200, start_date="2025-01-01", end_date=None):
        all_tweets = []
        queries = self.get_search_queries()

        print(f"\n{'=' * 60}")
        print(f"Starting to scrape {len(queries)} queries...")
        print(f"Date range: {start_date} -> {end_date or 'now'}")
        print(f"Max results per query: {max_results_per_query}")
        print(f"{'=' * 60}\n")

        for i, query_dict in enumerate(queries, 1):
            print(f"\nQuery {i}/{len(queries)}: {query_dict['description']}")
            tweets = self.scrape_tweets(
                query_dict["query"],
                max_results=max_results_per_query,
                start_date=start_date,
                end_date=end_date,
            )
            all_tweets.extend(tweets)
            print(f"Total tweets collected so far: {len(all_tweets)}")

        df = pd.DataFrame(all_tweets)
        if df.empty:
            print("\nNo tweets found.")
            return df

        df["engagement_score"] = (
            df.get("like_count", 0)
            + df.get("retweet_count", 0) * 2
            + df.get("reply_count", 0)
            + df.get("quote_count", 0)
        )

        df = df.sort_values("engagement_score", ascending=False)
        df = df.drop_duplicates(subset=["id"], keep="first")

        print(f"\nTotal unique tweets scraped: {len(df)}")
        return df

    def save_to_jsonl(self, df, filename="twitter_data_snscrape.jsonl", text_only=True):
        """
        Save JSON Lines for LLM training.
        If text_only=True: minimal schema.
        """
        if df.empty:
            print("No data to save.")
            return

        with open(filename, "w", encoding="utf-8") as f:
            for _, row in df.iterrows():
                rec = row.to_dict()
                if text_only:
                    out = {
                        "id": rec.get("id"),
                        "text": rec.get("text", ""),
                        "date": rec.get("date"),
                        "lang": rec.get("language"),
                        "query": rec.get("query"),
                        "source": rec.get("source", "snscrape"),
                        "url": rec.get("url"),
                    }
                else:
                    out = rec
                f.write(json.dumps(out, ensure_ascii=False) + "\n")

        print(f"Data saved to {filename} (jsonl, text_only={text_only})")


def main():
    scraper = TwitterScraperSnscrape()
    df = scraper.scrape_all_queries(max_results_per_query=200, start_date="2025-01-01")
    if not df.empty:
        scraper.save_to_jsonl(df, filename="twitter_snscrape_text.jsonl", text_only=True)
        scraper.save_to_jsonl(df, filename="twitter_snscrape_raw.jsonl", text_only=False)


if __name__ == "__main__":
    main()