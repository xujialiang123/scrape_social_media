#!/usr/bin/env python3
"""
Example script demonstrating how to use both Twitter scrapers
This shows basic usage and customization options
"""

import os
import sys

# Example 1: Using tweepy scraper
def example_tweepy():
    """Example using tweepy scraper"""
    print("\n" + "="*60)
    print("Example 1: Using Tweepy Scraper")
    print("="*60)
    
    from twitter_scraper_tweepy import TwitterScraperTweepy
    
    # Check if bearer token is available
    if not os.environ.get('TWITTER_BEARER_TOKEN'):
        print("⚠️  TWITTER_BEARER_TOKEN not set. Skipping tweepy example.")
        print("Set it with: export TWITTER_BEARER_TOKEN='your_token'")
        return
    
    try:
        # Initialize scraper
        scraper = TwitterScraperTweepy()
        
        # Option 1: Scrape with custom query
        print("\nScraping custom query...")
        tweets = scraper.scrape_tweets(
            query="China economy -is:retweet lang:en",
            max_results=10
        )
        print(f"Found {len(tweets)} tweets")
        
        # Option 2: Scrape all predefined queries
        print("\nScraping all predefined queries...")
        df = scraper.scrape_all_queries(max_results_per_query=50)
        
        if not df.empty:
            print(f"\nTotal tweets: {len(df)}")
            print("\nTop 5 most engaging tweets:")
            print(df[['text', 'engagement_score', 'author_username']].head())
            
            # Save results
            scraper.save_to_csv(df, 'example_tweepy_results.csv')
            
    except Exception as e:
        print(f"Error: {e}")


# Example 2: Using snscrape scraper
def example_snscrape():
    """Example using snscrape scraper"""
    print("\n" + "="*60)
    print("Example 2: Using snscrape Scraper")
    print("="*60)
    
    from twitter_scraper_snscrape import TwitterScraperSnscrape
    
    try:
        # Initialize scraper
        scraper = TwitterScraperSnscrape()
        
        # Option 1: Scrape with custom query
        print("\nScraping custom query...")
        tweets = scraper.scrape_tweets(
            query="Japan politics",
            max_results=10,
            start_date="2025-01-01"
        )
        print(f"Found {len(tweets)} tweets")
        
        # Option 2: Scrape all predefined queries
        print("\nScraping all predefined queries...")
        df = scraper.scrape_all_queries(
            max_results_per_query=50,
            start_date="2025-01-01"
        )
        
        if not df.empty:
            print(f"\nTotal tweets: {len(df)}")
            
            # Get statistics
            stats = scraper.get_statistics(df)
            print("\nStatistics:")
            import json
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            
            # Get top tweets
            top_tweets = scraper.get_top_tweets(df, n=5)
            print("\nTop 5 trending tweets:")
            for i, (_, tweet) in enumerate(top_tweets.iterrows(), 1):
                print(f"\n{i}. @{tweet['username']} - Engagement: {tweet['engagement_score']}")
                print(f"   {tweet['text'][:100]}...")
            
            # Save results
            scraper.save_to_csv(df, 'example_snscrape_results.csv')
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


# Example 3: Custom implementation
def example_custom():
    """Example with custom implementation"""
    print("\n" + "="*60)
    print("Example 3: Custom Implementation")
    print("="*60)
    
    from twitter_scraper_snscrape import TwitterScraperSnscrape
    
    try:
        scraper = TwitterScraperSnscrape()
        
        # Define custom queries for specific topics
        custom_queries = [
            "中美关系",  # China-US relations
            "日本经济",  # Japan economy
            "欧洲局势",  # Europe situation
        ]
        
        all_tweets = []
        for query in custom_queries:
            print(f"\nScraping: {query}")
            tweets = scraper.scrape_tweets(
                query=query,
                max_results=20,
                start_date="2025-01-01"
            )
            all_tweets.extend(tweets)
        
        if all_tweets:
            import pandas as pd
            df = pd.DataFrame(all_tweets)
            
            # Calculate engagement score
            df['engagement_score'] = (
                df['like_count'] + 
                df['retweet_count'] * 2 + 
                df['reply_count']
            )
            
            # Sort by engagement
            df = df.sort_values('engagement_score', ascending=False)
            
            print(f"\nTotal tweets collected: {len(df)}")
            print(f"Most engaging tweet has {df['engagement_score'].max()} engagement points")
            
            # Save
            df.to_csv('custom_results.csv', index=False, encoding='utf-8-sig')
            print("Results saved to custom_results.csv")
            
    except Exception as e:
        print(f"Error: {e}")


def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("Twitter Scraper Examples")
    print("="*60)
    print("\nThis script demonstrates different ways to use the scrapers.")
    print("You can run individual examples or all of them.")
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        example = sys.argv[1]
        if example == "tweepy":
            example_tweepy()
        elif example == "snscrape":
            example_snscrape()
        elif example == "custom":
            example_custom()
        else:
            print(f"Unknown example: {example}")
            print("Usage: python examples.py [tweepy|snscrape|custom]")
    else:
        # Run all examples
        print("\nRunning all examples...")
        example_tweepy()
        example_snscrape()
        example_custom()
    
    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60)


if __name__ == "__main__":
    main()
