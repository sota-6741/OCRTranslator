import sys
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QRect, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QKeyEvent, QMouseEvent, QPainter, QPen, QColor, QScreen
import threading
from typing import Callable, Optional
from models.utils.capture_image import RectangleCoordinates

class Overlay(QWidget):
    """スクリーンオーバーレイ"""
    closed = pyqtSignal()

    def __init__(self, callback: Optional[Callable] = None):
        super().__init__()
        self.callback = callback
        self.start_position = None
        self.current_position = None
        self.selecting = False

        # スクリーン情報をデバッグ出力
        app = QApplication.instance()
        if app:
            primary_screen = app.primaryScreen()
            if primary_screen:
                geometry = primary_screen.geometry()
                device_pixel_ratio = primary_screen.devicePixelRatio()
                print(f"PyQt6 Screen: geometry={geometry.width()}x{geometry.height()}, DPI ratio={device_pixel_ratio}")

        # 画面設定
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()
        self.setCursor(Qt.CursorShape.CrossCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_position = event.position().toPoint()
            self.selecting = True

    def mouseMoveEvent(self, event):
        if self.selecting:
            self.current_position = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if self.selecting and self.start_position and self.current_position:
            rect = QRect(self.start_position, self.current_position).normalized()

            if rect.width() > 10 and rect.height() > 10:
                # デバイスピクセル比を取得して物理座標に変換
                app = QApplication.instance()
                device_pixel_ratio = 1.0
                if app:
                    try:
                        # プライマリスクリーンのデバイスピクセル比を取得
                        screens = app.screens()
                        if screens:
                            device_pixel_ratio = screens[0].devicePixelRatio()
                            print(f"Overlay: Device pixel ratio = {device_pixel_ratio}")
                    except Exception as e:
                        print(f"Overlay: Could not get device pixel ratio: {e}")

                # 物理座標に変換
                physical_x = int(rect.x() * device_pixel_ratio)
                physical_y = int(rect.y() * device_pixel_ratio)
                physical_width = int(rect.width() * device_pixel_ratio)
                physical_height = int(rect.height() * device_pixel_ratio)

                rectangle_coordinate = RectangleCoordinates(physical_x, physical_y, physical_width, physical_height)

                # デバッグ用：座標情報をログ出力
                print(f"Overlay: Logical area - x={rect.x()}, y={rect.y()}, width={rect.width()}, height={rect.height()}")
                print(f"Overlay: Physical area - x={physical_x}, y={physical_y}, width={physical_width}, height={physical_height}")
                print(f"Overlay: Start position - x={self.start_position.x()}, y={self.start_position.y()}")
                print(f"Overlay: Current position - x={self.current_position.x()}, y={self.current_position.y()}")
                print(f"Overlay: MSS coordinates - {rectangle_coordinate.mss_coordinates}")

                if self.callback:

                    callback_thread = threading.Thread(
                        target=self.callback,
                        args=(rectangle_coordinate,),
                        daemon=True
                    )
                    callback_thread.start()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def closeEvent(self, event):
        """Override closeEvent to emit the signal"""
        print("Overlay: Emitting closed signal.")
        self.closed.emit()
        super().closeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        # 半透明背景
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))

        # 選択矩形
        if self.selecting and self.start_position and self.current_position:
            rect = QRect(self.start_position, self.current_position).normalized()
            # 選択領域を透明に
            painter.fillRect(rect, QColor(0, 0, 0, 0))
            # 矩形の枠線
            painter.setPen(QPen(QColor(0, 120, 215), 2))
            painter.drawRect(rect)

def show_screen_area(callback):
    """画面選択オーバーレイを表示"""
    return Overlay(callback)
