# # gui/alerts.py
# import sys, os

# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, ROOT_DIR)
# sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

# from datetime import datetime, timedelta
# from PySide6.QtWidgets import (
#     QWidget,
#     QVBoxLayout,
#     QHBoxLayout,
#     QLabel,
#     QTableWidget,
#     QTableWidgetItem,
#     QHeaderView,
#     QAbstractItemView,
#     QFrame,
#     QApplication,
#     QPushButton,
# )
# from PySide6.QtGui import QColor, QFont
# from PySide6.QtCore import Qt, QTimer

# from gui.theme import (
#     BG_CARD,
#     BORDER,
#     TEXT_PRIMARY,
#     TEXT_SECONDARY,
#     TEXT_MUTED,
#     SUCCESS,
#     WARNING,
#     DANGER,
#     ACCENT,
#     BG_DARK,
# )

# _SEV = {
#     "DOWN": ("CRITICAL", DANGER, "▼"),
#     "DEGRADED": ("WARNING", WARNING, "◆"),
#     "UP": ("RECOVERED", SUCCESS, "▲"),
# }

# _COLS = ["Time", "Node", "Event", "Severity", "Latency"]


# # ─────────────────────────────────────────
# # Alert Popup — fires only on DOWN / DEGRADED
# # ─────────────────────────────────────────
# class AlertPopup(QWidget):
#     AUTO_CLOSE_SEC = 8
#     _active = []

#     def __init__(self, node_display: str, state: str, ip: str, latency, color: str):
#         super().__init__(
#             None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
#         )
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.setAttribute(Qt.WA_ShowWithoutActivating)
#         self._remaining = self.AUTO_CLOSE_SEC
#         self._bar_full_width = 324
#         self._build_ui(node_display, state, ip, latency, color)
#         self._position()

#         self._tick = QTimer(self)
#         self._tick.setInterval(1000)
#         self._tick.timeout.connect(self._countdown)
#         self._tick.start()

#     def _build_ui(self, node_display, state, ip, latency, color):
#         outer = QVBoxLayout(self)
#         outer.setContentsMargins(0, 0, 0, 0)

#         card = QFrame()
#         card.setFixedWidth(360)
#         card.setStyleSheet(f"""
#             QFrame {{
#                 background: #12151f;
#                 border: 1px solid {color};
#                 border-top: 4px solid {color};
#                 border-radius: 12px;
#             }}
#         """)
#         lay = QVBoxLayout(card)
#         lay.setContentsMargins(18, 16, 18, 16)
#         lay.setSpacing(10)

#         # Header
#         hdr = QHBoxLayout()
#         icon_lbl = QLabel("🚨" if state == "DOWN" else "⚠️")
#         icon_lbl.setStyleSheet(
#             "font-size: 22px; background: transparent; border: none;"
#         )

#         title_col = QVBoxLayout()
#         title_col.setSpacing(1)
#         sev_lbl = QLabel("CRITICAL ALERT" if state == "DOWN" else "WARNING")
#         sev_lbl.setStyleSheet(
#             f"color:{color}; font-size:11px; font-weight:700; letter-spacing:1px; background:transparent; border:none;"
#         )
#         node_lbl = QLabel(
#             f"Node {node_display} Failed"
#             if state == "DOWN"
#             else f"Node {node_display} Degraded"
#         )
#         node_lbl.setStyleSheet(
#             "color:#ffffff; font-size:15px; font-weight:700; background:transparent; border:none;"
#         )
#         title_col.addWidget(sev_lbl)
#         title_col.addWidget(node_lbl)

#         close_btn = QLabel("✕")
#         close_btn.setStyleSheet(
#             f"color:{TEXT_MUTED}; font-size:14px; background:transparent; border:none; padding:2px 6px;"
#         )
#         close_btn.setCursor(Qt.PointingHandCursor)
#         close_btn.mousePressEvent = lambda _: self.close()

#         hdr.addWidget(icon_lbl)
#         hdr.addSpacing(8)
#         hdr.addLayout(title_col)
#         hdr.addStretch()
#         hdr.addWidget(close_btn)
#         lay.addLayout(hdr)

