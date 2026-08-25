-- ========================================================== --
--                                                            --
--                      HYPER - RICE                          --
--                                                            --
-- ========================================================== --


-- ========================================================== --
-- MONITORES                                                  --
-- ========================================================== --
hl.monitor({
    output   = "eDP-1",
    mode     = "1920x1080@60",
    position = "0x0",
    scale    = 1,
})


-- ========================================================== --
-- PROGRAMAS PREDETERMINADOS                                  --
-- ========================================================== --
local terminal    = "kitty"
local fileManager = "thunar"
local menu        = "rofi"
local browser     = "firefox"


-- ========================================================== --
-- AUTOSTART                                                  --
-- ========================================================== --
hl.on("hyprland.start", function()
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")
    hl.exec_cmd("waybar > /dev/null 2>&1")
    hl.exec_cmd("pidof swaync >/dev/null || swaync")
    hl.exec_cmd("python3 ~/.config/waybar/scripts/quick_menu.py --daemon")
    hl.exec_cmd("mkdir -p ~/.cache/awww")
    hl.exec_cmd("selector-fondos --restore")
    hl.exec_cmd("pidof hypridle >/dev/null || hypridle")
    hl.exec_cmd("pidof polkit-gnome-authentication-agent-1 >/dev/null || /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 || /usr/lib/polkit-kde-authentication-agent-1")
    hl.exec_cmd("/usr/bin/gnome-keyring-daemon --start --components=secrets")
    hl.exec_cmd("wl-paste --type text --watch cliphist store")
    hl.exec_cmd("wl-paste --type image --watch cliphist store")
    hl.exec_cmd("pidof udiskie >/dev/null || udiskie --no-tray")
    hl.exec_cmd("pidof swayosd-server >/dev/null || swayosd-server")
    hl.exec_cmd("pidof hyprsunset >/dev/null || hyprsunset --temperature 7000")
    hl.exec_cmd("python3 ~/.local/bin/mpvpaper-autopause.py")
    hl.exec_cmd("systemctl --user start hypr-battery-alert.service hypr-usb-sound.service")
end)


