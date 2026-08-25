#!/usr/bin/env python3

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

import os
import sys
import json
import time
import socket
import hashlib
import threading
import subprocess
import signal
import urllib.request
import urllib.parse

SOCK_FILE = "/tmp/waybar_media_popup.sock"
FLAG_FILE = "/tmp/media_popup_open"
CACHE_DIR = os.path.expanduser("~/.cache/media_covers")

# ⚡ ULTRA-FAST IPC CLIENT DISPATCH (<1ms)
if __name__ == '__main__' and os.path.exists(SOCK_FILE):
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "toggle"
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

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell, Pango

CSS_STYLE = """
@define-color bg rgba(0, 0, 0, 0.50);
@define-color border-bottom-color rgba(255, 255, 255, 0.85);
@define-color fg #ffffff;

* {
    font-family: 'Poppins', 'MonaspiceNe Nerd Font', 'JetBrains Mono Nerd Font', sans-serif;
    color: @fg;
    border: none;
    outline: none;
    box-shadow: none;
    text-shadow: none;
}

window {
    background-color: transparent;
}

.waybar-capsule {
    background-color: @bg;
    border-bottom: 0.22rem solid @border-bottom-color;
    border-radius: 50px;
    padding: 0.35rem 0.85rem;
}

.album-art {
    border-radius: 50%;
    margin-right: 8px;
}

.track-title {
    font-size: 13px;
    font-weight: 700;
    color: #ffffff;
}

.track-artist {
    font-size: 11px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.65);
}

.control-btn {
    background: transparent;
    color: #ffffff;
    font-size: 13px;
    padding: 0 4px;
    margin: 0 2px;
    border-radius: 50px;
}

.control-btn:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.20);
}

.play-pause-btn {
    background: transparent;
    color: #ffffff;
    font-size: 15px;
    padding: 0 5px;
    margin: 0 2px;
    border-radius: 50px;
}

.play-pause-btn:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.25);
}

.empty-state-box {
    padding: 0 4px;
}
.empty-state-label {
    font-size: 13px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.70);
}
.empty-state-btn {
    background: transparent;
    color: #ffffff;
    font-size: 12px;
    font-weight: 700;
    padding: 0 6px;
    border-radius: 50px;
}
.empty-state-btn:hover {
    background: rgba(255, 255, 255, 0.20);
}
"""

