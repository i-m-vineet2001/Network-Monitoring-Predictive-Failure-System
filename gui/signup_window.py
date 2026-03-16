

import sys, os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QFrame,
)
from PySide6.QtCore import Qt

from db.user_service import create_user
from gui.theme import (
    BG_DARK,
    BG_CARD,
    ACCENT,
    BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    DANGER,
    SUCCESS,
)


class SignupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Monitor — Create Account")
        self.setFixedSize(420, 500)
        self.setStyleSheet(f"background-color: {BG_DARK};")
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(36, 36, 36, 36)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(32, 32, 32, 32)
        lay.setSpacing(6)

        icon = QLabel("✨")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 34px; background: transparent; border: none;")

        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent; border: none;"
        )

        sub = QLabel("Join Network Monitor")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(
            f"font-size: 12px; color: {TEXT_SECONDARY}; background: transparent; border: none;"
        )

        self.username = self._field("Username")
        self.email = self._field("Email address")
        self.password = self._field("Password", echo=True)
        self.password.returnPressed.connect(self.handle_signup)

        self.msg = QLabel("")
        self.msg.setAlignment(Qt.AlignCenter)
        self.msg.setWordWrap(True)
        self.msg.setFixedHeight(20)
        self.msg.setStyleSheet(
            f"color: {DANGER}; font-size: 12px; background: transparent; border: none;"
        )

        btn = QPushButton("Create Account")
        btn.setFixedHeight(44)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: #fff;
                border-radius: 10px; font-size: 14px; font-weight: 600; border: none;
            }}
            QPushButton:hover  {{ background: #6ba0ff; }}
            QPushButton:pressed {{ background: #3a72d8; }}
        """)
        btn.clicked.connect(self.handle_signup)

        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(12)
        lay.addWidget(self._label("Username"))
        lay.addWidget(self.username)
        lay.addSpacing(4)
        lay.addWidget(self._label("Email"))
        lay.addWidget(self.email)
        lay.addSpacing(4)
        lay.addWidget(self._label("Password"))
        lay.addWidget(self.password)
        lay.addSpacing(8)
        lay.addWidget(self.msg)
        lay.addSpacing(4)
        lay.addWidget(btn)

        outer.addWidget(card)

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:12px; font-weight:600; background:transparent; border:none;"
        )
        return lbl

    def _field(self, placeholder, echo=False):
        f = QLineEdit()
        f.setPlaceholderText(f"  {placeholder}")
        f.setFixedHeight(44)
        if echo:
            f.setEchoMode(QLineEdit.Password)
        f.setStyleSheet(f"""
            QLineEdit {{
                background: #1e2130; border: 1px solid {BORDER};
                border-radius: 10px; padding: 0 14px;
                color: {TEXT_PRIMARY}; font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        return f

    def handle_signup(self):
        success, message = create_user(
            self.username.text().strip(),
            self.email.text().strip(),
            self.password.text(),
        )
        color = SUCCESS if success else DANGER
        self.msg.setStyleSheet(
            f"color: {color}; font-size: 12px; background: transparent; border: none;"
        )
        self.msg.setText(("✓  " if success else "⚠  ") + message)