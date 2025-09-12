import asyncio
import flet as ft
from flet import canvas as cv
import numpy as np

from models.image_manager.image_manager import ImageManager, RectangleCoordinates, Point

class CaptureOverlay:

    def __init__(self, page: ft.Page, point=Point, rectangle_coordinates=RectangleCoordinates):
        self._page = page
        self.captured_image: np.ndarray = None
        self._page.title = "画面キャプチャウィンドウ"

        self._canvas: cv.Canvas
        self._rect_shape: cv.Rect

        self.start_point = point(0, 0)
        self.update_point = point(0, 0)

        self.rectangle_coordinates = rectangle_coordinates

        self._rect_shape = None
        self._canvas = None
        self._overlay_container = None

        self.stroke_paint = ft.Paint(
            stroke_width=3,
            style=ft.PaintingStyle.STROKE,
            color=ft.Colors.BLUE,
            stroke_cap=ft.StrokeCap.ROUND
        )

        @property
        def captured_image(self) -> np.ndarray:
            captured_image = self.captured_image
            return captured_image

    def show(self):
        """オーバーレイを表示"""
        page = self._page

        # Canvas（全画面相当のサイズを与える）
        CANVAS_WIDTH = int(page.width or 1200)
        CANVAS_HEIGHT = int(page.height or 800)
        self._canvas = cv.Canvas(
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            expand=True,
        )

        gesture = ft.GestureDetector(
            on_pan_start=self.pan_start,
            on_pan_update=self.pan_update,
            on_pan_end=self.on_pan_end,
            content=ft.Container(width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bgcolor=ft.Colors.TRANSPARENT)
        )

        stack = ft.Stack([gesture, self._canvas])

        overlay = ft.Container(
            content=stack,
            bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLACK)
        )

        self._overlay_container = overlay
        self._page.add(overlay)
        self._page.update()


    def pan_start(self, e: ft.DragStartEvent):
        self.start_point.x = int(e.local_x)
        self.start_point.y = int(e.local_y)

        self._rect_shape = cv.Rect(
            x=self.start_point.x,
            y=self.start_point.y,
            width=1,
            height=1,
            paint=self.stroke_paint,
            visible=True
        )

        if self._canvas:
            self._canvas.shapes.append(self._rect_shape)
            self._canvas.update()

    def pan_update(self, e:ft.DragUpdateEvent):
        # 更新中座標
        self.update_point.x = int(e.local_x)
        self.update_point.y = int(e.local_y)

        left = min(self.start_point.x, self.update_point.x)
        top = min(self.start_point.y, self.update_point.y)
        width = abs(self.update_point.x - self.start_point.x)
        height = abs(self.update_point.y - self.start_point.y)

        self._rect_shape.x = left
        self._rect_shape.y = top
        self._rect_shape.width = width
        self._rect_shape.height = height

        self._canvas.update()

    def on_pan_end(self, e: ft.DragEndEvent):
        #終了座標取得
        end_left = int(self._rect_shape.x)
        end_top = int(self._rect_shape.y)
        end_width = int(self._rect_shape.width)
        end_height = int(self._rect_shape.height)

        self.rectangle_coordinates = RectangleCoordinates(
            end_left, end_top, end_width, end_height
        )

        self._page.open(ft.SnackBar(ft.Text(f"Selected: {end_left},{end_top} {end_width}x{end_height}")))
        self._page.update()

        self._rect_shape.visible = False
        self._canvas.update()

        asyncio.create_task(self.capture_image(self.rectangle_coordinates))


    async def capture_image(self, rectangle_coordinates: RectangleCoordinates):
        loop = asyncio.get_event_loop
        try:
            self.captured_image = ImageManager(rectangle_coordinates).rectangle_capture()
        except Exception as e:
            self._page.open(ft.SnackBar(ft.Text(f"キャプチャ失敗: {e}"), open=True))
            self._page.update()

    async def close(self):
        if self._overlay_container:
            try:
                self._page.controls.remove(self._overlay_container)
            except Exception:
                try:
                    self._page.dialog = None
                except Exception:
                    pass
            self._overlay_container = None
            self._canvas = None
            self._rect_shape = None
            self._page.update()


