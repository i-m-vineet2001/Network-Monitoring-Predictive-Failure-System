



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
#     QComboBox,
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
#     "AI": ("AI ALERT", "#9b59b6", "⬤"),
# }

# _COLS = ["Time", "Node", "Event", "Severity", "Latency"]

# # Fixed popup height — used for stacking BEFORE the widget is rendered
# _POPUP_HEIGHT = 220


# # ─────────────────────────────────────────
# # Alert Popup
# # ─────────────────────────────────────────
# class AlertPopup(QWidget):
#     AUTO_CLOSE_SEC = 8
#     _active = []  # keeps references so GC doesn't destroy popups

#     def __init__(self, node_display: str, state: str, ip: str, latency, color: str):
#         super().__init__(
#             None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
#         )
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.setAttribute(Qt.WA_ShowWithoutActivating)
#         self._remaining = self.AUTO_CLOSE_SEC
#         self._bar_full_width = 324
#         self._build_ui(node_display, state, ip, latency, color)
#         # NOTE: _position() is called in fire() AFTER show() so height() is real

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

#         # Header row
#         hdr = QHBoxLayout()
#         if state == "DOWN":
#             icon_txt, title_txt = "🚨", "CRITICAL ALERT"
#             body_txt = (
#                 "This node is unreachable. Check the device and network connection."
#             )
#             node_title = f"Node {node_display} Failed"
#         elif state == "DEGRADED":
#             icon_txt, title_txt = "⚠️", "WARNING"
#             body_txt = "This node is responding slowly. Performance may be degraded."
#             node_title = f"Node {node_display} Degraded"

#         elif state == "AI":
#             icon_txt, title_txt = "🧠", "AI PREDICTION"
#             body_txt = "ML model predicts this node may fail soon. Monitor closely."
#             node_title = f"Node {node_display} — Failure Risk High"

#         else:  # UP / RECOVERED
#             icon_txt, title_txt = "✅", "RECOVERED"
#             body_txt = "This node is back online and responding normally."
#             node_title = f"Node {node_display} Recovered"

#         icon_lbl = QLabel(icon_txt)
#         icon_lbl.setStyleSheet(
#             f"font-size: 22px; color: {color}; background: transparent; border: none;"
#         )

#         title_col = QVBoxLayout()
#         title_col.setSpacing(1)
#         sev_lbl = QLabel(title_txt)
#         sev_lbl.setStyleSheet(
#             f"color:{color}; font-size:11px; font-weight:700; letter-spacing:1px; background:transparent; border:none;"
#         )
#         node_lbl = QLabel(node_title)
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
#         msg = QLabel(body_txt)
#         msg.setWordWrap(True)
#         msg.setStyleSheet(
#             f"color:{TEXT_SECONDARY}; font-size:11px; background:transparent; border:none;"
#         )
#         lay.addWidget(msg)

#         # Countdown progress bar
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
#         """Position popup in bottom-right corner, stacking above previous ones."""
#         screen = QApplication.primaryScreen().availableGeometry()
#         # Use actual height if available, fall back to fixed estimate
#         h = self.height() if self.height() > 10 else _POPUP_HEIGHT
#         offset = len(AlertPopup._active) * (h + 10)
#         self.move(
#             screen.right() - self.width() - 24,
#             screen.bottom() - h - 24 - offset,
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
#         print(
#             f"[AlertPopup.fire] node={node_display}, state={state}, ip={ip}, color={color}"
#         )
#         p = AlertPopup(node_display, state, ip, latency, color)
#         AlertPopup._active.append(
#             p
#         )  # append BEFORE show so _position sees correct count
#         p.show()
#         p._position()  # ← FIXED: called AFTER show() so height() is real
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
#         self._initialized = False
#         self._ml_last_alert = {}
#         self._state_last_alert = {}  # tracks last DOWN/DEGRADED alert timestamp per node
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

#         # Filter tabs - Alert Type dropdown and Time dropdown
#         tabs_row = QHBoxLayout()
#         tabs_row.setSpacing(8)
#         self._tab_btns = {}

#         # Alert type dropdown
#         type_label = QLabel("Type:")
#         type_label.setStyleSheet(
#             f"font-size:11px; color:{TEXT_SECONDARY}; font-weight:600; background:transparent; border:none;"
#         )
#         tabs_row.addWidget(type_label)

