from typing import Optional
import asyncio
from dataclasses import dataclass

from models.ocr.ocr import OCREngine, OCRFactory
from models.translator.translator import TranslationEngine, TranslatorFactory, TranslationConfig
from models.image_manager.image_manager import ImageManager, RectangleCoordinates

@dataclass
class AppState:
    """最小限の状態管理"""
    ocr_result: str = ""
    translation_result: str = ""
    error_message: str = ""
    ocr_button_enabled: bool = False
    translate_button_enabled: bool = False

class MainPresenter:
    """最小限のPresenter実装"""

    def __init__(self, view):
        self.view = view
        self.state = AppState()
        self.image_manager: Optional[ImageManager] = None

        # デフォルト設定で初期化
        self._init_engines()
        self._render()

    def _init_engines(self):
        """デフォルト設定でエンジン初期化"""
        try:
            ocr_strategy = OCRFactory.create_ocr("tesseract", "jpn")
            self.ocr_engine = OCREngine(ocr_strategy)

            config = TranslationConfig("auto", "ja")
            translator_strategy = TranslatorFactory.create_translator(
                "Google translator", "", config
            )
            self.translation_engine = TranslationEngine(translator_strategy)
        except Exception as e:
            self._handle_error(f"初期化エラー: {str(e)}")

    # 簡素化されたイベントハンドラ
    def on_capture(self):
        """画面キャプチャ（固定サイズ）"""
        try:
            # 画面中央の固定サイズエリアを使用（設定UI削除）
            coords = RectangleCoordinates(100, 100, 400, 200)
            self.image_manager = ImageManager(coords)
            self.state.ocr_button_enabled = True
            self.view.show_message("キャプチャエリア設定完了")
            self._render()
        except Exception as e:
            self._handle_error(f"キャプチャエラー: {str(e)}")

    def on_ocr(self):
        """OCR実行"""
        if not self.image_manager:
            self._handle_error("キャプチャが必要です")
            return

        asyncio.create_task(self._execute_ocr())

    def on_translate(self):
        """翻訳実行"""
        if not self.state.ocr_result:
            self._handle_error("OCR結果が必要です")
            return

        asyncio.create_task(self._execute_translation())

    async def _execute_ocr(self):
        """OCR実行（簡素化）"""
        try:
            image = await asyncio.get_event_loop().run_in_executor(
                None, self.image_manager.rectangle_capture
            )
            text = await asyncio.get_event_loop().run_in_executor(
                None, self.ocr_engine.extract_text, image
            )

            self.state.ocr_result = text
            self.state.translate_button_enabled = bool(text.strip())
            self._render()
        except Exception as e:
            self._handle_error(f"OCRエラー: {str(e)}")

    async def _execute_translation(self):
        """翻訳実行（簡素化）"""
        try:
            config = TranslationConfig("auto", "ja")
            translator_strategy = TranslatorFactory.create_translator(
                "Google translator", self.state.ocr_result, config
            )
            self.translation_engine.set_strategy(translator_strategy)

            result = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.translation_engine.translated_text()
            )

            self.state.translation_result = result
            self._render()
        except Exception as e:
            self._handle_error(f"翻訳エラー: {str(e)}")

    def _handle_error(self, message: str):
        """エラー処理（簡素化）"""
        self.state.error_message = message
        self._render()

    def _render(self):
        """状態反映"""
        self.view.render(self.state)