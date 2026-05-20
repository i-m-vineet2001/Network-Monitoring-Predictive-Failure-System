# import sys, os

# # gui/ → root/,  src/ for db imports
# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, ROOT_DIR)
# sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

# from PySide6.QtWidgets import (
#     QWidget,
#     QLabel,
#     QLineEdit,
#     QPushButton,
#     QVBoxLayout,
#     QHBoxLayout,
#     QFrame,
# )
# from PySide6.QtCore import Qt

# from db.user_service import login_user
# from gui.theme import (
#     BG_DARK,
#     BG_CARD,
#     ACCENT,
#     BORDER,
#     TEXT_PRIMARY,
#     TEXT_SECONDARY,
#     TEXT_MUTED,
#     DANGER,
# )


# class LoginWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Network Monitor — Login")
#         self.setFixedSize(460, 500)
#         self.setStyleSheet(f"background-color: {BG_DARK};")
#         self._build_ui()

#     def _build_ui(self):
#         outer = QVBoxLayout(self)
#         outer.setAlignment(Qt.AlignCenter)
#         outer.setContentsMargins(40, 40, 40, 40)

#         card = QFrame()
#         card.setStyleSheet(f"""
#             QFrame {{
#                 background-color: {BG_CARD};
#                 border: 1px solid {BORDER};
#                 border-radius: 16px;
#             }}
#         """)
#         lay = QVBoxLayout(card)
#         lay.setContentsMargins(36, 36, 36, 36)
#         lay.setSpacing(14)

#         # Icon + title
#         icon = QLabel("🌐")
#         icon.setAlignment(Qt.AlignCenter)
#         icon.setStyleSheet("font-size: 38px; background: transparent; border: none;")

#         title = QLabel("Network Monitor")
#         title.setAlignment(Qt.AlignCenter)
#         title.setStyleSheet(
#             f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent; border: none;"
#         )

#         sub = QLabel("Sign in to your account")
#         sub.setAlignment(Qt.AlignCenter)
#         sub.setStyleSheet(
#             f"font-size: 13px; color: {TEXT_SECONDARY}; background: transparent; border: none;"
#         )

#         divider = QFrame()
#         divider.setFrameShape(QFrame.HLine)
#         divider.setFixedHeight(1)
#         divider.setStyleSheet(f"background: {BORDER}; border: none;")

#         # Fields
#         self.username = self._field("Username")
#         self.password = self._field("Password", echo=True)
#         self.password.returnPressed.connect(self.handle_login)

#         # Error label
#         self.error_lbl = QLabel("")
#         self.error_lbl.setAlignment(Qt.AlignCenter)
#         self.error_lbl.setWordWrap(True)
#         self.error_lbl.setStyleSheet(
#             f"color: {DANGER}; font-size: 12px; background: transparent; border: none;"
#         )

#         # Login button
#         login_btn = QPushButton("Sign In")
#         login_btn.setFixedHeight(44)
#         login_btn.setCursor(Qt.PointingHandCursor)
#         login_btn.setStyleSheet(f"""
#             QPushButton {{
#                 background: {ACCENT}; color: #fff;
#                 border-radius: 10px; font-size: 14px; font-weight: 600; border: none;
#             }}
#             QPushButton:hover  {{ background: #6ba0ff; }}
#             QPushButton:pressed {{ background: #3a72d8; }}
#         """)
#         login_btn.clicked.connect(self.handle_login)

#         # Signup row
#         row = QHBoxLayout()
#         no_acc = QLabel("Don't have an account?")
#         no_acc.setStyleSheet(
#             f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent; border: none;"
#         )
#         signup_btn = QPushButton("Create one")
#         signup_btn.setFlat(True)
#         signup_btn.setCursor(Qt.PointingHandCursor)
#         signup_btn.setStyleSheet(f"""
#             QPushButton {{
#                 color: {ACCENT}; font-size: 12px; font-weight: 600;
#                 background: transparent; border: none; padding: 0;
#             }}
#             QPushButton:hover {{ color: #6ba0ff; }}
#         """)
#         signup_btn.clicked.connect(self.open_signup)
#         row.addStretch()
#         row.addWidget(no_acc)
#         row.addWidget(signup_btn)
#         row.addStretch()

#         for lbl_text, widget in [
#             ("Username", self.username),
#             ("Password", self.password),
#         ]:
#             lbl = QLabel(lbl_text)
#             lbl.setStyleSheet(
#                 f"color:{TEXT_SECONDARY}; font-size:12px; font-weight:600; background:transparent; border:none;"
#             )
#             lay.addWidget(lbl)
#             lay.addWidget(widget)

#         lay.insertWidget(0, icon)
#         lay.insertWidget(1, title)
#         lay.insertWidget(2, sub)
#         lay.insertWidget(3, divider)
#         lay.addWidget(self.error_lbl)
#         lay.addSpacing(4)
#         lay.addWidget(login_btn)
#         lay.addLayout(row)

#         outer.addWidget(card)

