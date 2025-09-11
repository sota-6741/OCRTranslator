from typing import Callable, List, Dict, Any
import numpy as np
import time
import cv2

from src.image_manager.image_manager import ImageConverter

class PreProcessor():
    """
    画像の前処理を行うためのユーティリティクラス

    主な機能:
        - グレースケール化
        - 線形階調変換（コントラスト・明るさ調整）
    """
    @staticmethod
    def run_pipline(image: np.ndarray):
         # 画像の前処理
        pipeline = Pipeline()

        pipeline.add_step("grayscale", PreProcessor.apply_grayscale)
        pipeline.add_step("LIT", PreProcessor.apply_lit)
        pipeline.add_step("convert_cv2_to_pil", ImageConverter.convert_cv2_to_pil)
        return pipeline.execute(image=image)

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