-- ========================================================== --
-- VARIABLES DE ENTORNO                                       --
-- ========================================================== --
hl.env("PATH", (os.getenv("HOME") or "/home/nivek") .. "/.local/bin:" .. (os.getenv("PATH") or "/usr/local/bin:/usr/bin:/bin"))
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XDG_SESSION_TYPE", "wayland")
hl.env("XDG_SESSION_DESKTOP", "Hyprland")
hl.env("GDK_BACKEND", "wayland,x11,*")
hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")
hl.env("QT_WAYLAND_DISABLE_WINDOWDECORATION", "1")
hl.env("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
hl.env("CLUTTER_BACKEND", "wayland")
hl.env("SDL_VIDEODRIVER", "wayland")
hl.env("MOZ_ENABLE_WAYLAND", "1")
hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")
hl.env("LIBVA_DRIVER_NAME", "iHD")


-- ========================================================== --
-- APARIENCIA Y DISEÑO                                        --
-- ========================================================== --
hl.config({
    general = {
        gaps_in          = 5,
        gaps_out         = 15,
        border_size      = 0,
        col = {
            active_border   = "rgba(ef473a20)",
            inactive_border = "rgba(f8503210)",
        },
        resize_on_border = false,
        allow_tearing    = false,
        layout           = "dwindle",
    },

    decoration = {
        rounding         = 7,
        rounding_power   = 2,
        active_opacity   = 1,
        inactive_opacity = 1,

        shadow = {
            enabled      = false,
            range        = 4,
            render_power = 3,
            color        = "0x1a1a1aee",
        },

        blur = {
            enabled           = true,
            size              = 5,
            passes            = 2,
            vibrancy          = 0.1696,
            new_optimizations = true,
            ignore_opacity    = true,
            popups            = true,
        },
    },

    animations = {
        enabled = true,
    },
})


-- ========================================================== --
-- ANIMACIONES Y CURVAS                                       --
-- ========================================================== --
hl.curve("easeOutQuint",   { type = "bezier", points = { { 0.23, 1.00 }, { 0.32, 1.00 } } })
hl.curve("easeInOutCubic", { type = "bezier", points = { { 0.65, 0.05 }, { 0.36, 1.00 } } })
hl.curve("linear",         { type = "bezier", points = { { 0.00, 0.00 }, { 1.00, 1.00 } } })
hl.curve("almostLinear",   { type = "bezier", points = { { 0.50, 0.50 }, { 0.75, 1.00 } } })
hl.curve("quick",          { type = "bezier", points = { { 0.15, 0.00 }, { 0.10, 1.00 } } })
hl.curve("spring",         { type = "bezier", points = { { 0.05, 0.90 }, { 0.10, 1.05 } } })
hl.curve("fastOut",        { type = "bezier", points = { { 0.30, 0.00 }, { 0.80, 0.15 } } })

hl.animation({ leaf = "global",        enabled = true, speed = 2.0, bezier = "default" })
hl.animation({ leaf = "border",        enabled = true, speed = 1.8, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows",       enabled = true, speed = 1.8, bezier = "spring" })
hl.animation({ leaf = "windowsIn",     enabled = true, speed = 1.8, bezier = "spring",        style = "popin 88%" })
hl.animation({ leaf = "windowsOut",    enabled = true, speed = 1.3, bezier = "fastOut",       style = "popin 92%" })
hl.animation({ leaf = "fadeIn",        enabled = true, speed = 1.5, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut",       enabled = true, speed = 1.2, bezier = "almostLinear" })
hl.animation({ leaf = "fade",          enabled = true, speed = 1.4, bezier = "quick" })
hl.animation({ leaf = "layers",        enabled = true, speed = 1.8, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersIn",      enabled = true, speed = 1.8, bezier = "easeOutQuint" })
hl.animation({ leaf = "layersOut",     enabled = true, speed = 1.3, bezier = "fastOut" })
hl.animation({ leaf = "fadeLayersIn",  enabled = true, speed = 1.8, bezier = "easeOutQuint" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.3, bezier = "fastOut" })
hl.animation({ leaf = "workspaces",    enabled = true, speed = 1.8, bezier = "easeOutQuint",  style = "slidefade 20%" })
hl.animation({ leaf = "workspacesIn",  enabled = true, speed = 1.8, bezier = "easeOutQuint",  style = "slidefade 20%" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 1.8, bezier = "easeOutQuint",  style = "slidefade 20%" })
hl.animation({ leaf = "zoomFactor",    enabled = true, speed = 2.0, bezier = "quick" })


-- ========================================================== --
-- LAYOUTS Y COMPORTAMIENTO                                   --
-- ========================================================== --
hl.config({
    dwindle = { preserve_split = true },
    master = { new_status = "master" },
    misc = { force_default_wallpaper = 0, disable_hyprland_logo = true },
})


-- ========================================================== --
-- ENTRADA (TECLADO Y RATÓN)                                  --
-- ========================================================== --
hl.config({
    input = {
        kb_layout = "us", kb_variant = "intl", kb_model = "", kb_options = "", 
        kb_rules = "", follow_mouse = 1, sensitivity = 0, touchpad = { natural_scroll = false },
    },
})
hl.gesture({ fingers = 3, direction = "horizontal", action = "workspace" })
hl.device({ name = "epic-mouse-v1", sensitivity = -0.5 })


-- ========================================================== --
-- ATAJOS DE TECLADO                                          --
-- ========================================================== --
local mainMod = "SUPER"

-- APLICACIONES Y SISTEMA --
hl.bind(mainMod .. " + T",         hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + code:36",   hl.dsp.exec_cmd("kitty"))
hl.bind(mainMod .. " + C",         hl.dsp.window.close())
hl.bind(mainMod .. " + L",         hl.dsp.exec_cmd("hyprlock"))
hl.bind(mainMod .. " + E",         hl.dsp.exec_cmd(fileManager))
hl.bind(mainMod .. " + V",         hl.dsp.exec_cmd("~/.config/hypr/scripts/clipboard.sh copy"))
hl.bind(mainMod .. " + SHIFT + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + ALT + V",   hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + D",         hl.dsp.exec_cmd("pkill rofi || rofi -show drun"))
hl.bind(mainMod .. " + P",         hl.dsp.window.pseudo())
hl.bind(mainMod .. " + B",         hl.dsp.exec_cmd(browser))
hl.bind(mainMod .. " + S",         hl.dsp.exec_cmd("spotify-launcher"))
hl.bind(mainMod .. " + W",           hl.dsp.exec_cmd("~/.local/bin/selector-fondos"))
hl.bind(mainMod .. " + CTRL + W",  hl.dsp.exec_cmd("~/.local/bin/selector-fondos --random"))
hl.bind(mainMod .. " + SHIFT + W",   hl.dsp.exec_cmd("~/.local/bin/selector-fondos --animated"))
hl.bind(mainMod .. " + ALT + W",     hl.dsp.exec_cmd("~/.local/bin/selector-fondos --static"))
hl.bind(mainMod .. " + Escape",    hl.dsp.exec_cmd("~/.config/waybar/scripts/power.sh"))
hl.bind(mainMod .. " + N",         hl.dsp.exec_cmd("swaync-client -t -sw"))
hl.bind(mainMod .. " + SHIFT + N", hl.dsp.exec_cmd("swaync-client -d -sw"))
hl.bind(mainMod .. " + SHIFT + B", hl.dsp.exec_cmd("~/.config/hypr/scripts/btop-toggle.sh"))

-- UTILIDADES DE ESCRITORIO --
hl.bind(mainMod .. " + O",         hl.dsp.exec_cmd("~/.config/hypr/scripts/idle-toggle.sh"))
hl.bind(mainMod .. " + ALT + N",   hl.dsp.exec_cmd("~/.config/hypr/scripts/nightlight.sh"))
hl.bind(mainMod .. " + ALT + P",   hl.dsp.exec_cmd("nwg-displays"))
hl.bind(mainMod .. " + ALT + A",   hl.dsp.exec_cmd("nwg-look"))

-- CAPTURAS Y GRABACIÓN --
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh area"))
hl.bind("Print",                   hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh full"))
hl.bind(mainMod .. " + Print",     hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh area"))
hl.bind(mainMod .. " + SHIFT + R", hl.dsp.exec_cmd("~/.config/hypr/scripts/screen-record.sh"))

-- CONTROL MULTIMEDIA --
hl.bind(mainMod .. " + space",     hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind(mainMod .. " + comma",     hl.dsp.exec_cmd("playerctl previous"),   { locked = true })
hl.bind(mainMod .. " + period",    hl.dsp.exec_cmd("playerctl next"),       { locked = true })

-- NAVEGACIÓN Y FOCO --
hl.bind(mainMod .. " + left",      hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right",     hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",        hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",      hl.dsp.focus({ direction = "down" }))

-- WORKSPACES --
for i = 1, 10 do
    local key = i % 10
    hl.bind(mainMod .. " + " .. key,         hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- CONTROL DE VENTANAS --
hl.bind(mainMod .. " + M", hl.dsp.window.fullscreen("maximized", "toggle"))
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen("fullscreen", "toggle"))
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- TECLAS ESPECIALES Y HARDWARE --
hl.bind("XF86AudioRaiseVolume",  hl.dsp.exec_cmd("~/.config/hypr/scripts/volume-brightness.sh vol-up"),     { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume",  hl.dsp.exec_cmd("~/.config/hypr/scripts/volume-brightness.sh vol-down"),   { locked = true, repeating = true })
hl.bind("XF86AudioMute",         hl.dsp.exec_cmd("~/.config/hypr/scripts/volume-brightness.sh vol-mute"),   { locked = true, repeating = true })
hl.bind("XF86AudioMicMute",      hl.dsp.exec_cmd("~/.config/hypr/scripts/volume-brightness.sh mic-mute"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("~/.config/hypr/scripts/volume-brightness.sh bright-up"),  { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("~/.config/hypr/scripts/volume-brightness.sh bright-down"),{ locked = true, repeating = true })
hl.bind("Caps_Lock",             hl.dsp.exec_cmd("~/.config/hypr/scripts/volume-brightness.sh caps"),       { locked = true })
hl.bind("XF86AudioNext",         hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPause",        hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPlay",         hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioPrev",         hl.dsp.exec_cmd("playerctl previous"),   { locked = true })
hl.bind("switch:on:Lid Switch",  hl.dsp.exec_cmd("pidof hyprlock || hyprlock"), { locked = true })
hl.bind("switch:off:Lid Switch", hl.dsp.exec_cmd("hyprctl dispatch dpms on"),  { locked = true })


-- ========================================================== --
-- REGLAS DE VENTANAS Y CAPAS                                 --
-- ========================================================== --

-- REGLAS BÁSICAS --
hl.window_rule({ 
    name = "suppress-maximize-events", 
    match = { class = ".*" }, 
    suppress_event = "maximize" 
})

hl.window_rule({ 
    name = "fix-xwayland-drags", 
    match = { 
        class = "^$", 
        title = "^$", 
        xwayland = true, 
        float = true, 
        fullscreen = false, 
        pin = false 
    }, 
    no_focus = true 
})

hl.window_rule({ 
    name = "move-hyprland-run", 
    match = { class = "hyprland-run" }, 
    move = "20 monitor_h-120", 
    float = true 
})

hl.window_rule({ 
    name = "player-popup-float", 
    match = { class = ".*player-popup.*" }, 
    float = true, 
    move = "12 54", 
    pin = true 
})

hl.window_rule({ 
    name = "notifications-popup-float", 
    match = { class = ".*notifications-popup.*" }, 
    float = true, 
    move = "1520 54", 
    pin = true 
})

hl.window_rule({ 
    name = "polkit-float", 
    match = { class = ".*polkit.*|.*Polkit.*" }, 
    float = true, 
    pin = true 
})


-- VENTANAS FLOTANTES --
hl.window_rule({ 
    name = "swappy-float", 
    match = { class = "swappy" }, 
    float = true 
})

hl.window_rule({ 
    name = "nwg-displays-float", 
    match = { class = "nwg-displays" }, 
    float = true 
})

hl.window_rule({ 
    name = "nwg-look-float", 
    match = { class = "nwg-look" }, 
    float = true 
})

hl.window_rule({ 
    name = "nm-connection-editor-float", 
    match = { class = "nm-connection-editor" }, 
    float = true 
})

hl.window_rule({ 
    name = "pavucontrol-float", 
    match = { class = "pavucontrol" }, 
    float = true 
})

hl.window_rule({ 
    name = "blueman-manager-float", 
    match = { class = "blueman-manager" }, 
    float = true 
})

hl.window_rule({ 
    name = "btop-float", 
    match = { class = "btop_float" }, 
    float = true, 
    size = "950 600", 
    center = true 
})


-- OPACIDAD --
hl.window_rule({ 
    name = "code-opacity", 
    match = { class = ".*[Cc]ode.*|.*code-oss.*|.*visual-studio-code-electron.*" }, 
    opacity = "0.85 0.85 1.0" 
})

hl.window_rule({ 
    name = "discord-opacity", 
    match = { class = ".*[Dd]iscord.*|.*[Vv]esktop.*|.*[Ww]eb[Cc]ord.*" }, 
    opacity = "0.85 0.85 1.0" 
})

hl.window_rule({ 
    name = "spotify-opacity", 
    match = { class = ".*[Ss]potify.*" }, 
    opacity = "0.85 0.85 1.0" 
})


-- BLUR EN CAPAS --
hl.layer_rule({ 
    match = { namespace = ".*notifications.*|.*swaync.*" }, 
    blur = true, 
    ignore_alpha = 0.05 
})

hl.layer_rule({ 
    match = { namespace = ".*swayosd.*" }, 
    blur = true, 
    ignore_alpha = 0.05 
})

hl.layer_rule({ 
    match = { namespace = ".*eww.*|.*dynamic_island.*" }, 
    blur = true, 
    ignore_alpha = 0.05 
})

hl.layer_rule({ 
    match = { namespace = ".*kitty.*" }, 
    blur = true, 
    ignore_alpha = 0.25 
})

hl.layer_rule({ 
    match = { namespace = ".*rofi.*|rofi" }, 
    blur = true, 
    ignore_alpha = 0.1, 
    animation = "slide bottom" 
})

hl.layer_rule({ 
    match = { namespace = ".*quick_menu.*" }, 
    blur = true, 
    ignore_alpha = 0.1, 
    animation = "slide top" 
})

hl.layer_rule({ 
    match = { namespace = ".*swaync-control-center.*|.*swaync-notification-window.*" }, 
    blur = true, 
    ignore_alpha = 0.1, 
    animation = "slide right" 
})

hl.layer_rule({ 
    match = { namespace = "waybar" }, 
    blur = true, 
    ignore_alpha = 0.1 
})
hl.layer_rule({ match = { namespace = ".*sys_dashboard.*" }, blur = true, ignore_alpha = 0.1, animation = "slide left" })
