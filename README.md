# Offline PDF Reader Guru

<p align="center">
  <img src="docs/banner.png" alt="Sage Banner" width="700"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python" />
  <img src="https://img.shields.io/badge/AI-Ollama%20%7C%20Offline-green?style=flat-square" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?style=flat-square" />
  <img src="https://img.shields.io/badge/License-MIT-orange?style=flat-square" />
  <img src="https://img.shields.io/badge/Built%20for-Google%20CodeFest-red?style=flat-square&logo=google" />
</p>

> **Every expert wrote a book. Not everyone can afford a tutor.**
> Sage sits beside you as you read — simplifying every page in plain language, privately, with zero internet required.

---

## 🎯 The Problem

Technical books like *Designing Machine Learning Systems*, *Clean Code*, or *The Pragmatics of Programming* are written by experts — for experts. Beginners buy these books and hit a wall on page 10. They can't afford tutors. Online explanations are scattered and shallow.

**Sage solves this.** Open any PDF. Hit one button. Get a clear, faithful explanation of exactly what you're reading — powered by a local LLM running entirely on your machine.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 **Built-in PDF Reader** | Smooth rendering, page navigation, zoom |
| 🧠 **AI Page Simplifier** | Explains current page in plain English without losing meaning |
| 🔒 **100% Offline** | Powered by Ollama — your data never leaves your machine |
| 🤖 **Model Switcher** | Use llama3, mistral, phi3, or any Ollama model |
| 🪟 **Windows + Linux** | One codebase, both platforms |
| ⌨️ **Keyboard First** | Arrow keys to navigate, Space to explain |
| 📝 **Explanation History** | Every page explanation saved in session |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│                  Sage App                   │
│                                             │
│  ┌──────────────┐    ┌────────────────────┐ │
│  │  PDF Viewer  │    │   AI Sidebar       │ │
│  │  (PyQt6 +    │───▶│   (Ollama SDK +    │ │
│  │   PyMuPDF)   │    │    Streaming)      │ │
│  └──────────────┘    └────────────────────┘ │
│         │                     │             │
│  ┌──────▼─────────────────────▼──────────┐  │
│  │         Core Engine                   │  │
│  │  pdf_reader · extractor · ai_engine   │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
         │
         ▼
  Ollama (localhost:11434)
  llama3 / mistral / phi3 — running locally
```

---

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.10+
python --version

# Install Ollama — https://ollama.com/download
# Then pull a model:
ollama pull mistral
```

### 2. Install Sage

```bash
git clone https://github.com/Harish141296/offline_pdfreader_guru.git
cd offline_pdfreader_guru

pip install -r requirements.txt
```

### 3. Run

```bash
# Start Ollama first
ollama serve

# Then in a new terminal:
python main.py
```

---

## 🎮 Usage

1. Click **Open PDF** or drag a PDF onto the window
2. Navigate pages with `←` `→` arrow keys
3. Press `Space` or click **Explain This Page**
4. Watch Sage simplify the content in real time

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| GUI | PyQt6 | Cross-platform desktop UI |
| PDF | PyMuPDF (fitz) | Fast PDF rendering + text extraction |
| AI | Ollama Python SDK | Local LLM inference, streaming |
| Packaging | PyInstaller | Single executable for distribution |
| Testing | pytest | Unit tests for core modules |

---

## 📦 Build Executable

```bash
# Windows
scripts\build_windows.bat

# Linux
bash scripts/build_linux.sh
```

Output: `dist/sage.exe` (Windows) or `dist/sage` (Linux)

---

## 🗂️ Project Structure

```
sage/
├── main.py                  # Entry point
├── requirements.txt
├── sage/
│   ├── core/
│   │   ├── pdf_reader.py    # PyMuPDF wrapper
│   │   ├── extractor.py     # Text extraction
│   │   ├── ai_engine.py     # Ollama integration
│   │   └── prompt_templates.py
│   ├── ui/
│   │   ├── main_window.py   # App window
│   │   ├── viewer.py        # PDF viewer panel
│   │   ├── sidebar.py       # AI explanation panel
│   │   ├── settings.py      # Model picker
│   │   └── theme.py         # Dark theme constants
│   └── assets/
├── tests/
├── docs/
└── scripts/
```

---

## 🤝 Contributing

Pull requests welcome. For major changes, open an issue first.

---

## 📄 License

MIT — free to use, modify, and distribute.

---

<p align="center">Built with ❤️ for Google CodeFest · <a href="https://github.com/Harish141296/offline_pdfreader_guru">github.com/Harish141296/offline_pdfreader_guru</a></p>
