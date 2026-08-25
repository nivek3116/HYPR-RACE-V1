#!/usr/bin/env python3

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

# -*- coding: utf-8 -*-

import os
import sys
import glob
import socket
import threading
import subprocess
import signal
import time
import getpass
import shutil

SOCK_FILE = "/tmp/sys_dashboard.sock"

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
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GtkLayerShell

CSS_STYLE = """
@define-color cc-bg rgba(0, 0, 0, 0.50);
@define-color text-main #F8FAFC;
@define-color text-muted #94A3B8;
@define-color accent #FFFFFF;
@define-color danger #EF4444;

* {
    font-family: "Poppins", "JetBrainsMono Nerd Font", "MonaspiceNe Nerd Font", sans-serif;
    color: @text-main;
    transition: 200ms cubic-bezier(0.05, 0.7, 0.1, 1.0);
}

window, scrolledwindow, viewport {
    background-color: transparent;
    background: transparent;
    border: none;
    box-shadow: none;
}

#sys_dashboard_win {
    background-color: transparent;
    border: none;
}

scrollbar, scrollbar slider, scrollbar trough, scrollbar.vertical, scrollbar.horizontal {
    min-width: 0px; min-height: 0px; border: none; background: transparent; opacity: 0;
}

/* Contenedor Transparente Sin Fondo Trasero */
.main-container {
    min-width: 380px;
    background-color: transparent;
    background: transparent;
    border: none;
    padding: 0px;
    margin: 0px;
    box-shadow: none;
}

/* Cápsulas Independientes con color y transparencia de Waybar y Sin Borde */
.section-card {
    background-color: @cc-bg;
    border: none;
    border-radius: 18px;
    padding: 12px 16px;
    margin-bottom: 7px;
    box-shadow: none;
}

.section-card:hover {
    background-color: rgba(0, 0, 0, 0.65);
    border: none;
}

.section-title {
    font-size: 11.5px;
    font-weight: 700;
    color: @text-muted;
    letter-spacing: 0.6px;
}

.section-value-main {
    font-size: 13px;
    font-weight: 700;
    color: @text-main;
}

.section-value-sub {
    font-size: 11.5px;
    font-weight: 600;
    color: @text-muted;
}

.avatar-widget {
    border-radius: 12px;
    margin-right: 12px;
}

/* Barras de progreso flotantes en la base */
progressbar {
    min-height: 7px;
    margin: 7px 0 2px 0;
}

progressbar trough {
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    min-height: 7px;
    border: none;
}

progressbar progress {
    background-color: @accent;
    border-radius: 8px;
    min-height: 7px;
    border: none;
}

/* Filas de procesos */
.proc-row {
    padding: 3.5px 2px;
    border: none;
}

.proc-num {
    font-size: 11px;
    font-weight: 700;
    color: @text-muted;
    min-width: 22px;
}

.proc-name {
    font-size: 11.5px;
    font-weight: 600;
    color: @text-main;
}

.proc-cpu {
    font-size: 11.5px;
    font-weight: 700;
    color: @accent;
    min-width: 52px;
}

.proc-mem {
    font-size: 11.5px;
    color: @text-muted;
    min-width: 56px;
}

/* Botones de acción integrados dentro de la cápsula de procesos */
.action-box {
    margin-top: 8px;
    margin-bottom: 2px;
    border: none;
}

button.action-btn,
.action-btn {
    background-color: rgba(255, 255, 255, 0.08);
    background-image: none;
    border: none;
    border-radius: 12px;
    padding: 7px 0px;
    min-height: 32px;
    outline: none;
    box-shadow: none;
    -gtk-outline-radius: 12px;
}

button.action-btn:focus,
.action-btn:focus {
    background-color: rgba(255, 255, 255, 0.08);
    background-image: none;
    border: none;
    outline: none;
    box-shadow: none;
}

button.action-btn:hover,
.action-btn:hover {
    background-color: rgba(255, 255, 255, 0.16);
    background-image: none;
    border: none;
    box-shadow: none;
}

button.action-btn:active,
button.action-btn:checked,
.action-btn:active,
.action-btn:checked {
    background-color: rgba(255, 255, 255, 0.25);
    background-image: none;
    border: none;
    box-shadow: none;
}
"""

