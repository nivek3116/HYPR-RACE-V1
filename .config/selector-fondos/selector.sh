#!/usr/bin/env bash

# ==============================================================================
# Selector de Fondos Inteligente y Minimalista para Hyprland
# Ubicación de fondos: ~/fondos/
# Características:
#  • Auto-detección de contexto: abre en 'Estáticos' o 'Animados' según el fondo activo.
#  • Alternador de pestañas/categorías en caliente con Tab o teclas Up/Down.
#  • Listas limpias e independientes (las fotos no se mezclan con los videos).
#  • Miniaturas automáticas con insignia '▶' para videos/GIFs.
#  • Transiciones suaves sin pantallas negras (awww <-> mpvpaper).
#  • Auto-pausa inteligente de mpvpaper en pantalla completa (-p -a FULL).
#  • Notificaciones discretas con vista previa (SwayNC / notify-send).
#  • Modo aleatorio instantáneo (--random).
#  • Envío a la papelera con Shift+Delete directamente desde el dock.
# ==============================================================================

export PATH="${HOME}/.local/bin:${PATH}"
WALLPAPER_DIR="${HOME}/fondos"
SCRIPT_SOURCE="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
THEME_FILE="${SCRIPT_DIR}/style.rasi"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/selector-fondos"

mkdir -p "$CACHE_DIR"

# Generar miniatura optimizada y frame limpio para extracción de color
generate_thumbnail() {
    local img="$1"
    local thumb="$2"
    local filename="${img##*/}"
    local ext="${filename##*.}"
    ext="${ext,,}"
    local color_frame="${CACHE_DIR}/${filename}.color.png"

    case "$ext" in
        mp4|webm|mkv)
            ffmpeg -y -ss 00:00:02 -i "$img" -vframes 1 -update 1 -vf "scale=480:270:force_original_aspect_ratio=increase,crop=480:270" "$color_frame" 2>/dev/null || \
            ffmpeg -y -ss 00:00:00 -i "$img" -vframes 1 -update 1 -vf "scale=480:270:force_original_aspect_ratio=increase,crop=480:270" "$color_frame" 2>/dev/null

            if [ -f "$color_frame" ]; then
                magick "$color_frame" -thumbnail 240x135^ -gravity center -extent 240x135 \
                    \( -size 240x135 xc:transparent \
                       -fill "rgba(10,10,15,0.75)" -stroke "rgba(255,255,255,0.3)" -strokewidth 1 \
                       -draw "roundrectangle 192,98 230,126 5,5" \
                       -fill "#FFFFFF" -stroke none \
                       -draw "polygon 208,105 208,119 219,112" \) \
                    -composite "$thumb" 2>/dev/null
            fi
            ;;
        gif)
            magick "${img}[0]" -thumbnail 480x270^ -gravity center -extent 480x270 "$color_frame" 2>/dev/null
            magick "$color_frame" -thumbnail 240x135^ -gravity center -extent 240x135 \
                \( -size 240x135 xc:transparent \
                   -fill "rgba(10,10,15,0.75)" -stroke "rgba(255,255,255,0.3)" -strokewidth 1 \
                   -draw "roundrectangle 192,98 230,126 5,5" \
                   -fill "#FFFFFF" -stroke none \
                   -draw "polygon 208,105 208,119 219,112" \) \
                    -composite "$thumb" 2>/dev/null
            ;;
        *)
            magick "$img" -thumbnail 480x270^ -gravity center -extent 480x270 "$color_frame" 2>/dev/null
            magick "$color_frame" -thumbnail 240x135^ -gravity center -extent 240x135 "$thumb" 2>/dev/null
            ;;
    esac
}

