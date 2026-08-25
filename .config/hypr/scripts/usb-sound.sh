#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

# Hyprland USB Device Sound Daemon (Clean, Single-Instance, Resilient)

SOUND_DIR="$HOME/.config/hypr/sounds"
SOUND_CONNECT="$SOUND_DIR/usb_connect.wav"
SOUND_DISCONNECT="$SOUND_DIR/usb_disconnect.wav"

last_connect=0
last_disconnect=0
DEBOUNCE_MS=1200

get_time_ms() {
    echo $(($(date +%s%N)/1000000))
}

play_snd() {
    local snd="$1"
    if [ -f "$snd" ]; then
        pw-play "$snd" 2>/dev/null || paplay "$snd" 2>/dev/null &
    fi
}

process_event() {
    [ -z "$action" ] && return

    # Ignorar si ocurrió un evento de cargador (USB-C) en los últimos 2 segundos
    if [ -f /tmp/hypr_charger_event ]; then
        charger_ts=$(cat /tmp/hypr_charger_event 2>/dev/null || echo 0)
        now_s=$(date +%s)
        if [ $((now_s - charger_ts)) -le 2 ]; then
            return
        fi
    fi

    # Ignorar dispositivos internos (Bluetooth, cámara web, lector de huellas, etc.)
    if [ "$integration" = "internal" ]; then
        return
    fi

    # Ignorar interfaces o productos Bluetooth explícitamente
    if [[ "$interfaces" =~ :e00101: ]] || [[ "$model" =~ [Bb]luetooth ]] || [[ "$product" =~ ^8087/ ]]; then
        return
    fi

    # Ignorar root hubs
    if [[ "$product" =~ ^1d6b/ ]]; then
        return
    fi

    case "$action" in
        add)
            now=$(get_time_ms)
            if [ $((now - last_connect)) -gt $DEBOUNCE_MS ]; then
                last_connect=$now
                play_snd "$SOUND_CONNECT"
            fi
            ;;
        remove)
            now=$(get_time_ms)
            if [ $((now - last_disconnect)) -gt $DEBOUNCE_MS ]; then
                last_disconnect=$now
                play_snd "$SOUND_DISCONNECT"
            fi
            ;;
    esac
}

# Auto-reconnection loop
while true; do
    action=""
    integration=""
    interfaces=""
    model=""
    product=""

    udevadm monitor --udev --property --subsystem-match=usb/usb_device 2>/dev/null | while IFS= read -r line; do
        if [[ "$line" =~ ^ACTION=(.*)$ ]]; then
            action="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^ID_INTEGRATION=(.*)$ ]]; then
            integration="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^ID_USB_INTERFACES=(.*)$ ]]; then
            interfaces="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^ID_MODEL=(.*)$ ]] || [[ "$line" =~ ^ID_MODEL_FROM_DATABASE=(.*)$ ]]; then
            [ -z "$model" ] && model="${BASH_REMATCH[1]}"
        elif [[ "$line" =~ ^PRODUCT=(.*)$ ]]; then
            product="${BASH_REMATCH[1]}"
        elif [ -z "$line" ]; then
            process_event
            action=""
            integration=""
            interfaces=""
            model=""
            product=""
        fi
    done
    sleep 2
done