#     def _field(self, placeholder, echo=False):
#         f = QLineEdit()
#         f.setPlaceholderText(f"  {placeholder}")
#         f.setFixedHeight(44)
#         if echo:
#             f.setEchoMode(QLineEdit.Password)
#         f.setStyleSheet(f"""
#             QLineEdit {{
#                 background: #1e2130; border: 1px solid {BORDER};
#                 border-radius: 10px; padding: 0 14px;
#                 color: {TEXT_PRIMARY}; font-size: 13px;
#             }}
#             QLineEdit:focus {{ border-color: {ACCENT}; }}
#         """)
#         return f

#     def handle_login(self):
#         self.error_lbl.setText("")
#         success, message = login_user(
#             self.username.text().strip(),
#             self.password.text(),
#         )
#         if success:
#             from gui.gui import NetworkMonitorGUI

#             self.monitor_window = NetworkMonitorGUI()
#             self.monitor_window.show()
#             self.close()
#         else:
#             self.error_lbl.setText(f"⚠  {message}")

#     def open_signup(self):
#         from gui.signup_window import SignupWindow

#         self.signup_window = SignupWindow()
#         self.signup_window.show()


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
    QHBoxLayout,
    QFrame,
)
from PySide6.QtCore import Qt

from db.user_service import login_user
from gui.theme import (
    BG_DARK,
    BG_CARD,
    ACCENT,
    BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    DANGER,
)


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Monitor — Login")
        self.setFixedSize(460, 500)
        self.setStyleSheet(f"background-color: {BG_DARK};")
        self._build_ui()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(40, 40, 40, 40)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(36, 36, 36, 36)
        lay.setSpacing(6)

        # Header
        icon = QLabel("🌐")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet(
            "font-size: 38px; color: #4f8ef7; background: transparent; border: none;"
        )

        title = QLabel("Network Monitor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {TEXT_PRIMARY};"
            f" background: transparent; border: none;"
        )

        sub = QLabel("Sign in to your account")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet(
            f"font-size: 13px; color: {TEXT_SECONDARY};"
            f" background: transparent; border: none;"
        )

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFixedHeight(1)
        divider.setStyleSheet(f"background: {BORDER}; border: none;")

        # Fields
        self.username = self._field("Username")
        self.password = self._field("Password", echo=True)
        self.password.returnPressed.connect(self.handle_login)

        # Error label
        self.error_lbl = QLabel("")
        self.error_lbl.setAlignment(Qt.AlignCenter)
        self.error_lbl.setWordWrap(True)
        self.error_lbl.setFixedHeight(20)
        self.error_lbl.setStyleSheet(
            f"color: {DANGER}; font-size: 12px; background: transparent; border: none;"
        )

        # Login button
        login_btn = QPushButton("Sign In")
        login_btn.setFixedHeight(44)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet(f"""
            QPushButton {{
                background: {ACCENT}; color: #fff;
                border-radius: 10px; font-size: 14px; font-weight: 600; border: none;
            }}
            QPushButton:hover   {{ background: #6ba0ff; }}
            QPushButton:pressed {{ background: #3a72d8; }}
        """)
        login_btn.clicked.connect(self.handle_login)

        # Signup row
        row = QHBoxLayout()
        no_acc = QLabel("Don't have an account?")
        no_acc.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; background: transparent; border: none;"
        )
        signup_btn = QPushButton("Create one")
        signup_btn.setFlat(True)
        signup_btn.setCursor(Qt.PointingHandCursor)
        signup_btn.setStyleSheet(f"""
            QPushButton {{
                color: {ACCENT}; font-size: 12px; font-weight: 600;
                background: transparent; border: none; padding: 0;
            }}
            QPushButton:hover {{ color: #6ba0ff; }}
        """)
        signup_btn.clicked.connect(self.open_signup)
        row.addStretch()
        row.addWidget(no_acc)
        row.addWidget(signup_btn)
        row.addStretch()

        # Add everything in strict top-to-bottom order — no insertWidget!
        lay.addWidget(icon)
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addSpacing(8)
        lay.addWidget(divider)
        lay.addSpacing(8)
        lay.addWidget(self._label("Username"))
        lay.addWidget(self.username)
        lay.addSpacing(4)
        lay.addWidget(self._label("Password"))
        lay.addWidget(self.password)
        lay.addSpacing(8)
        lay.addWidget(self.error_lbl)
        lay.addSpacing(4)
        lay.addWidget(login_btn)
        lay.addSpacing(4)
        lay.addLayout(row)

        outer.addWidget(card)

    def _label(self, text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"
            f" background: transparent; border: none;"
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
                background: #1e2130;
                border: 1px solid {BORDER};
                border-radius: 10px;
                padding: 0 14px;
                color: {TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:focus {{ border-color: {ACCENT}; }}
        """)
        return f

    def handle_login(self):
        self.error_lbl.setText("")
        success, message = login_user(
            self.username.text().strip(),
            self.password.text(),
        )
        if success:
            from gui.gui import NetworkMonitorGUI

            self.monitor_window = NetworkMonitorGUI()
            self.monitor_window.show()
            self.close()
        else:
            self.error_lbl.setText(f"⚠  {message}")

    def open_signup(self):
        from gui.signup_window import SignupWindow

        self.signup_window = SignupWindow()
        self.signup_window.show()
