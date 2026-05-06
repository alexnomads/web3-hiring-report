#!/usr/bin/env python3
"""Update index.html to point to the latest report dynamically."""
import glob
import os
from datetime import datetime

def update_index():
    """Find latest report and update index.html links."""
    
    # Find all report HTML files and sort by modification time (latest first)
    report_files = sorted(glob.glob('web3_hiring_report_*.html'), key=os.path.getmtime, reverse=True)
    
    if not report_files:
        print("❌ No reports found")
        return False
    
    latest_report = report_files[0]
    
    # Extract date from filename
    import re
    m = re.search(r'web3_hiring_report_(\d{4}-\d{2}-\d{2})\.html', latest_report)
    report_date = m.group(1) if m else ''
    
    print(f"Latest report: {latest_report}")
    print(f"Report date: {report_date}")
    
    # Read current index.html
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update the "Latest Report" section
    # Find and replace the hard-coded April 30 report reference
    latest_section = f'<h2 class=\'section-title\' style=\'margin-top:30px\'>Latest Report — {report_date}</h2><a href=\'{latest_report}\' class=\'report-link\' style=\'display:inline-block;background:#0a0a0a;border:1px solid #00d4aa;color:#00d4aa;font-weight:bold;text-decoration:none;padding:15px;margin-bottom:20px\'>📄 View Latest Report ({report_date})</a>'
    
    # Update the report list - extract existing links and prepend latest at top
    old_reports = []
    new_reports = []
    
    # Find all existing report-item divs
    import re
    pattern = r'<div class=\'report-item\'>\s*<a href=\'(.*?)\'\s+class=\'report-link\'>(.*?)</a></div>'
    matches = re.findall(pattern, content)
    
    for link, date in sorted(matches, key=lambda x: datetime.strptime(x[1].replace('📄 ', ''), '%Y-%m-%d'), reverse=True):
        if link not in [os.path.basename(r) for r in report_files]:
            continue
        new_reports.append(f'''<div class='report-item'>
            <a href='{link}' class='report-link'>
                <span class='report-date'>{date}</span>
                <span class='report-status'>📄 View</span>
            </a>
        </div>''')
    
    # Build the full report list (latest at top)
    new_report_list = '\n'.join(new_reports[:20])  # Top 20 reports
    
    # Dynamically count today's posts and marketing from latest JSON file
    import json
    raw_path = os.path.join(os.path.dirname(__file__), f'web3_hiring_posts_{report_date}.json')
    if os.path.exists(raw_path):
        with open(raw_path, 'r', encoding='utf-8') as rf:
            try:
                raw_data = json.load(rf)
                total_posts = raw_data.get('count', 1)
                marketing_posts = raw_data.get('marketing_count', 0)
            except Exception as e:
                print(f"Warning: Could not read JSON counts: {e}")
                total_posts = 1
                marketing_posts = 0
    else:
        print(f"Warning: Raw data file not found: {raw_path}")
        total_posts = 1
        marketing_posts = 0
    html = f"""<!DOCTYPE html>
<html lang='en'><head><meta charset='UTF-8'><title>Web3 Hiring Report Archive</title>
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
.report-list{{margin:30px 0}}.report-item{{margin-bottom:8px}}.report-link{{display:flex;justify-content:space-between;align-items:center;padding:12px 15px;background:#1a1a1a;border:1px solid #333;border-radius:8px;text-decoration:none;color:#e0e0e0;transition:background 0.2s}}
.report-link:hover{{background:#2a2a2a}}.report-date{{font-weight:bold;color:#00d4aa}}.report-status{{color:#888;font-size:12px}}
.latest-report{{margin-bottom:30px;padding:20px;background:#0f0f0f;border:2px solid #00d4aa;border-radius:8px;text-align:center}}
.latest-report a{{display:inline-block;background:#00d4aa;color:#0a0a0a;font-weight:bold;padding:15px 25px;text-decoration:none;border-radius:6px;margin-bottom:15px}}
.latest-report span{{font-size:14px;color:#888}}
</style></head><body><div class='container'>
<div class='header'><h1>Web3 Hiring Report Archive</h1><p>Daily Web3 hiring intelligence • Powered by @SuccessHunter</p>
<div class='stats'><div class='stat'><div class='stat-num'>{len(report_files)}</div><div class='stat-label'>Total Reports</div></div>
<div class='stat'><div class='stat-num'>{total_posts}</div><div class='stat-label'>Today's Posts</div></div>
<div class='stat'><div class='stat-num'>{marketing_posts}</div><div class='stat-label'>Marketing & Growth</div></div></div></div>

{latest_section}

<h2 class='section-title'>All Reports (Latest First)</h2>
<div class='report-list'>{new_report_list}</div>

<div class='footer'><p>Generated by @SuccessHunter • <a href='https://github.com/alexnomads/web3-hiring-report' style='color:#00d4aa'>GitHub Repo</a></p></div></div></body></html>"""
    
    # Write updated index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print('index.html updated successfully')
    return True

if __name__ == '__main__':
    update_index()