"""
Configuration manager for Wallpaper Downloader.
Stores settings in ~/.config/wallpaper/config.json with graceful fallback.
"""

import json
import os
from pathlib import Path

DEFAULT_DOWNLOAD_DIR = str(Path.home() / "Pictures" / "Wallpapers")
CONFIG_DIR = Path.home() / ".config" / "wallpaper"
CONFIG_FILE = CONFIG_DIR / "config.json"

RESOLUTIONS = {
    "4k": (3840, 2160),
    "5k": (5120, 2880),
    "8k": (7680, 4320),
    "retina": (3024, 1964),
    "ultrawide_1440p": (3440, 1440),
    "ultrawide_5k": (5120, 2160),
}

DEFAULT_CONFIG = {
    "download_dir": DEFAULT_DOWNLOAD_DIR,
    "default_resolution": "4k",
    "default_ratio": "all",  # "all", "16:9", "16:10", "21:9", "32:9"
    "default_count": 1,
    "default_sources": ["wallhaven", "unsplash", "reddit", "bing"],
    "sfw_only": True,
    "user_agent": "macOS-WallpaperVault/1.0.0"
}

def load_config() -> dict:
    """Load config from disk or return default config."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(data)
                return merged
    except Exception:
        pass
    return DEFAULT_CONFIG.copy()

def save_config(cfg: dict) -> bool:
    """Save config to disk with exception handling."""
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def get_download_dir(custom_dir: str = None) -> Path:
    """Get the target download directory."""
    if custom_dir:
        target = Path(os.path.expanduser(custom_dir))
    else:
        cfg = load_config()
        target = Path(os.path.expanduser(cfg.get("download_dir", DEFAULT_DOWNLOAD_DIR)))
    try:
        target.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return target
