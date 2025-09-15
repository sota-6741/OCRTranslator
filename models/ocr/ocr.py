from typing import Dict, Any, List, Protocol
import sys
import os
from pathlib import Path
import platform
import pytesseract
import numpy as np

from models.ocr.preprocess import run_pipeline

class IOCR(Protocol):
    """OCR インターフェース"""

    engine_name: str
    def extract_text(self, image: np.ndarray) -> str: ...


class TesseractOCR(IOCR):
    """
    画像からテキストを抽出するためのOCRユーティリティクラス

    前処理を行った後，pytesseractを用いて画像から文字認識を実施します

    主なメソッド:
        - 画像から文字を抽出
    """
    def __init__(self, language: str="eng"):

        self.language = language

        self.tesseract_config = ""

        # PyInstaller の場合は _MEIPASS が使われる。そうでなければこのファイルのディレクトリを基準にする。
        base_directory = getattr(sys, "_MEIPASS", None)
        if base_directory is None:
            base_directory = os.path.dirname(os.path.abspath(__file__))
        base_dir = Path(base_directory)

        # プロジェクト内での tesseract 配置想定
        # Windows は Tesseract-OCR フォルダ（あなたの tree に合わせて）
        # Linux は tesseract_bin/linux/bin と lib を想定
        system = platform.system()
        if system == "Windows":
            tesseract_bin_dir = base_dir.joinpath("..", "..", "tesseract_bin", "Tesseract-OCR")
            tess_bin = tesseract_bin_dir.joinpath("tesseract.exe")
            tess_lib_dir = None
        elif system == "Linux":
            tesseract_bin_dir = base_dir.joinpath("..", "..", "tesseract_bin", "linux", "bin")
            tess_bin = tesseract_bin_dir.joinpath("tesseract")
            tess_lib_dir = base_dir.joinpath("..", "..", "tesseract_bin", "linux", "lib")
        else:
            raise RuntimeError("非対応のOSです．")

        # 絶対パスに正規化
        tess_bin = str(tess_bin.resolve())
        if tess_lib_dir is not None:
            tess_lib_dir = str(tess_lib_dir.resolve())

        # pytesseract に使用する実行ファイルを指定
        pytesseract.pytesseract.tesseract_cmd = tess_bin

        # tessdata のパス（同梱 tessdata を想定）
        tessdata_directory = base_dir.joinpath("..", "..", "tessdata")
        self.tessdata_directory = str(tessdata_directory.resolve())
        self.tesseract_config += f' --tessdata-dir "{self.tessdata_directory}"'

        # **重要**: 同梱した lib を優先するため、環境変数をセット
        # (pytesseract が呼ぶ子プロセスはこの環境を継承します)
        if tess_lib_dir:
            # 既存の LD_LIBRARY_PATH を壊さない形で先頭に追加
            prev = os.environ.get("LD_LIBRARY_PATH", "")
            os.environ["LD_LIBRARY_PATH"] = tess_lib_dir + (":" + prev if prev else "")

        # Windows の場合、もし必要なら PATH に bin を追加しておく（子プロセス用）
        if system == "Windows":
            prev_path = os.environ.get("PATH", "")
            os.environ["PATH"] = os.path.dirname(tess_bin) + (os.pathsep + prev_path if prev_path else "")

    def extract_text(self, image: np.ndarray) -> str:
        """画像から文字を抽出するメソッド

        Returns:
            str: 画像から抽出されたテキスト
        """
        # 前処理の実行
        processed_image, _ = run_pipeline(image)

        return pytesseract.image_to_string(processed_image, self.language, config=self.tesseract_config)

    @property
    def engine_name(self) -> str:
        """OCRエンジンの名前"""
        return "Tesseract"


class OCRFactory:
    """OCRエンジンのファクトリークラス"""
    _ocr_engines = {
        "tesseract": TesseractOCR,
    }

    @staticmethod
    def create_ocr(engine_type: str, language: str = "eng") -> IOCR:
        if engine_type not in OCRFactory._ocr_engines:
            raise ValueError(f"サポートされていないエンジンタイプです: {engine_type}")

        engine_class = OCRFactory._ocr_engines[engine_type]
        return engine_class(language=language)

    @staticmethod
    def get_available_engines() -> List[str]:
        """利用可能なエンジン一覧を取得"""
        return list(OCRFactory._ocr_engines.keys())

class OCREngine:
    """OCRエンジンのコンテキストクラス"""

    def __init__(self, strategy: IOCR):
        self._strategy = strategy

    def set_strategy(self, strategy: IOCR):
        """OCRエンジンを切り替える"""
        self._strategy = strategy

    def extract_text(self, image: np.ndarray) -> str:
        """現在のエンジンでテキスト抽出"""
        return self._strategy.extract_text(image)

    def get_engine_info(self) -> Dict[str, Any]:
        """OCRエンジンの情報を取得"""
        return {
            "engine": self._strategy.engine_name
        }