#         # Divider
#         div = QFrame()
#         div.setFrameShape(QFrame.HLine)
#         div.setFixedHeight(1)
#         div.setStyleSheet(f"background:{color}; border:none;")
#         lay.addWidget(div)

#         # Details box
#         details = QFrame()
#         details.setStyleSheet("""
#             QFrame {
#                 background: rgba(255,255,255,0.04);
#                 border: 1px solid rgba(255,255,255,0.08);
#                 border-radius: 8px;
#             }
#         """)
#         det_lay = QVBoxLayout(details)
#         det_lay.setContentsMargins(12, 10, 12, 10)
#         det_lay.setSpacing(6)

#         def detail_row(label, value, val_color=TEXT_PRIMARY):
#             row = QHBoxLayout()
#             l = QLabel(label)
#             l.setStyleSheet(
#                 f"color:{TEXT_MUTED}; font-size:11px; font-weight:600; background:transparent; border:none;"
#             )
#             v = QLabel(str(value))
#             v.setStyleSheet(
#                 f"color:{val_color}; font-size:12px; font-weight:600; background:transparent; border:none;"
#             )
#             row.addWidget(l)
#             row.addStretch()
#             row.addWidget(v)
#             return row

#         try:
#             lat_str = f"{float(latency):.1f} ms"
#         except (TypeError, ValueError):
#             lat_str = "No data"

#         det_lay.addLayout(detail_row("Status", state, color))
#         det_lay.addLayout(detail_row("IP Address", ip or "Unknown", TEXT_PRIMARY))
#         det_lay.addLayout(detail_row("Latency", lat_str, TEXT_PRIMARY))
#         det_lay.addLayout(
#             detail_row("Time", datetime.now().strftime("%H:%M:%S"), TEXT_SECONDARY)
#         )
#         lay.addWidget(details)

#         # Message
#         msg = QLabel(
#             "This node is unreachable. Check the device and network connection."
#             if state == "DOWN"
#             else "This node is responding slowly. Performance may be degraded."
#         )
#         msg.setWordWrap(True)
#         msg.setStyleSheet(
#             f"color:{TEXT_SECONDARY}; font-size:11px; background:transparent; border:none;"
#         )
#         lay.addWidget(msg)

#         # Countdown bar
#         bar_bg = QFrame()
#         bar_bg.setFixedHeight(4)
#         bar_bg.setStyleSheet(
#             "background:rgba(255,255,255,0.08); border-radius:2px; border:none;"
#         )

#         self._bar = QFrame(bar_bg)
#         self._bar.setFixedHeight(4)
#         self._bar.setFixedWidth(self._bar_full_width)
#         self._bar.setStyleSheet(f"background:{color}; border-radius:2px; border:none;")

#         self._countdown_lbl = QLabel(f"Closing in {self._remaining}s")
#         self._countdown_lbl.setAlignment(Qt.AlignRight)
#         self._countdown_lbl.setStyleSheet(
#             f"color:{TEXT_MUTED}; font-size:10px; background:transparent; border:none;"
#         )

#         lay.addWidget(bar_bg)
#         lay.addWidget(self._countdown_lbl)

#         outer.addWidget(card)
#         self.adjustSize()

#     def _position(self):
#         screen = QApplication.primaryScreen().availableGeometry()
#         # Stack popups if multiple are open
#         offset = len(AlertPopup._active) * (self.height() + 10)
#         self.move(
#             screen.right() - self.width() - 24,
#             screen.bottom() - self.height() - 24 - offset,
#         )

#     def _countdown(self):
#         self._remaining -= 1
#         self._countdown_lbl.setText(f"Closing in {self._remaining}s")
#         w = int(self._bar_full_width * self._remaining / self.AUTO_CLOSE_SEC)
#         self._bar.setFixedWidth(max(0, w))
#         if self._remaining <= 0:
#             self._tick.stop()
#             self.close()

#     @staticmethod
#     def fire(node_display: str, state: str, ip: str, latency, color: str):
#         p = AlertPopup(node_display, state, ip, latency, color)
#         p.show()
#         AlertPopup._active.append(p)
#         QTimer.singleShot(
#             (AlertPopup.AUTO_CLOSE_SEC + 2) * 1000,
#             lambda: AlertPopup._active.remove(p) if p in AlertPopup._active else None,
#         )


