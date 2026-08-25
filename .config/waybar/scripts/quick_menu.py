#!/usr/bin/env python3

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

import os
import sys
import socket

SOCK_FILE = "/tmp/waybar_quick_menu.sock"
PID_FILE = "/tmp/waybar_quick_menu.pid"

# ⚡ ULTRA-FAST IPC CLIENT DISPATCH (<1ms)
if __name__ == '__main__' and os.path.exists(SOCK_FILE):
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "battery"
    if target != "--daemon":
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect(SOCK_FILE)
            s.send(target.encode("utf-8"))
            s.close()
            sys.exit(0)
        except Exception:
            try:
                os.remove(SOCK_FILE)
            except Exception:
                pass

import json
import re
import threading
import subprocess
import signal
import time

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell

WLSUNSET_BIN = os.path.expanduser("~/.local/bin/wlsunset")

CSS_STYLE = """
/* Reset & Typography - Exact Waybar Font Stack */
* {
    font-family: 'Poppins', 'MonaspiceNe Nerd Font', 'JetBrains Mono Nerd Font', sans-serif;
    color: #FFFFFF;
}

window {
    background-color: transparent;
}

/* Global Button Reset */
button {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.06);
    border: none;
    border-radius: 8px;
    box-shadow: none;
    text-shadow: none;
    color: #cbd5e1;
    font-size: 11px;
    font-weight: 600;
    padding: 5px 12px;
    transition: all 0.2s ease;
}

button:hover {
    background-color: #ffffff;
    border: none;
    color: #000000;
}

button:hover * {
    color: #000000;
}

button:active, button:checked {
    background-color: #ffffff;
    border: none;
    color: #000000;
}

button:active *, button:checked * {
    color: #000000;
}

scrolledwindow, viewport {
    background-color: transparent;
    border: none;
}

/* Scrollbars invisibles al estilo SwayNC */
scrollbar,
scrollbar slider,
scrollbar trough,
scrollbar.vertical,
scrollbar.horizontal {
    min-width: 0px;
    min-height: 0px;
    border: none;
    background: transparent;
    opacity: 0;
}

/* Outer Main Glass Container matching Waybar */
.main-container {
    min-width: 330px;
    background-color: rgba(0, 0, 0, 0.50);
    border: none;
    border-radius: 12px;
    padding: 12px;
    box-shadow: none;
}

/* Top Quick Toggles Inset Bar */
.toggles-bar {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 8px;
    padding: 6px;
    margin-bottom: 10px;
}

/* Pill Buttons / Quick Action Toggles */
.pill-btn {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.06);
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 36px;
    font-size: 15px;
    color: #cbd5e1;
    transition: all 0.2s ease;
}

.pill-btn label {
    margin: 0;
    padding: 0;
    color: inherit;
}

.pill-btn:hover {
    background-color: #ffffff;
    border: none;
    color: #000000;
}

.pill-btn:hover label {
    color: #000000;
}

.pill-btn.active {
    background-color: #ffffff;
    border: none;
    color: #000000;
}

.pill-btn.active label {
    color: #000000;
}

.pill-btn.power:hover {
    background-color: rgba(239, 68, 68, 0.85);
    border: none;
    color: #ffffff;
}

.pill-btn.power:hover label {
    color: #ffffff;
}

/* Power Profile Buttons */
.profile-btn {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.06);
    border: none;
    border-radius: 8px;
    padding: 5px 3px;
    min-height: 30px;
    font-size: 10.5px;
    font-weight: 600;
    color: #cbd5e1;
    transition: all 0.2s ease;
}

.profile-btn label {
    margin: 0;
    padding: 0;
    color: inherit;
}

.profile-btn:hover {
    background-color: #ffffff;
    border: none;
    color: #000000;
}

.profile-btn:hover label {
    color: #000000;
}

.profile-btn.active {
    background-color: rgba(255, 255, 255, 0.20);
    border: none;
    color: #ffffff;
}

.profile-btn.active label {
    color: #ffffff;
}

/* Headers */
.view-header {
    margin-bottom: 8px;
    padding: 0 2px;
}

.view-title {
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.2px;
    color: #ffffff;
}

.trash-btn {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.06);
    border: none;
    border-radius: 8px;
    padding: 5px 12px;
    color: #cbd5e1;
    font-size: 11px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.trash-btn:hover {
    background-color: #ffffff;
    border: none;
    color: #000000;
}

/* Inner Frame Area */
.inset-frame {
    background-color: transparent;
    border: none;
    padding: 4px;
    min-height: 285px;
}

/* Metric Tiles (3 Columns Mosaic) */
.metric-tile {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 8px;
    padding: 10px 4px;
    transition: all 0.2s ease;
}

.metric-tile:hover {
    background-color: rgba(255, 255, 255, 0.12);
    border: none;
}

.metric-val {
    font-size: 13.5px;
    font-weight: 700;
    color: #ffffff;
}

.metric-sub {
    font-size: 10.5px;
    font-weight: 500;
    color: #94a3b8;
    margin-top: 3px;
}

/* Notification Card */
.notif-box-white {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 6px;
    box-shadow: none;
    transition: all 0.2s ease;
}

.notif-box-white:hover {
    border: none;
    background-color: rgba(255, 255, 255, 0.12);
}

.avatar-image {
    border-radius: 6px;
}

.notif-icon-pure {
    font-size: 22px;
    color: #ffffff;
    min-width: 26px;
    margin-right: 2px;
}

.notif-appname {
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
}

.notif-time {
    font-size: 10.5px;
    color: #64748b;
}

.notif-body {
    font-size: 12px;
    color: #cbd5e1;
    margin-top: 2px;
}

.empty-box {
    padding: 40px 10px;
}

.empty-icon {
    font-size: 28px;
    color: #64748b;
    margin-bottom: 6px;
}

.empty-label {
    font-size: 13px;
    color: #64748b;
}

/* Sub-views Navigation & Lists */
.icon-btn {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.06);
    border: none;
    border-radius: 8px;
    padding: 5px 10px;
    color: #cbd5e1;
    font-size: 12px;
    transition: all 0.2s ease;
}

.icon-btn:hover {
    background-color: #ffffff;
    border: none;
    color: #000000;
}

.icon-btn:hover * {
    color: #000000;
}

.section-box {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
}

.section-title {
    font-size: 10.5px;
    font-weight: 700;
    color: #94a3b8;
    letter-spacing: 0.6px;
    padding: 2px 2px;
}

.power-label {
    font-size: 12.5px;
    font-weight: 600;
    color: #ffffff;
}

.status-label {
    font-size: 11px;
    color: #94a3b8;
}

/* Sliders Section */
.slider-container {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
    margin-bottom: 6px;
    transition: all 0.2s ease;
}

.slider-container:hover {
    background-color: rgba(255, 255, 255, 0.12);
    border: none;
}

.slider-icon {
    font-size: 15px;
    color: #ffffff;
    min-width: 22px;
}

.slider-icon.muted {
    color: #64748b;
}

.slider-btn {
    background-image: none;
    background-color: transparent;
    border: none;
    padding: 2px 4px;
    border-radius: 6px;
}

.slider-btn:hover {
    background-color: rgba(255, 255, 255, 0.14);
}

.slider-value {
    font-size: 11.5px;
    font-weight: 600;
    color: #cbd5e1;
    min-width: 36px;
}

scale {
    margin: 0 4px;
    padding: 0;
}

scale trough {
    background-color: rgba(255, 255, 255, 0.12);
    border-radius: 4px;
    min-height: 4px;
    border: none;
}

scale highlight {
    background-color: #ffffff;
    border-radius: 4px;
    min-height: 4px;
}

scale slider {
    background-color: #ffffff;
    border-radius: 8px;
    min-width: 12px;
    min-height: 12px;
    margin: -4px;
    border: none;
    box-shadow: 0 1px 4px rgba(0,0,0,0.5);
}

scale slider:hover {
    background-color: #cbd5e1;
    min-width: 14px;
    min-height: 14px;
    margin: -5px;
}

/* Item cards (Wi-Fi, BT, Audio outputs, Nightlight, Theme) */
.item-card {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 6px;
    transition: all 0.2s ease;
}

.item-card:hover {
    background-color: rgba(255, 255, 255, 0.12);
    border: none;
}

.item-card.connected, .item-card.selected {
    background-color: rgba(255, 255, 255, 0.20);
    border: none;
}

.item-title {
    font-size: 12.5px;
    font-weight: 700;
    color: #ffffff;
}

.item-sub {
    font-size: 11.5px;
    color: #94a3b8;
}

.action-btn {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.06);
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
    color: #cbd5e1;
    transition: all 0.2s ease;
}

.action-btn:hover {
    background-color: #ffffff;
    border: none;
    color: #000000;
}

.action-btn.disconnect {
    background-color: rgba(239, 68, 68, 0.25);
    border: none;
    color: #fca5a5;
}

.action-btn.disconnect:hover {
    background-color: rgba(239, 68, 68, 0.85);
    border: none;
    color: #ffffff;
}

.password-entry {
    background-color: rgba(255, 255, 255, 0.08);
    border: none;
    border-radius: 8px;
    padding: 6px 10px;
    color: #ffffff;
    font-size: 12px;
}

/* Power Menu Action Cards */
.power-action-card {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.06);
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    transition: all 0.2s ease;
}

.power-action-icon {
    font-size: 15px;
    color: #cbd5e1;
    min-width: 22px;
}

.power-action-text {
    font-size: 12.5px;
    font-weight: 600;
    color: #cbd5e1;
}

.power-action-card:hover {
    background-color: #ffffff;
    border: none;
}

.power-action-card:hover .power-action-icon,
.power-action-card:hover .power-action-text,
.power-action-card:hover label {
    color: #000000;
}

.power-action-card.poweroff:hover {
    background-color: rgba(239, 68, 68, 0.85);
    border: none;
}

.power-action-card.poweroff:hover .power-action-icon,
.power-action-card.poweroff:hover .power-action-text,
.power-action-card.poweroff:hover label {
    color: #ffffff;
}

/* GTK Switch matching SwayNC */
switch {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.10);
    border-radius: 15px;
    border: none;
    min-width: 38px;
    min-height: 20px;
    box-shadow: none;
    outline: none;
    color: transparent;
}

switch:checked {
    background-image: none;
    background-color: #ffffff;
    border: none;
    color: transparent;
}

switch slider {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.35);
    border-radius: 10px;
    min-width: 16px;
    min-height: 16px;
    margin: 2px;
    border: none;
    box-shadow: none;
}

switch:checked slider {
    background-image: none;
    background-color: rgba(255, 255, 255, 0.90);
    border: none;
}

switch label {
    font-size: 0px;
    color: transparent;
    opacity: 0;
}
"""


def clean_markup(text):
    if not text:
        return ""
    cleaned = re.sub(r"<[^>]+>", "", text)
    return cleaned.strip()

