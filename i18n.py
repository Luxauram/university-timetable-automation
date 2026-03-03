"""
i18n.py
=======
Internationalisation string registry for the PDF Timetable Downloader.

All user-visible strings are stored here as nested dicts keyed by language
code (``"it"`` or ``"en"``). The active language is controlled by the
``language`` setting in settings.py.

How to add a new string
-----------------------
1. Add the key under both ``"it"`` and ``"en"``.
2. Reference it in gui.py via ``t("your_key")``.

License: MIT
"""

from __future__ import annotations

_STRINGS: dict[str, dict[str, str]] = {
    # ── Menu bar ──────────────────────────────────────────────────────────────
    "menu_file": {"it": "File", "en": "File"},
    "menu_file_open_folder": {"it": "Apri cartella download", "en": "Open download folder"},
    "menu_file_exit": {"it": "Esci", "en": "Exit"},
    "menu_settings": {"it": "Impostazioni", "en": "Settings"},
    "menu_settings_title": {"it": "Impostazioni", "en": "Settings"},
    "menu_updates": {"it": "Aggiornamenti", "en": "Updates"},
    "menu_updates_check": {"it": "Controlla aggiornamenti", "en": "Check for updates"},
    "menu_info": {"it": "Info", "en": "About"},
    # ── Settings dialog ───────────────────────────────────────────────────────
    "settings_pptx_default": {
        "it": "Conversione PPTX attiva di default",
        "en": "Enable PPTX conversion by default",
    },
    "settings_open_folder": {
        "it": "Apri cartella automaticamente dopo il download",
        "en": "Open folder automatically after download",
    },
    "settings_language": {"it": "Lingua / Language", "en": "Lingua / Language"},
    "settings_quality": {"it": "Qualità conversione PPTX", "en": "PPTX conversion quality"},
    "settings_quality_low": {"it": "Bassa  (72 DPI — veloce)", "en": "Low   (72 DPI — fast)"},
    "settings_quality_medium": {
        "it": "Media  (150 DPI — bilanciata)",
        "en": "Medium (150 DPI — balanced)",
    },
    "settings_quality_high": {"it": "Alta   (300 DPI — lenta)", "en": "High  (300 DPI — slow)"},
    "settings_save": {"it": "Salva", "en": "Save"},
    "settings_cancel": {"it": "Annulla", "en": "Cancel"},
    "settings_saved": {"it": "Impostazioni salvate.", "en": "Settings saved."},
    # ── Info dialog ───────────────────────────────────────────────────────────
    "info_title": {"it": "Info", "en": "About"},
    "info_version": {"it": "Versione", "en": "Version"},
    "info_author": {"it": "Autore principale", "en": "Main author"},
    "info_license": {"it": "Licenza", "en": "License"},
    "info_license_value": {
        "it": "MIT — libero uso, modifica e distribuzione",
        "en": "MIT — free to use, modify and distribute",
    },
    "info_contributions": {
        "it": "Contributi benvenuti! Apri una Issue o una Pull Request.",
        "en": "Contributions welcome! Open an Issue or a Pull Request.",
    },
    "info_open_github": {"it": "Apri su GitHub", "en": "Open on GitHub"},
    # ── Update dialog ─────────────────────────────────────────────────────────
    "update_checking": {
        "it": "Controllo aggiornamenti in corso...",
        "en": "Checking for updates...",
    },
    "update_up_to_date": {
        "it": "Sei già all'ultima versione ({version}).",
        "en": "You are already on the latest version ({version}).",
    },
    "update_available": {
        "it": "Nuova versione disponibile: {latest}\nVersione attuale: {current}",
        "en": "New version available: {latest}\nCurrent version: {current}",
    },
    "update_download": {"it": "Scarica aggiornamento", "en": "Download update"},
    "update_error": {
        "it": "Impossibile controllare gli aggiornamenti.\nVerifica la connessione internet.",
        "en": "Could not check for updates.\nPlease check your internet connection.",
    },
    "update_title": {"it": "Aggiornamenti", "en": "Updates"},
    # ── Main UI ───────────────────────────────────────────────────────────────
    "header_title": {"it": "Orari Lezioni", "en": "Course Timetables"},
    "header_subtitle": {
        "it": "Scarica i PDF degli orari direttamente dal sito universitario",
        "en": "Download timetable PDFs directly from the university website",
    },
    "label_corso": {"it": "Corso di laurea", "en": "Degree course"},
    "btn_carica": {"it": "Carica orari", "en": "Load timetables"},
    "label_salva_in": {"it": "Salva in:", "en": "Save to:"},
    "btn_sfoglia": {"it": "Sfoglia...", "en": "Browse..."},
    "check_convert_pptx": {
        "it": "  Converti automaticamente i PDF in PowerPoint (.pptx)",
        "en": "  Automatically convert PDFs to PowerPoint (.pptx)",
    },
    "card_link_title": {"it": "Aggiungi PDF da link esterno", "en": "Add PDF from external link"},
    "card_link_subtitle": {
        "it": "Incolla un URL diretto a un PDF per aggiungerlo alla lista",
        "en": "Paste a direct PDF URL to add it to the list",
    },
    "label_url": {"it": "URL:", "en": "URL:"},
    "label_nome": {"it": "Nome:", "en": "Name:"},
    "btn_aggiungi": {"it": "Aggiungi", "en": "Add"},
    "card_lista_title": {"it": "PDF disponibili", "en": "Available PDFs"},
    "lista_placeholder": {
        "it": 'Seleziona un corso e premi "Carica orari"',
        "en": 'Select a course and press "Load timetables"',
    },
    "btn_select_all": {"it": "Seleziona tutti", "en": "Select all"},
    "btn_deselect_all": {"it": "Deseleziona tutti", "en": "Deselect all"},
    "btn_scarica": {"it": "⬇   Scarica PDF selezionati", "en": "⬇   Download selected PDFs"},
    "status_ready": {"it": "Pronto.", "en": "Ready."},
    "tag_external": {"it": "  [Link esterno]", "en": "  [External link]"},
    # ── Messages ──────────────────────────────────────────────────────────────
    "msg_no_course": {
        "it": "Corso non trovato nella configurazione.",
        "en": "Course not found in configuration.",
    },
    "msg_loading": {
        "it": "Caricamento orari per {corso}...",
        "en": "Loading timetables for {corso}...",
    },
    "msg_no_pdfs": {
        "it": "Nessun PDF trovato per questo corso.",
        "en": "No PDFs found for this course.",
    },
    "msg_found_pdfs": {
        "it": "Trovati {n} PDF. Seleziona quelli da scaricare.",
        "en": "Found {n} PDFs. Select the ones to download.",
    },
    "msg_empty_url": {"it": "Inserisci un URL.", "en": "Please enter a URL."},
    "msg_invalid_url": {
        "it": "L'URL deve iniziare con http:// o https://",
        "en": "URL must start with http:// or https://",
    },
    "msg_double_pdf": {
        "it": "Il link termina con .pdf.pdf — file non valido.",
        "en": "Link ends with .pdf.pdf — invalid file.",
    },
    "msg_link_added": {
        "it": "Link esterno aggiunto: {label}",
        "en": "External link added: {label}",
    },
    "msg_nothing_selected": {
        "it": "Seleziona almeno un PDF dalla lista.",
        "en": "Please select at least one PDF from the list.",
    },
    "msg_downloading": {"it": "Download in corso... (0/{n})", "en": "Downloading... (0/{n})"},
    "msg_progress": {
        "it": "Download: {current}/{total}   OK: {ok}   Errori: {err}",
        "en": "Download: {current}/{total}   OK: {ok}   Errors: {err}",
    },
    "msg_converting": {"it": "Conversione: {filename}...", "en": "Converting: {filename}..."},
    "msg_done_pdf": {"it": "Completato — {ok} PDF scaricati", "en": "Done — {ok} PDFs downloaded"},
    "msg_done_pptx": {
        "it": "Completato — {ok} PDF, {conv_ok} PPTX",
        "en": "Done — {ok} PDFs, {conv_ok} PPTX",
    },
    "msg_summary_title": {"it": "Completato", "en": "Done"},
    "msg_summary_pdfs": {"it": "{ok} PDF salvati in: {path}", "en": "{ok} PDFs saved to: {path}"},
    "msg_summary_errors": {
        "it": "{err} file non scaricati",
        "en": "{err} files failed to download",
    },
    "msg_summary_pptx": {
        "it": "{conv_ok} PPTX salvati in: {path}",
        "en": "{conv_ok} PPTX saved to: {path}",
    },
    "msg_summary_pptx_errors": {
        "it": "{conv_err} conversioni fallite",
        "en": "{conv_err} conversions failed",
    },
    "msg_load_error": {"it": "Errore caricamento: {err}", "en": "Load error: {err}"},
    # ── Dialog titles ─────────────────────────────────────────────────────────
    "dlg_error": {"it": "Errore", "en": "Error"},
    "dlg_warning": {"it": "Attenzione", "en": "Warning"},
    "dlg_empty_field": {"it": "Campo vuoto", "en": "Empty field"},
    "dlg_invalid_url": {"it": "URL non valido", "en": "Invalid URL"},
    "dlg_invalid_file": {"it": "File non valido", "en": "Invalid file"},
    "dlg_nothing_to_download": {"it": "Niente da scaricare", "en": "Nothing to download"},
    "dlg_browse_title": {
        "it": "Scegli cartella di destinazione",
        "en": "Choose destination folder",
    },
}


def t(key: str, lang: str = "it", **kwargs) -> str:
    """
    Returns the translated string for the given key and language code.

    Supports Python str.format()-style placeholders via keyword arguments::

        t("msg_loading", lang="it", corso="Informatica")
        # → "Caricamento orari per Informatica..."

    Falls back to the Italian string if the key is missing in the requested
    language, and to the raw key string if the key is not found at all.

    @param key:    String identifier defined in _STRINGS.
    @param lang:   Language code: ``"it"`` or ``"en"``.
    @param kwargs: Optional format placeholders.
    @return:       Translated and formatted string.
    """
    entry = _STRINGS.get(key, {})
    text = entry.get(lang) or entry.get("it") or key
    return text.format(**kwargs) if kwargs else text
