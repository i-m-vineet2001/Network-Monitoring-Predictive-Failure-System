# gui/gui.py
import sys, os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, "src"))

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QFrame,
)
from PySide6.QtCore import QTimer, Qt

# ── local gui imports (same folder) ──
from gui.chart import LatencyChart, GlobalLatencyChart
from gui.node_availability_chart import NodeAvailabilityChart
from gui.widgets import NodeListWidget
from gui.summary import HealthSummaryWidget
from gui.alerts import AlertsPanel
from gui.theme import (
    BG_DARK,
    BG_CARD,
    BG_SIDEBAR,
    BORDER,
    ACCENT,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    state_color,
)

# ── data lives in gui/data.py ──
from gui.data import (
    read_latest_node_states,
    get_node_latency_history,
    get_global_latency_history,
    get_node_state_distribution,
    get_global_state_distribution,
)


# ─────────────────────────────────────────
# Node detail card
# ─────────────────────────────────────────
class NodeDetailCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        # Header
        header = QHBoxLayout()
        self.name_lbl = QLabel("Select a node")
        self.name_lbl.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {TEXT_PRIMARY}; background: transparent; border: none;"
        )
        self.badge = QLabel("")
        self.badge.setFixedHeight(24)
        self.badge.setAlignment(Qt.AlignCenter)
        header.addWidget(self.name_lbl)
        header.addStretch()
        header.addWidget(self.badge)
        lay.addLayout(header)

        # Stat grid
        grid = QHBoxLayout()
        grid.setSpacing(8)
        self._ip = self._stat_box("IP", "—")
        self._net = self._stat_box("Type", "—")
        self._lat = self._stat_box("Latency", "—")
        self._fail = self._stat_box("Fails", "—")
        self._ml = self._stat_box("Risk", "—")
        for w in [self._ip, self._net, self._lat, self._fail, self._ml]:
            grid.addWidget(w)
        lay.addLayout(grid)

        self._hint = QLabel("Click a node on the left to view details")
        self._hint.setStyleSheet(
            f"color: {TEXT_MUTED}; font-size: 12px; background: transparent; border: none;"
        )
        lay.addWidget(self._hint)

    # ── helpers ──
    def _stat_box(self, label: str, value: str) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background: rgba(255,255,255,0.04);
                border: 1px solid {BORDER};
                border-radius: 8px;
            }}
        """)
        v = QVBoxLayout(f)
        v.setContentsMargins(10, 8, 10, 8)
        v.setSpacing(2)
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"font-size:10px; color:{TEXT_MUTED}; font-weight:600; background:transparent; border:none;"
        )
        val = QLabel(value)
        val.setObjectName("val")
        val.setStyleSheet(
            f"font-size:13px; font-weight:600; color:{TEXT_PRIMARY}; background:transparent; border:none;"
        )
        v.addWidget(lbl)
        v.addWidget(val)
        return f

    def _set(self, box: QFrame, value: str):
        box.findChild(QLabel, "val").setText(value)

    @staticmethod
    def _fmt_lat(lat) -> str:
        try:
            if lat is None or str(lat).strip().lower() == "none":
                return "0 ms"  # Show 0 ms for no data instead of "No data"
            return f"{float(lat):.1f} ms"
        except (TypeError, ValueError):
            return "0 ms"

    @staticmethod
    def _hex_rgb(h: str) -> str:
        h = h.lstrip("#")
        return f"{int(h[:2], 16)},{int(h[2:4], 16)},{int(h[4:], 16)}"

    def update_node(self, node_name: str, info: dict):
        if not info:
            return
        self._hint.hide()
        display = node_name.replace("node_", "").replace("_", " ").title()
        self.name_lbl.setText(display)

        state = info["state"]
        color = state_color(state)
        rgb = self._hex_rgb(color)
        self.badge.setText(f"  {state}  ")
        self.badge.setStyleSheet(f"""
            background: rgba({rgb},0.18);
            color: {color};
            border: 1px solid rgba({rgb},0.35);
            border-radius: 6px;
            font-size: 11px; font-weight: 700;
            padding: 0 8px;
        """)

        self._set(self._ip, info.get("ip", "—"))
        self._set(self._net, info.get("network_type", "—"))
        self._set(self._lat, self._fmt_lat(info.get("latency")))
        self._set(self._fail, str(info.get("fails", "—")))

        prob = info.get("ml_probability")
        try:
            prob = float(prob) if prob is not None else None
        except:
            prob = None
        # reset first
        self._set(self._ml, "⏳")

        # reset style
        self._ml.setStyleSheet(f"""
        QFrame {{
        background: rgba(255,255,255,0.04);
        border: 1px solid {BORDER};
        border-radius: 8px;
        }}
        """)

        if prob is not None:
            percent = prob * 100

            if prob > 0.6:
                text = f"🔴 {percent:.1f}%"
            elif prob > 0.3:
                text = f"🟡 {percent:.1f}%"
            else:
                text = f"🟢 {percent:.1f}%"

            # ✅ SET VALUE
            self._set(self._ml, text)

            # ✅ ADD BORDER (your question)
            if prob > 0.6:
                self._ml.setStyleSheet(
                    f""" border: 1px solid #e74c3c;border-radius: 8px; """
                )

            # ✅ ADD TOOLTIP (your question)
            if prob is not None:
                self._ml.setToolTip(f"Failure probability: {percent:.2f}%")
            else:
                self._ml.setToolTip("Waiting for prediction...")