# # ─────────────────────────────────────────
# # Helpers
# # ─────────────────────────────────────────
# def _fmt_node(raw: str) -> str:
#     parts = raw.replace("node_", "").split("_")
#     return " ".join(p.capitalize() for p in parts)


# def _colored_item(
#     text: str, color: str, bold=False, align=Qt.AlignLeft
# ) -> QTableWidgetItem:
#     item = QTableWidgetItem(text)
#     item.setForeground(QColor(color))
#     item.setTextAlignment(align | Qt.AlignVCenter)
#     item.setFlags(item.flags() & ~Qt.ItemIsEditable)
#     if bold:
#         f = QFont()
#         f.setBold(True)
#         item.setFont(f)
#     return item


# # ─────────────────────────────────────────
# # Alerts Panel
# # ─────────────────────────────────────────
# class AlertsPanel(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._prev_states: dict = {}
#         self._all_events: list = []  # (datetime, node_raw, state, latency)
#         self._initialized = False  # ← KEY FIX: track first refresh
#         self._build_ui()

#     def _build_ui(self):
#         lay = QVBoxLayout(self)
#         lay.setContentsMargins(0, 0, 0, 0)
#         lay.setSpacing(8)

#         # Header
#         hdr = QHBoxLayout()
#         title = QLabel("Alerts")
#         title.setStyleSheet(
#             f"font-size:15px; font-weight:700; color:{TEXT_PRIMARY}; background:transparent; border:none;"
#         )
#         self.counter = QLabel("0 events")
#         self.counter.setStyleSheet(
#             f"font-size:12px; color:{TEXT_MUTED}; background:transparent; border:none;"
#         )
#         hdr.addWidget(title)
#         hdr.addStretch()
#         hdr.addWidget(self.counter)
#         lay.addLayout(hdr)

#         # Filter tabs
#         tabs_row = QHBoxLayout()
#         tabs_row.setSpacing(6)
#         self._tab_btns = {}
#         for label in ["All", "1 Day", "7 Days", "30 Days"]:
#             btn = self._tab_btn(label)
#             self._tab_btns[label] = btn
#             tabs_row.addWidget(btn)
#         tabs_row.addStretch()
#         lay.addLayout(tabs_row)
#         self._active_filter = "All"
#         self._tab_btns["All"].setStyleSheet(self._btn_style(active=True))

#         # Table
#         self.table = QTableWidget(0, len(_COLS))
#         self.table.setHorizontalHeaderLabels(_COLS)
#         self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
#         self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
#         self.table.setAlternatingRowColors(True)
#         self.table.verticalHeader().setVisible(False)
#         self.table.setShowGrid(False)
#         self.table.setFocusPolicy(Qt.NoFocus)

#         hh = self.table.horizontalHeader()
#         hh.setSectionResizeMode(0, QHeaderView.Fixed)
#         self.table.setColumnWidth(0, 80)
#         hh.setSectionResizeMode(1, QHeaderView.Fixed)
#         self.table.setColumnWidth(1, 90)
#         hh.setSectionResizeMode(2, QHeaderView.Stretch)
#         hh.setSectionResizeMode(3, QHeaderView.Fixed)
#         self.table.setColumnWidth(3, 90)
#         hh.setSectionResizeMode(4, QHeaderView.Fixed)
#         self.table.setColumnWidth(4, 80)

#         self.table.setStyleSheet(f"""
#             QTableWidget {{
#                 background-color: {BG_CARD};
#                 alternate-background-color: #1e2130;
#                 border: 1px solid {BORDER};
#                 border-radius: 10px;
#                 color: {TEXT_PRIMARY};
#                 font-size: 12px;
#                 gridline-color: transparent;
#                 outline: none;
#             }}
#             QHeaderView::section {{
#                 background-color: #1a1d2e;
#                 color: {TEXT_MUTED};
#                 font-size: 11px;
#                 font-weight: 600;
#                 letter-spacing: 0.5px;
#                 padding: 6px 8px;
#                 border: none;
#                 border-bottom: 1px solid {BORDER};
#             }}
#             QTableWidget::item {{ padding: 6px 8px; border: none; }}
#             QTableWidget::item:selected {{
#                 background-color: rgba(79,142,247,0.15);
#                 color: {TEXT_PRIMARY};
#             }}
#             QScrollBar:vertical {{ background:{BG_DARK}; width:6px; border-radius:3px; }}
#             QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:20px; }}
#         """)
#         lay.addWidget(self.table)

