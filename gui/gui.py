# # gui/gui.py
# import sys
# from PySide6.QtWidgets import (
#     QApplication,
#     QMainWindow,
#     QLabel,
#     QWidget,
#     QHBoxLayout,
# )
# from PySide6.QtWidgets import QVBoxLayout
# from data import get_node_latency_history
# from chart import LatencyChart
# from PySide6.QtCore import QTimer
# from widgets import NodeListWidget
# from data import read_latest_node_states
# from summary import HealthSummaryWidget
# from global_chart import GlobalLatencyChart
# from data import get_global_latency_history
# from alerts import AlertsPanel
# from node_availability_chart import NodeAvailabilityChart
# from data import get_node_state_distribution


# class NetworkMonitorGUI(QMainWindow):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Network Health Monitor")
#         self.setGeometry(100, 100, 900, 500)

#         # Central widget
#         central_widget = QWidget()
#         self.setCentralWidget(central_widget)

#         # Layout
#         main_layout = QVBoxLayout()
#         central_widget.setLayout(main_layout)

#         # ADD summary widget at top
#         self.summary = HealthSummaryWidget()
#         main_layout.addWidget(self.summary)
#         # ADD global latency chart below summary
#         self.global_chart = GlobalLatencyChart()
#         main_layout.addWidget(self.global_chart)
#         # ADD availability pie chart
#         self.availability_chart = AvailabilityPieChart()
#         main_layout.addWidget(self.availability_chart)

#         # ADD content layout below summary
#         content_layout = QHBoxLayout()
#         main_layout.addLayout(content_layout)
#         # LEFT: sidebar + detail
#         left_layout = QHBoxLayout()
#         content_layout.addLayout(left_layout, 3)
#         # RIGHT: alerts panel
#         self.alerts_panel = AlertsPanel()
#         content_layout.addWidget(self.alerts_panel, 1)


#         # Sidebar
#         self.node_list = NodeListWidget(self)
#         left_layout.addWidget(self.node_list)
#         self.node_list.itemClicked.connect(self.on_node_clicked)

#         # Detail panel Right side layout
#         right_layout = QVBoxLayout()

#         self.detail_label = QLabel("Select a node to view details")
#         self.detail_label.setStyleSheet("font-size: 16px;")

#         # Create chart here
#         self.chart = LatencyChart()
#         self.selected_node = None

#         # Add widgets to right layout
#         right_layout.addWidget(self.detail_label)
#         right_layout.addWidget(self.chart)

#         # Add right layout to main layout
#         left_layout.addLayout(right_layout)

#         # Timer MUST be inside __init__
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.refresh_nodes)
#         self.timer.start(2000)

#         # Initial refresh
#         self.refresh_nodes()

#     #  click handler
#     def on_node_clicked(self, item):
#         node = item.text().split()[1]

#         # store selected node
#         self.selected_node = node

#         info = self.states.get(node)

#         if not info:
#             return

#         details = (
#             f"Node: {node}\n"
#             f"IP: {info['ip']}\n"
#             f"State: {info['state']}\n"
#             f"Latency: {info['latency']} ms\n"
#             f"Fails: {info['fails']}"
#         )

#         self.detail_label.setText(details)

#         latency_history = get_node_latency_history(node)
#         self.chart.update_data(latency_history)

#     def refresh_nodes(self):
#         print("Refreshing GUI...")  # DEBUG LINE
#         # refresh sidebar
#         # read latest states from log
#         self.states = read_latest_node_states()
#         # update all components with new states
#         self.node_list.refresh(self.states, self)

#         # update summary, availability chart, alerts panel, global chart
#         self.summary.update_summary(self.states)
#         self.availability_chart.update_data(self.states)
#         self.alerts_panel.update_alerts(self.states)
#         # update global chart
#         global_history = get_global_latency_history()
#         self.global_chart.update_data(global_history)

#         # update graph and details ONLY if node selected
#         if self.selected_node:
#             info = self.states.get(self.selected_node)

#             if not info:
#                 return

#             # update graph
#             latency_history = get_node_latency_history(self.selected_node)
#             print("Latency history length:", len(latency_history))  # DEBUG
#             self.chart.update_data(latency_history)

#             # update details panel
#             details = (
#                 f"Node: {self.selected_node}\n"
#                 f"IP: {info['ip']}\n"
#                 f"Network: {info['network_type']}\n"
#                 f"State: {info['state']}\n"
#                 f"Latency: {info['latency']} ms\n"
#                 f"Fails: {info['fails']}"
#             )

