import pytesseract
import numpy as np
import cv2
from PIL import Image

class OCR():
    """
    画像からテキストを抽出するためのOCRユーティリティクラス

    前処理（グレースケール化や階調変換など）を行った後，
    pytesseractを用いて画像から文字認識を実施します

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
            PreProcessor.convert_cv2_to_pil
        ]

        pre_processed_image = image
        for func in pipeline:
            pre_processed_image = func(pre_processed_image)

        return pytesseract.image_to_string(pre_processed_image, lang="eng")

