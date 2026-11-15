"""
Command-line interface for the wallpaper downloader.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List

from .config import load_config, save_config, get_download_dir, RESOLUTIONS
from .query_parser import parse_prompt
from .sources import search_wallpapers
from .downloader import download_wallpaper, DownloadResult
from .macos_stock import sync_stock_wallpapers

# ANSI Colors for terminal output
BOLD = "\033[1m"
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RED = "\033[31m"
DIM = "\033[2m"
RESET = "\033[0m"

def render_progress_bar(current: int, total: int, width: int = 30) -> None:
    """Print terminal progress bar."""
    if total <= 0:
        sys.stdout.write(f"\r  {CYAN}Downloading...{RESET} {current / 1024 / 1024:.2f} MB")
        sys.stdout.flush()
        return

    fraction = min(1.0, current / total)
    filled = int(width * fraction)
    bar = "█" * filled + "░" * (width - filled)
    percent = int(fraction * 100)
    current_mb = current / (1024 * 1024)
    total_mb = total / (1024 * 1024)
    sys.stdout.write(f"\r  {CYAN}[{bar}]{RESET} {percent:3d}% ({current_mb:.1f}/{total_mb:.1f} MB)")
    sys.stdout.flush()

def format_bytes(size: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="wallpaper",
        description="macOS 4K/8K Wallpaper Downloader: Automatically find and download ultra-HD wallpapers for macOS displays."
    )

    parser.add_argument(
        "prompt",
        nargs="*",
        help="Search topic, person, context, or style (e.g., 'tokyo rain neon', 'steve jobs minimalist', 'space nebula 8k')"
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=1,
        help="Number of wallpapers to download (default: 1)"
    )
    parser.add_argument(
        "-o", "--dir",
        type=str,
        default=None,
        help="Custom download directory (default: ~/Pictures/Wallpapers)"
    )
    parser.add_argument(
        "-r", "--res",
        type=str,
        default=None,
        choices=["4k", "5k", "8k", "retina"],
        help="Minimum resolution (4k: 3840x2160, 5k: 5120x2880, 8k: 7680x4320, retina: 3024x1964)"
    )
    parser.add_argument(
        "--ratio",
        type=str,
        default=None,
        help="Target aspect ratio: 16:9, 16:10, 21:9, 32:9 or 'all'"
    )
    parser.add_argument(
        "-s", "--source",
        type=str,
        default="all",
        choices=["all", "wallhaven", "unsplash", "reddit", "bing"],
        help="Wallpaper source provider (default: all)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Search and list wallpapers without downloading"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON results"
    )
    parser.add_argument(
        "--set-dir",
        type=str,
        default=None,
        help="Permanently update default download directory"
    )
    parser.add_argument(
        "--macos-stock",
        action="store_true",
        help="Download and sync all official 6K macOS stock wallpapers"
    )

    args = parser.parse_args()

    # Handle directory update
    if args.set_dir:
        cfg = load_config()
        cfg["download_dir"] = str(Path(args.set_dir).expanduser().resolve())
        save_config(cfg)
        print(f"{GREEN}✓ Default download directory updated to:{RESET} {cfg['download_dir']}")
        return 0

    prompt_text = " ".join(args.prompt).strip()

    # Handle macOS stock sync
    if args.macos_stock or prompt_text.lower() in ["macos-stock", "stock", "update-stock", "macos stock"]:
        cfg = load_config()
        base_dir = get_download_dir(args.dir)
        stock_dir = base_dir / "macos stock"
        res = sync_stock_wallpapers(stock_dir)
        return 0 if not res["failed"] else 1
    if not prompt_text:
        parser.print_help()
        print(f"\n{YELLOW}Örnek kullanım:{RESET}")
        print("  wallpaper \"yağmurlu tokyo gecesi neon\"")
        print("  wallpaper \"steve jobs minimalist\" --res 8k")
        print("  wallpaper \"kara delik uzay\" --ratio 21:9 -n 3")
        print("  wallpaper \"cyberpunk car\" --dir ~/Desktop/Wallpapers")
        return 1

    cfg = load_config()

    # 1. Parse prompt
    parsed = parse_prompt(prompt_text)

    # Resolve resolution
    res_key = args.res or parsed.target_resolution or cfg.get("default_resolution", "4k")
    min_w, min_h = RESOLUTIONS.get(res_key, (3840, 2160))

    # Resolve ratio
    ratio_arg = args.ratio or parsed.target_ratio or cfg.get("default_ratio", "all")
    ratios_list = None
    if ratio_arg != "all":
        ratios_list = [r.strip() for r in ratio_arg.split(",")]

    target_sources = [args.source] if args.source != "all" else cfg.get("default_sources", ["wallhaven", "unsplash", "reddit", "bing"])
    download_folder = get_download_dir(args.dir)

    if not args.json:
        print(f"\n{BOLD}{MAGENTA}✦ macOS Wallpaper Downloader{RESET}")
        print(f"{DIM}──────────────────────────────────────────{RESET}")
        print(f"{BOLD}Arama İstemi :{RESET} {CYAN}{parsed.original}{RESET}")
        print(f"{BOLD}Optimize Sorgu:{RESET} {GREEN}{parsed.search_query}{RESET}")
        print(f"{BOLD}Hedef Kalite :{RESET} {YELLOW}{res_key.upper()} (min {min_w}x{min_h}){RESET}")
        if ratios_list:
            print(f"{BOLD}Ekran Oranı  :{RESET} {', '.join(ratios_list)}")
        print(f"{BOLD}Hedef Klasör :{RESET} {download_folder}")
        print(f"{DIM}──────────────────────────────────────────{RESET}")
        print(f"{CYAN}🔍 Kaynaklar taranıyor ({', '.join(target_sources)})...{RESET}")

    # 2. Search wallpapers
    wallpapers = search_wallpapers(
        query=parsed.search_query,
        sources=target_sources,
        min_width=min_w,
        min_height=min_h,
        ratios=ratios_list,
        categories=parsed.categories,
        total_count=max(args.count * 2, 6)
    )

    if not wallpapers:
        # Fallback search with broader terms if no result
        if len(parsed.keywords) > 2:
            broad_query = " ".join(parsed.keywords[:2])
            wallpapers = search_wallpapers(
                query=broad_query,
                sources=target_sources,
                min_width=min_w,
                min_height=min_h,
                ratios=ratios_list,
                categories="111",
                total_count=args.count
            )

    if not wallpapers:
        if args.json:
            print(json.dumps({"error": "No wallpapers found matching criteria", "query": parsed.search_query}))
        else:
            print(f"{RED}✖ Belirtilen kriterlere uygun 4K/8K wallpaper bulunamadı.{RESET}")
            print(f"{DIM}İpucu: Aramayı biraz daha genel tutmayı veya çözünürlük filtresini esnetmeyi deneyin.{RESET}\n")
        return 1

    # 3. Handle --list or --json
    if args.list:
        print(f"\n{GREEN}Bulunan Görseller ({len(wallpapers)} adet):{RESET}")
        for idx, w in enumerate(wallpapers[:args.count], 1):
            print(f" {idx}. [{w.source}] {w.title}")
            print(f"    Çözünürlük: {w.width}x{w.height} ({w.ratio}) | URL: {w.url}")
        return 0

    if args.json and not args.list:
        # If json is requested with download, do download and output json
        pass

    # 4. Download wallpapers
    items_to_download = wallpapers[:args.count]
    results: List[DownloadResult] = []

    if not args.json:
        print(f"\n{BOLD}{GREEN}⬇ {len(items_to_download)} adet görsel indiriliyor...{RESET}\n")

    for i, item in enumerate(items_to_download, 1):
        if not args.json:
            print(f"{BOLD}[{i}/{len(items_to_download)}]{RESET} {item.title} {DIM}({item.width}x{item.height} - {item.source}){RESET}")

        res = download_wallpaper(
            item=item,
            query_slug=parsed.search_query,
            custom_dir=str(download_folder),
            progress_callback=render_progress_bar if not args.json else None
        )
        results.append(res)

        if not args.json:
            sys.stdout.write("\n")
            if res.success:
                status = f"{YELLOW}[Zaten Mevcut]{RESET}" if res.already_existed else f"{GREEN}[İndirildi]{RESET}"
                size_str = format_bytes(res.file_size_bytes)
                print(f"  {status} {res.file_path.name} ({size_str})")
            else:
                print(f"  {RED}[Hata]{RESET} {res.error_message}")
            print()

    # 5. Output summary
    if args.json:
        output_payload = {
            "query": parsed.original,
            "optimized_query": parsed.search_query,
            "resolution": res_key,
            "download_dir": str(download_folder),
            "results": [
                {
                    "success": r.success,
                    "title": r.item.title,
                    "source": r.item.source,
                    "resolution": f"{r.item.width}x{r.item.height}",
                    "ratio": r.item.ratio,
                    "file_path": str(r.file_path) if r.file_path else None,
                    "file_size": r.file_size_bytes,
                    "already_existed": r.already_existed,
                    "error": r.error_message
                }
                for r in results
            ]
        }
        print(json.dumps(output_payload, indent=2, ensure_ascii=False))
    else:
        success_count = sum(1 for r in results if r.success)
        print(f"{DIM}──────────────────────────────────────────{RESET}")
        print(f"{BOLD}{GREEN}✓ İşlem Tamamlandı!{RESET} {success_count}/{len(items_to_download)} görsel hazır.")
        print(f"{BOLD}Klasör:{RESET} {CYAN}{download_folder}{RESET}\n")

    return 0 if any(r.success for r in results) else 1

if __name__ == "__main__":
    sys.exit(main())
