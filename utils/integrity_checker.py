"""
データ整合性チェック機能
"""
from typing import List, Dict, Any
import pandas as pd


class IntegrityChecker:
    """データ整合性チェッククラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続
        """
        self.conn = db_connection
        self.issues = []
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        全てのチェックを実行
        
        Returns:
            Dict: チェック結果のサマリー
        """
        self.issues = []
        
        # 各種チェックを実行
        self.check_orphaned_records()
        self.check_duplicate_data()
        self.check_invalid_values()
        self.check_missing_data()
        self.check_coordinate_validity()
        
        return {
            'total_issues': len(self.issues),
            'issues': self.issues,
            'status': 'OK' if len(self.issues) == 0 else 'WARNINGS'
        }
    
    def check_orphaned_records(self):
        """孤立レコードをチェック"""
        # 親調査地のない調査地
        sql = """
            SELECT ss.id, ss.name
            FROM survey_sites ss
            LEFT JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE ps.id IS NULL AND ss.deleted_at IS NULL
        """
        orphaned_sites = pd.read_sql_query(sql, self.conn)
        
        if not orphaned_sites.empty:
            for _, row in orphaned_sites.iterrows():
                self.issues.append({
                    'type': 'orphaned_record',
                    'severity': 'high',
                    'table': 'survey_sites',
                    'record_id': row['id'],
                    'message': f"調査地「{row['name']}」の親調査地が存在しません",
                    'fixable': False
                })
        
        # 調査地のない調査イベント
        sql = """
            SELECT se.id, se.survey_date
            FROM survey_events se
            LEFT JOIN survey_sites ss ON se.survey_site_id = ss.id
            WHERE ss.id IS NULL AND se.deleted_at IS NULL
        """
        orphaned_events = pd.read_sql_query(sql, self.conn)
        
        if not orphaned_events.empty:
            for _, row in orphaned_events.iterrows():
                self.issues.append({
                    'type': 'orphaned_record',
                    'severity': 'high',
                    'table': 'survey_events',
                    'record_id': row['id'],
                    'message': f"調査イベント（{row['survey_date']}）の調査地が存在しません",
                    'fixable': False
                })
        
        # 種マスタにない種のアリ記録
        sql = """
            SELECT ar.id, ar.species_id
            FROM ant_records ar
            LEFT JOIN species_master sm ON ar.species_id = sm.id
            WHERE sm.id IS NULL AND ar.deleted_at IS NULL
        """
        orphaned_records = pd.read_sql_query(sql, self.conn)
        
        if not orphaned_records.empty:
            for _, row in orphaned_records.iterrows():
                self.issues.append({
                    'type': 'orphaned_record',
                    'severity': 'high',
                    'table': 'ant_records',
                    'record_id': row['id'],
                    'message': f"アリ記録（ID:{row['id']}）の種が種マスタに存在しません",
                    'fixable': False
                })
    
    def check_duplicate_data(self):
        """重複データをチェック"""
        # 同一名の親調査地
        sql = """
            SELECT name, COUNT(*) as count
            FROM parent_sites
            WHERE deleted_at IS NULL
            GROUP BY name
            HAVING count > 1
        """
        duplicates = pd.read_sql_query(sql, self.conn)
        
        if not duplicates.empty:
            for _, row in duplicates.iterrows():
                self.issues.append({
                    'type': 'duplicate',
                    'severity': 'medium',
                    'table': 'parent_sites',
                    'message': f"親調査地名「{row['name']}」が重複しています（{row['count']}件）",
                    'fixable': False
                })
        
        # 同一調査イベント・同一種の重複記録
        sql = """
            SELECT survey_event_id, species_id, COUNT(*) as count
            FROM ant_records
            WHERE deleted_at IS NULL
            GROUP BY survey_event_id, species_id
            HAVING count > 1
        """
        duplicate_records = pd.read_sql_query(sql, self.conn)
        
        if not duplicate_records.empty:
            for _, row in duplicate_records.iterrows():
                self.issues.append({
                    'type': 'duplicate',
                    'severity': 'high',
                    'table': 'ant_records',
                    'message': f"調査イベント{row['survey_event_id']}・種{row['species_id']}の記録が重複しています（{row['count']}件）",
                    'fixable': True
                })
    
    def check_invalid_values(self):
        """不正な値をチェック"""
        # 緯度の範囲チェック（親調査地）
        sql = """
            SELECT id, name, latitude
            FROM parent_sites
            WHERE (latitude < -90 OR latitude > 90) AND deleted_at IS NULL
        """
        invalid_lat = pd.read_sql_query(sql, self.conn)
        
        if not invalid_lat.empty:
            for _, row in invalid_lat.iterrows():
                self.issues.append({
                    'type': 'invalid_value',
                    'severity': 'high',
                    'table': 'parent_sites',
                    'record_id': row['id'],
                    'message': f"親調査地「{row['name']}」の緯度（{row['latitude']}）が範囲外です",
                    'fixable': False
                })
        
        # 経度の範囲チェック（親調査地）
        sql = """
            SELECT id, name, longitude
            FROM parent_sites
            WHERE (longitude < -180 OR longitude > 180) AND deleted_at IS NULL
        """
        invalid_lon = pd.read_sql_query(sql, self.conn)
        
        if not invalid_lon.empty:
            for _, row in invalid_lon.iterrows():
                self.issues.append({
                    'type': 'invalid_value',
                    'severity': 'high',
                    'table': 'parent_sites',
                    'record_id': row['id'],
                    'message': f"親調査地「{row['name']}」の経度（{row['longitude']}）が範囲外です",
                    'fixable': False
                })
        
        # 負の個体数
        sql = """
            SELECT ar.id, sm.name, ar.count
            FROM ant_records ar
            JOIN species_master sm ON ar.species_id = sm.id
            WHERE ar.count < 0 AND ar.deleted_at IS NULL
        """
        negative_counts = pd.read_sql_query(sql, self.conn)
        
        if not negative_counts.empty:
            for _, row in negative_counts.iterrows():
                self.issues.append({
                    'type': 'invalid_value',
                    'severity': 'high',
                    'table': 'ant_records',
                    'record_id': row['id'],
                    'message': f"種「{row['name']}」の個体数が負の値（{row['count']}）です",
                    'fixable': True
                })
        
        # 被度の範囲チェック（0-100%）
        sql = """
            SELECT id, canopy_coverage, sasa_coverage, herb_coverage, litter_coverage
            FROM vegetation_data
            WHERE deleted_at IS NULL
            AND (
                canopy_coverage < 0 OR canopy_coverage > 100 OR
                sasa_coverage < 0 OR sasa_coverage > 100 OR
                herb_coverage < 0 OR herb_coverage > 100 OR
                litter_coverage < 0 OR litter_coverage > 100
            )
        """
        invalid_coverage = pd.read_sql_query(sql, self.conn)
        
        if not invalid_coverage.empty:
            for _, row in invalid_coverage.iterrows():
                self.issues.append({
                    'type': 'invalid_value',
                    'severity': 'medium',
                    'table': 'vegetation_data',
                    'record_id': row['id'],
                    'message': f"植生データ（ID:{row['id']}）の被度が範囲外（0-100%）です",
                    'fixable': True
                })
    
    def check_missing_data(self):
        """必須データの欠落をチェック"""
        # 植生データのない調査イベント
        sql = """
            SELECT se.id, se.survey_date, ss.name
            FROM survey_events se
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            LEFT JOIN vegetation_data vd ON se.id = vd.survey_event_id
            WHERE vd.id IS NULL AND se.deleted_at IS NULL
        """
        events_without_veg = pd.read_sql_query(sql, self.conn)
        
        if not events_without_veg.empty:
            for _, row in events_without_veg.iterrows():
                self.issues.append({
                    'type': 'missing_data',
                    'severity': 'low',
                    'table': 'vegetation_data',
                    'message': f"調査イベント（{row['survey_date']}, {row['name']}）に植生データがありません",
                    'fixable': False
                })
        
        # アリ記録のない調査イベント
        sql = """
            SELECT se.id, se.survey_date, ss.name
            FROM survey_events se
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            LEFT JOIN ant_records ar ON se.id = ar.survey_event_id
            WHERE ar.id IS NULL AND se.deleted_at IS NULL
        """
        events_without_ants = pd.read_sql_query(sql, self.conn)
        
        if not events_without_ants.empty:
            for _, row in events_without_ants.iterrows():
                self.issues.append({
                    'type': 'missing_data',
                    'severity': 'low',
                    'table': 'ant_records',
                    'message': f"調査イベント（{row['survey_date']}, {row['name']}）にアリ記録がありません",
                    'fixable': False
                })
    
    def check_coordinate_validity(self):
        """座標の妥当性をチェック（日本国内かどうか）"""
        # 日本のおおよその範囲
        # 緯度: 24-46度、経度: 123-146度
        
        sql = """
            SELECT id, name, latitude, longitude
            FROM parent_sites
            WHERE deleted_at IS NULL
            AND (
                latitude < 24 OR latitude > 46 OR
                longitude < 123 OR longitude > 146
            )
        """
        outside_japan = pd.read_sql_query(sql, self.conn)
        
        if not outside_japan.empty:
            for _, row in outside_japan.iterrows():
                self.issues.append({
                    'type': 'suspicious_value',
                    'severity': 'low',
                    'table': 'parent_sites',
                    'record_id': row['id'],
                    'message': f"親調査地「{row['name']}」の座標（{row['latitude']}, {row['longitude']}）が日本国外の可能性があります",
                    'fixable': False
                })
    
    def fix_issue(self, issue: Dict[str, Any]) -> bool:
        """
        修正可能な問題を修正
        
        Args:
            issue: 問題の情報
            
        Returns:
            bool: 修正成功時True
        """
        if not issue.get('fixable', False):
            return False
        
        cursor = self.conn.cursor()
        
        try:
            if issue['type'] == 'duplicate' and issue['table'] == 'ant_records':
                # 重複レコードを削除（最初の1件を残す）
                sql = """
                    DELETE FROM ant_records
                    WHERE id NOT IN (
                        SELECT MIN(id)
                        FROM ant_records
                        WHERE survey_event_id = ? AND species_id = ?
                        GROUP BY survey_event_id, species_id
                    )
                """
                # この実装は簡易版です
                pass
            
            elif issue['type'] == 'invalid_value':
                if issue['table'] == 'ant_records' and 'negative' in issue['message']:
                    # 負の個体数を0に修正
                    cursor.execute("""
                        UPDATE ant_records SET count = 0 WHERE id = ?
                    """, (issue['record_id'],))
                    self.conn.commit()
                    return True
            
            return False
            
        except Exception as e:
            self.conn.rollback()
            print(f"修正エラー: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, int]:
        """
        データベースの統計情報を取得
        
        Returns:
            Dict: 統計情報
        """
        cursor = self.conn.cursor()
        
        stats = {}
        
        tables = [
            'parent_sites', 'survey_sites', 'survey_events',
            'vegetation_data', 'species_master', 'ant_records'
        ]
        
        for table in tables:
            # アクティブなレコード数
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table} WHERE deleted_at IS NULL
            """)
            stats[f'{table}_active'] = cursor.fetchone()[0]
            
            # 削除済みレコード数
            cursor.execute(f"""
                SELECT COUNT(*) FROM {table} WHERE deleted_at IS NOT NULL
            """)
            stats[f'{table}_deleted'] = cursor.fetchone()[0]
        
        return stats