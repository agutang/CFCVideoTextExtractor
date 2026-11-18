from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QImage, QPixmap, QPen, QColor
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem
from models.preset import Region

class VideoPreview(QGraphicsView):
    selected = Signal(object)

    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.pixmap = self.scene().addPixmap(QPixmap())
        self.overlays = []
        self.start = None
        self.drag = None
        self.frame = None
        self.setMinimumSize(480, 270)
        self.setAlignment(Qt.AlignCenter)

    def set_frame(self, frame):
        self.frame = frame
        height, width = frame.shape[:2]
        image = QImage(frame.data, width, height, frame.strides[0], QImage.Format_BGR888).copy()
        self.pixmap.setPixmap(QPixmap.fromImage(image))
        self.setSceneRect(QRectF(0, 0, width, height))
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

    def show_regions(self, regions, active):
        for overlay in self.overlays:
            self.scene().removeItem(overlay)
        self.overlays = []
        for index, region in enumerate(regions):
            pen = QPen(QColor('#ffb000' if index == 0 else '#00c8ff'), 3 if index == active else 1)
            pen.setCosmetic(True)
            rect = self.scene().addRect(region.x, region.y, region.width, region.height, pen)
            self.overlays.append(rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.frame is not None:
            point = self.mapToScene(event.position().toPoint())
            if self.sceneRect().contains(point):
                self.start = point
                self.drag = self.scene().addRect(QRectF(point, point), QPen(QColor('lime')))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.start is not None:
            point = self.mapToScene(event.position().toPoint())
            self.drag.setRect(QRectF(self.start, point).normalized().intersected(self.sceneRect()))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.start is not None:
            rect = self.drag.rect().toAlignedRect()
            self.scene().removeItem(self.drag)
            self.start = self.drag = None
            if rect.width() > 0 and rect.height() > 0:
                self.selected.emit(Region(rect.x(), rect.y(), rect.width(), rect.height()))
        super().mouseReleaseEvent(event)
