# University Timetable Automation

A cross-platform desktop application for downloading university timetable PDFs from web pages and converting them to PowerPoint presentations automatically.

Currently configured for **Università del Molise** (Dipartimento di Bioscienze e Territorio). Adapting it to another university requires editing a single file — see [Adding courses or universities](#adding-courses-or-universities).

---

## Download

Every push to `main` automatically builds the application for all three platforms via GitHub Actions. Download the latest version below:

| Platform    | Download                                                                                                                                                                  |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Windows** | [University_Timetable_Automation.exe](https://github.com/Luxauram/university-timetable-automation.git/releases/latest/download/University_Timetable_Automation.exe)       |
| **macOS**   | [University_Timetable_Automation (macOS)](https://github.com/Luxauram/university-timetable-automation.git/releases/latest/download/University_Timetable_Automation_macOS) |
| **Linux**   | [University_Timetable_Automation (Linux)](https://github.com/Luxauram/university-timetable-automation.git/releases/latest/download/University_Timetable_Automation_Linux) |

> No installation required — just download and run.
> On macOS/Linux you may need to make the file executable first: `chmod +x University_Timetable_Automation`

---

## Features

- Select a course from the dropdown and fetch all available PDF timetables in one click
- Batch download selected PDFs into an organised folder structure
- Automatic PDF → PowerPoint conversion (one slide per page, full resolution)
- Add any external PDF URL manually to include it in the download batch
- Files are saved in separate `PDF/` and `PPTX/` subfolders

---

## Project structure

```
├── main.py          # Entry point
├── courses.py       # Course list and URLs — edit this to add courses
├── config.py        # Colours, fonts, window size, network settings
├── scraper.py       # Web scraping logic
├── converter.py     # PDF → PPTX conversion
├── gui.py           # Tkinter GUI
├── requirements.txt # Python dependencies
├── build_exe.bat    # Windows build script (manual alternative to CI)
├── .github/
│   └── workflows/
│       └── build.yml  # GitHub Actions — builds for Windows, macOS and Linux
└── .gitignore
```

---

## Running from source

**Requirements:** Python 3.10+, no system dependencies (no Poppler, Ghostscript or ImageMagick needed).

```bash
# 1. Clone the repository
git clone https://github.com/Luxauram/university-timetable-automation.git
cd university-timetable-automation

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate      # macOS / Linux
# venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python3 main.py
```

---

## Adding courses or universities

Open `courses.py` — it is the **only file** you need to change:

```python
CORSI = {
    "MY UNIVERSITY — Bachelor — Course Name": "https://university.edu/timetable-page",
    "MY UNIVERSITY — Master  — Course Name":  "https://university.edu/timetable-page",
}
```

If your university hosts PDFs on a different backend, also update `BASE_STRAPI` in the same file.

> The scraper works with any page that uses the ReadSpeaker docreader pattern to embed PDF links. If your university uses a different pattern, `scraper.py` is the place to adapt.

---

## Automated builds

The repository includes a GitHub Actions workflow (`.github/workflows/build.yml`) that builds the application for **Windows, macOS and Linux** automatically on every push to `main`. You can also trigger it manually from the **Actions** tab on GitHub.

Build artifacts are available for 30 days under the **Actions** tab. To make them permanently available as release downloads, create a GitHub Release and attach the artifacts — the links in the Download table above will resolve automatically.

If you prefer to build manually on Windows, run `build_exe.bat` — it handles dependency installation and PyInstaller compilation in one step.

---

## Contributing

Contributions are welcome and appreciated.

If you want to help — whether it is fixing a bug, adding support for a new university, improving the UI, or anything else — feel free to:

1. **Fork** the repository
2. **Create a branch** (`git checkout -b feature/your-feature`)
3. **Commit** your changes with a clear message
4. **Open a pull request** describing what you changed and why

If you are not sure where to start, open an **Issue** first to discuss the idea. All skill levels are welcome.

---

## Troubleshooting

**No PDFs found after loading a course**
The university page structure may have changed. Check the URL in `courses.py` and confirm the page is reachable in your browser.

**`ModuleNotFoundError` on startup**
Make sure you are inside the virtual environment and have run `pip install -r requirements.txt`.

**PPTX conversion fails**
Try updating pypdfium2: `pip install --upgrade pypdfium2`

**Executable crashes on launch**
Recompile with the `--collect-all pypdfium2` flag. Without it, the PDFium native libraries are not bundled.

---

## License

[MIT](LICENSE) — free to use, modify and distribute.
