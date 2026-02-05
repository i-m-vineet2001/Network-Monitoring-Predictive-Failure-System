from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter


class GlobalLatencyChart(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.chart_obj = QChart()
        self.chart_obj.setTitle("Global Average Latency")

        self.series = QLineSeries()
        self.chart_obj.addSeries(self.series)

        self.axisX = QValueAxis()
        self.axisX.setTitleText("Time")

        self.axisY = QValueAxis()
        self.axisY.setTitleText("Avg Latency (ms)")

        self.chart_obj.addAxis(self.axisX, Qt.AlignBottom)
        self.chart_obj.addAxis(self.axisY, Qt.AlignLeft)

        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)

        self.setChart(self.chart_obj)
        self.setRenderHint(QPainter.Antialiasing)

    def update_data(self, latency_list):

        self.series.clear()

        if not latency_list:
            return

        for i, latency in enumerate(latency_list):
            self.series.append(i, latency)

        min_y = min(latency_list)
        max_y = max(latency_list)

        padding = 10

        self.axisX.setRange(0, len(latency_list))
        self.axisY.setRange(max(0, min_y - padding), max_y + padding)

        self.chart_obj.update()
        self.update()
