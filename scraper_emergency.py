#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency scraper for web3 hiring tweets.
Runs bird-search directly with broader queries and proper encoding.
"""
import json
import os
import sys
import subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Force UTF-8
os.environ["PYTHONIOENCODING"] = "utf-8"
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Paths
REPO = Path(__file__).parent
WORKSPACE = REPO.parent
BIRD_MJS = WORKSPACE / "agents-experiment" / "skills" / "last30days-official" / "scripts" / "last30days" / "vendor" / "bird-search" / "bird-search.mjs"
ENV_PATH = WORKSPACE / "agents-experiment" / "geopolitical-agent" / ".twitter_cookies.env"

# Load credentials
def load_creds():
    creds = {}
    if ENV_PATH.exists():
        with open(ENV_PATH, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    creds[k.strip()] = v.strip().strip('"')
    return creds

creds = load_creds()

# Broader queries - cast a wider net
QUERIES = [
    "hiring web3",
    "hiring crypto",
    "hiring blockchain",
    "hiring defi",
    "hiring nft",
    "hiring dao",
    "hiring ethereum",
    "hiring solana",
    "hiring token",
    "hiring metaverse",
    "hiring web3 marketing",
    "hiring crypto growth",
    "looking for web3",
    "looking for crypto",
    "web3 job opening",
    "crypto job opening",
    "blockchain job opening",
    "defi hiring",
    "web3 team join",
    "crypto startup hiring",
]

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
YESTERDAY = (datetime.now(timezone.utc) - timedelta(days=2)).strftime("%Y-%m-%d")

def run_bird(query):
    """Run bird-search with proper encoding."""
    full_query = f"{query} since:{YESTERDAY}"
    cmd = [
        "node", str(BIRD_MJS),
        full_query,
        "--count", "30",
        "--json",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=30,
            env={**os.environ, **creds},
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        if isinstance(data, list):
            return data
        return data.get("items", data.get("tweets", []))
    except Exception as e:
        print(f"  Error: {e}")
        return []

def is_hiring(text):
    t = text.lower()
    return any(kw in t for kw in [
        'hiring', 'looking for', 'join our team', 'we are hiring',
        'open position', 'apply now', 'send cv', 'now hiring',
        'we are looking', 'seeking', 'recruiting', 'career opportunity',
        'job opening', 'role opening',
    ])

def is_web3(text, bio=""):
    t = (text + " " + bio).lower()
    return any(kw in t for kw in [
        'web3', 'crypto', 'blockchain', 'defi', 'nft', 'dao',
        'ethereum', 'solana', 'token', 'chain', 'wallet',
        'decentralized', 'smart contract', 'layer 2', 'layer2',
        'web 3', 'metaverse', 'gaming', 'gamefi',
    ])

# Collect tweets
all_tweets = []
seen_ids = set()

for i, query in enumerate(QUERIES):
    print(f"[{i+1}/{len(QUERIES)}] Searching: {query}")
    items = run_bird(query)
    print(f"  Got {len(items)} raw results")
    
    for item in items:
        try:
            tid = str(item.get("id", item.get("tweetId", "")))
            if not tid or tid in seen_ids:
                continue
            seen_ids.add(tid)
            
            text = (item.get("text", "") or "").strip()
            if not text or len(text) < 20:
                continue
            
            # Get author info
            author = item.get("author", item.get("user", {})) or {}
            username = author.get("username", author.get("screen_name", ""))
            name = item.get("authorName", item.get("name", ""))
            bio = item.get("profile_bio", item.get("description", ""))
            created_at = item.get("createdAt", item.get("created_at", ""))
            likes = item.get("likeCount", item.get("like_count", 0))
            retweets = item.get("retweetCount", item.get("retweet_count", 0))
            
            if not username:
                continue
            
            # Filter: must be hiring AND web3-related
            if not is_hiring(text):
                continue
            if not is_web3(text, bio):
                continue
            
            # Extract job title
            job_title = None
            for kw in ["CMO", "Head of Marketing", "Head of Growth", "CTO", "CEO", 
                       "Product Manager", "Engineer", "Developer", "Designer",
                       "Growth Lead", "Marketing Lead", "Community Manager"]:
                if kw.lower() in text.lower():
                    job_title = kw
                    break
            
            url = item.get("permanent_url", f"https://x.com/{username}/status/{tid}")
            
            tweet = {
                "username": username,
                "name": name or username,
                "bio": bio or "",
                "text": text[:500],
                "job_title": job_title,
                "company": (name or username).lower(),
                "tweet_id": tid,
                "created_at": created_at,
                "twitter_url": url,
                "likes": likes,
                "retweets": retweets,
            }
            all_tweets.append(tweet)
            print(f"  ✓ @{username}: {text[:80]}...")
        except Exception as e:
            continue
    
    if len(all_tweets) >= 15:
        print(f"\nReached 15 tweets, stopping early")
        break

# Build output
output = {
    "date": TODAY,
    "generated": datetime.now(timezone.utc).isoformat(),
    "count": len(all_tweets),
    "marketing_count": sum(1 for t in all_tweets if any(kw in t['text'].lower() for kw in ['marketing', 'cmo', 'growth', 'brand'])),
    "results": all_tweets,
    "marketing_results": [t for t in all_tweets if any(kw in t['text'].lower() for kw in ['marketing', 'cmo', 'growth', 'brand'])],
    "all_tweets": all_tweets,
}

out_file = REPO / f"web3_hiring_posts_{TODAY}.json"
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"TOTAL: {len(all_tweets)} unique hiring tweets found")
print(f"Saved to: {out_file}")
print(f"{'='*60}")
