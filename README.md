# 📄 Smart PDF Search Engine

A powerful, locally-hosted web application that lets you **upload PDF documents** and **search for keywords** within them — with full support for **scanned/image-based PDFs** via OCR.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Instant Text Search** — Upload a PDF and search for any keyword across all pages with highlighted snippets.
- **OCR for Scanned PDFs** — Automatically detects image-only pages and runs Tesseract OCR in parallel for fast processing.
- **Real-Time Progress Bar** — Background OCR processing with a live progress indicator so you're never left waiting blindly.
- **Smart Caching** — Extracted text is cached as JSON, making repeated searches instant.
- **Dark & Light Themes** — A sleek, modern UI with a toggle between dark and light modes.
- **50 MB Upload Limit** — Handles large PDF files with graceful error handling.
- **Safe Re-Upload** — Re-uploading a new file automatically cancels any running OCR tasks.
- **Privacy-First** — Everything runs locally on your machine. No data leaves your computer.

---

## 🛠️ Tech Stack

| Layer       | Technology                                                                 |
|-------------|----------------------------------------------------------------------------|
| **Backend** | [Flask](https://flask.palletsprojects.com/) (Python)                       |
| **PDF Parsing** | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) — native text extraction |
| **OCR**     | [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) via [pytesseract](https://pypi.org/project/pytesseract/) |
| **Frontend**| HTML, CSS, JavaScript, [Bootstrap 5](https://getbootstrap.com/)            |
| **Fonts**   | [Inter](https://fonts.google.com/specimen/Inter) (Google Fonts)            |

---

## 📁 Project Structure

```
project/
├── app.py              # Flask application (routes, OCR logic, search)
├── templates/
│   └── index.html      # Single-page UI (upload, search, results, docs)
├── static/             # Static assets (currently empty)
├── uploads/            # Uploaded PDF files (git-ignored)
├── cache/              # Cached JSON text extractions (git-ignored)
├── venv/               # Python virtual environment (git-ignored)
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Tesseract OCR** installed on your system

#### Install Tesseract

- **Windows**: Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and install to `C:\Program Files\Tesseract-OCR\`.
- **macOS**: `brew install tesseract`
- **Linux (Debian/Ubuntu)**: `sudo apt install tesseract-ocr`

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd project
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask PyMuPDF pytesseract Pillow markupsafe werkzeug
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in your browser**
   ```
   http://127.0.0.1:5000
   ```

---

## 📖 Usage

1. **Upload** a PDF file using the upload section on the home page.
2. If the PDF contains **scanned pages**, OCR processing starts automatically in the background with a progress bar.
3. Once processing is complete, **enter a keyword** in the search bar and hit Search.
4. Results are displayed with **highlighted snippets** showing the keyword in context, along with the page number.
5. Use the **Clear All** button to remove uploaded files and cached data.

---

## ⚙️ Configuration

| Setting               | Default               | Location     | Description                          |
|-----------------------|-----------------------|--------------|--------------------------------------|
| `MAX_CONTENT_LENGTH`  | 50 MB                 | `app.py`     | Maximum upload file size             |
| `SNIPPET_RADIUS`      | 300 characters        | `app.py`     | Context around keyword in snippets   |
| `OCR_DPI`             | 150                   | `app.py`     | Resolution for rendering scanned pages |
| `MAX_RESULT_STORE`    | 50                    | `app.py`     | Max server-side stored result sets   |
| `SECRET_KEY`          | Random / env variable | `app.py`     | Flask session secret key             |

---

## 🧩 How It Works

```
PDF Upload
    │
    ▼
┌──────────────────────┐
│  PyMuPDF Text Check  │  ← Checks each page for native text
└──────────┬───────────┘
           │
     ┌─────┴─────┐
     │            │
  Has Text    Image-Only
     │            │
     ▼            ▼
  Cache JSON   Background OCR (Tesseract)
     │            │  ← Parallel, with progress tracking
     │            ▼
     │        Cache JSON
     │            │
     └─────┬──────┘
           │
           ▼
     Keyword Search
           │
           ▼
     Highlighted Snippets
```

---

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

---

> Built with ❤️ using Flask, PyMuPDF, and Tesseract OCR.