#             self.detail_label.setText(details)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = NetworkMonitorGUI()
#     window.show()
#     sys.exit(app.exec())





# gui/gui.py

import sys

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)

from PySide6.QtCore import QTimer

# charts
from chart import LatencyChart
from global_chart import GlobalLatencyChart
from node_availability_chart import NodeAvailabilityChart

# data
from data import (
    read_latest_node_states,
    get_node_latency_history,
    get_global_latency_history,
    get_node_state_distribution,
)

# widgets
from widgets import NodeListWidget
from summary import HealthSummaryWidget
from alerts import AlertsPanel


class NetworkMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Network Health Monitor")
        self.setGeometry(100, 100, 900, 600)

        self.selected_node = None
        self.states = {}

        # =========================
        # Central widget
        # =========================

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # =========================
        # Summary widget
        # =========================

        self.summary = HealthSummaryWidget()
        main_layout.addWidget(self.summary)

        # =========================
        # Global latency chart
        # =========================

        self.global_chart = GlobalLatencyChart()
        main_layout.addWidget(self.global_chart)

        # =========================
        # Content layout
        # =========================

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # LEFT SIDE
        left_layout = QHBoxLayout()
        content_layout.addLayout(left_layout, 3)

        # RIGHT SIDE (alerts)
        self.alerts_panel = AlertsPanel()
        content_layout.addWidget(self.alerts_panel, 1)

        # =========================
        # Sidebar
        # =========================

        self.node_list = NodeListWidget(self)
        self.node_list.itemClicked.connect(self.on_node_clicked)

        left_layout.addWidget(self.node_list)

        # =========================
        # Details section
        # =========================

        right_layout = QVBoxLayout()

        # Node detail label
        self.detail_label = QLabel("Select a node to view details")
        self.detail_label.setStyleSheet("font-size: 16px;")

        right_layout.addWidget(self.detail_label)

        # Latency chart
        self.chart = LatencyChart()
        right_layout.addWidget(self.chart)

        # =========================
        # NODE AVAILABILITY PIE CHART  (FIX ADDED)
        # =========================

        self.node_availability_chart = NodeAvailabilityChart()
        self.node_availability_chart.setMinimumHeight(250)

        right_layout.addWidget(self.node_availability_chart)

        # add details section to layout
        left_layout.addLayout(right_layout)

        # =========================
        # Timer
        # =========================

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_nodes)
        self.timer.start(2000)

        # Initial refresh
        self.refresh_nodes()

    # =========================
    # Node clicked
    # =========================

    def on_node_clicked(self, item):

        node = item.text().split()[1]

        self.selected_node = node

        info = self.states.get(node)

        if not info:
            return

        # update details text
        details = (
            f"Node: {node}\n"
            f"IP: {info['ip']}\n"
            f"Network: {info['network_type']}\n"
            f"State: {info['state']}\n"
            f"Latency: {info['latency']} ms\n"
            f"Fails: {info['fails']}"
        )

        self.detail_label.setText(details)

        # update latency chart
        latency_history = get_node_latency_history(node)
        self.chart.update_data(latency_history)

        # =========================
        # UPDATE PIE CHART (FIX)
        # =========================

        up, degraded, down = get_node_state_distribution(node)

        self.node_availability_chart.update_data(up, degraded, down)

    # =========================
    # Refresh GUI
    # =========================

    def refresh_nodes(self):

        print("Refreshing GUI...")

        # read states
        self.states = read_latest_node_states()

        # update sidebar
        self.node_list.refresh(self.states, self)

        # update summary
        self.summary.update_summary(self.states)

        # update alerts
        self.alerts_panel.update_alerts(self.states)

        # update global chart
        global_history = get_global_latency_history()
        self.global_chart.update_data(global_history)

        # update selected node charts
        if self.selected_node:
            info = self.states.get(self.selected_node)

            if not info:
                return

            # update latency chart
            latency_history = get_node_latency_history(self.selected_node)

            self.chart.update_data(latency_history)

            # update pie chart  (FIX)
            up, degraded, down = get_node_state_distribution(self.selected_node)

            self.node_availability_chart.update_data(up, degraded, down)

            # update text
            details = (
                f"Node: {self.selected_node}\n"
                f"IP: {info['ip']}\n"
                f"Network: {info['network_type']}\n"
                f"State: {info['state']}\n"
                f"Latency: {info['latency']} ms\n"
                f"Fails: {info['fails']}"
            )

            self.detail_label.setText(details)


# =========================
# Run app
# =========================

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = NetworkMonitorGUI()

    window.show()

    sys.exit(app.exec())
