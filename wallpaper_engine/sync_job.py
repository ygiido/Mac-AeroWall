"""
Scheduled daily synchronization job.
Runs in background, updates stock archives, and sends native notification if new images were added.
"""

import sys
import datetime
from pathlib import Path

# Add project root to sys.path so it works directly or via launchd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wallpaper_engine.config import load_config, get_download_dir
from wallpaper_engine.macos_stock import sync_stock_wallpapers

def run_daily_sync():
    cfg = load_config()
    base_dir = get_download_dir()
    stock_dir = base_dir / "macos stock"

    log_dir = Path.home() / ".config" / "wallpaper"
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "daily_sync.log"
    except Exception:
        log_file = None

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Run sync with notification enabled
    result = sync_stock_wallpapers(target_dir=stock_dir, notify=True, quiet=False)

    log_entry = (
        f"[{timestamp}] Checked: {result['total']} total | "
        f"New: {result['downloaded']} | Skipped: {result['skipped']} | "
        f"Failed: {result['failed']}\n"
    )

    if log_file:
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception:
            pass

    return result

if __name__ == "__main__":
    run_daily_sync()
