#!/bin/bash

# Mac AeroWall - Clean Uninstaller Script

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}✦ Mac AeroWall Kaldırma Aracı (Uninstaller)${NC}"
echo "──────────────────────────────────────────────"

# 1. Ask for confirmation unless -y or --yes flag is given
if [[ "$1" != "-y" && "$1" != "--yes" ]]; then
    read -p "Mac AeroWall bileşenlerini kaldırmak istediğinize emin misiniz? [e/H]: " confirm
    if [[ "$confirm" != "e" && "$confirm" != "E" && "$confirm" != "y" && "$confirm" != "Y" ]]; then
        echo -e "${YELLOW}Kaldırma işlemi iptal edildi.${NC}"
        exit 0
    fi
fi

echo ""
echo -e "${CYAN}Bileşenler temizleniyor...${NC}"

# 2. Stop and remove launchd background service
PLIST_FILE="$HOME/Library/LaunchAgents/com.ygiido.wallpaper-sync.plist"
if [ -f "$PLIST_FILE" ]; then
    launchctl unload "$PLIST_FILE" 2>/dev/null || true
    rm -f "$PLIST_FILE"
    echo -e "  ${GREEN}✓${NC} Günlük arka plan servisi durduruldu ve silindi."
fi

# 3. Remove CLI binary link from ~/.local/bin
if [ -L "$HOME/.local/bin/wallpaper" ] || [ -f "$HOME/.local/bin/wallpaper" ]; then
    rm -f "$HOME/.local/bin/wallpaper"
    echo -e "  ${GREEN}✓${NC} ~/.local/bin/wallpaper kısayolu kaldırıldı."
fi

# 4. Clean zshrc aliases
if [ -f "$HOME/.zshrc" ]; then
    if grep -q "wallpaper_engine" "$HOME/.zshrc"; then
        cp "$HOME/.zshrc" "$HOME/.zshrc.aerowall_bak"
        sed -i '' '/wallpaper_engine/d' "$HOME/.zshrc" 2>/dev/null || true
        echo -e "  ${GREEN}✓${NC} ~/.zshrc içindeki terminal alias'ları temizlendi."
    fi
fi

# 5. Remove Antigravity plugin registration
PLUGIN_DIR="$HOME/.gemini/config/plugins/macos-wallpaper"
if [ -d "$PLUGIN_DIR" ]; then
    rm -rf "$PLUGIN_DIR"
    echo -e "  ${GREEN}✓${NC} Antigravity eklenti kaydı kaldırıldı."
fi

# 6. Remove config directory
CONFIG_DIR="$HOME/.config/wallpaper"
if [ -d "$CONFIG_DIR" ]; then
    rm -rf "$CONFIG_DIR"
    echo -e "  ${GREEN}✓${NC} ~/.config/wallpaper ayar dosyaları temizlendi."
fi

echo ""
echo -e "${YELLOW}! Not:${NC} İndirdiğiniz duvar kağıtları (iCloud Drive / ygiido wallpapers) güvenliğiniz için silinmedi."
echo -e "Eğer görselleri de silmek isterseniz Finder'dan manuel silebilirsiniz."
echo ""
echo -e "${BOLD}${GREEN}✓ Mac AeroWall başarıyla sistemden kaldırıldı.${NC}"
echo "──────────────────────────────────────────────"
