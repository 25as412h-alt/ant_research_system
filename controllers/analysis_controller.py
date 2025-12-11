"""
統計解析コントローラー
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional, Any
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')  # GUI用バックエンド


class AnalysisController:
    """統計解析管理クラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続
        """
        self.conn = db_connection
        
        # 日本語フォント設定
        plt.rcParams['font.sans-serif'] = ['Yu Gothic', 'MS Gothic', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def calculate_diversity_indices(self, site_id: Optional[int] = None) -> pd.DataFrame:
        """
        種多様度指数を計算
        
        Args:
            site_id: 調査地ID（Noneの場合は全調査地）
            
        Returns:
            DataFrame: 多様度指数のデータフレーム
        """
        # データ取得
        sql = """
            SELECT 
                se.survey_site_id,
                ss.name as site_name,
                ps.name as parent_site_name,
                ar.species_id,
                SUM(ar.count) as total_count
            FROM ant_records ar
            JOIN survey_events se ON ar.survey_event_id = se.id
            JOIN survey_sites ss ON se.survey_site_id = ss.id
            JOIN parent_sites ps ON ss.parent_site_id = ps.id
            WHERE ar.deleted_at IS NULL
        """
        
        params = []
        if site_id is not None:
            sql += " AND se.survey_site_id = ?"
            params.append(site_id)
        
        sql += " GROUP BY se.survey_site_id, ar.species_id"
        
        df = pd.read_sql_query(sql, self.conn, params=params)
        
        if df.empty:
            return pd.DataFrame()
        
        # 調査地ごとに計算
        results = []
        
        for site_id in df['survey_site_id'].unique():
            site_data = df[df['survey_site_id'] == site_id]
            site_name = site_data['site_name'].iloc[0]
            parent_name = site_data['parent_site_name'].iloc[0]
            
            counts = site_data['total_count'].values
            total = counts.sum()
            
            # 種数
            species_richness = len(counts)
            
            # Shannon多様度指数
            proportions = counts / total
            shannon = -np.sum(proportions * np.log(proportions))
            
            # Simpson多様度指数
            simpson = 1 - np.sum(proportions ** 2)
            
            # Pielou均等度
            pielou = shannon / np.log(species_richness) if species_richness > 1 else 0
            
            # Berger-Parker優占度
            berger_parker = np.max(counts) / total
            
            results.append({
                'site_id': site_id,
                'parent_site_name': parent_name,
                'site_name': site_name,
                'species_richness': species_richness,
                'total_individuals': int(total),
                'shannon_index': round(shannon, 3),
                'simpson_index': round(simpson, 3),
                'pielou_evenness': round(pielou, 3),
                'berger_parker_dominance': round(berger_parker, 3)
            })
        
        return pd.DataFrame(results)
    
    def calculate_correlation(self, var1_name: str, var2_name: str,
                            method: str = 'pearson') -> Dict[str, Any]:
        """
        2変数間の相関を計算
        
        Args:
            var1_name: 変数1のカラム名
            var2_name: 変数2のカラム名
            method: 相関係数の種類 ('pearson' or 'spearman')
            
        Returns:
            Dict: 相関係数、p値、データ
        """
        # 植生データから取得
        sql = f"""
            SELECT 
                vd.{var1_name},
                vd.{var2_name}
            FROM vegetation_data vd
            WHERE vd.deleted_at IS NULL
            AND vd.{var1_name} IS NOT NULL
            AND vd.{var2_name} IS NOT NULL
        """
        
        df = pd.read_sql_query(sql, self.conn)
        
        if len(df) < 3:
            raise ValueError("データが不足しています（最低3件必要）")
        
        x = df[var1_name].values
        y = df[var2_name].values
        
        if method == 'pearson':
            corr, p_value = stats.pearsonr(x, y)
        else:
            corr, p_value = stats.spearmanr(x, y)
        
        return {
            'correlation': round(corr, 4),
            'p_value': round(p_value, 4),
            'n': len(df),
            'data': df,
            'method': method
        }
    
    def create_scatter_plot(self, var1_name: str, var2_name: str,
                          var1_label: str, var2_label: str,
                          show_regression: bool = True) -> plt.Figure:
        """
        散布図を作成
        
        Args:
            var1_name: 変数1のカラム名
            var2_name: 変数2のカラム名
            var1_label: 変数1の表示ラベル
            var2_label: 変数2の表示ラベル
            show_regression: 回帰直線を表示するか
            
        Returns:
            Figure: matplotlibのFigureオブジェクト
        """
        # データ取得
        result = self.calculate_correlation(var1_name, var2_name, 'pearson')
        df = result['data']
        
        # 図の作成
        fig, ax = plt.subplots(figsize=(8, 6))
        
        x = df[var1_name].values
        y = df[var2_name].values
        
        # 散布図
        ax.scatter(x, y, alpha=0.6, s=50)
        
        # 回帰直線
        if show_regression and len(x) > 2:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, p(x_line), "r--", alpha=0.8, linewidth=2)
        
        # ラベル設定
        ax.set_xlabel(var1_label, fontsize=12)
        ax.set_ylabel(var2_label, fontsize=12)
        ax.set_title(f'{var1_label} vs {var2_label}\n'
                    f'相関係数: {result["correlation"]:.3f} (p={result["p_value"]:.3f})',
                    fontsize=14)
        
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return fig
    
    def create_diversity_comparison(self) -> plt.Figure:
        """
        調査地間の種多様度比較グラフを作成
        
        Returns:
            Figure: matplotlibのFigureオブジェクト
        """
        diversity_df = self.calculate_diversity_indices()
        
        if diversity_df.empty:
            raise ValueError("多様度データがありません")
        
        # 上位10調査地のみ表示（多すぎる場合）
        if len(diversity_df) > 10:
            diversity_df = diversity_df.nlargest(10, 'shannon_index')
        
        # 図の作成
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Shannon指数
        ax1.barh(diversity_df['site_name'], diversity_df['shannon_index'], 
                color='steelblue', alpha=0.7)
        ax1.set_xlabel('Shannon多様度指数', fontsize=11)
        ax1.set_title('Shannon多様度指数の比較', fontsize=13, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        
        # 種数
        ax2.barh(diversity_df['site_name'], diversity_df['species_richness'], 
                color='coral', alpha=0.7)
        ax2.set_xlabel('種数', fontsize=11)
        ax2.set_title('種数の比較', fontsize=13, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        
        return fig
    
    def create_species_accumulation_curve(self) -> plt.Figure:
        """
        種数累積曲線を作成
        
        Returns:
            Figure: matplotlibのFigureオブジェクト
        """
        # 調査イベントごとの種数を取得
        sql = """
            SELECT 
                se.id,
                se.survey_date,
                COUNT(DISTINCT ar.species_id) as species_count
            FROM survey_events se
            LEFT JOIN ant_records ar ON se.id = ar.survey_event_id
            WHERE se.deleted_at IS NULL
            GROUP BY se.id
            ORDER BY se.survey_date
        """
        
        df = pd.read_sql_query(sql, self.conn)
        
        if df.empty:
            raise ValueError("データがありません")
        
        # 全種取得
        all_species_sql = """
            SELECT DISTINCT species_id
            FROM ant_records
            WHERE deleted_at IS NULL
        """
        all_species = pd.read_sql_query(all_species_sql, self.conn)
        
        # 累積種数を計算
        cumulative_species = []
        seen_species = set()
        
        for idx, row in df.iterrows():
            # このイベントで出現した種
            event_species_sql = f"""
                SELECT DISTINCT species_id
                FROM ant_records
                WHERE survey_event_id = {row['id']}
                AND deleted_at IS NULL
            """
            event_species = pd.read_sql_query(event_species_sql, self.conn)
            
            for species_id in event_species['species_id']:
                seen_species.add(species_id)
            
            cumulative_species.append(len(seen_species))
        
        # 図の作成
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(range(1, len(cumulative_species) + 1), cumulative_species, 
               marker='o', linewidth=2, markersize=5, color='forestgreen')
        
        # 最大種数の参照線
        ax.axhline(y=len(all_species), color='red', linestyle='--', 
                  alpha=0.5, label=f'全種数: {len(all_species)}')
        
        ax.set_xlabel('調査イベント数', fontsize=12)
        ax.set_ylabel('累積種数', fontsize=12)
        ax.set_title('種数累積曲線', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.tight_layout()
        
        return fig
    
    def get_vegetation_summary_stats(self) -> pd.DataFrame:
        """
        植生データの基本統計量を取得
        
        Returns:
            DataFrame: 基本統計量
        """
        sql = """
            SELECT 
                basal_area,
                avg_tree_height,
                avg_herb_height,
                soil_temperature,
                canopy_coverage,
                sasa_coverage,
                herb_coverage,
                litter_coverage,
                light_condition,
                soil_moisture,
                vegetation_complexity
            FROM vegetation_data
            WHERE deleted_at IS NULL
        """
        
        df = pd.read_sql_query(sql, self.conn)
        
        if df.empty:
            return pd.DataFrame()
        
        # 基本統計量を計算
        summary = df.describe().T
        summary['median'] = df.median()
        
        # 列名を日本語に
        summary.index = [
            '胸高断面積',
            '平均樹高',
            '平均草丈',
            '地温',
            '樹冠被度',
            'ササ被度',
            '草本被度',
            'リター被度',
            '光条件',
            '土湿条件',
            '植生複雑度'
        ]
        
        summary.columns = ['件数', '平均', '標準偏差', '最小値', '25%', '50%', '75%', '最大値', '中央値']
        
        return summary.round(2)
