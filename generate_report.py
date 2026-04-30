#!/usr/bin/env python3
"""Filter raw Twitter data and generate HTML report for web3 hiring."""
import json
import re
import sys
import os
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding='utf-8')

RAW_FILE = os.path.join(os.path.dirname(__file__), 'web3_hiring_posts_2026-04-30.json')
REPORT_FILE = os.path.join(os.path.dirname(__file__), 'web3_hiring_report_2026-04-30.html')

# Keywords that indicate hiring/job posts
HIRING_KEYWORDS = [
    r'\b(hiring|hire|now\s+hiring|looking\s+for|join\s+our|we\'?re?\s+looking|open\s+role|we\s+are?\s+hiring)',
    r'\b(job|position|role|opportunity|career)\b',
    r'\b(remote|salary|compensation|benefits)\b',
    r'\bapply|application|submit|send\s+your',
]

# Keywords that indicate marketing/promotional content
MARKETING_KEYWORDS = [
    r'\b(our\s+platform|join\s+our\s+(community|network|telegram|discord|channel))',
    r'\b(sign\s+up|subscribe|follow|download|install)\b',
    r'\b(announcement|launch|new\s+feature|update|exclusive)',
    r'\b(don\'?t\s+miss|limited\s+time|free\s+(signup|trial|access))',
    r'\b(apply\s+for\s+free|get\s+started|learn\s+more)',
]

# Exclude these common non-job patterns
EXCLUDE_PATTERNS = [
    r'\b(captcha|scam|phishing|fraud|warning|alert|protect)\b.*\b(yourself|your|don\'?t)\b',
    r'\b(not\s+hiring|fake|hiring\s+posts|marketing\s+campaign)\b',
    r'\b(someone\s+else|not\s+directly|sharing\s+for|repost)\b',
]

def is_hiring_post(text):
    """Check if a tweet is about hiring/jobs."""
    text_lower = text.lower()
    
    # First check exclusions
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, text_lower):
            return False
    
    # Check hiring keywords
    score = 0
    for pattern in HIRING_KEYWORDS:
        if re.search(pattern, text_lower):
            score += 1
    
    # Also check for specific job-related patterns
    if re.search(r'\b(\$[\d,]+|k\s+salary|equity|stock|bonus)\b', text_lower):
        score += 2
    if re.search(r'\b(remote|location|office)\b', text_lower):
        score += 1
    if re.search(r'\b(full[- ]?time|part[- ]?time|contract|freelance)\b', text_lower):
        score += 1
    if re.search(r'\b(comment|dm|send|message|email|apply)\b', text_lower):
        score += 1
    if re.search(r'\b(junior|senior|mid[- ]?level|lead|director|vp|cto|cfo|head\s+of)\b', text_lower):
        score += 1
    
    return score >= 2

def is_marketing_post(text):
    """Check if a tweet is marketing/promotional content."""
    text_lower = text.lower()
    
    score = 0
    for pattern in MARKETING_KEYWORDS:
        if re.search(pattern, text_lower):
            score += 1
    
    # Check for self-promotion patterns
    if re.search(r'\b(we\s+build|we\s+help|we\s+offer|our\s+services|our\s+platform|our\s+team)\b', text_lower):
        score += 1
    if re.search(r'\b(check\s+out|visit|link\s+in|bio|profile)\b', text_lower):
        score += 1
    
    return score >= 2

def extract_job_title(text):
    """Extract job title from text."""
    patterns = [
        r'(?:hiring|looking for|now hiring):\s*([A-Z][A-Za-z\s&]+?)(?:\n|$|–|-|:| )',
        r'(?:hiring|looking for)\s+([A-Z][A-Za-z\s&]+?)\s+(?:a|an|for|to|in|at)',
        r'\b([A-Z][A-Za-z\s&]+?)\s+(?:is|are)\s+hiring\b',
        r'(?:role|position|opportunity|career):\s*([A-Z][A-Za-z\s&]+?)(?:\n|$|–|-)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            title = match.group(1).strip()
            # Clean up
            title = re.sub(r'\s*\(.*?\)\s*', ' ', title)
            title = re.sub(r'\s+', ' ', title)
            if len(title) > 3 and len(title) < 100:
                return title
    return None

def extract_company(text, username):
    """Extract company name from text."""
    text_lower = text.lower()
    patterns = [
        r'(?:@|by|at)\s+([A-Z][A-Za-z0-9_]+)',  # @mentions
        r'\b([A-Z][A-Za-z0-9&\s]+?)\s+(?:is|are|has|just|now)\s+(hiring|looking|announcing|posting)',
        r'(?:hiring|looking for)\s+(?:a|an)\s+([A-Z][A-Za-z0-9\s&]+?)\s+(?:at|for|at\s+@)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            company = match.group(1).strip()
            company = re.sub(r'\s+', ' ', company)
            if len(company) > 2 and len(company) < 50:
                return company
    return username

def process_data():
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    
    all_tweets = raw.get('all_tweets', [])
    results = []
    marketing_results = []
    
    for tweet in all_tweets:
        text = tweet.get('text', '')
        if not text or len(text) < 20:
            continue
        
        author = tweet.get('author', {})
        username = author.get('userName', '') or author.get('username', '') or ''
        # Extract username from twitterUrl if still empty
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
        
        if is_hiring_post(text):
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
            })
        
        if is_marketing_post(text):
            marketing_results.append({
                'username': username,
                'name': name,
                'bio': bio,
                'text': text,
                'tweet_id': tweet_id,
                'followers': followers,
                'is_verified': is_verified,
                'twitter_url': twitter_url,
                'created_at': created_at,
            })
    
    print(f"Total raw tweets: {len(all_tweets)}")
    print(f"Filtered hiring posts: {len(results)}")
    print(f"Filtered marketing posts: {len(marketing_results)}")
    
    # Update the raw data file with filtered results
    raw['results'] = results
    raw['marketing_results'] = marketing_results
    raw['count'] = len(results)
    raw['marketing_count'] = len(marketing_results)
    raw['generated'] = datetime.now(timezone.utc).isoformat()
    
    with open(RAW_FILE, 'w', encoding='utf-8') as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)
    
    return results, marketing_results

