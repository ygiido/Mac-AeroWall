#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}✦ macOS 4K/8K Wallpaper Downloader Kurulumu${NC}"
echo "──────────────────────────────────────────────"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_PATH="$SCRIPT_DIR/bin/wallpaper"
TARGET_DIR="$HOME/Pictures/Wallpapers"
GEMINI_PLUGIN_DIR="$HOME/.gemini/config/plugins/macos-wallpaper"

# 1. Ensure executable permission
chmod +x "$BIN_PATH"

# 2. Create target wallpaper directory
mkdir -p "$TARGET_DIR"
echo -e "${GREEN}✓${NC} Duvar kağıdı klasörü hazırlandı: ${BOLD}$TARGET_DIR${NC}"

# 3. Install CLI tool to user PATH (~/.local/bin or /usr/local/bin)
LOCAL_BIN="$HOME/.local/bin"
mkdir -p "$LOCAL_BIN"

ln -sf "$BIN_PATH" "$LOCAL_BIN/wallpaper"
echo -e "${GREEN}✓${NC} CLI aracı bağlandı: ${BOLD}$LOCAL_BIN/wallpaper${NC}"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$LOCAL_BIN:"* ]]; then
  echo -e "${YELLOW}! Not:${NC} $LOCAL_BIN PATH değişkeninizde olmayabilir."
  echo "  ~/.zshrc dosyanıza şunu ekleyebilirsiniz:"
  echo -e "  ${CYAN}export PATH=\"\$HOME/.local/bin:\$PATH\"${NC}"
fi

# 4. Install plugin into Antigravity global plugins
mkdir -p "$GEMINI_PLUGIN_DIR/skills/wallpaper"
cp "$SCRIPT_DIR/plugin.json" "$GEMINI_PLUGIN_DIR/plugin.json"
cp "$SCRIPT_DIR/.agents/skills/wallpaper/SKILL.md" "$GEMINI_PLUGIN_DIR/skills/wallpaper/SKILL.md"

echo -e "${GREEN}✓${NC} Antigravity Plugin kaydedildi: ${BOLD}$GEMINI_PLUGIN_DIR${NC}"

echo "──────────────────────────────────────────────"
echo -e "${BOLD}${GREEN}Kurulum başarıyla tamamlandı!${NC}"
echo ""
echo -e "${BOLD}Nasıl Kullanılır?${NC}"
echo -e "1. ${BOLD}Terminalden:${NC}"
echo -e "   ${CYAN}wallpaper \"yağmurlu tokyo gecesi neon\"${NC}"
echo -e "   ${CYAN}wallpaper \"steve jobs minimalist\" --res 8k${NC}"
echo -e "   ${CYAN}wallpaper \"kara delik uzay\" --ratio 21:9 -n 3${NC}"
echo ""
echo -e "2. ${BOLD}Antigravity İçinden:${NC}"
echo -e "   Chat ekranına doğrudan yazabilirsiniz:"
echo -e "   ${CYAN}\"bana tokyo neon 4k wallpaper indir\"${NC} veya ${CYAN}\"/wallpaper ...\"${NC}"
echo ""
