"""
settings.py
===========
Persistent user preferences for the PDF Timetable Downloader.

Settings are stored as a JSON file in the OS-appropriate user data directory:
  - Windows : %APPDATA%\\UniversityTimetableAutomation\\settings.json
  - macOS   : ~/Library/Application Support/UniversityTimetableAutomation/settings.json
  - Linux   : ~/.config/UniversityTimetableAutomation/settings.json

The module exposes a single ``Settings`` instance (``settings``) that the
rest of the application imports directly. Changes are persisted by calling
``settings.save()``.

License: MIT
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULTS: dict = {
    "language": "it",  # "it" | "en"
    "pptx_default_on": True,
    "open_folder": True,
    "pptx_quality": "medium",
}

QUALITY_DPI: dict[str, int] = {
    "low": 72,
    "medium": 150,
    "high": 300,
}


def _get_settings_path() -> Path:
    """
    Returns the platform-appropriate path for the settings JSON file,
    creating parent directories if they do not exist.

    @return: Absolute Path to settings.json.
    """
    app_name = "UniversityTimetableAutomation"

    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home()))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))

    settings_dir = base / app_name
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir / "settings.json"


class Settings:
    """
    Thin wrapper around a dict of user preferences backed by a JSON file.

    Access individual settings via attribute syntax::

        settings.language          # → "it"
        settings.pptx_quality      # → "medium"
        settings.dpi               # → 150  (derived from pptx_quality)

    @ivar _data: Internal dict holding current preference values.
    @ivar _path: Path to the JSON file on disk.
    """

    def __init__(self) -> None:
        """
        Loads settings from disk, falling back to DEFAULTS for any missing key.
        """
        self._path = _get_settings_path()
        self._data = dict(DEFAULTS)
        self._load()

    def _load(self) -> None:
        """
        Reads the JSON file and merges its values into ``_data``.
        Missing or corrupt files are silently ignored (defaults are used).
        """
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                stored = json.load(f)
            for key in DEFAULTS:
                if key in stored:
                    self._data[key] = stored[key]
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self) -> None:
        """
        Writes the current settings dict to the JSON file.
        Fails silently if the file cannot be written.
        """
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key: str):
        """
        Returns the value for the given settings key.

        @param key: Settings key as defined in DEFAULTS.
        @return:    Current value, or the default if the key is unknown.
        """
        return self._data.get(key, DEFAULTS.get(key))

    def set(self, key: str, value) -> None:
        """
        Updates a settings value in memory. Call save() to persist it.

        @param key:   Settings key as defined in DEFAULTS.
        @param value: New value to store.
        """
        self._data[key] = value

    # ── Convenience properties ────────────────────────────────────────────────

    @property
    def language(self) -> str:
        """Active UI language code (``"it"`` or ``"en"``)."""
        return self._data["language"]

    @property
    def pptx_default_on(self) -> bool:
        """Whether the PPTX conversion checkbox should be checked on startup."""
        return self._data["pptx_default_on"]

    @property
    def open_folder(self) -> bool:
        """Whether to open the output folder after download completes."""
        return self._data["open_folder"]

    @property
    def pptx_quality(self) -> str:
        """PPTX rendering quality key: ``"low"``, ``"medium"``, or ``"high"``."""
        return self._data["pptx_quality"]

    @property
    def dpi(self) -> int:
        """
        DPI value derived from the current pptx_quality setting.
        Used directly by converter.py.

        @return: Integer DPI value (72, 150, or 300).
        """
        return QUALITY_DPI.get(self._data["pptx_quality"], 150)


# ── Singleton ─────────────────────────────────────────────────────────────────

settings = Settings()
