#!/usr/bin/env python3
import os
import sys
import json
import time
import socket
import subprocess

# Clases y títulos de ventanas que NO deben pausar el fondo animado
IGNORED_CLASSES = {
    "kitty",
    "rofi",
    "swaync",
    "swaync-control-center",
    "quick_menu",
    "sys_dashboard",
    "dashboard",
    "swayosd",
    "swayosd-server",
    "waybar",
    "pavucontrol",
    "org.pulseaudio.pavucontrol",
}

def is_mpvpaper_running():
    try:
        subprocess.check_output(["pgrep", "-x", "mpvpaper"])
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def pause_mpvpaper():
    if is_mpvpaper_running():
        subprocess.run(["pkill", "-STOP", "-x", "mpvpaper"], stderr=subprocess.DEVNULL)

def resume_mpvpaper():
    if is_mpvpaper_running():
        subprocess.run(["pkill", "-CONT", "-x", "mpvpaper"], stderr=subprocess.DEVNULL)

def update_playback_state(state: dict):
    if not is_mpvpaper_running():
        state["is_paused"] = False
        return

    try:
        ws_out = subprocess.check_output(["hyprctl", "activeworkspace", "-j"], text=True)
        ws_data = json.loads(ws_out)
        active_ws_id = ws_data.get("id")

        clients_out = subprocess.check_output(["hyprctl", "clients", "-j"], text=True)
        clients = json.loads(clients_out)

        # Contar ventanas bloqueadoras en el workspace activo
        blocking_count = 0
        for c in clients:
            client_ws_id = c.get("workspace", {}).get("id")
            if client_ws_id == active_ws_id:
                c_class = c.get("class", "").strip().lower()
                c_initial = c.get("initialClass", "").strip().lower()
                
                # Ignorar si coincide con la lista de apps permitidas
                if (c_class in IGNORED_CLASSES or 
                    c_initial in IGNORED_CLASSES or 
                    any(ignored in c_class for ignored in ("kitty", "rofi", "swaync", "dashboard"))):
                    continue
                
                blocking_count += 1

        if blocking_count > 0:
            if not state["is_paused"]:
                pause_mpvpaper()
                state["is_paused"] = True
        else:
            if state["is_paused"]:
                resume_mpvpaper()
                state["is_paused"] = False

    except Exception:
        pass

def get_socket_path():
    sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
    uid = os.getuid()
    if sig:
        sock = f"/run/user/{uid}/hypr/{sig}/.socket2.sock"
        if os.path.exists(sock):
            return sock

    hypr_dir = f"/run/user/{uid}/hypr"
    if os.path.exists(hypr_dir):
        for entry in os.listdir(hypr_dir):
            candidate = os.path.join(hypr_dir, entry, ".socket2.sock")
            if os.path.exists(candidate):
                return candidate
    return None

def main():
    sock_path = get_socket_path()
    if not sock_path:
        sys.exit(1)

    state = {"is_paused": False}

    # Estado inicial al arrancar
    update_playback_state(state)

    while True:
        try:
            if not os.path.exists(sock_path):
                time.sleep(1)
                continue

            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.connect(sock_path)
            buffer = ""
            while True:
                data = s.recv(2048)
                if not data:
                    break
                buffer += data.decode("utf-8", errors="ignore")
                while "\n" in buffer:
                    event, buffer = buffer.split("\n", 1)
                    if event.startswith((
                        "workspace>>",
                        "focusedmon>>",
                        "openwindow>>",
                        "closewindow>>",
                        "movewindow>>",
                        "fullscreen>>",
                        "changefloatingmode>>"
                    )):
                        update_playback_state(state)
        except (socket.error, ConnectionResetError, BrokenPipeError):
            time.sleep(1)
        except KeyboardInterrupt:
            resume_mpvpaper()
            break
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    main()
