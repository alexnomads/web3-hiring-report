import json
from datetime import datetime, timezone

data = json.load(open('web3_hiring_posts_2026-05-08.json', encoding='utf-8'))
tweets = data.get('all_tweets', [])
print(f'Total tweets: {len(tweets)}')
for t in tweets:
    print(f"  {t.get('username', '?')} - {t.get('created_at', '?')[:30]}")
