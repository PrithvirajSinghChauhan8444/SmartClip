#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import requests
import shutil

# Talk like caveman: config path
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

def notify(msg):
    # Caveman notify
    print(f"Notify: {msg}")
    if shutil.which("notify-send"):
        subprocess.run(["notify-send", "SmartClip", msg])

def load_config():
    if not os.path.exists(CONFIG_PATH):
        notify("No config.json!")
        sys.exit(1)
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def get_selection():
    # Read Wayland primary selection
    if shutil.which("wl-paste"):
        try:
            res = subprocess.run(["wl-paste", "--primary"], capture_output=True, text=True, check=True)
            text = res.stdout.strip()
            if text:
                return text
        except Exception:
            pass

        # Fallback to clipboard
        try:
            res = subprocess.run(["wl-paste"], capture_output=True, text=True, check=True)
            text = res.stdout.strip()
            if text:
                return text
        except Exception:
            pass
    return None

def show_menu(config):
    # Prepare menu items
    items = []
    tags = config.get("tags", {})
    for tag, val in tags.items():
        items.append(f"{tag} - {val.get('name', '')}")
    
    menu_config = config.get("menu", {})
    tool = menu_config.get("tool", "wofi")
    args = menu_config.get("args", ["--dmenu"])

    # Fallback to rofi if wofi not installed
    if not shutil.which(tool):
        if tool == "wofi" and shutil.which("rofi"):
            tool = "rofi"
            args = ["-dmenu", "-p", "Select Action:"]
        elif tool == "rofi" and shutil.which("wofi"):
            tool = "wofi"
            args = ["--dmenu", "--prompt", "Select Action:"]
        else:
            notify(f"No menu tool ({tool}) found!")
            sys.exit(1)

    cmd = [tool] + args
    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = proc.communicate(input="\n".join(items))
        if proc.returncode != 0 or not out.strip():
            sys.exit(0) # Cancelled
        
        # Parse selected tag
        selected = out.strip().split(" - ")[0]
        if selected in tags:
            return selected
    except Exception as e:
        notify(f"Menu error: {e}")
        sys.exit(1)
    
    notify("Invalid selection")
    sys.exit(1)

def get_user_input(config, prompt_text):
    menu_config = config.get("menu", {})
    tool = menu_config.get("tool", "wofi")
    
    if not shutil.which(tool):
        if tool == "wofi" and shutil.which("rofi"):
            tool = "rofi"
        elif tool == "rofi" and shutil.which("wofi"):
            tool = "wofi"
        else:
            notify(f"No menu tool ({tool}) found!")
            sys.exit(1)

    if tool == "wofi":
        cmd = ["wofi", "--dmenu", "--prompt", prompt_text, "--width=400", "--height=100"]
    else:
        cmd = ["rofi", "-dmenu", "-p", prompt_text]

    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        out, _ = proc.communicate(input="")
        if proc.returncode != 0:
            return None
        return out.strip()
    except Exception as e:
        notify(f"Input error: {e}")
        return None

def query_ollama(config, prompt, text):
    ollama_config = config.get("ollama", {})
    host = ollama_config.get("host", "http://localhost:11434")
    model = ollama_config.get("model", "gemma4:e4b")
    options = ollama_config.get("options", {})

    url = f"{host}/api/generate"
    payload = {
        "model": model,
        "prompt": f"{prompt}\n\nInput Text:\n{text}",
        "stream": False,
        "options": options
    }

    try:
        res = requests.post(url, json=payload, timeout=90)
        res.raise_for_status()
        return res.json().get("response", "").strip()
    except Exception as e:
        notify(f"Ollama error: {e}")
        sys.exit(1)

def copy_to_clipboard(output):
    # Copy to both registers
    if shutil.which("wl-copy"):
        try:
            subprocess.run(["wl-copy", "--primary"], input=output, text=True, check=True)
            subprocess.run(["wl-copy"], input=output, text=True, check=True)
        except Exception as e:
            notify(f"Clipboard copy error: {e}")
            sys.exit(1)
    else:
        notify("wl-copy missing!")
        sys.exit(1)


def main():
    config = load_config()
    
    # 1. Get text
    text = get_selection()
    if not text:
        notify("No highlighted text!")
        sys.exit(1)

    # 2. Parse tag
    first_word = text.split()[0] if text.split() else ""
    tags = config.get("tags", {})
    
    tag = None
    if first_word in tags:
        tag = first_word
        # Strip tag from start of text
        text = text[len(tag):].strip()
    else:
        # Show dynamic menu
        tag = show_menu(config)

    # 3. Query LLM
    tag_config = tags[tag]
    prompt = tag_config["prompt"]
    
    if tag_config.get("input", False):
        question = get_user_input(config, "Ask question about text:")
        if not question:
            sys.exit(0) # Cancelled
        prompt = f"{prompt}\nUser Question: {question}"

    notify(f"Running {tag}...")
    output = query_ollama(config, prompt, text)

    if not output:
        notify("Empty AI output!")
        sys.exit(1)

    # 4. Copy to clipboard and notify
    copy_to_clipboard(output)
    notify("Output saved to clipboard!")

if __name__ == "__main__":
    main()
