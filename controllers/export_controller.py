"""
データ出力コントローラー
"""
import pandas as pd
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


class ExportController:
    """データ出力管理クラス"""
    
    def __init__(self, db_connection, export_dir='exports'):
        """
        初期化
        
        Args:
            db_connection: データベース接続
            export_dir: エクスポート先ディレクトリ
        """
        self.conn = db_connection
        self.export_dir = export_dir
        
        # ディレクトリが存在しない場合は作成
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
    
    def export_ant_matrix(self, value_type='presence', 
                         start_date: Optional[str] = None,
                         end_date: Optional[str] = None,
                         site_ids: Optional[List[int]] = None) -> str:
        """
        アリ類群集行列を出力
        
        Args:
            value_type: 値のタイプ ('presence': 在不在, 'count': 個体数)
            start_date: 開始日（YYYY-MM-DD）
            end_date: 終了日（YYYY-MM-DD）
            site_ids: 出力する調査地IDのリスト
            
        Returns:
            str: 出力ファイルパス
        """
        # データ取得クエリ
        sql = """
            SELECT 
                ss.name || ' (' || ps.name || ')' as site_name,
                sm.name as species_name,
                ar.count
            FROM ant_records ar
            JOIN survey_events se ON ar.survey_event_id = se.id
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
            JOIN species_master sm ON ar.species_id = sm.id
            WHERE ar.deleted_at IS NULL
        """
        
        params = []
        
        if start_date:
            sql += " AND date(se.survey_date) >= ?"
            params.append(start_date)
        
        if end_date:
            sql += " AND date(se.survey_date) <= ?"
            params.append(end_date)
        
        if site_ids:
            placeholders = ','.join('?' * len(site_ids))
            sql += f" AND se.survey_site_id IN ({placeholders})"
            params.extend(site_ids)
        
        sql += " ORDER BY site_name, species_name"
        
        # データフレーム作成
        df = pd.read_sql_query(sql, self.conn, params=params)
        
        if df.empty:
            raise ValueError("出力するデータがありません")
        
        # ピボットテーブル作成
        if value_type == 'presence':
            # 在不在（0/1）
            pivot_df = df.pivot_table(
                index='site_name',
                columns='species_name',
                values='count',
                aggfunc=lambda x: 1,  # 出現していれば1
                fill_value=0
            )
        else:
            # 個体数
            pivot_df = df.pivot_table(
                index='site_name',
                columns='species_name',
                values='count',
                aggfunc='sum',
                fill_value=0
            )
        
        # ファイル名生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ant_matrix_{value_type}_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        # CSV出力（UTF-8 with BOM for Excel）
        pivot_df.to_csv(filepath, encoding='utf-8-sig')
        
        return filepath
    
    def export_vegetation_matrix(self, 
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None,
                                site_ids: Optional[List[int]] = None) -> str:
        """
        植生データ行列を出力
        
        Args:
            start_date: 開始日
            end_date: 終了日
            site_ids: 出力する調査地IDのリスト
            
        Returns:
            str: 出力ファイルパス
        """
        sql = """
            SELECT 
                ss.name || ' (' || ps.name || ')' as site_name,
                se.survey_date,
                vd.dominant_tree,
                vd.dominant_sasa,
                vd.dominant_herb,
                vd.basal_area,
                vd.avg_tree_height,
                vd.avg_herb_height,
                vd.soil_temperature,
                vd.canopy_coverage,
                vd.sasa_coverage,
                vd.herb_coverage,
                vd.litter_coverage,
                vd.light_condition,
                vd.soil_moisture,
                vd.vegetation_complexity
            FROM vegetation_data vd
            JOIN survey_events se ON vd.survey_event_id = se.id
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE vd.deleted_at IS NULL
        """
        
        params = []
        
        if start_date:
            sql += " AND date(se.survey_date) >= ?"
            params.append(start_date)
        
        if end_date:
            sql += " AND date(se.survey_date) <= ?"
            params.append(end_date)
        
        if site_ids:
            placeholders = ','.join('?' * len(site_ids))
            sql += f" AND se.survey_site_id IN ({placeholders})"
            params.extend(site_ids)
        
        sql += " ORDER BY se.survey_date DESC"
        
        df = pd.read_sql_query(sql, self.conn, params=params)
        
        if df.empty:
            raise ValueError("出力するデータがありません")
        
        # ファイル名生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"vegetation_data_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        # CSV出力
        df.to_csv(filepath, encoding='utf-8-sig', index=False)
        
        return filepath
    
    def export_combined_data(self, include_diversity: bool = True) -> str:
        """
        調査地ごとの統合データを出力（植生 + 種多様性）
        
        Args:
            include_diversity: 多様度指数を含めるか
            
        Returns:
            str: 出力ファイルパス
        """
        # 植生データ取得
        veg_sql = """
            SELECT 
                ss.id as site_id,
                ss.name as site_name,
                ps.name as parent_site_name,
                ss.latitude,
                ss.longitude,
                ss.altitude,
                ss.area,
                AVG(vd.basal_area) as avg_basal_area,
                AVG(vd.avg_tree_height) as avg_tree_height,
                AVG(vd.canopy_coverage) as avg_canopy_coverage,
                AVG(vd.sasa_coverage) as avg_sasa_coverage,
                AVG(vd.herb_coverage) as avg_herb_coverage,
                AVG(vd.litter_coverage) as avg_litter_coverage,
                AVG(vd.light_condition) as avg_light_condition,
                AVG(vd.soil_moisture) as avg_soil_moisture,
                AVG(vd.vegetation_complexity) as avg_vegetation_complexity
            FROM survey_sites ss
            LEFT JOIN parent_sites ps ON ss.parent_site_id = ps.id
            LEFT JOIN survey_events se ON ss.id = se.survey_site_id
            LEFT JOIN vegetation_data vd ON se.id = vd.survey_event_id
            WHERE ss.deleted_at IS NULL
            GROUP BY ss.id
        """
        
        df = pd.read_sql_query(veg_sql, self.conn)
        
        if include_diversity:
            # 種多様性を追加
            diversity_sql = """
                SELECT 
                    se.survey_site_id as site_id,
                    COUNT(DISTINCT ar.species_id) as species_richness,
                    SUM(ar.count) as total_individuals
                FROM ant_records ar
                JOIN survey_events se ON ar.survey_event_id = se.id
                WHERE ar.deleted_at IS NULL
                GROUP BY se.survey_site_id
            """
            
            diversity_df = pd.read_sql_query(diversity_sql, self.conn)
            
            # マージ
            df = df.merge(diversity_df, on='site_id', how='left')
            df['species_richness'] = df['species_richness'].fillna(0).astype(int)
            df['total_individuals'] = df['total_individuals'].fillna(0).astype(int)
        
        # ファイル名生成
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"combined_data_{timestamp}.csv"
        filepath = os.path.join(self.export_dir, filename)
        
        # CSV出力
        df.to_csv(filepath, encoding='utf-8-sig', index=False)
        
        return filepath
    
    def export_to_excel(self, include_all_sheets: bool = True) -> str:
        """
        複数シートを含むExcelファイルを出力
        
        Args:
            include_all_sheets: 全シートを含めるか
            
        Returns:
            str: 出力ファイルパス
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"ant_research_data_{timestamp}.xlsx"
        filepath = os.path.join(self.export_dir, filename)
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # シート1: 親調査地
            parent_sql = "SELECT * FROM parent_sites WHERE deleted_at IS NULL"
            pd.read_sql_query(parent_sql, self.conn).to_excel(
                writer, sheet_name='親調査地', index=False)
            
            # シート2: 調査地
            site_sql = """
                SELECT ss.*, ps.name as parent_site_name
                FROM survey_sites ss
                LEFT JOIN parent_sites ps ON ss.parent_site_id = ps.id
                WHERE ss.deleted_at IS NULL
            """
            pd.read_sql_query(site_sql, self.conn).to_excel(
                writer, sheet_name='調査地', index=False)
            
            # シート3: 調査イベント
            event_sql = """
                SELECT se.*, ss.name as site_name
                FROM survey_events se
                LEFT JOIN survey_sites ss ON se.survey_site_id = ss.id
                WHERE se.deleted_at IS NULL
            """
            pd.read_sql_query(event_sql, self.conn).to_excel(
                writer, sheet_name='調査イベント', index=False)
            
            if include_all_sheets:
                # シート4: 植生データ
                veg_sql = """
                    SELECT vd.*, se.survey_date, ss.name as site_name
                    FROM vegetation_data vd
                    LEFT JOIN survey_events se ON vd.survey_event_id = se.id
                    LEFT JOIN survey_sites ss ON se.survey_site_id = ss.id
                    WHERE vd.deleted_at IS NULL
                """
                pd.read_sql_query(veg_sql, self.conn).to_excel(
                    writer, sheet_name='植生データ', index=False)
                
                # シート5: アリ類記録
                ant_sql = """
                    SELECT ar.*, se.survey_date, ss.name as site_name, sm.name as species_name
                    FROM ant_records ar
                    LEFT JOIN survey_events se ON ar.survey_event_id = se.id
                    LEFT JOIN survey_sites ss ON se.survey_site_id = ss.id
                    LEFT JOIN species_master sm ON ar.species_id = sm.id
                    WHERE ar.deleted_at IS NULL
                """
                pd.read_sql_query(ant_sql, self.conn).to_excel(
                    writer, sheet_name='アリ類記録', index=False)
                
                # シート6: 種マスタ
                species_sql = "SELECT * FROM species_master WHERE deleted_at IS NULL"
                pd.read_sql_query(species_sql, self.conn).to_excel(
                    writer, sheet_name='種マスタ', index=False)
        
        return filepath
    
    def get_export_summary(self) -> Dict[str, int]:
        """
        エクスポート可能なデータのサマリーを取得
        
        Returns:
            Dict: データ件数のサマリー
        """
        cursor = self.conn.cursor()
        
        summary = {}
        
        tables = [
            ('parent_sites', '親調査地'),
            ('survey_sites', '調査地'),
            ('survey_events', '調査イベント'),
            ('vegetation_data', '植生データ'),
            ('species_master', '種マスタ'),
            ('ant_records', 'アリ類記録')
        ]
        
        for table, name in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE deleted_at IS NULL")
            summary[name] = cursor.fetchone()[0]
        
        return summary
