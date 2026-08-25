#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

if pidof gpu-screen-recorder >/dev/null 2>&1; then
    echo '{"text": "󰕧 REC", "tooltip": "Grabando pantalla a 60 FPS\nClic para detener grabación", "class": "recording"}'
else
    echo '{"text": "", "class": "idle"}'
fi
