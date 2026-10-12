#!/usr/bin/env python3
"""Download the free proxio.io proxy list and keep only the good proxies.

Data: https://github.com/proxio-io/proxy-list (CC BY 4.0, attribute proxio.io).
Needs only Python 3.8+ — no extra packages.

Examples:
  python proxy_list.py                          # Elite, reliable, fast, any country
  python proxy_list.py --country US --protocol socks5
  python proxy_list.py --country US --test      # also live-test HTTP(S) proxies
"""
import argparse
import concurrent.futures
import json
import sys
import urllib.request

LIST_URL = "https://raw.githubusercontent.com/proxio-io/proxy-list/main/all.json"
TEST_URL = "http://api.ipify.org"
PROTOCOLS = {"http": "HTTP", "https": "HTTPS", "socks4": "SOCKS4", "socks5": "SOCKS5"}


def download():
    req = urllib.request.Request(LIST_URL, headers={"User-Agent": "proxy-list-filter"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)


def keep(p, args):
    if p.get("anonymity") != "Elite" and not args.allow_anonymous:
        return False
    if args.allow_anonymous and p.get("anonymity") == "Transparent":
        return False
    if PROTOCOLS[args.protocol] not in p.get("protocols", []):
        return False
    if args.country and p.get("code", "").upper() not in args.country:
        return False
    if (p.get("reliability") or 0) < args.min_reliability:
        return False
    latency = p.get("latency_s")
    if latency is None or latency > args.max_latency:
        return False
    return p.get("fail_streak", 0) == 0


def live_test(p, timeout):
    """Return True if an HTTP(S) proxy can fetch a page right now."""
    proxy = f"http://{p['ip']}:{p['port']}"
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    try:
        with opener.open(TEST_URL, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--protocol", choices=PROTOCOLS, default="http")
    ap.add_argument("--country", type=lambda s: {c.strip().upper() for c in s.split(",")},
                    help="2-letter country codes, comma separated (e.g. US,GB)")
    ap.add_argument("--min-reliability", type=float, default=70)
    ap.add_argument("--max-latency", type=float, default=3.0, help="seconds")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--allow-anonymous", action="store_true",
                    help="also keep 'Anonymous' (never 'Transparent') proxies")
    ap.add_argument("--test", action="store_true",
                    help="live-test HTTP/HTTPS proxies before saving")
    ap.add_argument("--out", default="proxies.txt")
    args = ap.parse_args()

    print("Downloading proxio.io list...")
    data = download()
    picked = [p for p in data["proxies"] if keep(p, args)]
    picked.sort(key=lambda p: (-(p.get("reliability") or 0), p["latency_s"]))
    print(f"{len(picked)} of {data['count']} proxies match (list updated {data['updated_at']})")

    if args.test:
        if args.protocol.startswith("socks"):
            print("--test only works for http/https; skipping live test.")
        else:
            candidates = picked[: args.limit * 3]
            print(f"Live-testing {len(candidates)} proxies...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=50) as pool:
                ok = list(pool.map(lambda p: live_test(p, args.max_latency + 5), candidates))
            picked = [p for p, good in zip(candidates, ok) if good]
            print(f"{len(picked)} passed the live test")

    picked = picked[: args.limit]
    if not picked:
        sys.exit("No proxies matched. Try --max-latency 5 or a different --country.")

    scheme = "http" if args.protocol == "https" else args.protocol
    with open(args.out, "w") as f:
        for p in picked:
            f.write(f"{scheme}://{p['ip']}:{p['port']}\n")
    print(f"Saved {len(picked)} proxies to {args.out}")
    best = picked[0]
    print(f"Best one: {best['ip']}:{best['port']}  {best['country']}  "
          f"{best['latency_s']}s  reliability {best['reliability']}")


if __name__ == "__main__":
    main()
