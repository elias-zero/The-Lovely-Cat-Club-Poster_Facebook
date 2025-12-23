#!/usr/bin/env python3
import random, json
from pathlib import Path
from datetime import datetime, timedelta

BASE = Path('.')
COMPONENTS_FILE = BASE / 'components.json'
FILES = {
    'basic': BASE / 'captions_basic.txt',
    'no_color': BASE / 'captions_no_color.txt',
    'attr': BASE / 'captions_attr.txt',
    'color_attr': BASE / 'captions_color_attr.txt'
}
HISTORY = BASE / 'posted_history.json'

# config
MAX_HISTORY_ENTRIES = 500
AVOID_DAYS = 30
AVOID_LAST_N = 30

def load_lines(p: Path):
    return [l.strip() for l in p.read_text(encoding='utf-8').splitlines() if l.strip()] if p.exists() else []

def load_components():
    if COMPONENTS_FILE.exists():
        return json.loads(COMPONENTS_FILE.read_text(encoding='utf-8'))
    return {}

components = load_components()

basic_pool = load_lines(FILES['basic'])
no_color_pool = load_lines(FILES['no_color'])
attr_pool = load_lines(FILES['attr'])
color_attr_pool = load_lines(FILES['color_attr'])

if HISTORY.exists():
    try:
        history = json.loads(HISTORY.read_text(encoding='utf-8'))
    except Exception:
        history = []
else:
    history = []

def save_history(entry):
    history.append(entry)
    new_hist = history[-MAX_HISTORY_ENTRIES:]
    HISTORY.write_text(json.dumps(new_hist, ensure_ascii=False, indent=2), encoding='utf-8')

def recent_captions():
    return [h['caption'] for h in history]

def caption_used_recently(caption):
    last_n = [h['caption'] for h in history[-AVOID_LAST_N:]]
    if caption in last_n:
        return True
    cutoff = datetime.utcnow() - timedelta(days=AVOID_DAYS)
    for h in history[::-1]:
        try:
            ts = datetime.fromisoformat(h['time'])
        except Exception:
            continue
        if ts < cutoff:
            break
        if h['caption'] == caption:
            return True
    return False

def choose_template_key(tags):
    color_terms = set(['orange','white','black','gray','brown','ginger','tabby'])
    tags_set = set(t.lower() for t in tags)
    has_color = bool(tags_set & color_terms)
    has_attr = len(tags) > 0 and (len(tags_set - color_terms) > 0)
    if has_color and has_attr:
        return 'color_attr'
    if has_attr and not has_color:
        return 'attr'
    if not has_attr and not has_color:
        return 'no_color'
    return 'basic'

def fill_placeholders(template, tags):
    intro = random.choice(components.get('intros', ['Look at this kitty!']))
    cta = random.choice(components.get('ctas', ['Name it!']))
    descriptor = random.choice(components.get('descriptors', ['adorable']))
    emoji_map = components.get('emojis', {})

    color = next((t for t in tags if t in ['orange','white','black','gray','brown','ginger','tabby']), None)
    attr = next((t for t in tags if t != color), None)

    color_word = color if color else ''
    color_adj = color_word
    attr_word = attr if attr else ''
    attr_desc = attr_word
    emoji = emoji_map.get(attr, emoji_map.get(color, emoji_map.get('default','🐾')))

    s = template
    s = s.replace('{intro}', intro)
    s = s.replace('{cta}', cta)
    s = s.replace('{descriptor}', descriptor)
    s = s.replace('{emoji}', emoji)
    s = s.replace('{color_word}', color_word)
    s = s.replace('{color_adj}', color_adj)
    s = s.replace('{attr_word}', attr_word)
    s = s.replace('{attr_desc}', attr_desc)
    return s

def generate_caption(tags):
    # Public function used by post_to_facebook.py
    key = choose_template_key(tags)
    pool = {'basic': basic_pool, 'no_color': no_color_pool, 'attr': attr_pool, 'color_attr': color_attr_pool}.get(key, basic_pool)
    if not pool:
        pool = basic_pool or ['Cute! 🐾']

    tries = 0
    while tries < 30:
        template = random.choice(pool)
        caption = fill_placeholders(template, tags)
        if not caption_used_recently(caption):
            entry = {'time': datetime.utcnow().isoformat(), 'caption': caption}
            save_history(entry)
            return caption
        tries += 1

    caption = (fill_placeholders(random.choice(pool), tags)) + ' ' + random.choice(['🐾','❤️','😺'])
    entry = {'time': datetime.utcnow().isoformat(), 'caption': caption}
    save_history(entry)
    return caption

# allow quick local test without interfering import
if __name__ == '__main__':
    print(generate_caption(['orange','sleeping','kitten']))
