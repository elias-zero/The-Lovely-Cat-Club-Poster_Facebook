#!/usr/bin/env python3
from PIL import Image
from io import BytesIO
import requests

def download_and_make_square(url, out_path, size=1080):
    """
    Download image from `url`, center-crop to square, resize to (size x size)
    and save as JPEG to out_path. Returns out_path.
    """
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    img = Image.open(BytesIO(r.content)).convert('RGB')

    w, h = img.size
    min_side = min(w, h)
    left = (w - min_side) // 2
    top = (h - min_side) // 2
    img = img.crop((left, top, left + min_side, top + min_side))
    img = img.resize((size, size), Image.LANCZOS)
    img.save(out_path, format='JPEG', quality=92)
    return out_path

def cataas_random_square_url(size=1080):
    """
    Return a CATAAS URL requesting an image roughly of given size.
    We still download and process locally to guarantee exact 1080x1080.
    """
    return f'https://cataas.com/cat?width={size}&height={size}'
