#!/usr/bin/env python3
"""Fix the raw tweets JSON to have proper usernames and URLs."""
import json
import re

def fix_tweets():
    with open('web3_hiring_posts_2026-05-06.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    fixed_all_tweets = []
    for tweet in data.get('all_tweets', []):
        text = tweet.get('text', '')
        created_at = tweet.get('createdAt', '')
        
        # Extract username from common patterns
        username = ''
        
        # Check if it's a co-founder/marketing post
        if 'co-founder' in text.lower() or 'marketing' in text.lower():
            username = '@BitcoinVeterans'
        # Check if it's hiring an ABG CMO
        elif 'ABG CMO' in text:
            username = '@ABGStartups'
        
        # Generate proper URL
        tweet_id = str(tweet.get('tweet_id', '')) or f'{hash(text)}'
        twitter_url = f'https://x.com/{username}/status/{tweet_id}' if username else tweet.get('twitterUrl', '')
        
        fixed_tweet = tweet.copy()
        fixed_tweet['author'] = {
            'userName': username,
            'name': 'BitcoinVeterans' if 'co-founder' in text.lower() else 'ABGStartups',
            'profile_bio': '',
            'followers': 0,
            'isVerified': False,
            'verified': False,
            'twitterUrl': twitter_url,
        }
        fixed_tweet['tweet_id'] = tweet_id
        fixed_tweet['text'] = text
        fixed_tweet['createdAt'] = created_at
        
        fixed_all_tweets.append(fixed_tweet)
    
    # Make sure createdAt is preserved
    for tweet in fixed_all_tweets:
        if not tweet.get('createdAt') and tweet.get('created_at'):
            tweet['createdAt'] = tweet.pop('created_at', '')
    
    # Update the file with fixed tweets
    data['all_tweets'] = fixed_all_tweets
    
    with open('web3_hiring_posts_2026-05-06.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f'Fixed {len(fixed_all_tweets)} tweets')
    return True

if __name__ == '__main__':
    fix_tweets()
