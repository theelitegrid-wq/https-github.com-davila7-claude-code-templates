# Client Hunter

Finds local businesses that need a website or AI help, ranks them, and writes the first message.
You send the messages and close the deals. Claude builds what you sell.

## What's inside

| File | What it does |
|---|---|
| `tools/find_leads.sh` | Searches Google Maps for businesses in your city, then ranks them |
| `tools/qualify_leads.py` | Checks each business's website (none? broken? not mobile? no booking?) and scores how likely they are to buy |
| `PLAYBOOK.md` | What to sell, prices, phone script, follow-ups, objections, how to close |
| `data/` (created when you run it) | `leads_ranked.csv` = your lead list, `messages.md` = ready first messages |

Lead finding uses the open-source [gosom/google-maps-scraper](https://github.com/gosom/google-maps-scraper) (MIT).

## How to run it (on your computer)

1. Install **Docker Desktop** and **Python 3**, and start Docker.
2. Download this repo.
3. Run, using your own city and name:
   ```bash
   MY_NAME="Alex" tools/find_leads.sh "Austin, TX"
   ```
   Or pick niches: `tools/find_leads.sh "Dubai" dentist "car repair" salon`
4. After ~10 minutes, open `data/leads_ranked.csv` and `data/messages.md`.
5. Follow `PLAYBOOK.md`.

On Windows, run step 3 in WSL or Git Bash. Or open this folder in Claude Code and say *"find leads in [city]"*.

Already have a list from another tool? Use `python3 tools/qualify_leads.py your_list.csv --name "Alex"`.
It needs columns `title, category, website, phone, review_count, review_rating` (`emails` is optional).
