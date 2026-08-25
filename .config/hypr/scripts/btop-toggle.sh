#!/usr/bin/env bash

# ========================================================== #
#                      HYPER - RICE                          #
# ========================================================== #

if pgrep -f "btop_float" >/dev/null 2>&1; then
    pkill -f "btop_float" 2>/dev/null
else
    kitty --class btop_float -e btop
fi