#     def _btn_style(self, active=False) -> str:
#         if active:
#             return f"""QPushButton {{
#                 background:{ACCENT}; color:#fff; border:none;
#                 border-radius:6px; padding:4px 14px;
#                 font-size:11px; font-weight:600;
#             }}"""
#         return f"""QPushButton {{
#                 background:{BG_CARD}; color:{TEXT_SECONDARY};
#                 border:1px solid {BORDER}; border-radius:6px;
#                 padding:4px 14px; font-size:11px;
#             }}
#             QPushButton:hover {{ background:#1e2130; color:{TEXT_PRIMARY}; }}"""

#     def _tab_btn(self, label: str) -> QPushButton:
#         btn = QPushButton(label)
#         btn.setFixedHeight(28)
#         btn.setCursor(Qt.PointingHandCursor)
#         btn.setStyleSheet(self._btn_style(active=False))
#         btn.clicked.connect(lambda _, l=label: self._set_filter(l))
#         return btn

#     def _set_filter(self, label: str):
#         self._active_filter = label
#         for lbl, btn in self._tab_btns.items():
#             btn.setStyleSheet(self._btn_style(active=(lbl == label)))
#         self._render_table()

#     def update_alerts(self, states: dict):
#         now = datetime.now()

#         if not self._initialized:
#             # ── FIRST RUN: seed _prev_states silently, no events, no popups ──
#             # BUT if any node is already DOWN/DEGRADED, log it immediately
#             for node, info in states.items():
#                 current = info.get("state", "UNKNOWN")
#                 self._prev_states[node] = current
#                 if current in ("DOWN", "DEGRADED"):
#                     raw_lat = info.get("latency")
#                     self._all_events.insert(0, (now, node, current, raw_lat))
#                     # Fire popup for already-failed nodes on startup
#                     sev_label, color, icon = _SEV[current]
#                     AlertPopup.fire(
#                         node_display=_fmt_node(node),
#                         state=current,
#                         ip=info.get("ip", "Unknown"),
#                         latency=raw_lat,
#                         color=color,
#                     )
#             self._initialized = True
#             self._render_table()
#             return

#         # ── SUBSEQUENT RUNS: detect state changes ──
#         for node, info in states.items():
#             current = info.get("state", "UNKNOWN")
#             previous = self._prev_states.get(node)

#             if previous is not None and previous != current:
#                 raw_lat = info.get("latency") or info.get("last_latency")
#                 self._all_events.insert(0, (now, node, current, raw_lat))

#                 # Popup only for failures
#                 if current in ("DOWN", "DEGRADED"):
#                     sev_label, color, icon = _SEV[current]
#                     AlertPopup.fire(
#                         node_display=_fmt_node(node),
#                         state=current,
#                         ip=info.get("ip", "Unknown"),
#                         latency=raw_lat,
#                         color=color,
#                     )

#             self._prev_states[node] = current

#         self._render_table()

#     def update_alerts_filtered(self, range_key: str = "all"):
#         pass  # handled by tab buttons internally

#     def _cutoff(self):
#         now = datetime.now()
#         return {
#             "1 Day": now - timedelta(days=1),
#             "7 Days": now - timedelta(days=7),
#             "30 Days": now - timedelta(days=30),
#         }.get(self._active_filter, None)

#     def _render_table(self):
#         cutoff = self._cutoff()
#         events = [e for e in self._all_events if cutoff is None or e[0] >= cutoff]

#         self.table.setRowCount(0)
#         for dt, node_raw, state, latency in events:
#             row = self.table.rowCount()
#             self.table.insertRow(row)

#             sev_label, color, icon = _SEV.get(state, ("INFO", TEXT_MUTED, "●"))
#             node_display = _fmt_node(node_raw)

#             if state == "DOWN":
#                 event_text = f"{node_display} is OFFLINE — connection lost"
#             elif state == "DEGRADED":
#                 event_text = f"{node_display} is DEGRADED — high latency"
#             elif state == "UP":
#                 event_text = f"{node_display} recovered — back ONLINE"
#             else:
#                 event_text = f"{node_display} → {state}"

