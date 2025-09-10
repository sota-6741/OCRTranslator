import pytesseract
import numpy as np
import cv2
from PIL import Image

from src.image_manager.image_manager import ImageConverter

class OCR():
    """
    画像からテキストを抽出するためのOCRユーティリティクラス

    前処理を行った後，pytesseractを用いて画像から文字認識を実施します

    主なメソッド:
        - 画像から文字を抽出
    """

    @staticmethod
    def read_text(image: np.ndarray) -> str:
        """画像から文字を抽出するメソッド

        Args:
            image (np.ndarray): OCR処理を行う画像

        Returns:
            str: 画像から抽出されたテキスト
        """

        # imageの前処理
        pipeline = [
            PreProcessor.apply_grayscale,
            PreProcessor.apply_lit,
            ImageConverter.convert_cv2_to_pil
        ]

        pre_processed_image = image
        for func in pipeline:
            pre_processed_image = func(pre_processed_image)

        return pytesseract.image_to_string(pre_processed_image, lang="eng")

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
            beta (float): 明るさ調整係数 (default: 1)

        Returns:
            np.ndarray: 階調変換後の画像(NupPy配列)
        """

        # テーブル作成
        look_up_table = alpha * np.arange(256) + beta
        # [0, 255]でクリップし，uint8型にする
        look_up_table = np.clip(look_up_table, 0, 255).astype(np.uint8)

        return cv2.LUT(image, look_up_table)