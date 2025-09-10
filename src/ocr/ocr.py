from typing import Callable, List, Dict, Any
from abc import ABC, abstractmethod
import pytesseract
import numpy as np
import time
import cv2

from src.image_manager.image_manager import ImageConverter

class IOCR(ABC):
    """OCR インターフェース"""
    @abstractmethod
    def read_text(self) -> str:
        """画像からテキストを抽出する"""
        pass

    @property
    @abstractmethod
    def extracted_text(self) -> str:
        """抽出結果をプロパティで取得"""
        pass

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
        def extract_text(self) -> str:
            return self._extracted_text


    def read_text(self) -> str:
        """画像から文字を抽出するメソッド

        Args:
            image (np.ndarray): OCR処理を行う画像

        Returns:
            str: 画像から抽出されたテキスト
        """

        return pytesseract.image_to_string(self.processed_image, lang="eng")

class PreProcessor():
    """
    画像の前処理を行うためのユーティリティクラス

    主な機能:
        - グレースケール化
        - 線形階調変換（コントラスト・明るさ調整）
    """

    @staticmethod
    def apply_grayscale(image: np.ndarray):
        """画像をグレイスケール化

        Args:
            image (np.ndarray): 入力画像
        """

        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def apply_lit(image: np.ndarray, alpha: float=1, beta: float=0):
        """線形階調変換を画像に適用

        Args:
            image (np.ndarray): 入力画像
            alpha (float): コントラスト調整係数 (default: 1)
            beta (float): 明るさ調整係数 (default: 0)

        Returns:
            np.ndarray: 階調変換後の画像(NupPy配列)
        """

        # テーブル作成
        look_up_table = alpha * np.arange(256) + beta
        # [0, 255]でクリップし，uint8型にする
        look_up_table = np.clip(look_up_table, 0, 255).astype(np.uint8)

        return cv2.LUT(image, look_up_table)

class Pipeline:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, name: str, function: Callable):
        self.steps.append({"name": name, "function": function})

    def execute(self, image: np.ndarray):

        log = []
        current_image = image.copy()

        for step in self.steps:
            t0 = time.time()
            try:
                current_image = step["function"](current_image)
                log.append({
                    "step": step["name"],
                    "status": "success",
                    "time": time.time() - t0
                })
            except Exception as e:
                log.append({
                    "step": step["name"],
                    "status": "failed",
                    "error": str(e)
                })
                break
        return current_image, log