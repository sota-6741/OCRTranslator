# OCRTranslator

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/github/license/sota-6741/OCRTranslator)

---

## 📖 プロジェクト概要

**OCRTranslator** は、画像からテキストを抽出し、翻訳までをワンストップで行うデスクトップアプリケーションです。Tesseract OCRと翻訳APIを組み合わせ、スクリーンショットや画像ファイルから簡単にテキストを取得・翻訳できます。

---

## このプロジェクトの有用性

- **画像からのテキスト抽出**: スクリーンショットや画像ファイルから高精度で文字認識
- **ワンクリック翻訳**: 認識したテキストを即座に翻訳
- **クロスプラットフォーム**: Windows/Linux対応


---

## 利用開始方法

### 1. クローン & セットアップ

```bash
git clone https://github.com/sota-6741/OCRTranslator.git
cd OCRTranslator
python -m venv .venv
source .venv/bin/activate  # Windowsは .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Tesseractバイナリの配置
- `tesseract_bin/` ディレクトリにOSごとのバイナリを同梱済み
- 追加言語データは `tesseract_bin/<os>/tessdata/` へ配置

### 3. アプリ起動

```bash
python3   main.py
```

### 4. 使い方
- アプリを起動し、画面の指示に従って画像を選択またはスクリーンショットを取得
- 認識・翻訳結果が画面に表示されます

---

## サポート

- **FAQ・トラブルシューティング**: [`ocr_translator.log`](ocr_translator.log) を参照
- **Tesseractの追加言語**: [公式リポジトリ](https://github.com/tesseract-ocr/tessdata) から取得し `tessdata/` へ配置
- **Issue報告・質問**: [GitHub Issues](https://github.com/sota-6741/OCRTranslator/issues)

---

## メンテナンス

- **メンテナ**: [sota-6741](https://github.com/sota-6741)
---

## ディレクトリ構成

```
OCRTranslator/
├── main.py
├── requirements.txt
├── tesseract_bin/
├── models/
├── ocr/
├── translator/
├── utils/
├── presenter/
├── view/
└── ...
```

---


## 変更履歴

### v1.1.1 (最新)
- Linux、Windows用バイナリを含むリリース
- バグ修正

### v1.1.0
- 修正したLinux版バイナリとソースコードを公開

### v1.0.0
- 初回リリース（ローカルビルド）
- 作成日時: 2025-09-15 01:39:04

---

## サポート情報

- **開発環境**: Visual Studio Code
- **連絡先**: [GitHub Issues](https://github.com/sota-6741/OCRTranslator/issues)

---
