import json
from datetime import datetime, timezone, timedelta, tzinfo
from email.utils import parsedate_to_datetime

data = json.load(open('web3_hiring_posts_2026-05-08.json', encoding='utf-8'))
tweets = data.get('all_tweets', [])

# Europe/Madrid timezone
class EuropeMadrid(tzinfo):
    def utcoffset(self, dt): return timedelta(hours=2)
    def tzname(self, dt): return "CEST"
    def dst(self, dt): return timedelta(hours=1)

user_tz_obj = EuropeMadrid()
now_local = datetime.now(user_tz_obj)
cutoff_local = now_local - timedelta(hours=48)

print(f"Now (local): {now_local}")
print(f"Cutoff (local): {cutoff_local}")
print()

for t in tweets:
    created_at_str = t.get('createdAt', '')
    if not created_at_str:
        print(f"Tweet: {t.get('username', '?')} - NO CREATED_AT")
        continue
    tweet_dt = parsedate_to_datetime(created_at_str)
    print(f"Tweet: {t.get('username', '?')}")
    print(f"  Raw: {created_at_str[:40]}")
    print(f"  Parsed: {tweet_dt} (tzinfo={tweet_dt.tzinfo})")
    
    # What the code does
    if tweet_dt.tzinfo is None:
        tweet_dt_local = tweet_dt.replace(tzinfo=user_tz_obj)
    else:
        tweet_dt_local = tweet_dt
    
    print(f"  After tz fix: {tweet_dt_local} (tzinfo={tweet_dt_local.tzinfo})")
    print(f"  cutoff_local: {cutoff_local} (tzinfo={cutoff_local.tzinfo})")
    print(f"  tweet < cutoff: {tweet_dt_local < cutoff_local}")
    print()