#         self._type_combo = QComboBox()
#         self._type_combo.addItems(
#             ["All Types", "Critical", "Warning", "Recovered", "AI"]
#         )
#         self._type_combo.setCurrentText("All Types")
#         self._type_combo.setFixedWidth(120)
#         self._type_combo.setStyleSheet(f"""
#             QComboBox {{
#                 background: {BG_CARD};
#                 border: 1px solid {BORDER};
#                 border-radius: 10px;
#                 color: {TEXT_PRIMARY};
#                 padding: 8px 12px;
#                 font-size: 12px;
#                 font-weight: 500;
#                 min-height: 32px;
#                 outline: none;
#             }}
#             QComboBox::drop-down {{
#                 border: none;
#                 width: 28px;
#                 padding-right: 8px;
#                 subcontrol-origin: padding;
#                 subcontrol-position: center right;
#             }}
#             QComboBox::down-arrow {{
#                 image: none;
#                 border: none;
#                 width: 0;
#                 height: 0;
#                 border-left: 4px solid transparent;
#                 border-right: 4px solid transparent;
#                 border-top: 5px solid {TEXT_SECONDARY};
#                 margin-top: 2px;
#             }}
#             QComboBox:hover {{
#                 border-color: {ACCENT};
#                 background: linear-gradient(135deg, #1e2130 0%, #252836 100%);
#             }}
#             QComboBox:hover::down-arrow {{
#                 border-top-color: {ACCENT};
#             }}
#             QComboBox::drop-down:hover {{
#                 background: transparent;
#             }}
#             QComboBox:focus {{
#                 border-color: {ACCENT};
#             }}
#             QComboBox QAbstractItemView {{
#                 background: linear-gradient(135deg, {BG_CARD} 0%, #1a1d2e 100%);
#                 border: 1px solid {BORDER};
#                 border-radius: 8px;
#                 color: {TEXT_PRIMARY};
#                 selection-background-color: {ACCENT};
#                 selection-color: white;
#                 padding: 6px;
#                 outline: none;
#             }}
#             QComboBox QAbstractItemView::item {{
#                 padding: 8px 12px;
#                 border-radius: 4px;
#                 margin: 1px;
#                 font-size: 12px;
#             }}
#             QComboBox QAbstractItemView::item:hover {{
#                 background: rgba(79,142,247,0.1);
#                 color: {TEXT_PRIMARY};
#             }}
#             QComboBox QAbstractItemView::item:selected {{
#                 background: {ACCENT};
#                 color: white;
#             }}
#         """)
#         self._type_combo.currentTextChanged.connect(self._on_type_filter_changed)
#         tabs_row.addWidget(self._type_combo)

#         # Separator
#         sep = QFrame()
#         sep.setFrameShape(QFrame.VLine)
#         sep.setFrameShadow(QFrame.Sunken)
#         sep.setStyleSheet(f"color: {BORDER}; margin: 0 4px;")
#         tabs_row.addWidget(sep)

#         # Time dropdown
#         time_label = QLabel("Time:")
#         time_label.setStyleSheet(
#             f"font-size:11px; color:{TEXT_SECONDARY}; font-weight:600; background:transparent; border:none;"
#         )
#         tabs_row.addWidget(time_label)

#         self._time_combo = QComboBox()
#         self._time_combo.addItems(["All Time", "1 Day", "7 Days", "30 Days"])
#         self._time_combo.setCurrentText("All Time")
#         self._time_combo.setFixedWidth(110)
#         self._time_combo.setStyleSheet(f"""
#             QComboBox {{
#                 background: {BG_CARD};
#                 border: 1px solid {BORDER};
#                 border-radius: 10px;
#                 color: {TEXT_PRIMARY};
#                 padding: 8px 12px;
#                 font-size: 12px;
#                 font-weight: 500;
#                 min-height: 32px;
#                 outline: none;
#             }}
#             QComboBox::drop-down {{
#                 border: none;
#                 width: 28px;
#                 padding-right: 8px;
#                 subcontrol-origin: padding;
#                 subcontrol-position: center right;
#             }}
#             QComboBox::down-arrow {{
#                 image: none;
#                 border: none;
#                 width: 0;
#                 height: 0;
#                 border-left: 4px solid transparent;
#                 border-right: 4px solid transparent;
#                 border-top: 5px solid {TEXT_SECONDARY};
#                 margin-top: 2px;
#             }}
#             QComboBox:hover {{
#                 border-color: {ACCENT};
#                 background: linear-gradient(135deg, #1e2130 0%, #252836 100%);
#             }}
#             QComboBox:hover::down-arrow {{
#                 border-top-color: {ACCENT};
#             }}
#             QComboBox::drop-down:hover {{
#                 background: transparent;
#             }}
#             QComboBox:focus {{
#                 border-color: {ACCENT};
#             }}
#             QComboBox QAbstractItemView {{
#                 background: linear-gradient(135deg, {BG_CARD} 0%, #1a1d2e 100%);
#                 border: 1px solid {BORDER};
#                 border-radius: 8px;
#                 color: {TEXT_PRIMARY};
#                 selection-background-color: {ACCENT};
#                 selection-color: white;
#                 padding: 6px;
#                 outline: none;
#             }}
#             QComboBox QAbstractItemView::item {{
#                 padding: 8px 12px;
#                 border-radius: 4px;
#                 margin: 1px;
#                 font-size: 12px;
#             }}
#             QComboBox QAbstractItemView::item:hover {{
#                 background: rgba(79,142,247,0.1);
#                 color: {TEXT_PRIMARY};
#             }}
#             QComboBox QAbstractItemView::item:selected {{
#                 background: {ACCENT};
#                 color: white;
#             }}
#         """)
#         self._time_combo.currentTextChanged.connect(self._on_time_filter_changed)
#         tabs_row.addWidget(self._time_combo)

#         tabs_row.addStretch()

#         # Circular notification toggle button
#         self._notifications_enabled = True
#         self._notify_btn = QPushButton("🔔")
#         self._notify_btn.setFixedSize(44, 44)
#         self._notify_btn.setCursor(Qt.PointingHandCursor)
#         self._notify_btn.clicked.connect(self._toggle_notifications)

#         self._badge = QLabel("●", self._notify_btn)
#         self._badge.setStyleSheet(
#             "background: #ff4d4f; color: transparent; border-radius: 5px;"
#         )
#         self._badge.setFixedSize(10, 10)
#         self._badge.move(30, 6)
#         self._badge.hide()

#         tabs_row.addWidget(self._notify_btn)

#         lay.addLayout(tabs_row)

#         self._active_type_filter = "All Types"
#         self._active_time_filter = "All Time"

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
#         self._update_notify_button_style()

#     def _on_type_filter_changed(self, text):
#         self._active_type_filter = text
#         self._render_table()

#     def _on_time_filter_changed(self, text):
#         self._active_time_filter = text
#         self._render_table()

