#!/usr/bin/env python3
"""
Daily Web3 Hiring Report Runner
Automatically fetches fresh hiring tweets and generates the HTML report.

This script:
1. Uses Twitter credentials from .twitter_cookies.env
2. Calls the bird_x scraper to get fresh hiring tweets
3. Generates the HTML report for today's date
4. Can be run manually or scheduled via cron job
"""

import sys
import os
from pathlib import Path

# Add last30days skill to path
WORKSPACE = Path(__file__).parent.parent
SKILLS_PATH = WORKSPACE / "agents-experiment" / "skills" / "last30days-official" / "scripts"
sys.path.insert(0, str(SKILLS_PATH))

from pathlib import Path as LibPath
from last30days.bird_x import search_x, is_bird_installed, get_bird_status
from last30days.env import load_from_env_file

def setup_credentials():
    """Load Twitter credentials from geopolitical-agent's cookies.env"""
    env_path = WORKSPACE / "agents-experiment" / "geopolitical-agent" / ".twitter_cookies.env"
    
    if not env_path.exists():
        print("❌ No Twitter credentials found at:", env_path)
        return None, None
    
    creds = {}
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                creds[key.strip()] = value.strip().strip('"')
    
    return creds.get("AUTH_TOKEN"), creds.get("CT0")

def scrape_tweets():
    """Scrape hiring tweets using bird_x"""
    print("=" * 60)
    print("🔍 Web3 Hiring Daily Report - Starting")
    print("=" * 60)
    
    auth_token, ct0 = setup_credentials()
    if not auth_token or not ct0:
        return None
    
    # Check bird is installed
    if not is_bird_installed():
        print("❌ Bird search is not installed or available")
        return None
    
    print(f"✓ Twitter credentials loaded from {env_path}")
    
    today = "2026-05-04"  # Current date
    cutoff_date = "2026-05-03"  # Yesterday for since: filter
    
    # Search queries for hiring tweets
    SEARCH_QUERIES = [
        "hiring founder web3",
        "looking for marketing founder", 
        "hiring cmo crypto",
        "join our team web3 founder",
        "open positions web3 startup",
        "we're hiring defi",
        "hiring growth web3",
    ]
    
    all_tweets = []
    results = []
    marketing_results = []
    count = 0
    
    for query in SEARCH_QUERIES:
        print(f"\n🔍 Searching: {query}")
        
        # Use bird-search with date filter
        query_with_date = f"{query} since:{cutoff_date}"
        print(f"   Query: {query_with_date}")
        
        try:
            response = search_x(query_with_date, today, today)
            
            if "error" in response and "items" not in response:
                print(f"   Error from bird-search: {response.get('error', 'Unknown error')}")
                continue
            
            # Extract items from response
            raw_items = response if isinstance(response, list) else response.get("items", [])
            
            for item in raw_items[:3]:  # Limit to first 3 per query
                try:
                    tweet_id = item.get("id") or item.get("tweetId")
                    
                    author = item.get("author", {}) or item.get("user", {})
                    username = author.get("username") or author.get("screen_name", "")
                    
                    if not username:
                        continue
                    
                    name = item.get("authorName") or item.get("name", "")
                    text = (item.get("text", "") or "").strip()[:500]  # Limit length
                    bio = item.get("profile_bio") or item.get("description") or ""
                    created_at = item.get("createdAt") or item.get("created_at", "")
                    
                    # Get company/author name
                    company = item.get("authorName") or name or username
                    
                    # Skip non-hiring tweets
                    text_lower = text.lower()
                    if not any(kw in text_lower for kw in ['hiring', 'looking for', 'job']):
                        continue
                    
                    tweet_data = {
                        "username": username,
                        "name": name,
                        "bio": bio,
                        "text": text,
                        "job_title": None,
                        "company": company.lower(),
                        "tweet_id": tweet_id,
                        "created_at": created_at,
                    }
                    
                    all_tweets.append(tweet_data)
                    count += 1
                    print(f"   ✓ Found hiring post: {name} @ {company}")
                
                except Exception as e:
                    print(f"   - Error processing tweet: {e}")
                    continue
                    
        except Exception as e:
            print(f"   Error for query '{query}': {e}")
            continue
    
    # Separate marketing and general results
    for tweet in all_tweets:
        text_lower = tweet['text'].lower()
        is_marketing = any(kw in text_lower for kw in [
            'cmo', 'marketing', 'head of marketing', 'growth',
            'product marketing', 'vp marketing'
        ])
        
        if is_marketing:
            marketing_results.append(tweet)
        else:
            results.append(tweet)
    
    # Build output JSON
    date_str = "2026-05-04"  # Today's date
    
    output = {
        "date": date_str,
        "generated": None,  # Will be set by generate_report.py
        "count": len(results),
        "marketing_count": len(marketing_results),
        "results": results,
        "marketing_results": marketing_results,
        "all_tweets": all_tweets,
    }
    
    # Save to file
    output_file = Path(__file__).parent / f"web3_hiring_posts_{date_str}.json"
    with open(output_file, 'w') as f:
        import json
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✓ Total hiring tweets found: {count}")
    print(f"  - General jobs: {len(results)}")
    print(f"  - Marketing: {len(marketing_results)}")
    print('='*60)
    
    return output

def main():
    """Main entry point"""
    scrape_tweets()
    print("\n✅ Scraping complete! Run generate_report.py to create HTML.")

if __name__ == "__main__":
    main()
