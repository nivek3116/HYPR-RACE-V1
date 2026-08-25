#!/usr/bin/env bash
# Menú Rofi interactivo para Wi-Fi con nmcli para SwayNC

swaync-client -cp >/dev/null 2>&1

THEME="$HOME/.config/rofi/dropdown.rasi"
ROFI_CMD="rofi -dmenu -i -theme $THEME"

wifi_state=$(nmcli -fields WIFI g)

if [[ "$wifi_state" =~ "disabled" ]]; then
    toggle="󰤮  Encender Wi-Fi"
else
    toggle="󰤨  Apagar Wi-Fi"
fi

current_ssid=$(nmcli -t -f active,ssid dev wifi | grep '^yes' | cut -d: -f2)

raw_list=$(nmcli --terse --fields "IN-USE,BSSID,SSID,BARS,SECURITY" device wifi list --rescan auto 2>/dev/null | awk -F: '!seen[$3]++')

options="$toggle\n󰑐  Escanear redes"
while IFS=":" read -r in_use bssid ssid bars security; do
    [ -z "$ssid" ] && continue
    if [ "$in_use" = "*" ]; then
        options="$options\n󰄴  $ssid ($bars)"
    else
        [ -n "$security" ] && sec_icon="󰌾" || sec_icon=""
        options="$options\n󰤨  $ssid $sec_icon ($bars)"
    fi
done <<< "$raw_list"

chosen=$(echo -e "$options" | $ROFI_CMD -p "Wi-Fi")
[ -z "$chosen" ] && exit 0

if [[ "$chosen" == *"Encender Wi-Fi"* ]]; then
    nmcli radio wifi on
    notify-send -i network-wireless "Wi-Fi" "Activado"
elif [[ "$chosen" == *"Apagar Wi-Fi"* ]]; then
    nmcli radio wifi off
    notify-send -i network-wireless-offline "Wi-Fi" "Desactivado"
elif [[ "$chosen" == *"Escanear redes"* ]]; then
    nmcli device wifi rescan
    notify-send -i network-wireless "Wi-Fi" "Redes actualizadas"
    exec bash "$0"
else
    clean_ssid=$(echo "$chosen" | sed -E 's/^[󰤨󰄴 ]+ //; s/ 󰌾//; s/ \([^)]*\)$//')
    if [ "$clean_ssid" = "$current_ssid" ]; then
        nmcli connection down "$clean_ssid" && notify-send -i network-wireless "Wi-Fi" "Desconectado de $clean_ssid"
    else
        success=$(nmcli device wifi connect "$clean_ssid" 2>&1)
        if echo "$success" | grep -qi "successfully"; then
            notify-send -i network-wireless "Wi-Fi" "Conectado a $clean_ssid"
        else
            pass=$(rofi -dmenu -password -p "Contraseña para $clean_ssid:" -theme "$THEME")
            if [ -n "$pass" ]; then
                if nmcli device wifi connect "$clean_ssid" password "$pass" >/dev/null 2>&1; then
                    notify-send -i network-wireless "Wi-Fi" "Conectado a $clean_ssid"
                else
                    notify-send -i dialog-error "Error de conexión" "No se pudo conectar a $clean_ssid"
                fi
            fi
        fi
    fi
fi
