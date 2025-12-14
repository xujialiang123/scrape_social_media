#!/usr/bin/env python3
"""
Twitter Scraper using Tweepy Library
Scrapes Twitter data about domestic and international situations for 2025
Focus on trending topics related to China, US, Japan and other countries
"""

import tweepy
import pandas as pd
from datetime import datetime, timezone
import json
import os


# Default start date for 2025 data collection
DEFAULT_START_DATE = "2025-01-01T00:00:00Z"


class TwitterScraperTweepy:
    """
    Twitter scraper using Tweepy library for collecting data about
    domestic and international situations from 2025
    """

    def __init__(self, bearer_token=None):
        """
        Initialize the scraper with Twitter API credentials

        Args:
            bearer_token: Twitter API v2 Bearer Token
        """
        # IMPORTANT: Do NOT hardcode tokens in code.
        # Read from argument first, then from environment variable.
        self.bearer_token = bearer_token or os.environ.get("TWITTER_BEARER_TOKEN")

        if not self.bearer_token:
            raise ValueError(
                "Bearer token is required. Set TWITTER_BEARER_TOKEN environment variable "
                "or pass it directly."
            )

        # Initialize the Twitter API client with v2 endpoint
        self.client = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)

    def get_search_queries(self):
        """
        Define search queries for domestic and international situations
        Focused on China, US, Japan and other major countries

        Returns:
            list: List of search query strings
        """
        queries = [
            # China domestic situation
            "中国 (政治 OR 经济 OR 社会) -is:retweet lang:zh",
            "China (politics OR economy OR society) -is:retweet lang:en",

            # US domestic situation
            "美国 (政治 OR 经济 OR 社会) -is:retweet lang:zh",
            "USA (politics OR economy OR society) -is:retweet lang:en",
            "America (domestic OR policy) -is:retweet lang:en",

            # Japan domestic situation
            "日本 (政治 OR 経済 OR 社会) -is:retweet",
            "Japan (politics OR economy OR society) -is:retweet lang:en",

            # International relations
            "国际局势 -is:retweet lang:zh",
            "international situation (China OR USA OR Japan) -is:retweet lang:en",
            "geopolitics Asia -is:retweet lang:en",

            # Other major countries
            "European Union (politics OR economy) -is:retweet lang:en",
            "Russia (international OR relations) -is:retweet lang:en",
            "India (politics OR economy) -is:retweet lang:en",
        ]
        return queries

    def scrape_tweets(self, query, max_results=100, start_time=DEFAULT_START_DATE):
        """
        Scrape tweets based on a search query

        Args:
            query: Search query string
            max_results: Maximum number of tweets to retrieve (10-100 per request)
            start_time: Start time in ISO format (default: 2025-01-01)

        Returns:
            list: List of tweet dictionaries

        Note:
            - search_recent_tweets only searches the past 7 days by default
        """
        tweets_data = []

        try:
            from datetime import datetime, timezone, timedelta
            current_time = datetime.now(timezone.utc)
            seven_days_ago = current_time - timedelta(days=7)

            search_params = {
                "query": query,
                "max_results": max_results,
                "tweet_fields": ["created_at", "public_metrics", "author_id", "lang", "entities"],
                "user_fields": ["username", "name", "verified", "public_metrics"],
                "expansions": ["author_id"],
            }

            if start_time and start_time != DEFAULT_START_DATE:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    if start_dt >= seven_days_ago:
                        search_params["start_time"] = start_time
                except ValueError:
                    pass

            tweets = self.client.search_recent_tweets(**search_params)

            users = {}
            if tweets.includes and "users" in tweets.includes:
                for user in tweets.includes["users"]:
                    users[user.id] = user

            if tweets.data:
                for tweet in tweets.data:
                    author = users.get(tweet.author_id)

                    tweet_dict = {
                        "id": tweet.id,
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "author_id": tweet.author_id,
                        "author_username": author.username if author else None,
                        "author_name": author.name if author else None,
                        "author_verified": author.verified if author else None,
                        "language": tweet.lang if hasattr(tweet, "lang") else None,
                        "retweet_count": tweet.public_metrics["retweet_count"] if tweet.public_metrics else 0,
                        "reply_count": tweet.public_metrics["reply_count"] if tweet.public_metrics else 0,
                        "like_count": tweet.public_metrics["like_count"] if tweet.public_metrics else 0,
                        "quote_count": tweet.public_metrics["quote_count"] if tweet.public_metrics else 0,
                        "query": query,
                    }
                    tweets_data.append(tweet_dict)

            print(f"Scraped {len(tweets_data)} tweets for query: {query[:50]}...")

        except tweepy.TweepyException as e:
            print(f"Error scraping tweets for query '{query}': {e}")

        return tweets_data

    def scrape_all_queries(self, max_results_per_query=100):
        all_tweets = []
        queries = self.get_search_queries()

        print(f"Starting to scrape {len(queries)} queries...")

        for i, query in enumerate(queries, 1):
            print(f"\nProcessing query {i}/{len(queries)}")
            tweets = self.scrape_tweets(query, max_results=max_results_per_query)
            all_tweets.extend(tweets)

        df = pd.DataFrame(all_tweets)

        if not df.empty:
            df["engagement_score"] = df["like_count"] + df["retweet_count"] * 2 + df["reply_count"]
            df = df.sort_values("engagement_score", ascending=False)

            print(f"\nTotal tweets scraped: {len(df)}")
            print(f"Date range: {df['created_at'].min()} to {df['created_at'].max()}")
        else:
            print("\nNo tweets found.")

        return df

    def save_to_csv(self, df, filename="twitter_data_tweepy_2025.csv"):
        if not df.empty:
            df.to_csv(filename, index=False, encoding="utf-8-sig")
            print(f"\nData saved to {filename}")
        else:
            print("No data to save.")

    def save_to_jsonl(self, df, filename="twitter_data_tweepy_2025_text.jsonl"):
        """
        Save as JSON Lines for LM training: one sample per line.
        Minimal schema: {"id":..., "text":..., "date":..., "lang":..., "source":..., "query":...}
        """
        if df.empty:
            print("No data to save.")
            return

        df_copy = df.copy()
        if "created_at" in df_copy.columns:
            df_copy["created_at"] = df_copy["created_at"].astype(str)

        with open(filename, "w", encoding="utf-8") as f:
            for _, row in df_copy.iterrows():
                rec = row.to_dict()
                out = {
                    "id": rec.get("id"),
                    "text": rec.get("text", ""),
                    "date": rec.get("created_at"),
                    "lang": rec.get("language"),
                    "source": "tweepy",
                    "query": rec.get("query"),
                }
                f.write(json.dumps(out, ensure_ascii=False) + "\n")

        print(f"Data saved to {filename} (jsonl)")


def main():
    print("=" * 60)
    print("Twitter Scraper using Tweepy")
    print("Scraping domestic and international situation data for 2025")
    print("=" * 60)

    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        print("\nERROR: TWITTER_BEARER_TOKEN environment variable not set.")
        print("\nSet it like:")
        print("  export TWITTER_BEARER_TOKEN='your_bearer_token_here'")
        return

    try:
        scraper = TwitterScraperTweepy(bearer_token=bearer_token)
        df = scraper.scrape_all_queries(max_results_per_query=100)

        if not df.empty:
            scraper.save_to_csv(df)
            scraper.save_to_jsonl(df)

    except Exception as e:
        print(f"\nError running scraper: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()