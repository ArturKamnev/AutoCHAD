"""
AutoCHAD PyQt6 Viewer

Run instructions
-----------------
1. Install dependencies: ``pip install -r requirements.txt``.
2. Launch the application: ``python autochad.py``.

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
The application opens a PyQt6 main window with a grid-backed canvas, top toolbar
for selecting architectural tools, mouse wheel zoom, middle-button panning, and
selection/undo support via keyboard shortcuts.
=======
The application opens a PyQt6 main window with a grid-backed canvas. Use the mouse
wheel to zoom, the middle mouse button to pan, and the bottom command line to
switch tools using the keywords ``LINE``, ``CIRCLE``, or ``RECTANGLE``.
>>>>>>> main
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Callable, Optional

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
from PyQt6.QtCore import QPoint, QPointF, QRectF, Qt, QLineF, QSize
from PyQt6.QtGui import (
    QAction,
    QActionGroup,
    QBrush,
    QColor,
    QKeySequence,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PyQt6.QtWidgets import (
    QApplication,
    QDockWidget,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QTextEdit,
    QToolBar,
    QVBoxLayout,
    QWidget,
=======
from PyQt6.QtCore import QPoint, QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QKeySequence, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QDockWidget,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsSimpleTextItem,
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
>>>>>>> main
)


GRID_SIZE = 25
ZOOM_FACTOR = 1.15
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
WALL_THICKNESS = 24.0
DOOR_WIDTH = 8.0
ATTACHMENT_SIZE = 12.0


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))
=======
>>>>>>> main


class GridGraphicsView(QGraphicsView):
    """Graphics view with grid drawing, zooming, and panning support."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setRenderHints(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setMouseTracking(True)
        self._panning = False
        self._last_pan_point: Optional[QPoint] = None
        self.event_delegate: Optional["CanvasEventDelegate"] = None

    # --- Coordinate helpers -------------------------------------------------
    def view_to_scene(self, pos: QPoint) -> QPointF:
        """Convert a viewport position to a scene position."""
        return self.mapToScene(pos)

    def scene_to_view(self, pos: QPointF) -> QPoint:
        """Convert a scene position to a viewport position."""
        return self.mapFromScene(pos)

    # --- Drawing ------------------------------------------------------------
    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:  # noqa: N802
        """Draw a light grid in the background."""
        super().drawBackground(painter, rect)
        painter.save()
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
        painter.setPen(QPen(QColor(220, 220, 220, 30)))
=======
        painter.setPen(QPen(QColor(220, 220, 220, 60)))
>>>>>>> main

        left = int(math.floor(rect.left())) - (int(math.floor(rect.left())) % GRID_SIZE)
        top = int(math.floor(rect.top())) - (int(math.floor(rect.top())) % GRID_SIZE)

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
=======
        # Use QPointF to avoid overload resolution errors when mixing ints/floats.
>>>>>>> main
        x = float(left)
        while x < rect.right():
            painter.drawLine(QPointF(x, rect.top()), QPointF(x, rect.bottom()))
            x += GRID_SIZE

        y = float(top)
        while y < rect.bottom():
            painter.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
            y += GRID_SIZE

        painter.restore()

    # --- Interaction --------------------------------------------------------
    def wheelEvent(self, event):  # noqa: N802
        delta = event.angleDelta().y()
        factor = ZOOM_FACTOR if delta > 0 else 1 / ZOOM_FACTOR
        self.scale(factor, factor)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_pan_point = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if self.event_delegate:
            handled = self.event_delegate.handle_mouse_press(event)
            if handled:
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # noqa: N802
        if self._panning and self._last_pan_point is not None:
            delta = event.pos() - self._last_pan_point
            self._last_pan_point = event.pos()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return
        if self.event_delegate and self.event_delegate.handle_mouse_move(event):
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # noqa: N802
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self._last_pan_point = None
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        if self.event_delegate and self.event_delegate.handle_mouse_release(event):
            event.accept()
            return
        super().mouseReleaseEvent(event)


class SelectionManager:
    """Handle item selection and highlight state."""

    def __init__(self, on_change: Callable[[Optional[QGraphicsItem]], None]) -> None:
        self.current: Optional[QGraphicsItem] = None
        self.on_change = on_change
        self._previous_pen: Optional[QPen] = None

    def select(self, item: Optional[QGraphicsItem]) -> None:
        self._clear_highlight()
        self.current = item
        if item is None:
            self.on_change(None)
            return
        try:
            if hasattr(item, "pen"):
                pen = item.pen()  # type: ignore[attr-defined]
                self._previous_pen = pen
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
                highlight = QPen(QColor(255, 120, 0))
=======
                highlight = QPen(QColor(255, 0, 0))
