# sidebar, panels

# gui/widgets.py
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMessageBox
from PySide6.QtGui import QBrush, QColor


class NodeListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)
        self.previous_states = {}

    def refresh(self, states, parent_window):
        self.clear()

        for node, info in states.items():
            state = info["state"]

            # choose color
            if state == "UP":
                color = QColor("#2ecc71")  # green
            elif state == "DEGRADED":
                color = QColor("#f1c40f")  # yellow
            else:
                color = QColor("#e74c3c")  # red

            item = QListWidgetItem(f"●  {node} {state}")
            item.setForeground(QBrush(color))
            self.addItem(item)

            # alert on transition → DOWN
            prev = self.previous_states.get(node)
            if state == "DOWN" and prev != "DOWN":
                QMessageBox.warning(
                    parent_window,
                    "Node DOWN Alert",
                    f"Node: {node}\nIP: {info['ip']}\nStatus: DOWN",
                )

            self.previous_states[node] = state
