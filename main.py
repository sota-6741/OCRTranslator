import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox

# プロジェクトのモジュールをインポート
from models.model_facade import ModelFacade
from presenter.main_presenter import MainPresenter
from view.main_view import MainView


def setup_logging():
    """ログ設定を初期化"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ocr_translator.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """メインアプリケーション"""
    # ログ設定
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # PyQt6アプリケーション作成
        app = QApplication(sys.argv)

        # Qt High DPI設定（高解像度ディスプレイ対応）
        # PyQt6では自動的に高DPIスケーリングが有効になります
        app.setApplicationName("OCR Translator")
        app.setApplicationVersion("1.0.0")

        logger.info("OCR Translator アプリケーションを開始しています...")

        # MVPアーキテクチャの初期化
        model = ModelFacade()
        view = MainView()
        presenter = MainPresenter(model, view)

        # ビューにプレゼンターを設定
        view.set_presenter(presenter)

        # メインウィンドウを表示
        view.show()

        logger.info("アプリケーションが正常に起動しました")

        # イベントループ開始
        exit_code = app.exec()

        logger.info(f"アプリケーションが終了しました (終了コード: {exit_code})")
        return exit_code

    except Exception as e:
        logger.error(f"アプリケーションの起動に失敗しました: {e}", exc_info=True)

        try:
            from PyQt6.QtWidgets import QMessageBox
            app = QApplication.instance() or QApplication(sys.argv)

            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("起動エラー")
            msg_box.setText(f"アプリケーションの起動に失敗しました:\n{e}")
            msg_box.exec()
        except Exception as dialog_error:
            print(f"エラーダイアログの表示にも失敗しました: {dialog_error}")

        return 1


if __name__ == "__main__":
    sys.exit(main())