#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

SOUND="/usr/share/sounds/freedesktop/stereo/screen-capture.oga"

play_sound() {
    if [ -f "$SOUND" ]; then
        pw-play "$SOUND" &
    fi
}

swaync-client -cp 2>/dev/null || true
sleep 0.22

case "$1" in
    area)
        geom=$(slurp)
        if [ -n "$geom" ]; then
            play_sound
            if command -v swappy >/dev/null 2>&1; then
                grim -g "$geom" - | swappy -f -
            else
                grim -g "$geom" - | wl-copy
                notify-send -i image-x-generic "Captura" "Área copiada al portapapeles"
            fi
        fi
        ;;
    full)
        play_sound
        if command -v swappy >/dev/null 2>&1; then
            grim - | swappy -f -
        else
            grim - | wl-copy
            notify-send -i image-x-generic "Captura" "Pantalla completa copiada al portapapeles"
        fi
        ;;
    copy-area)
        geom=$(slurp)
        if [ -n "$geom" ]; then
            play_sound
            grim -g "$geom" - | wl-copy
            notify-send -i image-x-generic "Captura" "Área copiada al portapapeles"
        fi
        ;;
    *)
        geom=$(slurp)
        if [ -n "$geom" ]; then
            play_sound
            if command -v swappy >/dev/null 2>&1; then
                grim -g "$geom" - | swappy -f -
            else
                grim -g "$geom" - | wl-copy
            fi
        fi
        ;;
esac
