# LinkedIn Hiring Posts Scraper with VPN

Directly searches LinkedIn for hiring posts with VPN country selection.

## Setup

```bash
cd /Users/Shared/kittybabai/linkedin-scraper
source venv/bin/activate
```

## Create .env with LinkedIn credentials:
```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password_here
```

## Usage

```bash
source venv/bin/activate

# Default (Netherlands)
python main.py

# With specific country
python main.py --country usa
python main.py --country uk
python main.py --country france
python main.py --country singapore
python main.py --country russia

# With options
python main.py --country usa --max-results 20
python main.py --country uk --search "flutter developer"

# Disable VPN extension (use only geolocation spoofing)
python main.py --country usa --no-vpn
```

## Available Countries

| Country | Flag | Timezone | Locale |
|---------|------|----------|--------|
| france | 🇫🇷 | Europe/Paris | fr-FR |
| netherlands | 🇳🇱 | Europe/Amsterdam | nl-NL |
| russia | 🇷🇺 | Europe/Moscow | ru-RU |
| singapore | 🇸🇬 | Asia/Singapore | en-SG |
| uk | 🇬🇧 | Europe/London | en-GB |
| usa | 🇺🇸 | America/Los_Angeles | en-US |

## Features

- 🌐 **VPN Extension**: VeePN extension for real IP masking
- 🌍 **Geolocation Spoofing**: Browser geolocation set to country
- 🕐 **Timezone**: Matches selected country
- ✅ **Hiring Posts Only**: Filters out job seekers
- 💾 **Persistent Session**: Saves login across runs

## Output

- `data/results.json` - Scraped hiring posts
- `browser_session/chrome_profile/` - Persistent browser profile
