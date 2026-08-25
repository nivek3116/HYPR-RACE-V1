#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

# Hyprland Battery & Charger Real-Time Event Daemon (Instant Kernel udev Response)

SOUND_DIR="$HOME/.config/hypr/sounds"
SOUND_PLUG="$SOUND_DIR/plug.wav"
SOUND_UNPLUG="$SOUND_DIR/unplug.wav"
SOUND_BAT_CRIT="$SOUND_DIR/battery_critical.wav"

play_snd() {
    local snd="$1"
    if [ -f "$snd" ]; then
        (pw-play "$snd" 2>/dev/null || paplay "$snd" 2>/dev/null) &
    fi
}

is_ac_online() {
    for f in /sys/class/power_supply/*/online; do
        if [ -f "$f" ] && [ "$(cat "$f" 2>/dev/null)" = "1" ]; then
            return 0
        fi
    done
    for s in /sys/class/power_supply/BAT*/status; do
        if [ -f "$s" ]; then
            local stat
            stat=$(cat "$s" 2>/dev/null)
            if [ "$stat" = "Charging" ] || [ "$stat" = "Full" ]; then
                return 0
            fi
        fi
    done
    return 1
}

get_battery_capacity() {
    for c in /sys/class/power_supply/BAT*/capacity; do
        if [ -f "$c" ]; then
            local cap
            cap=$(cat "$c" 2>/dev/null)
            if [ -n "$cap" ]; then
                echo "$cap"
                return
            fi
        fi
    done
    echo "100"
}

warned_15=false
warned_5=false

if is_ac_online; then
    prev_ac_state=1
else
    prev_ac_state=0
fi

last_ac_change=0
get_time_ms() {
    echo $(($(date +%s%N)/1000000))
}

check_battery_levels() {
    if is_ac_online; then
        warned_15=false
        warned_5=false
        return
    fi

    local capacity
    capacity=$(get_battery_capacity)

    if [ "$capacity" -le 5 ]; then
        if [ "$warned_5" = false ]; then
            notify-send -u critical -a "Batería" -i "battery-empty" \
                "¡Batería Crítica!" \
                "Conecta el cargador de inmediato."
            play_snd "$SOUND_BAT_CRIT"
            warned_5=true
            warned_15=true
        fi
    elif [ "$capacity" -le 15 ]; then
        if [ "$warned_15" = false ]; then
            notify-send -u critical -a "Batería" -i "battery-caution" \
                "Batería Baja" \
                "Conecta el cargador."
            play_snd "$SOUND_BAT_CRIT"
            warned_15=true
        fi
    elif [ "$capacity" -gt 15 ]; then
        warned_15=false
        warned_5=false
    fi
}

handle_power_change() {
    local curr_ac_state
    if is_ac_online; then
        curr_ac_state=1
    else
        curr_ac_state=0
    fi

    if [ "$curr_ac_state" -ne "$prev_ac_state" ]; then
        local now
        now=$(get_time_ms)
        if [ $((now - last_ac_change)) -gt 300 ]; then
            last_ac_change=$now
            date +%s > /tmp/hypr_charger_event 2>/dev/null
            if [ "$curr_ac_state" -eq 1 ]; then
                play_snd "$SOUND_PLUG"
                warned_15=false
                warned_5=false
            fi
            prev_ac_state="$curr_ac_state"
        fi
    fi

    check_battery_levels
}

# Heartbeat background thread for battery percentage monitoring while discharging
(
    while true; do
        sleep 20
        check_battery_levels
    done
) &
HEARTBEAT_PID=$!

trap 'kill "$HEARTBEAT_PID" 2>/dev/null' EXIT

# Real-time Kernel udev event monitor for instantaneous (<10ms) AC adapter reaction
while true; do
    udevadm monitor --udev --subsystem-match=power_supply 2>/dev/null | while read -r line; do
        handle_power_change
    done
    sleep 2
done