>>>>>>> main
                highlight.setWidthF(max(2.0, pen.widthF()))
                item.setPen(highlight)  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Selection highlight failed: {exc}")
        self.on_change(item)

    def _clear_highlight(self) -> None:
        if self.current and self._previous_pen:
            try:
                self.current.setPen(self._previous_pen)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive
                print(f"Failed to restore pen: {exc}")
        self.current = None
        self._previous_pen = None


class UndoManager:
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
    """Track reversible actions for undo/redo support."""

    def __init__(self) -> None:
        self._undo: list[tuple[Callable[[], None], Optional[Callable[[], None]]]] = []
        self._redo: list[tuple[Callable[[], None], Optional[Callable[[], None]]]] = []

    def push(self, undo: Callable[[], None], redo: Optional[Callable[[], None]] = None) -> None:
        self._undo.append((undo, redo))
        self._redo.clear()

    def undo(self) -> None:
        if not self._undo:
            return
        undo, redo = self._undo.pop()
        try:
            undo()
            if redo:
                self._redo.append((redo, undo))
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Undo failed: {exc}")

    def redo(self) -> None:
        if not self._redo:
            return
        redo, undo = self._redo.pop()
        try:
            redo()
            self._undo.append((undo, redo))
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Redo failed: {exc}")

=======
    """Track reversible actions for undo support."""

    def __init__(self) -> None:
        self._stack: list[Callable[[], None]] = []

    def push(self, action: Callable[[], None]) -> None:
        self._stack.append(action)

    def undo(self) -> None:
        if not self._stack:
            return
        try:
            action = self._stack.pop()
            action()
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Undo failed: {exc}")

>>>>>>> main

@dataclass
class ToolContext:
    scene: QGraphicsScene
    selection: SelectionManager
    undo: UndoManager


