"""OCRTranslator アプリケーション エントリーポイント（簡潔版）"""

import sys
import logging
import flet as ft

from views.main_view import MainView
from models.ocr.ocr import OCRFactory
from models.translator.translator import TranslatorFactory

def main(page: ft.Page):
    # ページの基本設定
    page.title = "OCR Translator"
    page.window.width = 800
    page.window.height = 600
    page.window.min_width = 600
    page.window.min_height = 400
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20

    # ページを設定（set_pageは内部でUIを追加します）
    ocr_factory = OCRFactory
    translator_factory = TranslatorFactory

    view = MainView(ocr_factory=ocr_factory,
                    translation_factory=translator_factory
    )
    view.set_page(page)

if __name__ == "__main__":
    ft.app(target=main)
