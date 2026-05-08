# Daily Web3 Hiring Report Publishing Setup

## Current Status

The daily report publishing can be achieved through **two methods**:

### 1. GitHub Actions (Recommended) ⭐
Automatically runs at 9:00 AM UTC every day, scraping fresh hiring tweets and generating the HTML report.

**What's needed:**
- ✅ GitHub Actions workflow file restored (`.github/workflows/deploy.yml`)
- ✅ Twitter API credentials stored in GitHub secrets:
  - `TWITTER_AUTH_TOKEN`
  - `TWITTER_CT0`
- ✅ Workflow configured to run automatically at 9:00 AM UTC daily

### 2. OpenClaw Cron Job (Alternative) 🕐
Set up a cron job in your workspace to run the report generation manually or on schedule.

**Manual Run:**
```bash
cd C:\Users\coliv\.openclaw\workspace\web3-hiring-report
python run_report_daily.py  # Scrapes tweets and generates JSON
python generate_report.py   # Converts JSON to HTML report
```

## Required Files

### 1. Twitter Credentials (`.twitter_cookies.env`)
Location: `C:\Users\coliv\.openclaw\workspace\agents-experiment\geopolitical-agent\.twitter_cookies.env`

This file contains:
- `AUTH_TOKEN` - Twitter API authentication token
- `CT0` - Twitter session cookie for authenticated requests

The scraper will automatically load these credentials.

### 2. Bird/X Search Module
Location: `C:\Users\coliv\.openclaw\workspace\agents-experiment\skills\last30days-official\scripts\lib\bird_x.py`

This module handles the Twitter API calls for searching hiring tweets.

### 3. Report Generator
Location: `web3-hiring-report/generate_report.py`

Converts the scraped JSON data into an HTML report with job listings.

## Automation Options

### Option A: GitHub Actions (Best for public repo)
1. Create a `.github/workflows/deploy.yml` file
2. Set up secrets in GitHub repo settings:
   - `TWITTER_AUTH_TOKEN` = value from `.twitter_cookies.env`
   - `TWITTER_CT0` = cookie value from `.twitter_cookies.env`
3. Workflow runs automatically at 9:00 AM UTC daily

### Option B: OpenClaw Cron Job (Best for private repo)
Create a cron job in your workspace:

```python
{
  "name": "Daily Web3 Hiring Report",
  "schedule": {
    "kind": "cron", 
    "expr": "0 9 * * *",  # 9:00 AM UTC daily (5:00 AM Madrid time)
    "tz": "Europe/Madrid"
  },
  "payload": {
    "kind": "agentTurn",
    "message": """
cd C:\\Users\\coliv\\.openclaw\\workspace\\web3-hiring-report
python run_report_daily.py
git add .
git commit -m "Daily report: $(date +%Y-%m-%d) generated"
git push
"""
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "webhook",
    "to": "https://hooks.slack.com/services/XXXXX"  # Optional webhook notification
  }
}
```

Then add to your cron list with:
```python
cron_add({job_object_here})
```

## Troubleshooting

### No tweets found?
1. Check Twitter credentials in `.twitter_cookies.env`
2. Verify bird search is installed and accessible
3. Ensure the scraper has access to recent hiring posts

### Report not updating?
1. Run `python run_report_daily.py` manually first
2. Check that JSON file has data: `cat web3_hiring_posts_YYYY-MM-DD.json | jq '.count'`
3. Run `python generate_report.py` to create HTML

### GitHub Actions not working?
1. Check secrets are set in repo settings
2. Verify workflow file syntax is correct
3. Enable "Actions" in repo settings if disabled

## Manual Testing

To test the daily publishing pipeline:

```bash
# Step 1: Ensure you're on the main branch
git checkout main

# Step 2: Run the scraper
python run_report_daily.py

# Step 3: Generate HTML report
python generate_report.py

# Step 4: Check results
cat web3_hiring_posts_*.json | jq '.count'
ls -la web3_hiring_report_*.html

# Step 5: Commit and push if successful
git add .
git commit -m "Daily report: $(date +%Y-%m-%d)"
git push
```

## Next Steps to Enable Daily Publishing

1. **Restore GitHub Actions** (Recommended):
   - Copy `.github/workflows/deploy.yml` to your repo
   - Set up secrets in GitHub settings
   - Enable Actions in repo settings

2. **OR Set Up OpenClaw Cron**:
   - Add the cron job using `cron_add()` function
   - Configure webhook or email notifications for completion

3. **Test the pipeline** with manual run first:
   ```bash
   python run_report_daily.py && python generate_report.py
   ```

## Current Issue (May 4, 2026)

The report is not publishing daily because:
- ❌ GitHub Actions workflow was deleted in commit `da55159`
- ❌ No fresh hiring tweet data being collected
- ⚠️ No automated mechanism to run the scraper daily

**Solution**: Restore GitHub Actions workflow and set up credentials as described above.
