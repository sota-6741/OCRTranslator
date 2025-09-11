import numpy as np
from PIL import Image
import cv2
from mss.screenshot import ScreenShot

class ImageConverter:
    """画像形式を変換するクラス

    主なメソッド:
        - OpenCV形式（NumPy配列）の画像をPIL.Image形式に変換するメソッド
        - mss形式 (ScreenShotクラス)の画像をOpenCV形式（NumPy配列）に変換するメソッド

    """

    @staticmethod
    def convert_cv2_to_pil(image: np.ndarray) -> Image.Image:
        """
        OpenCV形式（NumPy配列）の画像をPIL.Image形式に変換するメソッド

        Args:
            image (np.ndarray): OpenCV形式の画像

        Returns:
            Image.Image: PIL形式の画像
        """

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        # メモリ開放
        del rgb_image

        return pil_image

    @staticmethod
    def convert_mss_to_cv2(image: ScreenShot):
        """
        mss形式 (ScreenShotクラス)の画像をOpenCV形式（NumPy配列）に変換するメソッド

        Args:
            image (ScreenShot): mss形式 (ScreenShotクラス)の画像

        Returns:
            np.ndarray: OpenCV形式の画像
        """

        image_array = np.array(image)
        bgr_image = cv2.cvtColor(image_array, cv2.COLOR_BGRA2BGR)

        # メモリ開放
        del image_array

        return bgr_image
