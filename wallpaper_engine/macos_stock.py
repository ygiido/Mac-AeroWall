"""
macOS & Apple Official Stock Wallpapers Sync and Updater.
Syncs:
1. Official macOS 6K releases (Cheetah -> Sequoia -> Tahoe -> Golden Gate)
2. Vintage Mac OS 9 & 1984 Macintosh 5K collection
3. High-end aesthetic, minimalist community MacBook/Apple wallpapers (4K/5K/8K)
Supports incremental sync, daily auto-check, and macOS notifications.
"""

import os
import re
import ssl
import subprocess
import sys
import time
import json
import urllib.parse
import urllib.request
from pathlib import Path
from typing import List, Dict, Tuple

MACOS_ARCHIVE_URL = "https://512pixels.net/projects/default-mac-wallpapers-in-5k/"
MACOS9_ARCHIVE_URL = "https://512pixels.net/projects/mac-os-9-5k-wallpapers/"

# Friendly naming mapping for clean file identification
FRIENDLY_NAMES = {
    # Mac OS X / macOS 6K
    "10-0_10-1-6k.jpg": "01_macOS_10.0_Cheetah_Puma_6K.jpg",
    "10-2-6k.jpg": "02_macOS_10.2_Jaguar_6K.jpg",
    "10-3-6k.jpg": "03_macOS_10.3_Panther_6K.jpg",
    "10-4-6k.jpg": "04_macOS_10.4_Tiger_6K.jpg",
    "10-5-6k.jpg": "05_macOS_10.5_Leopard_6K.jpg",
    "10-5-Server-6k.jpg": "05_macOS_10.5_Leopard_Server_6K.jpg",
    "10-6-6k.jpg": "06_macOS_10.6_Snow_Leopard_6K.jpg",
    "10-6-Server-6k.jpg": "06_macOS_10.6_Snow_Leopard_Server_6K.jpg",
    "10-7-6k.jpg": "07_macOS_10.7_Lion_6K.jpg",
    "10-8-6k.jpg": "08_macOS_10.8_Mountain_Lion_6K.jpg",
    "10-9-6k.jpg": "09_macOS_10.9_Mavericks_6K.jpg",
    "10-10-6k.jpg": "10_macOS_10.10_Yosemite_6K.jpg",
    "10-11-6k.jpg": "11_macOS_10.11_El_Capitan_6K.jpg",
    "10-12-6k.jpg": "12_macOS_10.12_Sierra_6K.jpg",
    "10-13-6k.jpg": "13_macOS_10.13_High_Sierra_6K.jpg",
    "10-14-Day-6k.jpg": "14_macOS_10.14_Mojave_Day_6K.jpg",
    "10-14-Night-6k.jpg": "14_macOS_10.14_Mojave_Night_6K.jpg",
    "10-15-Day-6k.jpg": "15_macOS_10.15_Catalina_Day_6K.jpg",
    "10-15-Night-6k.jpg": "15_macOS_10.15_Catalina_Night_6K.jpg",
    "11-Big-Sur-Day-6k.jpg": "16_macOS_11_Big_Sur_Photo_Day_6K.jpg",
    "11-Big-Sur-Night-6k.jpg": "16_macOS_11_Big_Sur_Photo_Night_6K.jpg",
    "11-Big-Sur-Color-Day-6k.jpg": "16_macOS_11_Big_Sur_Graphic_Day_6K.jpg",
    "11-Big-Sur-Color-Night-6k.jpg": "16_macOS_11_Big_Sur_Graphic_Night_6K.jpg",
    "12-Monterey-Light.jpg": "17_macOS_12_Monterey_Light_6K.jpg",
    "12-Monterey-Dark.jpg": "17_macOS_12_Monterey_Dark_6K.jpg",
    "13-Ventura-Light.jpg": "18_macOS_13_Ventura_Light_6K.jpg",
    "13-Ventura-Dark.jpg": "18_macOS_13_Ventura_Dark_6K.jpg",
    "14-Sonoma-Light.jpg": "19_macOS_14_Sonoma_Light_6K.jpg",
    "14-Sonoma-Dark.jpg": "19_macOS_14_Sonoma_Dark_6K.jpg",
    "14-Sonoma-Horizon.png": "19_macOS_14_Sonoma_Horizon_6K.png",
    "15-Sequoia-Light-6K.jpg": "20_macOS_15_Sequoia_Light_6K.jpg",
    "15-Sequoia-Dark-6K.jpg": "20_macOS_15_Sequoia_Dark_6K.jpg",
    "15-Sequoia-Sunrise.png": "20_macOS_15_Sequoia_Sunrise_6K.png",
    "26-Tahoe-Light-6K.png": "21_macOS_Tahoe_Light_6K.png",
    "26-Tahoe-Dark-6K.png": "21_macOS_Tahoe_Dark_6K.png",
    "26-Tahoe-Beach-Dawn.png": "21_macOS_Tahoe_Beach_Dawn_6K.png",
    "26-Tahoe-Beach-Day.png": "21_macOS_Tahoe_Beach_Day_6K.png",
    "26-Tahoe-Beach-Dusk.png": "21_macOS_Tahoe_Beach_Dusk_6K.png",
    "26-Tahoe-Beach-Night.png": "21_macOS_Tahoe_Beach_Night_6K.png",
    "27-Golden-Gate-Bridge.jpg": "22_macOS_Golden_Gate_Bridge_Photo_6K.jpg",
    "27-Golden-Gate.png": "22_macOS_Golden_Gate_Light_6K.png",
    "27-Golden-Gate-Dark.png": "22_macOS_Golden_Gate_Dark_6K.png",

    # Mac OS 9 & Vintage Macintosh 5K
    "Mac-OS-Background.jpg": "00_Vintage_Macintosh_Classic_Desktop_5K.jpg",
    "Blueberry-Oxygen.jpg": "00_Mac_OS_9_Blueberry_Oxygen_5K.jpg",
    "Blueberry-Union.jpg": "00_Mac_OS_9_Blueberry_Union_5K.jpg",
    "Flower-Power.jpg": "00_Mac_OS_9_iMac_Flower_Power_5K.jpg",
    "Blue-Dalmation.jpg": "00_Mac_OS_9_iMac_Blue_Dalmation_5K.jpg",
    "Grape-Gravity.jpg": "00_Mac_OS_9_Grape_Gravity_5K.jpg",
    "Grape-Mission.jpg": "00_Mac_OS_9_Grape_Mission_5K.jpg",
    "Lime-Horizon.jpg": "00_Mac_OS_9_Lime_Horizon_5K.jpg",
    "Lime-Sharp.jpg": "00_Mac_OS_9_Lime_Sharp_5K.jpg",
    "Strawberry-Parabola.jpg": "00_Mac_OS_9_Strawberry_Parabola_5K.jpg",
    "Strawbery-Baby.jpg": "00_Mac_OS_9_Strawberry_Baby_5K.jpg",
    "Tangerine-Fusion.jpg": "00_Mac_OS_9_Tangerine_Fusion_5K.jpg",
    "Tangerine-Melt.jpg": "00_Mac_OS_9_Tangerine_Melt_5K.jpg",
    "Golden-Poppy.jpg": "00_Mac_OS_9_Golden_Poppy_5K.jpg",
    "Quantum-Foam.jpg": "00_Mac_OS_9_Quantum_Foam_5K.jpg",
    "Shutters.jpg": "00_Mac_OS_9_Shutters_5K.jpg",
    "Bottles-1.jpg": "00_Mac_OS_9_Bottles_5K.jpg",
    "Tub.jpg": "00_Mac_OS_9_Tub_5K.jpg",
    "UFO-1.jpg": "00_Mac_OS_9_UFO_1_5K.jpg",
    "UFO-2.jpg": "00_Mac_OS_9_UFO_2_5K.jpg",
}