#     def _update_notify_button_style(self):
#         if self._notifications_enabled:
#             bg = "#2ecc71"
#             icon = "🔔"
#         else:
#             bg = "#555b6e"
#             icon = "🔕"

#         self._notify_btn.setText(icon)
#         self._notify_btn.setStyleSheet(f"""
#             QPushButton {{
#                 background: {bg};
#                 border-radius: 22px;
#                 font-size: 18px;
#                 font-weight: bold;
#                 border: none;
#                 color: white;
#                 padding: 0px;
#             }}
#             QPushButton:hover {{
#                 background: #2c3142;
#             }}
#         """)

#     def _toggle_notifications(self):
#         self._notifications_enabled = not self._notifications_enabled
#         self._update_notify_button_style()

#     def update_alerts(self, states: dict):
#         now = datetime.now()

#         if not self._initialized:
#             # First run: seed _prev_states silently
#             # But fire popups + log events for nodes already DOWN/DEGRADED
#             for node, info in states.items():
#                 current = info.get("state", "UNKNOWN")
#                 self._prev_states[node] = current
#                 if current in ("DOWN", "DEGRADED"):
#                     raw_lat = info.get("latency")
#                     self._all_events.insert(0, (now, node, current, raw_lat))
#                     if self._notifications_enabled:
#                         sev_label, color, icon = _SEV[current]
#                         AlertPopup.fire(
#                             node_display=_fmt_node(node),
#                             state=current,
#                             ip=info.get("ip", "Unknown"),
#                             latency=raw_lat,
#                             color=color,
#                         )
#                         self._state_last_alert[node] = now
#             self._initialized = True
#             self._render_table()
#             return

#         # Subsequent runs: detect every state change
#         for node, info in states.items():
#             # 🔥 ML ALERT (REAL-TIME + COOLDOWN)
#             ml_prob = info.get("ml_probability")
#             try:
#                 ml_prob = float(ml_prob) if ml_prob is not None else None
#             except (TypeError, ValueError):
#                 ml_prob = None

#             now_ts = datetime.now()

#             if ml_prob is not None and ml_prob > 0.7:
#                 last = self._ml_last_alert.get(node)

#                 if not last or (now_ts - last).total_seconds() > 10:
#                     self._all_events.insert(
#                         0, (now_ts, node, "AI", info.get("latency"))
#                     )
#                     if self._notifications_enabled:
#                         AlertPopup.fire(
#                             node_display=_fmt_node(node),
#                             state="AI",
#                             ip=info.get("ip"),
#                             latency=info.get("latency"),
#                             color="#9b59b6",
#                         )
#                     self._ml_last_alert[node] = now_ts

#             current = info.get("state", "UNKNOWN")
#             previous = self._prev_states.get(node)
#             raw_lat = info.get("latency") or info.get("last_latency")
#             state_alert_cooldown = 30
#             last_state_alert = self._state_last_alert.get(node)
#             state_alert_expired = (
#                 last_state_alert is None
#                 or (now - last_state_alert).total_seconds() > state_alert_cooldown
#             )

#             if previous is None and current in ("DOWN", "DEGRADED"):
#                 self._all_events.insert(0, (now, node, current, raw_lat))
#                 if self._notifications_enabled:
#                     sev_label, color, icon = _SEV[current]
#                     AlertPopup.fire(
#                         node_display=_fmt_node(node),
#                         state=current,
#                         ip=info.get("ip", "Unknown"),
#                         latency=raw_lat,
#                         color=color,
#                     )
#                 self._state_last_alert[node] = now

#             elif previous is not None and previous != current:
#                 self._all_events.insert(0, (now, node, current, raw_lat))
#                 if current in _SEV:
#                     sev_label, color, icon = _SEV[current]
#                     if self._notifications_enabled:
#                         AlertPopup.fire(
#                             node_display=_fmt_node(node),
#                             state=current,
#                             ip=info.get("ip", "Unknown"),
#                             latency=raw_lat,
#                             color=color,
#                         )
#                 if current in ("DOWN", "DEGRADED"):
#                     self._state_last_alert[node] = now
#                 else:
#                     self._state_last_alert.pop(node, None)

#             elif (
#                 previous == current
#                 and current in ("DOWN", "DEGRADED")
#                 and state_alert_expired
#             ):
#                 self._all_events.insert(0, (now, node, current, raw_lat))
#                 if self._notifications_enabled:
#                     sev_label, color, icon = _SEV[current]
#                     AlertPopup.fire(
#                         node_display=_fmt_node(node),
#                         state=current,
#                         ip=info.get("ip", "Unknown"),
#                         latency=raw_lat,
#                         color=color,
#                     )
#                 self._state_last_alert[node] = now

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
#         }.get(self._active_time_filter, None)

#     def _render_table(self):
#         cutoff = self._cutoff()

#         # Filter by time first
#         time_filtered = [
#             e for e in self._all_events if cutoff is None or e[0] >= cutoff
#         ]

#         # Then filter by alert type
#         if self._active_type_filter == "All Types":
#             events = time_filtered
#         else:
#             type_map = {
#                 "Critical": ["DOWN"],
#                 "Warning": ["DEGRADED"],
#                 "Recovered": ["UP"],
#                 "AI": ["AI"],
#             }
#             allowed_states = type_map.get(self._active_type_filter, [])
#             events = [e for e in time_filtered if e[2] in allowed_states]

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
#         # 🔴 Notification badge logic (ADD HERE)
#         if n > 0:
#             self._badge.show()
#         else:
#             self._badge.hide()







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
#     QComboBox,
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
#     "AI": ("AI ALERT", "#9b59b6", "⬤"),
# }

