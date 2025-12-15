#!/usr/bin/env python3
"""
Twitter Scraper using snscrape Library
Scrapes Twitter data about domestic and international situations
Focus on topics related to China, Japan, Korea, US, EU
Outputs JSONL for LLM training

Features:
- Streams results to TWO single JSONL files (append mode):
  - raw.jsonl: full metadata
  - text.jsonl: minimal training-friendly schema
- Cross-run deduplication:
  - Loads existing IDs from raw.jsonl at startup and skips duplicates
- Preserves partial progress even if interrupted (flush after each write)
"""

import snscrape.modules.twitter as sntwitter
import pandas as pd
import json
import os
from typing import Optional, Set


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

    def _build_search_query(self, query, start_date, end_date):
        # snscrape uses Twitter advanced search operators inside the query string.
        if end_date:
            return f"{query} since:{start_date} until:{end_date}"
        return f"{query} since:{start_date}"

    @staticmethod
    def _to_text_record(raw_record: dict) -> dict:
        return {
            "id": raw_record.get("id"),
            "text": raw_record.get("text", ""),
            "date": raw_record.get("date"),
            "lang": raw_record.get("language"),
            "query": raw_record.get("query"),
            "source": raw_record.get("source", "snscrape"),
            "url": raw_record.get("url"),
        }

    @staticmethod
    def load_existing_ids(jsonl_path: str) -> Set[int]:
        """
        Load existing tweet IDs from an existing JSONL file.
        Used for cross-run deduplication.

        Notes:
        - Expects each line is a JSON object with an `id` field.
        - Skips malformed lines.
        """
        seen: Set[int] = set()
        if not jsonl_path or not os.path.exists(jsonl_path):
            return seen

        total = 0
        bad = 0
        with open(jsonl_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                total += 1
                try:
                    obj = json.loads(line)
                    tid = obj.get("id")
                    if tid is None:
                        continue
                    # Ensure int-ish (some tools may store as str)
                    tid = int(tid)
                    seen.add(tid)
                except Exception:
                    bad += 1
                    continue

        print(f"Loaded {len(seen)} existing ids from {jsonl_path} (lines={total}, bad_lines={bad})")
        return seen

    def scrape_and_append_jsonl(
        self,
        query: str,
        raw_fp,
        text_fp,
        max_results: int = 200,
        start_date: str = "2025-01-01",
        end_date: Optional[str] = None,
        seen_ids: Optional[Set[int]] = None,
    ):
        """
        Scrape tweets for a query and append each record to open JSONL file handles.
        Writes BOTH raw and text records per tweet.

        Returns:
            (tweets_data, seen_ids)
        """
        if seen_ids is None:
            seen_ids = set()

        tweets_data = []
        search_query = self._build_search_query(query, start_date, end_date)
        print(f"Scraping query: {search_query}")

        count_written = 0
        count_skipped_dup = 0
        try:
            for tweet in sntwitter.TwitterSearchScraper(search_query).get_items():
                if count_written >= max_results:
                    break

                tweet_id = getattr(tweet, "id", None)
                if tweet_id is not None:
                    try:
                        tweet_id = int(tweet_id)
                    except Exception:
                        tweet_id = None

                if tweet_id is not None and tweet_id in seen_ids:
                    count_skipped_dup += 1
                    continue

                raw_record = {
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

                # Fallback language filter: keep only zh/en (allow None)
                lang = raw_record.get("language")
                if lang not in (None, "zh", "en"):
                    continue

                # Write raw + text (streaming append)
                raw_fp.write(json.dumps(raw_record, ensure_ascii=False) + "\n")
                text_fp.write(json.dumps(self._to_text_record(raw_record), ensure_ascii=False) + "\n")

                raw_fp.flush()
                text_fp.flush()

                if tweet_id is not None:
                    seen_ids.add(tweet_id)

                tweets_data.append(raw_record)
                count_written += 1

            print(f"Appended {count_written} tweets (skipped duplicates: {count_skipped_dup})")
        except Exception as e:
            print(f"Error scraping tweets for query '{query}': {e}")

        return tweets_data, seen_ids

    def scrape_all_queries_streaming(
        self,
        raw_jsonl: str = "twitter_snscrape_raw.jsonl",
        text_jsonl: str = "twitter_snscrape_text.jsonl",
        max_results_per_query: int = 200,
        start_date: str = "2025-01-01",
        end_date: Optional[str] = None,
        dedup_from: str = "raw",  # "raw" or "text"
    ):
        """
        Scrape all queries and append results to two JSONL files as we go.
        Cross-run dedup is done by loading existing ids from raw_jsonl (default).

        Returns:
            DataFrame of records collected in THIS run (for summary only).
        """
        queries = self.get_search_queries()

        # Cross-run dedup: load ids from existing file
        id_source = raw_jsonl if dedup_from == "raw" else text_jsonl
        seen_ids = self.load_existing_ids(id_source)

        all_tweets = []

        print(f"\n{'=' * 60}")
        print(f"Starting to scrape {len(queries)} queries (streaming JSONL)...")
        print(f"Date range: {start_date} -> {end_date or 'now'}")
        print(f"Max results per query: {max_results_per_query}")
        print(f"RAW output:  {os.path.abspath(raw_jsonl)}")
        print(f"TEXT output: {os.path.abspath(text_jsonl)}")
        print(f"Dedup: load existing ids from: {os.path.abspath(id_source)}")
        print(f"{'=' * 60}\n")

        # append mode: keep existing files and continue (dedup will prevent duplicates)
        with open(raw_jsonl, "a", encoding="utf-8") as raw_fp, open(text_jsonl, "a", encoding="utf-8") as text_fp:
            for i, q in enumerate(queries, 1):
                print(f"\nQuery {i}/{len(queries)}: {q['description']}")
                tweets, seen_ids = self.scrape_and_append_jsonl(
                    q["query"],
                    raw_fp,
                    text_fp,
                    max_results=max_results_per_query,
                    start_date=start_date,
                    end_date=end_date,
                    seen_ids=seen_ids,
                )
                all_tweets.extend(tweets)
                print(f"Total tweets collected in this run so far: {len(all_tweets)}")

        df = pd.DataFrame(all_tweets)
        if df.empty:
            print("\nNo tweets found in this run.")
            return df

        df["engagement_score"] = (
            df.get("like_count", 0)
            + df.get("retweet_count", 0) * 2
            + df.get("reply_count", 0)
            + df.get("quote_count", 0)
        )
        df = df.sort_values("engagement_score", ascending=False)
        df = df.drop_duplicates(subset=["id"], keep="first")
        print(f"\nTotal unique tweets collected in this run: {len(df)}")
        return df


def main():
    scraper = TwitterScraperSnscrape()
    scraper.scrape_all_queries_streaming(
        raw_jsonl="twitter_snscrape_raw.jsonl",
        text_jsonl="twitter_snscrape_text.jsonl",
        max_results_per_query=200,
        start_date="2025-01-01",
        end_date=None,
        dedup_from="raw",
    )


if __name__ == "__main__":
    main()