def generate_html(results, marketing_results):
    """Generate HTML report."""
    date_str = "2026-04-30"
    verified_count = sum(1 for r in results if r.get('is_verified'))
    
    # Build opportunities section
    opp_html = ""
    for r in results[:20]:  # Top 20
        job = r.get('job_title') or 'Opportunity'
        company = r.get('company') or r.get('username', '')
        created = r.get('created_at', '')
        
        opp_html += f"""<div class='card'>
<div class='card-header'><span class='card-handle'>@{r.get('username', '')}</span> {f'<span style="color:#888">({r.get("name", "")})</span>' if r.get('name') else ''}</div>
<div class='card-title'>{job}</div>
<div class='card-company'>{company}</div>
<div class='card-text'>{r.get('text', '')[:300]}{'...' if len(r.get('text', '')) > 300 else ''}</div>
<div class='card-meta'><span>🕒 {created}</span><span>👁 {r.get('followers', 0)}</span><a href="{r.get('twitter_url', '')}" target="_blank">View tweet →</a></div>
</div>
"""
    
    # Build marketing section
    mkt_html = ""
    for r in marketing_results:
        mkt_html += f"""<div class='card'>
<div class='card-header'><span class='card-handle'>@{r.get('username', '')}</span> {f'<span style="color:#888">({r.get("name", "")})</span>' if r.get('name') else ''}</div>
<div class='card-text'>{r.get('text', '')[:300]}{'...' if len(r.get('text', '')) > 300 else ''}</div>
<div class='card-meta'><span>🕒 {r.get('created_at', '')}</span><span>👁 {r.get('followers', 0)}</span><a href="{r.get('twitter_url', '')}" target="_blank">View →</a></div>
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
.section-title-marketing{{color:#00d4aa}}.card{{background:#1a1a1a;border:1px solid #333;border-radius:8px;padding:15px;margin-bottom:10px}}
.card-header{{display:flex;align-items:center;gap:8px;margin-bottom:8px}}.card-handle{{font-weight:bold;color:#00d4aa}}
.card-title{{font-size:16px;margin-bottom:5px}}.card-company{{color:#888;font-size:14px;margin-bottom:8px}}
.card-text{{color:#ccc;font-size:14px;line-height:1.5;margin-bottom:10px}}.card-meta{{display:flex;gap:15px;font-size:12px;color:#666}}
.card-meta a{{color:#00d4aa;text-decoration:none}}.footer{{text-align:center;margin-top:40px;color:#555;font-size:12px}}
</style></head><body><div class='container'>
<div class='header'><h1>Web3 Hiring Report</h1><p>{date_str}</p>
<div class='stats'><div class='stat'><div class='stat-num'>{len(results)}</div><div class='stat-label'>Total Posts</div></div>
<div class='stat'><div class='stat-num'>{len(marketing_results)}</div><div class='stat-label'>Marketing & Growth</div></div>
<div class='stat'><div class='stat-num'>{verified_count}</div><div class='stat-label'>Verified Accounts</div></div></div></div>

<h2 class='section-title'>Top Hiring Opportunities</h2><div id='opportunities'>{opp_html}</div>

<h2 class='section-title' style='margin-top:30px'>Marketing & Growth Posts</h2><div id='marketing'>{mkt_html}</div>

<div class='footer'><p>Generated by @SuccessHunter</p></div></div></body></html>"""
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Report saved to {REPORT_FILE}")
    return html

if __name__ == '__main__':
    results, marketing_results = process_data()
    generate_html(results, marketing_results)
