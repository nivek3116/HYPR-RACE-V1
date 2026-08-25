#!/usr/bin/env python3

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

import os
import sys
import re
import json
import time
import glob
import socket
import select
import threading
import subprocess
_cached_meta = None
_last_meta_check = 0

def clean_brackets(s):
    if not s:
        return ""
    return re.sub(r'\s*[\(\[\{].*?[\)\]\}]', '', s)

def clean_artist_name(s):
    if not s:
        return ""
    s = clean_brackets(s)
    # Case-insensitive removal of VEVO (glued or separate)
    s = re.sub(r'(?i)vevo\b', '', s)
    s = re.sub(r'(?i)vevo$', '', s)
    # Remove channel suffixes
    s = re.sub(r'(?i)\s*-\s*Topic$', '', s)
    s = re.sub(r'(?i)\b(Topic|Official|Channel|Music|Records)\b', '', s)
    # Extract only the 1st primary artist
    s = re.sub(r'\s+(feat\.?|ft\.?|featuring|with)\s+.*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s*[,&/\\+]\s*.*', '', s)
    s = re.sub(r'\s+(x|X|y|and)\s+.*', '', s)
    return re.sub(r'\s+', ' ', s).strip(' -–—:|/\\')

def clean_song_title(s):
    if not s:
        return ""
    s = clean_brackets(s)
    # Remove trailing descriptors like " | Official Video", " - Video Oficial", " // Videoclip"
    s = re.sub(r'\s*(\||\/\/|\/|-|–|—)\s*(official\s*(music\s*)?video|video\s*oficial|audio\s*oficial|visualizer|letra|lyrics|lyric\s*video|videoclip|remix|audio|tema\s*oficial).*', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+(feat\.?|ft\.?|featuring|with)\s+.*', '', s, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', s).strip(' -–—:|/\\')

def get_player_info():
    global _cached_meta, _last_meta_check
    now = time.time()
    if _cached_meta is not None and (now - _last_meta_check) < 0.6:
        return _cached_meta

    _last_meta_check = now
    try:
        status_res = subprocess.run(['playerctl', 'status'], capture_output=True, text=True, timeout=0.3)
        status = status_res.stdout.strip()
        if status not in ('Playing', 'Paused'):
            _cached_meta = None
            return None

        # Fetch metadata
        meta_res = subprocess.run([
            'playerctl', 'metadata', '--format',
            '{{playerName}}\t{{artist}}\t{{title}}\t{{album}}\t{{xesam:url}}\t{{xesam:title}}\t{{xesam:artist}}'
        ], capture_output=True, text=True, timeout=0.3)
        
        parts = meta_res.stdout.strip().split('\t')
        player = parts[0] if len(parts) > 0 else ''
        artist = parts[1] if len(parts) > 1 else ''
        title = parts[2] if len(parts) > 2 else ''
        album = parts[3] if len(parts) > 3 else ''
        url = parts[4] if len(parts) > 4 else ''
        xesam_title = parts[5] if len(parts) > 5 else ''
        xesam_artist = parts[6] if len(parts) > 6 else ''

        if not title:
            title = xesam_title
        if not artist:
            artist = xesam_artist

        raw_title = title.strip() if title else ""
        raw_artist = artist.strip() if artist else ""

        if not raw_title:
            _cached_meta = None
            return None

        # 1. Split artist and song using space-surrounded hyphens or pipes
        split_match = re.split(r'\s+(?:[-–—:]|\|{1,2})\s+', raw_title, maxsplit=1)

        if len(split_match) == 2:
            art_part, title_part = split_match[0], split_match[1]
            artist_clean = clean_artist_name(art_part)
            song_clean = clean_song_title(title_part)
        else:
            song_clean = clean_song_title(raw_title)
            artist_clean = clean_artist_name(raw_artist)

        # Fallback if artist is empty or generic browser/platform name
        if not artist_clean or artist_clean.lower() in ('youtube', 'unknown', 'desconocido', 'firefox', 'chromium', 'brave', 'zen'):
            fallback_art = clean_artist_name(raw_artist)
            if fallback_art and fallback_art.lower() not in ('youtube', 'unknown', 'desconocido', 'firefox', 'chromium', 'brave', 'zen'):
                artist_clean = fallback_art

        if not artist_clean:
            artist_clean = "Desconocido"
        if not song_clean:
            song_clean = "Audio"

        # Deduplication rule: If artist is in title, omit redundant artist
        if artist_clean and (artist_clean.lower() in song_clean.lower()):
            combined = song_clean
        elif not artist_clean or artist_clean.lower() == "desconocido":
            combined = song_clean
        else:
            combined = f"{artist_clean} - {song_clean}"

        # 2. Character limit rule (28 chars)
        MAX_LEN = 28
        if len(combined) <= MAX_LEN:
            track_short = combined
        else:
            if len(song_clean) > MAX_LEN:
                track_short = song_clean[:MAX_LEN - 1] + "…"
            else:
                track_short = song_clean

        # 3. Detección de icono inteligente según la plataforma de audio
        p_lower = (player or "").lower()
        u_lower = (url or "").lower()
        t_lower = (raw_title or "").lower()
        
        if "spotify" in p_lower:
            base_icon = "󰓇"
        elif "youtube" in u_lower or "youtu.be" in u_lower or "youtube" in p_lower or "youtube" in t_lower:
            base_icon = "󰗃"
        elif "soundcloud" in u_lower or "soundcloud" in p_lower:
            base_icon = "󰓀"
        elif "apple" in p_lower or "cider" in p_lower:
            base_icon = "󰀵"
        elif "tidal" in p_lower:
            base_icon = "󰠱"
        elif "mpv" in p_lower or "vlc" in p_lower:
            base_icon = "󰕼"
        elif any(b in p_lower for b in ("firefox", "zen", "floorp", "librewolf")):
            base_icon = "󰈹"
        elif any(b in p_lower for b in ("chrome", "chromium", "brave", "edge", "opera", "vivaldi")):
            base_icon = "󰊯"
        elif any(b in p_lower for b in ("amberol", "rhythmbox", "audacious", "lollypop", "deadbeef")):
            base_icon = "󰎆"
        else:
            base_icon = "󰎈"

        icon = base_icon
        is_playing = (status == "Playing")
        status_str = "Sonando" if is_playing else "En pausa"
        text = f"{icon}  {track_short}"
        tooltip = f"<b>{song_clean}</b>\n{artist_clean}\n<i>({status_str})</i>"
        css_class = ["playing"] if is_playing else ["paused"]

        info = {
            "text": text,
            "tooltip": tooltip,
            "class": css_class,
            "percentage": 100,
            "_is_playing": is_playing
        }
        _cached_meta = info
        return info
    except Exception:
        _cached_meta = None
        return None

