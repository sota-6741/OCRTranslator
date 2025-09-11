from typing import Dict, Any, List
from abc import ABC, abstractmethod
import pytesseract
import numpy as np

from models.ocr.preprocess import PreProcessor

class IOCR(ABC):
    """OCR インターフェース"""

    @abstractmethod
    def extract_text(self, image: np.ndarray) -> str:
        """画像からテキストを抽出する"""

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """OCRエンジン名を取得"""


class TesseractOCR(IOCR):
    """
    画像からテキストを抽出するためのOCRユーティリティクラス

    前処理を行った後，pytesseractを用いて画像から文字認識を実施します

    主なメソッド:
        - 画像から文字を抽出
    """
    def __init__(self, language: str="eng", preprocessor: PreProcessor = None):
        self.language = language
        self.preprocessor = preprocessor or PreProcessor()

    def extract_text(self, image: np.ndarray) -> str:
        """画像から文字を抽出するメソッド

        Returns:
            str: 画像から抽出されたテキスト
        """
        # 前処理の実行
        processed_image, _ = self.preprocessor.run_pipeline(image)

        return pytesseract.image_to_string(processed_image, self.language)

    @property
    def engine_name(self) -> str:
        """OCRエンジンの名前"""
        return "Tesseract"


class OCRFactory:
    """OCRエンジンのファクトリークラス"""
    _ocr_engines = {
        "tesseract": TesseractOCR,
    }

    @staticmethod
    def create_ocr(engine_type: str, language: str = "eng") -> IOCR:
        if engine_type not in OCRFactory._ocr_engines:
            raise ValueError(f"サポートされていないエンジンタイプです: {engine_type}")

        engine_class = OCRFactory._ocr_engines[engine_type]
        return engine_class(language=language)

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

    def extract_text(self, image: np.ndarray) -> str:
        """現在のエンジンでテキスト抽出"""
        return self._strategy.extract_text(image)

    def get_engine_info(self) -> Dict[str, Any]:
        """OCRエンジンの情報を取得"""
        return {
            "engine": self._strategy.engine_name
        }
