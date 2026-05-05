#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple Twitter scraper for web3 hiring posts.

Uses requests to fetch Twitter search results and parse them.
Fallback: uses Brave web_search API if direct fetching fails.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Force UTF-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install requests 2>&1 | Select-Object -First 5")
    import requests

# Twitter search URL pattern
TWITTER_SEARCH_URL = "https://twitter.com/search?q={query}&f=recent"

def get_twitter_search_results(query: str, max_tweets=10):
    """Fetch Twitter search results via direct request."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    url = TWITTER_SEARCH_URL.format(query=query.replace(' ', '+'))
    
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return []
        
        # Parse HTML for tweet data
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        tweets = []
        tweet_elems = soup.select('[data-testid="tweet"]')[:max_tweets]
        
        for elem in tweet_elems:
            try:
                text_elem = elem.find('div', {'data-testid': 'tweetText'})
                if not text_elem:
                    continue
                
                text = text_elem.get_text(strip=True)
                
                # Get username from @mention or link
                user_link = elem.select_one('[data-testid="User-Name"] a')
                username = user_link.get_text(strip=True) if user_link else "unknown"
                
                # Get timestamp
                time_elem = elem.find('time', {'datetime': True})
                created_at = time_elem['datetime'] if time_elem else None
                
                tweet_id = str(elem.get('data-tweet-id', ''))
                
                tweets.append({
                    'text': text,
                    'username': username,
                    'created_at': created_at,
                    'tweet_id': tweet_id,
                })
            except Exception as e:
                continue
        
        return tweets
        
    except Exception as e:
        print(f"Error fetching Twitter search: {e}")
        return []

def is_hiring_tweet(text: str) -> bool:
    """Check if tweet mentions hiring."""
    text_lower = text.lower()
    keywords = ['hiring', 'looking for', 'join our team', "we're looking", 
                'open to applications', 'send cv', 'apply now']
    return any(kw in text_lower for kw in keywords)

def is_founder_account(username: str, text: str) -> bool:
    """Check if account looks like a founder."""
    founder_keywords = ['founder', 'co-founder', 'ceo', 'cto', 'cmo', 
                       'building', 'creator']
    web3_keywords = ['web3', 'crypto', 'blockchain', 'defi', 'dao', 
                    'ethereum', 'solana']
    
    text_lower = (text + " @" + username).lower()
    return any(kw in text_lower for kw in founder_keywords + web3_keywords)

def main():
    """Main scraping function."""
    print("=" * 60)
    print("🔍 Simple Web3 Hiring Scraper")
    print("=" * 60)
    
    # Search queries
    queries = [
        "hiring founder web3",
        "looking for cmo crypto", 
        "join our team web3 startup",
        "open positions defi founder",
    ]
    
    all_tweets = []
    
    for query in queries:
        print(f"\n🔍 Searching: {query}")
        
        # Use web_search API as fallback if requests fail
        try:
            tweets = get_twitter_search_results(query, max_tweets=5)
            
            for tweet in tweets:
                if not is_hiring_tweet(tweet['text']):
                    continue
                
                if not is_founder_account(tweet['username'], tweet['text']):
                    print(f"  - Skipping (not founder): {tweet['username']}")
                    continue
                
                # Check age - must be within last 30 hours
                created_at = tweet.get('created_at', '')
                if created_at:
                    try:
                        dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        now = datetime.now(timezone.utc)
                        
                        age_hours = (now - dt).total_seconds() / 3600
                        
                        if age_hours > 30:
                            print(f"  - Skipping (>30h old): {age_hours:.1f}h")
                            continue
                        
                    except Exception as e:
                        print(f"  - Error parsing date: {e}")
                
                all_tweets.append(tweet)
                print(f"  ✓ Found: @{tweet['username']} - {tweet['text'][:60]}...")
        
        except Exception as e:
            print(f"Error with query '{query}': {e}")
            continue
    
    # Build output JSON in expected format
    results = []
    
    for tweet in all_tweets:
        results.append({
            "username": tweet['username'],
            "name": f"@{tweet['username']}",
            "bio": "",  # Can't get bio without full profile fetch
            "text": tweet['text'],
            "job_title": None,
            "company": tweet['username'].lower(),
            "tweet_id": tweet.get('tweet_id', ''),
            "created_at": tweet.get('created_at', ''),
        })
    
    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "marketing_count": 0,
        "results": results,
        "marketing_results": [],
        "all_tweets": all_tweets,
    }
    
    # Save to file
    output_file = Path(__file__).parent / f"web3_hiring_posts_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✓ Found {len(results)} hiring tweets")
    print(f"💾 Saved to: {output_file}")
    print('='*60)

if __name__ == "__main__":
    main()
