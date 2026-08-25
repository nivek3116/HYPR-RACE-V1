#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

STATE_FILE="/tmp/hypr_caffeine_active"

if [ -f "$STATE_FILE" ]; then
    # Inhibidor activo -> mostrar icono en Waybar
    echo '{"text": "󰈈", "alt": "awake", "class": "activated", "tooltip": "Inhibidor activo (Pantalla siempre activa)"}'
else
    # Modo normal
    echo '{"text": "", "alt": "normal", "class": "deactivated", "tooltip": ""}'
fi
