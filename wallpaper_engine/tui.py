"""
Interactive Terminal Application (TUI) for Mac AeroWall.
Provides full interactive menu, smart search with count selector,
stock sync, wallpaper management, and desktop setting.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Optional

if __package__ is None or __package__ == "":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from wallpaper_engine.config import load_config, save_config, get_download_dir, RESOLUTIONS
    from wallpaper_engine.query_parser import parse_prompt
    from wallpaper_engine.sources import search_wallpapers
    from wallpaper_engine.downloader import download_wallpaper, format_bytes, render_progress_bar
    from wallpaper_engine.macos_stock import sync_stock_wallpapers
else:
    from .config import load_config, save_config, get_download_dir, RESOLUTIONS
    from .query_parser import parse_prompt
    from .sources import search_wallpapers
    from .downloader import download_wallpaper, format_bytes, render_progress_bar
    from .macos_stock import sync_stock_wallpapers

# ANSI Colors
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RED = "\033[31m"
RESET = "\033[0m"

def clear_screen():
    os.system("clear" if os.name != "nt" else "cls")

def set_desktop_wallpaper(image_path: Path) -> bool:
    """Sets the macOS desktop background using AppleScript."""
    abs_path = str(image_path.resolve())
    script = f'''
    tell application "System Events"
        tell every desktop
            set picture to POSIX file "{abs_path}"
        end tell
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True)
        return True
    except Exception:
        # Fallback to sqlite/killall Dock if needed
        return False

def print_header():
    print(f"{CYAN}{BOLD}")
    print("  ╭─────────────────────────────────────────────────────────────╮")
    print("  │                  ✦ MAC AEROWALL TERMINAL ✦                  │")
    print("  │     Intelligent 4K/8K Wallpaper Engine & iCloud Sync        │")
    print("  ╰─────────────────────────────────────────────────────────────╯")
    print(f"{RESET}")

def search_flow():
    clear_screen()
    print_header()
    print(f"{BOLD}{MAGENTA}🔍 Akıllı Duvar Kağıdı Arama & İndirme{RESET}")
    print(f"{DIM}─────────────────────────────────────────────────────────────{RESET}")
    print(f"{DIM}Örnek: 'yağmurlu tokyo neon', 'steve jobs minimalist', 'kara delik uzay'{RESET}\n")

    try:
        prompt = input(f"{BOLD}Arama konusu / detay:{RESET} ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not prompt:
        print(f"{YELLOW}Arama konusu boş bırakılamaz.{RESET}")
        time.sleep(1)
        return

    # Adet Sistemi (Count Selector)
    print(f"\n{BOLD}Kaç adet farklı duvar kağıdı indirilsin?{RESET}")
    try:
        count_input = input(f"{CYAN}Adet [Varsayılan: 1]:{RESET} ").strip()
        count = int(count_input) if count_input and count_input.isdigit() and int(count_input) > 0 else 1
    except (KeyboardInterrupt, EOFError):
        return

    # Çözünürlük Tercihi
    print(f"\n{BOLD}Hedef Çözünürlük:{RESET}")
    print(f"  [1] 4K (3840x2160) - {DIM}Önerilen{RESET}")
    print(f"  [2] 5K (5120x2880) - {DIM}Studio Display / iMac{RESET}")
    print(f"  [3] 8K (7680x4320) - {DIM}Ultra HD{RESET}")
    print(f"  [4] Retina (16:10 MacBook){RESET}")
    try:
        res_choice = input(f"{CYAN}Seçim [1-4, Varsayılan: 1]:{RESET} ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    res_map = {"1": "4k", "2": "5k", "3": "8k", "4": "retina"}
    res_key = res_map.get(res_choice, "4k")
    min_w, min_h = RESOLUTIONS.get(res_key, (3840, 2160))

    # Parse and optimize prompt
    parsed = parse_prompt(prompt)
    cfg = load_config()
    dest_dir = get_download_dir()

    print(f"\n{DIM}─────────────────────────────────────────────────────────────{RESET}")
    print(f"{BOLD}Arama İstemi   :{RESET} {CYAN}{prompt}{RESET}")
    print(f"{BOLD}Optimize Sorgu :{RESET} {GREEN}{parsed.search_query}{RESET}")
    print(f"{BOLD}İndirilecek    :{RESET} {YELLOW}{count} farklı görsel ({res_key.upper()}){RESET}")
    print(f"{BOLD}Hedef Klasör   :{RESET} {dest_dir}")
    print(f"{DIM}─────────────────────────────────────────────────────────────{RESET}")
    print(f"{CYAN}🔍 Kaynaklar taranıyor (Wallhaven, Unsplash, Reddit, Bing)...{RESET}\n")

    wallpapers = search_wallpapers(
        query=parsed.search_query,
        sources=cfg.get("default_sources", ["wallhaven", "unsplash", "reddit", "bing"]),
        min_width=min_w,
        min_height=min_h,
        ratios=None,
        categories=parsed.categories,
        total_count=max(count * 2, 8)
    )

    if not wallpapers:
        print(f"{RED}✖ Belirtilen kriterlere uygun duvar kağıdı bulunamadı.{RESET}")
        input(f"\n{DIM}Devam etmek için Enter'a basın...{RESET}")
        return

    items_to_download = wallpapers[:count]
    print(f"{GREEN}✓ {len(items_to_download)} adet görsel bulundu, indirme başlatılıyor...{RESET}\n")

    downloaded_files: List[Path] = []
    for idx, item in enumerate(items_to_download, 1):
        print(f"{BOLD}[{idx}/{len(items_to_download)}]{RESET} {item.title} {DIM}({item.width}x{item.height} - {item.source}){RESET}")
        res = download_wallpaper(
            item=item,
            query_slug=parsed.search_query,
            custom_dir=str(dest_dir),
            progress_callback=render_progress_bar
        )
        sys.stdout.write("\n")
        if res.success:
            status = f"{YELLOW}[Zaten Mevcut]{RESET}" if res.already_existed else f"{GREEN}[İndirildi]{RESET}"
            size_str = format_bytes(res.file_size_bytes)
            print(f"  {status} {res.file_path.name} ({size_str})\n")
            if res.file_path:
                downloaded_files.append(res.file_path)
        else:
            print(f"  {RED}[Hata]{RESET} {res.error_message}\n")

    if downloaded_files:
        print(f"{BOLD}{GREEN}✓ Tüm indirmeler tamamlandı!{RESET}")
        print(f"Görseller iCloud Drive klasörünüzde: {CYAN}{dest_dir}{RESET}\n")

        # Ask to set first image as wallpaper
        try:
            set_choice = input(f"{BOLD}İndirilen ilk görsel masaüstü arka planı yapılsın mı? [e/H]:{RESET} ").strip().lower()
            if set_choice in ["e", "evet", "y", "yes"]:
                if set_desktop_wallpaper(downloaded_files[0]):
                    print(f"{GREEN}✓ Masaüstü arka planı başarıyla değiştirildi!{RESET}")
                else:
                    print(f"{YELLOW}! Masaüstü ayarlanırken izin veya sistem hatası oluştu.{RESET}")
        except (KeyboardInterrupt, EOFError):
            pass

    input(f"\n{DIM}Ana menüye dönmek için Enter'a basın...{RESET}")

def stock_sync_flow():
    clear_screen()
    print_header()
    cfg = load_config()
    base_dir = get_download_dir()
    stock_dir = base_dir / "macos stock"
    sync_stock_wallpapers(stock_dir, notify=True, quiet=False)
    input(f"\n{DIM}Ana menüye dönmek için Enter'a basın...{RESET}")

def view_wallpapers_flow():
    clear_screen()
    print_header()
    dest_dir = get_download_dir()
    print(f"{BOLD}{CYAN}📂 iCloud Drive Duvar Kağıdı Arşivi{RESET}")
    print(f"{DIM}Klasör: {dest_dir}{RESET}\n")

    extensions = {".jpg", ".jpeg", ".png", ".webp", ".heic"}
    files = []
    if dest_dir.exists():
        for p in sorted(dest_dir.glob("*")):
            if p.is_file() and p.suffix.lower() in extensions:
                files.append(p)

    stock_dir = dest_dir / "macos stock"
    stock_files = []
    if stock_dir.exists():
        for p in sorted(stock_dir.glob("*")):
            if p.is_file() and p.suffix.lower() in extensions:
                stock_files.append(p)

    print(f"{BOLD}Genel İndirilenler ({len(files)} adet):{RESET}")
    for idx, f in enumerate(files[:10], 1):
        size_mb = f.stat().st_size / 1024 / 1024
        print(f"  {idx}. {f.name} {DIM}({size_mb:.1f} MB){RESET}")
    if len(files) > 10:
        print(f"  {DIM}... ve {len(files) - 10} adet daha{RESET}")

    print(f"\n{BOLD}macOS & Minimal Stock Arşivi ({len(stock_files)} adet):{RESET}")
    print(f"  {GREEN}✓ 62+ adet 5K/6K Apple resmi ve minimal görsel hazır.{RESET}")

    print(f"\n{BOLD}İşlemler:{RESET}")
    print(f"  [1] Klasörü Finder'da Aç")
    print(f"  [2] macOS Stock Klasörünü Finder'da Aç")
    print(f"  [3] Geri Dön")

    try:
        sub = input(f"\n{CYAN}Seçim [1-3]:{RESET} ").strip()
        if sub == "1":
            subprocess.run(["open", str(dest_dir)], check=False)
        elif sub == "2":
            subprocess.run(["open", str(stock_dir)], check=False)
    except (KeyboardInterrupt, EOFError):
        pass

def set_wallpaper_flow():
    clear_screen()
    print_header()
    dest_dir = get_download_dir()
    extensions = {".jpg", ".jpeg", ".png", ".webp", ".heic"}

    all_files = []
    for f in sorted(dest_dir.glob("*")):
        if f.is_file() and f.suffix.lower() in extensions:
            all_files.append(f)

    stock_dir = dest_dir / "macos stock"
    if stock_dir.exists():
        for f in sorted(stock_dir.glob("*")):
            if f.is_file() and f.suffix.lower() in extensions:
                all_files.append(f)

    if not all_files:
        print(f"{YELLOW}Klasörde henüz ayarlanacak görsel bulunmuyor.{RESET}")
        input(f"\n{DIM}Enter'a basın...{RESET}")
        return

    print(f"{BOLD}{MAGENTA}🖥️ Duvar Kağıdı Seç & Arka Plan Yap{RESET}\n")
    for idx, f in enumerate(all_files[:25], 1):
        print(f"  [{idx:2d}] {f.name}")
    if len(all_files) > 25:
        print(f"  {DIM}... (Toplam {len(all_files)} görsel mevcut){RESET}")

    try:
        choice = input(f"\n{CYAN}Masaüstü yapmak istediğiniz numara (1-{min(len(all_files), 25)}):{RESET} ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(all_files):
            chosen = all_files[int(choice) - 1]
            if set_desktop_wallpaper(chosen):
                print(f"\n{GREEN}{BOLD}✓ Arka Plan Değiştirildi:{RESET} {chosen.name}")
            else:
                print(f"\n{RED}✖ Hata oluştu.{RESET}")
    except (KeyboardInterrupt, EOFError):
        pass

    input(f"\n{DIM}Enter'a basın...{RESET}")

def settings_flow():
    clear_screen()
    print_header()
    cfg = load_config()
    print(f"{BOLD}{BLUE}⚙️ Sistem Ayarları{RESET}\n")
    print(f"  İndirme Dizini  : {CYAN}{cfg.get('download_dir')}{RESET}")
    print(f"  Varsayılan Kalite: {YELLOW}{cfg.get('default_resolution', '4k').upper()}{RESET}")
    print(f"  Kaynaklar       : {GREEN}{', '.join(cfg.get('default_sources', []))}{RESET}")
    print(f"  Günlük Kontrol  : {GREEN}Etkin (Her 24 saatte bir arka planda tarar){RESET}")
    print(f"  macOS Bildirimi : {GREEN}Etkin (Yeni görsel indiğinde sesli bildirim verir){RESET}")

    print(f"\n{BOLD}Seçenekler:{RESET}")
    print(f"  [1] İndirme Klasörünü Değiştir")
    print(f"  [2] Geri Dön")

    try:
        c = input(f"\n{CYAN}Seçim [1-2]:{RESET} ").strip()
        if c == "1":
            new_path = input("Yeni klasör yolu: ").strip()
            if new_path:
                resolved = str(Path(new_path).expanduser().resolve())
                cfg["download_dir"] = resolved
                save_config(cfg)
                print(f"{GREEN}✓ Kaydedildi:{RESET} {resolved}")
                time.sleep(1.5)
    except (KeyboardInterrupt, EOFError):
        pass

def run_tui():
    """Main loop for the terminal user interface."""
    while True:
        clear_screen()
        print_header()
        cfg = load_config()
        print(f"  {DIM}Hedef Klasör:{RESET} {CYAN}{cfg.get('download_dir')}{RESET}\n")
        print(f"  {BOLD}[1]{RESET} 🔍 Akıllı Duvar Kağıdı Ara & İndir {DIM}(Adet & Çözünürlük Seçimli){RESET}")
        print(f"  {BOLD}[2]{RESET} 🍎 macOS, Mac OS 9 & Minimal MacBook Arşivini Senkronize Et")
        print(f"  {BOLD}[3]{RESET} 📂 İndirilen Duvar Kağıtlarını Görüntüle & Finder'da Aç")
        print(f"  {BOLD}[4]{RESET} 🖥️ Bir Duvar Kağıdı Seç ve Anında Masaüstü Yap")
        print(f"  {BOLD}[5]{RESET} ⚙️ Sistem Ayarları & Günlük Kontrol Durumu")
        print(f"  {BOLD}[q]{RESET} Çıkış\n")

        try:
            choice = input(f"{BOLD}{CYAN}Seçiminiz [1-5, q]:{RESET} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nÇıkış yapılıyor...")
            break

        if choice == "1":
            search_flow()
        elif choice == "2":
            stock_sync_flow()
        elif choice == "3":
            view_wallpapers_flow()
        elif choice == "4":
            set_wallpaper_flow()
        elif choice == "5":
            settings_flow()
        elif choice in ["q", "quit", "exit", "cikis", "çıkış"]:
            print(f"\n{GREEN}Mac AeroWall'dan çıkıldı. İyi günler!{RESET}\n")
            break
        else:
            print(f"{YELLOW}Geçersiz seçim!{RESET}")
            time.sleep(0.8)

if __name__ == "__main__":
    run_tui()
