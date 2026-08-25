#!/usr/bin/env bash
# Menú Rofi interactivo para Bluetooth con bluetoothctl para SwayNC

swaync-client -cp >/dev/null 2>&1

THEME="$HOME/.config/rofi/dropdown.rasi"
ROFI_CMD="rofi -dmenu -i -theme $THEME"

power_state=$(bluetoothctl show | grep "Powered:" | awk '{print $2}')

if [ "$power_state" = "yes" ]; then
    toggle="󰂯  Apagar Bluetooth"
else
    toggle="󰂲  Encender Bluetooth"
fi

options="$toggle\n󰑐  Escanear nuevos dispositivos"

paired_devices=$(bluetoothctl devices Paired | cut -d ' ' -f 2-)
while IFS= read -r dev; do
    [ -z "$dev" ] && continue
    mac=$(echo "$dev" | awk '{print $1}')
    name=$(echo "$dev" | cut -d ' ' -f 2-)
    info=$(bluetoothctl info "$mac")
    if echo "$info" | grep -q "Connected: yes"; then
        options="$options\n󰄴  $name (Conectado)"
    else
        options="$options\n󰂯  $name"
    fi
done <<< "$paired_devices"

chosen=$(echo -e "$options" | $ROFI_CMD -p "Bluetooth")
[ -z "$chosen" ] && exit 0

if [[ "$chosen" == *"Encender Bluetooth"* ]]; then
    bluetoothctl power on
    notify-send -i bluetooth "Bluetooth" "Encendido"
elif [[ "$chosen" == *"Apagar Bluetooth"* ]]; then
    bluetoothctl power off
    notify-send -i bluetooth-disabled "Bluetooth" "Apagado"
elif [[ "$chosen" == *"Escanear"* ]]; then
    notify-send -i bluetooth "Bluetooth" "Buscando dispositivos durante 5s..."
    bluetoothctl --timeout 5 scan on
    exec bash "$0"
else
    clean_name=$(echo "$chosen" | sed -E 's/^[󰂯󰄴 ]+ //; s/ \(Conectado\)$//')
    mac=$(bluetoothctl devices | grep "$clean_name" | awk '{print $2}')
    if [ -n "$mac" ]; then
        if bluetoothctl info "$mac" | grep -q "Connected: yes"; then
            bluetoothctl disconnect "$mac"
            notify-send -i bluetooth "Bluetooth" "Desconectado de $clean_name"
        else
            notify-send -i bluetooth "Bluetooth" "Conectando a $clean_name..."
            bluetoothctl connect "$mac"
        fi
    fi
fi
