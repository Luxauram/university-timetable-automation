"""
University Timetable Automation
========================
A cross-platform desktop application for downloading and converting
university timetable PDFs from web pages.

Entry point: initialises the GUI and starts the Tk event loop.

License: MIT
"""

import os
import sys
import tkinter as tk

from gui import App


def _set_window_icon(root: tk.Tk) -> None:
    """
    Attempts to set the application window icon from `icon.png`.
    Fails silently if the file is missing or the format is unsupported,
    so the app always starts regardless of icon availability.

    @param root: The root Tk window instance.
    """
    icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
    if not os.path.isfile(icon_path):
        return
    try:
        icon = tk.PhotoImage(file=icon_path)
        root.iconphoto(True, icon)
    except Exception:
        pass


if __name__ == "__main__":
    app = App()
    _set_window_icon(app)
    app.mainloop()
