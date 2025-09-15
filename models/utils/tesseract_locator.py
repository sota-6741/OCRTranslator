from pathlib import Path
import sys
import os
import platform
import subprocess

def get_base_dir(override: str | Path | None = None) -> Path:
    if override:
        return Path(override)
    if getattr(sys, "frozen", False):
        # onefile は _MEIPASS、onedir は exe の親ディレクトリ
        if hasattr(sys, "_MEIPASS"):
            return Path(sys._MEIPASS)
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent  # utils/ の一つ上 (プロジェクトルート想定)

def find_tesseract_folder(base_dir: Path) -> Path | None:
    """
    base_dir を起点に tesseract_bin を見つける。見つからなければ None を返す。
    候補リストを増やせば柔軟に対応できる。
    """
    candidates = [
        base_dir / "tesseract_bin",
        base_dir / "_internal" / "tesseract_bin",
        base_dir.parent / "tesseract_bin",
        base_dir.parent.parent / "tesseract_bin",
    ]
    for c in candidates:
        if c.exists():
            return c

    # 最終手段: 再帰探索（小さいツリーなら OK）
    try:
        for p in base_dir.rglob("tesseract_bin"):
            if p.is_dir():
                return p
    except Exception:
        pass
    return None

def assemble_tesseract_paths(tess_root: Path) -> dict:
    """
    tess_root から OS に応じた tess_bin と tess_lib_dir を返す dict。
    """
    system = platform.system()
    if system == "Linux":
        return {
            "tess_bin": tess_root / "linux" / "bin" / "tesseract",
            "tess_lib_dir": tess_root / "linux" / "lib",
            "tessdata": Path(tess_root).parent / "tessdata"  # if tessdata is sibling; adjust if needed
        }
    elif system == "Windows":
        return {
            "tess_bin": tess_root / "windows" / "Tesseract-OCR" / "tesseract.exe",
            "tess_lib_dir": None,
            "tessdata": Path(tess_root) / "tessdata"  # adjust if necessary
        }
    else:
        raise RuntimeError(f"Unsupported platform: {system}")

def configure_environment(tessdata_path: Path | None,
                          tess_lib_dir: Path | None,
                          tess_bin: Path | None,
                          set_pytesseract: bool = True,
                          ensure_executable: bool = True) -> None:
    """
    環境変数や実行権限のセットを行う。
    - tessdata_path: Path to tessdata folder (may be None)
    - tess_lib_dir: Path to native libs (Linux)
    - tess_bin: Path to tesseract executable
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