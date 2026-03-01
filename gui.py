"""
gui.py
======
Graphical user interface layer for the PDF Timetable Downloader.

Builds and manages all Tkinter widgets. Contains no scraping or conversion
logic — it delegates entirely to scraper.py and converter.py.

Design notes
------------
- ``ttk.Button`` with custom named styles is used instead of ``tk.Button``
  because macOS's native Aqua theme silently overrides ``bg``/``fg`` on
  standard Tk buttons, making custom colours impossible without ttk styles.
- Forcing ``ttk.Style.theme_use("default")`` switches to the cross-platform
  theme, which respects all colour and font overrides on every OS.
- All long-running operations (network requests, file I/O, PDF rendering) run
  in daemon threads and communicate back to the main thread via
  ``widget.after()``, keeping the UI fully responsive.

License: MIT
"""

import os
import re
import subprocess
import sys
import threading
from tkinter import filedialog, messagebox
import tkinter as tk
from tkinter import ttk

import requests

from config import (
    BG,
    BG_ALT,
    SURFACE,
    BORDER,
    TEXT,
    TEXT_DIM,
    HEADER_BG,
    HEADER_FG,
    HEADER_SUB,
    BTN_CONFIRM,
    BTN_CANCEL,
    BTN_INFO,
    BTN_NEUTRAL,
    FONT,
    FONT_SIZE,
    FONT_SMALL,
    FONT_LARGE,
    WINDOW_TITLE,
    WINDOW_SIZE,
    WINDOW_MIN_SIZE,
    CORSI,
    DEFAULT_DEST,
    REQUEST_TIMEOUT,
    USER_AGENT,
)
from scraper import scrape_pdf_links
from converter import pdf_to_pptx


# ── Module-level helpers ───────────────────────────────────────────────────────


def _sanitize_filename(name: str) -> str:
    """
    Removes characters that are illegal in file system paths and trims the
    result to a safe maximum length.

    @param name: Raw string to sanitize (typically a PDF label).
    @return:     A filesystem-safe filename string without an extension.
    """
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.strip(". ")
    return name[:120] if name else "file"


def _strip_pdf_ext(name: str) -> str:
    """
    Removes a trailing ``.pdf`` extension from a string (case-insensitive).
    Used to prevent labels that already contain the extension from producing
    double-extension filenames such as ``filename.pdf.pdf``.

    @param name: Input string, possibly ending with ``.pdf``.
    @return:     The input string with the trailing ``.pdf`` removed, if present.
    """
    return name[:-4] if name.lower().endswith(".pdf") else name


def _unique_path(directory: str, filename: str) -> str:
    """
    Returns a file path that does not yet exist on disk.

    If ``filename`` already exists in ``directory``, a numeric suffix is
    appended to the base name (e.g. ``file_1.pdf``, ``file_2.pdf``, …).

    @param directory: Target directory for the file.
    @param filename:  Desired filename including extension.
    @return:          A unique, non-colliding absolute file path.
    """
    path = os.path.join(directory, filename)
    base, ext = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = f"{base}_{counter}{ext}"
        counter += 1
    return path


def _open_folder(path: str) -> None:
    """
    Opens a directory in the default file manager of the current OS.
    Fails silently if the operation is unsupported or raises an exception.

    @param path: Absolute path of the folder to open.
    """
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


# ── Main application class ────────────────────────────────────────────────────


