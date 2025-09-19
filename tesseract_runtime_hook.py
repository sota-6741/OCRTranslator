import os, sys, stat, platform

if platform.system() == "Linux":
    def _get_base():
        if getattr(sys, "frozen", False):
            _base = getattr(sys, "_MEIPASS", None)
            if not _base:
                _base = os.path.dirname(sys.executable)
        else:
            # 開発実行時： spec の場所を基準にする（hook が置かれる場所）
            # __file__ inside hook points to the hook file path when running normally
            _base = os.path.dirname(__file__)
        return _base

    base = _get_base()

    # Expect layout inside bundle:
    # base/
    #   tesseract/                <- binary here
    #   tesseract/lib/            <- .so here
    #   tessdata/ or data/tessdata/ <- tessdata here

    tesseract_exec = os.path.join(base, "tesseract", "tesseract")
    if sys.platform.startswith("win"):
        tesseract_exec = os.path.join(base, "tesseract", "tesseract.exe")

    # Ensure executable bit (non-Windows)
    if not sys.platform.startswith("win"):
        try:
            st = os.stat(tesseract_exec)
            os.chmod(tesseract_exec, st.st_mode | stat.S_IEXEC)
        except Exception:
            pass

    # Point LD_LIBRARY_PATH to bundled libs (so child tesseract process finds .so)
    libdir = os.path.join(base, "tesseract", "lib")
    if os.path.isdir(libdir):
        prev = os.environ.get("LD_LIBRARY_PATH", "")
        os.environ["LD_LIBRARY_PATH"] = libdir + (":" + prev if prev else "")

    # Set TESSDATA_PREFIX to bundled tessdata (if present)
    candidates = [
        os.path.join(base, "data", "tessdata"),
        os.path.join(base, "ocr", "tessdata"),
        os.path.join(base, "tessdata"),
    ]
    for p in candidates:
        if os.path.isdir(p):
            os.environ["TESSDATA_PREFIX"] = p
            break

    # Configure pytesseract if available
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = tesseract_exec
    except Exception:
        pass
