# # gui/widgets.py
# import sys, os

# ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, ROOT_DIR)

# from PySide6.QtWidgets import QListWidget, QListWidgetItem, QStyledItemDelegate, QStyle
# from PySide6.QtGui import QColor, QFont, QPainter, QPen
# from PySide6.QtCore import Qt, QRect, QSize

# from gui.theme import (
#     TEXT_PRIMARY,
#     TEXT_SECONDARY,
#     TEXT_MUTED,
#     BG_CARD,
#     BORDER,
#     SUCCESS,
#     WARNING,
#     DANGER,
#     ACCENT,
# )

# _DOT_COLORS = {
#     "UP": SUCCESS,
#     "DEGRADED": WARNING,
#     "DOWN": DANGER,
# }

# # ── Data roles ────────────────────────────────────────────
# _ROLE_STATE = Qt.UserRole
# _ROLE_LATENCY = Qt.UserRole + 1
# _ROLE_DISPLAY = Qt.UserRole + 2
# _ROLE_ML_PROB = Qt.UserRole + 3  # ← NEW: stores ml_probability float


# class _NodeDelegate(QStyledItemDelegate):
#     DOT_R = 5
#     PAD_L = 14
#     PAD_V = 8

#     def paint(self, painter: QPainter, option, index):
#         painter.save()

#         rect = option.rect
#         is_hovered = bool(option.state & QStyle.State_MouseOver)
#         is_selected = bool(option.state & QStyle.State_Selected)

#         # ── background card ──────────────────────────────
#         if is_selected:
#             painter.setBrush(QColor("#1e2a45"))
#             painter.setPen(QColor(ACCENT))
#         elif is_hovered:
#             painter.setBrush(QColor("#f5c518"))
#             painter.setPen(Qt.NoPen)
#         else:
#             painter.setBrush(QColor("#1a1d27"))
#             painter.setPen(QColor(BORDER))

#         painter.setRenderHint(QPainter.Antialiasing)
#         painter.drawRoundedRect(rect.adjusted(2, 1, -2, -1), 8, 8)

#         # ── read item data ────────────────────────────────
#         state = index.data(_ROLE_STATE) or "UNKNOWN"
#         latency = index.data(_ROLE_LATENCY) or None
#         display = index.data(_ROLE_DISPLAY) or index.data(Qt.DisplayRole) or ""

#         # ── FIX: read ml_probability from role ────────────
#         ml_prob_raw = index.data(_ROLE_ML_PROB)
#         try:
#             ml_prob = float(ml_prob_raw) if ml_prob_raw is not None else None
#         except (TypeError, ValueError):
#             ml_prob = None

#         # ── colored status dot ────────────────────────────
#         dot_color = QColor(_DOT_COLORS.get(state, TEXT_MUTED))
#         cx = rect.left() + self.PAD_L + self.DOT_R
#         cy = rect.top() + rect.height() // 2

#         painter.setBrush(dot_color)
#         painter.setPen(Qt.NoPen)
#         painter.drawEllipse(
#             cx - self.DOT_R,
#             cy - self.DOT_R,
#             self.DOT_R * 2,
#             self.DOT_R * 2,
#         )

#         text_x = cx + self.DOT_R + 10

#         # ── node name ─────────────────────────────────────
#         name_font = QFont()
#         name_font.setPointSize(12)
#         painter.setFont(name_font)
#         painter.setPen(QColor("#000000" if is_hovered else TEXT_PRIMARY))
#         name_rect = QRect(
#             text_x,
#             rect.top() + self.PAD_V,
#             rect.width() - text_x + rect.left() - 6,
#             18,
#         )
#         painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, display)

#         # ── state · latency sub-line ──────────────────────
#         sub_font = QFont()
#         sub_font.setPointSize(10)
#         painter.setFont(sub_font)
#         painter.setPen(QColor("#333333" if is_hovered else TEXT_MUTED))

#         try:
#             lat_str = f"{float(latency):.1f} ms"
#         except (TypeError, ValueError):
#             lat_str = "— ms"

#         sub_rect = QRect(
#             text_x,
#             rect.top() + self.PAD_V + 20,
#             rect.width() - text_x + rect.left() - 6,
#             16,
#         )
#         painter.drawText(
#             sub_rect,
#             Qt.AlignLeft | Qt.AlignVCenter,
#             f"{state}  ·  {lat_str}",
#         )

#         # ── FIX: ML risk badge (drawn BEFORE restore) ─────
#         # Only show when probability > 60% and not hovered (yellow bg hides it)
#         if ml_prob is not None and ml_prob > 0.6 and not is_hovered:
#             risk_font = QFont()
#             risk_font.setPointSize(8)
#             risk_font.setBold(True)
#             painter.setFont(risk_font)
#             painter.setPen(QColor("#9b59b6"))  # purple for AI risk

