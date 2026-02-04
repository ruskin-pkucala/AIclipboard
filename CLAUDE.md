# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Windows desktop application that automatically monitors clipboard changes and provides AI-powered text correction/polishing using Zhipu AI (智谱 AI) GLM-4.7 API.

**Tech Stack**: Python 3.8+, PyQt5 (GUI), SQLite (storage), pywin32 (clipboard monitoring), zhipuai (AI service)

## Running the Application

```bash
# Run directly (Python 3.12)
py -3.12 main.py

# Or use the batch file
启动.bat

# Test AI service connection
py -3.12 test_ai.py
# or
test.bat
```

## Building to EXE

```bash
pip install pyinstaller
pyinstaller build.spec
```

Output: Single-file executable at `dist/剪贴板智能纠错工具.exe`

## Architecture

### Entry Point & Coordination
- [main.py](main.py) - `ClipboardPolisherApp` class orchestrates all components:
  - Creates MainWindow and SystemTray
  - Starts ClipboardWatcher background thread
  - Handles first-time API key setup dialog

### Clipboard Monitoring
- [clipboard_watcher.py](clipboard_watcher.py) - `ClipboardWatcher` runs in daemon thread
  - Polls Windows clipboard via `win32clipboard` every 0.3s
  - Detects changes using MD5 hash comparison
  - Saves images to `~/.clipboard-polisher/images/`
  - Callback pattern: `callback(content_type, content, image_path)`

### Data Layer
- [database.py](database.py) - SQLite wrapper with FIFO auto-cleanup
  - DB location: `~/.clipboard-polisher/records.db`
  - Max records: 50 (configurable)
  - Table: `clipboard_records` (id, content_type, content, image_path, timestamp, corrected, correction_status)

### AI Service
- [ai_service.py](ai_service.py) - `AIService` wraps Zhipu AI GLM-4.7 API
  - Rate limiting: 1 second minimum between requests (thread-safe with lock)
  - Retry logic: 3 attempts with exponential backoff for 429/1302 rate limit errors
  - Modes: `correct`, `formal`, `casual`, `academic`, `concise`, `creative`

### Configuration
- [config/settings.py](config/settings.py) - `Config` class loads API key from:
  1. `~/.clipboard-polisher/config.json` (preferred, created on first run)
  2. Environment variable `ZHIPUAI_API_KEY`

### GUI Components
- [gui/main_window.py](gui/main_window.py) - Main window with record list + preview panel
- [gui/result_window.py](gui/result_window.py) - Split-view dialog (original vs corrected) with mode selection
- [gui/system_tray.py](gui/system_tray.py) - System tray icon with context menu

## Thread Safety Notes

- ClipboardWatcher runs in background daemon thread
- GUI updates from clipboard callback use `QTimer.singleShot()` to execute on main thread
- AI service uses `threading.Lock()` for rate limiting

## Data Storage

| Location | Purpose |
|----------|---------|
| `~/.clipboard-polisher/config.json` | API key storage |
| `~/.clipboard-polisher/records.db` | SQLite database |
| `~/.clipboard-polisher/images/` | Clipboard images |
