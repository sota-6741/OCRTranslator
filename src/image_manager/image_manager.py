from dataclasses import dataclass
from typing import NamedTuple
import datetime
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import mss
from mss.screenshot import ScreenShot

@dataclass
class Point(NamedTuple):
    """
    2次元空間内の点の座標

    Attributes:
        x (int): 点のx座標
        y (int): 点のy座標
    """
    x: int
    y: int


@dataclass
class RectangleCoordinates(NamedTuple):
    """選択した矩形範囲の座標を管理する

    Attributes:
        top_left (Point): 矩形の左上の座標
        top_right (Point): 矩形の右上の座標
        bottom_left (Point): 矩形の左下の座標
        bottom_right (Point): 矩形の右下の座標

    Properties:
        width (int): 矩形の幅．top_leftとtop_rightの水平距離
        height (int): 矩形の高さ．top_leftとbottom_leftの垂直距離
        rectangle_coordinates (tuple[int, int, int, int]): MSSでスクリーンショットを取るための形式（top_left.x, top_left.y, width, heigth）で矩形の座標を返す
    """
    top_left: Point
    top_right: Point
    bottom_left: Point
    bottom_right: Point

    @property
    def width(self) -> int:
        """矩形の幅"""
        return self.top_right.x - self.top_left.x

    @property
    def height(self) -> int:
        """矩形の高さ"""
        return self.top_left.y - self.bottom_left.y

    @property
    def rectangle_coordinates(self) -> tuple[int, int, int, int]:
        """MSSでの矩形座標"""
        return (self.top_left.x, self.top_left.y, self.width, self.height)


class ImageManager:
    """画像のキャプチャ、取得時のタイムスタンプの取得、画像の保存に関するクラス。"""

    def __init__(self, rectangle_coords: RectangleCoordinates):
        self.rectangle_coordinates: RectangleCoordinates = rectangle_coords
        # Imagesディレクトリの作成
        self.temp_dir = Path("Images/temp")
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def rectangle_capture(self):
        """rectangle_coordinatesを使って矩形範囲の画面をキャプチャ

        Returns:
            image_cv2 (np.ndarray): キャプチャした画像
        """

        screenshot_tool = mss.mss()
        image: ScreenShot = screenshot_tool.grab(self.rectangle_coordinates.rectangle_coordinates)
        cv2_image: np.ndarray = ImageConverter.convert_mss_to_cv2(image=image)

        del image
        return cv2_image

    def _get_timestamp(self):
        """現在のタイムスタンプを取得"""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    def save_image(self, image: np.ndarray, filename: str = "tmp") -> str:
        """指定された画像を一時ディレクトリに保存し、保存先のファイルパスを返す。

        Args:
            image (np.ndarray): 保存する画像
            filename (str): ファイル名のプレフィックス

        Returns:
            str: 保存した画像のファイルパス
        """
        filename = f"{filename}_{self._get_timestamp()}.png"

        filepath = self.temp_dir / filename

        cv2.imwrite(str(filepath), image)

        return str(filepath)


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

        rgb_image = cv2.cutColor(image, cv2.COLOR_BGR2RGB)
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
