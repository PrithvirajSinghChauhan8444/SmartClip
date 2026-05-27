# SmartClip

A localized, AI-driven background service for Linux (Wayland/Hyprland) that intercepts selected text, processes it using a local LLM via specific tags, and updates the system clipboard.

---

## Current State & Features
* **Zero Latency & Privacy**: Powered by local **Ollama** running `gemma4:e4b`.
* **Wayland Native**: Retrieves text seamlessly using `wl-paste --primary` and copies back with `wl-copy`.
* **Dynamic Menu Fallback**: If no inline tag is found in the highlighted text, it launches `wofi` (or `rofi`) at the mouse cursor to select an action.
* **Interactive Tag Support (`!ask`)**: Prompts the user with a second input box to ask a custom question about the selected text.
* **Desktop Notifications**: Uses `notify-send` to keep the user informed of active tasks and finished outputs.

---

## Directory Structure
```
SmartClip/
├── .venv/                 # Local Python virtual environment
├── config.json            # Tags, prompts, and Ollama configuration
├── smartclip.py           # Core orchestrator script
├── setup.sh               # Dependency and environment checker
└── README.md              # This document
```

---

## Installation & Setup

1. **Verify System Dependencies**:
   Ensure you have the required Wayland utilities installed:
   ```bash
   # Arch Linux
   sudo pacman -S wl-clipboard wofi notify-send
   ```

2. **Initialize Environment**:
   Verify everything is ready by running the setup script:
   ```bash
   ./setup.sh
   ```

3. **Install Python Packages**:
   Make sure the dependencies are installed inside the virtual environment:
   ```bash
   .venv/bin/pip install requests
   ```

---

## How To Use

### Method 1: Manual Run (Terminal)
1. Highlight some text on your screen.
2. Run the script:
   ```bash
   .venv/bin/python3 smartclip.py
   ```
3. A `wofi` menu will overlay. Select an action.
4. The output is copied directly to your clipboard (and auto-pasted back if `wtype` is installed).

---

## Direct Command & Execution Modes 🚀
We have added two high-productivity direct execution modes:

### 1. Direct Command Mode (`-d` / `--direct`)
* **What it does**: Prompts you for a custom instruction to apply to the highlighted text.
* **Example**: Highlight `"Hello my friend"`, run with `-d`, type `"Translate to Spanish"`, and get `"Hola mi amigo"`.
* **CLI Command**:
  ```bash
  .venv/bin/python3 smartclip.py --direct
  ```

### 2. Direct Text Execution Mode (`-e` / `--exec`)
* **What it does**: Instantly treats the highlighted text *itself* as the direct prompt/instruction for the AI, bypassing all prompt menus.
* **Example**: Highlight `"Write a quick joke about programmers"`, run with `-e`, and it gets replaced/copied instantly with the joke.
* **CLI Command**:
  ```bash
  .venv/bin/python3 smartclip.py --exec
  ```

---

## Global Hotkey Configurations
To integrate these modes seamlessly into your Hyprland workspace, add the following bindings to `~/.config/hypr/hyprland.conf`:

```ini
# Normal SmartClip (Inline tag detection or Tag Menu fallback)
bind = SUPER_SHIFT, C, exec, /home/prit/Project_Linux/SmartClip/.venv/bin/python3 /home/prit/Project_Linux/SmartClip/smartclip.py

# Direct Command Mode (Prompts for custom instruction on highlighted text)
bind = SUPER_CTRL, C, exec, /home/prit/Project_Linux/SmartClip/.venv/bin/python3 /home/prit/Project_Linux/SmartClip/smartclip.py --direct

# Direct Text Execution Mode (Treats highlighted text itself as AI prompt)
bind = SUPER_ALT, C, exec, /home/prit/Project_Linux/SmartClip/.venv/bin/python3 /home/prit/Project_Linux/SmartClip/smartclip.py --exec
```
