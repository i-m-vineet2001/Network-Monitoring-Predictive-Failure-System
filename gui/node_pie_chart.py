# gui/node_pie_chart.py
from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter


class NodePieChart(QChartView):
    def __init__(self, node_name, parent=None):
        super().__init__(parent)
        self.node_name = node_name

        self.chart_obj = QChart()
        self.chart_obj.setTitle(f"{node_name} Status")

        self.series = QPieSeries()
        self.chart_obj.addSeries(self.series)

        self.setChart(self.chart_obj)
        self.setRenderHint(QPainter.Antialiasing)

    def update_data(self, availability_percent, packet_loss_percent):
        """
        Update pie chart with availability and packet loss percentages
        availability_percent: 0-100
        packet_loss_percent: 0-100
        """
        self.series.clear()

        # Create slices
        availability_slice = QPieSlice(
            f"Available {availability_percent}%", availability_percent
        )
        availability_slice.setColor(QColor("#2ecc71"))  # green

        loss_slice = QPieSlice(f"Loss {packet_loss_percent}%", packet_loss_percent)
        loss_slice.setColor(QColor("#e74c3c"))  # red

        self.series.append(availability_slice)
        self.series.append(loss_slice)

        # Label styling
        availability_slice.setLabelVisible(True)
        loss_slice.setLabelVisible(True)
