content = open('scraper_twitter_hiring.py', encoding='utf-8').read()
old_path = 'Path(__file__).parent.parent.parent / "agents-experiment" / "geopolitical-agent" / ".twitter_cookies.env"'
new_path = 'Path(__file__).parent.parent / "agents-experiment" / "geopolitical-agent" / ".twitter_cookies.env"'
content = content.replace(old_path, new_path)
open('scraper_twitter_hiring.py', 'w', encoding='utf-8').write(content)
print('fixed path')