# ─────────────────────────────────────────
# Main window
# ─────────────────────────────────────────
class NetworkMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Network Health Monitor")
        self.setMinimumSize(1200, 780)
        self.setStyleSheet(f"background-color: {BG_DARK};")

        self.selected_node: str | None = None
        self.states: dict = {}

        self._build_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_nodes)
        self.timer.start(2000)
        self.refresh_nodes()

    # ── layout ──
    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        root_lay = QHBoxLayout(root)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(0)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setFixedWidth(236)
        sidebar.setStyleSheet(
            f"background:{BG_SIDEBAR}; border-right:1px solid {BORDER};"
        )
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(12, 20, 12, 20)
        sb.setSpacing(12)

        app_title = QLabel("🌐  NetMonitor")
        app_title.setStyleSheet(
            f"font-size:17px; font-weight:700; color:{TEXT_PRIMARY}; background:transparent;"
        )
        app_sub = QLabel("Real-time network health")
        app_sub.setStyleSheet(
            f"font-size:11px; color:{TEXT_MUTED}; background:transparent;"
        )
        nodes_hdr = QLabel("NODES")
        nodes_hdr.setStyleSheet(
            f"font-size:10px; font-weight:700; color:{TEXT_MUTED}; letter-spacing:1px; background:transparent;"
        )

        self.node_list = NodeListWidget()
        self.node_list.itemClicked.connect(self._on_node_clicked)

        sb.addWidget(app_title)
        sb.addWidget(app_sub)
        sb.addSpacing(8)
        sb.addWidget(nodes_hdr)
        sb.addWidget(self.node_list)
        sb.addStretch()
        root_lay.addWidget(sidebar)

        # ── Main content ──
        content = QWidget()
        content.setStyleSheet(f"background:{BG_DARK};")
        c = QVBoxLayout(content)
        c.setContentsMargins(20, 20, 20, 20)
        c.setSpacing(14)

        self.summary = HealthSummaryWidget()
        c.addWidget(self.summary)

        self.global_chart = GlobalLatencyChart()
        self.global_chart.setFixedHeight(180)
        c.addWidget(self.global_chart)

        # Middle row
        mid = QHBoxLayout()
        mid.setSpacing(14)

        # Left column
        left = QVBoxLayout()
        left.setSpacing(14)
        self.detail_card = NodeDetailCard()
        left.addWidget(self.detail_card)
        self.latency_chart = LatencyChart()
        self.latency_chart.setFixedHeight(200)
        left.addWidget(self.latency_chart)
        self.pie_chart = NodeAvailabilityChart()
        self.pie_chart.setFixedHeight(220)
        left.addWidget(self.pie_chart)
        mid.addLayout(left, 3)

        # Right column — alerts only (no dropdown, tabs are inside AlertsPanel)
        right = QVBoxLayout()
        right.setSpacing(0)
        right.setContentsMargins(0, 0, 0, 0)

        self.alerts_panel = AlertsPanel()
        right.addWidget(self.alerts_panel)
        mid.addLayout(right, 2)

        c.addLayout(mid)
        root_lay.addWidget(content)

    # ── events ──
    def _on_node_clicked(self, item):
        # New delegate stores display name in UserRole+2, not item.text()
        from PySide6.QtCore import Qt as _Qt

        display = item.data(_Qt.UserRole + 2)
        if not display:
            # fallback: parse from text
            display = item.text().split("\n")[0].strip().lstrip("●").strip()

        for key in self.states:
            parts = key.replace("node_", "").split("_")
            if " ".join(p.capitalize() for p in parts) == display:
                self.selected_node = key
                break
        self._refresh_detail()

    def _refresh_detail(self):
        if not self.selected_node:
            # Show global stats when no node selected
            up, deg, dn = get_global_state_distribution()
            self.pie_chart.update_data(up, deg, dn)
            return
        info = self.states.get(self.selected_node)
        if not info:
            return
        self.detail_card.update_node(self.selected_node, info)
        self.latency_chart.update_data(get_node_latency_history(self.selected_node))
        up, deg, dn = get_node_state_distribution(self.selected_node)
        self.pie_chart.update_data(up, deg, dn)

    def refresh_nodes(self):
        self.states = read_latest_node_states()
        self.node_list.refresh(self.states, self)
        self.summary.update_summary(self.states)
        self.global_chart.update_data(get_global_latency_history())
        self.alerts_panel.update_alerts(self.states)
        self._refresh_detail()

    def _filter_changed(self):
        pass  # alerts panel now handles filtering via its own tab buttons
