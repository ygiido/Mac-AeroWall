"""
macOS 4K/8K Wallpaper Downloader Package.
"""

from .config import load_config, save_config, get_download_dir
from .query_parser import parse_prompt, ParsedQuery
from .sources import search_wallpapers, ALL_SOURCES
from .downloader import download_wallpaper, DownloadResult

__version__ = "1.0.0"
