"""
Downloader module for high resolution wallpapers.
Handles streaming download, progress updates, duplicate detection, and file integrity.
"""

import os
import re
import ssl
import sys
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable
from .sources.base import WallpaperItem
from .config import get_download_dir

@dataclass
class DownloadResult:
    success: bool
    item: WallpaperItem
    file_path: Optional[Path] = None
    file_size_bytes: int = 0
    error_message: Optional[str] = None
    already_existed: bool = False
    duration_seconds: float = 0.0

def slugify(text: str) -> str:
    """Convert text to safe filename slug."""
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text).strip("_")
    return text[:30] if text else "wallpaper"

def download_wallpaper(
    item: WallpaperItem,
    query_slug: str = "wallpaper",
    custom_dir: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None
) -> DownloadResult:
    """
    Downloads a single wallpaper to the target directory.
    """
    start_time = time.time()
    dest_dir = get_download_dir(custom_dir)

    # Determine file extension
    ext = item.file_type.lower().replace("jpeg", "jpg")
    if not ext or ext not in ["jpg", "png", "webp"]:
        # Try inferring from url
        if ".png" in item.url.lower():
            ext = "png"
        elif ".webp" in item.url.lower():
            ext = "webp"
        else:
            ext = "jpg"

    # Construct clean filename
    safe_src = item.source.replace("/", "_")
    safe_slug = slugify(query_slug)
    filename = f"{safe_slug}_{safe_src}_{item.width}x{item.height}_{item.id}.{ext}"
    target_path = dest_dir / filename

    # Check if already downloaded
    if target_path.exists() and target_path.stat().st_size > 50000:
        return DownloadResult(
            success=True,
            item=item,
            file_path=target_path,
            file_size_bytes=target_path.stat().st_size,
            already_existed=True,
            duration_seconds=time.time() - start_time
        )

    temp_path = dest_dir / f"{filename}.part"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://wallhaven.cc/"
    }

    try:
        req = urllib.request.Request(item.url, headers=headers)
        ctx = ssl.create_default_context()

        with urllib.request.urlopen(req, timeout=30, context=ctx) as response:
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            chunk_size = 65536  # 64 KB

            with open(temp_path, "wb") as f:
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)

        # Move from .part to final target
        if temp_path.exists():
            temp_path.rename(target_path)

        final_size = target_path.stat().st_size
        return DownloadResult(
            success=True,
            item=item,
            file_path=target_path,
            file_size_bytes=final_size,
            already_existed=False,
            duration_seconds=time.time() - start_time
        )

    except Exception as e:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass
        return DownloadResult(
            success=False,
            item=item,
            error_message=str(e),
            duration_seconds=time.time() - start_time
        )
