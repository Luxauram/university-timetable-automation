# University Timetable Automation

A cross-platform desktop application for downloading university timetable PDFs from web pages and converting them to PowerPoint presentations automatically.

Currently configured for **Università del Molise** (Dipartimento di Bioscienze e Territorio). Adapting it to another university requires editing a single file — see [Adding courses or universities](#adding-courses-or-universities).

---

## Download

Every push to `main` automatically builds the application for all three platforms via GitHub Actions. Download the latest version below:

| Platform    | Download                                                                                                                                                                        |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Windows** | [University_Timetable_Automation_Windows.exe](https://github.com/Luxauram/university-timetable-automation/releases/latest/download/University_Timetable_Automation_Windows.exe) |
| **macOS**   | [University_Timetable_Automation_macOS](https://github.com/Luxauram/university-timetable-automation/releases/latest/download/University_Timetable_Automation_macOS)             |
| **Linux**   | [University_Timetable_Automation_Linux](https://github.com/Luxauram/university-timetable-automation/releases/latest/download/University_Timetable_Automation_Linux)             |

> No installation required — just download and run.
> On macOS/Linux make the file executable first: `chmod +x University_Timetable_Automation_macOS`

---

## Features

- Select a course from the dropdown and fetch all available PDF timetables in one click
- Batch download selected PDFs into an organised folder structure (`PDF/` and `PPTX/` subfolders)
- Automatic PDF → PowerPoint conversion (one slide per page, configurable quality)
- Add any external PDF URL manually to include it in the download batch
- **Menu bar** with File, Settings, Updates and About sections
- **Persistent settings** saved per-user (PPTX quality, language, auto-open folder)
- **Bilingual UI** — switch between Italian and English in Settings without restarting the app
- **Update checker** — checks GitHub Releases for newer versions directly from the app
- **About dialog** showing version, author, license and a link to the repository

---

## Project structure

```
├── main.py          # Entry point with icon loading
├── courses.py       # Course list and URLs — edit this to add courses
├── config.py        # App version, colours, fonts, window size, network settings
├── settings.py      # Persistent user preferences (JSON, OS-appropriate path)
├── i18n.py          # Bilingual string registry (Italian / English)
├── scraper.py       # Web scraping logic (ReadSpeaker docreader pattern)
├── converter.py     # PDF → PPTX conversion via pypdfium2
├── gui.py           # Tkinter GUI with menu bar and settings dialog
├── requirements.txt # Python dependencies
├── build_exe.bat    # Windows build script (manual alternative to CI)
├── icon.png         # Application icon (256×256 PNG)
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

## Settings

Open **Settings** from the menu bar to configure:

| Setting                       | Description                                                  |
| ----------------------------- | ------------------------------------------------------------ |
| PPTX conversion on by default | Pre-check the conversion checkbox at startup                 |
| Open folder after download    | Automatically open the output folder when done               |
| PPTX quality                  | Low (72 DPI, fast) / Medium (150 DPI) / High (300 DPI, slow) |
| Language                      | Italian / English — applied instantly without restarting     |

Settings are stored in the OS-appropriate user directory:

- **Windows:** `%APPDATA%\UniversityTimetableAutomation\settings.json`
- **macOS:** `~/Library/Application Support/UniversityTimetableAutomation/settings.json`
- **Linux:** `~/.config/UniversityTimetableAutomation/settings.json`

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

The repository includes a GitHub Actions workflow (`.github/workflows/build.yml`) that builds the application for **Windows, macOS and Linux** automatically on every push to `main`. The release tag is read directly from `APP_VERSION` in `config.py` — so bumping the version and pushing is all that is needed to publish a new versioned release. You can also trigger builds manually from the **Actions** tab on GitHub.

If you prefer to build manually on Windows, run `build_exe.bat` — it handles dependency installation and PyInstaller compilation in one step.

---

## Contributing

Contributions are welcome and appreciated.

If you want to help — whether it is fixing a bug, adding support for a new university, improving the UI, or anything else — feel free to:

1. **Fork** the repository
2. **Create a branch**
3. **Commit** your changes with a clear message
4. **Open a pull request** describing what you changed and why

If you are not sure where to start, open an **Issue** first to discuss the idea. All skill levels are welcome.

---

## License

[MIT](LICENSE) — free to use, modify and distribute.
