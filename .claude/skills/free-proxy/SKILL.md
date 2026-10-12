---
name: free-proxy
description: Get a fresh list of free public proxies (HTTP, HTTPS, SOCKS4, SOCKS5) filtered by country, anonymity, reliability and latency, from the proxio.io list. Use when the user asks for free proxies, a proxy list, a proxy for a country, or proxies to paste into AdsPower, Donut Browser or another anti-detect browser.
---

# Free proxy list

Run the bundled filter script from the repository root. It needs only Python 3.8+.

```bash
python3 proxy-tools/proxy_list.py [options]
```

Pick options from the user's request:

| Option | Default | Use when |
|---|---|---|
| `--country US,GB` | any | user names countries (2-letter codes) |
| `--protocol socks5` | `http` | user wants `https`, `socks4` or `socks5` |
| `--limit 20` | 200 | user wants a specific number |
| `--min-reliability 50` | 70 | too few results, especially for SOCKS5 |
| `--max-latency 5` | 3 | too few results |
| `--test` | off | user wants proxies checked live (HTTP/HTTPS only) |
| `--out file.txt` | `proxies.txt` | user wants a different file |

If the script prints "No proxies matched", loosen `--min-reliability` and `--max-latency` or drop `--country`, and say so.

After running, show the user the best few proxies from the output file and where it was saved.

Always tell the user:
- These are public datacenter-type proxies, not residential, so strict sites often block them.
- They die quickly, so re-run before each session.
- Never log in or enter passwords through them, because the proxy operator can see the traffic.

In a cloud Claude Code session, `--test` usually fails because outbound connections to proxy ports are blocked. Skip it there and tell the user to run the test on their own machine.

Data: proxio.io, CC BY 4.0.
