from flet import app, Page, MainAxisAlignment
from models.model_facade import ModelFacade
from presenter.main_presenter import MainPresenter
from view.main_view import MainView

def main(page: Page):
    page.title = "OCR Translator"
    page.vertical_alignment = MainAxisAlignment.CENTER

    # MVP components
    model = ModelFacade()
    view = MainView()
    presenter = MainPresenter(model, view)
    view.set_presenter(presenter)

    page.add(view)

if __name__ == "__main__":
    app(target=main)