class SystemMonitorDashboard(Gtk.Window):
    def __init__(self, start_hidden=False):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("System Monitor")
        self.set_name("sys_dashboard_win")
        
        # Exact SwayNC Dimensions: 380px width
        self.set_size_request(380, -1)
        
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)
        self.set_app_paintable(True)

        self.last_cpu_total = 0
        self.last_cpu_idle = 0
        self.is_running = True
        self.is_visible = False
        self.show_time = 0
        self.cached_temp_file = self.find_cpu_temp_file()
        self.cached_nvme_temp_file = self.find_nvme_temp_file()
        
        self.init_layer_shell()
        self.apply_styles()
        self.build_ui()
        self.init_events()
        
        self.start_ipc_server()
        self.start_hyprland_event_listener()
        
        self.periodic_update()
        GLib.timeout_add(1500, self.periodic_update)

        # Realize all widgets once
        self.show_all()
        self.refresh_all_metrics()
        if start_hidden:
            self.hide()
        else:
            self.show_dashboard()

    def init_layer_shell(self):
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_namespace(self, "sys_dashboard")
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 18)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 14)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.LEFT, 14)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

    def apply_styles(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS_STYLE.encode("utf-8"))
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def build_ui(self):
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)
        self.add(scrolled)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_box.get_style_context().add_class("main-container")
        scrolled.add(main_box)

        # 1. PROFILE SECTION
        sys_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        sys_box.get_style_context().add_class("section-card")
        
        spider_path = os.path.expanduser("~/.config/waybar/scripts/spiderman_clean_white.png")
        if os.path.exists(spider_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(spider_path, 42, 42, True)
                self.spider_widget = Gtk.Image.new_from_pixbuf(pixbuf)
                self.spider_widget.get_style_context().add_class("avatar-widget")
            except Exception:
                self.spider_widget = Gtk.Label()
                self.spider_widget.set_markup("<span font='18' foreground='#F8FAFC'>🕷</span>")
        else:
            self.spider_widget = Gtk.Label()
            self.spider_widget.set_markup("<span font='18' foreground='#F8FAFC'>🕷</span>")
        
        sys_info_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        sys_info_vbox.set_valign(Gtk.Align.CENTER)
        self.distro_name = self.get_distro_name()
        user = os.environ.get("USER") or os.environ.get("LOGNAME") or getpass.getuser() or "user"
        host = socket.gethostname()
        lbl_host = Gtk.Label(xalign=0)
        lbl_host.set_markup(f"<span font='12.5' weight='bold' foreground='#F8FAFC'>{user}@{host}</span>")
        
        self.lbl_uptime = Gtk.Label(xalign=0)
        self.lbl_uptime.get_style_context().add_class("section-value-sub")
        self.lbl_uptime.set_markup(f"{self.distro_name}  •  󱑂 up 0h 0m")
        
        sys_info_vbox.pack_start(lbl_host, False, False, 0)
        sys_info_vbox.pack_start(self.lbl_uptime, False, False, 0)
        
        sys_box.pack_start(self.spider_widget, False, False, 0)
        sys_box.pack_start(sys_info_vbox, True, True, 0)
        main_box.pack_start(sys_box, False, False, 0)

        # 2. CPU SECTION (Título ➔ Datos ➔ Barra en la base)
        cpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        cpu_box.get_style_context().add_class("section-card")
        
        # Línea 1: Título
        lbl_cpu_title = Gtk.Label(xalign=0)
        lbl_cpu_title.set_markup("  CPU")
        lbl_cpu_title.get_style_context().add_class("section-title")
        
        # Línea 2: Datos (Uso/Temp izq • GHz der)
        cpu_data_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        cpu_data_row.set_margin_top(4)
        
        cpu_left_vals = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_cpu_val = Gtk.Label(xalign=0)
        self.lbl_cpu_val.get_style_context().add_class("section-value-main")
        self.lbl_cpu_val.set_text("0.0%")
        
        self.lbl_cpu_temp = Gtk.Label(xalign=0)
        self.lbl_cpu_temp.get_style_context().add_class("section-value-sub")
        self.lbl_cpu_temp.set_markup("• 0°C")
        
        cpu_left_vals.pack_start(self.lbl_cpu_val, False, False, 0)
        cpu_left_vals.pack_start(self.lbl_cpu_temp, False, False, 0)
        
        self.lbl_cpu_freq = Gtk.Label(xalign=1)
        self.lbl_cpu_freq.get_style_context().add_class("section-value-sub")
        self.lbl_cpu_freq.set_text("0.00 GHz")
        
        cpu_data_row.pack_start(cpu_left_vals, True, True, 0)
        cpu_data_row.pack_end(self.lbl_cpu_freq, False, False, 0)
        
        # Línea 3: Barra limpia en la base
        self.pb_cpu = Gtk.ProgressBar()
        
        cpu_box.pack_start(lbl_cpu_title, False, False, 0)
        cpu_box.pack_start(cpu_data_row, False, False, 0)
        cpu_box.pack_start(self.pb_cpu, False, False, 0)
        main_box.pack_start(cpu_box, False, False, 0)

        # 3. GPU SECTION (Título ➔ Datos ➔ Barra en la base)
        gpu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        gpu_box.get_style_context().add_class("section-card")
        
        # Línea 1: Título
        self.lbl_gpu_title = Gtk.Label(xalign=0)
        self.lbl_gpu_title.set_markup("󰢮  GPU")
        self.lbl_gpu_title.get_style_context().add_class("section-title")
        
        # Línea 2: Datos (Uso/Reloj izq • Máx der)
        gpu_data_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        gpu_data_row.set_margin_top(4)
        
        gpu_left_vals = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_gpu_val = Gtk.Label(xalign=0)
        self.lbl_gpu_val.get_style_context().add_class("section-value-main")
        self.lbl_gpu_val.set_text("0%")
        
        self.lbl_gpu_freq = Gtk.Label(xalign=0)
        self.lbl_gpu_freq.get_style_context().add_class("section-value-sub")
        self.lbl_gpu_freq.set_markup("• 0 MHz")
        
        gpu_left_vals.pack_start(self.lbl_gpu_val, False, False, 0)
        gpu_left_vals.pack_start(self.lbl_gpu_freq, False, False, 0)
        
        self.lbl_gpu_sub = Gtk.Label(xalign=1)
        self.lbl_gpu_sub.get_style_context().add_class("section-value-sub")
        self.lbl_gpu_sub.set_text("0 MHz")
        
        gpu_data_row.pack_start(gpu_left_vals, True, True, 0)
        gpu_data_row.pack_end(self.lbl_gpu_sub, False, False, 0)
        
        # Línea 3: Barra limpia en la base
        self.pb_gpu = Gtk.ProgressBar()
        
        gpu_box.pack_start(self.lbl_gpu_title, False, False, 0)
        gpu_box.pack_start(gpu_data_row, False, False, 0)
        gpu_box.pack_start(self.pb_gpu, False, False, 0)
        main_box.pack_start(gpu_box, False, False, 0)

        # 4. FAN(S) SECTION (Solo RPM, Sin Barra)
        # 4.1. Single Fan Container (Full Width)
        self.fan_single_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.fan_single_box.get_style_context().add_class("section-card")
        
        self.lbl_fan_title = Gtk.Label(xalign=0)
        self.lbl_fan_title.set_markup("󰈐  VENTILADOR")
        self.lbl_fan_title.get_style_context().add_class("section-title")
        
        self.lbl_fan_val = Gtk.Label(xalign=1)
        self.lbl_fan_val.get_style_context().add_class("section-value-main")
        self.lbl_fan_val.set_text("0 RPM")
        
        self.fan_single_box.pack_start(self.lbl_fan_title, True, True, 0)
        self.fan_single_box.pack_end(self.lbl_fan_val, False, False, 0)
        main_box.pack_start(self.fan_single_box, False, False, 0)

        # 4.2. Dual Fan Container (2 Columns 50/50 - Solo RPM)
        self.fan_dual_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.fan_dual_box.get_style_context().add_class("section-card")
        self.fan_dual_box.set_homogeneous(True)
        
        # Fan 1 (CPU Fan)
        f1_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lbl_f1_title = Gtk.Label(xalign=0)
        lbl_f1_title.set_markup("󰈐  VENTILADOR CPU")
        lbl_f1_title.get_style_context().add_class("section-title")
        self.lbl_f1_val = Gtk.Label(xalign=1)
        self.lbl_f1_val.get_style_context().add_class("section-value-main")
        self.lbl_f1_val.set_text("0 RPM")
        f1_box.pack_start(lbl_f1_title, True, True, 0)
        f1_box.pack_end(self.lbl_f1_val, False, False, 0)
        
        # Fan 2 (GPU Fan)
        f2_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lbl_f2_title = Gtk.Label(xalign=0)
        lbl_f2_title.set_markup("󰈐  VENTILADOR GPU")
        lbl_f2_title.get_style_context().add_class("section-title")
        self.lbl_f2_val = Gtk.Label(xalign=1)
        self.lbl_f2_val.get_style_context().add_class("section-value-main")
        self.lbl_f2_val.set_text("0 RPM")
        f2_box.pack_start(lbl_f2_title, True, True, 0)
        f2_box.pack_end(self.lbl_f2_val, False, False, 0)
        
        self.fan_dual_box.pack_start(f1_box, True, True, 0)
        self.fan_dual_box.pack_start(f2_box, True, True, 0)
        main_box.pack_start(self.fan_dual_box, False, False, 0)

        # 5. RAM SECTION (Título ➔ Datos ➔ Barra en la base)
        ram_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        ram_box.get_style_context().add_class("section-card")
        
        # Línea 1: Título
        lbl_ram_title = Gtk.Label(xalign=0)
        lbl_ram_title.set_markup("󰍛  RAM")
        lbl_ram_title.get_style_context().add_class("section-title")
        
        # Línea 2: Datos (GB izq • % der)
        ram_data_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        ram_data_row.set_margin_top(4)
        
        self.lbl_ram_val = Gtk.Label(xalign=0)
        self.lbl_ram_val.get_style_context().add_class("section-value-main")
        self.lbl_ram_val.set_text("0.0 / 0.0 GB")
        
        self.lbl_ram_pct = Gtk.Label(xalign=1)
        self.lbl_ram_pct.get_style_context().add_class("section-value-sub")
        self.lbl_ram_pct.set_text(" (0%)")
        
        ram_data_row.pack_start(self.lbl_ram_val, True, True, 0)
        ram_data_row.pack_end(self.lbl_ram_pct, False, False, 0)
        
        # Línea 3: Barra limpia en la base
        self.pb_ram = Gtk.ProgressBar()
        
        ram_box.pack_start(lbl_ram_title, False, False, 0)
        ram_box.pack_start(ram_data_row, False, False, 0)
        ram_box.pack_start(self.pb_ram, False, False, 0)
        main_box.pack_start(ram_box, False, False, 0)

        # 6. ALMACENAMIENTO SECTION (Título ➔ Datos ➔ Barra en la base)
        disk_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        disk_box.get_style_context().add_class("section-card")
        
        # Línea 1: Título
        lbl_disk_title = Gtk.Label(xalign=0)
        lbl_disk_title.set_markup("󰋊  ALMACENAMIENTO")
        lbl_disk_title.get_style_context().add_class("section-title")
        
        # Línea 2: Datos (GB izq • Temp • % der)
        disk_data_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        disk_data_row.set_margin_top(4)
        
        disk_left_vals = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.lbl_disk_val = Gtk.Label(xalign=0)
        self.lbl_disk_val.get_style_context().add_class("section-value-main")
        self.lbl_disk_val.set_text("0.0 / 0.0 GB")
        
        self.lbl_disk_temp = Gtk.Label(xalign=0)
        self.lbl_disk_temp.get_style_context().add_class("section-value-sub")
        self.lbl_disk_temp.set_markup("• 0°C")
        
        disk_left_vals.pack_start(self.lbl_disk_val, False, False, 0)
        disk_left_vals.pack_start(self.lbl_disk_temp, False, False, 0)
        
        self.lbl_disk_pct = Gtk.Label(xalign=1)
        self.lbl_disk_pct.get_style_context().add_class("section-value-sub")
        self.lbl_disk_pct.set_text(" (0%)")
        
        disk_data_row.pack_start(disk_left_vals, True, True, 0)
        disk_data_row.pack_end(self.lbl_disk_pct, False, False, 0)
        
        # Línea 3: Barra limpia en la base
        self.pb_disk = Gtk.ProgressBar()
        
        disk_box.pack_start(lbl_disk_title, False, False, 0)
        disk_box.pack_start(disk_data_row, False, False, 0)
        disk_box.pack_start(self.pb_disk, False, False, 0)
        main_box.pack_start(disk_box, False, False, 0)



        # 7. PROCESOS & BOTONES DE ACCIÓN (Integrados en una sola cápsula)
        proc_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        proc_box.get_style_context().add_class("section-card")
        
        proc_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lbl_p_title = Gtk.Label(xalign=0)
        lbl_p_title.set_markup("󱒎  PROCESOS")
        lbl_p_title.get_style_context().add_class("section-title")
        
        proc_stat_header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        lbl_p_cpu = Gtk.Label(xalign=1)
        lbl_p_cpu.set_text("CPU")
        lbl_p_cpu.get_style_context().add_class("section-title")
        lbl_p_cpu.set_size_request(58, -1)
        
        lbl_p_mem = Gtk.Label(xalign=1)
        lbl_p_mem.set_text("RAM")
        lbl_p_mem.get_style_context().add_class("section-title")
        lbl_p_mem.set_size_request(62, -1)
        
        proc_stat_header.pack_start(lbl_p_cpu, False, False, 0)
        proc_stat_header.pack_start(lbl_p_mem, False, False, 0)
        
        proc_header.pack_start(lbl_p_title, True, True, 0)
        proc_header.pack_start(proc_stat_header, False, False, 0)
        proc_box.pack_start(proc_header, False, False, 4)
        
        self.proc_rows = []
        for i in range(10):
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            row.get_style_context().add_class("proc-row")
            
            num_lbl = Gtk.Label(xalign=0)
            num_lbl.get_style_context().add_class("proc-num")
            num_lbl.set_text(f"{i+1}.")
            
            name_lbl = Gtk.Label(xalign=0)
            name_lbl.get_style_context().add_class("proc-name")
            name_lbl.set_text("-")
            
            cpu_lbl = Gtk.Label(xalign=1)
            cpu_lbl.get_style_context().add_class("proc-cpu")
            cpu_lbl.set_text("-%")
            
            mem_lbl = Gtk.Label(xalign=1)
            mem_lbl.get_style_context().add_class("proc-mem")
            mem_lbl.set_text("-%")
            
            stats_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
            stats_box.pack_start(cpu_lbl, False, False, 0)
            stats_box.pack_start(mem_lbl, False, False, 0)
            
            row.pack_start(num_lbl, False, False, 0)
            row.pack_start(name_lbl, True, True, 0)
            row.pack_start(stats_box, False, False, 0)
            
            self.proc_rows.append({"name": name_lbl, "cpu": cpu_lbl, "mem": mem_lbl})
            proc_box.pack_start(row, False, False, 0)

        # Botones de Acción integrados dentro de la misma cápsula de procesos
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.get_style_context().add_class("action-box")
        action_box.set_homogeneous(True)
        
        # Botón 1: Liberar Caché de Memoria RAM
        btn_ram = Gtk.Button()
        btn_ram.set_can_focus(False)
        btn_ram.get_style_context().add_class("action-btn")
        btn_ram.set_tooltip_text("Liberar y optimizar memoria caché de RAM")
        lbl_btn_ram = Gtk.Label()
        lbl_btn_ram.set_markup("<span font='14' foreground='#F8FAFC'>󰍛</span>")
        btn_ram.add(lbl_btn_ram)
        btn_ram.connect("clicked", self.on_clean_ram_clicked)
        
        # Botón 2: Limpiar Basura del Sistema y Papelera
        btn_trash = Gtk.Button()
        btn_trash.set_can_focus(False)
        btn_trash.get_style_context().add_class("action-btn")
        btn_trash.set_tooltip_text("Vaciar papelera y archivos temporales del sistema")
        lbl_btn_trash = Gtk.Label()
        lbl_btn_trash.set_markup("<span font='14' foreground='#F8FAFC'>󰩹</span>")
        btn_trash.add(lbl_btn_trash)
        btn_trash.connect("clicked", self.on_clean_trash_clicked)
        
        action_box.pack_start(btn_ram, True, True, 0)
        action_box.pack_start(btn_trash, True, True, 0)
        proc_box.pack_start(action_box, False, False, 0)

        main_box.pack_start(proc_box, False, False, 0)

    def on_clean_ram_clicked(self, widget):
        def worker():
            try:
                subprocess.run("sync", shell=True)
                # Drop caches if polkit/root allows
                subprocess.run("pkexec sh -c 'sync; echo 3 > /proc/sys/vm/drop_caches'", shell=True, capture_output=True)
            except Exception:
                pass
            GLib.idle_add(self.refresh_all_metrics)
            subprocess.run([
                "notify-send", "-a", "Monitor del Sistema",
                "-i", "system-devices-memory",
                "Memoria RAM", "Caché de memoria optimizada y sincronizada."
            ], check=False)
            
        threading.Thread(target=worker, daemon=True).start()

    def on_clean_trash_clicked(self, widget):
        def worker():
            freed_bytes = 0
            # 1. Clean Trash
            trash_path = os.path.expanduser("~/.local/share/Trash")
            for sub in ["files", "info"]:
                p = os.path.join(trash_path, sub)
                if os.path.exists(p):
                    for item in os.listdir(p):
                        ip = os.path.join(p, item)
                        try:
                            if os.path.isfile(ip) or os.path.islink(ip):
                                freed_bytes += os.path.getsize(ip)
                                os.unlink(ip)
                            elif os.path.isdir(ip):
                                for root, dirs, files in os.walk(ip):
                                    for f in files:
                                        fp = os.path.join(root, f)
                                        freed_bytes += os.path.getsize(fp)
                                shutil.rmtree(ip)
                        except Exception:
                            pass
            
            # 2. Clean thumbnails cache
            thumb_path = os.path.expanduser("~/.cache/thumbnails")
            if os.path.exists(thumb_path):
                for root, dirs, files in os.walk(thumb_path):
                    for f in files:
                        fp = os.path.join(root, f)
                        try:
                            freed_bytes += os.path.getsize(fp)
                            os.unlink(fp)
                        except Exception:
                            pass
            
            # 3. Clean user journal
            try:
                subprocess.run("journalctl --user --vacuum-time=1d", shell=True, capture_output=True)
            except Exception:
                pass
            
            freed_mb = freed_bytes / 1024 / 1024
            msg = f"Se liberaron {freed_mb:.1f} MB de archivos temporales y papelera." if freed_mb > 0.1 else "Papelera y temporales del sistema limpios."
            GLib.idle_add(self.refresh_all_metrics)
            subprocess.run([
                "notify-send", "-a", "Monitor del Sistema",
                "-i", "user-trash",
                "Limpieza del Sistema", msg
            ], check=False)
            
        threading.Thread(target=worker, daemon=True).start()

    def init_events(self):
        self.connect("key-press-event", self.on_key_press)
        self.connect("focus-out-event", self.on_focus_out)

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.hide_dashboard()
            return True
        return False

    def on_focus_out(self, widget, event):
        if time.time() - self.show_time < 0.35:
            return False
        if self.is_visible:
            self.hide_dashboard()
        return False

    def start_ipc_server(self):
        def server_loop():
            try:
                if os.path.exists(SOCK_FILE):
                    try:
                        os.remove(SOCK_FILE)
                    except Exception:
                        pass
                server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                server.bind(SOCK_FILE)
                server.listen(5)
                while self.is_running:
                    conn, _ = server.accept()
                    data = conn.recv(128).decode("utf-8").strip().lower()
                    conn.close()
                    if data == "toggle":
                        GLib.idle_add(self.toggle_dashboard)
                    elif data == "show":
                        GLib.idle_add(self.show_dashboard)
                    elif data == "hide":
                        GLib.idle_add(self.hide_dashboard)
                    elif data == "quit":
                        GLib.idle_add(self.quit_app)
            except Exception:
                pass

        t = threading.Thread(target=server_loop, daemon=True)
        t.start()

    def start_hyprland_event_listener(self):
        def hypr_listener():
            his_dir = os.environ.get("XDG_RUNTIME_DIR", "/tmp")
            his_sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE", "")
            if not his_sig:
                return
            socket_path = f"{his_dir}/hypr/{his_sig}/.socket2.sock"
            while self.is_running:
                try:
                    if not os.path.exists(socket_path):
                        time.sleep(1)
                        continue
                    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    s.connect(socket_path)
                    while self.is_running:
                        data = s.recv(1024)
                        if not data:
                            break
                        for line in data.decode('utf-8', errors='ignore').splitlines():
                            if "workspace>>" in line or "activewindow>>" in line:
                                if self.is_visible and time.time() - self.show_time > 0.35:
                                    GLib.idle_add(self.hide_dashboard)
                    s.close()
                except Exception:
                    time.sleep(1)

        t = threading.Thread(target=hypr_listener, daemon=True)
        t.start()

    def toggle_dashboard(self):
        if self.is_visible:
            self.hide_dashboard()
        else:
            self.show_dashboard()

    def show_dashboard(self):
        self.is_visible = True
        self.show_time = time.time()
        self.refresh_all_metrics()
        self.show()
        self.present()

    def hide_dashboard(self):
        self.is_visible = False
        self.hide()

    def quit_app(self):
        self.is_running = False
        try:
            if os.path.exists(SOCK_FILE):
                os.remove(SOCK_FILE)
        except Exception:
            pass
        Gtk.main_quit()

    def get_distro_name(self):
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=', 1)[1].strip().strip('"')
                    elif line.startswith('NAME='):
                        return line.split('=', 1)[1].strip().strip('"')
        except Exception:
            pass
        return "Linux"

    def find_cpu_temp_file(self):
        priority_drivers = ['coretemp', 'k10temp', 'zenpower', 'cpu_thermal', 'thinkpad', 'asus_wmi', 'dell_smm', 'acpitz']
        hwmon_map = {}
        for h in glob.glob('/sys/class/hwmon/hwmon*'):
            try:
                with open(f'{h}/name', 'r') as f:
                    name = f.read().strip()
                    hwmon_map[name] = h
            except Exception:
                pass
        
        for driver in priority_drivers:
            if driver in hwmon_map:
                hdir = hwmon_map[driver]
                for tf in sorted(glob.glob(f'{hdir}/temp*_input')):
                    try:
                        with open(tf, 'r') as f:
                            val = float(f.read().strip())
                            if val > 0:
                                return tf
                    except Exception:
                        pass
        
        for tz in glob.glob('/sys/class/thermal/thermal_zone*/temp'):
            try:
                with open(tz, 'r') as f:
                    val = float(f.read().strip())
                    if val > 0:
                        return tz
            except Exception:
                pass
        return None

    def find_nvme_temp_file(self):
        for h in glob.glob('/sys/class/hwmon/hwmon*'):
            try:
                with open(f'{h}/name', 'r') as f:
                    name = f.read().strip().lower()
                if 'nvme' in name or 'drivetemp' in name:
                    for t in sorted(glob.glob(f'{h}/temp*_input')):
                        try:
                            with open(t, 'r') as tf:
                                val = float(tf.read().strip())
                                if val > 0:
                                    return t
                        except Exception:
                            pass
            except Exception:
                pass
        return None

    def periodic_update(self):
        if self.is_visible:
            self.refresh_all_metrics()
        return True

    def refresh_all_metrics(self):
        # 1. Update Uptime & Distro
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_sec = float(f.readline().split()[0])
                days, rem = divmod(int(uptime_sec), 86400)
                h, m = divmod(rem, 3600)
                m //= 60
                uptime_str = f"{days}d {h}h {m}m" if days > 0 else f"{h}h {m}m"
                distro = getattr(self, 'distro_name', 'Linux')
                self.lbl_uptime.set_markup(f"{distro}  •  󱑂 up {uptime_str}")
        except Exception:
            pass

        # 2. Update CPU Usage
        try:
            with open('/proc/stat', 'r') as f:
                fields = [float(col) for col in f.readline().strip().split()[1:]]
                idle = fields[3] + fields[4]
                total = sum(fields)
                d_idle = idle - self.last_cpu_idle
                d_total = total - self.last_cpu_total
                usage = 100.0 * (1.0 - d_idle / d_total) if d_total > 0 else 0.0
                self.last_cpu_idle = idle
                self.last_cpu_total = total
                self.lbl_cpu_val.set_text(f"{usage:.2f}%")
                self.pb_cpu.set_fraction(max(0.0, min(1.0, usage / 100.0)))
        except Exception:
            pass

        # 3. Update CPU Temp and Freq (Precise Scaling Freq)
        try:
            if not getattr(self, 'cached_temp_file', None) or not os.path.exists(self.cached_temp_file):
                self.cached_temp_file = self.find_cpu_temp_file()
            
            if self.cached_temp_file:
                with open(self.cached_temp_file, 'r') as f:
                    raw_temp = float(f.read().strip())
                    temp = raw_temp / 1000.0 if raw_temp > 200 else raw_temp
                    self.lbl_cpu_temp.set_markup(f"• {temp:.0f}°C")
            
            freq_files = glob.glob('/sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq')
            if freq_files:
                freqs = [float(open(f).read().strip()) / 1000.0 for f in freq_files]
                max_freq = max(freqs)
                freq_str = f"{max_freq/1000.0:.2f} GHz" if max_freq >= 1000 else f"{max_freq:.0f} MHz"
                self.lbl_cpu_freq.set_text(freq_str)
            else:
                with open('/proc/cpuinfo', 'r') as f:
                    freqs = [float(line.split(":")[1]) for line in f if "cpu MHz" in line]
                    if freqs:
                        max_freq = max(freqs)
                        freq_str = f"{max_freq/1000.0:.2f} GHz" if max_freq >= 1000 else f"{max_freq:.0f} MHz"
                        self.lbl_cpu_freq.set_text(freq_str)
        except Exception:
            pass

        # 4. Update GPU (Universal Intel iGPU / AMD / Nvidia Support)
        try:
            gpu_found = False
            # 4.1. Intel GPU
            for card in sorted(glob.glob('/sys/class/drm/card[0-9]')):
                act_f = f"{card}/gt_act_freq_mhz"
                if not os.path.exists(act_f):
                    act_f = f"{card}/gt/gt0/rps_act_freq_mhz"
                max_f = f"{card}/gt_max_freq_mhz"
                if not os.path.exists(max_f):
                    max_f = f"{card}/gt/gt0/rps_max_freq_mhz"
                min_f = f"{card}/gt_min_freq_mhz"
                if not os.path.exists(min_f):
                    min_f = f"{card}/gt/gt0/rps_min_freq_mhz"
                
                if os.path.exists(act_f) and os.path.exists(max_f):
                    try:
                        with open(act_f) as fp:
                            cur = float(fp.read().strip())
                        with open(max_f) as fp:
                            max_val = float(fp.read().strip())
                        min_val = 300.0
                        if os.path.exists(min_f):
                            with open(min_f) as fp:
                                min_val = float(fp.read().strip())
                        
                        if max_val > min_val:
                            pct = max(0.0, min(100.0, ((cur - min_val) / (max_val - min_val)) * 100.0))
                        else:
                            pct = (cur / max_val) * 100.0 if max_val > 0 else 0.0
                        
                        freq_str = f"{cur:.0f} MHz" if cur < 1000 else f"{cur/1000.0:.2f} GHz"
                        max_str = f"{max_val:.0f} MHz" if max_val < 1000 else f"{max_val/1000.0:.2f} GHz"
                        
                        self.lbl_gpu_title.set_markup("󰢮  GPU")
                        self.lbl_gpu_val.set_text(f"{pct:.0f}%")
                        self.lbl_gpu_freq.set_markup(f"• {freq_str}")
                        self.pb_gpu.set_fraction(max(0.0, min(1.0, pct / 100.0)))
                        self.lbl_gpu_sub.set_text(f"Máx {max_str}")
                        gpu_found = True
                        break
                    except Exception:
                        pass
            
            # 4.2. AMD GPU fallback
            if not gpu_found:
                for card in sorted(glob.glob('/sys/class/drm/card[0-9]/device')):
                    busy_file = f"{card}/gpu_busy_percent"
                    if os.path.exists(busy_file):
                        try:
                            with open(busy_file) as fp:
                                pct = float(fp.read().strip())
                            self.lbl_gpu_title.set_markup("󰢮  GPU")
                            self.lbl_gpu_val.set_text(f"{pct:.0f}%")
                            self.lbl_gpu_freq.set_markup("")
                            self.pb_gpu.set_fraction(max(0.0, min(1.0, pct / 100.0)))
                            self.lbl_gpu_sub.set_text("Radeon")
                            gpu_found = True
                            break
                        except Exception:
                            pass
            
            if not gpu_found:
                self.lbl_gpu_title.set_markup("󰢮  GPU")
                self.lbl_gpu_val.set_text("N/D")
                self.lbl_gpu_freq.set_markup("")
                self.pb_gpu.set_fraction(0.0)
                self.lbl_gpu_sub.set_text("Inactivo")
        except Exception:
            pass

        # 5. Update Fan(s) (Adaptive Single Fan or Dual Fan CPU/GPU - Solo RPM)
        try:
            fan_files = sorted(glob.glob("/sys/class/hwmon/hwmon*/fan*_input"))
            rpms = []
            for ff in fan_files:
                try:
                    with open(ff, 'r') as f:
                        r = int(f.read().strip())
                        rpms.append(r)
                except Exception:
                    pass

            if len(rpms) <= 1:
                # Single Fan Mode
                self.fan_dual_box.hide()
                self.fan_single_box.show()
                if rpms:
                    r1 = rpms[0]
                    self.lbl_fan_val.set_text(f"{r1} RPM")
                else:
                    self.lbl_fan_val.set_text("N/D")
            else:
                # Dual Fan Mode (CPU Fan Left + GPU Fan Right)
                self.fan_single_box.hide()
                self.fan_dual_box.show()
                r1 = rpms[0]
                r2 = rpms[1]
                self.lbl_f1_val.set_text(f"{r1} RPM")
                self.lbl_f2_val.set_text(f"{r2} RPM")
        except Exception:
            pass

        # 6. Update RAM (Sin SWAP)
        try:
            with open('/proc/meminfo', 'r') as f:
                mem = {}
                for line in f:
                    parts = line.split()
                    mem[parts[0].strip(':')] = int(parts[1])
            total_gb = mem.get("MemTotal", 0) / 1024 / 1024
            avail_gb = mem.get("MemAvailable", mem.get("MemFree", 0)) / 1024 / 1024
            used_gb = total_gb - avail_gb
            ram_pct = (used_gb / total_gb) * 100 if total_gb > 0 else 0
            self.lbl_ram_val.set_text(f"{used_gb:.1f} / {total_gb:.1f} GB")
            self.lbl_ram_pct.set_text(f" ({ram_pct:.0f}%)")
            self.pb_ram.set_fraction(max(0.0, min(1.0, ram_pct / 100.0)))
        except Exception:
            pass

        # 7. Update Disk & NVMe Temp
        try:
            st = os.statvfs('/')
            total_d = (st.f_blocks * st.f_frsize) / 1024 / 1024 / 1024
            free_d = (st.f_bavail * st.f_frsize) / 1024 / 1024 / 1024
            used_d = total_d - free_d
            disk_pct = (used_d / total_d) * 100 if total_d > 0 else 0
            self.lbl_disk_val.set_text(f"{used_d:.1f} / {total_d:.0f} GB")
            self.lbl_disk_pct.set_text(f" ({disk_pct:.0f}%)")
            self.pb_disk.set_fraction(max(0.0, min(1.0, disk_pct / 100.0)))
            
            if not getattr(self, 'cached_nvme_temp_file', None) or not os.path.exists(self.cached_nvme_temp_file):
                self.cached_nvme_temp_file = self.find_nvme_temp_file()
            
            if self.cached_nvme_temp_file:
                with open(self.cached_nvme_temp_file, 'r') as f:
                    raw_temp = float(f.read().strip())
                    temp = raw_temp / 1000.0 if raw_temp > 200 else raw_temp
                    self.lbl_disk_temp.set_markup(f"• {temp:.0f}°C")
            else:
                self.lbl_disk_temp.set_markup("")
        except Exception:
            pass

        # 8. Update Processes (10 Procesos - Robust Parsing)
        try:
            cmd = "ps -eo comm,pcpu,pmem --sort=-pcpu --no-headers | head -n 10"
            out = subprocess.check_output(cmd, shell=True, text=True).strip().splitlines()
            for i, line in enumerate(out):
                if i >= len(self.proc_rows):
                    break
                parts = line.strip().rsplit(None, 2)
                if len(parts) == 3:
                    cname = parts[0]
                    c_cpu = parts[1]
                    c_mem = parts[2]
                    self.proc_rows[i]["name"].set_text(cname[:14])
                    self.proc_rows[i]["cpu"].set_text(f"{c_cpu}%")
                    self.proc_rows[i]["mem"].set_text(f"{c_mem}%")
        except Exception:
            pass



def main():
    start_hidden = "--daemon" in sys.argv
    app = SystemMonitorDashboard(start_hidden=start_hidden)
    
    def on_sigterm(signum, frame):
        app.quit_app()
        
    signal.signal(signal.SIGINT, on_sigterm)
    signal.signal(signal.SIGTERM, on_sigterm)
    
    Gtk.main()

if __name__ == "__main__":
    main()
