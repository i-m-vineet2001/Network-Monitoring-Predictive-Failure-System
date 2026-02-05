from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtGui import QColor
from datetime import datetime


class AlertsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("Alerts")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")

        self.counter_label = QLabel("Total: 0")
        self.counter_label.setStyleSheet("font-size: 12px; color: #888;")

        self.list_widget = QListWidget()

        layout.addWidget(title)
        layout.addWidget(self.counter_label)
        layout.addWidget(self.list_widget)

        self.previous_states = {}

        # LIMIT alerts
        self.max_alerts = 100

    def update_alerts(self, states):
        current_time = datetime.now().strftime("%H:%M:%S")

        for node, info in states.items():
            current = info["state"]
            previous = self.previous_states.get(node)

            if previous and previous != current:
                if current == "DOWN":
                    severity = "CRITICAL"
                    color = QColor("#e74c3c")
                    status = "DOWN"

                elif current == "DEGRADED":
                    severity = "WARNING"
                    color = QColor("#f1c40f")
                    status = "DEGRADED"

                elif current == "UP":
                    severity = "INFO"
                    color = QColor("#2ecc71")
                    status = "RECOVERED"
                else:
                    return

                message = f"{current_time}  [{severity}]  {node}    {status}"

                item = QListWidgetItem(message)
                font = item.font()
                if severity == "CRITICAL":
                    font.setBold(True)
                item.setFont(font)

                item.setForeground(color)

                # insert at top
                self.list_widget.insertItem(0, item)

                # Remove old alerts if exceeding limit
                if self.list_widget.count() > self.max_alerts:
                    self.list_widget.takeItem(self.list_widget.count() - 1)

                # Update counter
                self.counter_label.setText(f"Total: {self.list_widget.count()}")

            self.previous_states[node] = current
