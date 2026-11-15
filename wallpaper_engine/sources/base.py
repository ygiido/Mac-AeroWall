"""
Base abstractions for wallpaper data and providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class WallpaperItem:
    id: str
    source: str
    title: str
    url: str               # Direct download URL for full-res image
    preview_url: str       # Thumbnail or preview URL
    width: int
    height: int
    ratio: str             # e.g. "16:9", "16:10", "21:9"
    file_type: str         # "jpg", "png", "webp"
    file_size: Optional[int] = None
    tags: Optional[List[str]] = None

    @property
    def resolution_str(self) -> str:
        return f"{self.width}x{self.height}"

    @property
    def is_4k_or_more(self) -> bool:
        # 4K standard is 3840x2160 (or approx 8.29 million pixels)
        # 16:10 MacBook Retina (e.g. 3024x1964 or 3456x2234) or Ultrawide 3440x1440
        return (self.width >= 3840 and self.height >= 2160) or (self.width * self.height >= 7000000)

    @property
    def is_8k(self) -> bool:
        return self.width >= 7680 or (self.width * self.height >= 30000000)

class BaseSource(ABC):
    name: str = "base"

    @abstractmethod
    def search(
        self,
        query: str,
        min_width: int = 3840,
        min_height: int = 2160,
        ratios: Optional[List[str]] = None,
        categories: str = "111",
        count: int = 5
    ) -> List[WallpaperItem]:
        """
        Search for wallpapers meeting criteria.
        Returns a list of WallpaperItem.
        """
        pass
