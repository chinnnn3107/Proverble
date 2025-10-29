import random, re, unicodedata
from pathlib import Path
from typing import Tuple, List, Dict

def normalize_proverb(s: str) -> str:
        s = unicodedata.normalize("NFC", s)     
        s = s.strip()
        s = re.sub(r"[.,;!?\"'()\-]", "", s)
        s = re.sub(r"\s+", " ", s)              
        return s.upper()

# Load proverbs and hints or folk sayings from a text file.
def load_proverbs_with_hints(path: str = "ProverbList.txt") -> Tuple[List[str], Dict[str, str]]:
    proverbs_raw: List[str] = []
    emoji_map: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "," in line:
                left, right = line.split(",", 1)
                answer_raw = left.strip()         
                emoji_hint = right.strip()
            else:
                answer_raw = line
                emoji_hint = ""
            if answer_raw:
                proverbs_raw.append(answer_raw)
            norm = normalize_proverb(answer_raw)
            if norm and emoji_hint:
                emoji_map[norm] = emoji_hint
    if not proverbs_raw:
        raise ValueError("Empty proverb list")
    return proverbs_raw, emoji_map

# Select a random proverb from the given list.
def choose_random_proverb(proverbs):
    return random.choice(proverbs)