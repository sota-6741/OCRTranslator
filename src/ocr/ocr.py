from typing import Dict, Any, List
from abc import ABC, abstractmethod
import pytesseract
import numpy as np

from src.ocr.preprocess import PreProcessor, Pipeline
from src.image_manager.image_manager import ImageConverter

class IOCR(ABC):
    """OCR インターフェース"""
    @abstractmethod
    def read_text(self) -> str:
        """画像からテキストを抽出する"""

    @property
    @abstractmethod
    def extracted_text(self) -> str:
        """抽出結果をプロパティで取得"""

    @property
    @abstractmethod
    def ocr_engine_name(self) -> str:
        """OCRエンジン名を取得"""


class TesseractOCR(IOCR):
    """
    画像からテキストを抽出するためのOCRユーティリティクラス

    前処理を行った後，pytesseractを用いて画像から文字認識を実施します

    主なメソッド:
        - 画像から文字を抽出
    """
    def __init__(self, image: np.ndarray):
        self.input_image = image

        # 画像の前処理
        pipeline = Pipeline()

        pipeline.add_step("grayscale", PreProcessor.apply_grayscale)
        pipeline.add_step("LIT", PreProcessor.apply_lit)
        pipeline.add_step("convert_cv2_to_pil", ImageConverter.convert_cv2_to_pil)

        self.processed_image, self.log = pipeline.execute(self.input_image)

        self._extracted_text: str = self.read_text()

    @property
    def extracted_text(self) -> str:
        """画像から抽出した文字"""
        return self._extracted_text

    @property
    def ocr_engine_name(self) -> str:
        """OCRエンジンの名前"""
        return "Tesseract"

    def read_text(self) -> str:
        """画像から文字を抽出するメソッド

        Args:
            image (np.ndarray): OCR処理を行う画像

        Returns:
            str: 画像から抽出されたテキスト
        """

        return pytesseract.image_to_string(self.processed_image, lang="eng")

class OCRFactory:
    """OCRエンジンのファクトリークラス"""
    _ocr_engines = {
        "tesseract": TesseractOCR,
    }

    @staticmethod
    def create_ocr(engine_type: str, image: np.ndarray) -> IOCR:
        try:
            return OCRFactory._ocr_engines[engine_type](image=image)
        except KeyError as e:
            raise ValueError(f"サポートされていないエンジンタイプです: {engine_type}") from e

    @staticmethod
    def get_available_engines() -> List[str]:
        """利用可能なエンジン一覧を取得"""
        return list(OCRFactory._ocr_engines.keys())

class OCREngine:
    """OCRエンジンのコンテキストクラス"""

    def __init__(self, strategy: IOCR):
        self._strategy = strategy

    def set_strategy(self, strategy: IOCR):
        """OCRエンジンを切り替える"""
        self._strategy = strategy

    def extract_text(self) -> str:
        """現在のエンジンでテキスト抽出"""
        return self._strategy.extracted_text

    def get_engine_info(self) -> Dict[str, Any]:
        """OCRエンジンの情報を取得"""
        return {
            "engine": self._strategy.ocr_engine_name,
            "text": self._strategy.extracted_text
        }
