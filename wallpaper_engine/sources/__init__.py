"""
Wallpaper Sources Registry and Aggregator.
"""

from typing import List, Optional
from .base import BaseSource, WallpaperItem
from .wallhaven import WallhavenSource
from .unsplash import UnsplashSource
from .reddit import RedditSource
from .bing import BingSource

ALL_SOURCES = {
    "wallhaven": WallhavenSource(),
    "unsplash": UnsplashSource(),
    "reddit": RedditSource(),
    "bing": BingSource()
}

def get_source(name: str) -> Optional[BaseSource]:
    return ALL_SOURCES.get(name.lower())

def search_wallpapers(
    query: str,
    sources: Optional[List[str]] = None,
    min_width: int = 3840,
    min_height: int = 2160,
    ratios: Optional[List[str]] = None,
    categories: str = "111",
    total_count: int = 10
) -> List[WallpaperItem]:
    """
    Search across requested sources.
    Fetches up to total_count items without artificial per-source throttling.
    Automatically falls back to Retina (2560x1440) if strict 4K results are fewer than requested.
    """
    selected_sources = []
    if sources and "all" not in sources:
        for s in sources:
            src = get_source(s)
            if src:
                selected_sources.append(src)
    else:
        # Default order: Wallhaven (best 4K/8K anime, art & general), Unsplash, Reddit, Bing
        selected_sources = [
            ALL_SOURCES["wallhaven"],
            ALL_SOURCES["unsplash"],
            ALL_SOURCES["reddit"],
            ALL_SOURCES["bing"]
        ]

    combined_results: List[WallpaperItem] = []
    seen_urls = set()

    # Pass 1: Strict resolution search
    for src in selected_sources:
        needed = total_count - len(combined_results)
        if needed <= 0:
            break
        try:
            items = src.search(
                query=query,
                min_width=min_width,
                min_height=min_height,
                ratios=ratios,
                categories=categories,
                count=max(needed * 2, 10)  # Request enough to satisfy
            )
            for item in items:
                if item.url not in seen_urls:
                    seen_urls.add(item.url)
                    combined_results.append(item)
                    if len(combined_results) >= total_count:
                        return combined_results
        except Exception:
            continue

    # Pass 2: Graceful fallback to Retina 2K+ (2560x1440) if still need more items
    if len(combined_results) < total_count and (min_width > 2560 or min_height > 1440):
        for src in selected_sources:
            needed = total_count - len(combined_results)
            if needed <= 0:
                break
            try:
                items = src.search(
                    query=query,
                    min_width=2560,
                    min_height=1440,
                    ratios=ratios,
                    categories=categories,
                    count=needed * 2
                )
                for item in items:
                    if item.url not in seen_urls:
                        seen_urls.add(item.url)
                        combined_results.append(item)
                        if len(combined_results) >= total_count:
                            return combined_results
            except Exception:
                continue

    return combined_results[:total_count]
