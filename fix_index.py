#!/usr/bin/env python3
"""Fix the index.html landing page to show correct marketing posts count."""
import json
import os
import re
from datetime import datetime

def fix_index():
    """Update index.html with dynamic counts from latest report data."""
    
    # Find the latest report file
    report_files = sorted(glob.glob('web3_hiring_report_*.html'), key=os.path.getmtime, reverse=True)
    if not report_files:
        print("❌ No reports found")
        return False
    
    latest_report = report_files[0]
    m = re.search(r'web3_hiring_report_(\d{4}-\d{2}-\d{2})\.html', latest_report)
    report_date = m.group(1) if m else ''
    
    # Read the raw data JSON for counts
    raw_file_path = os.path.join(os.path.dirname(__file__), f'web3_hiring_posts_{report_date}.json')
    
    try:
        with open(raw_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_posts = data.get('count', 1)
        marketing_posts = data.get('marketing_count', 0)
        print(f"Counts from JSON: Total={total_posts}, Marketing={marketing_posts}")
    except FileNotFoundError:
        print(f"Raw file not found: {raw_file_path}")
        total_posts = 1
        marketing_posts = 0
    except Exception as e:
        print(f"Error reading JSON: {e}")
        total_posts = 1
        marketing_posts = 0
    
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the hardcoded values with dynamic ones
    print(f"Replacements: Total={total_posts}, Marketing={marketing_posts}")
    content = re.sub(
        r'<div class=\'stat\'><div class=\'stat-num\'>1</div><div class=\'stat-label\'>Today\s*\'s\s*Posts</div></div>',
        f'<div class=\'stat\'><div class=\'stat-num\'>{total_posts}</div><div class=\'stat-label\'>Today\'s Posts</div></div>',
        content, count=1
    )
    
    content = re.sub(
        r'<div class=\'stat\'><div class=\'stat-num\'>0</div><div class=\'stat-label\'>Marketing\s*&\s*Growth</div></div>',
        f'<div class=\'stat\'><div class=\'stat-num\'>{marketing_posts}</div><div class=\'stat-label\'>Marketing & Growth</div></div>',
        content, count=1
    )
    
    # Write back to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('✅ index.html updated successfully')
    return True

if __name__ == '__main__':
    import glob
    fix_index()
