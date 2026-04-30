import json, sys
sys.stdout.reconfigure(encoding='utf-8')
with open(r'C:\Users\coliv\.openclaw\workspace\web3-hiring-report\web3_hiring_posts_2026-04-30.json') as f:
    data = json.load(f)
tweets = data['all_tweets']
for i, t in enumerate(tweets[:5]):
    author = t.get('author', {})
    print(f'Tweet {i+1}:')
    print(f'  author keys: {list(author.keys())}')
    print(f'  author.username: {author.get("username", "MISSING")}')
    print(f'  author.name: {author.get("name", "MISSING")}')
    print(f'  twitterUrl: {t.get("twitterUrl", "MISSING")}')
    print(f'  id: {t.get("id", "MISSING")}')
    print()
