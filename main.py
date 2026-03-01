"""
University Timetable Automation
================================
A cross-platform desktop application for downloading and converting
university timetable PDFs from web pages.

Entry point: initialises the GUI and starts the Tk event loop.

Icon
----
Place ``icon.png`` (256x256 px, PNG) in the same directory as this file.
Pillow is used to load it, so any PNG format (RGBA, palette, greyscale)
is supported. The file is resolved relative to this script so it works
both when running from source and when bundled by PyInstaller.

License: MIT
"""

import os
import sys
import tkinter as tk

from gui import App


def _resolve_resource(filename: str) -> str:
    """
    Resolves a resource file path that works both when running from source
    and when bundled into a single executable by PyInstaller.

    PyInstaller extracts bundled files to a temporary folder referenced by
    ``sys._MEIPASS``; when running from source, the file sits next to this
    script.

    @param filename: Name of the resource file (e.g. ``"icon.png"``).
    @return:         Absolute path to the resource file.
    """
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, filename)


def _set_window_icon(root: tk.Tk) -> None:
    """
    Sets the application window icon using Pillow + ImageTk, which supports
    any PNG format (RGBA, palette, greyscale, etc.).

    Falls back silently if the icon file is missing or loading fails,
    so the application always starts regardless of icon availability.

    @param root: The root Tk window instance.
    """
    icon_path = _resolve_resource("icon.png")
    if not os.path.isfile(icon_path):
        return
    try:
        from PIL import Image, ImageTk

        img = Image.open(icon_path).convert("RGBA")
        icon = ImageTk.PhotoImage(img)
        root.iconphoto(True, icon)
        root._icon_ref = icon
    except Exception:
        pass


if __name__ == "__main__":
    app = App()
    _set_window_icon(app)
    app.mainloop()
