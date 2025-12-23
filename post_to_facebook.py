#!/usr/bin/env python3
"""
Post a daily cat photo from CATAAS to a Facebook Page using the Page Access Token.
Requires env vars: FB_PAGE_ACCESS_TOKEN and FB_PAGE_ID
"""
import os
import random
import requests
import sys
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

FB_TOKEN = os.getenv("FB_PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("FB_PAGE_ID")
CAPTIONS_FILE = os.getenv("CAPTIONS_FILE", "captions.txt")
CATAAS_JSON = "https://cataas.com/cat?json=true"

if not FB_TOKEN or not PAGE_ID:
    logging.error("Missing FB_PAGE_ACCESS_TOKEN or FB_PAGE_ID environment variables.")
    sys.exit(1)


def load_captions(path=CAPTIONS_FILE):
    try:
        with open(path, encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        if not lines:
            raise ValueError("No captions found")
        return lines
    except Exception as e:
        logging.warning(f"Could not load captions from {path}: {e}")
        return ["Cute cat alert! 🐾"]


def pick_caption(captions):
    return random.choice(captions)


def get_cat_image_url():
    try:
        r = requests.get(CATAAS_JSON, timeout=15)
        r.raise_for_status()
        data = r.json()
        # data often contains 'url' or 'id'
        if isinstance(data, list) and data:
            data = data[0]
        if isinstance(data, dict):
            if 'url' in data:
                url = data['url']
                return url if url.startswith('http') else 'https://cataas.com' + url
            if 'id' in data:
                return f"https://cataas.com/cat/{data['id']}"
        # fallback to generic endpoint
        return 'https://cataas.com/cat'
    except Exception as e:
        logging.error(f"Failed to fetch cat image from CATAAS: {e}")
        raise


def post_photo_to_facebook(image_url, message):
    endpoint = f"https://graph.facebook.com/{PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "message": message,
        "access_token": FB_TOKEN
    }
    try:
        r = requests.post(endpoint, data=payload, timeout=30)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        logging.error(f"Facebook API error: {e} - {r.text if 'r' in locals() else ''}")
        raise


def main():
    captions = load_captions()
    caption = pick_caption(captions)
    logging.info(f"Selected caption: {caption}")

    image_url = get_cat_image_url()
    logging.info(f"Fetched image URL: {image_url}")

    resp = post_photo_to_facebook(image_url, caption)
    logging.info(f"Posted to Facebook: {resp}")


if __name__ == '__main__':
    main()
