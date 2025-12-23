#!/usr/bin/env python3
import os
import sys
import logging
import requests
from pathlib import Path
from caption_generator import generate_caption
from image_utils import download_and_make_square, cataas_random_square_url

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

FB_TOKEN = os.getenv('FB_PAGE_ACCESS_TOKEN')
PAGE_ID = os.getenv('FB_PAGE_ID')
TEMP_IMAGE = '/tmp/cat_post.jpg'

if not FB_TOKEN or not PAGE_ID:
    logging.error('Missing FB_PAGE_ACCESS_TOKEN or FB_PAGE_ID environment variables.')
    sys.exit(1)

# simple color detector (no external ML)
from PIL import Image
from io import BytesIO

def detect_color_simple(image_url):
    try:
        r = requests.get(image_url, timeout=15)
        r.raise_for_status()
        img = Image.open(BytesIO(r.content)).convert('RGB')
        img = img.resize((120,120))
        pixels = list(img.getdata())
        color_counts = {'orange':0,'white':0,'black':0,'gray':0,'brown':0,'other':0}
        for rr,gg,bb in pixels:
            if rr>150 and gg<130 and bb<120:
                color_counts['orange'] += 1
            elif rr>200 and gg>200 and bb>200:
                color_counts['white'] += 1
            elif rr<60 and gg<60 and bb<60:
                color_counts['black'] += 1
            elif abs(rr-gg)<15 and abs(gg-bb)<15 and 100<rr<200:
                color_counts['gray'] += 1
            elif rr>120 and gg>80 and bb<80:
                color_counts['brown'] += 1
            else:
                color_counts['other'] += 1
        dominant = max(color_counts, key=color_counts.get)
        return dominant if color_counts[dominant] > (len(pixels)*0.05) else 'other'
    except Exception as e:
        logging.warning(f'Color detect failed: {e}')
        return 'other'

def post_photo(image_path, message):
    endpoint = f'https://graph.facebook.com/{PAGE_ID}/photos'
    with open(image_path, 'rb') as f:
        files = {'source': f}
        data = {'message': message, 'access_token': FB_TOKEN}
        r = requests.post(endpoint, files=files, data=data, timeout=60)
        r.raise_for_status()
        return r.json()

def main():
    # request slightly larger image then crop/resize to 1080
    cataas_url = cataas_random_square_url(1200)
    color_tag = detect_color_simple(cataas_url)
    tags = [t for t in [color_tag] if t and t != 'other']

    download_and_make_square(cataas_url, TEMP_IMAGE, size=1080)

    caption = generate_caption(tags)
    logging.info(f'Caption: {caption}')

    resp = post_photo(TEMP_IMAGE, caption)
    logging.info(f'Posted: {resp}')

if __name__ == '__main__':
    main()
