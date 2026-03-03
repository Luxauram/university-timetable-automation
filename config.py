"""
config.py
=========
Application-wide configuration: colours, typography, window geometry,
network settings, and PDF-to-PPTX rendering parameters.

To add or modify courses, edit courses.py instead — this file
intentionally contains no course or university-specific data.

License: MIT
"""

import sys
from pathlib import Path

from courses import CORSI, BASE_STRAPI


# ── Application identity ──────────────────────────────────────────────────────

APP_VERSION: str = "1.0.0"
GITHUB_REPO: str = "https://github.com/Luxauram/university-timetable-automation"
AUTHOR: str = "Luxauram"


# ── Network ───────────────────────────────────────────────────────────────────

REQUEST_TIMEOUT: int = 30
USER_AGENT: str = "Mozilla/5.0"


# ── Default download folder ───────────────────────────────────────────────────


def _get_downloads_folder() -> Path:
    """
    Returns the current user's Downloads folder in a cross-platform way.

    On Windows the path is read from the registry (Shell Folders key) to
    handle non-standard locations; the standard ~/Downloads path is used
    as a fallback. On macOS and Linux ~/Downloads is used directly.

    @return: Path object pointing to the user's Downloads directory.
    """
    if sys.platform == "win32":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
            )
            downloads = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
            winreg.CloseKey(key)
            return Path(downloads)
        except Exception:
            return Path.home() / "Downloads"
    return Path.home() / "Downloads"


DEFAULT_DEST: str = str(_get_downloads_folder() / "Timetable_Downloads")


# ── Header text ───────────────────────────────────────────────────────────────

HEADER_TITLE: str = "Orari Lezioni"
HEADER_SUBTITLE: str = "Scarica i PDF degli orari direttamente dal sito universitario"


# ── Colour palette ────────────────────────────────────────────────────────────

BG = "#f0f4f8"
BG_ALT = "#e2eaf2"
SURFACE = "#ffffff"
BORDER = "#c5d3e0"

TEXT = "#1a2332"
TEXT_DIM = "#5a7090"

HEADER_BG = "#1e3a5f"
HEADER_FG = "#ffffff"
HEADER_SUB = "#90b4d0"


# ── Button colours ────────────────────────────────────────────────────────────
# Each tuple: (normal background, hover background, foreground text)

BTN_CONFIRM = ("#2d9e5f", "#237a4a", "#ffffff")
BTN_CANCEL = ("#d63b3b", "#b02e2e", "#ffffff")
BTN_INFO = ("#2980b9", "#1f6391", "#ffffff")
BTN_NEUTRAL = ("#dce6ef", "#c8d8e8", "#1a2332")


# ── Typography ────────────────────────────────────────────────────────────────

FONT = "Helvetica"
FONT_SIZE = 13
FONT_SMALL = 11
FONT_LARGE = 22


# ── Window geometry ───────────────────────────────────────────────────────────

WINDOW_TITLE = "University Timetable Automation"
WINDOW_SIZE = "980x900"
WINDOW_MIN_SIZE = (820, 780)


# ── PDF → PPTX rendering ─────────────────────────────────────────────────────

PPTX_DPI = 150
PPTX_SLIDE_W_IN = 11.69
PPTX_SLIDE_H_IN = 8.27
