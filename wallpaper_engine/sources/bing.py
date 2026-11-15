"""
Bing Daily Wallpaper UHD Provider.
Fetches pristine 4K Ultra-HD landscape & nature images from Microsoft Bing's global archives.
"""

import json
import urllib.parse
import urllib.request
import ssl
from typing import List, Optional
from .base import BaseSource, WallpaperItem

class BingSource(BaseSource):
    name = "bing"
    ARCHIVE_URL = "https://www.bing.com/HPImageArchive.aspx"

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
            # Fetch recent Bing daily wallpapers in UHD 4K
            params = {
                "format": "js",
                "idx": 0,
                "n": 8,
                "mkt": "en-US",
                "uhd": 1,
                "uhdwidth": 3840,
                "uhdheight": 2160
            }
            url = f"{self.ARCHIVE_URL}?{urllib.parse.urlencode(params)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            req = urllib.request.Request(url, headers=headers)
            ctx = ssl.create_default_context()

            with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
                if response.status != 200:
                    return results
                data = json.loads(response.read().decode("utf-8"))

            images = data.get("images", [])
            query_lower = query.lower()

            for img in images:
                title = img.get("title") or img.get("copyright") or "Bing UHD Wallpaper"
                # If query is generic nature/landscape or words match in copyright/title, include it
                if query_lower in ["", "nature", "landscape", "all", "bing", "daily"] or any(
                    w in title.lower() for w in query_lower.split()
                ):
                    urlbase = img.get("urlbase")
                    if urlbase:
                        # Full UHD 4K download link
                        full_url = f"https://www.bing.com{urlbase}_UHD.jpg"
                    else:
                        full_url = f"https://www.bing.com{img.get('url')}"

                    img_id = img.get("hsh") or img.get("startdate") or str(len(results))

                    results.append(
                        WallpaperItem(
                            id=img_id[:12],
                            source=self.name,
                            title=title[:60],
                            url=full_url,
                            preview_url=full_url,
                            width=3840,
                            height=2160,
                            ratio="16:9",
                            file_type="jpg",
                            file_size=None,
                            tags=["nature", "bing", "landscape"]
                        )
                    )

                    if len(results) >= count:
                        break

        except Exception:
            pass

        return results