#             try:
#                 if latency is None or str(latency).strip().lower() == "none":
#                     raise ValueError
#                 lat_val = float(latency)
#                 lat_str = f"{lat_val:.1f} ms"
#                 lat_color = WARNING if lat_val >= 100 else TEXT_PRIMARY
#             except (TypeError, ValueError):
#                 lat_str = "—"
#                 lat_color = TEXT_MUTED

#             self.table.setItem(
#                 row,
#                 0,
#                 _colored_item(
#                     dt.strftime("%H:%M:%S"), TEXT_SECONDARY, align=Qt.AlignCenter
#                 ),
#             )
#             self.table.setItem(
#                 row, 1, _colored_item(node_display, TEXT_PRIMARY, bold=True)
#             )
#             self.table.setItem(row, 2, _colored_item(f"{icon}  {event_text}", color))
#             self.table.setItem(
#                 row,
#                 3,
#                 _colored_item(
#                     sev_label, color, bold=(state == "DOWN"), align=Qt.AlignCenter
#                 ),
#             )
#             self.table.setItem(
#                 row, 4, _colored_item(lat_str, lat_color, align=Qt.AlignCenter)
#             )
#             self.table.setRowHeight(row, 36)

#         n = len(events)
#         self.counter.setText(f"{n} {'event' if n == 1 else 'events'}")










# gui/alerts.py
import sys, os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QFrame,
    QApplication,
    QPushButton,
)
from PySide6.QtGui import QColor, QFont
from PySide6.QtCore import Qt, QTimer

from gui.theme import (
    BG_CARD,
    BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    SUCCESS,
    WARNING,
    DANGER,
    ACCENT,
    BG_DARK,
)

_SEV = {
    "DOWN": ("CRITICAL", DANGER, "▼"),
    "DEGRADED": ("WARNING", WARNING, "◆"),
    "UP": ("RECOVERED", SUCCESS, "▲"),
}

_COLS = ["Time", "Node", "Event", "Severity", "Latency"]

# Fixed popup height — used for stacking BEFORE the widget is rendered
_POPUP_HEIGHT = 220


