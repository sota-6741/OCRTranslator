from typing import Optional, Callable
import flet as ft
from flet import Colors
from presenters.main_presenter import AppState

class MainView:
    """最小限のView実装"""

    def __init__(self):
        self.presenter = None
        self.page: Optional[ft.Page] = None
        self._init_components()

    def _init_components(self):
        """最小限のUIコンポーネント"""
        # シンプルなボタンとテキストエリアのみ
        self.capture_button = ft.ElevatedButton(
            "画面キャプチャ",
            on_click=lambda e: self._notify_presenter('capture')
        )

        self.ocr_button = ft.ElevatedButton(
            "OCR実行",
            disabled=True,
            on_click=lambda e: self._notify_presenter('ocr')
        )

        self.translate_button = ft.ElevatedButton(
            "翻訳実行",
            disabled=True,
            on_click=lambda e: self._notify_presenter('translate')
        )

        self.result_text = ft.TextField(
            label="結果",
            multiline=True,
            read_only=True,
            min_lines=8
        )

        self.status_text = ft.Text("準備完了")

    def build(self) -> ft.Control:
        """シンプルなレイアウト"""
        return ft.Column([
            ft.Text("OCR Translator", size=24),
            ft.Row([
                self.capture_button,
                self.ocr_button,
                self.translate_button
            ]),
            self.result_text,
            self.status_text
        ], spacing=20)

    def render(self, state: AppState):
        """最小限の状態反映"""
        self.ocr_button.disabled = not state.ocr_button_enabled
        self.translate_button.disabled = not state.translate_button_enabled
        self.result_text.value = f"OCR: {state.ocr_result}\n\n翻訳: {state.translation_result}"
        self.status_text.value = state.error_message or "準備完了"
        self._update_ui()

    def _notify_presenter(self, action: str):
        """Presenterへの通知"""
        if not self.presenter:
            return

        actions = {
            'capture': self.presenter.on_capture,
            'ocr': self.presenter.on_ocr,
            'translate': self.presenter.on_translate
        }

        if action in actions:
            actions[action]()

    def set_presenter(self, presenter):
        self.presenter = presenter

    def set_page(self, page: ft.Page):
        self.page = page

    def _update_ui(self):
        if self.page:
            self.page.update()

    # キャプチャオーバーレイ表示（簡素化）
    def show_capture_overlay(self, on_area_selected: Callable):
        """最小限のキャプチャオーバーレイ実装"""
        if not self.page:
            return

        # 座標保存用
        start_x = 0
        start_y = 0

        # 選択範囲表示用
        selection_rect = ft.Container(
            bgcolor=Colors.with_opacity(0.3, Colors.BLUE),
            border=ft.border.all(2, Colors.BLUE),
            visible=False
        )

        def on_pan_start(e: ft.DragStartEvent):
            nonlocal start_x, start_y
            start_x = e.global_x
            start_y = e.global_y
            selection_rect.left = start_x
            selection_rect.top = start_y
            selection_rect.width = 1
            selection_rect.height = 1
            selection_rect.visible = True
            self.page.update()

        def on_pan_update(e: ft.DragUpdateEvent):
            width = abs(e.global_x - start_x)
            height = abs(e.global_y - start_y)
            left = min(start_x, e.global_x)
            top = min(start_y, e.global_y)

            selection_rect.left = left
            selection_rect.top = top
            selection_rect.width = width
            selection_rect.height = height
            self.page.update()

        def on_pan_end(e: ft.DragEndEvent):
            width = abs(e.global_x - start_x)
            height = abs(e.global_y - start_y)
            left = min(start_x, e.global_x)
            top = min(start_y, e.global_y)

            # 最小サイズチェック
            if width > 10 and height > 10:
                on_area_selected(int(left), int(top), int(width), int(height))

            self.page.close(overlay)

        def on_cancel(e):
            self.page.close(overlay)

        # オーバーレイダイアログ
        overlay = ft.AlertDialog(
            content_padding=0,
            bgcolor=Colors.with_opacity(0.1, Colors.BLACK),
            content=ft.Container(
                content=ft.Stack([
                    # ドラッグ検出エリア
                    ft.GestureDetector(
                        on_pan_start=on_pan_start,
                        on_pan_update=on_pan_update,
                        on_pan_end=on_pan_end,
                        content=ft.Container(
                            width=1200,  # 固定サイズ
                            height=800,
                            bgcolor=ft.Colors.TRANSPARENT
                        )
                    ),
                    # 選択範囲表示
                    selection_rect,
                    # 指示テキスト
                    ft.Container(
                        content=ft.Text(
                            "ドラッグして範囲選択",
                            color=Colors.WHITE,
                            bgcolor=Colors.with_opacity(0.7, Colors.BLACK)
                        ),
                        top=20,
                        left=20
                    ),
                    # キャンセルボタン
                    ft.Container(
                        content=ft.ElevatedButton(
                            "キャンセル",
                            on_click=on_cancel,
                            bgcolor=Colors.RED
                        ),
                        top=20,
                        right=20
                    )
                ]),
                width=1200,
                height=800
            )
        )

    def show_message(self, message: str):
        self.status_text.value = message
        self._update_ui()