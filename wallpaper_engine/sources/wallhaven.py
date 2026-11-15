"""
Wallhaven Source Provider.
Wallhaven (wallhaven.cc) has one of the best curated collections of 4K/8K wallpapers.
"""

import json
import urllib.parse
import urllib.request
import ssl
from typing import List, Optional
from .base import BaseSource, WallpaperItem

class WallhavenSource(BaseSource):
    name = "wallhaven"
    BASE_URL = "https://wallhaven.cc/api/v1/search"

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
                "q": query,
                "atleast": f"{min_width}x{min_height}",
                "categories": categories,
                "purity": "100",  # SFW only
                "sorting": "relevance",
                "order": "desc",
                "page": 1
            }

            if ratios:
                # Wallhaven expects format "16x9,16x10"
                formatted_ratios = [r.replace(":", "x") for r in ratios]
                params["ratios"] = ",".join(formatted_ratios)

            url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
            req = urllib.request.Request(url, headers=headers)
            ctx = ssl.create_default_context()

            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                if response.status != 200:
                    return results
                data = json.loads(response.read().decode("utf-8"))

            items = data.get("data", [])
            for item in items[:count]:
                dim_x = int(item.get("dimension_x", 0))
                dim_y = int(item.get("dimension_y", 0))
                file_type = item.get("file_type", "image/jpeg").split("/")[-1]
                ratio_raw = item.get("ratio", "")
                
                results.append(
                    WallpaperItem(
                        id=str(item.get("id")),
                        source=self.name,
                        title=f"Wallhaven {item.get('id')} ({dim_x}x{dim_y})",
                        url=item.get("path"),
                        preview_url=item.get("thumbs", {}).get("large", item.get("path")),
                        width=dim_x,
                        height=dim_y,
                        ratio=ratio_raw,
                        file_type=file_type,
                        file_size=item.get("file_size"),
                        tags=item.get("tags")
                    )
                )

        except Exception as e:
            # Source query failed or timed out
            pass

        return results
