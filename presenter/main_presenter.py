from models.model_facade import ModelFacade
from models.utils.capture_image import RectangleCoordinates

class MainPresenter:
    def __init__(self, model: ModelFacade, view):
        self.model = model
        self.view = view

    def capture_and_translate(self, rect: RectangleCoordinates):
        """
        指定された領域をキャプチャし、翻訳して結果をビューに表示します。
        """
        try:
            translated_text, original_text, source_lang = self.model.translate_image_from_screen(rect)
            self.view.update_translation_display(translated_text, original_text, source_lang)
        except Exception as e:
            self.view.show_error(f"エラーが発生しました: {e}")