def notify_user(title: str, message: str, subtitle: str = ""):
    """Send native macOS notification banner with chime."""
    sub_clause = f'subtitle "{subtitle}"' if subtitle else ""
    script = f'''display notification "{message}" with title "{title}" {sub_clause} sound name "Glass"'''
    try:
        subprocess.run(["osascript", "-e", script], check=False)
    except Exception:
        pass

def fetch_all_stock_urls() -> List[Tuple[str, str]]:
    """
    Scrapes official macOS 6K, Mac OS 9 5K, and curated aesthetic MacBook wallpapers.
    Returns list of (url, target_filename).
    """
    items: List[Tuple[str, str]] = []
    seen = set()
    ctx = ssl.create_default_context()
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

    # 1. Fetch macOS 6K links
    try:
        req = urllib.request.Request(MACOS_ARCHIVE_URL, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            html = r.read().decode("utf-8")
            links = re.findall(
                r'href=[\"\'](https://media\.512pixels\.net/downloads/macos-wallpapers-6k/[^\"\']+)[\"\']',
                html
            )
            for l in links:
                if l not in seen:
                    seen.add(l)
                    raw_name = l.split("/")[-1]
                    name = FRIENDLY_NAMES.get(raw_name, raw_name)
                    items.append((l, name))
    except Exception as e:
        print(f"Error fetching macOS 6K links: {e}")

    # 2. Fetch Mac OS 9 / Vintage Macintosh links
    try:
        req9 = urllib.request.Request(MACOS9_ARCHIVE_URL, headers=headers)
        with urllib.request.urlopen(req9, timeout=15, context=ctx) as r:
            html = r.read().decode("utf-8")
            links9 = re.findall(
                r'href=[\"\'](https://media\.512pixels\.net/wp-content/uploads/2020/11/[^\"\']+\.(?:jpg|png))[\"\']',
                html
            )
            for l in links9:
                if l not in seen:
                    seen.add(l)
                    raw_name = l.split("/")[-1]
                    name = FRIENDLY_NAMES.get(raw_name, raw_name)
                    items.append((l, name))
    except Exception as e:
        print(f"Error fetching Mac OS 9 links: {e}")

    # 3. Fetch Curated Aesthetic & Minimal MacBook Wallpapers (Wallhaven 5K/8K API)
    aesthetic_queries = ["apple minimal", "apple logo", "apple dark", "macbook minimalist"]
    for query in aesthetic_queries:
        try:
            params = {
                "q": query,
                "atleast": "3840x2160",
                "categories": "100",  # general
                "purity": "100",      # SFW only
                "sorting": "toplist",
                "topRange": "1y"
            }
            url = f"https://wallhaven.cc/api/v1/search?{urllib.parse.urlencode(params)}"
            req_wh = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req_wh, timeout=10, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                for img in data.get("data", [])[:3]:  # Top 3 per aesthetic category
                    img_url = img.get("path")
                    if img_url and img_url not in seen:
                        seen.add(img_url)
                        dim_x = img.get("dimension_x", "4K")
                        dim_y = img.get("dimension_y", "")
                        ext = img.get("file_type", "image/jpeg").split("/")[-1]
                        slug = query.replace(" ", "_")
                        safe_name = f"Aesthetic_MacBook_{slug}_{dim_x}x{dim_y}_{img.get('id')}.{ext}"
                        items.append((img_url, safe_name))
        except Exception:
            continue

    return items

def sync_stock_wallpapers(target_dir: Path, notify: bool = False, quiet: bool = False) -> Dict[str, any]:
    """
    Downloads all 6K/5K macOS, Macintosh, and aesthetic MacBook wallpapers into target_dir.
    Skips any already downloaded files.
    Triggers macOS notification if new wallpapers are downloaded.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    items = fetch_all_stock_urls()

    downloaded = []
    skipped = []
    failed = []

    if not quiet:
        print(f"\n\033[1m\033[35m✦ macOS, Macintosh & Minimal MacBook Duvar Kağıdı Senkronizasyonu\033[0m")
        print(f"\033[2m──────────────────────────────────────────────────────────────────\033[0m")
        print(f"Toplam taranan arşiv görseli: \033[36m{len(items)}\033[0m")
        print(f"Hedef Klasör: \033[33m{target_dir}\033[0m")
        print(f"\033[2m──────────────────────────────────────────────────────────────────\033[0m\n")

    ctx = ssl.create_default_context()
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Referer": "https://512pixels.net/"
    }

    for idx, (url, dest_name) in enumerate(items, 1):
        out_path = target_dir / dest_name

        if out_path.exists() and out_path.stat().st_size > 50000:
            if not quiet:
                print(f"[{idx}/{len(items)}] \033[33m[Mevcut]\033[0m {dest_name} ({out_path.stat().st_size / 1024 / 1024:.1f} MB)")
            skipped.append(dest_name)
            continue

        if not quiet:
            print(f"[{idx}/{len(items)}] \033[32m[İndiriliyor]\033[0m {dest_name}...")
        temp_path = target_dir / f"{dest_name}.part"

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=40, context=ctx) as resp:
                with open(temp_path, "wb") as f:
                    while True:
                        chunk = resp.read(131072)  # 128 KB
                        if not chunk:
                            break
                        f.write(chunk)
            if temp_path.exists():
                temp_path.rename(out_path)
            size_mb = out_path.stat().st_size / 1024 / 1024
            if not quiet:
                print(f"       \033[32m✓ Tamamlandı:\033[0m {dest_name} ({size_mb:.1f} MB)")
            downloaded.append(dest_name)
        except Exception as e:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            if not quiet:
                print(f"       \033[31m✖ Hata:\033[0m {e}")
            failed.append((dest_name, str(e)))

    if not quiet:
        print(f"\n\033[2m──────────────────────────────────────────────────────────────────\033[0m")
        print(f"\033[1m\033[32m✓ Senkronizasyon Tamamlandı!\033[0m")
        print(f"Yeni indirilen : \033[32m{len(downloaded)}\033[0m")
        print(f"Zaten mevcut   : \033[33m{len(skipped)}\033[0m")
        if failed:
            print(f"Başarısız      : \033[31m{len(failed)}\033[0m")
        print(f"Klasör         : \033[36m{target_dir}\033[0m\n")

    # Send macOS notification if new wallpapers were downloaded
    if notify and downloaded:
        notify_user(
            title="Mac AeroWall Güncellendi",
            message=f"{len(downloaded)} yeni MacBook duvar kağıdı iCloud Drive klasörünüze eklendi.",
            subtitle="iCloud Drive / ygiido wallpapers / macos stock"
        )

    return {
        "total": len(items),
        "downloaded": len(downloaded),
        "skipped": len(skipped),
        "failed": len(failed)
    }
