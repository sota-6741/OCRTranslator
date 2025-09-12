import numpy as np
from PIL import Image
import cv2
from mss.screenshot import ScreenShot

def convert_cv2_to_pil(image: np.ndarray) -> Image.Image:
    """
    OpenCV形式（NumPy配列）の画像をPIL.Image形式に変換する関数

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

def convert_mss_to_cv2(image: ScreenShot) -> np.ndarray:
    """
    mss形式 (ScreenShotクラス)の画像をOpenCV形式（NumPy配列）に変換する関数

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
