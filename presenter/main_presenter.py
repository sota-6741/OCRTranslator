from models.model_facade import ModelFacade
from models.utils.capture_image import RectangleCoordinates

class MainPresenter:
    def __init__(self, model: ModelFacade, view=None):
        self.model = model
        self.view = view

    async def capture_and_translate(self, rect: RectangleCoordinates):
        """
        指定された領域をキャプチャし、翻訳して結果を返します。
        PyQt6版では戻り値を返し、Flet版では直接ビューを更新します。
        """
        try:
            translated_text, original_text, source_lang = await self.model.translate_image_from_screen(rect)

            # ビューが設定されている場合は直接更新（Flet版との互換性）
            if self.view and hasattr(self.view, 'update_translation_display'):
                self.view.update_translation_display(translated_text, original_text, source_lang)

            # 戻り値も返す（PyQt6版で使用）
            return translated_text, original_text, source_lang

        except Exception as e:
            error_msg = f"エラーが発生しました: {e}"

            # ビューが設定されている場合はエラーを表示
            if self.view and hasattr(self.view, 'show_error'):
                self.view.show_error(error_msg)

            # エラーを再発生させる（PyQt6版でキャッチするため）
            raise