def auto_switch_bluetooth_audio():
    try:
        raw = subprocess.run(["pactl", "-f", "json", "list", "sinks"], capture_output=True, text=True, timeout=0.3).stdout
        if raw.strip():
            data = json.loads(raw)
            for s in data:
                name = s.get("name", "")
                if name.startswith("bluez_output"):
                    subprocess.run(["pactl", "set-default-sink", name], capture_output=True, timeout=0.2)
                    subprocess.run(["pactl", "set-sink-mute", name, "0"], capture_output=True, timeout=0.2)
                    inps_raw = subprocess.run(["pactl", "-f", "json", "list", "sink-inputs"], capture_output=True, text=True, timeout=0.2).stdout
                    if inps_raw.strip():
                        inps = json.loads(inps_raw)
                        for inp in inps:
                            inp_idx = str(inp.get("index", ""))
                            if inp_idx:
                                subprocess.run(["pactl", "move-sink-input", inp_idx, name], capture_output=True, timeout=0.2)
                    break
    except Exception:
        pass

def fast_get_brightness():
    try:
        with open("/sys/class/backlight/intel_backlight/brightness", "r") as f:
            cur = int(f.read().strip())
        with open("/sys/class/backlight/intel_backlight/max_brightness", "r") as f:
            mx = int(f.read().strip())
        return int(round((cur / mx) * 100))
    except Exception:
        return 50

def fast_get_volume():
    try:
        res = subprocess.run(["pactl", "get-sink-volume", "@DEFAULT_SINK@"], capture_output=True, text=True, timeout=0.08).stdout
        parts = res.split("/")
        vol = int(parts[1].strip().replace("%", "")) if len(parts) > 1 else 50
        mute_res = subprocess.run(["pactl", "get-sink-mute", "@DEFAULT_SINK@"], capture_output=True, text=True, timeout=0.08).stdout
        is_muted = "yes" in mute_res.lower()
        return vol, is_muted
    except Exception:
        return 50, False

def fast_get_mic_volume():
    try:
        res = subprocess.run(["pactl", "get-source-volume", "@DEFAULT_SOURCE@"], capture_output=True, text=True, timeout=0.08).stdout
        parts = res.split("/")
        vol = int(parts[1].strip().replace("%", "")) if len(parts) > 1 else 50
        mute_res = subprocess.run(["pactl", "get-source-mute", "@DEFAULT_SOURCE@"], capture_output=True, text=True, timeout=0.08).stdout
        is_muted = "yes" in mute_res.lower()
        return vol, is_muted
    except Exception:
        return 50, False

def fast_get_battery_details():
    try:
        base = "/sys/class/power_supply/BAT0"
        def read_val(name, default=0):
            p = f"{base}/{name}"
            if os.path.exists(p):
                try:
                    with open(p, "r") as f:
                        return int(f.read().strip())
                except Exception:
                    pass
            return default

        cap = read_val("capacity", 50)
        e_now = read_val("energy_now", 0)
        e_full = read_val("energy_full", 1)
        e_design = read_val("energy_full_design", 1)
        p_now = read_val("power_now", 0)
        cycles = read_val("cycle_count", 0)

        raw_status = "Discharging"
        if os.path.exists(f"{base}/status"):
            with open(f"{base}/status", "r") as f:
                raw_status = f.read().strip()

        threshold = 100
        for p in [f"{base}/charge_control_end_threshold", f"{base}/charge_stop_threshold"]:
            if os.path.exists(p):
                try:
                    with open(p, "r") as f:
                        threshold = int(f.read().strip())
                        break
                except Exception:
                    pass

        ico = "󰁹"
        if raw_status == "Charging":
            ico = "󱊥"
        elif cap > 80:
            ico = "󰁹"
        elif cap > 60:
            ico = "󰂀"
        elif cap > 40:
            ico = "󰁾"
        elif cap > 20:
            ico = "󰁼"
        else:
            ico = "󰁺"

        time_str = ""
        status = "Descargando"

        if raw_status == "Charging":
            status = "Cargando"
            if p_now > 0:
                target_pct = threshold if threshold <= 85 else 100
                rem_e = max(0, (e_full * (target_pct / 100.0)) - e_now)
                hours = rem_e / p_now
                h = int(hours)
                m = int((hours - h) * 60)
                time_str = f"󱐋 {h}h {m:02d}m para carga" if h > 0 else f"󱐋 {m}m para carga"
                p_val = f"󱐋 {round(p_now / 1e6, 1)} W"
            else:
                time_str = "󱐋 Cargando..."
                p_val = "󱐋 Activa"
            p_sub = "Potencia de carga"
        elif raw_status == "Discharging":
            status = ""
            if p_now > 0:
                hours = e_now / p_now
                h = int(hours)
                m = int((hours - h) * 60)
                time_str = f"{ico} {h}h {m:02d}m restantes"
                p_val = f"⚡ {round(p_now / 1e6, 1)} W"
            else:
                time_str = f"{ico} {cap}% en batería"
                p_val = "⚡ Normal"
            p_sub = "Consumo actual"
        elif raw_status == "Full":
            status = ""
            time_str = f"{ico} Batería al 100%"
            p_val = "󱐋 100%"
            p_sub = "Conectado a CA"
        elif raw_status == "Not charging":
            status = "Carga en pausa"
            time_str = f"{ico} Carga al {cap}% (Pausa)"
            p_val = f"󱐋 {cap}%"
            p_sub = "Carga en pausa"
        else:
            status = raw_status
            time_str = f"{ico} {cap}%"
            p_val = "-- W"
            p_sub = "Batería"

        # Temperatura de la batería
        bat_temp = None
        for tp in ["/sys/class/power_supply/BAT0/temp", "/sys/class/hwmon/hwmon4/temp5_input", "/sys/class/thermal/thermal_zone3/temp", "/sys/class/thermal/thermal_zone0/temp"]:
            if os.path.exists(tp):
                try:
                    with open(tp, "r") as f:
                        v = int(f.read().strip())
                        if v > 0:
                            bat_temp = int(v / 1000) if v > 1000 else (int(v / 10) if v > 100 else v)
                            break
                except Exception:
                    pass
        t_val = f" {bat_temp}°C" if bat_temp is not None else " --°C"
        t_sub = "Temperatura"

        health_pct = min(100, int((e_full / e_design) * 100)) if e_design > 0 else 100
        h_val = f"󰓅 {health_pct}%"
        h_sub = "Salud batería"

        c_val = f"󰑐 {cycles:,}" if cycles > 0 else "󰑐 0"
        c_sub = "Ciclos de carga"

        profile = "balanced"
        try:
            res = subprocess.run(["powerprofilesctl", "get"], capture_output=True, text=True, timeout=0.1)
            if res.returncode == 0 and res.stdout.strip():
                profile = res.stdout.strip()
        except Exception:
            if os.path.exists("/sys/firmware/acpi/platform_profile"):
                try:
                    with open("/sys/firmware/acpi/platform_profile", "r") as f:
                        p = f.read().strip()
                        if p == "low-power":
                            profile = "power-saver"
                        else:
                            profile = p
                except Exception:
                    pass

        return cap, status, time_str, p_val, p_sub, t_val, t_sub, h_val, h_sub, c_val, c_sub, profile
    except Exception:
        return 50, "Descargando", "󰁹 50% restantes", "⚡ -- W", "Consumo actual", " --°C", "Temperatura", "󰓅 100%", "Salud batería", "󰑐 0", "Ciclos de carga", "balanced"

def set_power_profile_fast(profile):
    try:
        subprocess.Popen(["powerprofilesctl", "set", profile])
    except Exception:
        if os.path.exists("/sys/firmware/acpi/platform_profile"):
            try:
                plat = "low-power" if profile == "power-saver" else profile
                with open("/sys/firmware/acpi/platform_profile", "w") as f:
                    f.write(plat + "\n")
            except Exception:
                pass

def set_battery_threshold_fast(threshold, callback=None):
    def _worker():
        written = False
        for path in ["/sys/class/power_supply/BAT0/charge_control_end_threshold", "/sys/class/power_supply/BAT0/charge_stop_threshold"]:
            if os.path.exists(path):
                try:
                    with open(path, "w") as f:
                        f.write(f"{threshold}\n")
                    written = True
                except Exception:
                    pass
        if not written:
            try:
                subprocess.run([
                    "notify-send", "-a", "Batería", "-u", "critical",
                    "Permiso Requerido",
                    "Abre una terminal y ejecuta el comando sudo para activar el control del 80% sin contraseña."
                ], timeout=1)
            except Exception:
                pass
        if callback:
            GLib.idle_add(callback)

    threading.Thread(target=_worker, daemon=True).start()

def fast_get_wifi_status():
    try:
        out = subprocess.run(["rfkill", "list", "wifi"], capture_output=True, text=True, timeout=0.05).stdout
        if "Soft blocked: yes" in out or "Hard blocked: yes" in out or not out.strip():
            return False, "Desactivado"
        return True, "Activo"
    except Exception:
        return False, "Desactivado"

def get_kernel_wifi_signal():
    try:
        with open("/proc/net/wireless", "r") as f:
            lines = f.readlines()
            for line in lines[2:]:
                parts = line.strip().split()
                if len(parts) >= 3:
                    qual_str = parts[2].replace(".", "")
                    qual = float(qual_str)
                    return max(0, min(100, int((qual / 70.0) * 100)))
    except Exception:
        pass
    return None

def fast_get_saved_wifi_connections():
    saved = []
    try:
        raw = subprocess.run(["nmcli", "-t", "-f", "NAME,TIMESTAMP,TYPE", "connection", "show"], capture_output=True, text=True, timeout=0.2).stdout
        conns = []
        for line in raw.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 3 and ("802-11-wireless" in parts[2] or "wireless" in parts[2] or "wifi" in parts[2]):
                name = parts[0].strip()
                try:
                    ts = int(parts[1].strip())
                except ValueError:
                    ts = 0
                conns.append((ts, name))
        conns.sort(key=lambda x: -x[0])
        saved = [name for _, name in conns]
    except Exception:
        pass
    return saved

def fast_get_active_wifi_connection():
    try:
        raw = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device"], capture_output=True, text=True, timeout=0.1).stdout
        for line in raw.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 4 and parts[1] == "wifi":
                st = parts[2].lower()
                conn = parts[3].strip()
                if ("connect" in st) and conn and conn != "--":
                    return conn
    except Exception:
        pass
    return None

