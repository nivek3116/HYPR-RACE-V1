#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

# Grabador de pantalla profesional por hardware (1920x1080 @ 60 FPS - Solo Audio Interno)

RECORD_DIR="$HOME/Videos/Grabaciones"
mkdir -p "$RECORD_DIR"

START_SOUND="$HOME/.config/hypr/sounds/record_start.wav"
STOP_SOUND="$HOME/.config/hypr/sounds/record_stop.wav"

update_ui() {
    pkill -RTMIN+11 waybar 2>/dev/null || true
}

if pidof gpu-screen-recorder >/dev/null 2>&1; then
    # 🛑 DETENER GRABACIÓN
    killall -SIGINT gpu-screen-recorder 2>/dev/null || true
    sleep 0.5
    
    update_ui
    
    if [ -f "$STOP_SOUND" ]; then
        pw-play "$STOP_SOUND" &
    fi
    
    notify-send -a "Grabador" \
                -i camera-video \
                "Grabación finalizada"
else
    # 🎬 INICIAR GRABACIÓN (1920x1080 @ 60 FPS - Solo Audio Interno)
    OUTPUT_FILE="$RECORD_DIR/grabacion_$(date +'%Y-%m-%d_%H-%M-%S').mp4"
    
    # Lanzar como proceso huérfano totalmente independiente
    (
        setsid gpu-screen-recorder -w eDP-1 -f 60 -s 1920x1080 -a default_output -c mp4 -k h264 -o "$OUTPUT_FILE" </dev/null >/dev/null 2>&1 &
    ) &
    
    sleep 0.4
    update_ui
    
    if [ -f "$START_SOUND" ]; then
        pw-play "$START_SOUND" &
    fi
    
    notify-send -a "Grabador" \
                -i media-record \
                "Grabación iniciada"
fi
