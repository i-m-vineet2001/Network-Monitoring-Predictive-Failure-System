# gui/chart.py

from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter


class LatencyChart(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.chart_obj = QChart()
        self.chart_obj.setTitle("Latency History")

        self.series = QLineSeries()

        # Add series
        self.chart_obj.addSeries(self.series)

        # Axes
        self.axisX = QValueAxis()
        self.axisX.setTitleText("Samples")

        self.axisY = QValueAxis()
        self.axisY.setTitleText("Latency (ms)")

        # Add axes to chart
        self.chart_obj.addAxis(self.axisX, Qt.AlignBottom)
        self.chart_obj.addAxis(self.axisY, Qt.AlignLeft)

        # Attach series to axes
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)

        # Set chart
        self.setChart(self.chart_obj)

        # Enable smooth rendering
        self.setRenderHint(QPainter.Antialiasing)

    def update_data(self, latency_list):

        # Clear old points
        self.series.clear()

        if not latency_list:
            return

        # Add new points
        for i, latency in enumerate(latency_list):
            self.series.append(i, latency)

        # Calculate axis range
        min_y = min(latency_list)
        max_y = max(latency_list)

        padding = 10

        self.axisX.setRange(0, len(latency_list))
        self.axisY.setRange(max(0, min_y - padding), max_y + padding)

        # THIS IS THE IMPORTANT FIX — FORCE REDRAW
        self.chart_obj.update()
        self.update()
