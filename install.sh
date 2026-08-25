#!/bin/bash
# ==============================================================================
# Instalador de Dotfiles - HYPR-RACE-V1
# ==============================================================================

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}       Instalador de Dotfiles HYPR-RACE-V1        ${NC}"
echo -e "${BLUE}==================================================${NC}\n"

# Obtener directorio del repositorio
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${YELLOW}[1/4] Creando directorios en tu sistema...${NC}"
mkdir -p ~/.config
mkdir -p ~/.themes
mkdir -p ~/fondos
mkdir -p ~/.local/bin
mkdir -p ~/.local/share/fonts

echo -e "\n${YELLOW}[2/4] Copiando configuraciones (Dotfiles)...${NC}"
# Copiar .config
echo "--> Copiando ~/.config"
cp -r "$REPO_DIR/.config/"* ~/.config/ 2>/dev/null || true

# Copiar .themes
echo "--> Copiando ~/.themes"
cp -r "$REPO_DIR/.themes/"* ~/.themes/ 2>/dev/null || true

# Copiar .local
echo "--> Copiando ~/.local/bin y ~/.local/share/fonts"
cp -r "$REPO_DIR/.local/bin/"* ~/.local/bin/ 2>/dev/null || true
cp -r "$REPO_DIR/.local/share/fonts/"* ~/.local/share/fonts/ 2>/dev/null || true
fc-cache -fv >/dev/null 2>&1

# Copiar fondos
echo "--> Copiando ~/fondos"
cp -r "$REPO_DIR/fondos/"* ~/fondos/ 2>/dev/null || true

# Crear enlace simbólico para el selector de fondos
echo "--> Creando enlaces simbólicos"
ln -sf "$HOME/.config/selector-fondos/selector.sh" "$HOME/.local/bin/selector-fondos"

echo -e "\n${YELLOW}[3/4] Configurando permisos de ejecución...${NC}"
chmod +x ~/.config/hypr/scripts/*.sh 2>/dev/null || true
chmod +x ~/.config/hypr/scripts/*.py 2>/dev/null || true
chmod +x ~/.config/waybar/scripts/*.sh 2>/dev/null || true
chmod +x ~/.config/waybar/scripts/*.py 2>/dev/null || true
chmod +x ~/.config/waybar/scripts/quick_menu_client 2>/dev/null || true
chmod +x ~/.config/swaync/scripts/*.sh 2>/dev/null || true
chmod +x ~/.config/selector-fondos/*.sh 2>/dev/null || true
chmod +x ~/.local/bin/mpvpaper-autopause.py 2>/dev/null || true
echo "Permisos aplicados correctamente."

echo -e "\n${YELLOW}[4/4] Activando servicios en segundo plano...${NC}"
systemctl --user daemon-reload
systemctl --user enable --now hypr-battery-alert.service 2>/dev/null || true
systemctl --user enable --now hypr-usb-sound.service 2>/dev/null || true

echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN}        ¡Instalación completada con éxito!        ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo "Por favor, reinicia tu sesión para aplicar todos los cambios."
