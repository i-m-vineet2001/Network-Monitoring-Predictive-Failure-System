
# gui/widgets.py
import sys, os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QStyledItemDelegate, QStyle
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtCore import Qt, QRect, QSize

from gui.theme import (
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BG_CARD,
    BORDER,
    SUCCESS,
    WARNING,
    DANGER,
    ACCENT,
)

_DOT_COLORS = {
    "UP": SUCCESS,
    "DEGRADED": WARNING,
    "DOWN": DANGER,
}

_ROLE_STATE = Qt.UserRole
_ROLE_LATENCY = Qt.UserRole + 1
_ROLE_DISPLAY = Qt.UserRole + 2


class _NodeDelegate(QStyledItemDelegate):
    DOT_R = 5
    PAD_L = 14
    PAD_V = 10

    def paint(self, painter: QPainter, option, index):
        painter.save()

        rect = option.rect
        is_hovered = bool(option.state & QStyle.State_MouseOver)
        is_selected = bool(option.state & QStyle.State_Selected)

        # ── background: always draw a card box ──
        if is_selected:
            painter.setBrush(QColor("#1e2a45"))
            painter.setPen(QColor(ACCENT))
        elif is_hovered:
            painter.setBrush(QColor("#f5c518"))
            painter.setPen(Qt.NoPen)
        else:
            # faded card — same dark card colour as rest of UI
            painter.setBrush(QColor("#1a1d27"))
            painter.setPen(QColor(BORDER))

        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawRoundedRect(rect.adjusted(2, 1, -2, -1), 8, 8)

        state = index.data(_ROLE_STATE) or "UNKNOWN"
        latency = index.data(_ROLE_LATENCY) or None
        display = index.data(_ROLE_DISPLAY) or index.data(Qt.DisplayRole) or ""

        dot_color = QColor(_DOT_COLORS.get(state, TEXT_MUTED))

        cx = rect.left() + self.PAD_L + self.DOT_R
        cy = rect.top() + rect.height() // 2

        # ── colored dot ──
        painter.setBrush(dot_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            cx - self.DOT_R, cy - self.DOT_R, self.DOT_R * 2, self.DOT_R * 2
        )

        text_x = cx + self.DOT_R + 10

        # ── node name ──
        name_font = QFont()
        name_font.setPointSize(12)
        painter.setFont(name_font)
        painter.setPen(QColor("#000000" if is_hovered else TEXT_PRIMARY))
        name_rect = QRect(
            text_x, rect.top() + self.PAD_V, rect.width() - text_x + rect.left(), 18
        )
        painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, display)

        # ── state · latency ──
        sub_font = QFont()
        sub_font.setPointSize(10)
        painter.setFont(sub_font)
        painter.setPen(QColor("#333333" if is_hovered else TEXT_MUTED))

        try:
            lat_str = f"{float(latency):.1f} ms"
        except (TypeError, ValueError):
            lat_str = "— ms"

        sub_rect = QRect(
            text_x,
            rect.top() + self.PAD_V + 20,
            rect.width() - text_x + rect.left(),
            16,
        )
        painter.drawText(
            sub_rect, Qt.AlignLeft | Qt.AlignVCenter, f"{state}  ·  {lat_str}"
        )

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 54)


class NodeListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegate(_NodeDelegate(self))
        self.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                border-radius: 8px;
                margin: 3px 0;
            }
        """)

    def refresh(self, states: dict, parent=None):
        selected_display = None
        if self.currentItem():
            selected_display = self.currentItem().data(_ROLE_DISPLAY)

        self.clear()

        for node_name, info in states.items():
            state = info.get("state", "UNKNOWN")
            latency = info.get("latency", None)

            parts = node_name.replace("node_", "").split("_")
            display = " ".join(p.capitalize() for p in parts)

            item = QListWidgetItem()
            item.setData(_ROLE_STATE, state)
            item.setData(_ROLE_LATENCY, latency)
            item.setData(_ROLE_DISPLAY, display)
            item.setSizeHint(QSize(200, 54))

            self.addItem(item)

            if display == selected_display:
                self.setCurrentItem(item)