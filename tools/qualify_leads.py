#!/usr/bin/env python3
"""Rank scraped Google Maps businesses by how much they need a website / AI help.

Input:  the results.csv written by gosom/google-maps-scraper (see tools/find_leads.sh)
Output: data/leads_ranked.csv  - every usable lead, best first, with the problems found
        data/messages.md       - a ready-to-send first message for each top lead

Usage:  python3 tools/qualify_leads.py data/results.csv [--top 30] [--name "Your Name"]
Only uses the Python standard library.
"""
import argparse
import csv
import re
import ssl
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

csv.field_size_limit(sys.maxsize)

SOCIAL_HOSTS = ("facebook.com", "instagram.com", "linktr.ee", "tiktok.com",
                "business.site", "wa.me", "yelp.com", "linkedin.com")
CHAT_MARKERS = ("intercom", "tawk.to", "drift.com", "crisp.chat", "livechat",
                "tidio", "wa.me/", "api.whatsapp.com", "chatbot", "manychat")
BOOKING_MARKERS = ("book now", "book online", "appointment", "schedule", "calendly",
                   "booking", "reserve", "get a quote", "request a quote")

# Points for each problem. Bigger = easier sale.
PROBLEMS = {
    "no_website":   (50, "you don't have a website"),
    "social_only":  (35, "you only have a social media page, no real website"),
    "site_down":    (40, "your website does not load"),
    "not_mobile":   (20, "your website is hard to use on a phone"),
    "no_https":     (15, "your website shows 'Not secure' in the browser"),
    "slow":         (10, "your website is slow to load"),
    "outdated":     (10, "your website looks outdated"),
    "no_booking":   (10, "there is no way to book or request a quote online"),
    "no_chat":      (5,  "there is no chat or WhatsApp button to answer customers 24/7"),
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def fetch(url, timeout=15):
    """Return (final_url, html, seconds) or (None, None, None) if it fails."""
    if not url.startswith("http"):
        url = "http://" + url
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout,
                                    context=ssl.create_default_context()) as r:
            html = r.read(600_000).decode("utf-8", "ignore")
            return r.geturl(), html, time.time() - start
    except Exception:
        # Retry over plain http in case only the https certificate is broken.
        if url.startswith("https://"):
            return fetch("http://" + url[len("https://"):], timeout)
        return None, None, None


def check_site(website):
    """Return a list of problem keys for one website."""
    website = (website or "").strip()
    if not website:
        return ["no_website"]
    if any(h in website.lower() for h in SOCIAL_HOSTS):
        return ["social_only"]
    final_url, html, secs = fetch(website)
    if html is None:
        return ["site_down"]
    low = html.lower()
    problems = []
    if not re.search(r'<meta[^>]+name=["\']?viewport', low):
        problems.append("not_mobile")
    if not final_url.startswith("https://"):
        problems.append("no_https")
    if secs > 4:
        problems.append("slow")
    years = [int(y) for y in re.findall(r"(?:©|&copy;|copyright)\D{0,20}((?:19|20)\d\d)", low)]
    if years and max(years) < date.today().year - 2:
        problems.append("outdated")
    if not any(m in low for m in BOOKING_MARKERS) and "<form" not in low:
        problems.append("no_booking")
    if not any(m in low for m in CHAT_MARKERS):
        problems.append("no_chat")
    return problems


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def score(row, problems):
    s = sum(PROBLEMS[p][0] for p in problems)
    # Busy, well-reviewed businesses have money and lose the most from a bad site.
    reviews = to_int(row.get("review_count"))
    s += min(reviews, 200) // 10
    if to_float(row.get("review_rating")) >= 4.0 and reviews >= 20:
        s += 10
    return s


def first_message(row, problems, sender):
    name = row.get("title", "there").strip()
    category = (row.get("category") or "business").strip().lower()
    reviews = to_int(row.get("review_count"))
    rating = to_float(row.get("review_rating"))
    praise = (f"You have {reviews} reviews at {rating:.1f} stars, so people clearly like you. "
              if reviews >= 10 and rating >= 4.0 else "")
    top = [PROBLEMS[p][1] for p in problems[:2]]
    if "no_website" in problems or "social_only" in problems or "site_down" in problems:
        offer = ("I build simple, fast websites for local businesses that show up on Google "
                 "and let customers call or book in one tap.")
    else:
        offer = ("I fix websites like this and can add an AI assistant that answers customer "
                 "questions and takes bookings 24/7, even when you are busy.")
    issues = " and ".join(top)
    return (f"Hi {name} team,\n\n"
            f"I was looking for a {category} nearby and found you on Google Maps. {praise}"
            f"I noticed {issues}. That usually means customers who search "
            f"for you pick a competitor instead.\n\n"
            f"{offer} I can show you a free sample of what yours could look like - "
            f"no cost, no obligation.\n\n"
            f"Would that be useful? A quick yes or no is fine.\n\n"
            f"{sender}\n"
            f"(If you'd rather not hear from me, just reply 'no' and I won't contact you again.)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_csv")
    ap.add_argument("--top", type=int, default=30, help="how many messages to write")
    ap.add_argument("--name", default="[Your name]", help="your name for the messages")
    ap.add_argument("--out", default="data")
    args = ap.parse_args()

    with open(args.results_csv, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Drop closed businesses, duplicates and ones we can't contact.
    seen, leads = set(), []
    for r in rows:
        key = (r.get("title", "").lower(), r.get("phone", ""))
        status = (r.get("status") or "").lower()
        if key in seen or "closed" in status:
            continue
        if not (r.get("phone") or r.get("emails")):
            continue
        seen.add(key)
        leads.append(r)

    print(f"Checking {len(leads)} businesses' websites...", file=sys.stderr)
    with ThreadPoolExecutor(max_workers=10) as pool:
        all_problems = list(pool.map(lambda r: check_site(r.get("website")), leads))

    ranked = sorted(zip(leads, all_problems), key=lambda x: score(*x), reverse=True)
    ranked = [(r, p) for r, p in ranked if p]  # businesses with no problems aren't leads

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "leads_ranked.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["score", "name", "category", "phone", "email", "website", "rating",
                    "reviews", "address", "problems", "maps_link", "status", "notes"])
        for r, p in ranked:
            w.writerow([score(r, p), r.get("title"), r.get("category"), r.get("phone"),
                        (r.get("emails") or "").split(",")[0], r.get("website"),
                        r.get("review_rating"), r.get("review_count"), r.get("address"),
                        "; ".join(PROBLEMS[x][1] for x in p), r.get("link"), "new", ""])

    with open(out / "messages.md", "w", encoding="utf-8") as f:
        f.write(f"# First messages - top {min(args.top, len(ranked))} leads\n\n")
        f.write("Edit one or two words in each so it sounds like you. "
                "Send 10-30 a day, not all at once.\n\n")
        for i, (r, p) in enumerate(ranked[:args.top], 1):
            contact = r.get("phone") or ""
            email = (r.get("emails") or "").split(",")[0]
            f.write(f"## {i}. {r.get('title')} (score {score(r, p)})\n")
            f.write(f"- Phone: {contact or '-'}  |  Email: {email or '-'}\n")
            f.write(f"- Website: {r.get('website') or 'none'}\n")
            f.write(f"- Problems: {'; '.join(PROBLEMS[x][1] for x in p)}\n\n")
            f.write("```\n" + first_message(r, p, args.name) + "\n```\n\n")

    print(f"Done. {len(ranked)} leads -> {out}/leads_ranked.csv, "
          f"messages -> {out}/messages.md", file=sys.stderr)


if __name__ == "__main__":
    main()
