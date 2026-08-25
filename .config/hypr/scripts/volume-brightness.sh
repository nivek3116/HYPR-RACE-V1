#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

action="$1"
step="${2:-5}"

case "$action" in
    vol-up)
        if command -v swayosd-client >/dev/null 2>&1 && pgrep -x swayosd-server >/dev/null; then
            swayosd-client --output-volume raise
        else
            wpctl set-volume -l 1.5 @DEFAULT_AUDIO_SINK@ "${step}%+"
        fi
        ;;
    vol-down)
        if command -v swayosd-client >/dev/null 2>&1 && pgrep -x swayosd-server >/dev/null; then
            swayosd-client --output-volume lower
        else
            wpctl set-volume @DEFAULT_AUDIO_SINK@ "${step}%-"
        fi
        ;;
    vol-mute)
        if command -v swayosd-client >/dev/null 2>&1 && pgrep -x swayosd-server >/dev/null; then
            swayosd-client --output-volume mute-toggle
        else
            wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle
        fi
        ;;
    mic-mute)
        wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle
        if command -v swayosd-client >/dev/null 2>&1 && pgrep -x swayosd-server >/dev/null; then
            swayosd-client --input-volume mute-toggle 2>/dev/null
        fi
        ;;
    bright-up)
        if command -v swayosd-client >/dev/null 2>&1 && pgrep -x swayosd-server >/dev/null; then
            swayosd-client --brightness raise
        else
            brightnessctl set "+${step}%"
        fi
        ;;
    bright-down)
        if command -v swayosd-client >/dev/null 2>&1 && pgrep -x swayosd-server >/dev/null; then
            swayosd-client --brightness lower
        else
            brightnessctl set "${step}%-"
        fi
        ;;
    caps)
        if command -v swayosd-client >/dev/null 2>&1 && pgrep -x swayosd-server >/dev/null; then
            swayosd-client --caps-lock
        fi
        ;;
esac
