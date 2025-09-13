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

    # デバッグ用：mssで実際に使用される座標をログ出力
    mss_coords = rect.mss_coordinates
    print(f"MSS: Capturing area - left={mss_coords['left']}, top={mss_coords['top']}, width={mss_coords['width']}, height={mss_coords['height']}")

    # スクリーン情報も出力
    with mss.mss() as sct:
        monitors = sct.monitors
        print(f"MSS: Available monitors - {len(monitors)} monitors")
        for i, monitor in enumerate(monitors):
            print(f"MSS: Monitor {i} - {monitor}")

    shot: ScreenShot = mss_instance.grab(rect.mss_coordinates)
    print(f"MSS: Captured image size - {shot.width}x{shot.height}")

    cv2_img = convert_mss_to_cv2(shot)
    # shot を明示的に破棄
    del shot
    return cv2_img  # numpy array を返す（ミュータブルだが外側で扱う）