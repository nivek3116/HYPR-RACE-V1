#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

# Gestor de portapapeles con cliphist y rofi

case "$1" in
    copy)
        cliphist list | rofi -dmenu -p "📋 Portapapeles" | cliphist decode | wl-copy
        ;;
    delete)
        cliphist list | rofi -dmenu -p "🗑️ Eliminar elemento" | cliphist delete
        ;;
    wipe)
        cliphist wipe && notify-send -i edit-clear "Portapapeles" "Historial vaciado correctamente"
        ;;
    *)
        cliphist list | rofi -dmenu -p "📋 Portapapeles" | cliphist decode | wl-copy
        ;;
esac
