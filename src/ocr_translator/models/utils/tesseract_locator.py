from typing import Optional
from pathlib import Path
import sys
import os
import platform
import subprocess

def get_base_dir(override: Optional[str | Path] = None) -> Path:
    """
    プロジェクトのルートディレクトリを取得する

    Args:
        override: 明示的なパス指定
    Returns:
        Path: プロジェクトルートのパス
    """
    if override:
        return Path(override)
    if getattr(sys, "frozen", False):
        # PyInstaller: onefileは_MEIPASS、onedirはexeの親ディレクトリ
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    # 通常: utils/ のひとつ上がルートディレクトリ
    return Path(__file__).resolve().parent.parent.parent.parent

def find_tesseract_folder(base_dir: Path) -> Path | None:
    """
    `tesseract_bin` ディレクトリを探索する。

    開発環境とPyInstallerビルドの両方に対応するため、複数の候補パスを検索する。
    固定パスで見つからない場合は、`base_dir`内を再帰的に探索する。

    Args:
        base_dir (Path): 探索の基準ディレクトリ。

    Returns:
        Path | None: `tesseract_bin`のパス。見つからない場合はNone。
    """

    candidates = [
        base_dir / "tesseract_bin",
        base_dir / "_internal" / "tesseract_bin",
        base_dir.parent / "tesseract_bin",
        base_dir.parent.parent / "tesseract_bin",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    # 最終手段: 再帰探索（小さいツリーなら OK）
    try:
        for p in base_dir.rglob("tesseract_bin"):
            if p.is_dir():
                return p
    except StopIteration:
        return None
    except Exception:
        return None

def assemble_tesseract_paths(tess_root: Path) -> dict:
    """
    Tesseractの関連パスをOSに応じて組み立てる。

    Args:
        tess_root (Path): `tesseract_bin` ディレクトリのパス。

    Returns:
        dict: 以下のキーを含む辞書:
            - "tess_bin": Tesseract実行ファイルのパス。
            - "tess_lib_dir": Tesseractライブラリのパス (Linuxのみ)。
            - "tessdata": `tessdata` ディレクトリのパス。
    """
    system = platform.system()
    if system == "Linux":
        return {
            "tess_bin": tess_root / "linux" / "bin" / "tesseract",
            "tess_lib_dir": tess_root / "linux" / "lib",
            "tessdata": Path(tess_root) / "linux" / "tessdata"  # if tessdata is sibling; adjust if needed
        }
    elif system == "Windows":
        return {
            "tess_bin": tess_root / "windows" / "Tesseract-OCR" / "tesseract.exe",
            "tess_lib_dir": None,
            "tessdata": Path(tess_root) / "windows" / "tessdata"  # adjust if necessary
        }
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def configure_environment(tessdata_path: Path | None,
                          tess_lib_dir: Path | None,
                          tess_bin: Path | None,
                          set_pytesseract: bool = True,
                          ensure_executable: bool = True) -> None:
    """
    Tesseractの実行に必要な環境変数を設定し、実行権限を付与する。

    - `TESSDATA_PREFIX`: tessdataディレクトリのパスを設定する。
    - `LD_LIBRARY_PATH`: Tesseractの共有ライブラリパスを設定する (Linuxのみ)。
    - `pytesseract.tesseract_cmd`: `pytesseract` に実行ファイルのパスを教える。
    - 実行権限: Tesseract実行ファイルに実行権限を付与する (非Windows)。

    Args:
        tessdata_path (Path | None): `tessdata` ディレクトリのパス。
        tess_lib_dir (Path | None): 共有ライブラリのディレクトリパス (Linux)。
        tess_bin (Path | None): Tesseract実行ファイルのパス。
        set_pytesseract (bool): `pytesseract` にコマンドパスを設定するかどうか。
        ensure_executable (bool): 実行ファイルに実行権限を付与するかどうか。
    """
    if tessdata_path:
        os.environ["TESSDATA_PREFIX"] = str(tessdata_path)

    system = platform.system()
    if tess_lib_dir and tess_lib_dir.exists() and system == "Linux":
        old = os.environ.get("LD_LIBRARY_PATH", "")
        os.environ["LD_LIBRARY_PATH"] = str(tess_lib_dir) + (":" + old if old else "")

    if tess_bin and tess_bin.exists():
        if ensure_executable and system != "Windows":
            try:
                tess_bin.chmod(0o755)
            except Exception:
                # 無理なら続行し、後で実行時に失敗する
                pass
        if set_pytesseract:
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = str(tess_bin)
            except Exception:
                # pytesseract がない環境でも import 時に失敗しないように無視
                pass

def probe_tesseract_version(tess_bin: Path) -> str | None:
    """
    tesseract --version を呼んでバージョン文字列を返す。失敗時は None。
    """
    try:
        out = subprocess.run([str(tess_bin), "--version"], capture_output=True, text=True, check=True)
        return out.stdout.strip().splitlines()[0] if out.stdout else None
    except Exception:
        return None
