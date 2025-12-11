"""
アリ類群集・植生データ管理システム
メインエントリーポイント

Phase 1: データベース構築 + 親調査地・調査地の入力・閲覧機能
"""
import sys
import os
import configparser
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import Database
from views.main_window import MainWindow
from utils.sample_data import generate_sample_data


def load_config():
    """設定ファイルを読み込み"""
    config = configparser.ConfigParser()
    config_path = Path('config.ini')
    
    if config_path.exists():
        config.read(config_path, encoding='utf-8')
    else:
        print("⚠ config.ini が見つかりません。デフォルト設定を使用します。")
        config['Database'] = {
            'path': 'data/ant_database.db',
            'backup_dir': 'backups',
            'auto_backup': 'True'
        }
        config['SampleData'] = {
            'generate_on_first_run': 'True'
        }
    
    return config


def initialize_database(config):
    """データベースを初期化"""
    db_path = config.get('Database', 'path', fallback='data/ant_database.db')
    backup_dir = config.get('Database', 'backup_dir', fallback='backups')
    auto_backup = config.getboolean('Database', 'auto_backup', fallback=True)
    
    db = Database(db_path)
    
    # データベースファイルが存在するかチェック
    db_exists = Path(db_path).exists()
    
    if not db_exists:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("  🆕 初回起動を検出しました")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"  データベースを作成しています...")
        db.initialize_schema()
        print(f"  ✓ データベース作成完了: {db_path}")
        
        # サンプルデータの生成
        generate_sample = config.getboolean('SampleData', 
                                           'generate_on_first_run', 
                                           fallback=True)
        if generate_sample:
            print("\n  📊 サンプルデータを生成しています...")
            try:
                generate_sample_data(db)
                print("  ✓ サンプルデータ生成完了")
            except Exception as e:
                print(f"  ⚠ サンプルデータの生成に失敗しました: {e}")
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    else:
        # 既存DBのバックアップ
        if auto_backup:
            try:
                backup_path = db.backup(backup_dir)
                print(f"✓ バックアップ作成: {backup_path}")
            except Exception as e:
                print(f"⚠ バックアップに失敗しました: {e}")
    
    return db


def main():
    """メイン処理"""
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  アリ類群集・植生データ管理システム v1.0")
    print("  Phase 1: 基盤構築・データ入力機能")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    try:
        # 設定読み込み
        config = load_config()
        
        # データベース初期化
        db = initialize_database(config)
        
        # データベース接続を取得
        conn = db.connect()
        
        print("🚀 アプリケーションを起動しています...\n")
        
        # GUIアプリケーション起動
        app = MainWindow(conn)
        app.run()
        
        # 終了処理
        db.close()
        print("\n✓ アプリケーションを正常終了しました")
        
    except Exception as e:
        print(f"\n✗ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
