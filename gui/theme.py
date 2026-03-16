# gui/theme.py
# Central dark theme — import DARK_THEME and apply once on QApplication

ACCENT = "#4f8ef7"  # blue accent
SUCCESS = "#2ecc71"  # green  (UP)
WARNING = "#f39c12"  # amber  (DEGRADED)
DANGER = "#e74c3c"  # red    (DOWN)
BG_DARK = "#0f1117"  # main window background
BG_CARD = "#1a1d27"  # card / panel background
BG_SIDEBAR = "#12151e"  # sidebar background
BG_INPUT = "#1e2130"  # input fields
BORDER = "#2a2d3e"  # subtle borders
TEXT_PRIMARY = "#e8eaf0"
TEXT_SECONDARY = "#8b90a8"
TEXT_MUTED = "#555976"


def state_color(state: str) -> str:
    return {
        "UP": SUCCESS,
        "DEGRADED": WARNING,
        "DOWN": DANGER,
    }.get(state, TEXT_MUTED)


DARK_THEME = f"""
/* ── Global ── */
QWidget {{
    background-color: {BG_DARK};
    color: {TEXT_PRIMARY};
    font-family: "Segoe UI", "SF Pro Display", Arial, sans-serif;
    font-size: 13px;
}}

QMainWindow {{
    background-color: {BG_DARK};
}}

/* ── Scroll bars ── */
QScrollBar:vertical {{
    background: {BG_CARD};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
QScrollBar:horizontal {{ height: 6px; background: {BG_CARD}; border-radius: 3px; }}
QScrollBar::handle:horizontal {{ background: {BORDER}; border-radius: 3px; }}

/* ── Buttons ── */
QPushButton {{
    background-color: {ACCENT};
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 20px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton:hover  {{ background-color: #6ba0ff; }}
QPushButton:pressed {{ background-color: #3a72d8; }}
QPushButton#secondary {{
    background-color: transparent;
    border: 1px solid {BORDER};
    color: {TEXT_SECONDARY};
}}
QPushButton#secondary:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}

/* ── Line edits ── */
QLineEdit {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 10px 14px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}
QLineEdit::placeholder {{ color: {TEXT_MUTED}; }}

/* ── ComboBox ── */
QComboBox {{
    background-color: {BG_INPUT};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 7px 12px;
    color: {TEXT_PRIMARY};
}}
QComboBox:hover {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
    border-radius: 6px;
    padding: 4px;
}}

/* ── List widget ── */
QListWidget {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 6px;
    outline: none;
}}
QListWidget::item {{
    border-radius: 6px;
    padding: 8px 10px;
    margin: 2px 0;
}}
QListWidget::item:selected {{
    background-color: rgba(79, 142, 247, 0.18);
    color: {TEXT_PRIMARY};
}}
QListWidget::item:hover {{
    background-color: rgba(255, 255, 255, 0.04);
}}

/* ── Labels ── */
QLabel#title {{
    font-size: 22px;
    font-weight: 700;
    color: {TEXT_PRIMARY};
}}
QLabel#subtitle {{
    font-size: 12px;
    color: {TEXT_SECONDARY};
}}
QLabel#card_title {{
    font-size: 14px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
}}

/* ── Frames / cards ── */
QFrame#card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}

/* ── Chart views ── */
QChartView {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
}}

/* ── Message boxes ── */
QMessageBox {{
    background-color: {BG_CARD};
}}
QMessageBox QPushButton {{
    min-width: 80px;
}}
"""
