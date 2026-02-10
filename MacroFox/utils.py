import json
from pathlib import Path

def format_time(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"

SETTINGS_PATH = Path.home() / "Documents" / "MacroFox" / "Settings" / "settings.json"

def load_settings():
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r") as f:
                data = json.load(f)
                from constants import THEMES
                if data.get("theme") not in THEMES:
                    data["theme"] = "light"
                return data
        except Exception:
            pass
    return {"theme": "light", "always_on_top": False}

def save_settings(data):
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w") as f:
        json.dump(data, f, indent=2)

CUSTOM_TIMER_PATH = Path.home() / "Documents" / "MacroFox" / "Settings" / "custom_timers.json"

def load_custom_timers():
    CUSTOM_TIMER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if CUSTOM_TIMER_PATH.exists():
        try:
            with open(CUSTOM_TIMER_PATH, "r") as f:
                data = json.load(f)
                from constants import MATERIAL_TIMER
                return {
                    k: v for k, v in data.items()
                    if k in MATERIAL_TIMER and isinstance(v, int) and v > 0
                }
        except Exception:
            pass
    return {}

def save_custom_timers(data):
    CUSTOM_TIMER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CUSTOM_TIMER_PATH, "w") as f:
        json.dump(data, f, indent=2)