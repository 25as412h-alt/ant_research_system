"""
植生データモデル
"""
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any, List


class Vegetation:
    """植生データモデルクラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続オブジェクト
        """
        self.conn = db_connection
    
    def create(self, survey_event_id: int,
               dominant_tree: Optional[str] = None,
               dominant_sasa: Optional[str] = None,
               dominant_herb: Optional[str] = None,
               litter_type: Optional[str] = None,
               basal_area: Optional[float] = None,
               avg_tree_height: Optional[float] = None,
               avg_herb_height: Optional[float] = None,
               soil_temperature: Optional[float] = None,
               canopy_coverage: Optional[float] = None,
               sasa_coverage: Optional[float] = None,
               herb_coverage: Optional[float] = None,
               litter_coverage: Optional[float] = None,
               light_condition: Optional[int] = None,
               soil_moisture: Optional[int] = None,
               vegetation_complexity: Optional[int] = None) -> int:
        """
        植生データを新規作成
        
        Args:
            survey_event_id: 調査イベントID
            dominant_tree: 優占樹種
            dominant_sasa: 優占ササ種
            dominant_herb: 優占草本
            litter_type: リター種類
            basal_area: 胸高断面積合計 (㎡/ha)
            avg_tree_height: 平均樹高 (m)
            avg_herb_height: 平均草丈 (cm)
            soil_temperature: 地温 (℃)
            canopy_coverage: 樹冠被度 (%)
            sasa_coverage: ササ被度 (%)
            herb_coverage: 草本被度 (%)
            litter_coverage: リター被度 (%)
            light_condition: 光条件 (1-5)
            soil_moisture: 土湿条件 (1-5)
            vegetation_complexity: 植生複雑度 (1-5)
            
        Returns:
            int: 作成されたレコードのID
        """
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO vegetation_data (
                    survey_event_id, dominant_tree, dominant_sasa, dominant_herb, litter_type,
                    basal_area, avg_tree_height, avg_herb_height, soil_temperature,
                    canopy_coverage, sasa_coverage, herb_coverage, litter_coverage,
                    light_condition, soil_moisture, vegetation_complexity
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                survey_event_id, dominant_tree, dominant_sasa, dominant_herb, litter_type,
                basal_area, avg_tree_height, avg_herb_height, soil_temperature,
                canopy_coverage, sasa_coverage, herb_coverage, litter_coverage,
                light_condition, soil_moisture, vegetation_complexity
            ))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "FOREIGN KEY constraint failed" in str(e):
                raise ValueError("指定された調査イベントが存在しません")
            elif "CHECK constraint failed" in str(e):
                raise ValueError("入力値が範囲外です。被度は0-100%、段階評価は1-5で入力してください")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def get_by_event(self, survey_event_id: int) -> Optional[Dict[str, Any]]:
        """
        調査イベントに紐付く植生データを取得
        
        Args:
            survey_event_id: 調査イベントID
            
        Returns:
            Dict: 植生データ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT vd.*
            FROM vegetation_data vd
            WHERE vd.survey_event_id = ? AND vd.deleted_at IS NULL
        """, (survey_event_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_by_id(self, vegetation_id: int) -> Optional[Dict[str, Any]]:
        """
        IDで植生データを取得
        
        Args:
            vegetation_id: 植生データID
            
        Returns:
            Dict: 植生データ（存在しない場合はNone）
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM vegetation_data 
            WHERE id = ? AND deleted_at IS NULL
        """, (vegetation_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all(self, survey_site_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        植生データを取得
        
        Args:
            survey_site_id: 調査地IDで絞り込み（Noneの場合は全て）
            
        Returns:
            List[Dict]: 植生データのリスト
        """
        cursor = self.conn.cursor()
        
        sql = """
            SELECT 
                vd.*,
                se.survey_date,
                ss.name as site_name,
                ps.name as parent_site_name
            FROM vegetation_data vd
            JOIN survey_events se ON vd.survey_event_id = se.id
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE vd.deleted_at IS NULL
        """
        
        params = []
        
        if survey_site_id is not None:
            sql += " AND se.survey_site_id = ?"
            params.append(survey_site_id)
        
        sql += " ORDER BY se.survey_date DESC"
        
        cursor.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update(self, vegetation_id: int, **kwargs) -> bool:
        """
        植生データを更新
        
        Args:
            vegetation_id: 植生データID
            **kwargs: 更新する項目（任意）
            
        Returns:
            bool: 更新成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            # 更新可能なフィールドのリスト
            updatable_fields = [
                'dominant_tree', 'dominant_sasa', 'dominant_herb', 'litter_type',
                'basal_area', 'avg_tree_height', 'avg_herb_height', 'soil_temperature',
                'canopy_coverage', 'sasa_coverage', 'herb_coverage', 'litter_coverage',
                'light_condition', 'soil_moisture', 'vegetation_complexity'
            ]
            
            update_fields = []
            values = []
            
            for field in updatable_fields:
                if field in kwargs:
                    update_fields.append(f"{field} = ?")
                    values.append(kwargs[field])
            
            if update_fields:
                update_fields.append("updated_at = ?")
                values.append(datetime.now())
                values.append(vegetation_id)
                
                sql = f"""
                    UPDATE vegetation_data 
                    SET {', '.join(update_fields)}
                    WHERE id = ? AND deleted_at IS NULL
                """
                cursor.execute(sql, values)
                
                self.conn.commit()
                return cursor.rowcount > 0
            
            return False
            
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if "CHECK constraint failed" in str(e):
                raise ValueError("入力値が範囲外です。被度は0-100%、段階評価は1-5で入力してください")
            else:
                raise
        except Exception as e:
            self.conn.rollback()
            raise
    
    def delete(self, vegetation_id: int, logical: bool = True) -> bool:
        """
        植生データを削除
        
        Args:
            vegetation_id: 植生データID
            logical: 論理削除（True）か物理削除（False）か
            
        Returns:
            bool: 削除成功時True
        """
        cursor = self.conn.cursor()
        
        try:
            if logical:
                cursor.execute("""
                    UPDATE vegetation_data 
                    SET deleted_at = ? 
                    WHERE id = ? AND deleted_at IS NULL
                """, (datetime.now(), vegetation_id))
            else:
                cursor.execute("""
                    DELETE FROM vegetation_data WHERE id = ?
                """, (vegetation_id,))
            
            self.conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            self.conn.rollback()
            raise
    
    def exists_for_event(self, survey_event_id: int) -> bool:
        """
        指定された調査イベントに植生データが存在するか確認
        
        Args:
            survey_event_id: 調査イベントID
            
        Returns:
            bool: 存在する場合True
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM vegetation_data
            WHERE survey_event_id = ? AND deleted_at IS NULL
        """, (survey_event_id,))
        
        return cursor.fetchone()[0] > 0
