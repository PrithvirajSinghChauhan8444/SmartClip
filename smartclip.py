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

def paste_output():
    # If wtype is installed, automatically paste output to replace highlighted text
    if shutil.which("wtype"):
        try:
            import time
            time.sleep(0.15)  # Wait for active window focus to restore
            subprocess.run(["wtype", "-M", "ctrl", "-P", "v", "-m", "ctrl"], check=True)
        except Exception as e:
            notify(f"Auto-paste error: {e}")

def main():
    config = load_config()
    
    # Parse CLI modes
    mode = "default"
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ("--direct", "-d", "--prompt", "-p"):
            mode = "direct"
        elif arg in ("--exec", "-e", "--run", "-r"):
            mode = "exec"
        elif arg in ("--help", "-h"):
            print("SmartClip CLI Options:")
            print("  (no args)                     Default mode (inline tag or menu fallback)")
            print("  -d, --direct, -p, --prompt    Prompt for a custom command to apply to the selection")
            print("  -e, --exec, -r, --run         Treat selection directly as AI instruction/prompt")
            print("  -h, --help                    Show this help message")
            sys.exit(0)

    # 1. Get text
    text = get_selection()
    if not text:
        notify("No highlighted text!")
        sys.exit(1)

    tags = config.get("tags", {})
    prompt = None

    if mode == "direct":
        # Prompt user for direct command/instruction
        instruction = get_user_input(config, "Enter custom instruction:")
        if not instruction:
            sys.exit(0) # Cancelled
        prompt = f"Follow the user's custom instruction to process the input text.\nInstruction: {instruction}\n\nInput Text:"
        notify("Running custom command...")
        
    elif mode == "exec":
        # Selected text itself is the direct command/instruction
        prompt = "You are a helpful AI assistant. Execute the instruction, answer the question, or complete the task specified in the input text directly and concisely. Output ONLY the response/result. No intro, no explanation, no wrappers."
        notify("Executing text directly...")
        
    else:
        # Default behavior: check tag first
        first_word = text.split()[0] if text.split() else ""
        
        tag = None
        if first_word in tags:
            tag = first_word
            # Strip tag from start of text
            text = text[len(tag):].strip()
        else:
            # Show dynamic menu
            tag = show_menu(config)

        # Query LLM based on tag config
        tag_config = tags[tag]
        prompt = tag_config.get("prompt", "")

        # Special input handling for !custom and other input tags
        if tag == "!custom" or tag_config.get("input", False):
            prompt_label = "Enter custom instruction:" if tag == "!custom" else "Ask question about text:"
            instruction = get_user_input(config, prompt_label)
            if not instruction:
                sys.exit(0) # Cancelled
            if tag == "!custom":
                prompt = f"Follow the user's custom instruction to process the input text.\nInstruction: {instruction}\n\nInput Text:"
            else:
                prompt = f"{prompt}\nUser Question: {instruction}"

        notify(f"Running {tag}...")

    # 3. Query LLM
    output = query_ollama(config, prompt, text)

    if not output:
        notify("Empty AI output!")
        sys.exit(1)

    # 4. Copy to clipboard, notify, and auto-paste
    copy_to_clipboard(output)
    notify("Output saved to clipboard!")
    paste_output()

if __name__ == "__main__":
    main()