def fast_get_cached_wifi_networks():
    networks = []
    real_sig = get_kernel_wifi_signal()
    active_ssid = fast_get_active_wifi_connection()
    seen = set()

    # 1. Non-blocking cached scan list
    try:
        raw = subprocess.run(["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "device", "wifi", "list", "--rescan", "no"], capture_output=True, text=True, timeout=0.25).stdout
        for line in raw.strip().split("\n"):
            if not line:
                continue
            parts = line.replace(r"\:", "__COLON__").split(":")
            if len(parts) >= 4:
                in_use = (parts[0].strip() == "*") or (active_ssid and parts[1].replace("__COLON__", ":").strip() == active_ssid)
                ssid = parts[1].replace("__COLON__", ":").strip()
                sig_str = parts[2].strip()
                sec = parts[3].replace("__COLON__", ":").strip()
                
                if ssid and ssid not in seen:
                    seen.add(ssid)
                    try:
                        sig_int = int(sig_str)
                    except ValueError:
                        sig_int = 50
                    if in_use and real_sig is not None:
                        sig_int = real_sig
                    networks.append({
                        "active": in_use,
                        "ssid": ssid,
                        "signal": sig_int,
                        "security": sec,
                        "saved": True
                    })
    except Exception:
        pass

    # 2. If connected network wasn't in scan list, add it immediately
    if active_ssid and active_ssid not in seen:
        seen.add(active_ssid)
        networks.insert(0, {
            "active": True,
            "ssid": active_ssid,
            "signal": real_sig if real_sig is not None else 65,
            "security": "WPA2",
            "saved": True
        })

    # 3. Fallback: Saved profiles if scan list is empty
    if not networks:
        for s in fast_get_saved_wifi_connections():
            if s not in seen:
                seen.add(s)
                is_active = (s == active_ssid)
                networks.append({
                    "active": is_active,
                    "ssid": s,
                    "signal": real_sig if (is_active and real_sig is not None) else 50,
                    "security": "Guardada",
                    "saved": True
                })

    networks.sort(key=lambda n: (not n["active"], -n["signal"]))
    return networks

def fast_get_bt_status():
    try:
        out = subprocess.run(["rfkill", "list", "bluetooth"], capture_output=True, text=True, timeout=0.05).stdout
        if "Soft blocked: yes" in out or "Hard blocked: yes" in out or not out.strip():
            return False, "Desactivado"
        return True, "Activo"
    except Exception:
        return False, "Desactivado"

def fast_get_cached_bt_devices():
    devices = []
    seen_macs = set()
    try:
        # 1. Get set of connected macs instantly (0.007s)
        connected_macs = set()
        raw_conn = subprocess.run(["bluetoothctl", "devices", "Connected"], capture_output=True, text=True, timeout=0.15).stdout
        for line in raw_conn.strip().split("\n"):
            if line.startswith("Device"):
                parts = line.split(" ", 2)
                if len(parts) >= 2:
                    connected_macs.add(parts[1])

        # 2. Get paired devices
        paired = subprocess.run(["bluetoothctl", "devices", "Paired"], capture_output=True, text=True, timeout=0.2).stdout
        for line in paired.strip().split("\n"):
            if not line.startswith("Device"):
                continue
            parts = line.split(" ", 2)
            if len(parts) >= 3:
                mac, name = parts[1], parts[2]
                seen_macs.add(mac)
                is_connected = (mac in connected_macs)
                devices.append({
                    "mac": mac,
                    "name": name,
                    "connected": is_connected,
                    "paired": True
                })

        # 3. Get all other devices
        all_devs = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True, timeout=0.2).stdout
        for line in all_devs.strip().split("\n"):
            if not line.startswith("Device"):
                continue
            parts = line.split(" ", 2)
            if len(parts) >= 3:
                mac, name = parts[1], parts[2]
                if mac not in seen_macs:
                    seen_macs.add(mac)
                    devices.append({
                        "mac": mac,
                        "name": name,
                        "connected": False,
                        "paired": False
                    })
    except Exception:
        pass
    return devices

def fast_get_nightlight_status():
    try:
        res = subprocess.run(["pgrep", "-f", "hyprsunset --temperature 4200"], capture_output=True, text=True, timeout=0.05)
        if res.returncode == 0:
            return True
        res_w = subprocess.run(["pidof", "wlsunset"], capture_output=True, text=True, timeout=0.05)
        if res_w.returncode == 0:
            return True
        res_g = subprocess.run(["pidof", "gammastep"], capture_output=True, text=True, timeout=0.05)
        return (res_g.returncode == 0)
    except Exception:
        return False

def fast_get_mako_dnd_status():
    try:
        out = subprocess.run(["makoctl", "mode"], capture_output=True, text=True, timeout=0.1).stdout
        return "dnd" in out
    except Exception:
        return False

def fast_get_mako_notifications():
    cache_file = os.path.expanduser("~/.cache/notifications_history.json")
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
        except Exception:
            pass
    return []




class QuickMenu(Gtk.Window):
    def __init__(self, initial_view="wifi"):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Quick Settings")
        
        # Compact Dimensions - Exact Uniform Size across all views
        self.set_size_request(330, 345)

        # Init LayerShell
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_namespace(self, "quick_menu")
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 10)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 12)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        # Apply CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS_STYLE.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.is_running = True

        self.connect("focus-out-event", self.on_focus_out)
        self.connect("key-press-event", self.on_key_press)

        # Main Box
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.main_box.set_size_request(330, -1)
        self.main_box.get_style_context().add_class("main-container")
        self.add(self.main_box)

        # Stack for views
        self.stack = Gtk.Stack()
        self.stack.set_homogeneous(True)
        self.stack.set_interpolate_size(True)
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(100)
        self.main_box.pack_start(self.stack, True, True, 0)

        # Tracking state
        self.user_sliding = False
        self.last_vol, self.last_muted = 50, False
        self.last_mic, self.last_mic_muted = 50, False
        self.last_bri = 50
        self.dismissed_ids = set()

        # Build Hardware Views
        self.view_wifi = self.build_wifi_view()
        self.view_bt = self.build_bt_view()
        self.view_audio = self.build_audio_view()
        self.view_brightness = self.build_brightness_view()
        self.view_power = self.build_power_view()
        self.view_battery = self.build_battery_view()
        self.view_notification = self.build_notification_view()

        self.view_wifi.show_all()
        self.view_bt.show_all()
        self.view_audio.show_all()
        self.view_brightness.show_all()
        self.view_power.show_all()
        self.view_battery.show_all()
        self.view_notification.show_all()

        self.stack.add_named(self.view_wifi, "wifi")
        self.stack.add_named(self.view_bt, "bt")
        self.stack.add_named(self.view_audio, "audio")
        self.stack.add_named(self.view_brightness, "brightness")
        self.stack.add_named(self.view_power, "power")
        self.stack.add_named(self.view_battery, "battery")
        self.stack.add_named(self.view_notification, "notification")

        # ⚡ INSTANT SYNCHRONOUS PRE-POPULATION
        self.sync_all_hardware_instant()

        self.current_view_name = "battery"

        self.is_running = True
        self.is_visible = False

        # Start IPC Server thread for live view switching
        self.start_ipc_server()

        # Start Hyprland event listener for workspace change auto-close
        self.start_hyprland_event_listener()

        # Fast background polling
        GLib.timeout_add(300, self.fast_periodic_refresh)

        # Show all widgets inside window once during initialization so all components and layers are realized
        self.show_all()

        if initial_view == "--daemon":
            self.switch_view("battery")
            self.hide()
        else:
            self.show_menu(initial_view)

    def start_hyprland_event_listener(self):
        def listener():
            try:
                his = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
                xdg = os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}")
                sock_path = f"{xdg}/hypr/{his}/.socket2.sock"
                if os.path.exists(sock_path):
                    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    s.connect(sock_path)
                    while self.is_running:
                        data = s.recv(1024).decode("utf-8", errors="ignore")
                        if not data:
                            break
                        for line in data.splitlines():
                            if line.startswith("workspace>>") or line.startswith("focusedmon>>"):
                                if self.is_visible:
                                    GLib.idle_add(self.hide_menu)
            except Exception:
                pass

        threading.Thread(target=listener, daemon=True).start()

    def on_focus_out(self, widget, event):
        if self.is_visible:
            self.hide_menu()
        return False

    def sync_all_hardware_instant(self):
        # 1. Brightness & Displays
        cur_b = fast_get_brightness()
        self.last_bri = cur_b
        self.bri_scale.set_value(cur_b)
        self.lbl_bri_val.set_text(f"{cur_b}%")
        self.update_bri_icon(cur_b)
        
        is_night = fast_get_nightlight_status()
        self.night_switch.handler_block_by_func(self.on_night_switch_toggled)
        self.night_switch.set_active(is_night)
        self.night_switch.handler_unblock_by_func(self.on_night_switch_toggled)

        # 2. Audio & Mic
        v, vm = fast_get_volume()
        self.last_vol, self.last_muted = v, vm
        self.vol_scale.set_value(v)
        self.lbl_vol_val.set_text(f"{v}%")
        self.update_vol_icon(v, vm)

        mv, mvm = fast_get_mic_volume()
        self.last_mic, self.last_mic_muted = mv, mvm
        self.mic_scale.set_value(mv)
        self.lbl_mic_val.set_text(f"{mv}%")
        self.update_mic_icon(mv, mvm)

        # 3. Wi-Fi (Instant cached list)
        w_on, _ = fast_get_wifi_status()
        self.wifi_sub_switch.handler_block_by_func(self.on_wifi_sub_switch_toggled)
        self.wifi_sub_switch.set_active(w_on)
        self.wifi_sub_switch.handler_unblock_by_func(self.on_wifi_sub_switch_toggled)
        if w_on:
            nets = fast_get_cached_wifi_networks()
            self.render_wifi_networks_list(w_on, nets)
        else:
            self.render_wifi_networks_list(False, [])

        # 4. Bluetooth (Instant cached devices)
        b_on, _ = fast_get_bt_status()
        self.bt_sub_switch.handler_block_by_func(self.on_bt_sub_switch_toggled)
        self.bt_sub_switch.set_active(b_on)
        self.bt_sub_switch.handler_unblock_by_func(self.on_bt_sub_switch_toggled)
        if b_on:
            devs = fast_get_cached_bt_devices()
            self.render_bt_devices_list(b_on, devs)
        else:
            self.render_bt_devices_list(False, [])

        # 5. Battery & Power
        self.refresh_battery_state()

        # 6. Notifications & DND
        self.refresh_notification_state()

    def start_ipc_server(self):
        def server_thread():
            try:
                if os.path.exists(SOCK_FILE):
                    os.remove(SOCK_FILE)
                srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                srv.bind(SOCK_FILE)
                srv.listen(5)
                while self.is_running:
                    conn, _ = srv.accept()
                    data = conn.recv(1024).decode("utf-8").strip()
                    if data:
                        GLib.idle_add(self.handle_ipc_message, data)
                    conn.close()
            except Exception:
                pass

        threading.Thread(target=server_thread, daemon=True).start()

    def handle_ipc_message(self, requested_view):
        norm = self.normalize_view_name(requested_view)
        if self.is_visible:
            if norm == self.current_view_name:
                self.hide_menu()
            else:
                self.show_menu(norm)
        else:
            self.show_menu(norm)

    def normalize_view_name(self, name):
        if not name:
            return getattr(self, "current_view_name", "battery") if getattr(self, "current_view_name", "battery") not in ("main", "") else "battery"
        name = str(name).strip().lower()
        if "bat" in name or "energy" in name or "charge" in name or "power-profile" in name:
            return "battery"
        elif "audio" in name or "vol" in name or "sound" in name or "pulse" in name or "sink" in name:
            return "audio"
        elif "bt" in name or "blue" in name:
            return "bt"
        elif "wifi" in name or "net" in name or "wlan" in name:
            return "wifi"
        elif "bright" in name or "backlight" in name or "light" in name:
            return "brightness"
        elif "power" in name or "shutdown" in name:
            return "power"
        elif "notif" in name or "dnd" in name or "alert" in name or "mako" in name or "swaync" in name:
            return "notification"
        return getattr(self, "current_view_name", "battery") if getattr(self, "current_view_name", "battery") not in ("main", "") else "battery"

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide_menu()
            return True
        return False

    def hide_menu(self):
        self.is_visible = False
        self.hide()

    def show_menu(self, view_name):
        self.switch_view(view_name)
        self.is_visible = True
        self.show()
        self.present()

    def close_app(self):
        self.hide_menu()

    def quit_app(self):
        self.is_running = False
        try:
            if os.path.exists(SOCK_FILE):
                os.remove(SOCK_FILE)
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
        except Exception:
            pass
        Gtk.main_quit()

    def switch_view(self, view_name):
        norm = self.normalize_view_name(view_name)
        self.current_view_name = norm
        self.stack.set_visible_child_name(norm)

        if norm == "wifi":
            self.refresh_wifi_state(rescan=False)
        elif norm == "bt":
            self.refresh_bt_state()
        elif norm == "audio":
            self.refresh_audio_state()
        elif norm == "brightness":
            self.refresh_brightness_state()
        elif norm == "battery":
            self.refresh_battery_state()
        elif norm == "notification":
            self.refresh_notification_state()

        self.resize(330, 1)

    # ==========================================================================
    # 2. AUDIO & MICROPHONE VIEW (CLICK EN VOLUMEN DE WAYBAR)
    # ==========================================================================
    def build_audio_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("view-header")

        lbl_title = Gtk.Label(label="Audio", xalign=0)
        lbl_title.get_style_context().add_class("view-title")

        header.pack_start(lbl_title, True, True, 2)
        box.pack_start(header, False, False, 0)

        # Frame for Audio controls
        frame_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame_box.set_vexpand(True)
        frame_box.set_hexpand(True)
        frame_box.get_style_context().add_class("inset-frame")

        # 1. Salida de Audio
        lbl_sec_vol = Gtk.Label(label="Altavoces", xalign=0)
        lbl_sec_vol.get_style_context().add_class("item-sub")
        lbl_sec_vol.set_margin_start(4)
        frame_box.pack_start(lbl_sec_vol, False, False, 0)

        vol_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        vol_box.get_style_context().add_class("slider-container")

        self.btn_vol_mute = Gtk.Button()
        self.btn_vol_mute.get_style_context().add_class("slider-btn")
        self.lbl_vol_icon = Gtk.Label(label="󰕾")
        self.lbl_vol_icon.get_style_context().add_class("slider-icon")
        self.btn_vol_mute.add(self.lbl_vol_icon)
        self.btn_vol_mute.connect("clicked", self.on_vol_mute_clicked)

        self.vol_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.vol_scale.set_draw_value(False)
        self.vol_scale.connect("change-value", self.on_scale_drag_start)
        self.vol_scale.connect("value-changed", self.on_volume_scale_changed)

        self.lbl_vol_val = Gtk.Label(label="--%", xalign=1)
        self.lbl_vol_val.get_style_context().add_class("slider-value")

        vol_box.pack_start(self.btn_vol_mute, False, False, 0)
        vol_box.pack_start(self.vol_scale, True, True, 0)
        vol_box.pack_end(self.lbl_vol_val, False, False, 0)
        frame_box.pack_start(vol_box, False, False, 0)

        # 2. Entrada de Audio
        lbl_sec_mic = Gtk.Label(label="Micrófono", xalign=0)
        lbl_sec_mic.get_style_context().add_class("item-sub")
        lbl_sec_mic.set_margin_start(4)
        lbl_sec_mic.set_margin_top(4)
        frame_box.pack_start(lbl_sec_mic, False, False, 0)

        mic_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mic_box.get_style_context().add_class("slider-container")

        self.btn_mic_mute = Gtk.Button()
        self.btn_mic_mute.get_style_context().add_class("slider-btn")
        self.lbl_mic_icon = Gtk.Label(label="󰍬")
        self.lbl_mic_icon.get_style_context().add_class("slider-icon")
        self.btn_mic_mute.add(self.lbl_mic_icon)
        self.btn_mic_mute.connect("clicked", self.on_mic_mute_clicked)

        self.mic_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.mic_scale.set_draw_value(False)
        self.mic_scale.connect("change-value", self.on_scale_drag_start)
        self.mic_scale.connect("value-changed", self.on_mic_scale_changed)

        self.lbl_mic_val = Gtk.Label(label="--%", xalign=1)
        self.lbl_mic_val.get_style_context().add_class("slider-value")

        mic_box.pack_start(self.btn_mic_mute, False, False, 0)
        mic_box.pack_start(self.mic_scale, True, True, 0)
        mic_box.pack_end(self.lbl_mic_val, False, False, 0)
        frame_box.pack_start(mic_box, False, False, 0)

        # 3. Lista de Dispositivos de Salida
        lbl_sec_devs = Gtk.Label(label="Dispositivo de salida", xalign=0)
        lbl_sec_devs.get_style_context().add_class("item-sub")
        lbl_sec_devs.set_margin_start(4)
        lbl_sec_devs.set_margin_top(4)
        frame_box.pack_start(lbl_sec_devs, False, False, 0)

        self.audio_scrolled = Gtk.ScrolledWindow()
        self.audio_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.audio_scrolled.set_min_content_height(90)

        self.audio_sinks_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.audio_scrolled.add(self.audio_sinks_box)
        frame_box.pack_start(self.audio_scrolled, True, True, 0)

        box.pack_start(frame_box, True, True, 0)

        return box

    def on_scale_drag_start(self, scale, scroll, val):
        self.user_sliding = True
        GLib.timeout_add(300, self.reset_user_sliding)
        return False

    def reset_user_sliding(self):
        self.user_sliding = False
        return False

    def on_volume_scale_changed(self, scale):
        val = int(scale.get_value())
        self.last_vol = val
        self.lbl_vol_val.set_text(f"{val}%")
        self.update_vol_icon(val, self.last_muted)
        subprocess.Popen(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{val}%"])

    def on_vol_mute_clicked(self, btn):
        subprocess.run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"])
        v, vm = fast_get_volume()
        self.last_vol, self.last_muted = v, vm
        self.update_vol_icon(v, vm)

    def on_mic_scale_changed(self, scale):
        val = int(scale.get_value())
        self.last_mic = val
        self.lbl_mic_val.set_text(f"{val}%")
        self.update_mic_icon(val, self.last_mic_muted)
        subprocess.Popen(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"{val}%"])

    def on_mic_mute_clicked(self, btn):
        subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"])
        mv, mvm = fast_get_mic_volume()
        self.last_mic, self.last_mic_muted = mv, mvm
        self.update_mic_icon(mv, mvm)

    def update_vol_icon(self, vol_val, is_muted):
        v_ctx = self.lbl_vol_icon.get_style_context()
        if is_muted:
            self.lbl_vol_icon.set_text("󰝟")
            v_ctx.add_class("muted")
        else:
            v_ctx.remove_class("muted")
            if vol_val >= 60:
                self.lbl_vol_icon.set_text("󰕾")
            elif vol_val >= 25:
                self.lbl_vol_icon.set_text("󰖀")
            else:
                self.lbl_vol_icon.set_text("󰕿")

    def update_mic_icon(self, mic_val, is_muted):
        m_ctx = self.lbl_mic_icon.get_style_context()
        if is_muted:
            self.lbl_mic_icon.set_text("󰍭")
            m_ctx.add_class("muted")
        else:
            m_ctx.remove_class("muted")
            self.lbl_mic_icon.set_text("󰍬")

    def refresh_audio_state(self):
        def worker():
            vol, vol_muted = fast_get_volume()
            mic, mic_muted = fast_get_mic_volume()
            sinks = []
            try:
                raw = subprocess.run(["pactl", "-f", "json", "list", "sinks"], capture_output=True, text=True, timeout=0.15).stdout
                data = json.loads(raw)
                default_sink = subprocess.run(["pactl", "get-default-sink"], capture_output=True, text=True, timeout=0.08).stdout.strip()
                for s in data:
                    name = s.get("name", "")
                    desc = s.get("description", name)
                    sinks.append({
                        "name": name,
                        "description": desc,
                        "is_default": (name == default_sink)
                    })
            except Exception:
                pass

            GLib.idle_add(self.update_audio_ui, vol, vol_muted, mic, mic_muted, sinks)

        threading.Thread(target=worker, daemon=True).start()

    def update_audio_ui(self, vol, vol_muted, mic, mic_muted, sinks):
        self.last_vol, self.last_muted = vol, vol_muted
        self.last_mic, self.last_mic_muted = mic, mic_muted

        if not self.user_sliding:
            self.vol_scale.handler_block_by_func(self.on_volume_scale_changed)
            self.vol_scale.set_value(vol)
            self.vol_scale.handler_unblock_by_func(self.on_volume_scale_changed)
            self.lbl_vol_val.set_text(f"{vol}%")
            self.update_vol_icon(vol, vol_muted)

            self.mic_scale.handler_block_by_func(self.on_mic_scale_changed)
            self.mic_scale.set_value(mic)
            self.mic_scale.handler_unblock_by_func(self.on_mic_scale_changed)
            self.lbl_mic_val.set_text(f"{mic}%")
            self.update_mic_icon(mic, mic_muted)

        for child in self.audio_sinks_box.get_children():
            self.audio_sinks_box.remove(child)

        for sink in sinks:
            card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            card.get_style_context().add_class("item-card")
            if sink["is_default"]:
                card.get_style_context().add_class("selected")

            ico_str = "󰋋" if "headphone" in sink["name"].lower() or "blue" in sink["name"].lower() else "󰓃"
            lbl_ico = Gtk.Label(label=ico_str)

            lbl_name = Gtk.Label(label=sink["description"], xalign=0)
            lbl_name.get_style_context().add_class("item-title")
            lbl_name.set_line_wrap(True)

            card.pack_start(lbl_ico, False, False, 4)
            card.pack_start(lbl_name, True, True, 0)

            if sink["is_default"]:
                lbl_tag = Gtk.Label(label="Activo")
                lbl_tag.get_style_context().add_class("item-sub")
                card.pack_end(lbl_tag, False, False, 4)
            else:
                btn_sel = Gtk.Button(label="Usar")
                btn_sel.get_style_context().add_class("action-btn")
                btn_sel.connect("clicked", lambda b, sname=sink["name"]: self.set_default_sink(sname))
                card.pack_end(btn_sel, False, False, 0)

            self.audio_sinks_box.pack_start(card, False, False, 0)

        self.audio_sinks_box.show_all()

    def set_default_sink(self, sink_name):
        subprocess.run(["pactl", "set-default-sink", sink_name])
        self.refresh_audio_state()

    # ==========================================================================
    # 3. BRIGHTNESS & DISPLAY VIEW (CLICK EN BRILLO DE WAYBAR)
    # ==========================================================================
    def build_brightness_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("view-header")

        lbl_title = Gtk.Label(label="Pantalla y Apariencia", xalign=0)
        lbl_title.get_style_context().add_class("view-title")

        header.pack_start(lbl_title, True, True, 2)
        box.pack_start(header, False, False, 0)

        # Frame
        frame_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        frame_box.set_vexpand(True)
        frame_box.set_hexpand(True)
        frame_box.set_size_request(-1, 305)
        frame_box.get_style_context().add_class("inset-frame")

        # 1. Nivel de Brillo (Solo slider con porcentaje, sin botones presets)
        lbl_b_info = Gtk.Label(label="Nivel de Brillo", xalign=0)
        lbl_b_info.get_style_context().add_class("item-sub")
        lbl_b_info.set_margin_start(4)
        frame_box.pack_start(lbl_b_info, False, False, 0)

        bri_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bri_box.get_style_context().add_class("slider-container")

        self.lbl_bri_icon = Gtk.Label(label="󰃠")
        self.lbl_bri_icon.get_style_context().add_class("slider-icon")

        self.bri_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 5, 100, 1)
        self.bri_scale.set_draw_value(False)
        self.bri_scale.connect("change-value", self.on_scale_drag_start)
        self.bri_scale.connect("value-changed", self.on_brightness_scale_changed)

        self.lbl_bri_val = Gtk.Label(label="--%", xalign=1)
        self.lbl_bri_val.get_style_context().add_class("slider-value")

        bri_box.pack_start(self.lbl_bri_icon, False, False, 4)
        bri_box.pack_start(self.bri_scale, True, True, 0)
        bri_box.pack_end(self.lbl_bri_val, False, False, 0)
        frame_box.pack_start(bri_box, False, False, 0)

        # 2. Luz Nocturna Card
        night_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        night_card.get_style_context().add_class("item-card")
        night_card.set_margin_top(6)

        lbl_n_icon = Gtk.Label(label="󰃠")
        lbl_n_icon.get_style_context().add_class("slider-icon")

        lbl_n_title = Gtk.Label(label="Luz nocturna", xalign=0)
        lbl_n_title.get_style_context().add_class("item-title")

        self.night_switch = Gtk.Switch()
        self.night_switch.set_valign(Gtk.Align.CENTER)
        self.night_switch.connect("state-set", self.on_night_switch_toggled)

        night_card.pack_start(lbl_n_icon, False, False, 4)
        night_card.pack_start(lbl_n_title, True, True, 0)
        night_card.pack_end(self.night_switch, False, False, 0)
        frame_box.pack_start(night_card, False, False, 0)



        box.pack_start(frame_box, True, True, 0)

        return box

    def on_brightness_scale_changed(self, scale):
        val = int(scale.get_value())
        self.last_bri = val
        self.lbl_bri_val.set_text(f"{val}%")
        self.update_bri_icon(val)
        subprocess.Popen(["brightnessctl", "set", f"{val}%"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def update_bri_icon(self, bri_val):
        if bri_val >= 70:
            self.lbl_bri_icon.set_text("󰃠")
        elif bri_val >= 35:
            self.lbl_bri_icon.set_text("󰃟")
        else:
            self.lbl_bri_icon.set_text("󰃞")

    def on_night_switch_toggled(self, switch, state):
        def worker():
            if state:
                subprocess.run(["pkill", "-9", "-f", "hyprsunset"], capture_output=True)
                subprocess.Popen(["hyprsunset", "--temperature", "4200"])
            else:
                subprocess.run(["pkill", "-9", "-f", "hyprsunset"], capture_output=True)
                subprocess.Popen(["hyprsunset", "--temperature", "7000"])
                subprocess.run(["killall", "wlsunset", "gammastep"], capture_output=True)
            time.sleep(0.15)
            GLib.idle_add(self.refresh_brightness_state)
            GLib.idle_add(self.refresh_toggles_state)
        threading.Thread(target=worker, daemon=True).start()
        return False

    def refresh_brightness_state(self):
        cur_bri = fast_get_brightness()
        self.last_bri = cur_bri
        if not self.user_sliding:
            self.bri_scale.handler_block_by_func(self.on_brightness_scale_changed)
            self.bri_scale.set_value(cur_bri)
            self.bri_scale.handler_unblock_by_func(self.on_brightness_scale_changed)
            self.lbl_bri_val.set_text(f"{cur_bri}%")
            self.update_bri_icon(cur_bri)

        is_night = fast_get_nightlight_status()
        self.night_switch.handler_block_by_func(self.on_night_switch_toggled)
        self.night_switch.set_active(is_night)
        self.night_switch.handler_unblock_by_func(self.on_night_switch_toggled)

    # ==========================================================================
    # 4. WI-FI SUBVIEW (CLICK EN WI-FI DE WAYBAR)
    # ==========================================================================
    def build_wifi_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("view-header")

        lbl_title = Gtk.Label(label="Wi-Fi", xalign=0)
        lbl_title.get_style_context().add_class("view-title")

        header.pack_start(lbl_title, True, True, 2)
        box.pack_start(header, False, False, 0)

        # Frame for Networks list
        frame_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        frame_box.set_vexpand(True)
        frame_box.set_hexpand(True)
        frame_box.get_style_context().add_class("inset-frame")

        # Power Switch Box with status label
        power_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        power_box.get_style_context().add_class("section-box")

        lbl = Gtk.Label(label="Wi-Fi", xalign=0)
        lbl.get_style_context().add_class("power-label")

        self.wifi_sub_status_lbl = Gtk.Label(label="", xalign=0)
        self.wifi_sub_status_lbl.get_style_context().add_class("status-label")

        self.wifi_sub_switch = Gtk.Switch()
        self.wifi_sub_switch.set_valign(Gtk.Align.CENTER)
        self.wifi_sub_switch.connect("state-set", self.on_wifi_sub_switch_toggled)

        power_box.pack_start(lbl, False, False, 0)
        power_box.pack_start(self.wifi_sub_status_lbl, True, True, 0)
        power_box.pack_end(self.wifi_sub_switch, False, False, 0)
        frame_box.pack_start(power_box, False, False, 0)

        self.wifi_scrolled = Gtk.ScrolledWindow()
        self.wifi_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.wifi_scrolled.set_min_content_height(140)

        self.wifi_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.wifi_scrolled.add(self.wifi_list_box)
        frame_box.pack_start(self.wifi_scrolled, True, True, 0)

        box.pack_start(frame_box, True, True, 0)

        return box

    def scan_wifi_manual(self):
        self.wifi_sub_status_lbl.set_text("Buscando...")
        self.refresh_wifi_state(rescan=True)

    def on_wifi_sub_switch_toggled(self, switch, state):
        if state:
            self.wifi_sub_status_lbl.set_text("Encendiendo...")
        else:
            self.wifi_sub_status_lbl.set_text("")
            self.render_wifi_networks_list(False, [])

        def worker():
            cmd = "on" if state else "off"
            subprocess.run(["nmcli", "radio", "wifi", cmd])
            if state:
                subprocess.run(["rfkill", "unblock", "wifi"], capture_output=True)
                saved = fast_get_saved_wifi_connections()
                if saved:
                    cached_init = [{"active": (i == 0), "ssid": s, "signal": 70, "security": "Guardada", "saved": True} for i, s in enumerate(saved)]
                    GLib.idle_add(self.render_wifi_networks_list, True, cached_init)

                # Hardware readiness poll loop: wait for wireless card wlp0s20f3 state >= 30
                for _ in range(40):
                    time.sleep(0.05)
                    st = subprocess.run(["nmcli", "-g", "GENERAL.STATE", "device", "show", "wlp0s20f3"], capture_output=True, text=True, timeout=0.2).stdout.strip()
                    if st.startswith("30"):
                        try:
                            if saved:
                                subprocess.Popen(["nmcli", "connection", "up", saved[0]])
                            else:
                                subprocess.Popen(["nmcli", "device", "connect", "wlp0s20f3"])
                        except Exception:
                            pass
                        break
                    elif st.startswith("100"):
                        break

                # Continuous monitor until fully connected and settled
                for _ in range(30):
                    time.sleep(0.2)
                    act = fast_get_active_wifi_connection()
                    if act:
                        nets = fast_get_cached_wifi_networks()
                        if nets and any(n.get("active") for n in nets):
                            GLib.idle_add(self.render_wifi_networks_list, True, nets)
                            break
            GLib.idle_add(lambda: self.refresh_wifi_state(rescan=False))
        threading.Thread(target=worker, daemon=True).start()
        return False

    def refresh_wifi_state(self, rescan=False):
        def worker():
            is_enabled, _ = fast_get_wifi_status()
            networks = []
            if is_enabled:
                networks = fast_get_cached_wifi_networks()
                GLib.idle_add(self.render_wifi_networks_list, is_enabled, networks)

                if rescan or not networks:
                    subprocess.run(["nmcli", "device", "wifi", "list", "--rescan", "yes"], capture_output=True)
                    fresh_nets = fast_get_cached_wifi_networks()
                    if fresh_nets:
                        GLib.idle_add(self.render_wifi_networks_list, is_enabled, fresh_nets)
                return

            GLib.idle_add(self.render_wifi_networks_list, is_enabled, networks)

        threading.Thread(target=worker, daemon=True).start()

    def render_wifi_networks_list(self, is_enabled, networks):
        self.wifi_sub_status_lbl.set_text("")
        self.wifi_sub_switch.handler_block_by_func(self.on_wifi_sub_switch_toggled)
        self.wifi_sub_switch.set_active(is_enabled)
        self.wifi_sub_switch.handler_unblock_by_func(self.on_wifi_sub_switch_toggled)

        for child in self.wifi_list_box.get_children():
            self.wifi_list_box.remove(child)

        if not is_enabled:
            lbl = Gtk.Label(label="󰤮  Wi-Fi Desactivado", margin_top=40)
            lbl.get_style_context().add_class("item-sub")
            self.wifi_list_box.pack_start(lbl, True, True, 0)
            self.wifi_list_box.show_all()
            return

        if not networks:
            lbl = Gtk.Label(label="󰤨  Buscando redes...", margin_top=40)
            lbl.get_style_context().add_class("item-sub")
            self.wifi_list_box.pack_start(lbl, True, True, 0)
            self.wifi_list_box.show_all()
            return

        active_nets = [n for n in networks if n.get("active", False)]
        other_nets = [n for n in networks if not n.get("active", False)]

        if active_nets:
            for net in active_nets:
                card = self.create_wifi_card(net)
                self.wifi_list_box.pack_start(card, False, False, 0)

        # Section header for available networks with refresh button
        avail_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        avail_box.set_margin_top(8 if active_nets else 2)
        avail_box.set_margin_bottom(4)

        lbl_avail = Gtk.Label(label="REDES DISPONIBLES", xalign=0)
        lbl_avail.get_style_context().add_class("section-title")

        btn_scan = Gtk.Button(label="󰑐")
        btn_scan.get_style_context().add_class("icon-btn")
        btn_scan.set_tooltip_text("Escanear Redes")
        btn_scan.connect("clicked", lambda b: self.scan_wifi_manual())

        avail_box.pack_start(lbl_avail, True, True, 0)
        avail_box.pack_end(btn_scan, False, False, 0)
        self.wifi_list_box.pack_start(avail_box, False, False, 0)

        if other_nets:
            for net in other_nets:
                card = self.create_wifi_card(net)
                self.wifi_list_box.pack_start(card, False, False, 0)
        else:
            lbl_none = Gtk.Label(label="No se detectaron más redes cercanas", margin_top=10)
            lbl_none.get_style_context().add_class("item-sub")
            self.wifi_list_box.pack_start(lbl_none, False, False, 0)

        self.wifi_list_box.show_all()

    def create_wifi_card(self, net):
        card_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        card_box.get_style_context().add_class("item-card")
        if net["active"]:
            card_box.get_style_context().add_class("connected")

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        sig = net["signal"]
        icon_str = "󰤨" if sig >= 75 else ("󰤥" if sig >= 50 else ("󰤢" if sig >= 25 else "󰤟"))
        icon_lbl = Gtk.Label(label=icon_str)

        title_text = net["ssid"]
        if net.get("security") and net["security"] != "--":
            title_text += " 󰌾"
        title_lbl = Gtk.Label(label=title_text, xalign=0)
        title_lbl.get_style_context().add_class("item-title")

        row.pack_start(icon_lbl, False, False, 4)
        row.pack_start(title_lbl, True, True, 0)

        btn = Gtk.Button()
        if net["active"]:
            btn.set_label("Desconectar")
            btn.get_style_context().add_class("action-btn")
            btn.get_style_context().add_class("disconnect")
            btn.connect("clicked", lambda b, s=net["ssid"]: self.disconnect_wifi(s))
        else:
            btn.set_label("Conectar")
            btn.get_style_context().add_class("action-btn")
            btn.connect("clicked", lambda b, s=net["ssid"], sec=net["security"], cb=card_box: self.init_connect_wifi(s, sec, cb))

        row.pack_end(btn, False, False, 0)
        card_box.pack_start(row, False, False, 0)
        return card_box

    def disconnect_wifi(self, ssid):
        def worker():
            subprocess.run(["nmcli", "device", "disconnect", "wlan0"], capture_output=True)
            subprocess.run(["nmcli", "device", "disconnect", "wlp0s20f3"], capture_output=True)
            GLib.idle_add(self.refresh_wifi_state)
        threading.Thread(target=worker, daemon=True).start()

    def init_connect_wifi(self, ssid, security, card_box):
        saved = subprocess.run(["nmcli", "-t", "-f", "NAME", "connection", "show"], capture_output=True, text=True).stdout
        if ssid in [s.strip() for s in saved.split("\n")]:
            self.connect_wifi(ssid, None)
            return

        if getattr(card_box, "_has_pwd_entry", False):
            return

        card_box._has_pwd_entry = True

        pwd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        pwd_box.set_margin_top(6)

        entry = Gtk.Entry()
        entry.set_visibility(False)
        entry.set_placeholder_text("Contraseña...")
        entry.get_style_context().add_class("password-entry")

        btn_ok = Gtk.Button(label="OK")
        btn_ok.get_style_context().add_class("action-btn")

        def submit(b=None):
            pwd = entry.get_text()
            if pwd:
                self.connect_wifi(ssid, pwd)

        entry.connect("activate", submit)
        btn_ok.connect("clicked", submit)

        pwd_box.pack_start(entry, True, True, 0)
        pwd_box.pack_end(btn_ok, False, False, 0)

        card_box.pack_start(pwd_box, False, False, 0)
        card_box.show_all()
        entry.grab_focus()

    def connect_wifi(self, ssid, password):
        self.wifi_sub_status_lbl.set_text("Conectando...")
        def worker():
            if password:
                subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", password], capture_output=True, text=True)
            else:
                subprocess.run(["nmcli", "connection", "up", ssid], capture_output=True, text=True)
            
            GLib.idle_add(lambda: self.wifi_sub_status_lbl.set_text(""))
            GLib.idle_add(lambda: self.refresh_wifi_state(rescan=False))

        threading.Thread(target=worker, daemon=True).start()

    # ==========================================================================
    # 5. BLUETOOTH SUBVIEW (CLICK EN BLUETOOTH DE WAYBAR)
    # ==========================================================================
    def build_bt_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("view-header")

        lbl_title = Gtk.Label(label="Bluetooth", xalign=0)
        lbl_title.get_style_context().add_class("view-title")

        header.pack_start(lbl_title, True, True, 2)
        box.pack_start(header, False, False, 0)

        # Frame for Devices list
        frame_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        frame_box.set_vexpand(True)
        frame_box.set_hexpand(True)
        frame_box.get_style_context().add_class("inset-frame")

        power_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        power_box.get_style_context().add_class("section-box")

        lbl = Gtk.Label(label="Bluetooth", xalign=0)
        lbl.get_style_context().add_class("power-label")

        self.bt_sub_status_lbl = Gtk.Label(label="", xalign=0)
        self.bt_sub_status_lbl.get_style_context().add_class("status-label")

        self.bt_sub_switch = Gtk.Switch()
        self.bt_sub_switch.set_valign(Gtk.Align.CENTER)
        self.bt_sub_switch.connect("state-set", self.on_bt_sub_switch_toggled)

        power_box.pack_start(lbl, False, False, 0)
        power_box.pack_start(self.bt_sub_status_lbl, True, True, 0)
        power_box.pack_end(self.bt_sub_switch, False, False, 0)
        frame_box.pack_start(power_box, False, False, 0)

        self.bt_scrolled = Gtk.ScrolledWindow()
        self.bt_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.bt_scrolled.set_min_content_height(140)

        self.bt_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.bt_scrolled.add(self.bt_list_box)
        frame_box.pack_start(self.bt_scrolled, True, True, 0)

        box.pack_start(frame_box, True, True, 0)

        return box

    def on_bt_sub_switch_toggled(self, switch, state):
        if state:
            self.bt_sub_status_lbl.set_text("Encendiendo...")
        else:
            self.bt_sub_status_lbl.set_text("")
            self.render_bt_devices_list(False, [])

        def worker():
            if state:
                subprocess.run(["rfkill", "unblock", "bluetooth"], capture_output=True)
                time.sleep(0.15)
                subprocess.run(["bluetoothctl", "power", "on"], capture_output=True)
                found = False
                for _ in range(12):
                    time.sleep(0.25)
                    status = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True, timeout=0.4).stdout
                    if "Powered: yes" in status:
                        devs = fast_get_cached_bt_devices()
                        if devs:
                            GLib.idle_add(self.render_bt_devices_list, True, devs)
                            found = True
                            break
                if not found:
                    GLib.idle_add(self.refresh_bt_state)
            else:
                subprocess.run(["bluetoothctl", "power", "off"], capture_output=True)
                subprocess.run(["rfkill", "block", "bluetooth"], capture_output=True)
                GLib.idle_add(self.refresh_bt_state)
        threading.Thread(target=worker, daemon=True).start()
        return False

    def scan_bluetooth(self):
        self.bt_sub_status_lbl.set_text("Buscando...")
        def worker():
            subprocess.run(["bluetoothctl", "--timeout", "5", "scan", "on"], capture_output=True)
            GLib.idle_add(lambda: self.bt_sub_status_lbl.set_text(""))
            GLib.idle_add(self.refresh_bt_state)
        threading.Thread(target=worker, daemon=True).start()

    def refresh_bt_state(self):
        def worker():
            is_enabled, _ = fast_get_bt_status()
            devices = []
            if is_enabled:
                devices = fast_get_cached_bt_devices()
                if any(d.get("connected") for d in devices):
                    auto_switch_bluetooth_audio()

            GLib.idle_add(self.render_bt_devices_list, is_enabled, devices)

        threading.Thread(target=worker, daemon=True).start()

    def render_bt_devices_list(self, is_enabled, devices):
        self.bt_sub_status_lbl.set_text("")
        self.bt_sub_switch.handler_block_by_func(self.on_bt_sub_switch_toggled)
        self.bt_sub_switch.set_active(is_enabled)
        self.bt_sub_switch.handler_unblock_by_func(self.on_bt_sub_switch_toggled)

        for child in self.bt_list_box.get_children():
            self.bt_list_box.remove(child)

        if not is_enabled:
            lbl = Gtk.Label(label="󰂲  Bluetooth Desactivado", margin_top=40)
            lbl.get_style_context().add_class("item-sub")
            self.bt_list_box.pack_start(lbl, True, True, 0)
            self.bt_list_box.show_all()
            return

        paired_devs = [d for d in devices if d.get("paired", True)]
        avail_devs = [d for d in devices if not d.get("paired", True)]

        if paired_devs:
            for dev in paired_devs:
                card = self.create_bt_card(dev)
                self.bt_list_box.pack_start(card, False, False, 0)

        # Section header for available devices with search button
        avail_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        avail_box.set_margin_top(8 if paired_devs else 2)
        avail_box.set_margin_bottom(4)

        lbl_avail = Gtk.Label(label="DISPOSITIVOS DISPONIBLES", xalign=0)
        lbl_avail.get_style_context().add_class("section-title")

        btn_scan = Gtk.Button(label="󰂰")
        btn_scan.get_style_context().add_class("icon-btn")
        btn_scan.set_tooltip_text("Buscar Dispositivos")
        btn_scan.connect("clicked", lambda b: self.scan_bluetooth())

        avail_box.pack_start(lbl_avail, True, True, 0)
        avail_box.pack_end(btn_scan, False, False, 0)
        self.bt_list_box.pack_start(avail_box, False, False, 0)

        if avail_devs:
            for dev in avail_devs:
                card = self.create_bt_card(dev)
                self.bt_list_box.pack_start(card, False, False, 0)
        else:
            msg = "Toca 󰂰 para buscar nuevos dispositivos" if paired_devs else "󰂯  No hay dispositivos encontrados\nToca 󰂰 para buscar"
            lbl_empty = Gtk.Label(label=msg, margin_top=10)
            lbl_empty.set_justify(Gtk.Justification.CENTER)
            lbl_empty.get_style_context().add_class("item-sub")
            self.bt_list_box.pack_start(lbl_empty, False, False, 0)

        self.bt_list_box.show_all()

    def create_bt_card(self, dev):
        card_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        card_box.get_style_context().add_class("item-card")
        if dev["connected"]:
            card_box.get_style_context().add_class("connected")

        icon_str = "󰂱" if dev["connected"] else "󰂯"
        icon_lbl = Gtk.Label(label=icon_str)

        title_lbl = Gtk.Label(label=dev["name"], xalign=0)
        title_lbl.get_style_context().add_class("item-title")

        card_box.pack_start(icon_lbl, False, False, 4)
        card_box.pack_start(title_lbl, True, True, 0)

        btn = Gtk.Button()
        if dev["connected"]:
            btn.set_label("Desconectar")
            btn.get_style_context().add_class("action-btn")
            btn.get_style_context().add_class("disconnect")
            btn.connect("clicked", lambda b, m=dev["mac"]: self.disconnect_bt(m))
        else:
            btn.set_label("Conectar")
            btn.get_style_context().add_class("action-btn")
            btn.connect("clicked", lambda b, m=dev["mac"]: self.connect_bt(m))

        card_box.pack_end(btn, False, False, 0)
        return card_box

    def connect_bt(self, mac):
        self.bt_sub_status_lbl.set_text("Conectando...")
        def worker():
            subprocess.run(["bluetoothctl", "trust", mac], capture_output=True)
            subprocess.run(["bluetoothctl", "connect", mac], capture_output=True)
            time.sleep(0.4)
            auto_switch_bluetooth_audio()
            GLib.idle_add(lambda: self.bt_sub_status_lbl.set_text(""))
            GLib.idle_add(self.refresh_bt_state)
            GLib.idle_add(self.refresh_audio_state)
        threading.Thread(target=worker, daemon=True).start()

    def disconnect_bt(self, mac):
        self.bt_sub_status_lbl.set_text("Desconectando...")
        def worker():
            subprocess.run(["bluetoothctl", "disconnect", mac], capture_output=True)
            GLib.idle_add(lambda: self.bt_sub_status_lbl.set_text(""))
            GLib.idle_add(self.refresh_bt_state)
        threading.Thread(target=worker, daemon=True).start()

    # ==========================================================================
    # 6. POWER MENU VIEW
    # ==========================================================================
    def build_power_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("view-header")

        lbl_p_title = Gtk.Label(label="Menú de Apagado", xalign=0)
        lbl_p_title.get_style_context().add_class("view-title")

        header.pack_start(lbl_p_title, True, True, 2)
        box.pack_start(header, False, False, 0)

        # Frame
        frame_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame_box.set_vexpand(True)
        frame_box.set_hexpand(True)
        frame_box.set_size_request(-1, 305)
        frame_box.get_style_context().add_class("inset-frame")

        actions = [
            ("", "Bloquear", "pidof hyprlock || hyprlock", False),
            ("󰒲", "Suspender", "systemctl suspend", False),
            ("󰍃", "Cerrar sesión", "hyprctl dispatch exit", False),
            ("󰜉", "Reiniciar", "systemctl reboot", False),
            ("", "Apagar", "systemctl poweroff", True),
        ]

        for icon, label, cmd, is_danger in actions:
            btn = Gtk.Button()
            btn.get_style_context().add_class("power-action-card")
            if is_danger:
                btn.get_style_context().add_class("poweroff")

            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            icon_lbl = Gtk.Label(label=icon)
            icon_lbl.get_style_context().add_class("power-action-icon")

            text_lbl = Gtk.Label(label=label, xalign=0)
            text_lbl.get_style_context().add_class("power-action-text")

            btn_box.pack_start(icon_lbl, False, False, 4)
            btn_box.pack_start(text_lbl, True, True, 0)
            btn.add(btn_box)

            btn.connect("clicked", lambda b, c=cmd: self.run_power_cmd(c))
            frame_box.pack_start(btn, False, False, 0)

        box.pack_start(frame_box, True, True, 0)
        return box

    def run_power_cmd(self, cmd):
        self.close_app()
        subprocess.Popen(cmd, shell=True)

    # ==========================================================================
    # BATTERY & POWER PROFILES VIEW
    # ==========================================================================
    def build_battery_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("view-header")

        lbl_title = Gtk.Label(label="Batería y Energía", xalign=0)
        lbl_title.get_style_context().add_class("view-title")

        btn_refresh = Gtk.Button(label="󰑐")
        btn_refresh.get_style_context().add_class("icon-btn")
        btn_refresh.set_tooltip_text("Actualizar Batería")
        btn_refresh.connect("clicked", lambda b: self.refresh_battery_state())

        header.pack_start(lbl_title, True, True, 2)
        header.pack_end(btn_refresh, False, False, 0)
        box.pack_start(header, False, False, 0)

        # Frame
        frame_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        frame_box.set_vexpand(True)
        frame_box.set_hexpand(True)
        frame_box.get_style_context().add_class("inset-frame")

        # 1. Info Card (Tiempo restante con ícono de batería)
        self.bat_info_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.bat_info_card.get_style_context().add_class("item-card")

        self.bat_status_lbl = Gtk.Label(label="Calculando...", xalign=0)
        self.bat_status_lbl.get_style_context().add_class("item-title")
        self.bat_info_card.pack_start(self.bat_status_lbl, True, True, 4)
        frame_box.pack_start(self.bat_info_card, False, False, 0)

        # 2. Mosaico 2x2 (Grid)
        grid = Gtk.Grid()
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)

        # Tile 1: Potencia / Consumo (Fila 0, Col 0)
        tile_power = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        tile_power.get_style_context().add_class("metric-tile")
        self.bat_power_val = Gtk.Label(label="-- W", xalign=0.5)
        self.bat_power_val.get_style_context().add_class("metric-val")
        self.bat_power_sub = Gtk.Label(label="Consumo actual", xalign=0.5)
        self.bat_power_sub.get_style_context().add_class("metric-sub")
        tile_power.pack_start(self.bat_power_val, True, True, 0)
        tile_power.pack_start(self.bat_power_sub, False, False, 0)
        grid.attach(tile_power, 0, 0, 1, 1)

        # Tile 2: Temperatura (Fila 0, Col 1)
        tile_temp = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        tile_temp.get_style_context().add_class("metric-tile")
        self.bat_temp_val = Gtk.Label(label="--°C", xalign=0.5)
        self.bat_temp_val.get_style_context().add_class("metric-val")
        self.bat_temp_sub = Gtk.Label(label="Temperatura", xalign=0.5)
        self.bat_temp_sub.get_style_context().add_class("metric-sub")
        tile_temp.pack_start(self.bat_temp_val, True, True, 0)
        tile_temp.pack_start(self.bat_temp_sub, False, False, 0)
        grid.attach(tile_temp, 1, 0, 1, 1)

        # Tile 3: Salud batería (Fila 1, Col 0)
        tile_health = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        tile_health.get_style_context().add_class("metric-tile")
        self.bat_health_val = Gtk.Label(label="--%", xalign=0.5)
        self.bat_health_val.get_style_context().add_class("metric-val")
        self.bat_health_sub = Gtk.Label(label="Salud batería", xalign=0.5)
        self.bat_health_sub.get_style_context().add_class("metric-sub")
        tile_health.pack_start(self.bat_health_val, True, True, 0)
        tile_health.pack_start(self.bat_health_sub, False, False, 0)
        grid.attach(tile_health, 0, 1, 1, 1)

        # Tile 4: Ciclos de carga (Fila 1, Col 1)
        tile_cycles = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        tile_cycles.get_style_context().add_class("metric-tile")
        self.bat_cycles_val = Gtk.Label(label="--", xalign=0.5)
        self.bat_cycles_val.get_style_context().add_class("metric-val")
        self.bat_cycles_sub = Gtk.Label(label="Ciclos de carga", xalign=0.5)
        self.bat_cycles_sub.get_style_context().add_class("metric-sub")
        tile_cycles.pack_start(self.bat_cycles_val, True, True, 0)
        tile_cycles.pack_start(self.bat_cycles_sub, False, False, 0)
        grid.attach(tile_cycles, 1, 1, 1, 1)

        frame_box.pack_start(grid, False, False, 0)

        # 3. Power Profiles Section
        sec_profile = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        sec_profile.get_style_context().add_class("section-box")

        lbl_sec_prof = Gtk.Label(label="MODO DE ENERGÍA", xalign=0)
        lbl_sec_prof.get_style_context().add_class("power-label")
        sec_profile.pack_start(lbl_sec_prof, False, False, 0)

        profiles_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        profiles_bar.set_homogeneous(True)

        self.btn_prof_saver = Gtk.Button(label="󰌪 Ahorro")
        self.btn_prof_saver.get_style_context().add_class("profile-btn")
        self.btn_prof_saver.connect("clicked", lambda b: self.on_select_power_profile("power-saver"))

        self.btn_prof_balanced = Gtk.Button(label="󰗑 Balance")
        self.btn_prof_balanced.get_style_context().add_class("profile-btn")
        self.btn_prof_balanced.connect("clicked", lambda b: self.on_select_power_profile("balanced"))

        self.btn_prof_perf = Gtk.Button(label="󰓅 Rendim.")
        self.btn_prof_perf.get_style_context().add_class("profile-btn")
        self.btn_prof_perf.connect("clicked", lambda b: self.on_select_power_profile("performance"))

        profiles_bar.pack_start(self.btn_prof_saver, True, True, 0)
        profiles_bar.pack_start(self.btn_prof_balanced, True, True, 0)
        profiles_bar.pack_start(self.btn_prof_perf, True, True, 0)
        sec_profile.pack_start(profiles_bar, False, False, 0)

        frame_box.pack_start(sec_profile, False, False, 0)

        box.pack_start(frame_box, True, True, 0)
        return box

    def on_select_power_profile(self, profile):
        set_power_profile_fast(profile)
        self.update_profile_buttons(profile)

    def update_profile_buttons(self, profile):
        for btn, p_name in [(self.btn_prof_saver, "power-saver"), (self.btn_prof_balanced, "balanced"), (self.btn_prof_perf, "performance")]:
            ctx = btn.get_style_context()
            if p_name == profile:
                ctx.add_class("active")
            else:
                ctx.remove_class("active")

    def refresh_battery_state(self):
        cap, status, time_str, p_val, p_sub, t_val, t_sub, h_val, h_sub, c_val, c_sub, profile = fast_get_battery_details()
        
        stat_text = time_str if time_str else (f"󰁹 {cap}%" if not status else status)

        if self.bat_status_lbl.get_text() != stat_text:
            self.bat_status_lbl.set_text(stat_text)

        if self.bat_power_val.get_text() != p_val:
            self.bat_power_val.set_text(p_val)
        if self.bat_power_sub.get_text() != p_sub:
            self.bat_power_sub.set_text(p_sub)

        if self.bat_temp_val.get_text() != t_val:
            self.bat_temp_val.set_text(t_val)
        if self.bat_temp_sub.get_text() != t_sub:
            self.bat_temp_sub.set_text(t_sub)

        if self.bat_health_val.get_text() != h_val:
            self.bat_health_val.set_text(h_val)
        if self.bat_health_sub.get_text() != h_sub:
            self.bat_health_sub.set_text(h_sub)

        if self.bat_cycles_val.get_text() != c_val:
            self.bat_cycles_val.set_text(c_val)
        if self.bat_cycles_sub.get_text() != c_sub:
            self.bat_cycles_sub.set_text(c_sub)

        self.update_profile_buttons(profile)

    # ==========================================================================
    # NOTIFICATIONS VIEW (Mako Integration)
    # ==========================================================================
    def build_notification_view(self):
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)

        # Header
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.get_style_context().add_class("view-header")

        lbl_title = Gtk.Label(label="Notificaciones", xalign=0)
        lbl_title.get_style_context().add_class("view-title")

        btn_clear = Gtk.Button(label="󰃢  Limpiar todo")
        btn_clear.get_style_context().add_class("trash-btn")
        btn_clear.connect("clicked", lambda b: self.clear_all_notifications())

        header.pack_start(lbl_title, True, True, 2)
        header.pack_end(btn_clear, False, False, 0)
        box.pack_start(header, False, False, 0)

        # Frame
        frame_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        frame_box.set_vexpand(True)
        frame_box.set_hexpand(True)
        frame_box.get_style_context().add_class("inset-frame")

        # DND Switch Box (No molestar al estilo SwayNC)
        dnd_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        dnd_box.get_style_context().add_class("section-box")

        lbl_dnd = Gtk.Label(label="No molestar", xalign=0)
        lbl_dnd.get_style_context().add_class("power-label")

        self.notif_dnd_switch = Gtk.Switch()
        self.notif_dnd_switch.set_valign(Gtk.Align.CENTER)
        self.notif_dnd_switch.connect("notify::active", self.on_notif_dnd_switch_toggled)

        dnd_box.pack_start(lbl_dnd, True, True, 0)
        dnd_box.pack_end(self.notif_dnd_switch, False, False, 0)
        frame_box.pack_start(dnd_box, False, False, 0)

        # Scrolled Notification List
        self.notif_scrolled = Gtk.ScrolledWindow()
        self.notif_scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.notif_scrolled.set_min_content_height(140)

        self.notif_list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.notif_scrolled.add(self.notif_list_box)
        frame_box.pack_start(self.notif_scrolled, True, True, 0)

        box.pack_start(frame_box, True, True, 0)
        return box

    def on_notif_dnd_switch_toggled(self, switch, gparam):
        is_active = switch.get_active()
        notifs = getattr(self, "_last_notifs_cache", [])
        self._last_notif_sig = (is_active, tuple(n.get("id") for n in notifs))
        def worker():
            cmd = ["makoctl", "mode", "-s" if is_active else "-r", "dnd"]
            subprocess.run(cmd, capture_output=True)
            subprocess.run(["pkill", "-RTMIN+1", "waybar"], capture_output=True)
        threading.Thread(target=worker, daemon=True).start()

    def clear_all_notifications(self):
        def worker():
            cache_file = os.path.expanduser("~/.cache/notifications_history.json")
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump([], f)
            except Exception:
                pass
            subprocess.run(["makoctl", "dismiss", "-a"], capture_output=True)
            subprocess.run(["pkill", "-RTMIN+1", "waybar"], capture_output=True)
            GLib.idle_add(self.refresh_notification_state)
        threading.Thread(target=worker, daemon=True).start()

    def dismiss_single_notification(self, notif_id):
        def worker():
            cache_file = os.path.expanduser("~/.cache/notifications_history.json")
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        items = json.load(f)
                    filtered = [n for n in items if n.get("id") != notif_id]
                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(filtered, f, ensure_ascii=False, indent=2)
                except Exception:
                    pass
            subprocess.run(["makoctl", "dismiss", "-n", str(notif_id)], capture_output=True)
            subprocess.run(["pkill", "-RTMIN+1", "waybar"], capture_output=True)
            GLib.idle_add(self.refresh_notification_state)
        threading.Thread(target=worker, daemon=True).start()

    def refresh_notification_state(self):
        def worker():
            is_dnd = fast_get_mako_dnd_status()
            notifs = fast_get_mako_notifications()
            GLib.idle_add(self.render_notifications_list, is_dnd, notifs)
        threading.Thread(target=worker, daemon=True).start()

    def render_notifications_list(self, is_dnd, notifications):
        self._last_notifs_cache = notifications
        self._last_notif_sig = (is_dnd, tuple(n.get("id") for n in notifications))
        self.notif_dnd_switch.handler_block_by_func(self.on_notif_dnd_switch_toggled)
        self.notif_dnd_switch.set_active(is_dnd)
        self.notif_dnd_switch.handler_unblock_by_func(self.on_notif_dnd_switch_toggled)

        for child in self.notif_list_box.get_children():
            self.notif_list_box.remove(child)

        if not notifications:
            placeholder = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            placeholder.set_margin_top(40)
            placeholder.set_margin_bottom(20)

            icon_str = "󰂛" if is_dnd else "󰂚"
            icon_lbl = Gtk.Label(label=icon_str)
            icon_lbl.get_style_context().add_class("empty-icon")
            icon_lbl.set_markup(f"<span size='xx-large'>{icon_str}</span>")

            text_lbl = Gtk.Label(label="No hay notificaciones")
            text_lbl.get_style_context().add_class("item-sub")

            placeholder.pack_start(icon_lbl, False, False, 0)
            placeholder.pack_start(text_lbl, False, False, 0)
            self.notif_list_box.pack_start(placeholder, True, True, 0)
            self.notif_list_box.show_all()
            return

        for notif in notifications:
            n_id = notif.get("id")
            app_name = notif.get("app_name") or "Notificación"
            summary = notif.get("summary") or ""
            body = notif.get("body") or ""
            urgency = str(notif.get("urgency", "normal")).lower()

            card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            card.get_style_context().add_class("notif-box-white")
            if urgency == "critical":
                card.get_style_context().add_class("critical")

            # Left icon
            icon_str = "󰵅" if urgency == "critical" else "󰂚"
            icon_lbl = Gtk.Label(label=icon_str)
            icon_lbl.get_style_context().add_class("notif-icon-pure")
            card.pack_start(icon_lbl, False, False, 0)

            # Text content
            text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            text_box.set_hexpand(True)

            title_txt = summary if summary else app_name
            title_lbl = Gtk.Label(label=title_txt, xalign=0)
            title_lbl.get_style_context().add_class("notif-appname")
            title_lbl.set_line_wrap(True)
            text_box.pack_start(title_lbl, False, False, 0)

            if body and body != summary:
                body_lbl = Gtk.Label(label=body, xalign=0)
                body_lbl.get_style_context().add_class("notif-body")
                body_lbl.set_line_wrap(True)
                text_box.pack_start(body_lbl, False, False, 0)

            card.pack_start(text_box, True, True, 0)

            # Close button
            btn_close = Gtk.Button(label="󰅖")
            btn_close.get_style_context().add_class("icon-btn")
            btn_close.set_valign(Gtk.Align.CENTER)
            btn_close.connect("clicked", lambda b, i=n_id: self.dismiss_single_notification(i))
            card.pack_end(btn_close, False, False, 0)

            self.notif_list_box.pack_start(card, False, False, 0)

        self.notif_list_box.show_all()

    # ==========================================================================
    # ULTRA-FAST REAL-TIME HARDWARE SYNC
    # ==========================================================================
    def fast_periodic_refresh(self):
        if not self.is_visible:
            return True

        curr = self.stack.get_visible_child_name()
        if curr == "audio" and not self.user_sliding:
            v, vm = fast_get_volume()
            if v != self.last_vol or vm != self.last_muted:
                self.last_vol, self.last_muted = v, vm
                self.vol_scale.handler_block_by_func(self.on_volume_scale_changed)
                self.vol_scale.set_value(v)
                self.vol_scale.handler_unblock_by_func(self.on_volume_scale_changed)
                self.lbl_vol_val.set_text(f"{v}%")
                self.update_vol_icon(v, vm)

            mv, mvm = fast_get_mic_volume()
            if mv != self.last_mic or mvm != self.last_mic_muted:
                self.last_mic, self.last_mic_muted = mv, mvm
                self.mic_scale.handler_block_by_func(self.on_mic_scale_changed)
                self.mic_scale.set_value(mv)
                self.mic_scale.handler_unblock_by_func(self.on_mic_scale_changed)
                self.lbl_mic_val.set_text(f"{mv}%")
                self.update_mic_icon(mv, mvm)

        elif curr == "bt":
            b_on, _ = fast_get_bt_status()
            if b_on:
                devs = fast_get_cached_bt_devices()
                curr_sig = tuple((d["mac"], d["connected"], d["paired"]) for d in devs)
                if getattr(self, "_last_bt_sig", None) != curr_sig:
                    self._last_bt_sig = curr_sig
                    self.render_bt_devices_list(b_on, devs)
            else:
                if getattr(self, "_last_bt_sig", None) != False:
                    self._last_bt_sig = False
                    self.render_bt_devices_list(False, [])

        elif curr == "brightness" and not self.user_sliding:
            cur_b = fast_get_brightness()
            if cur_b != self.last_bri:
                self.last_bri = cur_b
                self.bri_scale.handler_block_by_func(self.on_brightness_scale_changed)
                self.bri_scale.set_value(cur_b)
                self.bri_scale.handler_unblock_by_func(self.on_brightness_scale_changed)
                self.lbl_bri_val.set_text(f"{cur_b}%")
                self.update_bri_icon(cur_b)

        elif curr == "battery":
            self.refresh_battery_state()

        elif curr == "notification":
            is_dnd = fast_get_mako_dnd_status()
            notifs = fast_get_mako_notifications()
            curr_sig = (is_dnd, tuple(n.get("id") for n in notifs))
            if getattr(self, "_last_notif_sig", None) != curr_sig:
                self._last_notif_sig = curr_sig
                self.render_notifications_list(is_dnd, notifs)

        return True

def main():
    target_view = "battery"
    if len(sys.argv) > 1:
        target_view = sys.argv[1].lower()

    # If instance already running, send view switch via unix domain socket (< 5ms response!)
    if os.path.exists(SOCK_FILE) and target_view != "--daemon":
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect(SOCK_FILE)
            s.send(target_view.encode("utf-8"))
            s.close()
            sys.exit(0)
        except Exception:
            try:
                os.remove(SOCK_FILE)
            except Exception:
                pass

    if os.path.exists(PID_FILE) and target_view == "--daemon":
        try:
            with open(PID_FILE, "r") as f:
                old_pid = int(f.read().strip())
            if old_pid != os.getpid():
                os.kill(old_pid, signal.SIGTERM)
            os.remove(PID_FILE)
        except Exception:
            pass

    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    app = QuickMenu(initial_view=target_view)

    signal.signal(signal.SIGINT, lambda *_: app.quit_app())
    signal.signal(signal.SIGTERM, lambda *_: app.quit_app())
    try:
        signal.signal(signal.SIGHUP, signal.SIG_IGN)
    except Exception:
        pass

    Gtk.main()

if __name__ == '__main__':
    main()
