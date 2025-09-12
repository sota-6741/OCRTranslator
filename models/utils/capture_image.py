from dataclasses import dataclass
from typing import Callable, Dict, Optional, Union
import datetime
from pathlib import Path
import numpy as np
import mss
from mss.screenshot import ScreenShot

from models.utils.image_converter import convert_mss_to_cv2

@dataclass
class Point:
    x: int
    y: int

@dataclass
class RectangleCoordinates:
    x: int
    y: int
    width: int
    height: int

    @property
    def mss_coordinates(self) -> Dict[str, int]:
        return {"left": self.x, "top": self.y, "width": self.width, "height": self.height}

# --- 純粋関数群 ---
def crop_cv2_image(image: np.ndarray, rect: RectangleCoordinates) -> np.ndarray:
    """image は numpy.ndarray（H, W, C）。入力を変更しない -> 新しい配列を返す。"""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    # スライスはビューを返すのでコピーして純粋性を保つ
    cropped = image[y:y+h, x:x+w].copy()
    return cropped

def make_filename(prefix: str, now_str: str) -> str:
    return f"{prefix}_{now_str}.png"

def capture_with_mss(rect: RectangleCoordinates, mss_instance: Optional[object] = None) -> np.ndarray:
    """mss の grab を使って画像を取得する（副作用）。"""
    if mss_instance is None:
        mss_instance = mss.mss()

    shot: ScreenShot = mss_instance.grab(rect.mss_coordinates)
    cv2_img = convert_mss_to_cv2(shot)
    # shot を明示的に破棄
    del shot
    return cv2_img  # numpy array を返す（ミュータブルだが外側で扱う）

def save_image_impure(image: np.ndarray, filepath: Path) -> Path:
    """cv2.imwrite などの副作用を行う薄いラッパー。"""
    import cv2
    filepath.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(filepath), image)
    return filepath

def current_timestamp_str() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")

def capture_and_save(rect: RectangleCoordinates,
                     capture_fn: Callable[[RectangleCoordinates], np.ndarray] = capture_with_mss,
                     save_fn: Callable[[np.ndarray, Path], Path] = save_image_impure,
                     now_fn: Callable[[], str] = current_timestamp_str,
                     filename_prefix: str = "tmp",
                     temp_dir: Path = Path("Images/temp")) -> Path:
    # 副作用を行う場所はここだけ
    img = capture_fn(rect)                     # 副作用: 画面取得
    # ここからは純粋処理（コピーして安全に扱う）
    # 例: cropped = crop_cv2_image(img, smaller_rect)
    filename = make_filename(filename_prefix, now_fn())
    filepath = temp_dir / filename
    saved_path = save_fn(img, filepath)        # 副作用: ファイル書き込み
    return saved_path