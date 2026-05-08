content = open('scraper_twitter_hiring.py', encoding='utf-8').read()
if 'sys.stdout.reconfigure' not in content:
    content = content.replace('import sys', 'import sys\nsys.stdout.reconfigure(encoding="utf-8")')
    open('scraper_twitter_hiring.py', 'w', encoding='utf-8').write(content)
    print('added stdout reconfigure')
else:
    print('already present')
