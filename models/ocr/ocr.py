from typing import Dict, Any, List, Protocol
import sys
import os
import platform
import pytesseract
import numpy as np

from models.ocr.preprocess import run_pipeline

class IOCR(Protocol):
    """OCR インターフェース"""

    engine_name: str
    def extract_text(self, image: np.ndarray) -> str: ...


class TesseractOCR(IOCR):
    """
    画像からテキストを抽出するためのOCRユーティリティクラス

    前処理を行った後，pytesseractを用いて画像から文字認識を実施します

    主なメソッド:
        - 画像から文字を抽出
    """
    def __init__(self, language: str="eng"):

        self.language = language

        self.tesseract_config = ""

        # tesseract実行ファイルを指定
        # PyInstaller対応: リソースパスの取得
        base_directory = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

        tesseract_bin = os.path.join(base_directory, "..", "..", "tesseract_bin", "Tesseract-OCR")
        tessdata_directory = os.path.join(base_directory, "..", "..", "tessdata")
        system = platform.system()
        if system == "Windows":
            tesseract_cmd = os.path.join(tesseract_bin, "tesseract.exe")
        elif system == "Linux":
            tesseract_cmd = os.path.join(tesseract_bin, "tesseract")
        else:
            raise RuntimeError("非対応のOSです．")
        # tessdataを指定
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        self.tessdata_directory = tessdata_directory
        self.tesseract_config += f'--tessdata-dir "{self.tessdata_directory}"'

    def extract_text(self, image: np.ndarray) -> str:
        """画像から文字を抽出するメソッド

        Returns:
            str: 画像から抽出されたテキスト
        """
        # 前処理の実行
        processed_image, _ = run_pipeline(image)

        return pytesseract.image_to_string(processed_image, self.language, config=self.tesseract_config)

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
