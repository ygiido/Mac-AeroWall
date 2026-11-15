"""
Smart query parser and prompt expander.
Translates Turkish or natural language prompts into optimized search queries and filter tags.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

# Turkish to English keyword translation dictionary for wallpaper terms
TRANSLATIONS = {
    # Themes & Moods
    "yağmurlu": "rainy",
    "yağmur": "rain",
    "gecesi": "night",
    "gece": "night",
    "karanlık": "dark moody",
    "aydınlık": "bright",
    "ışıkları": "lights",
    "ışıklar": "lights",
    "ışık": "light",
    "neon": "neon",
    "siberpunk": "cyberpunk",
    "fütüristik": "futuristic",
    "minimal": "minimalist",
    "minimalist": "minimalist",
    "sade": "clean minimal",
    "retro": "retro synthwave",
    "nostaljik": "vintage retro",
    "lofi": "lofi aesthetic",
    "estetik": "aesthetic",
    "gün batımı": "sunset",
    "gün doğumu": "sunrise",
    "şafak": "dawn sunrise",
    "sisli": "foggy misty",
    "sis": "fog mist",
    "bulutlu": "cloudy dramatic sky",
    "bulutlar": "clouds",
    "bulut": "cloud",
    "fırtına": "storm thunder",
    "şimşek": "lightning thunder",
    "karlı": "snow snowy winter",
    "kış": "winter snow",
    "sonbahar": "autumn fall",
    "ilkbahar": "spring blossom",
    "yaz": "summer sunny",

    # Nature & Scenery
    "doğa": "nature",
    "doğal": "natural scenery",
    "manzara": "landscape scenery",
    "manzarası": "landscape scenery",
    "dağ": "mountain mountains",
    "dağlar": "mountains alps",
    "dağları": "mountains alps",
    "orman": "forest woods",
    "ormanı": "forest woods",
    "ağaçlar": "trees forest",
    "deniz": "ocean sea waves",
    "denizi": "ocean sea",
    "okyanus": "ocean deep water",
    "sahil": "beach coastline",
    "plaj": "beach tropical",
    "göl": "lake reflection",
    "gölü": "lake reflection",
    "nehir": "river stream",
    "şelale": "waterfall",
    "çöl": "desert dunes",
    "çölü": "desert dunes",
    "yıldızlar": "stars starry sky milky way",
    "yıldızlı": "starry night",
    "yıldız": "star starry",
    "gökyüzü": "sky celestial",
    "uzay": "deep space galaxy cosmos",
    "derin": "deep",
    "galaksi": "galaxy nebula",
    "nebula": "nebula cosmic",
    "kara delik": "black hole cosmos",
    "karadelik": "black hole cosmos",
    "gezegen": "planet celestial",
    "gezegenler": "planets cosmic",
    "ay": "moon lunar",
    "hilal": "crescent moon",
    "dolunay": "full moon",
    "güneş": "sun solar flare",

    # Urban & Architecture
    "şehir": "city cityscape skyline",
    "şehri": "city skyline",
    "sokak": "street alley",
    "sokağı": "street alley",
    "sokaklar": "streets alleys",
    "cadde": "street avenue",
    "caddesi": "street avenue",
    "bina": "architecture buildings",
    "binalar": "architecture skyscrapers",
    "gökdelen": "skyscraper skyline",
    "gökdelenler": "skyscrapers skyline",
    "köprü": "bridge architecture",
    "köprüsü": "bridge architecture",
    "japon": "japan tokyo",
    "japonya": "japan",
    "tokyo": "tokyo japan",
    "new york": "new york manhattan",
    "istanbul": "istanbul bosphorus",

    # Vehicles & Tech
    "araba": "car automotive",
    "arabalar": "supercars cars",
    "otomobil": "supercar car",
    "yolu": "road highway",
    "yol": "road path",
    "otoban": "highway freeway",
    "motosiklet": "motorcycle bike",
    "uçak": "airplane aviation",
    "uzay gemisi": "spaceship scifi",
    "teknoloji": "technology scifi",
    "kodlama": "coding programmer matrix",
    "yazılım": "software code programming",
    "siber": "cyber scifi",

    # Art & Style
    "anime": "anime art",
    "manga": "manga style",
    "çizim": "illustration artwork",
    "illüstrasyon": "illustration digital art",
    "sanat": "digital art artwork",
    "yağlı boya": "oil painting art",
    "soyut": "abstract geometry",
    "geometrik": "geometric abstract",
    "siyah beyaz": "black and white monochrome",
    "tek renk": "monochrome",

    # Colors
    "mavi": "blue",
    "kırmızı": "red",
    "yeşil": "green",
    "sarı": "yellow",
    "mor": "purple violet",
    "turuncu": "orange",
    "pembe": "pink",
    "siyah": "black dark",
    "beyaz": "white clean",
    "altın": "gold golden",
    "gümüş": "silver metallic",
}

# Stopwords and filler expressions
STOPWORDS = {
    "bir", "biri", "birkaç", "tane", "ve", "ile", "veya", "ya", "da", "de",
    "için", "gibi", "kadar", "olan", "tüm", "her", "daha", "en", "çok",
    "var", "yok", "şu", "bu", "o", "bana", "bize", "bunu", "şunu", "onu",
    "indir", "bul", "getir", "ayarla", "istiyorum", "lütfen", "hadi",
    "güzel", "harika", "mükemmel", "kaliteli", "yüksek", "çözünürlük",
    "çözünürlüklü", "uyumlu", "wallpaper", "arka", "plan", "arkaplan",
    "duvar", "kağıdı", "duvarkağıdı", "masaüstü", "desktop", "ekran",
    "resim", "fotoğraf", "görsel", "mac", "macbook", "macos", "apple"
}

@dataclass
class ParsedQuery:
    original: str
    search_query: str
    target_resolution: Optional[str] = None  # "4k", "8k", "5k"
    target_ratio: Optional[str] = None       # "16:9", "16:10", "21:9"
    categories: str = "111"                 # 100=general, 110=general+anime, 111=all
    keywords: List[str] = None

def parse_prompt(user_prompt: str) -> ParsedQuery:
    """
    Parses user prompt, extracts resolution/ratio hints,
    translates Turkish terms to English search keywords, and cleans noise.
    """
    raw = user_prompt.strip()
    lower = raw.lower()

    # Detect resolution preferences
    res = None
    if "8k" in lower or "7680x4320" in lower:
        res = "8k"
    elif "5k" in lower or "5120x2880" in lower:
        res = "5k"
    elif "4k" in lower or "uhd" in lower or "3840x2160" in lower:
        res = "4k"

    # Detect aspect ratio preferences
    ratio = None
    if "ultrawide" in lower or "21:9" in lower or "21x9" in lower:
        ratio = "21:9"
    elif "32:9" in lower or "super ultrawide" in lower:
        ratio = "32:9"
    elif "16:10" in lower or "16x10" in lower or "retina" in lower:
        ratio = "16:10"
    elif "16:9" in lower or "16x9" in lower:
        ratio = "16:9"

    cleaned = lower
    # Remove resolution/ratio keywords from search string
    cleaned = re.sub(r"\b(4k|8k|5k|uhd|retina|ultrawide|16:9|16:10|21:9|32:9)\b", " ", cleaned)

    # Check for multi-word phrases first
    translated_tokens = []
    for tr_key in sorted(TRANSLATIONS.keys(), key=len, reverse=True):
        pattern = r"\b" + re.escape(tr_key) + r"\b"
        if re.search(pattern, cleaned):
            translated_tokens.append(TRANSLATIONS[tr_key])
            cleaned = re.sub(pattern, " ", cleaned)

    # Process remaining tokens
    tokens = re.split(r"[^\w\s-]", cleaned)
    for part in tokens:
        for w in part.split():
            w = w.strip()
            if not w or len(w) < 2 or w in STOPWORDS:
                continue
            if w in TRANSLATIONS:
                translated_tokens.append(TRANSLATIONS[w])
            else:
                translated_tokens.append(w)

    # Deduplicate while preserving order
    seen = set()
    final_keywords = []
    for token_group in translated_tokens:
        for word in token_group.split():
            w_lower = word.lower()
            if w_lower not in seen and w_lower not in STOPWORDS:
                seen.add(w_lower)
                final_keywords.append(word)

    search_query = " ".join(final_keywords) if final_keywords else raw

    # Detect category hint
    categories = "111"
    if any(k in search_query.lower() for k in ["anime", "manga", "waifu"]):
        categories = "010"
    elif any(k in search_query.lower() for k in ["person", "portrait", "actor", "actress", "model", "woman", "man", "girl", "boy"]):
        categories = "001"

    return ParsedQuery(
        original=raw,
        search_query=search_query,
        target_resolution=res,
        target_ratio=ratio,
        categories=categories,
        keywords=final_keywords
    )
