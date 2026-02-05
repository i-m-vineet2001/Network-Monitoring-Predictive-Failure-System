# gui/summary.py

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class HealthSummaryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("Loading summary...")
        self.label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            padding: 8px;
        """)

        layout.addWidget(self.label)

    def update_summary(self, states: dict):
        if not states:
            self.label.setText("No nodes available")
            return

        total = len(states)
        up = 0
        degraded = 0
        down = 0
        latency_sum = 0
        latency_count = 0

        for node, info in states.items():
            state = info["state"]

            if state == "UP":
                up += 1
            elif state == "DEGRADED":
                degraded += 1
            elif state == "DOWN":
                down += 1

            try:
                latency = float(info["latency"])
                latency_sum += latency
                latency_count += 1
            except:
                pass

        avg_latency = latency_sum / latency_count if latency_count > 0 else 0

        text = (
            f"Nodes: {total}    "
            f"UP: {up}    "
            f"DEGRADED: {degraded}    "
            f"DOWN: {down}    "
            f"Avg Latency: {avg_latency:.1f} ms"
        )

        self.label.setText(text)
