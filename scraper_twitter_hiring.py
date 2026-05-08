#!/usr/bin/env python3
"""
Twitter/X Web3 Hiring Scraper for web3-hiring-report repo
Pulls founder hiring tweets and generates JSON in expected format.

Searches for tweets with keywords like "hiring", "looking for" from founders/web3 accounts
within the last 30 hours.
"""

import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add the parent workspace to path so we can import bird_x
WORKSPACE = Path(__file__).parent.parent
BIRD_X_PATH = WORKSPACE / "agents-experiment" / "skills" / "last30days-official" / "scripts"
sys.path.insert(0, str(BIRD_X_PATH))

from pathlib import Path
import subprocess
from last30days.bird_x import search_x, is_bird_installed, get_bird_status
from last30days.env import load_from_env_file

def setup_credentials():
    """Load Twitter credentials from .env or cookies."""
    env_path = Path(__file__).parent.parent.parent / "agents-experiment" / "geopolitical-agent" / ".twitter_cookies.env"
    
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

def is_founder_or_web3_account(bio: str, text: str) -> bool:
    """Check if account appears to be a founder/web3 account.
    
    RELAXED FILTER: Now returns True for ANY account posting hiring content,
    not just verified founders. This captures more opportunities.
    """
    bio_lower = bio.lower()
    text_lower = text.lower()
    
    # Original strict founder/web3 keywords
    founder_keywords = ['founder', 'co-founder', 'cofounder', 'ceo', 'cfo', 'cto', 'cmo', 
                       'vp', 'head of', 'building', 'creator', 'eth researcher',
                       'solana', 'arbitrum', 'oplabs', 'defi', 'dao', 'protocol']
    web3_keywords = ['web3', 'crypto', 'blockchain', 'ethereum', 'btc', 'token', 
                    'smart contract', 'nft', 'metaverse']
    
    bio_text = (bio + " " + text).lower()
    
    has_founder = any(kw in bio_text for kw in founder_keywords)
    has_web3 = any(kw in bio_text for kw in web3_keywords)
    
    # RELAXED: If posting about hiring, treat as valid regardless of account type
    # This captures hiring posts from job boards, recruiters, and non-founder accounts
    if is_hiring_tweet(text):
        return True
    
    return has_founder or has_web3

def is_hiring_tweet(text: str) -> bool:
    """Check if tweet is about hiring."""
    text_lower = text.lower()
    hiring_keywords = ['hiring', 'looking for', 'join our team', 'we\'re looking',
                      'open to applications', 'applied?', 'apply now', 'send cv']
    
    return any(kw in text_lower for kw in hiring_keywords)

def get_tweet_date(created_at: str):
    """Parse Twitter's created_at format and return date."""
    try:
        if len(created_at) > 10 and created_at[10] == "T":
            # ISO format with timezone
            dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            # Twitter format: "Thu Apr 30 09:45:54 +0000 2026"
            dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
        
        # Convert to UTC if needed
        if dt.tzinfo:
            dt = dt.astimezone(timezone.utc)
        
        return dt.date()
    except Exception as e:
        print(f"  Error parsing date {created_at}: {e}")
        return None

