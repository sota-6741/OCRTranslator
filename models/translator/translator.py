from typing import Optional, List, Protocol
from dataclasses import dataclass
from googletrans import Translator
from langdetect import detect

class TranslationError(Exception):
    """翻訳例外クラス"""

@dataclass
class TranslationConfig:
    """翻訳設定クラス"""
    source_language: str = "auto"
    target_language: str = "ja"

class ITranslator(Protocol):
    """翻訳エンジン インターフェース"""

    @abstractmethod
    def translate(self) -> str:
        """テキストの翻訳"""

    @property
    @abstractmethod
    def translated_text(self) -> str:
        """翻訳結果をプロパティで取得"""

    @property
    @abstractmethod
    def translator_engine_name(self) ->str:
        """翻訳エンジン名をプロパティで取得"""

    @property
    @abstractmethod
    def source_language(self) -> str:
        """検出された元言語を取得"""

class GoogleTranslator(ITranslator):
    """Translatorライブラリの実装"""
    def __init__(self, text: str, config: Optional[TranslationConfig] = None):
        self.input_text = text
        self.config = config or TranslationConfig()
        self._translated_text = ""
        self._detected_language = ""

    @property
    def translated_text(self) -> str:
        return self._translated_text

    @property
    def translator_engine_name(self) -> str:
        return "Google translator"

    @property
    def source_language(self) -> str:
        return self._detected_language

    def translate(self) -> str:
        """テキストを翻訳する"""
        try:
            # 空文字列や空白のみの場合は空文字列を返す
            if not self.input_text or not self.input_text.strip():
                return ""

            translator = Translator()

            # 言語検出
            if self.config.source_language == "auto":
                self._detected_language = detect(self.input_text)
            else:
                self._detected_language = self.config.source_language

            result = translator.translate(
                self.input_text,
                src=self._detected_language,
                dest=self.config.target_language
            )

            return result.text

        except Exception as e:
            raise TranslationError(f"google翻訳エラー: {e}")

class TranslatorFactory:
    """翻訳エンジンのファクトリークラス"""
    _translator_engines = {
        "Google translator": GoogleTranslator,
    }

    @staticmethod
    def create_translator(engine_type: str, text: str, config: Optional[TranslationConfig] = None) -> ITranslator:
        """指定されたエンジンタイプで翻訳インスタンスを作成"""
        if engine_type not in TranslatorFactory._translator_engines:
            raise ValueError(f"サポートされていないエンジンタイプです: {engine_type}")

        engine_class = TranslatorFactory._translator_engines[engine_type]
        return engine_class(text=text, config=config)

    @staticmethod
    def get_available_engines() -> List[str]:
        """利用可能なエンジン一覧を取得"""
        return list(TranslatorFactory._translator_engines.keys())

class TranslationEngine:
    """翻訳エンジンのコンテキストクラス"""

    def __init__(self, strategy: ITranslator):
        self._strategy = strategy

    def set_strategy(self, strategy: ITranslator):
        """翻訳エンジンを切り替える"""
        self._strategy = strategy

    def translated_text(self) -> str:
        """現在のエンジンで翻訳結果を取得"""
        return self._strategy.translated_text

    def get_engine_info(self) -> dict:
        """エンジン情報を取得"""
        return {
            "engine": self._strategy.translator_engine_name,
            "source_language": self._strategy.source_language,
            "translated_text": self._strategy.translated_text
        }