def get_terminal_process(term_pid, win_title):
    try:
        children_paths = glob.glob(f'/proc/{term_pid}/task/*/children')
        children = []
        for p in children_paths:
            with open(p, 'r') as f:
                children.extend(f.read().split())
        
        shell_pids = []
        for c in children:
            comm_file = f'/proc/{c}/comm'
            if os.path.exists(comm_file):
                with open(comm_file, 'r') as f:
                    comm = f.read().strip()
                if comm not in ('kitten', 'kitty'):
                    shell_pids.append(c)
        
        if shell_pids:
            shell_pid = shell_pids[0]
            shell_children_paths = glob.glob(f'/proc/{shell_pid}/task/*/children')
            shell_children = []
            for p in shell_children_paths:
                with open(p, 'r') as f:
                    shell_children.extend(f.read().split())
            
            for cp in reversed(shell_children):
                comm_file = f'/proc/{cp}/comm'
                if os.path.exists(comm_file):
                    with open(comm_file, 'r') as f:
                        direct_comm = f.read().strip()
                    if direct_comm not in ('cat', 'pgrep', 'ps', 'pstree', 'sleep', 'sh', 'bash', 'zsh', 'fish'):
                        return direct_comm
    except Exception:
        pass
    
    return 'kitty'

def get_active_app_info():
    try:
        res = subprocess.run(['hyprctl', 'activewindow', '-j'], capture_output=True, text=True, timeout=0.5)
        if not res.stdout:
            return {"text": "", "tooltip": "", "class": "empty", "percentage": 0}
        
        data = json.loads(res.stdout)
        win_class = data.get('class', '')
        win_title = data.get('title', '')
        win_pid = data.get('pid')

        # Opción 1: Auto-Hide cuando el escritorio está limpio (sin ventana activa)
        if not win_class:
            return {"text": "", "tooltip": "", "class": "empty", "percentage": 0}

        cl = win_class.lower()

        # Terminals & CLI Tools
        if any(term in cl for term in ('kitty', 'alacritty', 'foot', 'wezterm')):
            child = get_terminal_process(win_pid, win_title) if win_pid else 'kitty'
            c = child.lower()

            if 'nvim' in c or 'vim' in c:
                icon, name = '', 'Nvim'
            elif c in ('btop', 'htop', 'top'):
                icon, name = '󰄧', c.capitalize()
            elif c in ('yazi', 'ranger', 'lf'):
                icon, name = '󰉋', c.capitalize()
            elif c in ('lazygit', 'git'):
                icon, name = '󰊢', 'Lazygit'
            elif c == 'cava':
                icon, name = '󰝚', 'Cava'
            elif c in ('fastfetch', 'neofetch'):
                icon, name = '󰣇', 'Fastfetch'
            elif c == 'agy':
                icon, name = '󰚩', 'Agy'
            elif c in ('python', 'python3', 'ipython'):
                icon, name = '󰌠', 'Python'
            elif c in ('node', 'npm', 'bun', 'pnpm'):
                icon, name = '󰎙', c.capitalize()
            elif c in ('docker', 'podman'):
                icon, name = '󰡨', 'Docker'
            elif c == 'ssh':
                icon, name = '󰒍', 'SSH'
            elif c in ('bash', 'zsh', 'fish', 'sh', 'kitty'):
                icon, name = '', 'Kitty'
            else:
                icon, name = '', child[:10].capitalize()
                
            tooltip = f"<b>{name}</b>\n{win_title or child}"

        # File Managers
        elif 'thunar' in cl:
            icon, name, tooltip = '󰉋', 'Thunar', f"<b>Thunar</b>\n{win_title or 'Archivos'}"
        elif 'nemo' in cl:
            icon, name, tooltip = '󰉋', 'Nemo', f"<b>Nemo</b>\n{win_title or 'Archivos'}"
        elif 'nautilus' in cl or 'org.gnome.nautilus' in cl:
            icon, name, tooltip = '󰉋', 'Nautilus', f"<b>Nautilus</b>\n{win_title or 'Archivos'}"
        elif 'dolphin' in cl or 'org.kde.dolphin' in cl:
            icon, name, tooltip = '󰉋', 'Dolphin', f"<b>Dolphin</b>\n{win_title or 'Archivos'}"

        # Web Browsers
        elif 'firefox' in cl:
            icon, name, tooltip = '󰈹', 'Firefox', f"<b>Firefox</b>\n{win_title or 'Navegador'}"
        elif 'zen' in cl:
            icon, name, tooltip = '󰈹', 'Zen', f"<b>Zen</b>\n{win_title or 'Navegador'}"
        elif 'brave' in cl:
            icon, name, tooltip = '󰊯', 'Brave', f"<b>Brave</b>\n{win_title or 'Navegador'}"
        elif 'google-chrome' in cl or 'chrome' in cl:
            icon, name, tooltip = '󰊯', 'Chrome', f"<b>Chrome</b>\n{win_title or 'Navegador'}"
        elif 'chromium' in cl:
            icon, name, tooltip = '󰊯', 'Chromium', f"<b>Chromium</b>\n{win_title or 'Navegador'}"

        # Code Editors
        elif 'code' in cl or 'vscodium' in cl:
            icon, name, tooltip = '󰨞', 'Code', f"<b>VS Code</b>\n{win_title or 'Editor'}"

        # Communication
        elif any(d in cl for d in ('discord', 'vesktop', 'webcord')):
            icon, name, tooltip = '󰙯', 'Discord', f"<b>Discord</b>\n{win_title or 'Chat'}"
        elif 'telegram' in cl:
            icon, name, tooltip = '', 'Telegram', f"<b>Telegram</b>\n{win_title or 'Chat'}"
        elif 'slack' in cl:
            icon, name, tooltip = '󰒱', 'Slack', f"<b>Slack</b>\n{win_title or 'Chat'}"

        # Media Players
        elif 'spotify' in cl:
            icon, name, tooltip = '󰓇', 'Spotify', f"<b>Spotify</b>\n{win_title or 'Música'}"
        elif 'mpv' in cl:
            icon, name, tooltip = '󰕼', 'MPV', f"<b>MPV</b>\n{win_title or 'Video'}"
        elif 'vlc' in cl:
            icon, name, tooltip = '󰕼', 'VLC', f"<b>VLC</b>\n{win_title or 'Video'}"
        elif 'obs' in cl:
            icon, name, tooltip = '󰑋', 'OBS', '<b>OBS Studio</b>'

        # System Tools
        elif 'pavucontrol' in cl or 'volume' in cl:
            icon, name, tooltip = '󰕾', 'Audio', 'Control de Volumen'
        elif 'blueman' in cl or 'bluetooth' in cl:
            icon, name, tooltip = '󰂯', 'Bluetooth', 'Bluetooth'
        elif 'nm-connection-editor' in cl or 'network' in cl:
            icon, name, tooltip = '󰤨', 'Red', 'Conexiones de Red'
        elif 'rofi' in cl or 'wofi' in cl:
            icon, name, tooltip = '', 'Rofi', 'Lanzador'

        # Fallback
        else:
            clean_name = win_class.split('.')[-1].replace('-', ' ').replace('_', ' ').split()[0].capitalize()
            icon, name, tooltip = '', clean_name[:10], f"<b>{clean_name}</b>\n{win_title or win_class}"

        return {
            "text": f"{icon}  {name}",
            "tooltip": tooltip,
            "class": "active-app",
            "percentage": 100
        }
    except Exception:
        return {"text": "", "tooltip": "", "class": "empty", "percentage": 0}

def render():
    info = get_player_info()
    if not info:
        info = get_active_app_info()
    if not info:
        info = {"text": "", "tooltip": "", "class": "empty", "percentage": 0}
    out_info = {k: v for k, v in info.items() if not k.startswith('_')}
    print(json.dumps(out_info), flush=True)
    return info

def main():
    sock_path = f"{os.environ.get('XDG_RUNTIME_DIR', '')}/hypr/{os.environ.get('HYPRLAND_INSTANCE_SIGNATURE', '')}/.socket2.sock"
    
    sock = None
    if os.path.exists(sock_path):
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(sock_path)
        except Exception:
            sock = None

    while True:
        try:
            info = render()
            is_playing = bool(info.get('_is_playing', False))
            timeout = 0.5

            if sock:
                r, _, _ = select.select([sock], [], [], timeout)
                if r:
                    data = sock.recv(4096)
                    if not data:
                        break
            else:
                time.sleep(timeout)
        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(0.5)

if __name__ == '__main__':
    main()
