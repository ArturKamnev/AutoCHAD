"""
AutoCHAD PyQt6 Viewer

Run instructions
-----------------
1. Install dependencies: ``pip install -r requirements.txt``.
2. Launch the application: ``python autochad.py``.

The application opens a PyQt6 main window with a grid-backed canvas. Use the mouse
wheel to zoom, the middle mouse button to pan, and the bottom command line to
switch tools using the keywords ``LINE``, ``CIRCLE``, or ``RECTANGLE``.
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass
from typing import Callable, Optional

from PyQt6.QtCore import QPoint, QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QDockWidget,
    QGraphicsEllipseItem,
    QGraphicsItem,
    QGraphicsLineItem,
    QGraphicsRectItem,
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
)


GRID_SIZE = 25
ZOOM_FACTOR = 1.15


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
        painter.setPen(QPen(QColor(220, 220, 220)))

        left = int(math.floor(rect.left())) - (int(math.floor(rect.left())) % GRID_SIZE)
        top = int(math.floor(rect.top())) - (int(math.floor(rect.top())) % GRID_SIZE)

        x = left
        while x < rect.right():
            painter.drawLine(x, rect.top(), x, rect.bottom())
            x += GRID_SIZE

        y = top
        while y < rect.bottom():
            painter.drawLine(rect.left(), y, rect.right(), y)
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
                highlight = QPen(QColor(255, 0, 0))
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


@dataclass
class ToolContext:
    scene: QGraphicsScene
    selection: SelectionManager


class CanvasTool:
    """Base class for drawing tools."""

    name: str = "TOOL"

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        self.context = context
        self.view = view
        self.preview_item: Optional[QGraphicsItem] = None

    def start(self) -> None:
        self.cancel()

    def cancel(self) -> None:
        if self.preview_item:
            self.context.scene.removeItem(self.preview_item)
            self.preview_item = None

    def on_press(self, pos: QPointF) -> None:  # pragma: no cover - UI
        raise NotImplementedError

    def on_move(self, pos: QPointF) -> None:  # pragma: no cover - UI
        raise NotImplementedError

    def on_release(self, pos: QPointF) -> None:  # pragma: no cover - UI
        raise NotImplementedError

    def finalize(self) -> None:
        self.cancel()


class LineTool(CanvasTool):
    name = "LINE"

    def __init__(self, context: ToolContext, view: GridGraphicsView) -> None:
        super().__init__(context, view)
        self._start: Optional[QPointF] = None

    def on_press(self, pos: QPointF) -> None:
        self._start = pos
        if not self.preview_item:
            pen = QPen(QColor(0, 120, 215))
            pen.setStyle(Qt.PenStyle.DashLine)
            self.preview_item = QGraphicsLineItem()
            self.preview_item.setPen(pen)
            self.preview_item.setZValue(10)
            self.context.scene.addItem(self.preview_item)

    def on_move(self, pos: QPointF) -> None:
        if self._start is None or not isinstance(self.preview_item, QGraphicsLineItem):
            return
        self.preview_item.setLine(self._start.x(), self._start.y(), pos.x(), pos.y())

    def on_release(self, pos: QPointF) -> None:
        if self._start is None:
            return
        line_item = QGraphicsLineItem(self._start.x(), self._start.y(), pos.x(), pos.y())
        line_item.setPen(QPen(QColor(0, 0, 0), 1.5))
        self.context.scene.addItem(line_item)
        self.context.selection.select(line_item)
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
            rect = QGraphicsRectItem()
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
        rect_item = QGraphicsRectItem(rect)
        rect_item.setPen(QPen(QColor(0, 0, 0), 1.5))
        rect_item.setBrush(QBrush(QColor(200, 200, 255, 80)))
        self.context.scene.addItem(rect_item)
        self.context.selection.select(rect_item)
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
        self.finalize()


class CanvasEventDelegate:
    """Bridge between view events and the active tool."""

    def __init__(self, view: GridGraphicsView, context: ToolContext) -> None:
        self.view = view
        self.context = context
        self.active_tool: Optional[CanvasTool] = None

    def set_tool(self, tool: Optional[CanvasTool]) -> None:
        if self.active_tool:
            self.active_tool.cancel()
        self.active_tool = tool
        if self.active_tool:
            self.active_tool.start()

    def handle_mouse_press(self, event) -> bool:
        try:
            scene_pos = self.view.view_to_scene(event.pos())
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
            scene_pos = self.view.view_to_scene(event.pos())
            self.active_tool.on_move(scene_pos)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            QMessageBox.warning(self.view, "Error", f"Mouse move failed: {exc}")
            return True

    def handle_mouse_release(self, event) -> bool:
        if not self.active_tool:
            return False
        try:
            scene_pos = self.view.view_to_scene(event.pos())
            self.active_tool.on_release(scene_pos)
            return True
        except Exception as exc:  # pragma: no cover - defensive
            QMessageBox.critical(self.view, "Error", f"Mouse release failed: {exc}")
            return True


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
            else:
                lines.append("No extra metadata available")
        except Exception as exc:  # pragma: no cover - defensive
            lines.append(f"Error reading item: {exc}")
        self.text.setPlainText("\n".join(lines))


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


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AutoCHAD")
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)

        self.view = GridGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        self.properties = PropertiesPanel(self)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties)

        self.selection = SelectionManager(on_change=self.properties.show_item)
        self.tool_context = ToolContext(scene=self.scene, selection=self.selection)
        self.event_delegate = CanvasEventDelegate(self.view, self.tool_context)
        self.view.event_delegate = self.event_delegate

        self.tools = {
            "LINE": LineTool(self.tool_context, self.view),
            "RECTANGLE": RectangleTool(self.tool_context, self.view),
            "CIRCLE": CircleTool(self.tool_context, self.view),
        }

        self.command_line = CommandLineWidget(self.activate_tool)
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.addWidget(self.view)
        layout.addWidget(self.command_line)
        layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.statusBar().showMessage("Use wheel to zoom, middle mouse to pan, CLI for tools")

    def activate_tool(self, name: str) -> None:
        tool = self.tools.get(name)
        if tool is None:
            QMessageBox.warning(self, "Unknown command", f"Unrecognized tool: {name}")
            return
        self.event_delegate.set_tool(tool)
        self.statusBar().showMessage(f"Active tool: {name}")

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
    window.resize(1024, 768)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
