"""
種名マスタモデル
"""
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any


class Species:
    """種名マスタモデルクラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続オブジェクト
        """
        self.conn = db_connection
    
    def create(self, name: str, 
               genus: Optional[str] = None,
               subfamily: Optional[str] = None,
               remarks: Optional[str] = None) -> int:
        """
        種を新規登録
        
        Args:
            name: 種名（学名）
            genus: 属名
            subfamily: 亜科名
            remarks: 備考
            
        Returns:
            int: 作成されたレコードのID
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO species_master (name, genus, subfamily, remarks)
                VALUES (?, ?, ?, ?)
            """, (name, genus, subfamily, remarks))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(f"種名 '{name}' は既に登録されています")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_by_id(self, species_id: int) -> Optional[Dict[str, Any]]:
        """
        IDで種を取得
        
        Args:
            species_id: 種ID
            
        Returns:
            Dict: 種データ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM species_master 
            WHERE id = ? AND deleted_at IS NULL
        """, (species_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        種名で取得
        
        Args:
            name: 種名
            
        Returns:
            Dict: 種データ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM species_master 
            WHERE name = ? AND deleted_at IS NULL
        """, (name,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all(self, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """
        全種を取得
        
        Args:
            include_deleted: 削除済みデータを含めるか
            
        Returns:
            List[Dict]: 種データのリスト
        """
        cursor = self.conn.cursor()
        
        if include_deleted:
            cursor.execute("SELECT * FROM species_master ORDER BY name")
        else:
            cursor.execute("""
                SELECT * FROM species_master 
                WHERE deleted_at IS NULL 
                ORDER BY name
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, species_id: int,
               name: Optional[str] = None,
               genus: Optional[str] = None,
               subfamily: Optional[str] = None,
               remarks: Optional[str] = None) -> bool:
        """
        種情報を更新
        
        Args:
            species_id: 種ID
            name: 種名
            genus: 属名
            subfamily: 亜科名
            remarks: 備考
            
        Returns:
            bool: 更新成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            update_fields = []
            values = []
            
            if name is not None:
                update_fields.append("name = ?")
                values.append(name)
            if genus is not None:
                update_fields.append("genus = ?")
                values.append(genus)
            if subfamily is not None:
                update_fields.append("subfamily = ?")
                values.append(subfamily)
            if remarks is not None:
                update_fields.append("remarks = ?")
                values.append(remarks)
            
            if update_fields:
                update_fields.append("updated_at = ?")
                values.append(datetime.now())
                values.append(species_id)
                
                sql = f"""
                    UPDATE species_master 
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
                raise ValueError(f"種名 '{name}' は既に登録されています")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def delete(self, species_id: int, logical: bool = True) -> bool:
        """
        種を削除
        
        Args:
            species_id: 種ID
            logical: 論理削除（True）か物理削除（False）か
            
        Returns:
            bool: 削除成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            if logical:
                cursor.execute("""
                    UPDATE species_master 
                    SET deleted_at = ? 
                    WHERE id = ? AND deleted_at IS NULL
                """, (datetime.now(), species_id))
            else:
                cursor.execute("""
                    DELETE FROM species_master WHERE id = ?
                """, (species_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("この種にはアリ類出現記録が紐付いているため削除できません")
            raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """
        キーワードで種を検索
        
        Args:
            keyword: 検索キーワード（種名、属名、亜科名を対象）
            
        Returns:
            List[Dict]: マッチした種のリスト
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM species_master 
            WHERE deleted_at IS NULL 
            AND (name LIKE ? OR genus LIKE ? OR subfamily LIKE ?)
            ORDER BY name
        """, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_by_subfamily(self, subfamily: str) -> List[Dict[str, Any]]:
        """
        亜科で種を取得
        
        Args:
            subfamily: 亜科名
            
        Returns:
            List[Dict]: 種のリスト
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM species_master 
            WHERE subfamily = ? AND deleted_at IS NULL
            ORDER BY name
        """, (subfamily,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_or_create(self, name: str, 
                      genus: Optional[str] = None,
                      subfamily: Optional[str] = None) -> int:
        """
        種を取得、存在しない場合は作成
        
        Args:
            name: 種名
            genus: 属名
            subfamily: 亜科名
            
        Returns:
            int: 種ID
        """
        # 既存の種を検索
        existing = self.get_by_name(name)
        if existing:
            return existing['id']
        
        # 存在しない場合は作成
        return self.create(name, genus, subfamily)
    
    def count(self) -> int:
        """
        登録されている種の総数を取得
        
        Returns:
            int: 種数
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM species_master 
            WHERE deleted_at IS NULL
        """)
        
        return cursor.fetchone()[0]
