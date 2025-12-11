# アリ類群集・植生データ管理システム - セットアップガイド

## 📁 プロジェクト構造

以下のフォルダ・ファイル構造を作成してください：

```
ant_research_system/
├── main.py
├── requirements.txt
├── config.ini
├── README.md
│
├── models/
│   ├── __init__.py
│   ├── database.py
│   ├── parent_site.py
│   ├── survey_site.py
│   ├── survey_event.py
│   ├── vegetation.py
│   ├── ant_record.py
│   └── species.py
│
├── views/
│   ├── __init__.py
│   ├── main_window.py
│   ├── input_tab.py
│   ├── view_tab.py
│   ├── analysis_tab.py
│   ├── map_tab.py
│   └── settings_tab.py
│
├── controllers/
│   ├── __init__.py
│   ├── site_controller.py
│   ├── data_controller.py
│   ├── export_controller.py
│   ├── analysis_controller.py
│   └── map_controller.py
│
├── utils/
│   ├── __init__.py
│   ├── validators.py
│   ├── logger.py
│   ├── backup.py
│   └── geo_utils.py
│
├── data/
│   └── .gitkeep
│
├── backups/
│   └── .gitkeep
│
├── logs/
│   └── .gitkeep
│
├── exports/
│   └── .gitkeep
│
├── templates/
│   └── .gitkeep
│
└── tests/
    ├── __init__.py
    └── test_models.py
```

## 🚀 セットアップ手順

### 1. フォルダ作成（Windows PowerShell / Command Prompt）

```powershell
# プロジェクトルートディレクトリ作成
mkdir ant_research_system
cd ant_research_system

# サブディレクトリ作成
mkdir models, views, controllers, utils, data, backups, logs, exports, templates, tests

# __init__.py ファイル作成
New-Item -ItemType File -Path models/__init__.py
New-Item -ItemType File -Path views/__init__.py
New-Item -ItemType File -Path controllers/__init__.py
New-Item -ItemType File -Path utils/__init__.py
New-Item -ItemType File -Path tests/__init__.py

# .gitkeep ファイル作成（空ディレクトリをGit管理下に置くため）
New-Item -ItemType File -Path data/.gitkeep
New-Item -ItemType File -Path backups/.gitkeep
New-Item -ItemType File -Path logs/.gitkeep
New-Item -ItemType File -Path exports/.gitkeep
New-Item -ItemType File -Path templates/.gitkeep
```

### 2. Python仮想環境の作成

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境のアクティベート（Windows）
venv\Scripts\activate

# 仮想環境のアクティベート（macOS/Linux）
source venv/bin/activate
```

### 3. requirements.txt の配置とインストール

プロジェクトルートに `requirements.txt` を配置後：

```bash
pip install -r requirements.txt
```

## 📋 次のステップ

1. ✅ フォルダ構造作成完了
2. ✅ 仮想環境セットアップ完了
3. ✅ パッケージインストール完了

→ **次は各ファイルのコード実装に進みます！**

## 🔧 トラブルシューティング

### tkinterが見つからない場合（Windows）
```bash
# Python再インストール時に「tcl/tk and IDLE」にチェックを入れる
```

### pipが古い場合
```bash
python -m pip install --upgrade pip
```

### 仮想環境から抜ける
```bash
deactivate
```