# Escaneo ultrarrápido y construcción de listas para ambos modos en una sola pasada
build_all_sessions() {
    local static=()
    local anim=()

    # 1. Fondos preferentes 1..7
    for i in {1..7}; do
        for f in "$WALLPAPER_DIR"/$i.*; do
            [ -f "$f" ] || continue
            local ext="${f##*.}"
            ext="${ext,,}"
            case "$ext" in
                mp4|webm|mkv|gif) anim+=("$f") ;;
                png|jpg|jpeg|webp) static+=("$f") ;;
            esac
            break
        done
    done

    # 2. Resto de archivos
    for f in "$WALLPAPER_DIR"/*; do
        [ -f "$f" ] || continue
        local fname="${f##*/}"
        [[ "$fname" =~ ^[1-7]\. ]] && continue
        local ext="${fname##*.}"
        ext="${ext,,}"
        case "$ext" in
            mp4|webm|mkv|gif) anim+=("$f") ;;
            png|jpg|jpeg|webp) static+=("$f") ;;
        esac
    done

    # Obtener fondos activos / últimos seleccionados
    local curr_wall=""
    [ -f "${CACHE_DIR}/current_wall" ] && curr_wall=$(<"${CACHE_DIR}/current_wall")
    local last_static=""
    [ -f "${CACHE_DIR}/last_static" ] && last_static=$(<"${CACHE_DIR}/last_static")
    local last_anim=""
    [ -f "${CACHE_DIR}/last_animated" ] && last_anim=$(<"${CACHE_DIR}/last_animated")

    local curr_static="$curr_wall"
    if [[ "$curr_wall" =~ \.(mp4|webm|mkv|gif)$ ]]; then
        curr_static="$last_static"
    fi
    [ -z "$curr_static" ] && [ -n "$last_static" ] && curr_static="$last_static"

    local curr_anim="$curr_wall"
    if [[ ! "$curr_wall" =~ \.(mp4|webm|mkv|gif)$ ]]; then
        curr_anim="$last_anim"
    fi
    [ -z "$curr_anim" ] && [ -n "$last_anim" ] && curr_anim="$last_anim"

    _build_single_mode "static" "$curr_static" "${static[@]}"
    _build_single_mode "animated" "$curr_anim" "${anim[@]}"
}

