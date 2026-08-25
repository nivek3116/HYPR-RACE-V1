#!/usr/bin/env bash
CONFIG_FILE="${HOME}/.config/swaync/notif_volume"

case "$1" in
    get)
        if [ -f "$CONFIG_FILE" ]; then
            cat "$CONFIG_FILE"
        else
            echo "80"
        fi
        ;;
    set)
        if [ -n "$2" ]; then
            val=$(printf "%.0f" "$2" 2>/dev/null || echo "$2")
            echo "$val" > "$CONFIG_FILE"
        fi
        ;;
    *)
        echo "Uso: $0 {get|set <valor>}"
        exit 1
        ;;
esac
