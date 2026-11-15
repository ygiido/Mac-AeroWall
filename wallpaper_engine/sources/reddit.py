"""
Reddit Wallpaper Source Provider.
Queries high quality wallpaper subreddits (r/wallpapers, r/WQHD_Wallpaper, r/MultiWall, r/EarthPorn).
"""

import json
import urllib.parse
import urllib.request
import ssl
import re
from typing import List, Optional
from .base import BaseSource, WallpaperItem

class RedditSource(BaseSource):
    name = "reddit"
    SUBREDDITS = ["wallpapers", "WQHD_Wallpaper", "MultiWall", "EarthPorn"]

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

        # Extract resolution if mentioned in Reddit titles like [3840x2160] or [4K]
        res_pattern = re.compile(r"\[?(\d{4})\s*[xX×]\s*(\d{4})\]?")

        for sub in self.SUBREDDITS:
            if len(results) >= count:
                break
            try:
                params = {
                    "q": query,
                    "restrict_sr": 1,
                    "sort": "top",
                    "t": "all",
                    "limit": 20
                }
                url = f"https://www.reddit.com/r/{sub}/search.json?{urllib.parse.urlencode(params)}"
                headers = {
                    "User-Agent": "macOS:wallpaper-cli:v1.0.0 (by /u/mac_user)"
                }
                req = urllib.request.Request(url, headers=headers)
                ctx = ssl.create_default_context()

                with urllib.request.urlopen(req, timeout=8, context=ctx) as response:
                    if response.status != 200:
                        continue
                    data = json.loads(response.read().decode("utf-8"))

                posts = data.get("data", {}).get("children", [])
                for p in posts:
                    post_data = p.get("data", {})
                    post_url = post_data.get("url", "")
                    title = post_data.get("title", "")

                    # Check if direct image link
                    if not (post_url.endswith(".jpg") or post_url.endswith(".png") or post_url.endswith(".jpeg")):
                        continue

                    # Check title for resolution
                    match = res_pattern.search(title)
                    w, h = 3840, 2160  # default assumption if in 4k wallpaper sub
                    if match:
                        w, h = int(match.group(1)), int(match.group(2))
                        if w < min_width and h < min_height:
                            continue

                    post_id = post_data.get("id", "")
                    preview = post_data.get("thumbnail", post_url)

                    results.append(
                        WallpaperItem(
                            id=post_id,
                            source=f"reddit/r/{sub}",
                            title=title[:60],
                            url=post_url,
                            preview_url=preview,
                            width=w,
                            height=h,
                            ratio="16:9" if round(w/max(h,1), 2) == 1.78 else "other",
                            file_type=post_url.split(".")[-1],
                            file_size=None,
                            tags=[sub, query]
                        )
                    )

                    if len(results) >= count:
                        break

            except Exception:
                continue

        return results
