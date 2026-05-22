# SmartClip — Future Agentic Roadmap

This document outlines the planned future features to transform **SmartClip** from a text processing utility into an **Agentic Action Tool**.

---

## 1. Agentic Actions (Tool-Executing Tags)

Unlike standard text tags that return output to the clipboard, **Agentic Tags** will execute system actions based on AI outputs.

### `!mail_send` (Send Email)
* **Goal**: Select a raw piece of text and launch a prefilled draft in your default email client.
* **Mechanism**:
  1. AI parses the highlighted text to extract `recipient`, `subject`, and `body`.
  2. Python script dynamically URL-encodes these fields.
  3. Launches system default mailto application:
     ```bash
     xdg-open "mailto:recipient@mail.com?subject=Subject&body=Body"
     ```

### `!search` (Contextual Web Search)
* **Goal**: Select an error code, term, or code block and search for it directly.
* **Mechanism**:
  1. AI extracts the core error or research question.
  2. Python script opens the default browser:
     ```bash
     xdg-open "https://duckduckgo.com/?q=extracted+search+query"
     ```

### `!cal_add` (Add Calendar Event)
* **Goal**: Highlight a conversational text (e.g. *"let's meet tomorrow at 3pm at HQ"*) and add it to your local calendar.
* **Mechanism**:
  1. AI parses the text into structured JSON: `title`, `date`, `time`, `location`.
  2. Script creates a temporary `.ics` (iCalendar) file.
  3. Automatically imports it using `gcalcli` or opens it in a system calendar app (like KOrganizer).

### `!todo_add` (Add Task)
* **Goal**: Instantly extract action items from high-level notes and append them to a checklist.
* **Mechanism**:
  1. AI extracts clear todo items.
  2. Appends them directly to a local `/home/prit/tasks.md` or a `todo.txt` ledger file.

### `!shell` (Safe Shell Command Execution)
* **Goal**: Describe a command you want to run (e.g. *"show me current disk space"*), and let the tool generate and run it.
* **Mechanism**:
  1. AI translates descriptions to precise shell commands.
  2. Script triggers a `wofi`/`rofi` confirmation box showing the command.
  3. If user approves, execution proceeds in a subshell, returning results to a desktop notification.

---

## 2. Dynamic Tool Execution Pipeline

To support these, `smartclip.py` will be updated to handle **Structured Outputs**:
1. When a tool-executing tag is triggered, the Ollama payload will ask for structured JSON (using Ollama's `format: "json"`).
2. The script will parse the JSON, identify the tool type, and call a dedicated local runner (e.g., `run_mailto()`, `run_calendar()`).
