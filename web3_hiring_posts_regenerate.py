#!/usr/bin/env python3
"""Quick fix: Regenerate web3_hiring_posts JSON with proper structure."""
import json
import glob
import os
from datetime import datetime, timezone

def main():
    workdir = 'C:\\Users\\coliv\\.openclaw\\workspace\\web3-hiring-report'
    posts = sorted(glob.glob(os.path.join(workdir, 'web3_hiring_posts_*.json')), 
                   key=lambda p: os.path.getmtime(p), reverse=True)
    
    for pf in posts:
        with open(pf) as f:
            data = json.load(f)
        
        # Extract and preserve all_tweets separately
        all_tweets = data.get('all_tweets', [])
        results = data.get('results', [])
        count = len(results) if isinstance(results, list) else 0
        
        new_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'generated': datetime.now(timezone.utc).isoformat(),
            'count': count,
            'all_tweets': all_tweets,  # Preserve full raw data
            'results': results         # Filtered results
        }
        
        with open(f'web3_hiring_posts_{datetime.now().strftime("%Y-%m-%d")}.json', 'w') as f:
            json.dump(new_data, f, indent=2)
    
    print(f"Regenerated from {len(posts)} posts")

if __name__ == '__main__':
    main()