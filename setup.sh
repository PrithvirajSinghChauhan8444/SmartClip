#!/usr/bin/env bash

# Caveman check tools
echo "--- SmartClip Setup Check ---"

check_tool() {
    if command -v "$1" >/dev/null 2>&1; then
        echo "[OK] $1 found"
        return 0
    else
        echo "[MISSING] $1 not found!"
        return 1
    fi
}

FAILED=0

check_tool "wl-paste" || FAILED=1
check_tool "wl-copy" || FAILED=1
check_tool "wtype" || FAILED=1

if command -v wofi >/dev/null 2>&1 || command -v rofi >/dev/null 2>&1; then
    echo "[OK] Menu launcher found"
else
    echo "[MISSING] Neither wofi nor rofi found!"
    FAILED=1
fi

if [ $FAILED -eq 1 ]; then
    echo "--- INSTALL REQUIRED SYSTEM PACKAGES ---"
    echo "Arch: sudo pacman -S wl-clipboard wofi wtype"
    echo "Ubuntu: sudo apt install wl-clipboard wofi wtype"
else
    echo "System dependencies OK!"
fi
