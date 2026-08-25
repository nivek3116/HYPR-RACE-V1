#!/usr/bin/env bash
SOUND_FILE="/home/nivek/.config/hypr/sounds/notification.wav"

if [ ! -f "$SOUND_FILE" ]; then
    exit 0
fi

# Verificar si el modo No Molestar (DND) está activo en SwayNC
if swaync-client -D 2>/dev/null | grep -qi "true"; then
    exit 0
fi

# Volumen suave y calibrado (45%)
pw-play --volume 0.45 "$SOUND_FILE" &
