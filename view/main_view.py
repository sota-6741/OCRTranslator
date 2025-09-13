import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                            QLabel, QFrame, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont
from models.utils.capture_image import RectangleCoordinates
from view.screen_overlay import Overlay
import asyncio

class AsyncWorkerThread(QThread):
    """非同期タスクを実行するワーカースレッド"""
    finished = pyqtSignal(str, str, str)  # translated, original, source_lang
    error_occurred = pyqtSignal(str)

    def __init__(self, presenter, rect):
        super().__init__()
        self.presenter = presenter
        self.rect = rect

    def run(self):
        """非同期で翻訳処理を実行"""
        try:
            # asyncioのイベントループを作成して実行
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            translated_text, original_text, source_lang = loop.run_until_complete(
                self.presenter.capture_and_translate(self.rect)
            )

            self.finished.emit(translated_text, original_text, source_lang)

        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            loop.close()

class MainView(QWidget):
    def __init__(self):
        super().__init__()
        self.presenter = None
        self.overlay = None
        self.worker_thread = None

        self.init_ui()

    def init_ui(self):
        """UIコンポーネントの初期化"""
        self.setWindowTitle("OCR Translator")
        self.setGeometry(100, 100, 600, 400)

        # レイアウト設定
        layout = QVBoxLayout()

        # キャプチャボタン
        self.capture_button = QPushButton("Capture and Translate")
        self.capture_button.clicked.connect(self.start_capture)
        self.capture_button.setFont(QFont("Arial", 12))
        layout.addWidget(self.capture_button)

        # 区切り線
        layout.addWidget(self.create_divider())

        # 翻訳結果セクション
        translation_label = QLabel("Translation:")
        translation_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        translation_label.setStyleSheet("QLabel { color: #2c3e50; margin-bottom: 5px; }")
        layout.addWidget(translation_label)

        self.translated_text = QTextEdit(self)
        self.translated_text.setPlainText("Translated text will appear here.")
        self.translated_text.setReadOnly(True)
        self.translated_text.setMaximumHeight(120)
        self.translated_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.translated_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.translated_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.translated_text.setStyleSheet("""
            QTextEdit {
                background-color: #f0f0f0;
                color: #333333;
                padding: 10px;
                border: 1px solid #ccc;
                font-size: 12px;
                font-family: Arial;
            }
        """)
        layout.addWidget(self.translated_text)

        layout.addWidget(self.create_divider())

        # 元テキストセクション
        original_label = QLabel("Original:")
        original_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        original_label.setStyleSheet("QLabel { color: #2c3e50; margin-bottom: 5px; }")
        layout.addWidget(original_label)

        self.original_text = QTextEdit(self)
        self.original_text.setPlainText("Original text will appear here.")
        self.original_text.setReadOnly(True)
        self.original_text.setMaximumHeight(120)
        self.original_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.original_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.original_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.original_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                color: #333333;
                padding: 10px;
                border: 1px solid #ccc;
                font-size: 12px;
                font-family: Arial;
            }
        """)
        layout.addWidget(self.original_text)

        layout.addWidget(self.create_divider())

        # 元言語セクション
        source_lang_label = QLabel("Source Language:")
        source_lang_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        source_lang_label.setStyleSheet("QLabel { color: #2c3e50; margin-bottom: 5px; }")
        layout.addWidget(source_lang_label)

        self.source_lang = QLabel("Source language will appear here.")
        self.source_lang.setStyleSheet("QLabel { background-color: #e8f4fd; color: #2c3e50; padding: 10px; border: 1px solid #ccc; font-size: 12px; font-weight: bold; }")
        layout.addWidget(self.source_lang)

        # レイアウトを下に伸ばす
        layout.addStretch()

        self.setLayout(layout)

    def create_divider(self):
        """区切り線を作成"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.HLine)
        frame.setFrameShadow(QFrame.Shadow.Sunken)
        return frame

    def set_presenter(self, presenter):
        """プレゼンターを設定"""
        self.presenter = presenter

    def start_capture(self):
        """画面キャプチャを開始"""
        if not self.presenter:
            self.show_error("プレゼンターが設定されていません。")
            return

        try:
            # メインウィンドウを一時的に隠す
            self.hide()

            # 少し待ってからオーバーレイを表示
            QTimer.singleShot(100, self.show_overlay)

        except Exception as e:
            self.show_error(f"キャプチャの開始に失敗しました: {e}")
            self.show()  # エラー時はウィンドウを再表示

    def show_overlay(self):
        """オーバーレイを表示"""
        try:
            self.overlay = Overlay(self.on_area_selected)
            self.overlay.closed.connect(self.on_overlay_closed)
            self.overlay.show()
        except Exception as e:
            self.show_error(f"オーバーレイの表示に失敗しました: {e}")
            self.show()

    def on_area_selected(self, rect: RectangleCoordinates):
        """エリア選択完了時のコールバック"""
        try:
            if self.presenter:
                # ワーカースレッドで非同期処理を実行
                self.worker_thread = AsyncWorkerThread(self.presenter, rect)
                self.worker_thread.finished.connect(self.update_translation_display)
                self.worker_thread.error_occurred.connect(self.show_error)
                self.worker_thread.start()

                # UIを更新してキャプチャ中であることを表示
                self.capture_button.setText("Processing...")
                self.capture_button.setEnabled(False)

        except Exception as e:
            self.show_error(f"処理の開始に失敗しました: {e}")

    def on_overlay_closed(self):
        """オーバーレイが閉じられた時のコールバック"""
        print("MainView: Overlay closed, showing main window.")
        self.show()  # メインウィンドウを再表示

        # オーバーレイの参照をクリア
        if self.overlay:
            self.overlay.deleteLater()
            self.overlay = None

    def update_translation_display(self, translated, original, source_lang):
        """翻訳結果の表示を更新"""
        # メインスレッドで確実に実行するために遅延実行
        QTimer.singleShot(0, lambda: self._update_ui_safely(translated, original, source_lang))

    def _update_ui_safely(self, translated, original, source_lang):
        """UIを安全に更新"""
        try:
            self.translated_text.setPlainText(translated if translated else "No text found.")
            self.original_text.setPlainText(original)
            self.source_lang.setText(source_lang)

            # ボタンを元に戻す
            self.capture_button.setText("Capture and Translate")
            self.capture_button.setEnabled(True)

            # ワーカースレッドをクリーンアップ
            if self.worker_thread:
                self.worker_thread.deleteLater()
                self.worker_thread = None

        except Exception as e:
            self.show_error(f"表示の更新に失敗しました: {e}")

    def show_error(self, message):
        """エラーメッセージを表示"""
        try:
            # ボタンを元に戻す
            self.capture_button.setText("Capture and Translate")
            self.capture_button.setEnabled(True)

            # メインウィンドウを表示
            self.show()

            # エラーダイアログを表示
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("エラー")
            msg_box.setText(message)
            msg_box.exec()

            # ワーカースレッドをクリーンアップ
            if self.worker_thread:
                self.worker_thread.deleteLater()
                self.worker_thread = None

        except Exception as e:
            print(f"エラー表示に失敗しました: {e}")

    def closeEvent(self, event):
        """ウィンドウが閉じられる時の処理"""
        # ワーカースレッドが実行中の場合は終了を待つ
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

        # オーバーレイが開いている場合は閉じる
        if self.overlay:
            self.overlay.close()

        event.accept()
