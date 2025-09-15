from typing import Dict, Any, List, Protocol
import sys
import os
from pathlib import Path
import subprocess
import platform
import pytesseract
import numpy as np

from models.ocr.preprocess import run_pipeline
from models.utils.tesseract_locator import get_base_dir, find_tesseract_folder, assemble_tesseract_paths, configure_environment, probe_tesseract_version

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
    def __init__(self, language: str="eng", tess_bin: Path | None = None, tessdata_path: Path | None = None, tesseract_config: str = "--psm 3"):
        self.language = language
        self.tess_bin = Path(tess_bin) if tess_bin else None
        self.tessdata_path = Path(tessdata_path) if tessdata_path else None
        self.tesseract_config = tesseract_config

        # pytesseract と環境変数の設定（もしファイルが与えられていれば）
        if self.tessdata_path and self.tessdata_path.exists():
            os.environ["TESSDATA_PREFIX"] = str(self.tessdata_path)

        if self.tess_bin and self.tess_bin.exists():
            # 権限確保（Linux）
            try:
                if platform.system() != "Windows":
                    self.tess_bin.chmod(0o755)
            except Exception:
                pass
            # pytesseract にバイナリを伝える
            try:
                pytesseract.pytesseract.tesseract_cmd = str(self.tess_bin)
            except Exception:
                pass

    def check_tesseract(self) -> bool:
        """tesseract が存在して実行可能かをチェック"""
        if not self.tess_bin or not self.tess_bin.exists():
            return False
        try:
            out = subprocess.run([str(self.tess_bin), "--version"], capture_output=True, text=True, check=True)
            return True
        except Exception:
            return False

    def extract_text(self, image: np.ndarray) -> str:
        """画像から文字を抽出するメソッド

        Returns:
            str: 画像から抽出されたテキスト
        """
        processed_image, _ = run_pipeline(image)
        # pytesseract.image_to_string(image, lang=..., config=...)
        return pytesseract.image_to_string(processed_image, lang=self.language, config=self.tesseract_config)

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
    def create_ocr(engine_type: str, language: str = "eng",  base_dir_override: str | Path | None = None, require_tesseract: bool = True) -> IOCR:
        if engine_type not in OCRFactory._ocr_engines:
            raise ValueError(f"サポートされていないエンジンタイプです: {engine_type}")

        engine_class = OCRFactory._ocr_engines[engine_type]
        # tesseract 用の探索と環境設定
        base_dir = get_base_dir(base_dir_override)
        tess_root = find_tesseract_folder(base_dir)

        if tess_root:
            info = assemble_tesseract_paths(tess_root)
            tess_bin = info.get("tess_bin")
            tess_lib_dir = info.get("tess_lib_dir")
            tessdata = info.get("tessdata", base_dir / "tessdata")
            # 環境変数や LD_LIBRARY_PATH, pytesseract 設定を行う
            configure_environment(tessdata, tess_lib_dir, tess_bin, set_pytesseract=True)

            if require_tesseract:
                if tess_bin is None:
                    raise RuntimeError("tesseract_bin が None です。base_dir の設定を確認してください。")
                ver = probe_tesseract_version(tess_bin)
                if not ver:
                    raise RuntimeError("tesseract が見つかったが実行できません。依存ライブラリを確認してください。")
        else:
            tess_bin = None
            tessdata = None
            if require_tesseract:
                raise RuntimeError(f"tesseract_bin が見つかりません。base_dir={base_dir}")

        # OCR インスタンス生成（最低限の情報だけ渡す）
        return engine_class(language=language, tess_bin=tess_bin, tessdata_path=tessdata)

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
