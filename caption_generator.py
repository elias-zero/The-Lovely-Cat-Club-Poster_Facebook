#!/usr/bin/env python3
"""
Generates captions based on tags, avoids repeats for 30 days or last 30 posts.
Reads component lists and caption templates.
Saves posted history with timestamps to posted_history.json
"""
import random
import json
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

# helpers
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
    history = json.loads(HISTORY.read_text(encoding='utf-8'))
else:
    history = []

# utilities

def save_history(entry):
    history.append(entry)
    # keep size reasonable
    new_hist = history[-MAX_HISTORY_ENTRIES:]
    HISTORY.write_text(json.dumps(new_hist, ensure_ascii=False, indent=2), encoding='utf-8')


def recent_captions():
    return [h['caption'] for h in history]


def caption_used_recently(caption):
    # check last N
    last_n = [h['caption'] for h in history[-AVOID_LAST_N:]]
    if caption in last_n:
        return True
    # check within days
    cutoff = datetime.utcnow() - timedelta(days=AVOID_DAYS)
    for h in history[::-1]:
        ts = datetime.fromisoformat(h['time'])
        if ts < cutoff:
            break
        if h['caption'] == caption:
            return True
    return False


def choose_template_key(tags):
    color_terms = set(['orange','white','black','gray','brown','ginger','tabby'])
    tags_set = set(t.lower() for t in tags)
    has_color 