# ─────────────────────────────────────────
# Alert Popup
# ─────────────────────────────────────────
class AlertPopup(QWidget):
    AUTO_CLOSE_SEC = 8
    _active = []  # keeps references so GC doesn't destroy popups

    def __init__(self, node_display: str, state: str, ip: str, latency, color: str):
        super().__init__(
            None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self._remaining = self.AUTO_CLOSE_SEC
        self._bar_full_width = 324
        self._build_ui(node_display, state, ip, latency, color)
        # NOTE: _position() is called in fire() AFTER show() so height() is real

        self._tick = QTimer(self)
        self._tick.setInterval(1000)
        self._tick.timeout.connect(self._countdown)
        self._tick.start()

    def _build_ui(self, node_display, state, ip, latency, color):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        card = QFrame()
        card.setFixedWidth(360)
        card.setStyleSheet(f"""
            QFrame {{
                background: #12151f;
                border: 1px solid {color};
                border-top: 4px solid {color};
                border-radius: 12px;
            }}
        """)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(10)

        # Header row
        hdr = QHBoxLayout()
        if state == "DOWN":
            icon_txt, title_txt = "🚨", "CRITICAL ALERT"
            body_txt = (
                "This node is unreachable. Check the device and network connection."
            )
            node_title = f"Node {node_display} Failed"
        elif state == "DEGRADED":
            icon_txt, title_txt = "⚠️", "WARNING"
            body_txt = "This node is responding slowly. Performance may be degraded."
            node_title = f"Node {node_display} Degraded"
        else:  # UP / RECOVERED
            icon_txt, title_txt = "✅", "RECOVERED"
            body_txt = "This node is back online and responding normally."
            node_title = f"Node {node_display} Recovered"

        icon_lbl = QLabel(icon_txt)
        icon_lbl.setStyleSheet(
            "font-size: 22px; background: transparent; border: none;"
        )

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        sev_lbl = QLabel(title_txt)
        sev_lbl.setStyleSheet(
            f"color:{color}; font-size:11px; font-weight:700; letter-spacing:1px; background:transparent; border:none;"
        )
        node_lbl = QLabel(node_title)
        node_lbl.setStyleSheet(
            "color:#ffffff; font-size:15px; font-weight:700; background:transparent; border:none;"
        )
        title_col.addWidget(sev_lbl)
        title_col.addWidget(node_lbl)

        close_btn = QLabel("✕")
        close_btn.setStyleSheet(
            f"color:{TEXT_MUTED}; font-size:14px; background:transparent; border:none; padding:2px 6px;"
        )
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.mousePressEvent = lambda _: self.close()

        hdr.addWidget(icon_lbl)
        hdr.addSpacing(8)
        hdr.addLayout(title_col)
        hdr.addStretch()
        hdr.addWidget(close_btn)
        lay.addLayout(hdr)

        # Divider
        div = QFrame()
        div.setFrameShape(QFrame.HLine)
        div.setFixedHeight(1)
        div.setStyleSheet(f"background:{color}; border:none;")
        lay.addWidget(div)

        # Details box
        details = QFrame()
        details.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
            }
        """)
        det_lay = QVBoxLayout(details)
        det_lay.setContentsMargins(12, 10, 12, 10)
        det_lay.setSpacing(6)

        def detail_row(label, value, val_color=TEXT_PRIMARY):
            row = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet(
                f"color:{TEXT_MUTED}; font-size:11px; font-weight:600; background:transparent; border:none;"
            )
            v = QLabel(str(value))
            v.setStyleSheet(
                f"color:{val_color}; font-size:12px; font-weight:600; background:transparent; border:none;"
            )
            row.addWidget(l)
            row.addStretch()
            row.addWidget(v)
            return row

        try:
            lat_str = f"{float(latency):.1f} ms"
        except (TypeError, ValueError):
            lat_str = "No data"

        det_lay.addLayout(detail_row("Status", state, color))
        det_lay.addLayout(detail_row("IP Address", ip or "Unknown", TEXT_PRIMARY))
        det_lay.addLayout(detail_row("Latency", lat_str, TEXT_PRIMARY))
        det_lay.addLayout(
            detail_row("Time", datetime.now().strftime("%H:%M:%S"), TEXT_SECONDARY)
        )
        lay.addWidget(details)

        # Message
        msg = QLabel(body_txt)
        msg.setWordWrap(True)
        msg.setStyleSheet(
            f"color:{TEXT_SECONDARY}; font-size:11px; background:transparent; border:none;"
        )
        lay.addWidget(msg)

        # Countdown progress bar
        bar_bg = QFrame()
        bar_bg.setFixedHeight(4)
        bar_bg.setStyleSheet(
            "background:rgba(255,255,255,0.08); border-radius:2px; border:none;"
        )

        self._bar = QFrame(bar_bg)
        self._bar.setFixedHeight(4)
        self._bar.setFixedWidth(self._bar_full_width)
        self._bar.setStyleSheet(f"background:{color}; border-radius:2px; border:none;")

        self._countdown_lbl = QLabel(f"Closing in {self._remaining}s")
        self._countdown_lbl.setAlignment(Qt.AlignRight)
        self._countdown_lbl.setStyleSheet(
            f"color:{TEXT_MUTED}; font-size:10px; background:transparent; border:none;"
        )

        lay.addWidget(bar_bg)
        lay.addWidget(self._countdown_lbl)

        outer.addWidget(card)
        self.adjustSize()

    def _position(self):
        """Position popup in bottom-right corner, stacking above previous ones."""
        screen = QApplication.primaryScreen().availableGeometry()
        # Use actual height if available, fall back to fixed estimate
        h = self.height() if self.height() > 10 else _POPUP_HEIGHT
        offset = len(AlertPopup._active) * (h + 10)
        self.move(
            screen.right() - self.width() - 24,
            screen.bottom() - h - 24 - offset,
        )

    def _countdown(self):
        self._remaining -= 1
        self._countdown_lbl.setText(f"Closing in {self._remaining}s")
        w = int(self._bar_full_width * self._remaining / self.AUTO_CLOSE_SEC)
        self._bar.setFixedWidth(max(0, w))
        if self._remaining <= 0:
            self._tick.stop()
            self.close()

    @staticmethod
    def fire(node_display: str, state: str, ip: str, latency, color: str):
        p = AlertPopup(node_display, state, ip, latency, color)
        AlertPopup._active.append(
            p
        )  # append BEFORE show so _position sees correct count
        p.show()
        p._position()  # ← FIXED: called AFTER show() so height() is real
        QTimer.singleShot(
            (AlertPopup.AUTO_CLOSE_SEC + 2) * 1000,
            lambda: AlertPopup._active.remove(p) if p in AlertPopup._active else None,
        )


# ─────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────
def _fmt_node(raw: str) -> str:
    parts = raw.replace("node_", "").split("_")
    return " ".join(p.capitalize() for p in parts)


def _colored_item(
    text: str, color: str, bold=False, align=Qt.AlignLeft
) -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setForeground(QColor(color))
    item.setTextAlignment(align | Qt.AlignVCenter)
    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
    if bold:
        f = QFont()
        f.setBold(True)
        item.setFont(f)
    return item


# ─────────────────────────────────────────
# Alerts Panel
# ─────────────────────────────────────────
class AlertsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._prev_states: dict = {}
        self._all_events: list = []  # (datetime, node_raw, state, latency)
        self._initialized = False
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Header
        hdr = QHBoxLayout()
        title = QLabel("Alerts")
        title.setStyleSheet(
            f"font-size:15px; font-weight:700; color:{TEXT_PRIMARY}; background:transparent; border:none;"
        )
        self.counter = QLabel("0 events")
        self.counter.setStyleSheet(
            f"font-size:12px; color:{TEXT_MUTED}; background:transparent; border:none;"
        )
        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(self.counter)
        lay.addLayout(hdr)

        # Filter tabs
        tabs_row = QHBoxLayout()
        tabs_row.setSpacing(6)
        self._tab_btns = {}
        for label in ["All", "1 Day", "7 Days", "30 Days"]:
            btn = self._tab_btn(label)
            self._tab_btns[label] = btn
            tabs_row.addWidget(btn)
        tabs_row.addStretch()
        lay.addLayout(tabs_row)
        self._active_filter = "All"
        self._tab_btns["All"].setStyleSheet(self._btn_style(active=True))

        # Table
        self.table = QTableWidget(0, len(_COLS))
        self.table.setHorizontalHeaderLabels(_COLS)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)

        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 80)
        hh.setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 90)
        hh.setSectionResizeMode(2, QHeaderView.Stretch)
        hh.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 90)
        hh.setSectionResizeMode(4, QHeaderView.Fixed)
        self.table.setColumnWidth(4, 80)

        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {BG_CARD};
                alternate-background-color: #1e2130;
                border: 1px solid {BORDER};
                border-radius: 10px;
                color: {TEXT_PRIMARY};
                font-size: 12px;
                gridline-color: transparent;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: #1a1d2e;
                color: {TEXT_MUTED};
                font-size: 11px;
                font-weight: 600;
                letter-spacing: 0.5px;
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid {BORDER};
            }}
            QTableWidget::item {{ padding: 6px 8px; border: none; }}
            QTableWidget::item:selected {{
                background-color: rgba(79,142,247,0.15);
                color: {TEXT_PRIMARY};
            }}
            QScrollBar:vertical {{ background:{BG_DARK}; width:6px; border-radius:3px; }}
            QScrollBar::handle:vertical {{ background:{BORDER}; border-radius:3px; min-height:20px; }}
        """)
        lay.addWidget(self.table)

    def _btn_style(self, active=False) -> str:
        if active:
            return f"""QPushButton {{
                background:{ACCENT}; color:#fff; border:none;
                border-radius:6px; padding:4px 14px;
                font-size:11px; font-weight:600;
            }}"""
        return f"""QPushButton {{
                background:{BG_CARD}; color:{TEXT_SECONDARY};
                border:1px solid {BORDER}; border-radius:6px;
                padding:4px 14px; font-size:11px;
            }}
            QPushButton:hover {{ background:#1e2130; color:{TEXT_PRIMARY}; }}"""

    def _tab_btn(self, label: str) -> QPushButton:
        btn = QPushButton(label)
        btn.setFixedHeight(28)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(self._btn_style(active=False))
        btn.clicked.connect(lambda _, l=label: self._set_filter(l))
        return btn

    def _set_filter(self, label: str):
        self._active_filter = label
        for lbl, btn in self._tab_btns.items():
            btn.setStyleSheet(self._btn_style(active=(lbl == label)))
        self._render_table()

    def update_alerts(self, states: dict):
        now = datetime.now()

        if not self._initialized:
            # First run: seed _prev_states silently
            # But fire popups + log events for nodes already DOWN/DEGRADED
            for node, info in states.items():
                current = info.get("state", "UNKNOWN")
                self._prev_states[node] = current
                if current in ("DOWN", "DEGRADED"):
                    raw_lat = info.get("latency")
                    self._all_events.insert(0, (now, node, current, raw_lat))
                    sev_label, color, icon = _SEV[current]
                    AlertPopup.fire(
                        node_display=_fmt_node(node),
                        state=current,
                        ip=info.get("ip", "Unknown"),
                        latency=raw_lat,
                        color=color,
                    )
            self._initialized = True
            self._render_table()
            return

        # Subsequent runs: detect every state change
        for node, info in states.items():
            current = info.get("state", "UNKNOWN")
            previous = self._prev_states.get(node)

            if previous is not None and previous != current:
                raw_lat = info.get("latency") or info.get("last_latency")
                self._all_events.insert(0, (now, node, current, raw_lat))

                # Fire popup for ALL transitions (DOWN, DEGRADED, and RECOVERED)
                if current in _SEV:
                    sev_label, color, icon = _SEV[current]
                    AlertPopup.fire(
                        node_display=_fmt_node(node),
                        state=current,
                        ip=info.get("ip", "Unknown"),
                        latency=raw_lat,
                        color=color,
                    )

            self._prev_states[node] = current

        self._render_table()

    def update_alerts_filtered(self, range_key: str = "all"):
        pass  # handled by tab buttons internally

    def _cutoff(self):
        now = datetime.now()
        return {
            "1 Day": now - timedelta(days=1),
            "7 Days": now - timedelta(days=7),
            "30 Days": now - timedelta(days=30),
        }.get(self._active_filter, None)

    def _render_table(self):
        cutoff = self._cutoff()
        events = [e for e in self._all_events if cutoff is None or e[0] >= cutoff]

        self.table.setRowCount(0)
        for dt, node_raw, state, latency in events:
            row = self.table.rowCount()
            self.table.insertRow(row)

            sev_label, color, icon = _SEV.get(state, ("INFO", TEXT_MUTED, "●"))
            node_display = _fmt_node(node_raw)

            if state == "DOWN":
                event_text = f"{node_display} is OFFLINE — connection lost"
            elif state == "DEGRADED":
                event_text = f"{node_display} is DEGRADED — high latency"
            elif state == "UP":
                event_text = f"{node_display} recovered — back ONLINE"
            else:
                event_text = f"{node_display} → {state}"

            try:
                if latency is None or str(latency).strip().lower() == "none":
                    raise ValueError
                lat_val = float(latency)
                lat_str = f"{lat_val:.1f} ms"
                lat_color = WARNING if lat_val >= 100 else TEXT_PRIMARY
            except (TypeError, ValueError):
                lat_str = "—"
                lat_color = TEXT_MUTED

            self.table.setItem(
                row,
                0,
                _colored_item(
                    dt.strftime("%H:%M:%S"), TEXT_SECONDARY, align=Qt.AlignCenter
                ),
            )
            self.table.setItem(
                row, 1, _colored_item(node_display, TEXT_PRIMARY, bold=True)
            )
            self.table.setItem(row, 2, _colored_item(f"{icon}  {event_text}", color))
            self.table.setItem(
                row,
                3,
                _colored_item(
                    sev_label, color, bold=(state == "DOWN"), align=Qt.AlignCenter
                ),
            )
            self.table.setItem(
                row, 4, _colored_item(lat_str, lat_color, align=Qt.AlignCenter)
            )
            self.table.setRowHeight(row, 36)

        n = len(events)
        self.counter.setText(f"{n} {'event' if n == 1 else 'events'}")