#             # FIX: define risk_rect properly (right side of the item)
#             risk_rect = QRect(
#                 rect.right() - 72,  # 72px wide from right edge
#                 rect.top() + self.PAD_V + 18,
#                 68,  # width
#                 14,  # height
#             )
#             painter.drawText(risk_rect, Qt.AlignRight | Qt.AlignVCenter, "⚠ High Risk")

#         # ── restore AFTER all drawing is done ─────────────
#         painter.restore()  # FIX: moved to end — was incorrectly placed before ML drawing

#     def sizeHint(self, option, index):
#         return QSize(option.rect.width(), 54)


# class NodeListWidget(QListWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._last_states = {}  # track last state to detect changes
#         self.setItemDelegate(_NodeDelegate(self))
#         self.setStyleSheet("""
#             QListWidget {
#                 background: transparent;
#                 border: none;
#                 outline: none;
#             }
#             QListWidget::item {
#                 border-radius: 8px;
#                 margin: 3px 0;
#             }
#         """)

#     def refresh(self, states: dict, parent=None):
#         # Only refresh if node set OR state (UP/DOWN/DEGRADED) changed.
#         # Ignore latency-only updates to prevent jumping.
#         nodes_changed = set(states.keys()) != set(self._last_states.keys())
#         state_changed = any(
#             states.get(node, {}).get("state")
#             != self._last_states.get(node, {}).get("state")
#             for node in set(list(states.keys()) + list(self._last_states.keys()))
#         )

#         # Save current states for next comparison
#         self._last_states = {k: {"state": v.get("state")} for k, v in states.items()}

#         # Skip refresh if only cosmetic changes (latency, fails, etc.)
#         if not nodes_changed and not state_changed:
#             return

#         # preserve scrollbar position to avoid jumping when refreshing
#         sb = self.verticalScrollBar()
#         try:
#             prev_pos = sb.value()
#         except Exception:
#             prev_pos = None

#         selected_display = None
#         if self.currentItem():
#             selected_display = self.currentItem().data(_ROLE_DISPLAY)

#         self.clear()

#         for node_name, info in states.items():
#             state = info.get("state", "UNKNOWN")
#             latency = info.get("latency", None)

#             # FIX: read ml_probability from info and store in item
#             ml_prob = info.get("ml_probability", None)
#             try:
#                 ml_prob = float(ml_prob) if ml_prob is not None else None
#             except (TypeError, ValueError):
#                 ml_prob = None

#             parts = node_name.replace("node_", "").split("_")
#             display = " ".join(p.capitalize() for p in parts)

#             item = QListWidgetItem()
#             item.setData(_ROLE_STATE, state)
#             item.setData(_ROLE_LATENCY, latency)
#             item.setData(_ROLE_DISPLAY, display)
#             item.setData(_ROLE_ML_PROB, ml_prob)  # ← FIX: store ml_prob in item
#             item.setSizeHint(QSize(200, 54))

#             self.addItem(item)
#             if display == selected_display:
#                 # reselect the previous item, but restore scrollbar afterwards
#                 self.setCurrentItem(item)

#         # restore previous scrollbar position to avoid auto-scrolling
#         try:
#             if prev_pos is not None:
#                 sb.setValue(prev_pos)
#         except Exception:
#             pass









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

# ── Data roles ────────────────────────────────────────────
_ROLE_STATE = Qt.UserRole
_ROLE_LATENCY = Qt.UserRole + 1
_ROLE_DISPLAY = Qt.UserRole + 2
_ROLE_ML_PROB = Qt.UserRole + 3  # ← NEW: stores ml_probability float


