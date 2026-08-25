#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

NIGHT_TEMP=4200

if [ "$SWAYNC_TOGGLE_STATE" = "true" ]; then
    if command -v hyprsunset >/dev/null 2>&1; then
        pkill -x hyprsunset 2>/dev/null || true
        setsid hyprsunset --temperature "$NIGHT_TEMP" >/dev/null 2>&1 &
    elif command -v wlsunset >/dev/null 2>&1; then
        pkill -x wlsunset 2>/dev/null || true
        setsid wlsunset -t "$NIGHT_TEMP" -T $((NIGHT_TEMP + 1)) >/dev/null 2>&1 &
    fi
elif [ "$SWAYNC_TOGGLE_STATE" = "false" ]; then
    pkill -x hyprsunset 2>/dev/null || true
    pkill -x wlsunset 2>/dev/null || true
else
    if pgrep -x hyprsunset >/dev/null; then
        pkill -x hyprsunset
    elif pgrep -x wlsunset >/dev/null; then
        pkill -x wlsunset
    elif command -v hyprsunset >/dev/null 2>&1; then
        setsid hyprsunset --temperature "$NIGHT_TEMP" >/dev/null 2>&1 &
    elif command -v wlsunset >/dev/null 2>&1; then
        setsid wlsunset -t "$NIGHT_TEMP" -T $((NIGHT_TEMP + 1)) >/dev/null 2>&1 &
    fi
fi
