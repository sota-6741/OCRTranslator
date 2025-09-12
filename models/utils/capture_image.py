from dataclasses import dataclass
from typing import Callable, Dict, Optional, Union
import datetime
from pathlib import Path
import numpy as np
import mss
from mss.screenshot import ScreenShot

from models.utils.image_converter import convert_mss_to_cv2

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
def capture_with_mss(rect: RectangleCoordinates, mss_instance: Optional[object] = None) -> np.ndarray:
    """mss の grab を使って画像を取得する（副作用）。"""
    if mss_instance is None:
        mss_instance = mss.mss()

    shot: ScreenShot = mss_instance.grab(rect.mss_coordinates)
    cv2_img = convert_mss_to_cv2(shot)
    # shot を明示的に破棄
    del shot
    return cv2_img  # numpy array を返す（ミュータブルだが外側で扱う）