class _NodeDelegate(QStyledItemDelegate):
    DOT_R = 5
    PAD_L = 14
    PAD_V = 8

    def paint(self, painter: QPainter, option, index):
        painter.save()

        rect = option.rect
        is_hovered = bool(option.state & QStyle.State_MouseOver)
        is_selected = bool(option.state & QStyle.State_Selected)

        # ── background card ──────────────────────────────
        if is_selected:
            painter.setBrush(QColor("#1e2a45"))
            painter.setPen(QColor(ACCENT))
        elif is_hovered:
            painter.setBrush(QColor("#f5c518"))
            painter.setPen(Qt.NoPen)
        else:
            painter.setBrush(QColor("#1a1d27"))
            painter.setPen(QColor(BORDER))

        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawRoundedRect(rect.adjusted(2, 1, -2, -1), 8, 8)

        # ── read item data ────────────────────────────────
        state = index.data(_ROLE_STATE) or "UNKNOWN"
        latency = index.data(_ROLE_LATENCY) or None
        display = index.data(_ROLE_DISPLAY) or index.data(Qt.DisplayRole) or ""

        # ── FIX: read ml_probability from role ────────────
        ml_prob_raw = index.data(_ROLE_ML_PROB)
        try:
            ml_prob = float(ml_prob_raw) if ml_prob_raw is not None else None
        except (TypeError, ValueError):
            ml_prob = None

        # ── colored status dot ────────────────────────────
        dot_color = QColor(_DOT_COLORS.get(state, TEXT_MUTED))
        cx = rect.left() + self.PAD_L + self.DOT_R
        cy = rect.top() + rect.height() // 2

        painter.setBrush(dot_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(
            cx - self.DOT_R,
            cy - self.DOT_R,
            self.DOT_R * 2,
            self.DOT_R * 2,
        )

        text_x = cx + self.DOT_R + 10

        # ── node name ─────────────────────────────────────
        name_font = QFont()
        name_font.setPointSize(12)
        painter.setFont(name_font)
        painter.setPen(QColor("#000000" if is_hovered else TEXT_PRIMARY))
        name_rect = QRect(
            text_x,
            rect.top() + self.PAD_V,
            rect.width() - text_x + rect.left() - 6,
            18,
        )
        painter.drawText(name_rect, Qt.AlignLeft | Qt.AlignVCenter, display)

        # ── state · latency sub-line ──────────────────────
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
            rect.width() - text_x + rect.left() - 6,
            16,
        )
        painter.drawText(
            sub_rect,
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{state}  ·  {lat_str}",
        )

        # ── FIX: ML risk badge (drawn BEFORE restore) ─────
        # Only show when probability > 60% and not hovered (yellow bg hides it)
        if ml_prob is not None and ml_prob > 0.6 and not is_hovered:
            risk_font = QFont()
            risk_font.setPointSize(8)
            risk_font.setBold(True)
            painter.setFont(risk_font)
            painter.setPen(QColor("#9b59b6"))  # purple for AI risk

            # FIX: define risk_rect properly (right side of the item)
            risk_rect = QRect(
                rect.right() - 72,  # 72px wide from right edge
                rect.top() + self.PAD_V + 18,
                68,  # width
                14,  # height
            )
            painter.drawText(risk_rect, Qt.AlignRight | Qt.AlignVCenter, "⚠ High Risk")

        # ── restore AFTER all drawing is done ─────────────
        painter.restore()  # FIX: moved to end — was incorrectly placed before ML drawing

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 54)


class NodeListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_states = {}  # track last state to detect changes
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
        # Only refresh if node set OR state (UP/DOWN/DEGRADED) changed.
        # Ignore latency-only updates to prevent jumping.
        nodes_changed = set(states.keys()) != set(self._last_states.keys())
        state_changed = any(
            states.get(node, {}).get("state")
            != self._last_states.get(node, {}).get("state")
            for node in set(list(states.keys()) + list(self._last_states.keys()))
        )

        def _risk_bucket(prob):
            """Coarse bucket so minor float changes don't trigger refresh."""
            try:
                p = float(prob)
                return "high" if p > 0.6 else "low"
            except (TypeError, ValueError):
                return "none"

        ml_risk_changed = any(
            _risk_bucket(states.get(node, {}).get("ml_probability"))
            != _risk_bucket(self._last_states.get(node, {}).get("ml_probability"))
            for node in set(list(states.keys()) + list(self._last_states.keys()))
        )

        # Save current states for next comparison
        self._last_states = {
            k: {
                "state": v.get("state"),
                "ml_probability": v.get("ml_probability"),
            }
            for k, v in states.items()
        }

        # Skip refresh if only cosmetic changes (latency, fails, etc.)
        if not nodes_changed and not state_changed and not ml_risk_changed:
            return

        # preserve scrollbar position to avoid jumping when refreshing
        sb = self.verticalScrollBar()
        try:
            prev_pos = sb.value()
        except Exception:
            prev_pos = None

        selected_display = None
        if self.currentItem():
            selected_display = self.currentItem().data(_ROLE_DISPLAY)

        self.clear()

        for node_name, info in states.items():
            state = info.get("state", "UNKNOWN")
            latency = info.get("latency", None)

            # FIX: read ml_probability from info and store in item
            ml_prob = info.get("ml_probability", None)
            try:
                ml_prob = float(ml_prob) if ml_prob is not None else None
            except (TypeError, ValueError):
                ml_prob = None

            parts = node_name.replace("node_", "").split("_")
            display = " ".join(p.capitalize() for p in parts)

            item = QListWidgetItem()
            item.setData(_ROLE_STATE, state)
            item.setData(_ROLE_LATENCY, latency)
            item.setData(_ROLE_DISPLAY, display)
            item.setData(_ROLE_ML_PROB, ml_prob)  # ← FIX: store ml_prob in item
            item.setSizeHint(QSize(200, 54))

            self.addItem(item)
            if display == selected_display:
                # reselect the previous item, but restore scrollbar afterwards
                self.setCurrentItem(item)

        # restore previous scrollbar position to avoid auto-scrolling
        try:
            if prev_pos is not None:
                sb.setValue(prev_pos)
        except Exception:
            pass