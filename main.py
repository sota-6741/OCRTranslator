import flet as ft
from models.model_facade import ModelFacade
from presenter.main_presenter import MainPresenter
from view.main_view import MainView

def main(page: ft.Page):
    page.title = "OCR Translator"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # MVP components
    model = ModelFacade()
    view = MainView(page)
    presenter = MainPresenter(model, view)
    view.set_presenter(presenter)

    page.add(view)

if __name__ == "__main__":
    ft.app(target=main)
