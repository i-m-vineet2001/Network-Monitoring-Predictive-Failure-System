# from PySide6.QtCharts import QChart, QChartView, QPieSeries
# from PySide6.QtGui import QPainter, QColor
# from PySide6.QtCore import Qt


# class NodeAvailabilityChart(QChartView):
#     def __init__(self, parent=None):

#         super().__init__(parent)

#         self.chart_obj = QChart()
#         self.chart_obj.setTitle("Node Availability Distribution")

#         self.series = QPieSeries()
#         self.series.setPieSize(0.7)

#         self.chart_obj.addSeries(self.series)

#         self.chart_obj.legend().setVisible(True)
#         self.chart_obj.legend().setAlignment(Qt.AlignRight)

#         self.setChart(self.chart_obj)
#         self.setRenderHint(QPainter.Antialiasing)

#     def update_data(self, up, degraded, down):

#         self.series.clear()

#         total = up + degraded + down

#         if total == 0:
#             return

#         # calculate percentages
#         up_pct = (up / total) * 100
#         degraded_pct = (degraded / total) * 100
#         down_pct = (down / total) * 100

#         # create slices with percentage labels
#         up_slice = self.series.append(
#             f"UP ({up_pct:.1f}%)", up
#         )

#         degraded_slice = self.series.append(
#             f"DEGRADED ({degraded_pct:.1f}%)", degraded
#         )

#         down_slice = self.series.append(
#             f"DOWN ({down_pct:.1f}%)", down
#         )

#         # colors
#         up_slice.setBrush(QColor("#2ecc71"))
#         degraded_slice.setBrush(QColor("#f1c40f"))
#         down_slice.setBrush(QColor("#e74c3c"))

#         # show labels
#         up_slice.setLabelVisible(True)
#         degraded_slice.setLabelVisible(True)
#         down_slice.setLabelVisible(True)

#         # explode largest slice
#         slices = [up_slice, degraded_slice, down_slice]

#         largest = max(slices, key=lambda s: s.value())

#         largest.setExploded(True)
#         largest.setExplodeDistanceFactor(0.1)

#         self.chart_obj.update()

















# gui/node_availability_chart.py
from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt
from gui.theme import BG_CARD, BORDER, TEXT_SECONDARY, SUCCESS, WARNING, DANGER


class NodeAvailabilityChart(QChartView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setMinimumHeight(220)

        self.chart_obj = QChart()
        self.chart_obj.setTitle("Node Availability")
        self.chart_obj.setBackgroundBrush(QColor(BG_CARD))
        self.chart_obj.setBackgroundRoundness(12)
        self.chart_obj.setTitleBrush(QColor(TEXT_SECONDARY))

        from PySide6.QtCore import QMargins

        self.chart_obj.setMargins(QMargins(8, 8, 8, 8))

        self.series = QPieSeries()
        self.series.setPieSize(0.72)
        self.series.setHoleSize(0.44)  # donut style
        self.chart_obj.addSeries(self.series)

        legend = self.chart_obj.legend()
        legend.setVisible(True)
        legend.setAlignment(Qt.AlignBottom)
        legend.setLabelBrush(QColor(TEXT_SECONDARY))
        f = QFont("Segoe UI", 9)
        legend.setFont(f)

        self.setChart(self.chart_obj)

    def update_data(self, up: int, degraded: int, down: int):
        self.series.clear()
        total = up + degraded + down
        if total == 0:
            return

        data = [
            (f"UP  {up / total * 100:.1f}%", up, SUCCESS),
            (f"DEGRADED  {degraded / total * 100:.1f}%", degraded, WARNING),
            (f"DOWN  {down / total * 100:.1f}%", down, DANGER),
        ]

        slices = []
        for label, value, color in data:
            if value == 0:
                continue
            sl = self.series.append(label, value)
            sl.setBrush(QColor(color))
            sl.setLabelVisible(False)  # labels live in the legend
            sl.setBorderColor(QColor(BG_CARD))
            sl.setBorderWidth(2)
            slices.append(sl)

        # Explode the largest slice slightly
        if slices:
            largest = max(slices, key=lambda s: s.value())
            largest.setExploded(True)
            largest.setExplodeDistanceFactor(0.07)

        self.chart_obj.update()
        self.update()