_build_single_mode() {
    local target_mode="$1"
    local current="$2"
    shift 2
    local wallpapers=("$@")
    local total=${#wallpapers[@]}
    local session_file="${CACHE_DIR}/session_list_${target_mode}.txt"
    local order_file="${CACHE_DIR}/session_order_${target_mode}.txt"

    if [ "$total" -eq 0 ]; then
        rm -f "$session_file" "$order_file"
        return
    fi

    local ordered=()
    local mid_pos=$((total / 2))

    local found=0
    if [ -n "$current" ]; then
        for img in "${wallpapers[@]}"; do
            if [ "$img" = "$current" ]; then
                found=1
                break
            fi
        done
    fi

    if [ "$found" -eq 1 ]; then
        local others=()
        for img in "${wallpapers[@]}"; do
            [ "$img" != "$current" ] && others+=("$img")
        done

        for ((i=0; i<mid_pos; i++)); do
            ordered+=("${others[i]}")
        done
        ordered+=("$current")
        for ((i=mid_pos; i<${#others[@]}; i++)); do
            ordered+=("${others[i]}")
        done
    else
        ordered=("${wallpapers[@]}")
    fi

    local order_out=""
    local session_out=""
    for img in "${ordered[@]}"; do
        order_out+="${img}\n"
        local filename="${img##*/}"
        local thumb="${CACHE_DIR}/${filename}.png"

        if [ ! -f "$thumb" ] || [ "$img" -nt "$thumb" ]; then
            generate_thumbnail "$img" "$thumb"
        fi

        session_out+="${img}\0icon\x1f${thumb}\n"
    done

    printf "%b" "$order_out" > "$order_file"
    printf "%b" "$session_out" > "$session_file"
}

build_session_wallpapers() {
    build_all_sessions
}

# Aplicar fondo de pantalla con transición suave e instantánea
apply_wallpaper() {
    local target="$1"
    local is_restore="${2:-0}"
    [ -z "$target" ] || [ ! -f "$target" ] && return 1

    local sel_filename="${target##*/}"
    local sel_ext="${sel_filename##*.}"
    sel_ext="${sel_ext,,}"
    local thumb="${CACHE_DIR}/${sel_filename}.png"

    if [ ! -f "$thumb" ] || [ "$target" -nt "$thumb" ]; then
        generate_thumbnail "$target" "$thumb"
    fi

    echo "$target" > "${CACHE_DIR}/current_wall"

    case "$sel_ext" in
        mp4|webm|mkv|gif)
            echo "$target" > "${CACHE_DIR}/last_animated"
            pkill -x mpvpaper 2>/dev/null
            sleep 0.02
            nohup mpvpaper -p -a FULL -o "no-audio --loop-playlist --hwdec=auto --scale=bilinear --panscan=1.0" "*" "$target" > /dev/null 2>&1 &
            ;;
        *)
            echo "$target" > "${CACHE_DIR}/last_static"
            if ! pgrep -x awww-daemon > /dev/null 2>&1; then
                nohup awww-daemon > /dev/null 2>&1 &
                sleep 0.1
            fi

            if [ "$is_restore" -eq 1 ]; then
                awww img "$target" --transition-step 255 > /dev/null 2>&1 &
            else
                awww img "$target" \
                    --transition-type wipe \
                    --transition-angle 45 \
                    --transition-duration 0.8 \
                    --transition-step 90 \
                    --transition-fps 60 \
                    --transition-bezier .25,1,.5,1 > /dev/null 2>&1 &
            fi

            # Matar mpvpaper de inmediato para eliminar parpadeos de frames residuales
            pkill -x mpvpaper 2>/dev/null
            ;;
    esac
}

# --- Modo Restaurar en Inicio (--restore / -r) ---
if [ "$1" = "--restore" ] || [ "$1" = "-r" ]; then
    wall_to_restore=""
    if [ -f "${CACHE_DIR}/current_wall" ]; then
        wall_to_restore="$(<"${CACHE_DIR}/current_wall")"
    fi

    if [ -z "$wall_to_restore" ] || [ ! -f "$wall_to_restore" ]; then
        for f in "$WALLPAPER_DIR"/*; do
            [ -f "$f" ] && { wall_to_restore="$f"; break; }
        done
    fi

    if [ -n "$wall_to_restore" ] && [ -f "$wall_to_restore" ]; then
        apply_wallpaper "$wall_to_restore" 1
    fi
    exit 0
fi

# --- Modo Aleatorio (--random / -rnd) ---
if [ "$1" = "--random" ] || [ "$1" = "-rnd" ]; then
    all_files=()
    for f in "$WALLPAPER_DIR"/*; do
        [ -f "$f" ] && all_files+=("$f")
    done

    if [ ${#all_files[@]} -gt 0 ]; then
        rand_idx=$(( RANDOM % ${#all_files[@]} ))
        rand_wall="${all_files[$rand_idx]}"
        apply_wallpaper "$rand_wall" 0
    fi
    exit 0
fi

# --- Callbacks de Rofi Script para modos independientes ---
if [ "$1" = "--mode-static" ] || [ "$1" = "--mode-animated" ]; then
    SUB_MODE="static"
    [ "$1" = "--mode-animated" ] && SUB_MODE="animated"
    
    SESSION_FILE="${CACHE_DIR}/session_list_${SUB_MODE}.txt"
    ORDER_FILE="${CACHE_DIR}/session_order_${SUB_MODE}.txt"

    # Acción de eliminar/papelera (Shift+Delete o Alt+BackSpace -> RETV 10 o 3)
    if [ -n "$ROFI_RETV" ] && { [ "$ROFI_RETV" -eq 10 ] || [ "$ROFI_RETV" -eq 3 ]; } && [ -n "$2" ] && [ -f "$2" ]; then
        filename_del="${2##*/}"
        gio trash "$2" 2>/dev/null || rm -f "$2"
        rm -f "${CACHE_DIR}/${filename_del}.png"
        notify-send -a "Fondo de Pantalla" "🗑️ Fondo Eliminado" "$filename_del movido a la papelera" -u low -t 2000 2>/dev/null &
        build_all_sessions
        printf "\0keep-selection\x1ftrue\n"
        if [ -f "$SESSION_FILE" ]; then
            cat "$SESSION_FILE"
        fi
        exit 0
    fi

    # Asegurar lista de sesión
    if [ ! -f "$SESSION_FILE" ] || [ ! -f "$ORDER_FILE" ]; then
        build_all_sessions
    fi

    # Selección y aplicación de fondo (RETV=1)
    if [ -n "$2" ] && [ -f "$2" ]; then
        apply_wallpaper "$2" 0

        SELECTED_INDEX=0
        if [ -f "$ORDER_FILE" ]; then
            grep_idx=$(grep -nxF "$2" "$ORDER_FILE" | cut -d: -f1)
            if [ -n "$grep_idx" ]; then
                SELECTED_INDEX=$((grep_idx - 1))
            fi
        fi

        printf "\0keep-selection\x1ftrue\n"
        printf "\0new-selection\x1f%d\n" "$SELECTED_INDEX"
    else
        # Al abrir o cambiar de modo, enfocar en el centro
        if [ -f "$ORDER_FILE" ]; then
            cnt=$(wc -l < "$ORDER_FILE")
            mid=$((cnt / 2))
            printf "\0new-selection\x1f%d\n" "$mid"
        fi
        printf "\0keep-selection\x1ftrue\n"
    fi

    if [ -f "$SESSION_FILE" ]; then
        cat "$SESSION_FILE"
    fi
    exit 0
fi

# --- Invocación Principal (Lanzador) ---

# 1. Si ya hay una instancia abierta de rofi, cerrarla (toggle)
if pgrep -x rofi > /dev/null 2>&1; then
    pkill -x rofi
    exit 0
fi

# 2. Verificar que el escritorio actual no tenga ventanas abiertas
ACTIVE_WINDOWS=$(hyprctl activeworkspace -j 2>/dev/null | grep -oP '"windows":\s*\K[0-9]+')
if [ -n "$ACTIVE_WINDOWS" ] && [ "$ACTIVE_WINDOWS" -gt 0 ]; then
    exit 0
fi

# 3. Detectar qué modo inicial mostrar (contexto actual)
INITIAL_MODE="estaticos"

if [ "$1" = "--animated" ] || [ "$1" = "-a" ] || [ "$1" = "--live" ]; then
    INITIAL_MODE="animados"
elif [ "$1" = "--static" ] || [ "$1" = "-s" ]; then
    INITIAL_MODE="estaticos"
else
    if pgrep -x mpvpaper >/dev/null 2>&1; then
        INITIAL_MODE="animados"
    elif [ -f "${CACHE_DIR}/current_wall" ]; then
        curr_file=$(<"${CACHE_DIR}/current_wall")
        curr_ext="${curr_file##*.}"
        curr_ext="${curr_ext,,}"
        if [[ "$curr_ext" =~ ^(mp4|webm|mkv|gif)$ ]]; then
            INITIAL_MODE="animados"
        fi
    fi
fi

# 4. Construir listas frescas para ambos modos
build_all_sessions

COUNT_STATIC=0
COUNT_ANIM=0
[ -f "${CACHE_DIR}/session_order_static.txt" ] && COUNT_STATIC=$(wc -l < "${CACHE_DIR}/session_order_static.txt")
[ -f "${CACHE_DIR}/session_order_animated.txt" ] && COUNT_ANIM=$(wc -l < "${CACHE_DIR}/session_order_animated.txt")

# Calcular cantidad máxima para ajustar ancho del dock
MAX_ITEMS=$COUNT_STATIC
[ "$COUNT_ANIM" -gt "$MAX_ITEMS" ] && MAX_ITEMS=$COUNT_ANIM
[ "$MAX_ITEMS" -gt 7 ] && MAX_ITEMS=7
[ "$MAX_ITEMS" -lt 1 ] && MAX_ITEMS=1

WIDTH=$(( MAX_ITEMS * 262 + 80 ))
[ "$WIDTH" -gt 1914 ] && WIDTH=1914

# 5. Monitor de eventos de Hyprland para auto-cerrar si se abren ventanas
python3 -c '
import os, socket, subprocess, sys, json
sig = os.environ.get("HYPRLAND_INSTANCE_SIGNATURE", "")
sock_path = f"/run/user/{os.getuid()}/hypr/{sig}/.socket2.sock"
try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(sock_path)
    buf = ""
    while True:
        data = s.recv(1024)
        if not data:
            break
        buf += data.decode("utf-8", errors="ignore")
        while "\n" in buf:
            event, buf = buf.split("\n", 1)
            if event.startswith(("workspace>>", "focusedmon>>", "openwindow>>")):
                out = subprocess.check_output(["hyprctl", "activeworkspace", "-j"], text=True)
                ws = json.loads(out)
                if ws.get("windows", 0) > 0:
                    subprocess.run(["pkill", "-x", "rofi"])
                    sys.exit(0)
except Exception:
    pass
' &
WATCHER_PID=$!

INITIAL_SELECTED_ROW=0
if [ "$INITIAL_MODE" = "estaticos" ] && [ "$COUNT_STATIC" -gt 0 ]; then
    INITIAL_SELECTED_ROW=$(( COUNT_STATIC / 2 ))
elif [ "$INITIAL_MODE" = "animados" ] && [ "$COUNT_ANIM" -gt 0 ]; then
    INITIAL_SELECTED_ROW=$(( COUNT_ANIM / 2 ))
fi

# 6. Lanzar Rofi con modos inteligentes 'estaticos' y 'animados'
rofi \
    -show "$INITIAL_MODE" \
    -selected-row "$INITIAL_SELECTED_ROW" \
    -modes "estaticos:${HOME}/.local/bin/selector-fondos --mode-static,animados:${HOME}/.local/bin/selector-fondos --mode-animated" \
    -theme "$THEME_FILE" \
    -theme-str "window { width: ${WIDTH}px; }" \
    -no-custom

# 7. Limpiar monitor al salir de Rofi
kill "$WATCHER_PID" 2>/dev/null || true
wait "$WATCHER_PID" 2>/dev/null || true
