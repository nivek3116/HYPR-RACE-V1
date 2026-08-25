#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

STATE_FILE="/tmp/hypr_caffeine_active"

if [ "$SWAYNC_TOGGLE_STATE" = "true" ]; then
    touch "$STATE_FILE"
    pkill -x hypridle 2>/dev/null || true
elif [ "$SWAYNC_TOGGLE_STATE" = "false" ]; then
    rm -f "$STATE_FILE"
    pkill -x hypridle 2>/dev/null || true
    setsid hypridle >/dev/null 2>&1 &
else
    if [ -f "$STATE_FILE" ]; then
        rm -f "$STATE_FILE"
        pkill -x hypridle 2>/dev/null || true
        setsid hypridle >/dev/null 2>&1 &
    else
        touch "$STATE_FILE"
        pkill -x hypridle 2>/dev/null || true
    fi
fi

sleep 0.05
pkill -RTMIN+10 waybar 2>/dev/null || true