def scrape_hiring_tweets(days_ago=2):
    """Scrape hiring-related tweets from the last N days."""
    print("=" * 60)
    print("🔍 Web3 Hiring Scraper - Starting")
    print("=" * 60)
    
    creds = setup_credentials()
    if not creds:
        return None
    
    auth_token, ct0 = creds
    
    # Check bird is installed
    if not is_bird_installed():
        print("❌ Bird search is not installed")
        return None
    
    print(f"✓ Twitter credentials loaded from {auth_token[:16]}...")
    
    # Build query for hiring tweets - use since: filter for last N days
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    # Multi-query approach to find hiring tweets
    SEARCH_QUERIES = [
        "hiring web3 founder",
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
        
        # Use bird-search with since: filter
        query_with_date = f"{query} since:{cutoff}"
        print(f"   Query: {query_with_date}")
        
        try:
            response = search_x(query_with_date, today, today)
            
            if "error" in response and "items" not in response:
                print(f"   Error from bird-search: {response['error']}")
                continue
            
            # Extract items from response (Bird returns list or {tweets: [...]})
            raw_items = response if isinstance(response, list) else response.get("items", response.get("tweets", []))
            
            for item in raw_items[:3]:  # Limit to first 3 per query
                try:
                    tweet_id = item.get("id") or item.get("tweetId")
                    
                    # Get username (Bird might use author.username or user.screen_name)
                    author = item.get("author", {}) or item.get("user", {})
                    username = author.get("username") or author.get("screen_name", "")
                    
                    if not username:
                        continue
                    
                    name = item.get("authorName") or item.get("name", "")
                    text = item.get("text", "")[:500]  # Limit length
                    bio = ""
                    created_at = item.get("createdAt") or item.get("created_at", "")
                    
                    date = get_tweet_date(created_at)
                    twitter_url = item.get("permanent_url") or f"https://x.com/{username}/status/{tweet_id}"
                    
                    # Skip non-founding accounts
                    if not is_founder_or_web3_account(bio, text):
                        print(f"   - Skipping (not a founder/web3 account): {name}")
                        continue
                    
                    # Must be about hiring
                    if not is_hiring_tweet(text):
                        print(f"   - Skipping (not hiring-related): {name[:30]}...")
                        continue
                    
                    # Check if within last 30 hours
                    if date:
                        tweet_time = datetime(date.year, date.month, date.day, 
                                           tzinfo=timezone.utc)
                        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=30)
                        
                        if tweet_time < cutoff_time:
                            print(f"   - Skipping (older than 30h): {created_at[:20]}")
                            continue
                    
                    # Parse job title from text
                    job_title = None
                    for kw in ["CMO", "growth", "marketing", "product", "sales", 
                               "head of", "vp ", "director "]:
                        if kw.lower() in text.lower():
                            job_title = kw.strip()
                            break
                    
                    company = item.get("authorName") or name or username
                    
                    tweet_data = {
                        "username": username,
                        "name": name,
                        "bio": bio,
                        "text": text,
                        "job_title": job_title,
                        "company": company.lower(),
                        "tweet_id": tweet_id,
                        "created_at": created_at,
                        "twitter_url": twitter_url,
                    }
                    
                    all_tweets.append(tweet_data)
                    
                    # Determine if it's marketing-related (for filtering in generate_report.py)
                    text_lower = text.lower()
                    is_marketing = any(kw in text_lower for kw in [
                        'cmo', 'marketing', 'head of marketing', 'growth',
                        'product marketing', 'vp marketing'
                    ])
                    
                    if is_marketing:
                        marketing_results.append(tweet_data)
                    else:
                        results.append(tweet_data)
                    
                    count += 1
                    print(f"   ✓ Found hiring post: {name} @ {company}")
                    
                except Exception as e:
                    print(f"   - Error processing tweet: {e}")
                    continue
                    
        except Exception as e:
            print(f"   Error for query '{query}': {e}")
            continue
    
    print(f"\n{'='*60}")
    print(f"✓ Total hiring tweets found: {len(all_tweets)}")
    print(f"  - General: {len(results)}")
    print(f"  - Marketing: {len(marketing_results)}")
    print('='*60)
    
    # Build output JSON
    output = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated": datetime.now(timezone.utc).isoformat(),
        "count": len(results),
        "marketing_count": len(marketing_results),
        "results": results,
        "marketing_results": marketing_results,
        "all_tweets": all_tweets,
    }
    
    # Save to file
    output_file = Path(__file__).parent / f"web3_hiring_posts_{datetime.now().strftime('%Y-%m-%d')}.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Saved raw data to: {output_file}")
    return output

if __name__ == "__main__":
    scrape_hiring_tweets(days_ago=1)  # Search last 1 day for recent tweets