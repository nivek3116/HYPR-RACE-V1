#!/usr/bin/env bash
# Selector y alternador de salida de audio PipeWire / WirePlumber

swaync-client -cp >/dev/null 2>&1

THEME="$HOME/.config/rofi/dropdown.rasi"
sinks=$(pactl list short sinks)
current_sink=$(pactl get-default-sink)

options=""
while IFS=$'\t' read -r id name module format state; do
    [ -z "$name" ] && continue
    clean_name=$(pactl list sinks | grep -A 12 "Name: $name" | grep "Description:" | head -n1 | cut -d: -f2- | sed 's/^[ \t]*//')
    [ -z "$clean_name" ] && clean_name="$name"
    if [ "$name" = "$current_sink" ]; then
        options="$options\n󰄴  $clean_name"
    else
        options="$options\n󰓃  $clean_name"
    fi
done <<< "$sinks"

options=$(echo -e "$options" | sed '/^$/d')

chosen=$(echo -e "$options" | rofi -dmenu -i -theme "$THEME" -p "Salida Audio")
[ -z "$chosen" ] && exit 0

selected_desc=$(echo "$chosen" | sed -E 's/^[󰓃󰄴 ]+ //')
target_sink=$(pactl list sinks | grep -B 2 -A 10 "Description: $selected_desc" | grep "Name:" | head -n1 | awk '{print $2}')

if [ -n "$target_sink" ]; then
    pactl set-default-sink "$target_sink"
    notify-send -i audio-speakers "Audio" "Salida: $selected_desc"
fi
