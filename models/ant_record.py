"""
アリ類出現記録モデル
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


class AntRecord:
    """アリ類出現記録モデルクラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続オブジェクト
        """
        self.conn = db_connection
    
    def create(self, survey_event_id: int, species_id: int, count: int,
               remarks: Optional[str] = None) -> int:
        """
        アリ類出現記録を新規作成
        
        Args:
            survey_event_id: 調査イベントID
            species_id: 種ID
            count: 個体数
            remarks: 備考
            
        Returns:
            int: 作成されたレコードのID
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO ant_records (survey_event_id, species_id, count, remarks)
                VALUES (?, ?, ?, ?)
            """, (survey_event_id, species_id, count, remarks))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("この調査イベントには既に同じ種の記録が存在します")
            elif "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("指定された調査イベントまたは種が存在しません")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("個体数は0以上の整数で入力してください")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """
        IDで出現記録を取得
        
        Args:
            record_id: 記録ID
            
        Returns:
            Dict: 出現記録データ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                ar.*,
                sm.name as species_name,
                se.survey_date,
                ss.name as site_name
            FROM ant_records ar
            JOIN species_master sm ON ar.species_id = sm.id
            JOIN survey_events se ON ar.survey_event_id = se.id
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            WHERE ar.id = ? AND ar.deleted_at IS NULL
        """, (record_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_by_event(self, survey_event_id: int) -> List[Dict[str, Any]]:
        """
        調査イベントに紐付く出現記録を取得
        
        Args:
            survey_event_id: 調査イベントID
            
        Returns:
            List[Dict]: 出現記録のリスト
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                ar.*,
                sm.name as species_name,
                sm.genus,
                sm.subfamily
            FROM ant_records ar
            JOIN species_master sm ON ar.species_id = sm.id
            WHERE ar.survey_event_id = ? AND ar.deleted_at IS NULL
            ORDER BY sm.name
        """, (survey_event_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_species(self, species_id: int) -> List[Dict[str, Any]]:
        """
        種ごとの出現記録を取得
        
        Args:
            species_id: 種ID
            
        Returns:
            List[Dict]: 出現記録のリスト
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                ar.*,
                se.survey_date,
                ss.name as site_name,
                ps.name as parent_site_name
            FROM ant_records ar
            JOIN survey_events se ON ar.survey_event_id = se.id
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE ar.species_id = ? AND ar.deleted_at IS NULL
            ORDER BY se.survey_date DESC
        """, (species_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all(self, survey_site_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        出現記録を取得
        
        Args:
            survey_site_id: 調査地IDで絞り込み（Noneの場合は全て）
            
        Returns:
            List[Dict]: 出現記録のリスト
        """
        cursor = self.conn.cursor()
        
        sql = """
            SELECT 
                ar.*,
                sm.name as species_name,
                se.survey_date,
                ss.name as site_name,
                ps.name as parent_site_name
            FROM ant_records ar
            JOIN species_master sm ON ar.species_id = sm.id
            JOIN survey_events se ON ar.survey_event_id = se.id
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE ar.deleted_at IS NULL
        """
        
        params = []
        
        if survey_site_id is not None:
            sql += " AND se.survey_site_id = ?"
            params.append(survey_site_id)
        
        sql += " ORDER BY se.survey_date DESC, sm.name"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, record_id: int,
               species_id: Optional[int] = None,
               count: Optional[int] = None,
               remarks: Optional[str] = None) -> bool:
        """
        出現記録を更新
        
        Args:
            record_id: 記録ID
            species_id: 種ID
            count: 個体数
            remarks: 備考
            
        Returns:
            bool: 更新成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            update_fields = []
            values = []
            
            if species_id is not None:
                update_fields.append("species_id = ?")
                values.append(species_id)
            if count is not None:
                update_fields.append("count = ?")
                values.append(count)
            if remarks is not None:
                update_fields.append("remarks = ?")
                values.append(remarks)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                values.append(datetime.now())
                values.append(record_id)
                
                sql = f"""
                    UPDATE ant_records 
                    SET {', '.join(update_fields)}
                    WHERE id = ? AND deleted_at IS NULL
                """
                cursor.execute(sql, values)
                
                self.conn.commit()
                return cursor.rowcount > 0
            
            return False
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise ValueError("この調査イベントには既に同じ種の記録が存在します")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("個体数は0以上の整数で入力してください")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def delete(self, record_id: int, logical: bool = True) -> bool:
        """
        出現記録を削除
        
        Args:
            record_id: 記録ID
            logical: 論理削除（True）か物理削除（False）か
            
        Returns:
            bool: 削除成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            if logical:
                cursor.execute("""
                    UPDATE ant_records 
                    SET deleted_at = ? 
                    WHERE id = ? AND deleted_at IS NULL
                """, (datetime.now(), record_id))
            else:
                cursor.execute("""
                    DELETE FROM ant_records WHERE id = ?
                """, (record_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_species_frequency(self) -> List[Dict[str, Any]]:
        """
        種ごとの出現頻度を取得
        
        Returns:
            List[Dict]: 種名、出現回数、総個体数
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                sm.name as species_name,
                sm.genus,
                sm.subfamily,
                COUNT(DISTINCT se.survey_site_id) as site_count,
                COUNT(ar.id) as occurrence_count,
                SUM(ar.count) as total_count,
                AVG(ar.count) as avg_count
            FROM species_master sm
            LEFT JOIN ant_records ar ON sm.id = ar.species_id AND ar.deleted_at IS NULL
            LEFT JOIN survey_events se ON ar.survey_event_id = se.id
            WHERE sm.deleted_at IS NULL
            GROUP BY sm.id
            HAVING occurrence_count > 0
            ORDER BY occurrence_count DESC, total_count DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_diversity_by_site(self, survey_site_id: int) -> Dict[str, Any]:
        """
        調査地ごとの種多様性を取得
        
        Args:
            survey_site_id: 調査地ID
            
        Returns:
            Dict: 種数、総個体数
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT ar.species_id) as species_count,
                SUM(ar.count) as total_individuals
            FROM ant_records ar
            JOIN survey_events se ON ar.survey_event_id = se.id
            WHERE se.survey_site_id = ? AND ar.deleted_at IS NULL
        """, (survey_site_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {'species_count': 0, 'total_individuals': 0}
    
    def count_by_event(self, survey_event_id: int) -> int:
        """
        調査イベントに紐付く出現記録の数を取得
        
        Args:
            survey_event_id: 調査イベントID
            
        Returns:
            int: 記録数
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM ant_records
            WHERE survey_event_id = ? AND deleted_at IS NULL
        """, (survey_event_id,))
        
        return cursor.fetchone()[0]
