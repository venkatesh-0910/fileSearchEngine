"""
Smart PDF Search Engine
========================
Text is extracted at upload time using PyMuPDF (native text only).
Scanned/image-only pages are skipped (no OCR).
Searches are instant via cached JSON.
Every page refresh starts completely fresh.
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
from werkzeug.utils import secure_filename
from markupsafe import escape
import os
import re
import json
import fitz  # PyMuPDF

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

UPLOAD_FOLDER = "uploads"
CACHE_FOLDER = "cache"
ALLOWED_EXTENSIONS = {".pdf", ".png"}
SNIPPET_RADIUS = 300

for folder in (UPLOAD_FOLDER, CACHE_FOLDER):
    os.makedirs(folder, exist_ok=True)


def clear_all_files():
    """Remove all uploaded PDFs and cached JSON files."""
    for f in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, f)
        try:
            os.remove(filepath)
        except Exception:
            pass
    for f in os.listdir(CACHE_FOLDER):
        filepath = os.path.join(CACHE_FOLDER, f)
        try:
            os.remove(filepath)
        except Exception:
            pass


# Clean up on startup
clear_all_files()


def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS


def no_cache_response(response):
    """Add no-cache headers to prevent browser from caching pages."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# ──────────────────────────────────────────────────────────────
# TEXT EXTRACTION (PyMuPDF native text only — instant)
# ──────────────────────────────────────────────────────────────

def extract_and_cache(filepath: str, filename: str) -> None:
    """
    Open PDF, extract native text from all pages, save to JSON cache.
    Scanned/image-only pages are skipped (no OCR).
    """
    pages = []
    skipped = 0

    with fitz.open(filepath) as doc:
        total_pages = len(doc)
        for i in range(total_pages):
            page = doc.load_page(i)
            text = page.get_text()

            if text.strip():
                pages.append({"page": i + 1, "text": text})
            else:
                skipped += 1

    cache_path = os.path.join(CACHE_FOLDER, f"{filename}.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(
            {"filename": filename, "pages": pages},
            f,
            ensure_ascii=False,
        )

    return total_pages, len(pages), skipped


# ──────────────────────────────────────────────────────────────
# SNIPPETS
# ──────────────────────────────────────────────────────────────

def build_snippet(text, keyword, radius=SNIPPET_RADIUS):
    """
    Extract a snippet of text around the keyword match,
    with radius characters of context on each side.
    """
    match = re.search(re.escape(keyword), text, re.IGNORECASE)
    if not match:
        return ""

    start = max(0, match.start() - radius)
    end = min(len(text), match.end() + radius)
    snippet = text[start:end]

    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""

    safe_snippet = str(escape(snippet))
    escaped_kw = str(escape(keyword))
    highlighted = re.sub(
        re.escape(escaped_kw),
        f"<mark>{escaped_kw}</mark>",
        safe_snippet,
        flags=re.IGNORECASE,
    )
    return prefix + highlighted.replace("\n", "<br>") + suffix


# ──────────────────────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """
    Home page.
    Always clears everything on a fresh GET request.
    Only shows data when redirected from upload/search via POST-redirect.
    """
    results = session.pop("results", None)
    keyword = session.pop("keyword", None)
    uploaded_file = session.pop("uploaded_file", None)

    if not uploaded_file:
        clear_all_files()
        uploaded_files = []
        cached_files = []
    else:
        uploaded_files = [uploaded_file]
        cached_files = [uploaded_file]

    response = make_response(
        render_template(
            "index.html",
            uploaded_files=uploaded_files,
            cached_files=cached_files,
            results=results,
            keyword=keyword,
            active_task_id=None,
        )
    )
    return no_cache_response(response)


@app.route("/upload", methods=["POST"])
def upload():
    """Handle PDF upload and extract text instantly."""
    file = request.files.get("file")

    if not file or file.filename == "":
        flash("Please select a file to upload.", "danger")
        return redirect(url_for("index"))

    if not allowed_file(file.filename):
        flash("Only PDF files are allowed.", "danger")
        return redirect(url_for("index"))

    clear_all_files()

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        total_pages, indexed, skipped = extract_and_cache(filepath, filename)

        if skipped > 0:
            flash(
                f"'{filename}' uploaded! {indexed} of {total_pages} pages indexed. "
                f"{skipped} scanned page(s) were skipped (text-based PDFs only).",
                "success",
            )
        else:
            flash(
                f"'{filename}' uploaded and indexed successfully! "
                f"All {total_pages} pages indexed.",
                "success",
            )
        session["uploaded_file"] = filename

    except Exception as e:
        flash(f"Upload OK but text extraction failed: {e}", "danger")

    return redirect(url_for("index"))


@app.route("/search", methods=["POST"])
def search():
    """Search cached JSON files for keyword matches."""
    keyword = request.form.get("keyword", "").strip()
    results = []

    if not keyword:
        flash("Please enter a keyword to search.", "warning")
        uploaded_files = [
            f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(".pdf")
        ]
        if uploaded_files:
            session["uploaded_file"] = uploaded_files[0]
        return redirect(url_for("index"))

    keyword_lower = keyword.lower()

    cache_files = [f for f in os.listdir(CACHE_FOLDER) if f.endswith(".json")]
    if not cache_files:
        flash("No PDF uploaded yet. Please upload a PDF first.", "warning")
        return redirect(url_for("index"))

    current_uploaded = None

    for cache_file in cache_files:
        cache_path = os.path.join(CACHE_FOLDER, cache_file)
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        current_uploaded = data["filename"]

        for page_info in data["pages"]:
            text = page_info["text"]
            if keyword_lower in text.lower():
                snippet = build_snippet(text, keyword)
                results.append({
                    "filename": data["filename"],
                    "page": page_info["page"],
                    "text": snippet,
                })

    if not results:
        flash(f"No results found for '{keyword}'.", "info")

    session["results"] = results
    session["keyword"] = keyword
    if current_uploaded:
        session["uploaded_file"] = current_uploaded

    return redirect(url_for("index"))


@app.route("/clear", methods=["POST"])
def clear():
    """Delete all uploaded PDFs and cached data."""
    clear_all_files()
    session.clear()
    flash("All files cleared.", "info")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)