import sys
content = open('scraper_twitter_hiring.py', encoding='utf-8-sig', errors='replace').read()
# Add set_credentials import
content = content.replace(
    'from last30days.bird_x import search_x, is_bird_installed, get_bird_status',
    'from last30days.bird_x import search_x, is_bird_installed, get_bird_status, set_credentials'
)
# Add set_credentials call after credentials loaded
old = '    print(f"✓ Twitter credentials loaded from {auth_token[:16]}...")'
new = '''    # Inject credentials into bird_x
    set_credentials(auth_token, ct0)
    print(f"✓ Twitter credentials loaded from {auth_token[:16]}...")
    
    # Verify authentication
    status = get_bird_status()
    print(f"   Auth status: {status.get('authenticated', 'unknown')}")'''
content = content.replace(old, new)
open('scraper_twitter_hiring.py', 'w', encoding='utf-8').write(content)
print('patched ok')
