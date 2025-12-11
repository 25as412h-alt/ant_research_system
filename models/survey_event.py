"""
調査イベントモデル
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


class SurveyEvent:
    """調査イベントモデルクラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続オブジェクト
        """
        self.conn = db_connection
    
    def create(self, survey_site_id: int, survey_date: str,
               surveyor_name: Optional[str] = None,
               weather: Optional[str] = None,
               temperature: Optional[float] = None,
               remarks: Optional[str] = None) -> int:
        """
        調査イベントを新規作成
        
        Args:
            survey_site_id: 調査地ID
            survey_date: 調査日時（YYYY-MM-DD HH:MM 形式）
            surveyor_name: 調査者名
            weather: 天候（晴れ/曇り/雨/雪）
            temperature: 気温（℃）
            remarks: 備考
            
        Returns:
            int: 作成されたレコードのID
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO survey_events 
                (survey_site_id, survey_date, surveyor_name, weather, temperature, remarks)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (survey_site_id, survey_date, surveyor_name, weather, temperature, remarks))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("指定された調査地が存在しません")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("天候は「晴れ/曇り/雨/雪」のいずれかを選択してください")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_by_id(self, event_id: int) -> Optional[Dict[str, Any]]:
        """
        IDで調査イベントを取得
        
        Args:
            event_id: 調査イベントID
            
        Returns:
            Dict: 調査イベントデータ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                se.*,
                ss.name as site_name,
                ps.name as parent_site_name
            FROM survey_events se
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE se.id = ? AND se.deleted_at IS NULL
        """, (event_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all(self, survey_site_id: Optional[int] = None,
                start_date: Optional[str] = None,
                end_date: Optional[str] = None,
                include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        調査イベントを取得
        
        Args:
            survey_site_id: 調査地IDで絞り込み
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）
            include_deleted: 削除済みデータを含めるか
            
        Returns:
            List[Dict]: 調査イベントデータのリスト
        """
        cursor = self.conn.cursor()
        
        sql = """
            SELECT 
                se.*,
                ss.name as site_name,
                ps.name as parent_site_name
            FROM survey_events se
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
        """
        
        conditions = []
        params = []
        
        if not include_deleted:
            conditions.append("se.deleted_at IS NULL")
        
        if survey_site_id is not None:
            conditions.append("se.survey_site_id = ?")
            params.append(survey_site_id)
        
        if start_date:
            conditions.append("date(se.survey_date) >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("date(se.survey_date) <= ?")
            params.append(end_date)
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY se.survey_date DESC"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, event_id: int,
               survey_site_id: Optional[int] = None,
               survey_date: Optional[str] = None,
               surveyor_name: Optional[str] = None,
               weather: Optional[str] = None,
               temperature: Optional[float] = None,
               remarks: Optional[str] = None) -> bool:
        """
        調査イベントを更新
        
        Args:
            event_id: 調査イベントID
            survey_site_id: 調査地ID
            survey_date: 調査日時
            surveyor_name: 調査者名
            weather: 天候
            temperature: 気温
            remarks: 備考
            
        Returns:
            bool: 更新成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            update_fields = []
            values = []
            
            if survey_site_id is not None:
                update_fields.append("survey_site_id = ?")
                values.append(survey_site_id)
            if survey_date is not None:
                update_fields.append("survey_date = ?")
                values.append(survey_date)
            if surveyor_name is not None:
                update_fields.append("surveyor_name = ?")
                values.append(surveyor_name)
            if weather is not None:
                update_fields.append("weather = ?")
                values.append(weather)
            if temperature is not None:
                update_fields.append("temperature = ?")
                values.append(temperature)
            if remarks is not None:
                update_fields.append("remarks = ?")
                values.append(remarks)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                values.append(datetime.now())
                values.append(event_id)
                
                sql = f"""
                    UPDATE survey_events 
                    SET {', '.join(update_fields)}
                    WHERE id = ? AND deleted_at IS NULL
                """
                cursor.execute(sql, values)
                
                self.conn.commit()
                return cursor.rowcount > 0
            
            return False
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("指定された調査地が存在しません")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("天候は「晴れ/曇り/雨/雪」のいずれかを選択してください")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def delete(self, event_id: int, logical: bool = True) -> bool:
        """
        調査イベントを削除
        
        Args:
            event_id: 調査イベントID
            logical: 論理削除（True）か物理削除（False）か
            
        Returns:
            bool: 削除成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            if logical:
                cursor.execute("""
                    UPDATE survey_events 
                    SET deleted_at = ? 
                    WHERE id = ? AND deleted_at IS NULL
                """, (datetime.now(), event_id))
            else:
                cursor.execute("""
                    DELETE FROM survey_events WHERE id = ?
                """, (event_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("この調査イベントには植生データまたはアリ類データが紐付いているため削除できません")
            raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_by_site(self, survey_site_id: int) -> List[Dict[str, Any]]:
        """
        調査地に紐付く調査イベントを取得
        
        Args:
            survey_site_id: 調査地ID
            
        Returns:
            List[Dict]: 調査イベントのリスト
        """
        return self.get_all(survey_site_id=survey_site_id)
    
    def count_by_site(self, survey_site_id: int) -> int:
        """
        調査地に紐付く調査イベントの数を取得
        
        Args:
            survey_site_id: 調査地ID
            
        Returns:
            int: 調査イベント数
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM survey_events
            WHERE survey_site_id = ? AND deleted_at IS NULL
        """, (survey_site_id,))
        
        return cursor.fetchone()[0]
    
    def get_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        最近の調査イベントを取得
        
        Args:
            limit: 取得件数
            
        Returns:
            List[Dict]: 調査イベントのリスト
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                se.*,
                ss.name as site_name,
                ps.name as parent_site_name
            FROM survey_events se
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE se.deleted_at IS NULL
            ORDER BY se.survey_date DESC
            LIMIT ?
        """, (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
