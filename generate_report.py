#!/usr/bin/env python3
"""Filter raw Twitter data and generate HTML report for web3 hiring.

Implements:
1. Target role keywords (Head of Marketing, CMO, GTM, etc.) + Crypto context classifier
2. 48h UTC time window filtering
3. Single results list with relevance scoring
4. Deduplication by tweet_id
5. Relevance badge in HTML output
6. Improved job title extraction for specific roles
"""
import json
import re
import os
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

sys = __import__('sys')
sys.stdout.reconfigure(encoding='utf-8')

def _get_report_date():
    """Extract YYYY-MM-DD from the raw file filename."""
    base = os.path.basename(RAW_FILE)
    m = re.search(r'(\d{4}-\d{2}-\d{2})', base)
    return m.group(1) if m else 'unknown'

import glob
post_files = glob.glob('web3_hiring_posts_*.json')
if post_files:
    for pf in sorted(post_files, key=os.path.getmtime, reverse=True):
        try:
            RAW_FILE = os.path.join(os.path.dirname(__file__), pf)
            with open(RAW_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            if 'all_tweets' in raw or 'results' in raw:
                m = re.search(r'web3_hiring_posts_(\d{4}-\d{2}-\d{2})\.json', pf)
                report_date = m.group(1) if m else _get_report_date()
                break
        except:
            continue
    else:
        report_date = datetime.now().strftime('%Y-%m-%d')
        RAW_FILE = os.path.join(os.path.dirname(__file__), 'web3_hiring_posts_{}.json'.format(report_date))
REPORT_FILE = os.path.join(os.path.dirname(__file__), 'web3_hiring_report_{}.html'.format(report_date))

# Target roles (marketing/growth leadership in web3)
TARGET_ROLE_KEYWORDS = [
    r'\bhead\s+of\s+marketing\b', r'\bhead\s+of\s+growth\b', r'\b(gtm|go-to-market)\b', r'\bcmo\b',
    r'\bproduct\s+marketing\b', r'\b(branding|brand\s+manager|brand\s+lead|head\s+of\s+brand)\b',
    r'\b(marketing\s+automation|growth\s+automation)\b', r'\bfounding\s+marketer\b',
    r'\b(vp\s+marketing|director\s+of\s+marketing|marketing\s+lead|growth\s+lead)\b',
]

# Crypto/web3 context
CRYPTO_KEYWORDS = [
    r'\bweb3\b', r'\bcrypto\b', r'\bblockchain\b', r'\bdefi\b', r'\bnft\b',
    r'\bdao\b', r'\btoken\b', r'\bethereum\b', r'\bsolana\b', r'\bbitcoin\b',
    r'\blayer2\b', r'\bzkb\b', r'\bdecentralized\b',
]

def classify_tweet(text):
    """Returns (category, score) where category is 'target', 'maybe', or None."""
    text_lower = text.lower()
    role_score = sum(1 for p in TARGET_ROLE_KEYWORDS if re.search(p, text_lower))
    crypto_score = sum(1 for p in CRYPTO_KEYWORDS if re.search(p, text_lower))

    if role_score >= 1 and crypto_score >= 1:
        return 'target', role_score + crypto_score
    if role_score >= 2:
        return 'target', role_score
    if role_score >= 1:
        return 'maybe', role_score
    return None, 0

def extract_job_title(text):
    """First try to match exact target roles, then fall back to generic."""
    text_clean = text.replace('\n', ' ').replace('\r', ' ')
    
    # Direct role patterns
    role_patterns = [
        r'(?:hiring|looking for|now hiring)\s+(?:a\s+)?(Head of Marketing|Head of Growth|CMO|Product Marketing Manager|Brand Manager|Founding Marketer|GTM Lead|VP Marketing|Director of Marketing|Growth Lead)',
        r'(?:role|position|opportunity)\s*:\s*(Head of Marketing|Head of Growth|CMO|Product Marketing Manager|Brand Manager|Founding Marketer|GTM Lead|VP Marketing|Director of Marketing|Growth Lead)',
    ]
    for pat in role_patterns:
        m = re.search(pat, text_clean, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    
    # Fall back to generic patterns
    patterns = [
        r'(?:hiring|looking for|now hiring):\s*([A-Z][A-Za-z\s&]+?)(?:\n|$|–|-|:| )',
        r'(?:hiring|looking for)\s+([A-Z][A-Za-z\s&]+?)\s+(?:a|an|for|to|in|at)',
        r'\b([A-Z][A-Za-z\s&]+?)\s+(?:is|are)\s+hiring\b',
        r'(?:role|position|opportunity|career):\s*([A-Z][A-Za-z\s&]+?)(?:\n|$|–|-)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text_clean, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            title = re.sub(r'\s*\(.*?\)\s*', ' ', title)
            title = re.sub(r'\s+', ' ', title)
            if len(title) > 3 and len(title) < 100:
                return title
    return None

def extract_company(text, username):
    """Extract company name from text."""
    text_lower = text.lower()
    patterns = [
        r'(?:@|by|at)\s+([A-Z][A-Za-z0-9_]+)',
        r'\b([A-Z][A-Za-z0-9&\s]+?)\s+(?:is|are|has|just|now)\s+(hiring|looking|announcing|posting)',
        r'(?:hiring|looking for)\s+(?:a|an)\s+([A-Z][A-Za-z\s&]+?)\s+(?:at|for|at\s+@)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            company = match.group(1).strip()
            company = re.sub(r'\s+', ' ', company)
            if len(company) > 2 and len(company) < 50:
                return company
    return username

def parse_created_at(created_at_str):
    """Parse Twitter createdAt format."""
    try:
        return parsedate_to_datetime(created_at_str)
    except Exception:
        return None

def process_data():
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    all_tweets = raw.get('all_tweets', [])
    results = []

    # Time filter: 48h UTC window
    now_utc = datetime.now(timezone.utc)
    cutoff_utc = now_utc - timedelta(hours=48)
    filtered_count = 0
    excluded_count = 0

    for tweet in all_tweets:
        created_at_str = tweet.get('createdAt', '')
        if created_at_str:
            tweet_dt = parse_created_at(created_at_str)
            if tweet_dt and tweet_dt.tzinfo is None:
                tweet_dt = tweet_dt.replace(tzinfo=timezone.utc)
            elif tweet_dt.utcoffset() is not None and tweet_dt.utcoffset().total_seconds() != 0:
                tweet_dt = tweet_dt.astimezone(timezone.utc)
            if tweet_dt and tweet_dt < cutoff_utc:
                excluded_count += 1
                continue
        else:
            excluded_count += 1
            continue
        
        filtered_count += 1
        text = tweet.get('text', '')
        if not text or len(text) < 20:
            continue
        
        author = tweet.get('author', {})
        username = author.get('userName', '') or author.get('username', '') or ''
        if not username:
            tu = tweet.get('twitterUrl', '') or author.get('twitterUrl', '')
            if tu:
                username = tu.rstrip('/').split('/')[-1]
        name = author.get('name', '')
        bio = author.get('profile_bio', '') or author.get('description', '')
        followers = author.get('followers', 0) or author.get('followersCount', 0) or 0
        is_verified = author.get('isVerified', False) or author.get('isBlueVerified', False) or author.get('verified', False)
        tweet_id = str(tweet.get('id', ''))
        created_at = tweet.get('createdAt', '')
        twitter_url = tweet.get('twitterUrl', '') or author.get('twitterUrl', f'https://x.com/{username}/status/{tweet_id}')
        
        cat, score = classify_tweet(text)
        if cat in ('target', 'maybe'):
            job_title = extract_job_title(text)
            company = extract_company(text, username)
            results.append({
                'username': username,
                'name': name,
                'bio': bio,
                'text': text,
                'job_title': job_title,
                'company': company,
                'tweet_id': tweet_id,
                'followers': followers,
                'is_verified': is_verified,
                'twitter_url': twitter_url,
                'created_at': created_at,
                'category': cat,
                'relevance': score,
            })
    
    print(f"Total raw tweets: {len(all_tweets)}")
    print(f"Tweets within 48h window: {filtered_count}")
    print(f"Excluded (older than 48h): {excluded_count}")
    print(f"Filtered posts (sorted by relevance): {len(results)}")
    
    # Sort by relevance score descending
    results.sort(key=lambda r: r['relevance'], reverse=True)
    
    # Deduplicate by tweet_id
    seen_ids = set()
    unique_results = []
    for r in results:
        if r['tweet_id'] not in seen_ids:
            seen_ids.add(r['tweet_id'])
            unique_results.append(r)
    
    raw['results'] = unique_results
    raw['count'] = len(unique_results)
    
    with open(RAW_FILE, 'w', encoding='utf-8') as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)
    
    return unique_results

def generate_html(results):
    """Generate HTML report."""
    date_str = _get_report_date()
    verified_count = sum(1 for r in results if r.get('is_verified'))
    
    opp_html = ""
    for r in results[:20]:
        job_title = r.get('job_title') or 'Opportunity'
        company = r.get('company') or r.get('username', '')
        created = r.get('created_at', '')
        
        badge_text = "🔥 High Match" if r['relevance'] >= 3 else '✨ Medium Match'
        badge_class = "badge-high" if r['relevance'] >= 3 else "badge-medium"
        
        opp_html += f"""<div class='card'>
<div class='card-header'><span class='card-handle'>@{r.get('username', '')}</span> {f'<span style="color:#888">({r.get("name", "")})</span>' if r.get('name') else ''}</div>
<div class='card-badge'><span class="badge badge-{badge_class}">{badge_text}</span></div>
<div class='card-title'>{job_title}</div>
<div class='card-company'>{company}</div>
<div class='card-text'>{r.get('text', '')[:300]}{'...' if len(r.get('text', '')) > 300 else ''}</div>
<div class='card-meta'><span>🕒 {created}</span><span>👁 {r.get('followers', 0)}</span><a href="{r.get('twitter_url', '')}" target="_blank">View tweet →</a></div>
</div>
"""
    
    html = f"""<!DOCTYPE html>
<html lang='en'><head><meta charset='UTF-8'><title>Web3 Hiring Report - {date_str}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:-apple-system,sans-serif;background:#0a0a0a;color:#e0e0e0;padding:20px}}
.container{{max-width:900px;margin:0 auto}}.header{{background:linear-gradient(135deg,#1a1a2e,#16213e);padding:30px;border-radius:12px;margin-bottom:20px}}
.header h1{{font-size:28px;color:#00d4aa;margin-bottom:10px}}.header p{{color:#888;font-size:14px}}
.stats{{display:flex;gap:20px;margin-top:20px}}.stat{{background:rgba(0,212,170,0.1);padding:15px 20px;border-radius:8px;flex:1;text-align:center}}
.stat-num{{font-size:24px;font-weight:bold;color:#00d4aa}}.stat-label{{font-size:12px;color:#888;margin-top:5px}}
.section-title{{font-size:20px;margin:30px 0 15px;padding-bottom:10px;border-bottom:1px solid #333}}
.card{{background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:15px;margin-bottom:10px}}
.card-badge{{display:flex;align-items:center;gap:8px;margin-bottom:8px;padding:8px;background:rgba(0,212,170,0.1);border-radius:4px}}
.badge{{font-weight:bold;font-size:13px;padding:4px 10px;border-radius:4px;color:#0a0a0a;background:#00d4aa}}.badge-high{{background:#ff4444;color:white}}.badge-medium{{background:#ffd700;color:black}}
.card-header{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}.card-handle{{font-weight:bold;color:#00d4aa}}
.card-title{{font-size:16px;margin-bottom:5px;color:#fff}}.card-text{{color:#ccc;font-size:14px;line-height:1.5;margin-bottom:10px}}
.card-meta{{display:flex;gap:15px;font-size:12px;color:#666}}.card-meta a{{color:#00d4aa;text-decoration:none}}
.footer{{text-align:center;margin-top:40px;color:#555;font-size:12px}}
</style></head><body><div class='container'>
<div class='header'><h1>Web3 Hiring Report</h1><p>{date_str}</p>
<div class='stats'><div class='stat'><div class='stat-num'>{len(results)}</div><div class='stat-label'>Total Posts</div></div>
<div class='stat'><div class='stat-num'>{verified_count}</div><div class='stat-label'>Verified Accounts</div></div></div></div>

<h2 class='section-title'>Top Hiring Opportunities</h2><div id='opportunities'>{opp_html}</div>

<div class='footer'><p>Generated by @SuccessHunter</p></div></div></body></html>"""
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Report saved to {REPORT_FILE}")
    return html

if __name__ == '__main__':
    results = process_data()
    generate_html(results)
