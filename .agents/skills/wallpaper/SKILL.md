---
name: wallpaper
description: Search, optimize, and download pristine 4K/8K wallpapers tailored for macOS displays based on topic, person, context, or style. Supports Wallhaven, Unsplash, Reddit, and Bing.
---

# macOS 4K/8K Wallpaper Skill

This skill allows the agent to automatically search the internet and download ultra-high-resolution (4K, 5K, 8K) wallpapers tailored for macOS displays (Retina 16:10, 16:9, Ultrawide 21:9 / 32:9).

## When to Use

Use this skill whenever the user asks for:
- Downloading wallpapers or desktop backgrounds ("wallpaper indir", "arka plan bul", "4k wallpaper", "8k masaüstü")
- Wallpapers about a specific person, topic, movie, anime, aesthetic, or scene (e.g. "Steve Jobs minimalist", "rainy Tokyo street", "cyberpunk car", "deep space galaxy")
- High-resolution backgrounds tailored for their Mac display

## How It Works

The engine contains:
1. **Smart Prompt Expansion**: Translates Turkish or conversational requests into targeted aesthetic search terms.
2. **Multi-Source Aggregator**: Queries Wallhaven, Unsplash, Reddit (`r/wallpapers`, `r/WQHD_Wallpaper`, `r/EarthPorn`), and Bing UHD.
3. **Resolution & Aspect Ratio Filtering**: Ensures minimum 4K (3840x2160) or 8K (7680x4320), matching 16:9, 16:10 (MacBook Retina), or Ultrawide.
4. **Target Directory**: Saves files safely to `~/Pictures/Wallpapers` (or user-specified folder).

## Running the Command

Execute the wallpaper CLI tool using `run_command`:

```bash
# Basic download (default 4K, saves to ~/Pictures/Wallpapers)
wallpaper "<prompt>"

# Or using the Python engine directly
python3 "wallpaper_engine/cli.py" "<prompt>" --json
```

### Useful Flags
- `--macos-stock`: Sync and download all official 6K macOS stock wallpapers (Cheetah through Sequoia, Sonoma, Ventura, Tahoe, Golden Gate)
- `-n <count>`: Number of wallpapers to download (e.g., `-n 3`)
- `-r <4k|5k|8k|retina>`: Minimum resolution filter
- `--ratio <16:9|16:10|21:9|32:9|all>`: Target aspect ratio
- `-s <all|wallhaven|unsplash|reddit|bing>`: Provider filter
- `-o <dir>`: Custom destination folder
- `--json`: Returns structured JSON with details of downloaded files

## Presenting Results to the User

When wallpapers are downloaded, always present:
1. Thumbnail / Title and Resolution (e.g. `3840x2160` or `7680x4320`).
2. Source provider.
3. Clickable file link using markdown format: `[Dosyayı Görüntüle](file:///Users/.../Pictures/Wallpapers/filename.jpg)`.
