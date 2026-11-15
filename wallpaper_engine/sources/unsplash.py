"""
Unsplash Source Provider.
Provides high quality photography and landscapes in Ultra-HD resolutions.
"""

import json
import urllib.parse
import urllib.request
import ssl
from typing import List, Optional
from .base import BaseSource, WallpaperItem

class UnsplashSource(BaseSource):
    name = "unsplash"
    SEARCH_URL = "https://unsplash.com/napi/search/photos"

    def search(
        self,
        query: str,
        min_width: int = 3840,
        min_height: int = 2160,
        ratios: Optional[List[str]] = None,
        categories: str = "111",
        count: int = 5
    ) -> List[WallpaperItem]:
        results: List[WallpaperItem] = []
        try:
            params = {
                "query": query,
                "per_page": max(count * 2, 10),
                "orientation": "landscape"
            }
            url = f"{self.SEARCH_URL}?{urllib.parse.urlencode(params)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json"
            }
            req = urllib.request.Request(url, headers=headers)
            ctx = ssl.create_default_context()

            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                if response.status != 200:
                    return results
                data = json.loads(response.read().decode("utf-8"))

            items = data.get("results", [])
            for item in items:
                width = int(item.get("width", 0))
                height = int(item.get("height", 0))

                # Ensure resolution is at least 4K or close high-res landscape
                if width < 3000 or height < 1800:
                    continue

                img_id = item.get("id", "")
                raw_url = item.get("urls", {}).get("raw", "")
                if not raw_url:
                    continue

                # Unsplash raw URL allows requesting maximum resolution
                download_url = f"{raw_url}&w={max(width, min_width)}&q=95&auto=format"
                preview_url = item.get("urls", {}).get("regular", raw_url)
                desc = item.get("alt_description") or item.get("description") or f"Unsplash {img_id}"

                ratio_val = round(width / max(height, 1), 2)
                ratio_str = "16:9" if 1.7 <= ratio_val <= 1.85 else ("16:10" if 1.55 <= ratio_val < 1.7 else f"{ratio_val}:1")

                results.append(
                    WallpaperItem(
                        id=str(img_id),
                        source=self.name,
                        title=desc[:50],
                        url=download_url,
                        preview_url=preview_url,
                        width=width,
                        height=height,
                        ratio=ratio_str,
                        file_type="jpg",
                        file_size=None,
                        tags=[query]
                    )
                )

                if len(results) >= count:
                    break

        except Exception:
            pass

        return results