# _COLS = ["Time", "Node", "Event", "Severity", "Latency"]

# # Fixed popup height — used for stacking BEFORE the widget is rendered
# _POPUP_HEIGHT = 220


# # ─────────────────────────────────────────
# # Alert Popup
# # ─────────────────────────────────────────
# class AlertPopup(QWidget):
#     AUTO_CLOSE_SEC = 8
#     _active = []  # keeps references so GC doesn't destroy popups

#     def __init__(self, node_display: str, state: str, ip: str, latency, color: str):
#         super().__init__(
#             None, Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
#         )
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.setAttribute(Qt.WA_ShowWithoutActivating)
#         self._remaining = self.AUTO_CLOSE_SEC
#         self._bar_full_width = 324
#         self._build_ui(node_display, state, ip, latency, color)
#         # NOTE: _position() is called in fire() AFTER show() so height() is real

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

#         # Header row
#         hdr = QHBoxLayout()
#         if state == "DOWN":
#             icon_txt, title_txt = "🚨", "CRITICAL ALERT"
#             body_txt = (
#                 "This node is unreachable. Check the device and network connection."
#             )
#             node_title = f"Node {node_display} Failed"
#         elif state == "DEGRADED":
#             icon_txt, title_txt = "⚠️", "WARNING"
#             body_txt = "This node is responding slowly. Performance may be degraded."
#             node_title = f"Node {node_display} Degraded"

#         elif state == "AI":
#             icon_txt, title_txt = "🧠", "AI PREDICTION"
#             body_txt = "ML model predicts this node may fail soon. Monitor closely."
#             node_title = f"Node {node_display} — Failure Risk High"

#         else:  # UP / RECOVERED
#             icon_txt, title_txt = "✅", "RECOVERED"
#             body_txt = "This node is back online and responding normally."
#             node_title = f"Node {node_display} Recovered"

#         icon_lbl = QLabel(icon_txt)
#         icon_lbl.setStyleSheet(
#             f"font-size: 22px; color: {color}; background: transparent; border: none;"
#         )

#         title_col = QVBoxLayout()
#         title_col.setSpacing(1)
#         sev_lbl = QLabel(title_txt)
#         sev_lbl.setStyleSheet(
#             f"color:{color}; font-size:11px; font-weight:700; letter-spacing:1px; background:transparent; border:none;"
#         )
#         node_lbl = QLabel(node_title)
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
#         msg = QLabel(body_txt)
#         msg.setWordWrap(True)
#         msg.setStyleSheet(
#             f"color:{TEXT_SECONDARY}; font-size:11px; background:transparent; border:none;"
#         )
#         lay.addWidget(msg)

#         # Countdown progress bar
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
#         """Position popup in bottom-right corner, stacking above previous ones."""
#         screen = QApplication.primaryScreen().availableGeometry()
#         # Use actual height if available, fall back to fixed estimate
#         h = self.height() if self.height() > 10 else _POPUP_HEIGHT
#         offset = len(AlertPopup._active) * (h + 10)
#         self.move(
#             screen.right() - self.width() - 24,
#             screen.bottom() - h - 24 - offset,
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
#         print(
#             f"[AlertPopup.fire] node={node_display}, state={state}, ip={ip}, color={color}"
#         )
#         p = AlertPopup(node_display, state, ip, latency, color)
#         AlertPopup._active.append(
#             p
#         )  # append BEFORE show so _position sees correct count
#         p.show()
#         p._position()  # ← FIXED: called AFTER show() so height() is real
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
#         self._initialized = False
#         self._ml_last_alert = {}
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

#         # Filter tabs - Alert Type dropdown and Time dropdown
#         tabs_row = QHBoxLayout()
#         tabs_row.setSpacing(8)
#         self._tab_btns = {}

#         # Alert type dropdown
#         type_label = QLabel("Type:")
#         type_label.setStyleSheet(
#             f"font-size:11px; color:{TEXT_SECONDARY}; font-weight:600; background:transparent; border:none;"
#         )
#         tabs_row.addWidget(type_label)

#         self._type_combo = QComboBox()
#         self._type_combo.addItems(
#             ["All Types", "Critical", "Warning", "Recovered", "AI"]
#         )
#         self._type_combo.setCurrentText("All Types")
#         self._type_combo.setFixedWidth(120)
#         self._type_combo.setStyleSheet(f"""
#             QComboBox {{
#                 background: {BG_CARD};
#                 border: 1px solid {BORDER};
#                 border-radius: 10px;
#                 color: {TEXT_PRIMARY};
#                 padding: 8px 12px;
#                 font-size: 12px;
#                 font-weight: 500;
#                 min-height: 32px;
#                 outline: none;
#             }}
#             QComboBox::drop-down {{
#                 border: none;
#                 width: 28px;
#                 padding-right: 8px;
#                 subcontrol-origin: padding;
#                 subcontrol-position: center right;
#             }}
#             QComboBox::down-arrow {{
#                 image: none;
#                 border: none;
#                 width: 0;
#                 height: 0;
#                 border-left: 4px solid transparent;
#                 border-right: 4px solid transparent;
#                 border-top: 5px solid {TEXT_SECONDARY};
#                 margin-top: 2px;
#             }}
#             QComboBox:hover {{
#                 border-color: {ACCENT};
#                 background: linear-gradient(135deg, #1e2130 0%, #252836 100%);
#             }}
#             QComboBox:hover::down-arrow {{
#                 border-top-color: {ACCENT};
#             }}
#             QComboBox::drop-down:hover {{
#                 background: transparent;
#             }}
#             QComboBox:focus {{
#                 border-color: {ACCENT};
#             }}
#             QComboBox QAbstractItemView {{
#                 background: linear-gradient(135deg, {BG_CARD} 0%, #1a1d2e 100%);
#                 border: 1px solid {BORDER};
#                 border-radius: 8px;
#                 color: {TEXT_PRIMARY};
#                 selection-background-color: {ACCENT};
#                 selection-color: white;
#                 padding: 6px;
#                 outline: none;
#             }}
#             QComboBox QAbstractItemView::item {{
#                 padding: 8px 12px;
#                 border-radius: 4px;
#                 margin: 1px;
#                 font-size: 12px;
#             }}
#             QComboBox QAbstractItemView::item:hover {{
#                 background: rgba(79,142,247,0.1);
#                 color: {TEXT_PRIMARY};
#             }}
#             QComboBox QAbstractItemView::item:selected {{
#                 background: {ACCENT};
#                 color: white;
#             }}
#         """)
#         self._type_combo.currentTextChanged.connect(self._on_type_filter_changed)
#         tabs_row.addWidget(self._type_combo)

