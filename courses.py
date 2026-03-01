"""
courses.py
==========
Course registry for the PDF Timetable Downloader.

This is the only file you need to edit to add, remove or rename courses,
or to point the application at a different university entirely.

How to add a course
-------------------
Add a new entry to the CORSI dictionary following this pattern::

    "UNIVERSITY — Degree type — Course name": "https://full-url-to-timetable-page"

The string before the first "—" is purely a visual label in the UI dropdown;
it does not affect scraping behaviour.

How to support a different university
--------------------------------------
1. Change the entries in CORSI to point to your university's timetable pages.
2. If your university uses a different Strapi backend, update BASE_STRAPI.
3. If the timetable pages use a different link pattern than ReadSpeaker
   docreader, you will also need to update the scraping logic in scraper.py.

License: MIT
"""

# Base URL of the Strapi media server used to host the PDF files.
# Change this if your university uses a different backend.
BASE_STRAPI = "https://apistrapi.unimol.it"

# Course registry.
# Format: "Label shown in the UI dropdown": "URL of the timetable page"
CORSI: dict[str, str] = {
    # ── Triennali ─────────────────────────────────────────────────────────────
    "UNIMOL — Triennale — Informatica": (
        "https://www3.unimol.it/dipartimenti/bioscienze-e-territorio/corso/informatica_lezioni"
    ),
    "UNIMOL — Triennale — Scienze Turistiche": (
        "https://www3.unimol.it/dipartimenti/bioscienze-e-territorio/corso/scienze_turistiche_lezioni"
    ),
    "UNIMOL — Triennale — Scienze del Turismo Ambientale": (
        "https://www3.unimol.it/dipartimenti/bioscienze-e-territorio/corso/scienze_del_turismo_ambientale_lezioni"
    ),
    # ── Magistrali ────────────────────────────────────────────────────────────
    "UNIMOL — Magistrale — Management del Turismo e dei Beni Culturali": (
        "https://www3.unimol.it/dipartimenti/bioscienze-e-territorio/corso/management_turismo_beni_culturali_lezioni"
    ),
    "UNIMOL — Magistrale — Progettazione e Gestione dei Sistemi Turistici Patrimoniali": (
        "https://www3.unimol.it/dipartimenti/bioscienze-e-territorio/corso/progettazione_e_gestione_dei_sistemi_turistici_patrimoniali_lezioni"
    ),
}
