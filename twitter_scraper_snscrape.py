#!/usr/bin/env python3
"""
Twitter Scraper using snscrape Library
Scrapes Twitter data about domestic and international situations for 2025
Focus on trending topics related to China, US, Japan and other countries
"""

import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime, timedelta
import json


class TwitterScraperSnscrape:
    """
    Twitter scraper using snscrape library for collecting data about
    domestic and international situations from 2025
    """

    def __init__(self):
        """
        Initialize the scraper
        snscrape doesn't require API credentials
        """
        print("Initializing Twitter scraper using snscrape...")
        print("Note: snscrape doesn't require API credentials")

    def get_search_queries(self):
        """
        Define search queries for domestic and international situations
        Focused on China, US, Japan and other major countries

        Returns:
            list: List of search query dictionaries
        """
        queries = [
            # China domestic situation
            {
                'query': '中国 (政治 OR 经济 OR 社会)',
                'description': 'China domestic situation (Chinese)'
            },
            {
                'query': 'China (politics OR economy OR society)',
                'description': 'China domestic situation (English)'
            },

            # US domestic situation
            {
                'query': '美国 (政治 OR 经济 OR 社会)',
                'description': 'USA domestic situation (Chinese)'
            },
            {
                'query': 'USA (politics OR economy OR society)',
                'description': 'USA domestic situation (English)'
            },
            {
                'query': 'America domestic policy',
                'description': 'America domestic policy'
            },

            # Japan domestic situation
            {
                'query': '日本 (政治 OR 経済 OR 社会)',
                'description': 'Japan domestic situation (Japanese/Chinese)'
            },
            {
                'query': 'Japan (politics OR economy OR society)',
                'description': 'Japan domestic situation (English)'
            },

            # International relations
            {
                'query': '国际局势',
                'description': 'International situation (Chinese)'
            },
            {
                'query': 'international situation (China OR USA OR Japan)',
                'description': 'International situation'
            },
            {
                'query': 'geopolitics Asia',
                'description': 'Asia geopolitics'
            },

            # Other major countries
            {
                'query': 'European Union (politics OR economy)',
                'description': 'European Union situation'
            },
            {
                'query': 'Russia international relations',
                'description': 'Russia international relations'
            },
            {
                'query': 'India (politics OR economy)',
                'description': 'India domestic situation'
            },
        ]
        return queries

    def scrape_tweets(self, query, max_results=100, start_date="2025-01-01", end_date=None):
        """
        Scrape tweets based on a search query

        Args:
            query: Search query string
            max_results: Maximum number of tweets to retrieve
            start_date: Start date in YYYY-MM-DD format (default: 2025-01-01)
            end_date: End date in YYYY-MM-DD format (default: None for current date)

        Returns:
            list: List of tweet dictionaries
        """
        tweets_data = []

        try:
            # Build the query with date filter
            if end_date:
                search_query = f"{query} since:{start_date} until:{end_date}"
            else:
                search_query = f"{query} since:{start_date}"

            print(f"Scraping query: {search_query}")

            # Scrape tweets using TwitterSearchScraper
            # Note: snscrape returns tweets in reverse chronological order (newest first)
            tweet_count = 0
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(search_query).get_items()):
                if tweet_count >= max_results:
                    break

                tweet_dict = {
                    'id': tweet.id,
                    'url': tweet.url,
                    'date': tweet.date,
                    'user': tweet.user.username,
                    'username': tweet.user.username,
                    'display_name': tweet.user.displayname,
                    'user_verified': tweet.user.verified if hasattr(tweet.user, 'verified') else False,
                    'user_followers': tweet.user.followersCount if hasattr(tweet.user, 'followersCount') else 0,
                    'text': getattr(tweet, 'rawContent', None) or getattr(tweet, 'content', ''),
                    'reply_count': tweet.replyCount if hasattr(tweet, 'replyCount') else 0,
                    'retweet_count': tweet.retweetCount if hasattr(tweet, 'retweetCount') else 0,
                    'like_count': tweet.likeCount if hasattr(tweet, 'likeCount') else 0,
                    'quote_count': tweet.quoteCount if hasattr(tweet, 'quoteCount') else 0,
                    'language': tweet.lang if hasattr(tweet, 'lang') else None,
                    'hashtags': list(tweet.hashtags) if tweet.hashtags is not None else [],
                    'query': query
                }
                tweets_data.append(tweet_dict)
                tweet_count += 1

            print(f"Scraped {len(tweets_data)} tweets")

        except Exception as e:
            print(f"Error scraping tweets for query '{query}': {e}")

        return tweets_data

    def scrape_all_queries(self, max_results_per_query=100, start_date="2025-01-01"):
        """
        Scrape tweets for all predefined queries

        Args:
            max_results_per_query: Maximum results per query (default: 100)
            start_date: Start date for scraping (default: 2025-01-01)

        Returns:
            pd.DataFrame: DataFrame containing all scraped tweets
        """
        all_tweets = []
        queries = self.get_search_queries()

        print(f"\n{'=' * 60}")
        print(f"Starting to scrape {len(queries)} queries...")
        print(f"Date range: from {start_date}")
        print(f"Max results per query: {max_results_per_query}")
        print(f"{'=' * 60}\n")

        for i, query_dict in enumerate(queries, 1):
            query = query_dict['query']
            description = query_dict['description']

            print(f"\nQuery {i}/{len(queries)}: {description}")
            tweets = self.scrape_tweets(query, max_results=max_results_per_query, start_date=start_date)
            all_tweets.extend(tweets)
            print(f"Total tweets collected so far: {len(all_tweets)}")

        # Convert to DataFrame
        df = pd.DataFrame(all_tweets)

        if not df.empty:
            # Calculate engagement score (prioritize hot/trending topics)
            df['engagement_score'] = (
                    df['like_count'] +
                    df['retweet_count'] * 2 +
                    df['reply_count'] +
                    df['quote_count']
            )

            # Sort by engagement score (trending/hot topics first)
            df = df.sort_values('engagement_score', ascending=False)

            # Remove duplicates (same tweet might appear in multiple queries)
            df = df.drop_duplicates(subset=['id'], keep='first')

            print(f"\n{'=' * 60}")
            print(f"Scraping completed!")
            print(f"Total unique tweets scraped: {len(df)}")
            if not df.empty:
                print(f"Date range: {df['date'].min()} to {df['date'].max()}")
                print(f"Average engagement score: {df['engagement_score'].mean():.2f}")
                print(f"Max engagement score: {df['engagement_score'].max()}")
            print(f"{'=' * 60}\n")
        else:
            print("\nNo tweets found.")

        return df

    @staticmethod
    def _format_hashtags_for_csv(hashtags):
        """
        Format hashtags list for CSV export

        Args:
            hashtags: List of hashtags, or None

        Returns:
            str: Comma-separated hashtags or empty string
        """
        if isinstance(hashtags, list) and hashtags:
            return ','.join(hashtags)
        return ''

    def save_to_csv(self, df, filename='twitter_data_snscrape_2025.csv'):
        """
        Save scraped data to CSV file

        Args:
            df: DataFrame with tweet data
            filename: Output filename
        """
        if not df.empty:
            # Convert date to string for CSV compatibility
            df_copy = df.copy()
            df_copy['date'] = df_copy['date'].astype(str)
            df_copy['hashtags'] = df_copy['hashtags'].apply(self._format_hashtags_for_csv)

            df_copy.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Data saved to {filename}")
        else:
            print("No data to save.")

    def save_to_json(self, df, filename='twitter_data_snscrape_2025.json'):
        """
        Save scraped data to JSON file

        Args:
            df: DataFrame with tweet data
            filename: Output filename
        """
        if not df.empty:
            # Convert date to string for JSON serialization
            df_copy = df.copy()
            df_copy['date'] = df_copy['date'].astype(str)

            df_copy.to_json(filename, orient='records', force_ascii=False, indent=2)
            print(f"Data saved to {filename}")
        else:
            print("No data to save.")

    def save_to_jsonl(self, df, filename='twitter_data_snscrape_2025.jsonl', text_only=False):
        """
        Save scraped data to JSON Lines (.jsonl), one record per line.

        Args:
            df: DataFrame with tweet data
            filename: Output filename
            text_only: If True, only save {"id":..., "text":...} (and minimal fields).
        """
        if df.empty:
            print("No data to save.")
            return

        df_copy = df.copy()
        # Ensure JSON-serializable
        if 'date' in df_copy.columns:
            df_copy['date'] = df_copy['date'].astype(str)

        with open(filename, 'w', encoding='utf-8') as f:
            for _, row in df_copy.iterrows():
                rec = row.to_dict()
                if text_only:
                    rec = {
                        "id": rec.get("id"),
                        "text": rec.get("text", ""),
                        "date": rec.get("date"),
                        "lang": rec.get("language"),
                        "source": "snscrape",
                        "query": rec.get("query"),
                        "url": rec.get("url"),
                    }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        print(f"Data saved to {filename} (jsonl, text_only={text_only})")

    def get_top_tweets(self, df, n=10):
        """
        Get top N tweets by engagement score

        Args:
            df: DataFrame with tweet data
            n: Number of top tweets to return

        Returns:
            pd.DataFrame: Top N tweets
        """
        if df.empty:
            return df

        return df.nlargest(n, 'engagement_score')

    def get_statistics(self, df):
        """
        Generate statistics about the scraped data

        Args:
            df: DataFrame with tweet data

        Returns:
            dict: Statistics dictionary
        """
        if df.empty:
            return {}

        stats = {
            'total_tweets': len(df),
            'unique_users': df['username'].nunique(),
            'date_range': {
                'start': str(df['date'].min()),
                'end': str(df['date'].max())
            },
            'engagement': {
                'total_likes': int(df['like_count'].sum()),
                'total_retweets': int(df['retweet_count'].sum()),
                'total_replies': int(df['reply_count'].sum()),
                'avg_engagement_score': float(df['engagement_score'].mean())
            },
            'top_languages': df['language'].value_counts().head(5).to_dict(),
            'verified_users': int(df['user_verified'].sum()) if 'user_verified' in df.columns else 0
        }

        return stats


