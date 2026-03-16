


# gui/chart.py
import sys, os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import QMargins

from gui.theme import BG_CARD, BORDER, TEXT_SECONDARY, ACCENT


def _styled_chart(title: str) -> QChart:
    chart = QChart()
    chart.setTitle(title)
    chart.setBackgroundBrush(QColor(BG_CARD))
    chart.setBackgroundRoundness(12)
    chart.setTitleBrush(QColor(TEXT_SECONDARY))
    chart.setTitleFont(QFont("Arial", 11))
    chart.legend().setVisible(False)
    chart.setMargins(QMargins(12, 8, 12, 8))
    chart.setPlotAreaBackgroundBrush(QColor("#141724"))
    chart.setPlotAreaBackgroundVisible(True)
    return chart


def _styled_axis(title: str) -> QValueAxis:
    axis = QValueAxis()
    axis.setTitleText(title)
    axis.setTitleBrush(QColor(TEXT_SECONDARY))
    axis.setLabelsBrush(QColor(TEXT_SECONDARY))
    axis.setGridLineColor(QColor(BORDER))
    axis.setLinePenColor(QColor(BORDER))
    axis.setTickCount(5)
    axis.setLabelsFont(QFont("Arial", 9))
    return axis


class _BaseLineChart(QChartView):
    """Shared base — avoids duplicated boilerplate between charts."""

    LINE_COLOR = ACCENT
    LINE_WIDTH = 2
    TITLE = ""
    AXIS_X_LABEL = "Samples"
    AXIS_Y_LABEL = "ms"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(160)

        self.chart_obj = _styled_chart(self.TITLE)

        self.series = QLineSeries()
        pen = QPen(QColor(self.LINE_COLOR))
        pen.setWidth(self.LINE_WIDTH)
        self.series.setPen(pen)
        self.chart_obj.addSeries(self.series)

        self.axisX = _styled_axis(self.AXIS_X_LABEL)
        self.axisY = _styled_axis(self.AXIS_Y_LABEL)

        self.chart_obj.addAxis(self.axisX, Qt.AlignBottom)
        self.chart_obj.addAxis(self.axisY, Qt.AlignLeft)
        self.series.attachAxis(self.axisX)
        self.series.attachAxis(self.axisY)

        self.setChart(self.chart_obj)

    def update_data(self, latency_list: list):
        self.series.clear()
        if not latency_list:
            return
        for i, v in enumerate(latency_list):
            self.series.append(i, v)
        pad = 10
        self.axisX.setRange(0, max(len(latency_list) - 1, 1))
        self.axisY.setRange(max(0, min(latency_list) - pad), max(latency_list) + pad)
        self.chart_obj.update()
        self.update()


class LatencyChart(_BaseLineChart):
    LINE_COLOR = "#4f8ef7"
    TITLE = "Node Latency History"
    AXIS_X_LABEL = "Samples"
    AXIS_Y_LABEL = "Latency (ms)"


class GlobalLatencyChart(_BaseLineChart):
    LINE_COLOR = "#2ecc71"
    TITLE = "Global Average Latency"
    AXIS_X_LABEL = "Time"
    AXIS_Y_LABEL = "Avg Latency (ms)"