class App(tk.Tk):
    """
    Root Tk window and application controller.

    Responsibilities:
    - Build and lay out all UI sections (header, cards, bottom bar, status bar).
    - Manage application state (pdf_links, check_vars, dest_dir, convert_var).
    - Dispatch background threads for network and file operations.
    - Route thread results back to UI via ``after()`` callbacks.
    """

    def __init__(self) -> None:
        """
        Initialises the Tk root window, sets up ttk styles, and builds the UI.

        Calls ``update_idletasks()`` after building the UI so that Tk finishes
        computing all widget sizes before the window is shown. This prevents
        the status bar and bottom bar from being clipped on the first render.
        """
        super().__init__()
        self.title(WINDOW_TITLE)
        self.configure(bg=BG)

        self.pdf_links: list[dict] = []
        self.check_vars: list[tk.BooleanVar] = []
        self.dest_dir = tk.StringVar(value=DEFAULT_DEST)
        self.convert_var = tk.BooleanVar(value=True)

        self._setup_styles()
        self._build_ui()

        # Let Tk finish computing all widget sizes, then enforce geometry.
        # This ensures the status bar is never clipped on startup.
        self.update_idletasks()
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)

    # ── Style setup ───────────────────────────────────────────────────────────

    def _setup_styles(self) -> None:
        """
        Configures all ttk widget styles used by the application.

        Forces the cross-platform ``"default"`` theme so that custom colours
        are not overridden by the macOS Aqua or Windows native themes.
        Registers four named button styles (Confirm, Cancel, Info, Neutral)
        and configures the progress bar and scrollbar appearance.
        """
        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "App.Horizontal.TProgressbar",
            troughcolor=BG_ALT,
            background=BTN_CONFIRM[0],
            thickness=8,
        )

        style.configure(
            "TCombobox",
            fieldbackground=SURFACE,
            background=SURFACE,
            foreground=TEXT,
            selectbackground=SURFACE,
            selectforeground=TEXT,
            font=(FONT, FONT_SIZE),
        )

        style.configure(
            "TScrollbar",
            background=BG_ALT,
            troughcolor=SURFACE,
            borderwidth=0,
            arrowsize=14,
        )

        for name, palette in (
            ("Confirm.TButton", BTN_CONFIRM),
            ("Cancel.TButton", BTN_CANCEL),
            ("Info.TButton", BTN_INFO),
            ("Neutral.TButton", BTN_NEUTRAL),
        ):
            self._register_btn_style(name, palette)

    def _register_btn_style(self, name: str, palette: tuple) -> None:
        """
        Registers a single named ttk.Button style with normal, hover (active),
        and pressed colour states derived from the given palette.

        @param name:    ttk style name (e.g. ``"Confirm.TButton"``).
        @param palette: Three-tuple of hex strings ``(normal_bg, hover_bg, fg)``.
        """
        bg, hover, fg = palette
        pressed = _darken(hover)
        style = ttk.Style()
        style.configure(
            name,
            background=bg,
            foreground=fg,
            font=(FONT, FONT_SIZE, "bold"),
            borderwidth=0,
            focusthickness=0,
            focuscolor=bg,
            padding=(18, 10),
            relief="flat",
        )
        style.map(
            name,
            background=[("pressed", pressed), ("active", hover)],
            foreground=[("pressed", fg), ("active", fg)],
            relief=[("pressed", "flat"), ("active", "flat")],
        )

    # ── Widget factories ──────────────────────────────────────────────────────

    def _btn(
        self, parent: tk.Widget, text: str, command, kind: str = "confirm", **kw
    ) -> ttk.Button:
        """
        Creates and returns a styled ttk.Button.

        @param parent:  Parent widget.
        @param text:    Button label.
        @param command: Callback invoked on click.
        @param kind:    One of ``"confirm"`` (green), ``"cancel"`` (red),
                        ``"info"`` (blue), or ``"neutral"`` (grey).
        @param kw:      Additional keyword arguments forwarded to ttk.Button.
        @return:        Configured ttk.Button (not yet packed/gridded).
        """
        style_map = {
            "confirm": "Confirm.TButton",
            "cancel": "Cancel.TButton",
            "info": "Info.TButton",
            "neutral": "Neutral.TButton",
        }
        return ttk.Button(
            parent,
            text=text,
            command=command,
            style=style_map.get(kind, "Neutral.TButton"),
            cursor="hand2",
            **kw,
        )

    def _label(
        self,
        parent: tk.Widget,
        text: str,
        size: int = None,
        bold: bool = False,
        dim: bool = False,
        bg: str = None,
        **kw,
    ) -> tk.Label:
        """
        Creates and returns a tk.Label with consistent typography.

        @param parent: Parent widget.
        @param text:   Label text.
        @param size:   Font size override; defaults to FONT_SIZE.
        @param bold:   If True, uses bold font weight.
        @param dim:    If True, uses TEXT_DIM colour instead of TEXT.
        @param bg:     Background colour override; defaults to BG.
        @param kw:     Additional keyword arguments forwarded to tk.Label.
        @return:       Configured tk.Label (not yet packed/gridded).
        """
        return tk.Label(
            parent,
            text=text,
            font=(FONT, size or FONT_SIZE, "bold" if bold else "normal"),
            bg=bg or BG,
            fg=TEXT_DIM if dim else TEXT,
            **kw,
        )

    def _entry(
        self, parent: tk.Widget, var: tk.StringVar, width: int = 40, bg: str = SURFACE
    ) -> tk.Entry:
        """
        Creates and returns a flat-bordered tk.Entry.

        @param parent: Parent widget.
        @param var:    StringVar to bind to the entry.
        @param width:  Character width of the entry field.
        @param bg:     Background colour of the entry field.
        @return:       Configured tk.Entry (not yet packed/gridded).
        """
        return tk.Entry(
            parent,
            textvariable=var,
            font=(FONT, FONT_SMALL),
            bg=bg,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            width=width,
        )

    def _card(self, parent: tk.Widget, pady: int = 10, padx: int = 20) -> tk.Frame:
        """
        Creates and returns a white surface frame with a subtle border,
        used to visually group related controls.

        @param parent: Parent widget.
        @param pady:   Internal vertical padding.
        @param padx:   Internal horizontal padding.
        @return:       Configured tk.Frame (not yet packed).
        """
        return tk.Frame(
            parent,
            bg=SURFACE,
            highlightbackground=BORDER,
            highlightthickness=1,
            pady=pady,
            padx=padx,
        )

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        """
        Constructs the full window layout by composing the individual sections.
        """
        self._build_header()
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=14)
        self._build_card_corso(outer)
        self._build_card_link_esterni(outer)
        self._build_card_lista(outer)
        self._build_bottom_bar()
        self._build_status_bar()

    def _build_header(self) -> None:
        """
        Builds the dark top banner with the application title and subtitle.
        Title and subtitle text are read from config.py (HEADER_TITLE,
        HEADER_SUBTITLE) so they can be changed without touching this file.
        """
        from config import HEADER_TITLE, HEADER_SUBTITLE

        hdr = tk.Frame(self, bg=HEADER_BG, pady=20)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text=HEADER_TITLE,
            font=(FONT, FONT_LARGE, "bold"),
            bg=HEADER_BG,
            fg=HEADER_FG,
        ).pack()
        tk.Label(
            hdr,
            text=HEADER_SUBTITLE,
            font=(FONT, FONT_SMALL),
            bg=HEADER_BG,
            fg=HEADER_SUB,
        ).pack(pady=(3, 0))

    def _build_card_corso(self, parent: tk.Widget) -> None:
        """
        Builds the top card containing:
        - course selection combobox + "Carica orari" button
        - destination folder entry + "Sfoglia..." button
        - PDF-to-PPTX conversion checkbox

        @param parent: Container widget to pack the card into.
        """
        card = self._card(parent, pady=16, padx=18)
        card.pack(fill="x", pady=(0, 10))
        card.columnconfigure(1, weight=1)

        self._label(card, "Corso di laurea", bold=True, bg=SURFACE).grid(
            row=0, column=0, sticky="w", padx=(0, 12), pady=(0, 6)
        )
        self.corso_var = tk.StringVar(value=list(CORSI.keys())[0])
        ttk.Combobox(
            card,
            textvariable=self.corso_var,
            values=list(CORSI.keys()),
            state="readonly",
            font=(FONT, FONT_SIZE),
            width=50,
        ).grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=(0, 6))
        self._btn(card, "Carica orari", self._on_carica, kind="info").grid(
            row=0, column=2, pady=(0, 6)
        )

        self._label(card, "Salva in:", dim=True, bg=SURFACE).grid(
            row=1, column=0, sticky="w", padx=(0, 12), pady=4
        )
        self._entry(card, self.dest_dir, width=50, bg=BG_ALT).grid(
            row=1, column=1, sticky="ew", padx=(0, 12), pady=4
        )
        self._btn(card, "Sfoglia...", self._on_sfoglia, kind="info").grid(row=1, column=2, pady=4)

        conv_frame = tk.Frame(card, bg=SURFACE)
        conv_frame.grid(row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        tk.Checkbutton(
            conv_frame,
            variable=self.convert_var,
            text="  Converti automaticamente i PDF in PowerPoint (.pptx)",
            font=(FONT, FONT_SMALL),
            bg=SURFACE,
            fg=TEXT,
            selectcolor=SURFACE,
            activebackground=SURFACE,
            activeforeground=TEXT,
            relief="flat",
            highlightthickness=0,
        ).pack(side="left")

    def _build_card_link_esterni(self, parent: tk.Widget) -> None:
        """
        Builds the card that lets the user manually add a PDF from an
        arbitrary external URL, with an optional custom display name.

        @param parent: Container widget to pack the card into.
        """
        card = self._card(parent, pady=12, padx=18)
        card.pack(fill="x", pady=(0, 10))

        self._label(card, "Aggiungi PDF da link esterno", bold=True, bg=SURFACE).pack(anchor="w")
        self._label(
            card,
            "Incolla un URL diretto a un PDF per aggiungerlo alla lista",
            size=FONT_SMALL,
            dim=True,
            bg=SURFACE,
        ).pack(anchor="w", pady=(2, 8))

        row = tk.Frame(card, bg=SURFACE)
        row.pack(fill="x")

        self.ext_url_var = tk.StringVar()
        self.ext_label_var = tk.StringVar()

        self._label(row, "URL:", bg=SURFACE).pack(side="left")
        self._entry(row, self.ext_url_var, width=44, bg=BG_ALT).pack(side="left", padx=(6, 16))
        self._label(row, "Nome:", bg=SURFACE).pack(side="left")
        self._entry(row, self.ext_label_var, width=18, bg=BG_ALT).pack(side="left", padx=6)
        self._btn(row, "Aggiungi", self._on_aggiungi_link, kind="confirm").pack(
            side="left", padx=(10, 0)
        )

    def _build_card_lista(self, parent: tk.Widget) -> None:
        """
        Builds the scrollable PDF list card.

        Uses a Canvas + inner Frame pattern to support vertical scrolling with
        both mouse wheel and trackpad gestures on macOS, Windows, and Linux.

        @param parent: Container widget to pack the card into.
        """
        card = self._card(parent, pady=12, padx=18)
        card.pack(fill="both", expand=True)

        self._label(card, "PDF disponibili", bold=True, bg=SURFACE).pack(anchor="w")

        border = tk.Frame(card, bg=BORDER, bd=1)
        border.pack(fill="both", expand=True, pady=(8, 0))

        self._canvas = tk.Canvas(border, bg=SURFACE, highlightthickness=0)
        scrollbar = ttk.Scrollbar(border, orient="vertical", command=self._canvas.yview)
        self.scroll_frame = tk.Frame(self._canvas, bg=SURFACE)

        self.scroll_frame.bind(
            "<Configure>",
            lambda _: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )

        self._canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self._canvas.configure(yscrollcommand=scrollbar.set)
        self._canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self._canvas.bind_all(
            "<MouseWheel>",
            lambda e: self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"),
        )
        self._canvas.bind_all("<Button-4>", lambda _: self._canvas.yview_scroll(-1, "units"))
        self._canvas.bind_all("<Button-5>", lambda _: self._canvas.yview_scroll(1, "units"))

        self._label(
            self.scroll_frame,
            'Seleziona un corso e premi "Carica orari"',
            dim=True,
            bg=SURFACE,
        ).pack(pady=30)

    def _build_bottom_bar(self) -> None:
        """
        Builds the action bar at the bottom of the window.

        Left side: "Seleziona tutti" (green) and "Deseleziona tutti" (red).
        Right side: "Scarica PDF selezionati" (green, prominent).
        """
        bar = tk.Frame(self, bg=BG, pady=14, padx=20)
        bar.pack(fill="x")

        left = tk.Frame(bar, bg=BG)
        left.pack(side="left")
        self._btn(left, "Seleziona tutti", self._on_select_all, kind="confirm").pack(
            side="left", padx=(0, 10)
        )
        self._btn(left, "Deseleziona tutti", self._on_deselect_all, kind="cancel").pack(side="left")

        right = tk.Frame(bar, bg=BG)
        right.pack(side="right")
        self._btn(right, "⬇   Scarica PDF selezionati", self._on_scarica, kind="confirm").pack(
            side="right"
        )

    def _build_status_bar(self) -> None:
        """
        Builds the status bar at the very bottom of the window, consisting of
        a progress bar (ttk) and a status message label.
        """
        self.progress = ttk.Progressbar(
            self, mode="determinate", style="App.Horizontal.TProgressbar"
        )
        self.progress.pack(fill="x")

        self.status_var = tk.StringVar(value="Pronto.")
        tk.Label(
            self,
            textvariable=self.status_var,
            font=(FONT, FONT_SMALL),
            bg=HEADER_BG,
            fg=HEADER_SUB,
            anchor="w",
            padx=20,
            pady=8,
        ).pack(fill="x")

    # ── List rendering ────────────────────────────────────────────────────────

    def _render_lista(self) -> None:
        """
        Clears the scrollable list and repopulates it from ``self.pdf_links``.

        Each row contains a Checkbutton (pre-checked) and a Label showing the
        PDF title. Rows alternate background colour for readability.
        External links are tagged with ``[Link esterno]``.
        """
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()

        for i, item in enumerate(self.pdf_links):
            var = tk.BooleanVar(value=True)
            self.check_vars.append(var)

            row_bg = SURFACE if i % 2 == 0 else BG_ALT
            row = tk.Frame(self.scroll_frame, bg=row_bg)
            row.pack(fill="x")

            tk.Checkbutton(
                row,
                variable=var,
                bg=row_bg,
                fg=TEXT,
                selectcolor=row_bg,
                activebackground=row_bg,
                activeforeground=TEXT,
                relief="flat",
                highlightthickness=0,
            ).pack(side="left", padx=(10, 2), pady=8)

            tag = "  [Link esterno]" if item.get("external") else ""
            tk.Label(
                row,
                text=item["label"] + tag,
                font=(FONT, FONT_SIZE),
                bg=row_bg,
                fg=TEXT,
                anchor="w",
                justify="left",
                wraplength=720,
            ).pack(side="left", fill="x", expand=True, pady=8, padx=4)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_sfoglia(self) -> None:
        """
        Opens a native directory chooser dialog and updates ``dest_dir``
        with the selected path. Does nothing if the user cancels.
        """
        directory = filedialog.askdirectory(title="Scegli cartella di destinazione")
        if directory:
            self.dest_dir.set(directory)

    def _on_select_all(self) -> None:
        """Sets all PDF checkboxes to True (selected)."""
        for var in self.check_vars:
            var.set(True)

    def _on_deselect_all(self) -> None:
        """Sets all PDF checkboxes to False (deselected)."""
        for var in self.check_vars:
            var.set(False)

    def _on_carica(self) -> None:
        """
        Reads the selected course from the combobox, resolves its URL from
        CORSI (courses.py), and starts a background thread to scrape PDF links.
        Shows an error dialog if the course key is not found in CORSI.
        """
        corso = self.corso_var.get()
        url = CORSI.get(corso)
        if not url:
            messagebox.showerror("Errore", "Corso non trovato nella configurazione.")
            return
        self._set_status(f"Caricamento orari per {corso}...")
        self.update_idletasks()
        threading.Thread(target=self._thread_carica, args=(url,), daemon=True).start()

    def _on_aggiungi_link(self) -> None:
        """
        Validates the external URL and label entered by the user and, if valid,
        appends the entry to ``self.pdf_links`` and refreshes the list.

        Validation rules:
        - URL field must not be empty.
        - URL must start with ``http://`` or ``https://``.
        - URL must not end with ``.pdf.pdf``.
        """
        url = self.ext_url_var.get().strip()
        label = self.ext_label_var.get().strip()

        if not url:
            messagebox.showwarning("Campo vuoto", "Inserisci un URL.")
            return
        if not url.lower().startswith("http"):
            messagebox.showwarning("URL non valido", "L'URL deve iniziare con http:// o https://")
            return
        if url.lower().endswith(".pdf.pdf"):
            messagebox.showwarning(
                "File non valido", "Il link termina con .pdf.pdf — file non valido."
            )
            return

        if not label:
            label = os.path.basename(url.split("?")[0]) or "PDF esterno"
        label = _strip_pdf_ext(label)

        self.pdf_links.append({"label": label, "url": url, "external": True})
        self._render_lista()
        self.ext_url_var.set("")
        self.ext_label_var.set("")
        self._set_status(f"Link esterno aggiunto: {label}")

    def _on_scarica(self) -> None:
        """
        Collects the selected PDF entries, creates the PDF/ and (optionally)
        PPTX/ subdirectories inside the destination folder, and starts the
        download thread. Shows an info dialog if nothing is selected.
        """
        selected = [self.pdf_links[i] for i, var in enumerate(self.check_vars) if var.get()]
        if not selected:
            messagebox.showinfo("Niente da scaricare", "Seleziona almeno un PDF dalla lista.")
            return

        dest = self.dest_dir.get()
        do_convert = self.convert_var.get()
        pdf_dir = os.path.join(dest, "PDF")
        pptx_dir = os.path.join(dest, "PPTX")

        os.makedirs(pdf_dir, exist_ok=True)
        if do_convert:
            os.makedirs(pptx_dir, exist_ok=True)

        self._set_status(f"Download in corso... (0/{len(selected)})")
        self.progress["maximum"] = len(selected)
        self.progress["value"] = 0

        threading.Thread(
            target=self._thread_scarica,
            args=(selected, pdf_dir, pptx_dir, do_convert),
            daemon=True,
        ).start()

    # ── Background threads ────────────────────────────────────────────────────

    def _thread_carica(self, url: str) -> None:
        """
        Background thread: calls scrape_pdf_links and schedules
        ``_on_links_caricati`` on the main thread with the results.

        @param url: Timetable page URL to scrape.
        """
        try:
            links = scrape_pdf_links(url)
            self.after(0, self._on_links_caricati, links)
        except Exception as exc:
            self.after(0, self._set_status, f"Errore caricamento: {exc}")

    def _thread_scarica(
        self, items: list[dict], pdf_dir: str, pptx_dir: str, do_convert: bool
    ) -> None:
        """
        Background thread: downloads each selected PDF to ``pdf_dir`` and,
        if ``do_convert`` is True, converts it to PPTX in ``pptx_dir``.

        Progress and status updates are scheduled on the main thread via
        ``after()`` after every file. The final summary is delivered through
        ``_on_download_done``.

        @param items:      List of PDF entry dicts (keys: ``label``, ``url``).
        @param pdf_dir:    Destination directory for downloaded PDF files.
        @param pptx_dir:   Destination directory for converted PPTX files.
        @param do_convert: Whether to run PDF-to-PPTX conversion after download.
        """
        ok = err = conv_ok = conv_err = 0

        for i, item in enumerate(items):
            try:
                url = item["url"].strip()
                if url.lower().endswith(".pdf.pdf"):
                    err += 1
                    continue

                response = requests.get(
                    url, timeout=REQUEST_TIMEOUT, headers={"User-Agent": USER_AGENT}
                )
                response.raise_for_status()

                label = _strip_pdf_ext(item["label"])
                filename = _sanitize_filename(label) + ".pdf"
                filepath = _unique_path(pdf_dir, filename)

                with open(filepath, "wb") as f:
                    f.write(response.content)
                ok += 1

                if do_convert:
                    self.after(0, self._set_status, f"Conversione: {os.path.basename(filepath)}...")
                    pptx_path = _unique_path(pptx_dir, _sanitize_filename(label) + ".pptx")
                    if pdf_to_pptx(filepath, pptx_path):
                        conv_ok += 1
                    else:
                        conv_err += 1

            except Exception:
                err += 1

            self.after(0, self._update_progress, i + 1, len(items), ok, err)

        self.after(
            0, self._on_download_done, ok, err, conv_ok, conv_err, pdf_dir, pptx_dir, do_convert
        )

    # ── Main-thread callbacks ─────────────────────────────────────────────────

    def _on_links_caricati(self, links: list[dict]) -> None:
        """
        Main-thread callback: updates the PDF list after a successful scrape.
        Displays a placeholder message if no links were found.

        @param links: List of PDF dicts returned by scrape_pdf_links.
        """
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.check_vars.clear()
        self.pdf_links.clear()

        if not links:
            self._label(
                self.scroll_frame, "Nessun PDF trovato per questo corso.", dim=True, bg=SURFACE
            ).pack(pady=20)
            self._set_status("Nessun PDF trovato.")
            return

        self.pdf_links = list(links)
        self._render_lista()
        self._set_status(f"Trovati {len(links)} PDF. Seleziona quelli da scaricare.")

    def _update_progress(self, current: int, total: int, ok: int, err: int) -> None:
        """
        Main-thread callback: advances the progress bar and updates the
        status label during a download operation.

        @param current: Number of files processed so far (success + error).
        @param total:   Total number of files to process.
        @param ok:      Number of files successfully downloaded.
        @param err:     Number of files that failed.
        """
        self.progress["value"] = current
        self._set_status(f"Download: {current}/{total}   OK: {ok}   Errori: {err}")

    def _on_download_done(
        self,
        ok: int,
        err: int,
        conv_ok: int,
        conv_err: int,
        pdf_dir: str,
        pptx_dir: str,
        do_convert: bool,
    ) -> None:
        """
        Main-thread callback: resets the progress bar, shows a summary dialog,
        updates the status label, and opens the root output folder.

        @param ok:         Number of PDFs downloaded successfully.
        @param err:        Number of PDFs that failed to download.
        @param conv_ok:    Number of PDFs successfully converted to PPTX.
        @param conv_err:   Number of conversions that failed.
        @param pdf_dir:    Path where PDFs were saved.
        @param pptx_dir:   Path where PPTX files were saved.
        @param do_convert: Whether conversion was enabled for this run.
        """
        self.progress["value"] = 0

        lines = [f"Download completato!\n{ok} PDF salvati in: {pdf_dir}"]
        if err:
            lines.append(f"{err} file non scaricati")
        if do_convert:
            lines.append(f"\n{conv_ok} PPTX salvati in: {pptx_dir}")
            if conv_err:
                lines.append(f"{conv_err} conversioni fallite")

        messagebox.showinfo("Completato", "\n".join(lines))
        self._set_status(
            f"Completato — {ok} PDF, {conv_ok} PPTX"
            if do_convert
            else f"Completato — {ok} PDF scaricati"
        )

        _open_folder(os.path.dirname(pdf_dir))

    def _set_status(self, message: str) -> None:
        """
        Updates the status bar label text.

        @param message: Message string to display.
        """
        self.status_var.set(message)


# ── Module-level private helpers ──────────────────────────────────────────────


def _darken(hex_color: str, factor: float = 0.85) -> str:
    """
    Returns a darkened version of a hex colour string.
    Used to compute the ``pressed`` state colour for button styles.

    @param hex_color: Six-digit hex colour string (with or without ``#``).
    @param factor:    Multiplier applied to each RGB channel (0.0–1.0).
                      Default 0.85 produces an ~15% darker shade.
    @return:          Darkened colour as a ``#rrggbb`` hex string.
    """
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return "#{:02x}{:02x}{:02x}".format(int(r * factor), int(g * factor), int(b * factor))
