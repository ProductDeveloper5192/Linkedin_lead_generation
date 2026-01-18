#!/usr/bin/env python3
"""
LinkedIn Hiring Posts Scraper (Multi-Country)

Directly searches LinkedIn for hiring posts.
Supports separate browser contexts and credentials for India and USA.

Usage:
    source venv/bin/activate
    python main.py                          # Default (India)
    python main.py --country usa            # Use USA context
    python main.py --country india --search "backend developer"
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from scraper.linkedin_scraper import (
    search_linkedin_posts,
    scrape_linkedin_posts,
    save_session,
)

# Load environment variables from .env file
load_dotenv()

# Available countries with their settings
COUNTRIES = {
    "india": {
        "name": "India", 
        "geo": {"latitude": 20.5937, "longitude": 78.9629, "accuracy": 100}, 
        "tz": "Asia/Kolkata", 
        "locale": "en-IN",
        "linkedin_subdomain": "in",
        "session_dir": "browser_session_india",
        "email_env": "LINKEDIN_EMAIL",
        "password_env": "LINKEDIN_PASSWORD"
    },
    "usa": {
        "name": "United States", 
        "geo": {"latitude": 37.7749, "longitude": -122.4194, "accuracy": 100}, 
        "tz": "America/Los_Angeles", 
        "locale": "en-US",
        "linkedin_subdomain": "www",
        "session_dir": "browser_session_usa",
        "email_env": "LINKEDIN_EMAIL_USA",
        "password_env": "LINKEDIN_PASSWORD_USA"
    },
}


def load_config() -> dict:
    """Load configuration from config.json."""
    config_path = Path(__file__).parent / "config.json"
    
    default_config = {
        "search_keywords": ["hiring", "we are hiring", "looking for", "job opening"],
        "job_titles": ["mobile developer", "app developer", "iOS developer", "android developer"],
        "max_results": 50,
        "delay_between_requests_seconds": 2,
        "headless": False,
    }
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            loaded = json.load(f)
            default_config.update(loaded)
    
    return default_config


def main():
    parser = argparse.ArgumentParser(description="LinkedIn Hiring Posts Scraper (Multi-Country)")
    parser.add_argument("--search", type=str, help="Search query (e.g. 'mobile developer hiring')")
    parser.add_argument("--max-results", type=int, help="Maximum number of results to scrape", default=50)
    parser.add_argument("--country", type=str, choices=list(COUNTRIES.keys()), default="india", help="Country to scrape from (india, usa)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    
    args = parser.parse_args()
    config = load_config()
    
    # Override config with CLI args
    if args.max_results:
        config["max_results"] = args.max_results
    if args.headless:
        config["headless"] = args.headless
    
    country_key = args.country
    country_info = COUNTRIES[country_key]
    
    # Determine search query
    search_query = args.search
    if not search_query:
        # Construct default query from config
        job = config["job_titles"][0]
        keyword = config["search_keywords"][0]
        search_query = f"{job} {keyword}"
    
    print("=" * 60)
    print("🔍 LinkedIn Hiring Posts Scraper")
    print("=" * 60)
    print(f"Search: {search_query}")
    print(f"Max results: {config['max_results']}")
    print(f"Country: {country_info['name']}")
    print(f"Session Dir: {country_info['session_dir']}")
    print(f"Headless: {config['headless']}")
    print("=" * 60 + "\n")
    
    # Get credentials for selected country
    email = os.getenv(country_info["email_env"])
    password = os.getenv(country_info["password_env"])
    
    if not email or not password:
        print(f"❌ Missing credentials for {country_info['name']}")
        print(f"   Please set {country_info['email_env']} and {country_info['password_env']} in .env")
        sys.exit(1)
        
    print(f"🔐 Using credentials for: {email}")

    # Setup browser with country-specific context
    with sync_playwright() as p:
        # Ensure session directory exists
        session_path = Path(__file__).parent / country_info["session_dir"]
        session_path.mkdir(exist_ok=True)
        
        print(f"🌍 Geolocation: {country_info['name']} ({country_info['geo']['latitude']}, {country_info['geo']['longitude']})")
        print(f"🕐 Timezone: {country_info['tz']}")
        print(f"🌐 Locale: {country_info['locale']}")
        
        # Launch persistent context
        # Note: No VPN extension loading anymore
        browser_args = [
            "--disable-blink-features=AutomationControlled",
        ]
        
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(session_path),
            headless=config["headless"],
            args=browser_args,
            viewport={"width": 1280, "height": 800},
            geolocation=country_info["geo"],
            permissions=["geolocation"],
            timezone_id=country_info["tz"],
            locale=country_info["locale"],
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Set extra headers for language
        context.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9"  # Defaulting to English generally, relying on locale for specifics
        })
        
        page = context.pages[0] if context.pages else context.new_page()
        
        try:
            # Step 1: Go directly to LinkedIn search - handle login only if needed
            linkedin_base = f"https://{country_info['linkedin_subdomain']}.linkedin.com"
            print(f"\n🔍 Searching LinkedIn ({linkedin_base}) for: {search_query}")
            
            post_urls = search_linkedin_posts(
                page,
                search_query,
                config["max_results"],
                config["delay_between_requests_seconds"],
                linkedin_subdomain=country_info["linkedin_subdomain"],
                email=email,
                password=password
            )
            
            if not post_urls:
                print("❌ No LinkedIn post URLs found")
                sys.exit(1)
            
            # Step 2: Scrape posts and filter for hiring posts only
            # Note: Scraper will use current page context
            scrape_linkedin_posts(
                page, 
                post_urls, 
                config["delay_between_requests_seconds"],
                filter_hiring_only=True
            )
            
            # Save session
            save_session(context)
            
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Persistent context closes automatically when leaving scope, but good to be explicit
            try:
                context.close()
            except:
                pass


if __name__ == "__main__":
    main()