def main():
    """
    Main function to run the Twitter scraper
    """
    print("=" * 60)
    print("Twitter Scraper using snscrape")
    print("Scraping domestic and international situation data for 2025")
    print("=" * 60)
    print("\nNote: snscrape doesn't require API credentials")
    print("It scrapes publicly available data from Twitter")

    try:
        # Initialize scraper
        scraper = TwitterScraperSnscrape()

        # Scrape tweets from 2025
        # Note: If running before 2025, you may need to adjust the date
        df = scraper.scrape_all_queries(max_results_per_query=100, start_date="2025-01-01")

        if not df.empty:
            # Save results
            scraper.save_to_csv(df)
            scraper.save_to_json(df)
            scraper.save_to_jsonl(df, filename="twitter_data_snscrape_2025_raw.jsonl", text_only=False)
            scraper.save_to_jsonl(df, filename="twitter_data_snscrape_2025_text.jsonl", text_only=True)

            # Display statistics
            stats = scraper.get_statistics(df)
            print("\n" + "=" * 60)
            print("Summary Statistics")
            print("=" * 60)
            print(json.dumps(stats, indent=2, ensure_ascii=False))

            # Display top 10 trending tweets
            print("\n" + "=" * 60)
            print("Top 10 Trending Tweets (by engagement)")
            print("=" * 60)
            top_tweets = scraper.get_top_tweets(df, n=10)
            for idx, (i, tweet) in enumerate(top_tweets.iterrows(), 1):
                print(f"\n{idx}. @{tweet['username']} (Engagement: {tweet['engagement_score']})")
                print(
                    f"   Likes: {tweet['like_count']}, Retweets: {tweet['retweet_count']}, Replies: {tweet['reply_count']}")
                print(f"   Text: {tweet['text'][:100]}...")
                print(f"   URL: {tweet['url']}")

    except Exception as e:
        print(f"\nError running scraper: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()