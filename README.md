# AudioVal 🎵

[![CI](https://github.com/cumulus13/audioval/actions/workflows/ci.yml/badge.svg)](https://github.com/cumulus13/audioval/actions)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AudioVal** is an advanced, high-performance CLI tool built for audiophiles, DJs, and archivists. It deeply scans massive music libraries to detect corrupted audio headers, broken files, and metadata tags that are completely empty or filled with blank spaces.

Powered by `mutagen` for robust audio parsing and `rich` for a beautiful, responsive terminal UI.

---

## 🚀 Features

*   **Corrupt Header Detection:** Natively catches sync errors, broken frames, and corrupted files using Mutagen.
*   **Deep Tag Validation:** Iterates through metadata dictionaries to ensure tags actually contain text, catching fields padded with empty spaces.
*   **Blazing Fast Concurrency:** Uses thread-pooling to process thousands of files simultaneously.
*   **Beautiful Terminal UI:** Live progress bars, color-coded summaries, and emoji-tagged alerts.
*   **CI/CD Ready:** Standardized exit codes (`0` for success, `1` for errors) allow for easy pipeline integration.

## 📦 Installation

### with pip

```bash
pip install audioval
```

### from source (dev mode)

To install this package for global use on your system:

```bash
git clone [https://github.com/cumulus13/audioval.git](https://github.com/cumulus13/audioval.git)
cd audioval
pip install -e .

```

## 💻 Usage

Once installed, the `audioval` command is available globally in your terminal.

**Basic Scan (Defaults to 4 workers, common audio formats):**

```bash
audioval -d /path/to/your/music

```

**Custom Extensions and High Concurrency:**
If you are scanning a massive NAS drive over a network and strictly want to check `.flac` and `.ogg` files using 8 parallel threads:

```bash
audioval --dir /Volumes/NAS/Music --ext flac ogg --workers 8

```

**Available Options:**

* `-d, --dir`: Target directory to scan (Required)
* `-e, --ext`: Space-separated list of extensions to scan (Default: `.mp3 .flac .m4a .ogg .wav .wma`)
* `-w, --workers`: Number of concurrent threads (Default: 4)

## 🛠️ Development & Testing

This project uses `pytest` for unit testing and `flake8` for linting.

```bash
# Install development dependencies including test coverage
pip install flake8 pytest pytest-cov build

# Run unit tests with a coverage report
pytest tests/ -v --cov=audioval --cov-report=term-missing

# Run linter
flake8 audioval

```

## 📄 License

[MIT](LICENSE)

---

## 👤 Author
        
[Hadi Cahyadi](mailto:cumulus13@gmail.com)
    

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/cumulus13)

[![Donate via Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/cumulus13)
 
[Support me on Patreon](https://www.patreon.com/cumulus13)

