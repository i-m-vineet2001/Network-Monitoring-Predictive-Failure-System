# gui/summary.py
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt
from gui.theme import (
    BG_CARD,
    BORDER,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    SUCCESS,
    WARNING,
    DANGER,
    ACCENT,
)


class _StatCard(QFrame):
    """A single stat card: icon + value + label."""

    def __init__(self, icon: str, value: str, label: str, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(f"""
            QFrame#card {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
                padding: 4px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(
            f"font-size: 22px; color: {color}; background: transparent; border: none;"
        )

        self.value_lbl = QLabel(value)
        self.value_lbl.setAlignment(Qt.AlignCenter)
        self.value_lbl.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {color}; background: transparent; border: none;"
        )

        label_lbl = QLabel(label)
        label_lbl.setAlignment(Qt.AlignCenter)
        label_lbl.setStyleSheet(
            f"font-size: 11px; color: {TEXT_SECONDARY}; background: transparent; border: none;"
        )

        layout.addWidget(icon_lbl)
        layout.addWidget(self.value_lbl)
        layout.addWidget(label_lbl)

    def set_value(self, value: str, color: str = None):
        self.value_lbl.setText(value)
        if color:
            self.value_lbl.setStyleSheet(
                f"font-size: 22px; font-weight: 700; color: {color}; background: transparent; border: none;"
            )


class HealthSummaryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        self._total = _StatCard("🖥", "—", "Total Nodes", TEXT_PRIMARY)
        self._up = _StatCard("✅", "—", "Online", SUCCESS)
        self._degraded = _StatCard("⚠️", "—", "Degraded", WARNING)
        self._down = _StatCard("🔴", "—", "Offline", DANGER)
        self._latency = _StatCard("⚡", "—", "Avg Latency", ACCENT)
        self._risk = _StatCard("🧠", "—", "High Risk", TEXT_SECONDARY)

        for card in [
            self._total,
            self._up,
            self._degraded,
            self._down,
            self._latency,
            self._risk,
        ]:
            layout.addWidget(card)

    def update_summary(self, states: dict):
        if not states:
            return

        total = len(states)
        up = degraded = down = 0
        lat_sum = lat_cnt = 0

        high_risk = 0

        for n in states.values():
            try:
                if float(n.get("ml_probability", 0)) > 0.6:
                    high_risk += 1
            except:
                pass

        for info in states.values():
            s = info["state"]
            if s == "UP":
                up += 1
            elif s == "DEGRADED":
                degraded += 1
            elif s == "DOWN":
                down += 1
            try:
                lat_sum += float(info["latency"])
                lat_cnt += 1
            except (TypeError, ValueError):
                pass

        avg_lat = f"{lat_sum / lat_cnt:.1f} ms" if lat_cnt else "— ms"

        self._total.set_value(str(total))
        self._up.set_value(str(up))
        self._degraded.set_value(str(degraded), WARNING if degraded else TEXT_SECONDARY)
        self._down.set_value(str(down), DANGER if down else TEXT_SECONDARY)
        self._latency.set_value(avg_lat)
        if high_risk > 0:
            color = "#9b59b6"
        else:
            color = TEXT_SECONDARY

        self._risk.set_value(str(high_risk), color)
