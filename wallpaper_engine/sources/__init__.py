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
    total_count: int = 5
) -> List[WallpaperItem]:
    """
    Search across requested sources (or all sources by default).
    Deduplicates and returns up to total_count items.
    """
    selected_sources = []
    if sources and "all" not in sources:
        for s in sources:
            src = get_source(s)
            if src:
                selected_sources.append(src)
    else:
        # Default order: Wallhaven first (highest resolution accuracy), then Unsplash, Reddit, Bing
        selected_sources = [
            ALL_SOURCES["wallhaven"],
            ALL_SOURCES["unsplash"],
            ALL_SOURCES["reddit"],
            ALL_SOURCES["bing"]
        ]

    combined_results: List[WallpaperItem] = []
    seen_urls = set()

    # Per source limit
    per_source = max(2, total_count // len(selected_sources) + 1)

    for src in selected_sources:
        try:
            items = src.search(
                query=query,
                min_width=min_width,
                min_height=min_height,
                ratios=ratios,
                categories=categories,
                count=per_source
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
