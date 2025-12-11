"""
データベース接続・初期化モジュール
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path
import shutil


class Database:
    """データベース管理クラス"""
    
    def __init__(self, db_path='data/ant_database.db'):
        """
        初期化
        
        Args:
            db_path: データベースファイルのパス
        """
        self.db_path = db_path
        self._ensure_directory()
        self.conn = None
        
    def _ensure_directory(self):
        """データベースディレクトリの存在確認・作成"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def connect(self):
        """データベース接続"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 列名でアクセス可能に
        # 外部キー制約を有効化
        self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn
    
    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def initialize_schema(self):
        """データベーススキーマの初期化"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # 親調査地テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parent_sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
                    longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
                    altitude REAL,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL
                )
            """)
            
            # 調査地テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_sites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_site_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
                    longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
                    altitude REAL,
                    area REAL CHECK(area > 0),
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL,
                    FOREIGN KEY (parent_site_id) REFERENCES parent_sites(id) ON DELETE RESTRICT,
                    UNIQUE(parent_site_id, name)
                )
            """)
            
            # 調査イベントテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS survey_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    survey_site_id INTEGER NOT NULL,
                    survey_date TIMESTAMP NOT NULL,
                    surveyor_name TEXT,
                    weather TEXT CHECK(weather IN ('晴れ', '曇り', '雨', '雪', NULL)),
                    temperature REAL,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL,
                    FOREIGN KEY (survey_site_id) REFERENCES survey_sites(id) ON DELETE CASCADE
                )
            """)
            
            # 植生データテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vegetation_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    survey_event_id INTEGER NOT NULL,
                    dominant_tree TEXT,
                    dominant_sasa TEXT,
                    dominant_herb TEXT,
                    litter_type TEXT,
                    basal_area REAL CHECK(basal_area >= 0),
                    avg_tree_height REAL CHECK(avg_tree_height >= 0),
                    avg_herb_height REAL CHECK(avg_herb_height >= 0),
                    soil_temperature REAL,
                    canopy_coverage REAL CHECK(canopy_coverage BETWEEN 0 AND 100),
                    sasa_coverage REAL CHECK(sasa_coverage BETWEEN 0 AND 100),
                    herb_coverage REAL CHECK(herb_coverage BETWEEN 0 AND 100),
                    litter_coverage REAL CHECK(litter_coverage BETWEEN 0 AND 100),
                    light_condition INTEGER CHECK(light_condition BETWEEN 1 AND 5),
                    soil_moisture INTEGER CHECK(soil_moisture BETWEEN 1 AND 5),
                    vegetation_complexity INTEGER CHECK(vegetation_complexity BETWEEN 1 AND 5),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL,
                    FOREIGN KEY (survey_event_id) REFERENCES survey_events(id) ON DELETE CASCADE
                )
            """)
            
            # 種名マスタテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS species_master (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    genus TEXT,
                    subfamily TEXT,
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL
                )
            """)
            
            # アリ類出現記録テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ant_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    survey_event_id INTEGER NOT NULL,
                    species_id INTEGER NOT NULL,
                    count INTEGER NOT NULL CHECK(count >= 0),
                    remarks TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL,
                    FOREIGN KEY (survey_event_id) REFERENCES survey_events(id) ON DELETE CASCADE,
                    FOREIGN KEY (species_id) REFERENCES species_master(id) ON DELETE RESTRICT,
                    UNIQUE(survey_event_id, species_id)
                )
            """)
            
            # 環境タグマスタテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS environment_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 親調査地-環境タグ中間テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS parent_site_environments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_site_id INTEGER NOT NULL,
                    environment_tag_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_site_id) REFERENCES parent_sites(id) ON DELETE CASCADE,
                    FOREIGN KEY (environment_tag_id) REFERENCES environment_tags(id) ON DELETE RESTRICT,
                    UNIQUE(parent_site_id, environment_tag_id)
                )
            """)
            
            # バージョン管理テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS app_version (
                    version TEXT PRIMARY KEY,
                    released_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # インデックス作成
            self._create_indexes(cursor)
            
            # 初期データ投入
            self._insert_initial_data(cursor)
            
            conn.commit()
            print("✓ データベーススキーマの初期化が完了しました")
            
        except sqlite3.Error as e:
            conn.rollback()
            print(f"✗ データベース初期化エラー: {e}")
            raise
        finally:
            self.close()
    
    def _create_indexes(self, cursor):
        """インデックスの作成"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_parent_sites_name ON parent_sites(name)",
            "CREATE INDEX IF NOT EXISTS idx_parent_sites_deleted ON parent_sites(deleted_at)",
            "CREATE INDEX IF NOT EXISTS idx_survey_sites_parent ON survey_sites(parent_site_id)",
            "CREATE INDEX IF NOT EXISTS idx_survey_sites_name ON survey_sites(name)",
            "CREATE INDEX IF NOT EXISTS idx_survey_sites_deleted ON survey_sites(deleted_at)",
            "CREATE INDEX IF NOT EXISTS idx_survey_events_site ON survey_events(survey_site_id)",
            "CREATE INDEX IF NOT EXISTS idx_survey_events_date ON survey_events(survey_date)",
            "CREATE INDEX IF NOT EXISTS idx_vegetation_event ON vegetation_data(survey_event_id)",
            "CREATE INDEX IF NOT EXISTS idx_species_name ON species_master(name)",
            "CREATE INDEX IF NOT EXISTS idx_ant_records_event ON ant_records(survey_event_id)",
            "CREATE INDEX IF NOT EXISTS idx_ant_records_species ON ant_records(species_id)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def _insert_initial_data(self, cursor):
        """初期マスタデータの投入"""
        # 環境タグの初期データ
        environment_tags = [
            ('落葉広葉樹林', 'ブナ、ミズナラ等が優占する森林'),
            ('常緑広葉樹林', 'スダジイ、アラカシ等が優占する森林'),
            ('針葉樹林', 'スギ、ヒノキ、カラマツ等の植林地'),
            ('混交林', '広葉樹と針葉樹が混在する森林'),
            ('草地', '草本が優占する開放地'),
            ('ササ原', 'ササ類が密生する環境'),
            ('農耕地', '水田、畑地、果樹園等'),
            ('市街地', '住宅地、公園等の人為的環境'),
            ('河川敷', '河川沿いの礫地や草地'),
        ]
        
        cursor.execute("SELECT COUNT(*) FROM environment_tags")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO environment_tags (name, description) VALUES (?, ?)",
                environment_tags
            )
        
        # バージョン情報
        cursor.execute("SELECT COUNT(*) FROM app_version")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO app_version (version) VALUES (?)",
                ('1.0.0',)
            )
    
    def backup(self, backup_dir='backups'):
        """
        データベースのバックアップ
        
        Args:
            backup_dir: バックアップディレクトリ
            
        Returns:
            str: バックアップファイルパス
        """
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"ant_database_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        try:
            shutil.copy2(self.db_path, backup_path)
            print(f"✓ バックアップ作成: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"✗ バックアップエラー: {e}")
            raise
    
    def get_connection(self):
        """接続オブジェクトを取得（コンテキストマネージャー用）"""
        if not self.conn:
            self.connect()
        return self.conn


if __name__ == "__main__":
    # テスト実行
    db = Database()
    db.initialize_schema()
    db.backup()
