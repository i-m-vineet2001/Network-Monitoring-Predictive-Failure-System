from PySide6.QtCharts import QChart, QChartView, QPieSeries
from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt


class NodeAvailabilityChart(QChartView):
    def __init__(self, parent=None):

        super().__init__(parent)

        self.chart_obj = QChart()
        self.chart_obj.setTitle("Node Availability Distribution")

        self.series = QPieSeries()
        self.series.setPieSize(0.7)

        self.chart_obj.addSeries(self.series)

        self.chart_obj.legend().setVisible(True)
        self.chart_obj.legend().setAlignment(Qt.AlignRight)

        self.setChart(self.chart_obj)
        self.setRenderHint(QPainter.Antialiasing)

    def update_data(self, up, degraded, down):

        self.series.clear()

        total = up + degraded + down

        if total == 0:
            return

        # calculate percentages
        up_pct = (up / total) * 100
        degraded_pct = (degraded / total) * 100
        down_pct = (down / total) * 100

        # create slices with percentage labels
        up_slice = self.series.append(
            f"UP ({up_pct:.1f}%)", up
        )

        degraded_slice = self.series.append(
            f"DEGRADED ({degraded_pct:.1f}%)", degraded
        )

        down_slice = self.series.append(
            f"DOWN ({down_pct:.1f}%)", down
        )

        # colors
        up_slice.setBrush(QColor("#2ecc71"))
        degraded_slice.setBrush(QColor("#f1c40f"))
        down_slice.setBrush(QColor("#e74c3c"))

        # show labels
        up_slice.setLabelVisible(True)
        degraded_slice.setLabelVisible(True)
        down_slice.setLabelVisible(True)

        # explode largest slice
        slices = [up_slice, degraded_slice, down_slice]

        largest = max(slices, key=lambda s: s.value())

        largest.setExploded(True)
        largest.setExplodeDistanceFactor(0.1)

        self.chart_obj.update()
