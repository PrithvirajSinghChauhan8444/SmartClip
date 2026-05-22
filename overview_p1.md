# Project Specification: Actionable Smart Clipboard (Phase 1)

## 1. Project Overview

**The Actionable Smart Clipboard is a localized, AI-driven background service that intercepts text copied by the user, processes it through a specific prompt based on a "tag," and automatically replaces the original text on the screen with the AI-generated output**^^^^^^.

**Phase 1 focuses strictly on core routing and text manipulation using generative AI **^^, without full autonomous decision-making or external agentic tools^^.

## 2. Scope & Constraints

* **Environment:** Designed exclusively for Linux environments ^^ (specifically integrated with window managers like Hyprland).
* **Scale:** Single device implementation^^.
* **AI Engine:** Local Generative AI processing (via Ollama) to ensure zero latency, zero cost, and total data privacy^^.
* **Autonomy Level:** Strictly manual/user-directed. The system does not guess user intent; it only acts when explicitly instructed via tags or a UI menu.

## 3. The Core Architecture (The Hotkey Workflow)

To preserve system resources and user privacy, the service does not constantly monitor standard copy events (`Ctrl+C`). Instead, it uses an "Active Hotkey" architecture.

* **Step 1: The Active Trigger**
  The user highlights a block of text and presses a dedicated global hotkey (e.g., `Super + Shift + C`). The background service wakes up and copies the highlighted text to the system clipboard.
* **Step 2: The Tag Check**
  The service reads the string and checks for a predefined inline tag prefix (e.g., `!format`, `!json`, `!cal`).
  * *Path A (Tag Found):* The script strips the tag from the text and prepares to route the remaining content.
  * *Path B (No Tag Found):* The script instantly launches a lightweight, transparent dynamic menu (e.g., via `rofi` or `wofi`) at the mouse cursor, allowing the user to select the desired action tag manually. If the user cancels the menu, the process terminates immediately.
* **Step 3: AI Routing & Execution**
  The system maps the identified tag to a specific instruction set (system prompt) and sends both the instruction and the raw text to the local LLM.
* **Step 4: Output & Replacement**
  Once the LLM generates the final output, the service updates the system clipboard memory with the new text. **It then simulates a native paste command (e.g., **`<span class="citation-66">Ctrl+V</span>` or `<span class="citation-66">Shift+Insert</span>`), automatically replacing the user's highlighted text on the screen with the processed result^^.

## 4. Proposed Tech Stack

* **Core Logic:** Python (lightweight daemon script).
* **AI Backend:** Ollama running a fast, efficient model (e.g., `llama3.1:8b`).
* **Clipboard Management:** `wl-clipboard` (standard for Wayland/Hyprland).
* **Hotkey Binding:** Handled natively via the `hyprland.conf` file to execute the Python script.
* **Dynamic Menu (UI):** `wofi`, `rofi` (Wayland fork), or `fuzzel` for the lightning-fast tag selection overlay.
* **Keyboard Simulation:** `ydotool` or `wtype` to simulate the final paste keystroke.

## 5. Development Roadmap (Phase 1)

1. **Clipboard I/O:** Write the basic Python script to read from and write to the Linux clipboard using Wayland tools.
2. **Hotkey Binding:** Map the script execution to the designated shortcut in the window manager.
3. **Tag Parsing Logic:** Implement the string-checking function to identify inline tags and strip them from the content payload.
4. **Menu Integration:** Connect the fallback "No Tag" logic to a local launcher (like `wofi`) to pass a selected tag back to the script.
5. **Ollama Connection:** Route the tag and content to the local Ollama API, applying specific system prompts based on the tag.
6. **Auto-Paste Mechanism:** Implement the final simulated keystroke to replace the text seamlessly on the user's screen.
