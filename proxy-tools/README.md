# Free proxy list filter

`proxy_list.py` downloads the free [proxio.io proxy list](https://github.com/proxio-io/proxy-list)
(about 15,000 proxies, refreshed every 20 minutes, CC BY 4.0) and keeps only the good ones:
Elite anonymity, high reliability, low latency, and your chosen country and protocol.

These are public datacenter-type proxies, not residential. Never log in or enter passwords through them.

## Install

1. Install Python 3.8+.
   - **Windows:** run `winget install Python.Python.3.12`, or download it from python.org and tick "Add to PATH".
   - **Mac:** Python 3 is usually already installed. Check with `python3 --version`, or run `brew install python`.
2. Download `proxy_list.py` into a folder, for example `Documents/proxy-tools`.
3. No extra packages are needed.

## Use

Open a terminal in that folder. On Windows, use `python` instead of `python3`.

```bash
python3 proxy_list.py                                  # best HTTP proxies, any country
python3 proxy_list.py --country US --test              # US HTTP proxies, live-tested now
python3 proxy_list.py --country US,GB --protocol socks5
python3 proxy_list.py --max-latency 5 --min-reliability 50   # looser filter, more results
```

The script writes `proxies.txt` with one proxy per line, like `socks5://1.2.3.4:1080`.

| Option | Default | Meaning |
|---|---|---|
| `--protocol` | `http` | `http`, `https`, `socks4` or `socks5` |
| `--country` | any | 2-letter codes, comma separated |
| `--min-reliability` | 70 | proxio's 0–100 reliability score |
| `--max-latency` | 3 | seconds |
| `--limit` | 200 | max proxies saved |
| `--test` | off | live-test HTTP/HTTPS proxies before saving |
| `--allow-anonymous` | off | also keep "Anonymous" proxies (never "Transparent") |

Free proxies die quickly. Re-run the script before each session.

## Use in AdsPower or Donut Browser

Profile → Proxy → pick the type (HTTP or SOCKS5) → paste the host and port from one line of
`proxies.txt` → **Check proxy** → save.
