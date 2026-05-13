"""
guru/ui/theme.py

Dark theme — single source of truth for every color, font, and spacing value.
Change it here, it changes everywhere.

Design language: editorial dark — like a premium reading app.
Inspired by iA Writer, Instapaper, and Bear Notes.
"""

# ── Color palette ──────────────────────────────────────────────
BG_DEEP     = "#0e0f11"   # App background
BG_SURFACE  = "#16181c"   # Panels, sidebars
BG_PANEL    = "#1d2025"   # Cards, input areas
BORDER      = "#2a2d35"   # Dividers, card borders
BORDER_SOFT = "#222530"   # Subtle separators

ACCENT      = "#c8a96e"   # Gold — primary action color
ACCENT_DIM  = "#a08750"   # Hover states
ACCENT2     = "#7eb8a4"   # Teal — status OK / success
DANGER      = "#c06060"   # Errors
WARNING     = "#d4a64a"   # Warnings

TEXT_PRIMARY   = "#e8e4dc"  # Main readable text
TEXT_SECONDARY = "#9da0aa"  # Labels, subtitles
TEXT_DIM       = "#55585f"  # Placeholders, hints
TEXT_CODE      = "#7eb8a4"  # Inline code, mono text

# ── Typography ─────────────────────────────────────────────────
FONT_BODY   = "Georgia"        # Readable serif for explanations
FONT_UI     = "Segoe UI"       # Windows-native sans for UI
FONT_MONO   = "Consolas"       # Monospace for model names, paths

FONT_SIZE_BODY  = 14
FONT_SIZE_UI    = 13
FONT_SIZE_SMALL = 11
FONT_SIZE_LARGE = 16
FONT_SIZE_TITLE = 20

# ── Spacing ────────────────────────────────────────────────────
RADIUS      = 10   # Border radius for cards
RADIUS_SM   = 6    # Smaller radius for badges, inputs
PADDING     = 16   # Standard inner padding
PADDING_LG  = 24   # Large padding for panels

# ── Full app stylesheet (Qt CSS) ───────────────────────────────
STYLESHEET = f"""
/* ── Global ── */
QWidget {{
    background-color: {BG_DEEP};
    color: {TEXT_PRIMARY};
    font-family: "{FONT_UI}";
    font-size: {FONT_SIZE_UI}px;
    border: none;
    outline: none;
}}

/* ── Main window ── */
QMainWindow {{
    background-color: {BG_DEEP};
}}

/* ── Toolbar / header ── */
QToolBar {{
    background-color: {BG_SURFACE};
    border-bottom: 1px solid {BORDER};
    padding: 4px 12px;
    spacing: 6px;
}}
QToolBar QLabel {{
    color: {TEXT_SECONDARY};
    font-size: {FONT_SIZE_SMALL}px;
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 6px 14px;
    font-size: {FONT_SIZE_UI}px;
}}
QPushButton:hover {{
    background-color: {BORDER};
    border-color: {BORDER_SOFT};
}}
QPushButton:pressed {{
    background-color: {BG_DEEP};
}}
QPushButton:disabled {{
    color: {TEXT_DIM};
    border-color: {BG_PANEL};
}}

/* Primary action button (Explain This Page) */
QPushButton#explainBtn {{
    background-color: transparent;
    color: {ACCENT};
    border: 1px solid {ACCENT_DIM};
    font-size: {FONT_SIZE_UI}px;
    font-weight: bold;
    padding: 8px 18px;
    border-radius: {RADIUS_SM}px;
}}
QPushButton#explainBtn:hover {{
    background-color: rgba(200,169,110,0.08);
    border-color: {ACCENT};
}}
QPushButton#explainBtn:disabled {{
    color: {TEXT_DIM};
    border-color: {BORDER};
}}

/* Open PDF button */
QPushButton#openBtn {{
    background-color: {ACCENT};
    color: #1a1500;
    border: none;
    font-weight: bold;
    padding: 6px 16px;
    border-radius: {RADIUS_SM}px;
}}
QPushButton#openBtn:hover {{
    background-color: {ACCENT_DIM};
}}

/* Nav / zoom buttons */
QPushButton#navBtn {{
    background-color: transparent;
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 4px 10px;
    min-width: 32px;
}}
QPushButton#navBtn:hover {{
    background-color: {BG_PANEL};
}}

/* ── Labels ── */
QLabel {{
    color: {TEXT_PRIMARY};
    background: transparent;
}}
QLabel#pageLabel {{
    color: {TEXT_SECONDARY};
    font-size: {FONT_SIZE_SMALL}px;
    font-family: "{FONT_MONO}";
}}
QLabel#statusLabel {{
    color: {TEXT_DIM};
    font-size: {FONT_SIZE_SMALL}px;
    font-family: "{FONT_MONO}";
}}
QLabel#logoLabel {{
    color: {ACCENT};
    font-size: {FONT_SIZE_TITLE}px;
    font-family: Georgia, serif;
}}
QLabel#sectionLabel {{
    color: {TEXT_DIM};
    font-size: {FONT_SIZE_SMALL}px;
    letter-spacing: 1px;
}}

/* ── ScrollArea (PDF viewer) ── */
QScrollArea {{
    background-color: {BG_DEEP};
    border: none;
}}
QScrollBar:vertical {{
    background: {BG_DEEP};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_DIM};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {BG_DEEP};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
    min-width: 20px;
}}

/* ── Sidebar ── */
QFrame#sidebar {{
    background-color: {BG_SURFACE};
    border-left: 1px solid {BORDER};
}}

/* ── Explanation text area ── */
QTextEdit#explanationText {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    font-family: Georgia, serif;
    font-size: {FONT_SIZE_BODY}px;
    line-height: 1.8;
    border: 1px solid {BORDER};
    border-radius: {RADIUS}px;
    padding: 14px;
    selection-background-color: rgba(200,169,110,0.25);
}}

/* ── ComboBox (model picker) ── */
QComboBox {{
    background-color: {BG_PANEL};
    color: {TEXT_SECONDARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 4px 10px;
    font-family: "{FONT_MONO}";
    font-size: {FONT_SIZE_SMALL}px;
}}
QComboBox:hover {{
    border-color: {TEXT_DIM};
}}
QComboBox::drop-down {{
    border: none;
    width: 20px;
}}
QComboBox QAbstractItemView {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    selection-background-color: rgba(200,169,110,0.15);
}}

/* ── LineEdit (ask question) ── */
QLineEdit {{
    background-color: {BG_PANEL};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    padding: 6px 10px;
    font-size: {FONT_SIZE_UI}px;
}}
QLineEdit:focus {{
    border-color: {ACCENT_DIM};
}}
QLineEdit::placeholder {{
    color: {TEXT_DIM};
}}

/* ── Splitter ── */
QSplitter::handle {{
    background-color: {BORDER};
    width: 1px;
}}

/* ── Status bar ── */
QStatusBar {{
    background-color: {BG_SURFACE};
    color: {TEXT_DIM};
    font-size: {FONT_SIZE_SMALL}px;
    font-family: "{FONT_MONO}";
    border-top: 1px solid {BORDER};
}}
"""
