
import flet as ft

import asyncio

from models.image_manager.image_manager import RectangleCoordinates
from models.ocr.ocr import OCREngine, OCRFactory
from models.translator.translator import TranslationEngine, TranslatorFactory, TranslationConfig

from views.capture_overlay import CaptureOverlay

class MainView:

    def __init__(self,ocr_factory: OCRFactory,
                 translation_factory: TranslatorFactory,
                 ):
        self.page: ft.Page

        self.ocr_factory = ocr_factory
        self.translation_factory = translation_factory

        self._worker_task: asyncio.Task | None=None
        self._overlay: CaptureOverlay | None=None

        self._init_components()

    def _init_components(self):
        """UI コンポーネントの初期化"""
        # 画面キャプチャボタン

        self.capture_button = ft.ElevatedButton(
            "画面キャプチャ",
            on_click = lambda e: self.on_capture_button
        )

        # 結果表示
        self.result_text = ft.TextField(
            label="結果",
            multiline=True,
            read_only=True,
            min_lines=8,
            expand=True
        )

        self.status_text = ft.Text("準備完了")

        # ルートコンテナ
        self._root = ft.Column(
            [
                ft.Text("OCR Translator", size=24),
                ft.Row([self.capture_button]),
                self.result_text
            ],
            spacing=12,
            expand=True
        )

    def build(self) -> ft.Control:
        return self._root

    def set_page(self, page: ft.Page):
        """ページを受け取り UI を追加（アプリ起動時に呼ぶ）"""
        self.page = page
        # overlay をページベースで一度だけ作る（再利用可）
        self._overlay = CaptureOverlay(self.page)
        try:
            self.page.add(self.build())
        except Exception:
            try:
                self.page.controls.append(self.build())
                self.page.update()
            except Exception:
                pass

    def on_capture_button(self, e: ft.ControlEvent):
        if not self.page:
            return

        # キャンセル中のワーカーがあればキャンセルしておく
        if self._worker_task and not self._worker_task.done():
            try:
                self._worker_task.cancel()
            except Exception:
                pass

        # overlay を開き、選択確定時に _on_area_captured を呼んでもらう
        if not self._overlay:
            self._overlay = CaptureOverlay(self.page)


        self._overlay.show()
        self.status_text.value = "範囲選択中..."
        self.page.update()

    def _on_area_captured(self, rect: RectangleCoordinates, image):
        """
        overlay -> 呼ばれる: rect と PIL.Image（または None）が渡される想定。
        ここで画像が None の場合は ImageManager を使ってキャプチャを行う。
        """
        # 既にワーカーが動いていたらキャンセルして新しいタスクを起動
        if self._worker_task and not self._worker_task.done():
            try:
                self._worker_task.cancel()
            except Exception:
                pass

        loop = asyncio.get_event_loop()
        self._worker_task = loop.create_task(self._orchestrate(image))

    async def _orchestrate(self, image):
        try:
            self.status_text.value = "キャプチャ/準備中..."
            self.page.update()

            loop = asyncio.get_event_loop()



            # OCR エンジン初期化（ファクトリ呼び出しは実装に合わせて調整）
            try:
                ocr_strategy = self.ocr_factory.create_ocr("tesseract", "jpn")
                ocr_engine = OCREngine(ocr_strategy)
            except Exception as ex:
                self.status_text.value = f"OCR初期化失敗: {ex}"
                self.page.update()
                return

            self.status_text.value = "OCR 実行中..."
            self.page.update()
            text = await loop.run_in_executor(None, ocr_engine.extract_text, image)

            # 翻訳エンジン初期化
            self.result_text.value = f"OCR:\n{text}\n\n翻訳:\n(翻訳中...)"
            self.status_text.value = "翻訳準備中..."
            self.page.update()

            try:
                config = TranslationConfig("auto", "ja")
                translator_strategy = self.translation_factory.create_translator("Google translator", text, config)
                translation_engine = TranslationEngine(translator_strategy)
            except Exception:
                translation_engine = None

            translated = ""
            if translation_engine:
                translated = await loop.run_in_executor(None, translation_engine.translated_text)
            else:
                translated = "(翻訳エンジン初期化失敗)"

            # 最終表示
            self.result_text.value = f"OCR:\n{text}\n\n翻訳:\n{translated}"
            self.status_text.value = "処理完了"
            self.page.update()

        except asyncio.CancelledError:
            # キャンセル時の表示
            self.status_text.value = "処理キャンセル"
            self.page.update()
        except Exception as ex:
            self.status_text.value = f"エラー: {ex}"
            try:
                self.page.open(ft.SnackBar(ft.Text(str(ex)), open=True))
                self.page.update
            except Exception:
                pass
        finally:
            self._worker_task = None