<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
# --- Graphics items --------------------------------------------------------
class WallItem(QGraphicsRectItem):
    """Rectangular wall with hatched fill and aligned dimension label."""

    def __init__(self, start: QPointF, end: QPointF, thickness: float = WALL_THICKNESS):
        super().__init__()
        self.start = QPointF(start)
        self.end = QPointF(end)
        self.thickness = thickness
        self.label = QGraphicsSimpleTextItem(self)
        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.label.setBrush(QBrush(QColor(40, 40, 40)))
        pen = QPen(QColor(0, 90, 180), 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        brush = QBrush(QColor(80, 130, 220, 120), Qt.BrushStyle.FDiagPattern)
        self.setBrush(brush)
        self.setZValue(1)
        self.update_geometry()

    def update_geometry(self) -> None:
        line = self.centerline()
        length = max(1.0, line.length())
        self.setRect(0, -self.thickness / 2.0, length, self.thickness)
        self.setPos(self.start)
        angle = -line.angle()
        self.setRotation(angle)
        self._update_label(length, angle)

    def _update_label(self, length: float, angle: float) -> None:
        self.label.setText(f"{length:.2f}")
        br = self.label.boundingRect()
        self.label.setTransformOriginPoint(br.center())
        self.label.setPos(length / 2.0, -br.height() / 2.0)
        self.label.setRotation(angle)

    def centerline(self) -> QLineF:
        return QLineF(self.start, self.end)

    def project_point(self, pos: QPointF) -> QPointF:
        line = self.centerline()
        if line.length() == 0:
            return QPointF(line.p1())
        dx = line.x2() - line.x1()
        dy = line.y2() - line.y1()
        t = ((pos.x() - line.x1()) * dx + (pos.y() - line.y1()) * dy) / (dx * dx + dy * dy)
        t = clamp(t, 0.0, 1.0)
        return QPointF(line.x1() + dx * t, line.y1() + dy * t)


class WindowItem(QGraphicsRectItem):
    """Window rectangle with elevated z-order and red outline."""

    def __init__(self, start: QPointF, end: QPointF, thickness: float = WALL_THICKNESS / 2):
        super().__init__()
        self.start = QPointF(start)
        self.end = QPointF(end)
        self.thickness = thickness
        pen = QPen(QColor(220, 60, 60), 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(Qt.BrushStyle.NoBrush)
        self.setZValue(5)
        self.update_geometry()

    def update_geometry(self) -> None:
        line = QLineF(self.start, self.end)
        length = max(1.0, line.length())
        self.setRect(0, -self.thickness / 2.0, length, self.thickness)
        self.setPos(self.start)
        self.setRotation(-line.angle())

    def centerline(self) -> QLineF:
        return QLineF(self.start, self.end)


class DoorItem(QGraphicsPathItem):
    """Door slab with swing arc."""

    def __init__(self, start: QPointF, end: QPointF):
        super().__init__()
        self.start = QPointF(start)
        self.end = QPointF(end)
        pen = QPen(QColor(120, 120, 120), 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(Qt.BrushStyle.NoBrush)
        self.setZValue(4)
        self.update_geometry()

    def update_geometry(self) -> None:
        line = QLineF(self.start, self.end)
        length = max(1.0, line.length())
        path = QPainterPath()
        path.addRect(QRectF(0, -DOOR_WIDTH / 2.0, length, DOOR_WIDTH))
        path.moveTo(0, 0)
        arc_rect = QRectF(0, 0, length * 2, length * 2)
        path.arcTo(arc_rect, 0, 90)
        self.setPath(path)
        self.setPos(self.start)
        self.setRotation(-line.angle())


class AttachmentItem(QGraphicsPathItem):
    """Base class for wall-mounted accessories."""

    def __init__(self, color: QColor, z: float) -> None:
        super().__init__()
        pen = QPen(color, 2)
        pen.setCosmetic(True)
        self.setPen(pen)
        self.setBrush(Qt.BrushStyle.NoBrush)
        self.setZValue(z)


class SwitchItem(AttachmentItem):
    def __init__(self) -> None:
        super().__init__(QColor(200, 40, 40), 6)
        path = QPolygonF(
            [
                QPointF(-ATTACHMENT_SIZE / 2, 0),
                QPointF(0, -ATTACHMENT_SIZE / 2),
                QPointF(ATTACHMENT_SIZE / 2, 0),
                QPointF(0, ATTACHMENT_SIZE / 2),
            ]
        )
        painter_path = path_to_pathitem(path)
        painter_path.moveTo(0, 0)
        painter_path.lineTo(0, ATTACHMENT_SIZE)
        painter_path.addEllipse(QPointF(0, 0), 3, 3)
        self.setPath(painter_path)


class OutletItem(AttachmentItem):
    def __init__(self) -> None:
        super().__init__(QColor(200, 40, 40), 6)
        rect = QRectF(-ATTACHMENT_SIZE / 2, -ATTACHMENT_SIZE / 2, ATTACHMENT_SIZE, ATTACHMENT_SIZE)
        painter_path = QPainterPath()
        painter_path.addRect(rect)
        painter_path.moveTo(-4, 0)
        painter_path.lineTo(-4, 4)
        painter_path.moveTo(4, 0)
        painter_path.lineTo(4, 4)
        self.setPath(painter_path)


def path_to_pathitem(points: QPolygonF) -> QPainterPath:
    """Convert polygon points to a painter path."""
    path = QPainterPath()
    if not points:
        return path
    path.moveTo(points[0])
    for pt in points[1:]:
        path.lineTo(pt)
    return path


# --- Tools -----------------------------------------------------------------
=======
>>>>>>> main
class CanvasTool:
    """Base class for drawing tools."""

    name: str = "TOOL"

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        self.context = context
        self.view = view
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
        self.delegate: Optional["CanvasEventDelegate"] = None
        self.preview_item: Optional[QGraphicsItem] = None

    def set_delegate(self, delegate: "CanvasEventDelegate") -> None:
        self.delegate = delegate

=======
        self.preview_item: Optional[QGraphicsItem] = None

>>>>>>> main
    def start(self) -> None:
        self.cancel()

    def cancel(self) -> None:
        if self.preview_item:
            self.context.scene.removeItem(self.preview_item)
            self.preview_item = None

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
    def snap_position(self, pos: QPointF) -> QPointF:
        if self.delegate:
            return self.delegate.snap_position(pos)
        return pos

=======
>>>>>>> main
    def on_press(self, pos: QPointF) -> None:  # pragma: no cover - UI
        raise NotImplementedError

    def on_move(self, pos: QPointF) -> None:  # pragma: no cover - UI
        raise NotImplementedError

    def on_release(self, pos: QPointF) -> None:  # pragma: no cover - UI
        raise NotImplementedError

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za

class WallTool(CanvasTool):
    name = "WALL"

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        super().__init__(context, view)
        self._start: Optional[QPointF] = None

    def on_press(self, pos: QPointF) -> None:
        self._start = pos
        if not self.preview_item:
            preview = WallItem(pos, pos)
            pen = preview.pen()
            pen.setStyle(Qt.PenStyle.DashLine)
            preview.setPen(pen)
            self.preview_item = preview
            self.context.scene.addItem(preview)

    def on_move(self, pos: QPointF) -> None:
        if self._start is None or not isinstance(self.preview_item, WallItem):
            return
        target = pos
        if self.delegate:
            target = self.delegate.apply_ortho(pos, self._start)
        self.preview_item.start = self._start
        self.preview_item.end = target
        self.preview_item.update_geometry()

    def on_release(self, pos: QPointF) -> None:
        if self._start is None:
            return
        target = pos
        if self.delegate:
            target = self.delegate.apply_ortho(pos, self._start)
        wall = WallItem(self._start, target)
        self.context.scene.addItem(wall)
        self.context.selection.select(wall)

        def undo() -> None:
            if self.context.selection.current is wall:
                self.context.selection.select(None)
            self.context.scene.removeItem(wall)

        def redo() -> None:
            self.context.scene.addItem(wall)
            self.context.selection.select(wall)

        self.context.undo.push(undo, redo)
        self.cancel()


class WindowTool(CanvasTool):
    name = "WINDOW"
=======
    def finalize(self) -> None:
        self.cancel()


class DimensionLineItem(QGraphicsLineItem):
    """Line item that maintains a dimension label."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label = QGraphicsSimpleTextItem(self)
        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.label.setBrush(QBrush(QColor(60, 60, 60)))
        self.update_label()

    def setLine(self, *args) -> None:  # noqa: N802
        super().setLine(*args)
        self.update_label()

    def update_label(self) -> None:
        line = self.line()
        length = math.hypot(line.dx(), line.dy())
        self.label.setText(f"{length:.2f}")
        mid_x = (line.x1() + line.x2()) / 2
        mid_y = (line.y1() + line.y2()) / 2
        self.label.setPos(QPointF(mid_x + 5, mid_y + 5))


class DimensionRectItem(QGraphicsRectItem):
    """Rectangle item with width/height label."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.label = QGraphicsSimpleTextItem(self)
        self.label.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIgnoresTransformations)
        self.label.setBrush(QBrush(QColor(60, 60, 60)))
        self.update_label()

    def setRect(self, *args) -> None:  # noqa: N802
        super().setRect(*args)
        self.update_label()

    def update_label(self) -> None:
        rect = self.rect()
        text = f"W:{rect.width():.2f} H:{rect.height():.2f}"
        self.label.setText(text)
        self.label.setPos(rect.center() + QPointF(5, 5))


class LineTool(CanvasTool):
    name = "LINE"
>>>>>>> main

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        super().__init__(context, view)
        self._start: Optional[QPointF] = None

    def on_press(self, pos: QPointF) -> None:
        self._start = pos
        if not self.preview_item:
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
            preview = WindowItem(pos, pos)
            pen = preview.pen()
            pen.setStyle(Qt.PenStyle.DashLine)
            preview.setPen(pen)
            self.preview_item = preview
            self.context.scene.addItem(preview)

    def on_move(self, pos: QPointF) -> None:
        if self._start is None or not isinstance(self.preview_item, WindowItem):
            return
        target = pos
        if self.delegate:
            target = self.delegate.apply_ortho(pos, self._start)
        self.preview_item.start = self._start
        self.preview_item.end = target
        self.preview_item.update_geometry()
=======
            pen = QPen(QColor(0, 120, 215))
            pen.setStyle(Qt.PenStyle.DashLine)
            self.preview_item = DimensionLineItem()
            self.preview_item.setPen(pen)
            self.preview_item.setZValue(10)
            self.context.scene.addItem(self.preview_item)

    def on_move(self, pos: QPointF) -> None:
        if self._start is None or not isinstance(self.preview_item, QGraphicsLineItem):
            return
        adjusted = self.view.event_delegate.apply_ortho(pos, self._start)
        self.preview_item.setLine(
            self._start.x(),
            self._start.y(),
            adjusted.x(),
            adjusted.y(),
        )
>>>>>>> main

    def on_release(self, pos: QPointF) -> None:
        if self._start is None:
            return
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
        target = pos
        if self.delegate:
            target = self.delegate.apply_ortho(pos, self._start)
        window = WindowItem(self._start, target)
        self.context.scene.addItem(window)
        self.context.selection.select(window)

        def undo() -> None:
            if self.context.selection.current is window:
                self.context.selection.select(None)
            self.context.scene.removeItem(window)

        def redo() -> None:
            self.context.scene.addItem(window)
            self.context.selection.select(window)

        self.context.undo.push(undo, redo)
        self.cancel()


class DoorTool(CanvasTool):
    name = "DOOR"

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        super().__init__(context, view)
        self._start: Optional[QPointF] = None

    def on_press(self, pos: QPointF) -> None:
        self._start = pos
        if not self.preview_item:
            preview = DoorItem(pos, pos)
            pen = preview.pen()
            pen.setStyle(Qt.PenStyle.DashLine)
            preview.setPen(pen)
            self.preview_item = preview
            self.context.scene.addItem(preview)

    def on_move(self, pos: QPointF) -> None:
        if self._start is None or not isinstance(self.preview_item, DoorItem):
            return
        target = pos
        if self.delegate:
            target = self.delegate.apply_ortho(pos, self._start)
        self.preview_item.start = self._start
        self.preview_item.end = target
        self.preview_item.update_geometry()

    def on_release(self, pos: QPointF) -> None:
        if self._start is None:
            return
        target = pos
        if self.delegate:
            target = self.delegate.apply_ortho(pos, self._start)
        door = DoorItem(self._start, target)
        self.context.scene.addItem(door)
        self.context.selection.select(door)

        def undo() -> None:
            if self.context.selection.current is door:
                self.context.selection.select(None)
            self.context.scene.removeItem(door)

        def redo() -> None:
            self.context.scene.addItem(door)
            self.context.selection.select(door)

        self.context.undo.push(undo, redo)
        self.cancel()


class WallAttachmentTool(CanvasTool):
    """Base for switch/outlet tools that snap to the nearest wall."""

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        super().__init__(context, view)
        self._hover_pos: Optional[QPointF] = None
        self._wall: Optional[WallItem] = None

    def snap_to_wall(self, pos: QPointF) -> Optional[tuple[WallItem, QPointF]]:
        if not self.delegate:
            return None
        return self.delegate.nearest_wall_projection(pos)

    def on_move(self, pos: QPointF) -> None:
        snapped = self.snap_to_wall(pos)
        if not snapped:
            return
        wall, point = snapped
        self._hover_pos = point
        self._wall = wall
        if not self.preview_item:
            self.preview_item = self.build_preview()
            if self.preview_item:
                self.context.scene.addItem(self.preview_item)
        if self.preview_item:
            self.preview_item.setPos(point)
            self.preview_item.setRotation(wall.rotation())

    def on_press(self, pos: QPointF) -> None:
        snapped = self.snap_to_wall(pos)
        if not snapped:
            QMessageBox.information(self.view, "No wall", "Place switches and outlets on walls.")
            return
        wall, point = snapped
        item = self.build_final()
        item.setPos(point)
        item.setRotation(wall.rotation())
        self.context.scene.addItem(item)
        self.context.selection.select(item)

        def undo() -> None:
            if self.context.selection.current is item:
                self.context.selection.select(None)
            self.context.scene.removeItem(item)

        def redo() -> None:
            self.context.scene.addItem(item)
            self.context.selection.select(item)

        self.context.undo.push(undo, redo)

    def build_preview(self) -> Optional[AttachmentItem]:
        raise NotImplementedError

    def build_final(self) -> AttachmentItem:
        raise NotImplementedError

    def on_release(self, pos: QPointF) -> None:  # pragma: no cover - UI
        return


class SwitchTool(WallAttachmentTool):
    name = "SWITCH"

    def build_preview(self) -> AttachmentItem:
        preview = SwitchItem()
        pen = preview.pen()
        pen.setStyle(Qt.PenStyle.DashLine)
        preview.setPen(pen)
        return preview

    def build_final(self) -> AttachmentItem:
        return SwitchItem()


class OutletTool(WallAttachmentTool):
    name = "OUTLET"

    def build_preview(self) -> AttachmentItem:
        preview = OutletItem()
        pen = preview.pen()
        pen.setStyle(Qt.PenStyle.DashLine)
        preview.setPen(pen)
        return preview

    def build_final(self) -> AttachmentItem:
        return OutletItem()
=======
        adjusted = self.view.event_delegate.apply_ortho(pos, self._start)
        line_item = DimensionLineItem(
            self._start.x(), self._start.y(), adjusted.x(), adjusted.y()
        )
        line_item.setPen(QPen(QColor(0, 0, 0), 1.5))
        self.context.scene.addItem(line_item)
        self.context.selection.select(line_item)

        def undo() -> None:
            if self.context.selection.current is line_item:
                self.context.selection.select(None)
            self.context.scene.removeItem(line_item)

        self.context.undo.push(undo)
        self.finalize()


class RectangleTool(CanvasTool):
    name = "RECTANGLE"

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        super().__init__(context, view)
        self._origin: Optional[QPointF] = None

    def on_press(self, pos: QPointF) -> None:
        self._origin = pos
        if not self.preview_item:
            pen = QPen(QColor(0, 120, 215))
            pen.setStyle(Qt.PenStyle.DashLine)
            rect = DimensionRectItem()
            rect.setPen(pen)
            rect.setBrush(QBrush(QColor(0, 120, 215, 40)))
            rect.setZValue(10)
            self.preview_item = rect
            self.context.scene.addItem(rect)

    def on_move(self, pos: QPointF) -> None:
        if self._origin is None or not isinstance(self.preview_item, QGraphicsRectItem):
            return
        rect = QRectF(self._origin, pos).normalized()
        self.preview_item.setRect(rect)

    def on_release(self, pos: QPointF) -> None:
        if self._origin is None:
            return
        rect = QRectF(self._origin, pos).normalized()
        rect_item = DimensionRectItem(rect)
        rect_item.setPen(QPen(QColor(0, 0, 0), 1.5))
        rect_item.setBrush(QBrush(QColor(200, 200, 255, 80)))
        self.context.scene.addItem(rect_item)
        self.context.selection.select(rect_item)

        def undo() -> None:
            if self.context.selection.current is rect_item:
                self.context.selection.select(None)
            self.context.scene.removeItem(rect_item)

        self.context.undo.push(undo)
        self.finalize()


class CircleTool(CanvasTool):
    name = "CIRCLE"

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        super().__init__(context, view)
        self._center: Optional[QPointF] = None

    def on_press(self, pos: QPointF) -> None:
        self._center = pos
        if not self.preview_item:
            pen = QPen(QColor(0, 120, 215))
            pen.setStyle(Qt.PenStyle.DashLine)
            ellipse = QGraphicsEllipseItem()
            ellipse.setPen(pen)
            ellipse.setBrush(QBrush(QColor(0, 120, 215, 40)))
            ellipse.setZValue(10)
            self.preview_item = ellipse
            self.context.scene.addItem(ellipse)

    def on_move(self, pos: QPointF) -> None:
        if self._center is None or not isinstance(self.preview_item, QGraphicsEllipseItem):
            return
        radius = math.hypot(pos.x() - self._center.x(), pos.y() - self._center.y())
        rect = QRectF(
            self._center.x() - radius,
            self._center.y() - radius,
            radius * 2,
            radius * 2,
        )
        self.preview_item.setRect(rect)

    def on_release(self, pos: QPointF) -> None:
        if self._center is None:
            return
        radius = math.hypot(pos.x() - self._center.x(), pos.y() - self._center.y())
        rect = QRectF(
            self._center.x() - radius,
            self._center.y() - radius,
            radius * 2,
            radius * 2,
        )
        ellipse_item = QGraphicsEllipseItem(rect)
        ellipse_item.setPen(QPen(QColor(0, 0, 0), 1.5))
        ellipse_item.setBrush(QBrush(QColor(200, 255, 200, 80)))
        self.context.scene.addItem(ellipse_item)
        self.context.selection.select(ellipse_item)

        def undo() -> None:
            if self.context.selection.current is ellipse_item:
                self.context.selection.select(None)
            self.context.scene.removeItem(ellipse_item)

        self.context.undo.push(undo)
        self.finalize()
>>>>>>> main


class CanvasEventDelegate:
    """Bridge between view events and the active tool."""

    def __init__(self, view: GridGraphicsView, context: ToolContext) -> None:
        self.view = view
        self.context = context
        self.active_tool: Optional[CanvasTool] = None
        self.snap_enabled = True
        self.ortho_active = False

    def set_tool(self, tool: Optional[CanvasTool]) -> None:
        if self.active_tool:
            self.active_tool.cancel()
        self.active_tool = tool
        if self.active_tool:
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
            self.active_tool.set_delegate(self)
=======
>>>>>>> main
            self.active_tool.start()

    def handle_mouse_press(self, event) -> bool:
        try:
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
            scene_pos = self.tool_position(event.pos())
=======
            scene_pos = self.snap_position(self.view.view_to_scene(event.pos()))
>>>>>>> main
            if self.active_tool:
                self.active_tool.on_press(scene_pos)
                return True
            item = self.context.scene.itemAt(scene_pos, self.view.transform())
            self.context.selection.select(item)
            return item is not None
        except Exception as exc:  # pragma: no cover - defensive
            QMessageBox.critical(self.view, "Error", f"Mouse press failed: {exc}")
            return True

    def handle_mouse_move(self, event) -> bool:
        if not self.active_tool:
            return False
        try:
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
            scene_pos = self.tool_position(event.pos())
=======
            scene_pos = self.snap_position(self.view.view_to_scene(event.pos()))
>>>>>>> main
            self.active_tool.on_move(scene_pos)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            QMessageBox.warning(self.view, "Error", f"Mouse move failed: {exc}")
            return True

    def handle_mouse_release(self, event) -> bool:
        if not self.active_tool:
            return False
        try:
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
            scene_pos = self.tool_position(event.pos())
=======
            scene_pos = self.snap_position(self.view.view_to_scene(event.pos()))
>>>>>>> main
            self.active_tool.on_release(scene_pos)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            QMessageBox.critical(self.view, "Error", f"Mouse release failed: {exc}")
            return True

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
    def tool_position(self, viewport_pos: QPoint) -> QPointF:
        scene_pos = self.view.view_to_scene(viewport_pos)
        if isinstance(self.active_tool, WallAttachmentTool):
            return scene_pos
        return self.snap_position(scene_pos)

=======
>>>>>>> main
    def snap_position(self, pos: QPointF) -> QPointF:
        if not self.snap_enabled:
            return pos
        return QPointF(
            round(pos.x() / GRID_SIZE) * GRID_SIZE,
            round(pos.y() / GRID_SIZE) * GRID_SIZE,
        )

    def apply_ortho(self, pos: QPointF, origin: Optional[QPointF]) -> QPointF:
        if not self.ortho_active or origin is None:
            return pos
        dx = abs(pos.x() - origin.x())
        dy = abs(pos.y() - origin.y())
        if dx >= dy:
            return QPointF(pos.x(), origin.y())
        return QPointF(origin.x(), pos.y())

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
    def nearest_wall_projection(self, pos: QPointF) -> Optional[tuple[WallItem, QPointF]]:
        best: Optional[tuple[WallItem, QPointF, float]] = None
        for item in self.context.scene.items():
            if not isinstance(item, WallItem):
                continue
            projected = item.project_point(pos)
            dist = QLineF(pos, projected).length()
            if best is None or dist < best[2]:
                best = (item, projected, dist)
        if best:
            return best[0], best[1]
        return None


# --- UI widgets ------------------------------------------------------------
=======

>>>>>>> main
class PropertiesPanel(QDockWidget):
    """Dockable widget showing selected item information."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__("Properties", parent)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.text)
        container.setLayout(layout)
        self.setWidget(container)

    def show_item(self, item: Optional[QGraphicsItem]) -> None:
        if item is None:
            self.text.setPlainText("No selection")
            return
        lines = [f"Type: {type(item).__name__}"]
        try:
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
            if isinstance(item, WallItem):
                line = item.centerline()
                lines.append(
                    f"Wall: start=({line.x1():.2f},{line.y1():.2f}) end=({line.x2():.2f},{line.y2():.2f})"
                )
                lines.append(f"Thickness: {item.thickness:.2f}")
            elif isinstance(item, WindowItem):
                line = item.centerline()
                lines.append(
                    f"Window: start=({line.x1():.2f},{line.y1():.2f}) end=({line.x2():.2f},{line.y2():.2f})"
                )
            elif isinstance(item, DoorItem):
                lines.append(
                    f"Door: start=({item.start.x():.2f},{item.start.y():.2f}) end=({item.end.x():.2f},{item.end.y():.2f})"
                )
            elif isinstance(item, AttachmentItem):
                pos = item.scenePos()
                lines.append(f"Attachment at ({pos.x():.2f}, {pos.y():.2f})")
=======
            if isinstance(item, QGraphicsLineItem):
                line = item.line()
                lines.append(
                    f"P1: ({line.x1():.2f}, {line.y1():.2f}) P2: ({line.x2():.2f}, {line.y2():.2f})"
                )
            elif isinstance(item, QGraphicsRectItem):
                rect = item.rect()
                lines.append(
                    f"Rect: x={rect.x():.2f}, y={rect.y():.2f}, w={rect.width():.2f}, h={rect.height():.2f}"
                )
            elif isinstance(item, QGraphicsEllipseItem):
                rect = item.rect()
                lines.append(
                    f"Center: ({rect.center().x():.2f}, {rect.center().y():.2f}), r={rect.width()/2:.2f}"
                )
>>>>>>> main
            else:
                lines.append("No extra metadata available")
        except Exception as exc:  # pragma: no cover - defensive
            lines.append(f"Error reading item: {exc}")
        self.text.setPlainText("\n".join(lines))


<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
=======
class CommandLineWidget(QWidget):
    """Bottom command line for switching tools."""

    def __init__(self, on_command: Callable[[str], None], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.on_command = on_command
        layout = QHBoxLayout()
        self.label = QLabel("Command:")
        self.input = QLineEdit()
        self.status = QLabel()
        self.input.returnPressed.connect(self._handle_input)
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.status)
        layout.setContentsMargins(5, 5, 5, 5)
        self.setLayout(layout)

    def _handle_input(self) -> None:
        text = self.input.text().strip().upper()
        if not text:
            self.status.setText("Enter LINE, CIRCLE, or RECTANGLE")
            return
        try:
            self.on_command(text)
            self.status.setText(f"Activated {text}")
        except Exception as exc:  # pragma: no cover - defensive
            self.status.setText(f"Error: {exc}")
        finally:
            self.input.clear()


>>>>>>> main
class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AutoCHAD")
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)

        self.view = GridGraphicsView(self.scene)
        self.view.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
=======
        self.setCentralWidget(self.view)
>>>>>>> main

        self.properties = PropertiesPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties)

        self.selection = SelectionManager(on_change=self.properties.show_item)
        self.undo = UndoManager()
        self.tool_context = ToolContext(
            scene=self.scene, selection=self.selection, undo=self.undo
        )
        self.event_delegate = CanvasEventDelegate(self.view, self.tool_context)
        self.view.event_delegate = self.event_delegate

        self.tools = {
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
            "WALL": WallTool(self.tool_context, self.view),
            "WINDOW": WindowTool(self.tool_context, self.view),
            "DOOR": DoorTool(self.tool_context, self.view),
            "SWITCH": SwitchTool(self.tool_context, self.view),
            "OUTLET": OutletTool(self.tool_context, self.view),
        }

        self.toolbar = QToolBar("Tools", self)
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        self.tool_actions: dict[str, QAction] = {}
        action_group = QActionGroup(self)
        action_group.setExclusive(True)
        for name in self.tools:
            action = QAction(name.title(), self)
            action.setCheckable(True)
            action.triggered.connect(lambda checked, n=name: self.activate_tool(n))
            self.toolbar.addAction(action)
            action_group.addAction(action)
            self.tool_actions[name] = action

        self.status_label = QLabel("Wheel to zoom, middle mouse to pan, Shift for ortho")
        status_container = QWidget()
        status_layout = QHBoxLayout(status_container)
        status_layout.addWidget(self.status_label)
        status_layout.setContentsMargins(8, 0, 8, 0)
        self.statusBar().addPermanentWidget(status_container)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.view)
=======
            "LINE": LineTool(self.tool_context, self.view),
            "RECTANGLE": RectangleTool(self.tool_context, self.view),
            "CIRCLE": CircleTool(self.tool_context, self.view),
        }

        self.command_line = CommandLineWidget(self.activate_tool)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.view)
        layout.addWidget(self.command_line)
>>>>>>> main
        layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(layout)
        self.setCentralWidget(container)

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
=======
        self.statusBar().showMessage("Use wheel to zoom, middle mouse to pan, CLI for tools")

>>>>>>> main
    def delete_selected(self) -> None:
        item = self.selection.current
        if item is None:
            return

        def restore() -> None:
            self.scene.addItem(item)
            self.selection.select(item)

<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
        def remove_again() -> None:
            if self.selection.current is item:
                self.selection.select(None)
            self.scene.removeItem(item)

        self.scene.removeItem(item)
        self.selection.select(None)
        self.undo.push(restore, remove_again)

    def keyPressEvent(self, event) -> None:  # noqa: N802
=======
        self.scene.removeItem(item)
        self.selection.select(None)
        self.undo.push(restore)

    def keyPressEvent(self, event) -> None:  # noqa: N802
        widget = self.focusWidget()
        if isinstance(widget, (QLineEdit, QTextEdit)):
            super().keyPressEvent(event)
            return
>>>>>>> main
        if event.key() == Qt.Key_Shift:
            self.event_delegate.ortho_active = True
        if event.matches(QKeySequence.StandardKey.Undo):
            self.undo.undo()
            event.accept()
            return
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
        if event.matches(QKeySequence.StandardKey.Redo):
            self.undo.redo()
            event.accept()
            return
=======
>>>>>>> main
        if event.key() == Qt.Key_Delete:
            self.delete_selected()
            event.accept()
            return
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event) -> None:  # noqa: N802
        if event.key() == Qt.Key_Shift:
            self.event_delegate.ortho_active = False
        super().keyReleaseEvent(event)

    def activate_tool(self, name: str) -> None:
        tool = self.tools.get(name)
        if tool is None:
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
            QMessageBox.warning(self, "Unknown tool", f"Unrecognized tool: {name}")
            return
        for key, action in self.tool_actions.items():
            action.setChecked(key == name)
        self.event_delegate.set_tool(tool)
        self.status_label.setText(f"Active tool: {name.title()}")
=======
            QMessageBox.warning(self, "Unknown command", f"Unrecognized tool: {name}")
            return
        self.event_delegate.set_tool(tool)
        self.statusBar().showMessage(f"Active tool: {name}")
>>>>>>> main

    def closeEvent(self, event) -> None:  # noqa: N802
        if self.event_delegate.active_tool:
            self.event_delegate.active_tool.cancel()
        super().closeEvent(event)


def main() -> None:
    try:
        app = QApplication(sys.argv)
    except Exception as exc:  # pragma: no cover - defensive
        sys.stderr.write(f"Failed to start Qt application: {exc}\n")
        sys.exit(1)

    window = MainWindow()
<<<<<<< codex/create-autochad.py-with-pyqt6-gui-e4m9za
    window.resize(1200, 800)
=======
    window.resize(1024, 768)
>>>>>>> main
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