class MediaPopup(Gtk.Window):
    def __init__(self, start_hidden=False):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Waybar Player Capsule")
        os.makedirs(CACHE_DIR, exist_ok=True)

        self.is_visible = False
        self.is_running = True
        self.has_playback = False
        self.timer_id = None
        self.current_art_url = ""
        self.current_player = ""

        self.init_layer_shell()
        self.apply_styles()
        self.build_ui()
        self.init_events()

        # Seed state
        self.update_media_state()

        if not start_hidden:
            self.show_popup()
        else:
            self.hide()

        self.start_ipc_server()
        self.start_hyprland_event_listener()

    def init_layer_shell(self):
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.OVERLAY)
        GtkLayerShell.set_namespace(self, "waybar_media_popup")
        GtkLayerShell.set_exclusive_zone(self, -1)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        
        # 📌 Coordenadas exactas milimétricas del módulo de Waybar
        # Waybar margin-top: 8px + .modules-left padding: 10px = 18px
        # Inicio cápsula: 236px
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 18)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, 236)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

    def apply_styles(self):
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(CSS_STYLE.encode('utf-8'))
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def build_ui(self):
        self.set_resizable(False)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.get_style_context().add_class("waybar-capsule")
        self.add(self.main_box)

        # 1. WAYBAR COMPACT CAPSULE LAYOUT
        self.content_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.content_box.set_valign(Gtk.Align.CENTER)
        self.main_box.pack_start(self.content_box, True, True, 0)

        # Mini Cover Art (24x24 circular vinyl)
        cover_event = Gtk.EventBox()
        cover_event.connect("button-press-event", lambda w, e: self.open_app())
        cover_event.set_tooltip_text("Abrir aplicación")

        self.img_cover = Gtk.Image()
        self.img_cover.get_style_context().add_class("album-art")
        self.img_cover.set_size_request(24, 24)
        cover_event.add(self.img_cover)
        self.content_box.pack_start(cover_event, False, False, 0)

        # Title & Artist stacked compactly
        lbl_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        lbl_vbox.set_valign(Gtk.Align.CENTER)

        self.lbl_title = Gtk.Label(label="Cargando...", xalign=0)
        self.lbl_title.get_style_context().add_class("track-title")
        self.lbl_title.set_ellipsize(Pango.EllipsizeMode.END)
        self.lbl_title.set_max_width_chars(16)
        lbl_vbox.pack_start(self.lbl_title, False, False, 0)

        self.lbl_artist = Gtk.Label(label="", xalign=0)
        self.lbl_artist.get_style_context().add_class("track-artist")
        self.lbl_artist.set_ellipsize(Pango.EllipsizeMode.END)
        self.lbl_artist.set_max_width_chars(18)
        lbl_vbox.pack_start(self.lbl_artist, False, False, 0)

        self.content_box.pack_start(lbl_vbox, True, True, 0)

        # Buttons [Prev] [Play/Pause] [Next] (matching Waybar glyph styling)
        ctrl_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=1)
        ctrl_box.set_valign(Gtk.Align.CENTER)

        self.btn_prev = Gtk.Button(label="󰒮")
        self.btn_prev.get_style_context().add_class("control-btn")
        self.btn_prev.connect("clicked", lambda b: self.exec_playerctl("previous"))

        self.btn_play = Gtk.Button(label="󰐊")
        self.btn_play.get_style_context().add_class("play-pause-btn")
        self.btn_play.connect("clicked", lambda b: self.exec_playerctl("play-pause"))

        self.btn_next = Gtk.Button(label="󰒭")
        self.btn_next.get_style_context().add_class("control-btn")
        self.btn_next.connect("clicked", lambda b: self.exec_playerctl("next"))

        ctrl_box.pack_start(self.btn_prev, False, False, 0)
        ctrl_box.pack_start(self.btn_play, False, False, 0)
        ctrl_box.pack_start(self.btn_next, False, False, 0)
        self.content_box.pack_end(ctrl_box, False, False, 0)

        # 2. EMPTY STATE
        self.empty_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.empty_box.get_style_context().add_class("empty-state-box")
        self.empty_box.set_valign(Gtk.Align.CENTER)

        lbl_no_music = Gtk.Label(label="󰎈  Sin reproducción", xalign=0)
        lbl_no_music.get_style_context().add_class("empty-state-label")

        btn_launch_spotify = Gtk.Button(label="Iniciar")
        btn_launch_spotify.get_style_context().add_class("empty-state-btn")
        btn_launch_spotify.connect("clicked", lambda b: self.launch_spotify())

        self.empty_box.pack_start(lbl_no_music, True, True, 0)
        self.empty_box.pack_end(btn_launch_spotify, False, False, 0)
        self.main_box.pack_start(self.empty_box, False, False, 0)

    def init_events(self):
        self.connect("focus-out-event", self.on_focus_out)
        self.connect("key-press-event", self.on_key_press)

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide_popup()
            return True
        return False

    def on_focus_out(self, widget, event):
        if self.is_visible:
            self.hide_popup()
        return False

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
                                    GLib.idle_add(self.hide_popup)
            except Exception:
                pass

        threading.Thread(target=listener, daemon=True).start()

    def start_ipc_server(self):
        def server():
            try:
                if os.path.exists(SOCK_FILE):
                    os.remove(SOCK_FILE)
                s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                s.bind(SOCK_FILE)
                s.listen(5)
                while self.is_running:
                    conn, _ = s.accept()
                    data = conn.recv(128).decode("utf-8").strip()
                    conn.close()
                    if data == "toggle":
                        GLib.idle_add(self.toggle_popup)
                    elif data == "show":
                        GLib.idle_add(self.show_popup)
                    elif data == "hide":
                        GLib.idle_add(self.hide_popup)
                    elif data == "quit":
                        GLib.idle_add(self.quit_app)
            except Exception:
                pass

        threading.Thread(target=server, daemon=True).start()

    def toggle_popup(self):
        if self.is_visible:
            self.hide_popup()
        else:
            self.show_popup()

    def show_popup(self):
        self.is_visible = True
        
        # Ocultar la cápsula de texto de Waybar
        try:
            with open(FLAG_FILE, 'w') as f:
                f.write('1')
        except Exception:
            pass
            
        self.update_media_state()
        self.show_all()
        if self.has_playback:
            self.empty_box.hide()
        else:
            self.content_box.hide()
            
        self.present()

        if self.timer_id is None:
            self.timer_id = GLib.timeout_add(1000, self.periodic_update)

    def hide_popup(self):
        self.is_visible = False
        
        # Restaurar la cápsula de texto de Waybar
        if os.path.exists(FLAG_FILE):
            try:
                os.remove(FLAG_FILE)
            except Exception:
                pass
                
        self.hide()
        if self.timer_id:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

    def quit_app(self):
        self.is_running = False
        if os.path.exists(FLAG_FILE):
            try:
                os.remove(FLAG_FILE)
            except Exception:
                pass
        if os.path.exists(SOCK_FILE):
            try:
                os.remove(SOCK_FILE)
            except Exception:
                pass
        Gtk.main_quit()

    def periodic_update(self):
        if not self.is_visible:
            return False
        self.update_media_state()
        return True

    def exec_playerctl(self, *args):
        subprocess.run(["playerctl"] + list(args))
        GLib.timeout_add(60, self.update_media_state)

    def open_app(self):
        if self.current_player:
            subprocess.run(["hyprctl", "dispatch", "focuswindow", f"class:{self.current_player}"])
        else:
            self.launch_spotify()
        self.hide_popup()

    def launch_spotify(self):
        subprocess.Popen(["spotify"])
        self.hide_popup()

    def set_cover_art(self, art_url):
        if not art_url:
            self.set_default_art()
            return

        if art_url == self.current_art_url:
            return
        self.current_art_url = art_url

        if art_url.startswith("file://"):
            local_path = urllib.parse.unquote(art_url[7:])
            self.load_image_file(local_path)
        elif art_url.startswith("http://") or art_url.startswith("https://"):
            h = hashlib.md5(art_url.encode()).hexdigest()
            cache_file = os.path.join(CACHE_DIR, f"{h}.jpg")
            if os.path.exists(cache_file):
                self.load_image_file(cache_file)
            else:
                def download():
                    try:
                        req = urllib.request.Request(art_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=3) as resp, open(cache_file, 'wb') as f:
                            f.write(resp.read())
                        GLib.idle_add(self.load_image_file, cache_file)
                    except Exception:
                        GLib.idle_add(self.set_default_art)
                threading.Thread(target=download, daemon=True).start()
        else:
            self.set_default_art()

    def load_image_file(self, path):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 24, 24, True)
            self.img_cover.set_from_pixbuf(pixbuf)
        except Exception:
            self.set_default_art()

    def set_default_art(self):
        self.current_art_url = ""
        self.img_cover.set_from_icon_name("audio-x-generic", Gtk.IconSize.BUTTON)

    def update_media_state(self):
        try:
            status_res = subprocess.run(['playerctl', 'status'], capture_output=True, text=True, timeout=0.25)
            status = status_res.stdout.strip()
            if status not in ('Playing', 'Paused'):
                self.has_playback = False
                if self.is_visible:
                    self.content_box.hide()
                    self.empty_box.show_all()
                return

            self.has_playback = True

            meta_res = subprocess.run([
                'playerctl', 'metadata', '--format',
                '{{playerName}}\t{{status}}\t{{artist}}\t{{title}}\t{{album}}\t{{mpris:artUrl}}'
            ], capture_output=True, text=True, timeout=0.25)

            parts = meta_res.stdout.strip().split('\t')
            player = parts[0] if len(parts) > 0 else 'spotify'
            p_status = parts[1] if len(parts) > 1 else status
            artist = parts[2] if len(parts) > 2 else ''
            title = parts[3] if len(parts) > 3 else ''
            album = parts[4] if len(parts) > 4 else ''
            art_url = parts[5] if len(parts) > 5 else ''

            self.current_player = player.lower()

            if self.is_visible:
                self.empty_box.hide()
                self.content_box.show_all()

            # Metadata info
            self.lbl_title.set_text(title or "Audio")
            self.lbl_artist.set_text(artist or "Desconocido")

            # Cover Art
            self.set_cover_art(art_url)

            # Play/Pause Icon
            if p_status == "Playing":
                self.btn_play.set_label("󰏤")
            else:
                self.btn_play.set_label("󰐊")

        except Exception:
            pass

def main():
    start_hidden = ("--daemon" in sys.argv)
    
    if start_hidden and os.path.exists(SOCK_FILE):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect(SOCK_FILE)
            s.close()
            sys.exit(0)
        except Exception:
            try:
                os.remove(SOCK_FILE)
            except Exception:
                pass

    if os.path.exists(FLAG_FILE):
        try:
            os.remove(FLAG_FILE)
        except Exception:
            pass

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = MediaPopup(start_hidden=start_hidden)
    Gtk.main()

if __name__ == '__main__':
    main()
