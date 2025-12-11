"""
調査地モデル
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


class SurveySite:
    """調査地モデルクラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続オブジェクト
        """
        self.conn = db_connection
    
    def create(self, parent_site_id: int, name: str, 
               latitude: float, longitude: float,
               altitude: Optional[float] = None, 
               area: Optional[float] = None,
               remarks: Optional[str] = None) -> int:
        """
        調査地を新規作成
        
        Args:
            parent_site_id: 親調査地ID
            name: 名称
            latitude: 緯度
            longitude: 経度
            altitude: 標高
            area: 面積（平方メートル）
            remarks: 備考
            
        Returns:
            int: 作成されたレコードのID
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO survey_sites 
                (parent_site_id, name, latitude, longitude, altitude, area, remarks)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (parent_site_id, name, latitude, longitude, altitude, area, remarks))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"調査地名 '{name}' は同じ親調査地内に既に登録されています")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("緯度・経度・面積の値を確認してください")
            elif "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("指定された親調査地が存在しません")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_by_id(self, site_id: int) -> Optional[Dict[str, Any]]:
        """
        IDで調査地を取得
        
        Args:
            site_id: 調査地ID
            
        Returns:
            Dict: 調査地データ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT ss.*, ps.name as parent_site_name
            FROM survey_sites ss
            LEFT JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE ss.id = ? AND ss.deleted_at IS NULL
        """, (site_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all(self, parent_site_id: Optional[int] = None,
                include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        調査地を取得
        
        Args:
            parent_site_id: 親調査地IDで絞り込み（Noneの場合は全て）
            include_deleted: 削除済みデータを含めるか
            
        Returns:
            List[Dict]: 調査地データのリスト
        """
        cursor = self.conn.cursor()
        
        sql = """
            SELECT ss.*, ps.name as parent_site_name
            FROM survey_sites ss
            LEFT JOIN parent_sites ps ON ss.parent_site_id = ps.id
        """
        
        conditions = []
        params = []
        
        if not include_deleted:
            conditions.append("ss.deleted_at IS NULL")
        
        if parent_site_id is not None:
            conditions.append("ss.parent_site_id = ?")
            params.append(parent_site_id)
        
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        
        sql += " ORDER BY ps.name, ss.name"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, site_id: int, 
               parent_site_id: Optional[int] = None,
               name: Optional[str] = None,
               latitude: Optional[float] = None, 
               longitude: Optional[float] = None,
               altitude: Optional[float] = None, 
               area: Optional[float] = None,
               remarks: Optional[str] = None) -> bool:
        """
        調査地を更新
        
        Args:
            site_id: 調査地ID
            parent_site_id: 親調査地ID
            name: 名称
            latitude: 緯度
            longitude: 経度
            altitude: 標高
            area: 面積
            remarks: 備考
            
        Returns:
            bool: 更新成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            update_fields = []
            values = []
            
            if parent_site_id is not None:
                update_fields.append("parent_site_id = ?")
                values.append(parent_site_id)
            if name is not None:
                update_fields.append("name = ?")
                values.append(name)
            if latitude is not None:
                update_fields.append("latitude = ?")
                values.append(latitude)
            if longitude is not None:
                update_fields.append("longitude = ?")
                values.append(longitude)
            if altitude is not None:
                update_fields.append("altitude = ?")
                values.append(altitude)
            if area is not None:
                update_fields.append("area = ?")
                values.append(area)
            if remarks is not None:
                update_fields.append("remarks = ?")
                values.append(remarks)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                values.append(datetime.now())
                values.append(site_id)
                
                sql = f"""
                    UPDATE survey_sites 
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
                raise ValueError(f"調査地名 '{name}' は同じ親調査地内に既に登録されています")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("緯度・経度・面積の値を確認してください")
            elif "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("指定された親調査地が存在しません")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def delete(self, site_id: int, logical: bool = True) -> bool:
        """
        調査地を削除
        
        Args:
            site_id: 調査地ID
            logical: 論理削除（True）か物理削除（False）か
            
        Returns:
            bool: 削除成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            if logical:
                cursor.execute("""
                    UPDATE survey_sites 
                    SET deleted_at = ? 
                    WHERE id = ? AND deleted_at IS NULL
                """, (datetime.now(), site_id))
            else:
                cursor.execute("""
                    DELETE FROM survey_sites WHERE id = ?
                """, (site_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("この調査地には調査イベントが紐付いているため削除できません")
            raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def search(self, keyword: str, 
               parent_site_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        キーワードで調査地を検索
        
        Args:
            keyword: 検索キーワード
            parent_site_id: 親調査地IDで絞り込み
            
        Returns:
            List[Dict]: マッチした調査地のリスト
        """
        cursor = self.conn.cursor()
        
        sql = """
            SELECT ss.*, ps.name as parent_site_name
            FROM survey_sites ss
            LEFT JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE ss.deleted_at IS NULL 
            AND (ss.name LIKE ? OR ss.remarks LIKE ?)
        """
        
        params = [f'%{keyword}%', f'%{keyword}%']
        
        if parent_site_id is not None:
            sql += " AND ss.parent_site_id = ?"
            params.append(parent_site_id)
        
        sql += " ORDER BY ps.name, ss.name"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_parent_site(self, parent_site_id: int) -> List[Dict[str, Any]]:
        """
        親調査地に紐付く調査地を取得
        
        Args:
            parent_site_id: 親調査地ID
            
        Returns:
            List[Dict]: 調査地のリスト
        """
        return self.get_all(parent_site_id=parent_site_id)
    
    def count_by_parent_site(self, parent_site_id: int) -> int:
        """
        親調査地に紐付く調査地の数を取得
        
        Args:
            parent_site_id: 親調査地ID
            
        Returns:
            int: 調査地数
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM survey_sites
            WHERE parent_site_id = ? AND deleted_at IS NULL
        """, (parent_site_id,))
        
        return cursor.fetchone()[0]

# エクスポート補助: モジュールから SurveySite を明示的にエクスポート
__all__ = ["SurveySite"]