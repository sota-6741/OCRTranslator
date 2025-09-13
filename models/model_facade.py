from typing import Optional, List

from models.ocr.ocr import OCRFactory, IOCR
from models.translator.translator import TranslatorFactory, ITranslator, TranslationConfig
from models.utils.capture_image import capture_with_mss, RectangleCoordinates


class ModelFacade:
    """
    Model層のビジネスロジックへのアクセスを簡素化するFacadeクラス。
    Presenter層は、このクラスを通じてModelの機能を利用します。
    """

    def __init__(self):
        # デフォルトのOCRエンジンと言語を設定
        self._ocr_engine: IOCR = OCRFactory.create_ocr("tesseract", language="eng")
        # デフォルトの翻訳エンジンを指定してFactoryをインスタンス化
        self._translator_factory = TranslatorFactory(engine_type="Google")

    def set_ocr_engine(self, engine_type: str, language: str = "eng"):
        """
        使用するOCRエンジンを切り替えます。

        Args:
            engine_type (str): "tesseract" などのエンジンタイプ。
            language (str): OCRの言語。
        """
        self._ocr_engine = OCRFactory.create_ocr(engine_type, language)

    def set_translator_engine(self, engine_type: str):
        """
        使用する翻訳エンジンを切り替えます。

        Args:
            engine_type (str): "Google" などのエンジンタイプ。
        """
        self._translator_factory = TranslatorFactory(engine_type)

    def get_available_ocr_engines(self) -> List[str]:
        """利用可能なOCRエンジンのリストを取得します。"""
        return OCRFactory.get_available_engines()

    def get_available_translator_engines(self) -> List[str]:
        """利用可能な翻訳エンジンのリストを取得します。"""
        return TranslatorFactory.get_available_engines()

    async def translate_image_from_screen(
        self,
        rect: RectangleCoordinates,
        translation_config: Optional[TranslationConfig] = None,
    ) -> tuple[str, str, str]:
        """
        画面の指定領域をキャプチャし、OCRでテキストを抽出し、翻訳します。

        Args:
            rect (RectangleCoordinates): キャプチャする画面領域。
            translation_config (Optional[TranslationConfig]): 翻訳設定。

        Returns:
            tuple[str, str, str]: (翻訳済みテキスト, 抽出された元テキスト, 検出されたソース言語)
        """
        # 1. 画面キャプチャ
        image = capture_with_mss(rect)

        # 2. OCRでテキスト抽出
        extracted_text = self._ocr_engine.extract_text(image)

        if not extracted_text.strip():
            return "", "", ""

        # 3. テキスト翻訳
        translator = self._translator_factory.create(
            config=translation_config,
        )
        translated_text = await translator.translate(extracted_text)
        source_language = translator.source_language

        return translated_text, extracted_text, source_language