#         # Separator
#         sep = QFrame()
#         sep.setFrameShape(QFrame.VLine)
#         sep.setFrameShadow(QFrame.Sunken)
#         sep.setStyleSheet(f"color: {BORDER}; margin: 0 4px;")
#         tabs_row.addWidget(sep)

#         # Time dropdown
#         time_label = QLabel("Time:")
#         time_label.setStyleSheet(
#             f"font-size:11px; color:{TEXT_SECONDARY}; font-weight:600; background:transparent; border:none;"
#         )
#         tabs_row.addWidget(time_label)

#         self._time_combo = QComboBox()
#         self._time_combo.addItems(["All Time", "1 Day", "7 Days", "30 Days"])
#         self._time_combo.setCurrentText("All Time")
#         self._time_combo.setFixedWidth(110)
#         self._time_combo.setStyleSheet(f"""
#             QComboBox {{
#                 background: {BG_CARD};
#                 border: 1px solid {BORDER};
#                 border-radius: 10px;
#                 color: {TEXT_PRIMARY};
#                 padding: 8px 12px;
#                 font-size: 12px;
#                 font-weight: 500;
#                 min-height: 32px;
#                 outline: none;
#             }}
#             QComboBox::drop-down {{
#                 border: none;
#                 width: 28px;
#                 padding-right: 8px;
#                 subcontrol-origin: padding;
#                 subcontrol-position: center right;
#             }}
#             QComboBox::down-arrow {{
#                 image: none;
#                 border: none;
#                 width: 0;
#                 height: 0;
#                 border-left: 4px solid transparent;
#                 border-right: 4px solid transparent;
#                 border-top: 5px solid {TEXT_SECONDARY};
#                 margin-top: 2px;
#             }}
#             QComboBox:hover {{
#                 border-color: {ACCENT};
#                 background: linear-gradient(135deg, #1e2130 0%, #252836 100%);
#             }}
#             QComboBox:hover::down-arrow {{
#                 border-top-color: {ACCENT};
#             }}
#             QComboBox::drop-down:hover {{
#                 background: transparent;
#             }}
#             QComboBox:focus {{
#                 border-color: {ACCENT};
#             }}
#             QComboBox QAbstractItemView {{
#                 background: linear-gradient(135deg, {BG_CARD} 0%, #1a1d2e 100%);
#                 border: 1px solid {BORDER};
#                 border-radius: 8px;
#                 color: {TEXT_PRIMARY};
#                 selection-background-color: {ACCENT};
#                 selection-color: white;
#                 padding: 6px;
#                 outline: none;
#             }}
#             QComboBox QAbstractItemView::item {{
#                 padding: 8px 12px;
#                 border-radius: 4px;
#                 margin: 1px;
#                 font-size: 12px;
#             }}
#             QComboBox QAbstractItemView::item:hover {{
#                 background: rgba(79,142,247,0.1);
#                 color: {TEXT_PRIMARY};
#             }}
#             QComboBox QAbstractItemView::item:selected {{
#                 background: {ACCENT};
#                 color: white;
#             }}
#         """)
#         self._time_combo.currentTextChanged.connect(self._on_time_filter_changed)
#         tabs_row.addWidget(self._time_combo)

#         tabs_row.addStretch()

#         # Circular notification toggle button
#         self._notifications_enabled = True
#         self._notify_btn = QPushButton("🔔")
#         self._notify_btn.setFixedSize(44, 44)
#         self._notify_btn.setCursor(Qt.PointingHandCursor)
#         self._notify_btn.clicked.connect(self._toggle_notifications)

#         self._badge = QLabel("●", self._notify_btn)
#         self._badge.setStyleSheet(
#             "background: #ff4d4f; color: transparent; border-radius: 5px;"
#         )
#         self._badge.setFixedSize(10, 10)
#         self._badge.move(30, 6)
#         self._badge.hide()

#         tabs_row.addWidget(self._notify_btn)

#         lay.addLayout(tabs_row)

#         self._active_type_filter = "All Types"
#         self._active_time_filter = "All Time"

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
#         self._update_notify_button_style()

#     def _on_type_filter_changed(self, text):
#         self._active_type_filter = text
#         self._render_table()

#     def _on_time_filter_changed(self, text):
#         self._active_time_filter = text
#         self._render_table()

#     def _update_notify_button_style(self):
#         if self._notifications_enabled:
#             bg = "#2ecc71"
#             icon = "🔔"
#         else:
#             bg = "#555b6e"
#             icon = "🔕"

