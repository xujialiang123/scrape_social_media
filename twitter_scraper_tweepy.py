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
        self.bearer_token = bearer_token or os.environ.get('TWITTER_BEARER_TOKEN')
        
        if not self.bearer_token:
            raise ValueError("Bearer token is required. Set TWITTER_BEARER_TOKEN environment variable or pass it directly.")
        
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
    
    def scrape_tweets(self, query, max_results=100, start_time="2025-01-01T00:00:00Z"):
        """
        Scrape tweets based on a search query
        
        Args:
            query: Search query string
            max_results: Maximum number of tweets to retrieve (10-100 per request)
            start_time: Start time in ISO format (default: 2025-01-01)
        
        Returns:
            list: List of tweet dictionaries
        """
        tweets_data = []
        
        try:
            # Search recent tweets with the query
            # Note: For 2025 data, this assumes the code runs in or after 2025
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang', 'entities'],
                user_fields=['username', 'name', 'verified', 'public_metrics'],
                expansions=['author_id'],
                start_time=start_time
            )
            
            # Create a dictionary to map user IDs to user data
            users = {}
            if tweets.includes and 'users' in tweets.includes:
                for user in tweets.includes['users']:
                    users[user.id] = user
            
            # Process tweets
            if tweets.data:
                for tweet in tweets.data:
                    # Get author information
                    author = users.get(tweet.author_id)
                    
                    tweet_dict = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'author_id': tweet.author_id,
                        'author_username': author.username if author else None,
                        'author_name': author.name if author else None,
                        'author_verified': author.verified if author else None,
                        'language': tweet.lang if hasattr(tweet, 'lang') else None,
                        'retweet_count': tweet.public_metrics['retweet_count'] if tweet.public_metrics else 0,
                        'reply_count': tweet.public_metrics['reply_count'] if tweet.public_metrics else 0,
                        'like_count': tweet.public_metrics['like_count'] if tweet.public_metrics else 0,
                        'quote_count': tweet.public_metrics['quote_count'] if tweet.public_metrics else 0,
                        'query': query
                    }
                    tweets_data.append(tweet_dict)
                    
            print(f"Scraped {len(tweets_data)} tweets for query: {query[:50]}...")
            
        except tweepy.TweepyException as e:
            print(f"Error scraping tweets for query '{query}': {e}")
        
        return tweets_data
    
    def scrape_all_queries(self, max_results_per_query=100):
        """
        Scrape tweets for all predefined queries
        
        Args:
            max_results_per_query: Maximum results per query (default: 100)
        
        Returns:
            pd.DataFrame: DataFrame containing all scraped tweets
        """
        all_tweets = []
        queries = self.get_search_queries()
        
        print(f"Starting to scrape {len(queries)} queries...")
        
        for i, query in enumerate(queries, 1):
            print(f"\nProcessing query {i}/{len(queries)}")
            tweets = self.scrape_tweets(query, max_results=max_results_per_query)
            all_tweets.extend(tweets)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_tweets)
        
        if not df.empty:
            # Sort by engagement (likes + retweets + replies)
            df['engagement_score'] = df['like_count'] + df['retweet_count'] * 2 + df['reply_count']
            df = df.sort_values('engagement_score', ascending=False)
            
            print(f"\nTotal tweets scraped: {len(df)}")
            print(f"Date range: {df['created_at'].min()} to {df['created_at'].max()}")
        else:
            print("\nNo tweets found.")
        
        return df
    
    def save_to_csv(self, df, filename='twitter_data_tweepy_2025.csv'):
        """
        Save scraped data to CSV file
        
        Args:
            df: DataFrame with tweet data
            filename: Output filename
        """
        if not df.empty:
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"\nData saved to {filename}")
        else:
            print("No data to save.")
    
    def save_to_json(self, df, filename='twitter_data_tweepy_2025.json'):
        """
        Save scraped data to JSON file
        
        Args:
            df: DataFrame with tweet data
            filename: Output filename
        """
        if not df.empty:
            df.to_json(filename, orient='records', force_ascii=False, indent=2)
            print(f"Data saved to {filename}")
        else:
            print("No data to save.")


def main():
    """
    Main function to run the Twitter scraper
    """
    print("=" * 60)
    print("Twitter Scraper using Tweepy")
    print("Scraping domestic and international situation data for 2025")
    print("=" * 60)
    
    # Check for bearer token
    bearer_token = os.environ.get('TWITTER_BEARER_TOKEN')
    
    if not bearer_token:
        print("\nERROR: TWITTER_BEARER_TOKEN environment variable not set.")
        print("\nTo use this scraper, you need to:")
        print("1. Create a Twitter Developer account at https://developer.twitter.com/")
        print("2. Create a project and app")
        print("3. Get your Bearer Token from the app settings")
        print("4. Set the environment variable:")
        print("   export TWITTER_BEARER_TOKEN='your_bearer_token_here'")
        print("\nAlternatively, you can pass the token directly when creating the scraper:")
        print("   scraper = TwitterScraperTweepy(bearer_token='your_token')")
        return
    
    try:
        # Initialize scraper
        scraper = TwitterScraperTweepy()
        
        # Scrape tweets
        df = scraper.scrape_all_queries(max_results_per_query=100)
        
        if not df.empty:
            # Save results
            scraper.save_to_csv(df)
            scraper.save_to_json(df)
            
            # Display summary statistics
            print("\n" + "=" * 60)
            print("Summary Statistics")
            print("=" * 60)
            print(f"Total tweets: {len(df)}")
            print(f"\nTop 5 languages:")
            print(df['language'].value_counts().head())
            print(f"\nTop 5 most engaging tweets:")
            print(df[['text', 'like_count', 'retweet_count', 'author_username']].head())
        
    except Exception as e:
        print(f"\nError running scraper: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
