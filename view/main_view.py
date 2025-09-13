import flet as ft
from models.utils.capture_image import RectangleCoordinates
from pynput import mouse
import time

class MainView(ft.Control):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.presenter = None
        self.start_pos = None
        self.listener = None

        # UI Components
        self.capture_button = ft.ElevatedButton(text="Capture and Translate", on_click=self.start_capture)
        self.translated_text = ft.Text("Translated text will appear here.")
        self.original_text = ft.Text("Original text will appear here.")
        self.source_lang = ft.Text("Source language will appear here.")

    def build(self):
        return ft.Column([
            self.capture_button,
            ft.Divider(),
            ft.Text("Translation:"),
            self.translated_text,
            ft.Divider(),
            ft.Text("Original:"),
            self.original_text,
            ft.Divider(),
            ft.Text("Source Language:"),
            self.source_lang,
        ])

    def set_presenter(self, presenter):
        self.presenter = presenter

    def start_capture(self, e):
        self.page.window.visible = False
        self.page.update()
        # Give the window time to hide
        time.sleep(0.5)

        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.start_pos = (x, y)
        else:
            if self.start_pos:
                end_pos = (x, y)
                self.listener.stop()

                left = min(self.start_pos[0], end_pos[0])
                top = min(self.start_pos[1], end_pos[1])
                width = abs(self.start_pos[0] - end_pos[0])
                height = abs(self.start_pos[1] - end_pos[1])

                # Ensure width and height are not zero
                if width > 0 and height > 0:
                    rect = RectangleCoordinates(x=left, y=top, width=width, height=height)
                    if self.presenter:
                        self.presenter.capture_and_translate(rect)

                # Restore the window
                self.page.window.visible = True
                self.page.update()
                self.start_pos = None


    def update_translation_display(self, translated, original, source_lang):
        self.translated_text.value = translated if translated else "見つかりませんでした．"
        self.original_text.value = original
        self.source_lang.value = source_lang
        self.update()

    def show_error(self, message):
        self.page.open(ft.SnackBar(ft.Text(message), open=True))
        self.page.update()