#         self._notify_btn.setText(icon)
#         self._notify_btn.setStyleSheet(f"""
#             QPushButton {{
#                 background: {bg};
#                 border-radius: 22px;
#                 font-size: 18px;
#                 font-weight: bold;
#                 border: none;
#                 color: white;
#                 padding: 0px;
#             }}
#             QPushButton:hover {{
#                 background: #2c3142;
#             }}
#         """)

#     def _toggle_notifications(self):
#         self._notifications_enabled = not self._notifications_enabled
#         self._update_notify_button_style()

#     def update_alerts(self, states: dict):
#         now = datetime.now()
#         print(
#             f"[AlertsPanel] update_alerts called with {len(states)} nodes. Initialized={self._initialized}"
#         )
#         for node, info in states.items():
#             print(
#                 f"  {node}: state={info.get('state')}, prev={self._prev_states.get(node)}, ml_prob={info.get('ml_probability')}"
#             )

#         if not self._initialized:
#             # First run: seed _prev_states silently
#             # But fire popups + log events for nodes already DOWN/DEGRADED
#             for node, info in states.items():
#                 current = info.get("state", "UNKNOWN")
#                 self._prev_states[node] = current
#                 if current in ("DOWN", "DEGRADED"):
#                     raw_lat = info.get("latency")
#                     self._all_events.insert(0, (now, node, current, raw_lat))
#                     sev_label, color, icon = _SEV[current]
#                     if self._notifications_enabled:
#                         try:
#                             print(
#                                 f"[AlertInit] Firing popup for {node} state={current}"
#                             )
#                             AlertPopup.fire(
#                                 node_display=_fmt_node(node),
#                                 state=current,
#                                 ip=info.get("ip", "Unknown"),
#                                 latency=raw_lat,
#                                 color=color,
#                             )
#                             print(f"[AlertInit] Popup fired successfully")
#                         except Exception as e:
#                             print(f"[ERROR AlertInit] Exception: {e}", file=sys.stderr)
#                             import traceback

#                             traceback.print_exc()
#             self._initialized = True
#             self._render_table()
#             return

#         # Subsequent runs: detect every state change
#         for node, info in states.items():
#             # 🔥 ML ALERT (REAL-TIME + COOLDOWN)
#             ml_prob = info.get("ml_probability")
#             try:
#                 ml_prob = float(ml_prob) if ml_prob is not None else None
#             except (TypeError, ValueError):
#                 ml_prob = None

#             now_ts = datetime.now()

#             if ml_prob is not None and ml_prob > 0.7:
#                 last = self._ml_last_alert.get(node)

#                 if not last or (now_ts - last).total_seconds() > 10:
#                     if self._notifications_enabled:
#                         AlertPopup.fire(
#                             node_display=_fmt_node(node),
#                             state="AI",
#                             ip=info.get("ip"),
#                             latency=info.get("latency"),
#                             color="#9b59b6",
#                         )
#                     self._ml_last_alert[node] = now_ts  # ✅ FIXED (INSIDE IF)

#             current = info.get("state", "UNKNOWN")
#             previous = self._prev_states.get(node)

#             if previous is None and current in ("DOWN", "DEGRADED"):
#                 # New node discovered after GUI startup may not have a prior state.
#                 raw_lat = info.get("latency") or info.get("last_latency")
#                 self._all_events.insert(0, (now, node, current, raw_lat))
#                 if self._notifications_enabled:
#                     sev_label, color, icon = _SEV[current]
#                     AlertPopup.fire(
#                         node_display=_fmt_node(node),
#                         state=current,
#                         ip=info.get("ip", "Unknown"),
#                         latency=raw_lat,
#                         color=color,
#                     )

#             elif previous is not None and previous != current:
#                 raw_lat = info.get("latency") or info.get("last_latency")
#                 self._all_events.insert(0, (now, node, current, raw_lat))

#                 # Fire popup for ALL transitions (DOWN, DEGRADED, and RECOVERED)
#                 if current in _SEV:
#                     sev_label, color, icon = _SEV[current]
#                     if self._notifications_enabled:
#                         AlertPopup.fire(
#                             node_display=_fmt_node(node),
#                             state=current,
#                             ip=info.get("ip", "Unknown"),
#                             latency=raw_lat,
#                             color=color,
#                         )

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
#         }.get(self._active_time_filter, None)

#     def _render_table(self):
#         cutoff = self._cutoff()

#         # Filter by time first
#         time_filtered = [
#             e for e in self._all_events if cutoff is None or e[0] >= cutoff
#         ]

