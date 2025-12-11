"""
親調査地モデル
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


class ParentSite:
    """親調査地モデルクラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続オブジェクト
        """
        self.conn = db_connection
    
    def create(self, name: str, latitude: float, longitude: float, 
               altitude: Optional[float] = None, remarks: Optional[str] = None,
               environment_tags: Optional[List[int]] = None) -> int:
        """
        親調査地を新規作成
        
        Args:
            name: 名称
            latitude: 緯度
            longitude: 経度
            altitude: 標高
            remarks: 備考
            environment_tags: 環境タグIDのリスト
            
        Returns:
            int: 作成されたレコードのID
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO parent_sites (name, latitude, longitude, altitude, remarks)
                VALUES (?, ?, ?, ?, ?)
            """, (name, latitude, longitude, altitude, remarks))
            
            parent_site_id = cursor.lastrowid
            
            # 環境タグの紐付け
            if environment_tags:
                for tag_id in environment_tags:
                    cursor.execute("""
                        INSERT INTO parent_site_environments (parent_site_id, environment_tag_id)
                        VALUES (?, ?)
                    """, (parent_site_id, tag_id))
            
            self.conn.commit()
            return parent_site_id
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"親調査地名 '{name}' は既に登録されています")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("緯度は-90～90、経度は-180～180の範囲で入力してください")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_by_id(self, parent_site_id: int) -> Optional[Dict[str, Any]]:
        """
        IDで親調査地を取得
        
        Args:
            parent_site_id: 親調査地ID
            
        Returns:
            Dict: 親調査地データ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM parent_sites 
            WHERE id = ? AND deleted_at IS NULL
        """, (parent_site_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        全親調査地を取得
        
        Args:
            include_deleted: 削除済みデータを含めるか
            
        Returns:
            List[Dict]: 親調査地データのリスト
        """
        cursor = self.conn.cursor()
        
        if include_deleted:
            cursor.execute("SELECT * FROM parent_sites ORDER BY name")
        else:
            cursor.execute("""
                SELECT * FROM parent_sites 
                WHERE deleted_at IS NULL 
                ORDER BY name
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, parent_site_id: int, name: Optional[str] = None,
               latitude: Optional[float] = None, longitude: Optional[float] = None,
               altitude: Optional[float] = None, remarks: Optional[str] = None,
               environment_tags: Optional[List[int]] = None) -> bool:
        """
        親調査地を更新
        
        Args:
            parent_site_id: 親調査地ID
            name: 名称
            latitude: 緯度
            longitude: 経度
            altitude: 標高
            remarks: 備考
            environment_tags: 環境タグIDのリスト
            
        Returns:
            bool: 更新成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            # 更新するフィールドを動的に構築
            update_fields = []
            values = []
            
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
            if remarks is not None:
                update_fields.append("remarks = ?")
                values.append(remarks)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                values.append(datetime.now())
                values.append(parent_site_id)
                
                sql = f"""
                    UPDATE parent_sites 
                    SET {', '.join(update_fields)}
                    WHERE id = ? AND deleted_at IS NULL
                """
                cursor.execute(sql, values)
            
            # 環境タグの更新
            if environment_tags is not None:
                # 既存の紐付けを削除
                cursor.execute("""
                    DELETE FROM parent_site_environments 
                    WHERE parent_site_id = ?
                """, (parent_site_id,))
                
                # 新しい紐付けを追加
                for tag_id in environment_tags:
                    cursor.execute("""
                        INSERT INTO parent_site_environments (parent_site_id, environment_tag_id)
                        VALUES (?, ?)
                    """, (parent_site_id, tag_id))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"親調査地名 '{name}' は既に登録されています")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("緯度は-90～90、経度は-180～180の範囲で入力してください")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def delete(self, parent_site_id: int, logical: bool = True) -> bool:
        """
        親調査地を削除
        
        Args:
            parent_site_id: 親調査地ID
            logical: 論理削除（True）か物理削除（False）か
            
        Returns:
            bool: 削除成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            if logical:
                # 論理削除
                cursor.execute("""
                    UPDATE parent_sites 
                    SET deleted_at = ? 
                    WHERE id = ? AND deleted_at IS NULL
                """, (datetime.now(), parent_site_id))
            else:
                # 物理削除（外部キー制約により関連データも削除される）
                cursor.execute("""
                    DELETE FROM parent_sites WHERE id = ?
                """, (parent_site_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("この親調査地には調査地が紐付いているため削除できません")
            raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_environment_tags(self, parent_site_id: int) -> List[Dict[str, Any]]:
        """
        親調査地に紐付く環境タグを取得
        
        Args:
            parent_site_id: 親調査地ID
            
        Returns:
            List[Dict]: 環境タグのリスト
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT et.* 
            FROM environment_tags et
            JOIN parent_site_environments pse ON et.id = pse.environment_tag_id
            WHERE pse.parent_site_id = ?
            ORDER BY et.name
        """, (parent_site_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        キーワードで親調査地を検索
        
        Args:
            keyword: 検索キーワード（名称、備考を対象）
            
        Returns:
            List[Dict]: マッチした親調査地のリスト
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM parent_sites 
            WHERE deleted_at IS NULL 
            AND (name LIKE ? OR remarks LIKE ?)
            ORDER BY name
        """, (f'%{keyword}%', f'%{keyword}%'))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_with_site_count(self) -> List[Dict[str, Any]]:
        """
        調査地数を含めて親調査地を取得
        
        Returns:
            List[Dict]: 親調査地データ + 調査地数
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                ps.*,
                COUNT(ss.id) as site_count
            FROM parent_sites ps
            LEFT JOIN survey_sites ss ON ps.id = ss.parent_site_id 
                AND ss.deleted_at IS NULL
            WHERE ps.deleted_at IS NULL
            GROUP BY ps.id
            ORDER BY ps.name
        """)
        
        return [dict(row) for row in cursor.fetchall()]
