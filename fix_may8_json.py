#!/usr/bin/env python3
"""Fix May 8 JSON file with all tweets and results."""
import json, codecs, datetime

all_tweets_raw = [
    {
        "username": "",
        "name": "",
        "bio": "",
        "text": "#Hiring: Chief Marketing Officer (CMO)\n\nLooking for a marketing leader who can do more than build campaigns.\n\nLocation: Dubai. \nIndian nationals will be provided with Visa and other benefits as per UAE Laws.\n\nClient needs someone who can:\n• Drive revenue growth\n• Build a powerful brand\n• Lead strategic partnerships\n• Represent the company at industry forums\n• Prepare the brand for IPO-stage visibility\n• Lead large marketing teams with clarity and scale\n\nIdeal background:\n✓ 20+ year",
        "job_title": None,
        "company": "narayani07",
        "tweet_id": "2052610072430436517",
        "created_at": "Fri May 08 04:42:31 +0000 2026",
        "twitter_url": "https://x.com/Narayani07/status/2052610072430436517"
    },
    {
        "username": "trotskomain",
        "name": "",
        "bio": "",
        "text": "Hi! I'm currently building a startup and looking for a marketing co-founder. Preferred location is NYC.",
        "job_title": null,
        "company": "trotskomain",
        "tweet_id": "2052644789577793767",
        "created_at": "Fri May 08 07:00:28 +0000 2026",
        "twitter_url": "https://x.com/trotskomain/status/2052644789577793767"
    },
    {
        "username": "1spyral",
        "name": "",
        "bio": "",
        "text": "startup idea:\n\nai therapist for people addicted to ai\n\nlooking for vc, engineers, co-founder, marketing",
        "job_title": null,
        "company": "1spyral",
        "tweet_id": "2052639013547430163",
        "created_at": "Fri May 08 06:37:31 +0000 2026",
        "twitter_url": "https://x.com/1spyral/status/2052639013547430163"
    },
    {
        "username": "AUaussieF",
        "name": "",
        "bio": "",
        "text": "@MartiniGuyYT Nice one, great find. Good on them for hiring into crypto, stoked the industry's finally getting some traction. Any idea if these roles are Sydney-based or mostly overseas?",
        "job_title": null,
        "company": "auaussief",
        "tweet_id": "2052656050445447178",
        "created_at": "Fri May 08 07:45:13 +0000 2026",
        "twitter_url": "https://x.com/AUaussieF/status/2052656050445447178"
    },
    {
        "username": "Job_Giant",
        "name": "",
        "bio": "",
        "text": "🚨Rendalli Company is hiring🚨\n\n Open role: HR Assistant\n\nApply here: https://t.co/syVLsmJDqu\n\nJoin our WhatsApp Channel for more alerts: https://t.co/zbevhCjIvP\n\nJob Giant is  affiliated!\n\nClosing date: 20 May 2026\n\nHiring location: jinja Uganda https://t.co/77hlhIjm0s",
        "job_title": null,
        "company": "job_giant",
        "tweet_id": "2052656045713932507",
        "created_at": "Fri May 08 07:45:12 +0000 2026",
        "twitter_url": "https://x.com/Job_Giant/status/2052656045713932507"
    },
    {
        "username": "mogotsi_b",
        "name": "",
        "bio": "",
        "text": "@ekene_xander @atoladimeji @NigeriaStories Children deserve the opportunity to go to school, however systematically even after they finish their studies there will still be the problem of who to prioritise when coming to hiring based on fact that citizen are to be prioritised first ideology.",
        "job_title": null,
        "company": null,
        "tweet_id": "2052656040991129660",
        "created_at": "Fri May 08 07:45:11 +0000 2026",
        "twitter_url": "https://x.com/mogotsi_b/status/2052656040991129660"
    },
    {
        "username": "Ekeminihthomas",
        "name": "",
        "bio": "",
        "text": "The Web3 hiring sweet spot in 2026:\n\nPre-TGE projects with funded teams of 5–15 people.\n\nSmall enough that one great BD, growth, or community hire can completely change trajectory.\n\nBig enough to actually have budget, runway, and real execution speed.\n\nThat's where the asymmetric opportunities are right now.",
        "job_title": null,
        "company": "ekeminihthomas",
        "tweet_id": "2052655960334749990",
        "created_at": "Fri May 08 07:44:52 +0000 2026",
        "twitter_url": "https://x.com/Ekeminihthomas/status/2052655960334749990"
    }
]

results_data = [
    {"username": "", "tweet_id": "2052610072430436517", "text": "#Hiring: Chief Marketing Officer (CMO)", "job_title": "Chief Marketing Officer (CMO)", "company": "narayani07", "category": "target", "relevance": 2},
    {"username": "trotskomain", "tweet_id": "2052644789577793767", "text": "Hi! I'm currently building a startup and looking for a marketing co-founder.", "job_title": "Marketing Co-Founder", "company": "trotskomain", "category": "target", "relevance": 1},
    {"username": "Job_Giant", "tweet_id": "2052656045713932507", "text": "🚨Rendalli Company is hiring", "job_title": "HR Assistant", "company": "Rendalli Company", "category": "target", "relevance": 1},
    {"username": "AUaussieF", "tweet_id": "2052656050445447178", "text": "@MartiniGuyYT Nice one, great find. Good on them for hiring into crypto...", "job_title": null, "company": None, "category": "maybe", "relevance": 1},
    {"username": "Ekeminihthomas", "tweet_id": "2052655960334749990", "text": "The Web3 hiring sweet spot in 2026:", "job_title": null, "company": None, "category": "target", "relevance": 1},
    {"username": "1spyral", "tweet_id": "2052639013547430163", "text": "startup idea:\n\nai therapist for people addicted to ai\n\nlooking for vc, engineers, co-founder, marketing", "job_title": null, "company": None, "category": "maybe", "relevance": 1},
    {"username": "mogotsi_b", "tweet_id": "2052656040991129660", "text": "@ekene_xander @atoladimeji @NigeriaStories Children deserve...", "job_title": null, "company": None, "category": None, "relevance": 0},
]

data = {
    "date": "2026-05-08",
    "generated": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ".000+00:00",
    "count": len(results_data),
    "marketing_count": 4,
    "results": [
        {**r, **{
            "name": "", "bio": "", "text": r["text"], 
            "job_title": r["job_title"] or "",
            "company": r["company"] or "",
            "followers": 0,
            "is_verified": False,
            "twitter_url": "",
            "created_at": ""
        }} for r in results_data
    ]
}

with open('web3_hiring_posts_2026-05-08.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Fixed May 8 JSON with {data['count']} results")