#         # Then filter by alert type
#         if self._active_type_filter == "All Types":
#             events = time_filtered
#         else:
#             type_map = {
#                 "Critical": ["DOWN"],
#                 "Warning": ["DEGRADED"],
#                 "Recovered": ["UP"],
#                 "AI": ["AI"],
#             }
#             allowed_states = type_map.get(self._active_type_filter, [])
#             events = [e for e in time_filtered if e[2] in allowed_states]

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
#         # 🔴 Notification badge logic (ADD HERE)
#         if n > 0:
#             self._badge.show()
#         else:
#             self._badge.hide()


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
    QComboBox,
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
    "AI": ("AI ALERT", "#9b59b6", "⬤"),
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

        elif state == "AI":
            icon_txt, title_txt = "🧠", "AI PREDICTION"
            body_txt = "ML model predicts this node may fail soon. Monitor closely."
            node_title = f"Node {node_display} — Failure Risk High"

        else:  # UP / RECOVERED
            icon_txt, title_txt = "✅", "RECOVERED"
            body_txt = "This node is back online and responding normally."
            node_title = f"Node {node_display} Recovered"

        icon_lbl = QLabel(icon_txt)
        icon_lbl.setStyleSheet(
            f"font-size: 22px; color: {color}; background: transparent; border: none;"
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

    MAX_ACTIVE = 3  # never show more than 3 popups at once

    @staticmethod
    def fire(node_display: str, state: str, ip: str, latency, color: str):
        # If we already have MAX_ACTIVE popups, close the oldest one first
        # so new alerts are always visible and never pushed off screen
        while len(AlertPopup._active) >= AlertPopup.MAX_ACTIVE:
            oldest = AlertPopup._active[0]
            try:
                oldest._tick.stop()
                oldest.close()
            except Exception:
                pass
            if oldest in AlertPopup._active:
                AlertPopup._active.remove(oldest)

        p = AlertPopup(node_display, state, ip, latency, color)
        AlertPopup._active.append(
            p
        )  # append BEFORE show so _position sees correct count
        p.show()
        p._position()  # called AFTER show() so height() is real
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
        self._ml_last_alert = {}
        self._state_last_alert = {}  # tracks last DOWN/DEGRADED alert timestamp per node
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

        # Filter tabs - Alert Type dropdown and Time dropdown
        tabs_row = QHBoxLayout()
        tabs_row.setSpacing(8)
        self._tab_btns = {}

        # Alert type dropdown
        type_label = QLabel("Type:")
        type_label.setStyleSheet(
            f"font-size:11px; color:{TEXT_SECONDARY}; font-weight:600; background:transparent; border:none;"
        )
        tabs_row.addWidget(type_label)

        self._type_combo = QComboBox()
        self._type_combo.addItems(
            ["All Types", "Critical", "Warning", "Recovered", "AI"]
        )
        self._type_combo.setCurrentText("All Types")
        self._type_combo.setFixedWidth(120)
        self._type_combo.setStyleSheet(f"""
            QComboBox {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
                color: {TEXT_PRIMARY};
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                min-height: 32px;
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 28px;
                padding-right: 8px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {TEXT_SECONDARY};
                margin-top: 2px;
            }}
            QComboBox:hover {{
                border-color: {ACCENT};
                background: linear-gradient(135deg, #1e2130 0%, #252836 100%);
            }}
            QComboBox:hover::down-arrow {{
                border-top-color: {ACCENT};
            }}
            QComboBox::drop-down:hover {{
                background: transparent;
            }}
            QComboBox:focus {{
                border-color: {ACCENT};
            }}
            QComboBox QAbstractItemView {{
                background: linear-gradient(135deg, {BG_CARD} 0%, #1a1d2e 100%);
                border: 1px solid {BORDER};
                border-radius: 8px;
                color: {TEXT_PRIMARY};
                selection-background-color: {ACCENT};
                selection-color: white;
                padding: 6px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
                font-size: 12px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: rgba(79,142,247,0.1);
                color: {TEXT_PRIMARY};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background: {ACCENT};
                color: white;
            }}
        """)
        self._type_combo.currentTextChanged.connect(self._on_type_filter_changed)
        tabs_row.addWidget(self._type_combo)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.VLine)
        sep.setFrameShadow(QFrame.Sunken)
        sep.setStyleSheet(f"color: {BORDER}; margin: 0 4px;")
        tabs_row.addWidget(sep)

        # Time dropdown
        time_label = QLabel("Time:")
        time_label.setStyleSheet(
            f"font-size:11px; color:{TEXT_SECONDARY}; font-weight:600; background:transparent; border:none;"
        )
        tabs_row.addWidget(time_label)

        self._time_combo = QComboBox()
        self._time_combo.addItems(["All Time", "1 Day", "7 Days", "30 Days"])
        self._time_combo.setCurrentText("All Time")
        self._time_combo.setFixedWidth(110)
        self._time_combo.setStyleSheet(f"""
            QComboBox {{
                background: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
                color: {TEXT_PRIMARY};
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                min-height: 32px;
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 28px;
                padding-right: 8px;
                subcontrol-origin: padding;
                subcontrol-position: center right;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid {TEXT_SECONDARY};
                margin-top: 2px;
            }}
            QComboBox:hover {{
                border-color: {ACCENT};
                background: linear-gradient(135deg, #1e2130 0%, #252836 100%);
            }}
            QComboBox:hover::down-arrow {{
                border-top-color: {ACCENT};
            }}
            QComboBox::drop-down:hover {{
                background: transparent;
            }}
            QComboBox:focus {{
                border-color: {ACCENT};
            }}
            QComboBox QAbstractItemView {{
                background: linear-gradient(135deg, {BG_CARD} 0%, #1a1d2e 100%);
                border: 1px solid {BORDER};
                border-radius: 8px;
                color: {TEXT_PRIMARY};
                selection-background-color: {ACCENT};
                selection-color: white;
                padding: 6px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
                font-size: 12px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: rgba(79,142,247,0.1);
                color: {TEXT_PRIMARY};
            }}
            QComboBox QAbstractItemView::item:selected {{
                background: {ACCENT};
                color: white;
            }}
        """)
        self._time_combo.currentTextChanged.connect(self._on_time_filter_changed)
        tabs_row.addWidget(self._time_combo)

        tabs_row.addStretch()

        # Circular notification toggle button
        self._notifications_enabled = True
        self._notify_btn = QPushButton("🔔")
        self._notify_btn.setFixedSize(44, 44)
        self._notify_btn.setCursor(Qt.PointingHandCursor)
        self._notify_btn.clicked.connect(self._toggle_notifications)

        self._badge = QLabel("●", self._notify_btn)
        self._badge.setStyleSheet(
            "background: #ff4d4f; color: transparent; border-radius: 5px;"
        )
        self._badge.setFixedSize(10, 10)
        self._badge.move(30, 6)
        self._badge.hide()

        tabs_row.addWidget(self._notify_btn)

        lay.addLayout(tabs_row)

        self._active_type_filter = "All Types"
        self._active_time_filter = "All Time"

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
        self._update_notify_button_style()

    def _on_type_filter_changed(self, text):
        self._active_type_filter = text
        self._render_table()

    def _on_time_filter_changed(self, text):
        self._active_time_filter = text
        self._render_table()

    def _update_notify_button_style(self):
        if self._notifications_enabled:
            bg = "#2ecc71"
            icon = "🔔"
        else:
            bg = "#555b6e"
            icon = "🔕"

        self._notify_btn.setText(icon)
        self._notify_btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                border-radius: 22px;
                font-size: 18px;
                font-weight: bold;
                border: none;
                color: white;
                padding: 0px;
            }}
            QPushButton:hover {{
                background: #2c3142;
            }}
        """)

    def _toggle_notifications(self):
        self._notifications_enabled = not self._notifications_enabled
        self._update_notify_button_style()

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
                    if self._notifications_enabled:
                        sev_label, color, icon = _SEV[current]
                        AlertPopup.fire(
                            node_display=_fmt_node(node),
                            state=current,
                            ip=info.get("ip", "Unknown"),
                            latency=raw_lat,
                            color=color,
                        )
                        # Do NOT set _state_last_alert here — we want the 30s
                        # repeat-alert timer to start fresh from login, not be
                        # blocked by the initialization popup.
            self._initialized = True
            self._render_table()
            return

        # Subsequent runs: detect every state change
        for node, info in states.items():
            # 🔥 ML ALERT (REAL-TIME + COOLDOWN)
            ml_prob = info.get("ml_probability")
            try:
                ml_prob = float(ml_prob) if ml_prob is not None else None
            except (TypeError, ValueError):
                ml_prob = None

            now_ts = datetime.now()

            if ml_prob is not None and ml_prob > 0.7:
                last = self._ml_last_alert.get(node)

                if not last or (now_ts - last).total_seconds() > 10:
                    self._all_events.insert(
                        0, (now_ts, node, "AI", info.get("latency"))
                    )
                    if self._notifications_enabled:
                        AlertPopup.fire(
                            node_display=_fmt_node(node),
                            state="AI",
                            ip=info.get("ip"),
                            latency=info.get("latency"),
                            color="#9b59b6",
                        )
                    self._ml_last_alert[node] = now_ts

            current = info.get("state", "UNKNOWN")
            previous = self._prev_states.get(node)
            raw_lat = info.get("latency") or info.get("last_latency")
            state_alert_cooldown = 30
            last_state_alert = self._state_last_alert.get(node)
            state_alert_expired = (
                last_state_alert is None
                or (now - last_state_alert).total_seconds() > state_alert_cooldown
            )

            if previous is None and current in ("DOWN", "DEGRADED"):
                self._all_events.insert(0, (now, node, current, raw_lat))
                if self._notifications_enabled:
                    sev_label, color, icon = _SEV[current]
                    AlertPopup.fire(
                        node_display=_fmt_node(node),
                        state=current,
                        ip=info.get("ip", "Unknown"),
                        latency=raw_lat,
                        color=color,
                    )
                self._state_last_alert[node] = now

            elif previous is not None and previous != current:
                self._all_events.insert(0, (now, node, current, raw_lat))
                if current in _SEV:
                    sev_label, color, icon = _SEV[current]
                    # Per-node cooldown on state-change popups: 30s minimum between
                    # popups for the same node. Prevents sim node flapping from flooding.
                    last_any = self._state_last_alert.get(node)
                    change_ok = (
                        last_any is None or (now - last_any).total_seconds() > 30
                    )
                    if self._notifications_enabled and change_ok:
                        AlertPopup.fire(
                            node_display=_fmt_node(node),
                            state=current,
                            ip=info.get("ip", "Unknown"),
                            latency=raw_lat,
                            color=color,
                        )
                        self._state_last_alert[node] = now
                if current in ("DOWN", "DEGRADED"):
                    pass  # already set above
                else:
                    self._state_last_alert.pop(node, None)

            elif (
                previous == current
                and current in ("DOWN", "DEGRADED")
                and state_alert_expired
            ):
                self._all_events.insert(0, (now, node, current, raw_lat))
                if self._notifications_enabled:
                    sev_label, color, icon = _SEV[current]
                    AlertPopup.fire(
                        node_display=_fmt_node(node),
                        state=current,
                        ip=info.get("ip", "Unknown"),
                        latency=raw_lat,
                        color=color,
                    )
                self._state_last_alert[node] = now

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
        }.get(self._active_time_filter, None)

    def _render_table(self):
        cutoff = self._cutoff()

        # Filter by time first
        time_filtered = [
            e for e in self._all_events if cutoff is None or e[0] >= cutoff
        ]

        # Then filter by alert type
        if self._active_type_filter == "All Types":
            events = time_filtered
        else:
            type_map = {
                "Critical": ["DOWN"],
                "Warning": ["DEGRADED"],
                "Recovered": ["UP"],
                "AI": ["AI"],
            }
            allowed_states = type_map.get(self._active_type_filter, [])
            events = [e for e in time_filtered if e[2] in allowed_states]

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
        # 🔴 Notification badge logic (ADD HERE)
        if n > 0:
            self._badge.show()
        else:
            self._badge.hide()