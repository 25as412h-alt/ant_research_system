"""
地図・地理情報コントローラー
"""
import folium
from folium import plugins
import pandas as pd
import numpy as np
from math import radians, sin, cos, sqrt, atan2
from sklearn.cluster import KMeans, DBSCAN
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any
import os
import webbrowser


class MapController:
    """地図・地理情報管理クラス"""
    
    def __init__(self, db_connection, map_dir='exports'):
        """
        初期化
        
        Args:
            db_connection: データベース接続
            map_dir: 地図ファイル保存先
        """
        self.conn = db_connection
        self.map_dir = map_dir
        
        if not os.path.exists(map_dir):
            os.makedirs(map_dir)
    
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        2地点間の距離を計算（Haversine公式）
        
        Args:
            lat1, lon1: 地点1の緯度経度
            lat2, lon2: 地点2の緯度経度
            
        Returns:
            float: 距離（km）
        """
        R = 6371  # 地球の半径（km）
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def get_distance_matrix(self, site_type: str = 'survey') -> pd.DataFrame:
        """
        距離行列を計算
        
        Args:
            site_type: 'survey' (調査地) or 'parent' (親調査地)
            
        Returns:
            DataFrame: 距離行列
        """
        if site_type == 'parent':
            sql = """
                SELECT id, name, latitude, longitude
                FROM parent_sites
                WHERE deleted_at IS NULL
                ORDER BY name
            """
        else:
            sql = """
                SELECT ss.id, ss.name, ss.latitude, ss.longitude
                FROM survey_sites ss
                WHERE ss.deleted_at IS NULL
                ORDER BY ss.name
            """
        
        df = pd.read_sql_query(sql, self.conn)
        
        if df.empty:
            raise ValueError("データがありません")
        
        # 距離行列を計算
        n = len(df)
        dist_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                dist = self.calculate_distance(
                    df.iloc[i]['latitude'], df.iloc[i]['longitude'],
                    df.iloc[j]['latitude'], df.iloc[j]['longitude']
                )
                dist_matrix[i, j] = dist
                dist_matrix[j, i] = dist
        
        # DataFrameに変換
        dist_df = pd.DataFrame(
            dist_matrix,
            index=df['name'].values,
            columns=df['name'].values
        )
        
        return dist_df
    
    def create_base_map(self, center_lat: Optional[float] = None,
                       center_lon: Optional[float] = None,
                       zoom: int = 10) -> folium.Map:
        """
        ベース地図を作成
        
        Args:
            center_lat: 中心緯度（Noneの場合は調査地の中心）
            center_lon: 中心経度
            zoom: ズームレベル
            
        Returns:
            folium.Map: 地図オブジェクト
        """
        # 中心座標が指定されていない場合は、調査地の中心を計算
        if center_lat is None or center_lon is None:
            sql = """
                SELECT AVG(latitude) as lat, AVG(longitude) as lon
                FROM survey_sites
                WHERE deleted_at IS NULL
            """
            result = pd.read_sql_query(sql, self.conn)
            
            if not result.empty:
                center_lat = result.iloc[0]['lat']
                center_lon = result.iloc[0]['lon']
            else:
                # デフォルト（日本の中心付近）
                center_lat = 36.0
                center_lon = 138.0
        
        # 地図作成
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=zoom,
            tiles='OpenStreetMap'
        )
        
        return m
    
    def create_site_map(self, show_parent: bool = True,
                       show_survey: bool = True,
                       show_diversity: bool = False) -> str:
        """
        調査地の地図を作成
        
        Args:
            show_parent: 親調査地を表示
            show_survey: 調査地を表示
            show_diversity: 種多様度を色で表現
            
        Returns:
            str: 生成されたHTMLファイルのパス
        """
        m = self.create_base_map()
        
        # 親調査地を表示
        if show_parent:
            parent_sql = """
                SELECT id, name, latitude, longitude
                FROM parent_sites
                WHERE deleted_at IS NULL
            """
            parent_df = pd.read_sql_query(parent_sql, self.conn)
            
            for _, site in parent_df.iterrows():
                folium.Marker(
                    location=[site['latitude'], site['longitude']],
                    popup=f"<b>{site['name']}</b><br>親調査地",
                    icon=folium.Icon(color='red', icon='home', prefix='fa'),
                    tooltip=site['name']
                ).add_to(m)
        
        # 調査地を表示
        if show_survey:
            survey_sql = """
                SELECT 
                    ss.id, 
                    ss.name, 
                    ss.latitude, 
                    ss.longitude,
                    ps.name as parent_name
                FROM survey_sites ss
                LEFT JOIN parent_sites ps ON ss.parent_site_id = ps.id
                WHERE ss.deleted_at IS NULL
            """
            survey_df = pd.read_sql_query(survey_sql, self.conn)
            
            # 多様度データを取得（show_diversity=Trueの場合）
            diversity_dict = {}
            if show_diversity:
                diversity_sql = """
                    SELECT 
                        se.survey_site_id,
                        COUNT(DISTINCT ar.species_id) as species_count
                    FROM ant_records ar
                    JOIN survey_events se ON ar.survey_event_id = se.id
                    WHERE ar.deleted_at IS NULL
                    GROUP BY se.survey_site_id
                """
                diversity_df = pd.read_sql_query(diversity_sql, self.conn)
                diversity_dict = dict(zip(diversity_df['survey_site_id'], 
                                         diversity_df['species_count']))
            
            for _, site in survey_df.iterrows():
                species_count = diversity_dict.get(site['id'], 0)
                
                # 種数に応じて色を変更
                if show_diversity:
                    if species_count == 0:
                        color = 'gray'
                    elif species_count < 5:
                        color = 'lightblue'
                    elif species_count < 10:
                        color = 'blue'
                    elif species_count < 15:
                        color = 'orange'
                    else:
                        color = 'darkred'
                else:
                    color = 'blue'
                
                popup_html = f"""
                <b>{site['name']}</b><br>
                親調査地: {site['parent_name']}<br>
                緯度: {site['latitude']:.6f}<br>
                経度: {site['longitude']:.6f}
                """
                
                if show_diversity and species_count > 0:
                    popup_html += f"<br>種数: {species_count}"
                
                folium.CircleMarker(
                    location=[site['latitude'], site['longitude']],
                    radius=8,
                    popup=folium.Popup(popup_html, max_width=200),
                    tooltip=site['name'],
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7
                ).add_to(m)
        
        # ファイル保存
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"site_map_{timestamp}.html"
        filepath = os.path.join(self.map_dir, filename)
        
        m.save(filepath)
        
        return filepath
    
    def create_heatmap(self, metric: str = 'species_richness') -> str:
        """
        ヒートマップを作成
        
        Args:
            metric: 表示する指標 ('species_richness' or 'shannon_index')
            
        Returns:
            str: 生成されたHTMLファイルのパス
        """
        m = self.create_base_map()
        
        # データ取得
        if metric == 'species_richness':
            sql = """
                SELECT 
                    ss.latitude,
                    ss.longitude,
                    COUNT(DISTINCT ar.species_id) as value
                FROM survey_sites ss
                LEFT JOIN survey_events se ON ss.id = se.survey_site_id
                LEFT JOIN ant_records ar ON se.id = ar.survey_event_id
                WHERE ss.deleted_at IS NULL
                GROUP BY ss.id
                HAVING value > 0
            """
        else:
            # Shannon指数を計算して取得（簡易版）
            sql = """
                SELECT 
                    ss.latitude,
                    ss.longitude,
                    COUNT(DISTINCT ar.species_id) as value
                FROM survey_sites ss
                LEFT JOIN survey_events se ON ss.id = se.survey_site_id
                LEFT JOIN ant_records ar ON se.id = ar.survey_event_id
                WHERE ss.deleted_at IS NULL
                GROUP BY ss.id
                HAVING value > 0
            """
        
        df = pd.read_sql_query(sql, self.conn)
        
        if df.empty:
            raise ValueError("ヒートマップ用のデータがありません")
        
        # ヒートマップデータ準備
        heat_data = [[row['latitude'], row['longitude'], row['value']] 
                    for _, row in df.iterrows()]
        
        # ヒートマップ追加
        plugins.HeatMap(
            heat_data,
            name='種多様度ヒートマップ',
            radius=25,
            blur=35,
            max_zoom=13,
            gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1.0: 'red'}
        ).add_to(m)
        
        # レイヤーコントロール追加
        folium.LayerControl().add_to(m)
        
        # 保存
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"heatmap_{metric}_{timestamp}.html"
        filepath = os.path.join(self.map_dir, filename)
        
        m.save(filepath)
        
        return filepath
    
    def perform_kmeans_clustering(self, n_clusters: int = 3,
                                  site_type: str = 'survey') -> Dict[str, Any]:
        """
        K-Meansクラスタリングを実行
        
        Args:
            n_clusters: クラスタ数
            site_type: 'survey' or 'parent'
            
        Returns:
            Dict: クラスタリング結果
        """
        if site_type == 'parent':
            sql = """
                SELECT id, name, latitude, longitude
                FROM parent_sites
                WHERE deleted_at IS NULL
            """
        else:
            sql = """
                SELECT ss.id, ss.name, ss.latitude, ss.longitude
                FROM survey_sites ss
                WHERE ss.deleted_at IS NULL
            """
        
        df = pd.read_sql_query(sql, self.conn)
        
        if len(df) < n_clusters:
            raise ValueError(f"データ数（{len(df)}）がクラスタ数（{n_clusters}）より少ないです")
        
        # 座標データ
        coords = df[['latitude', 'longitude']].values
        
        # K-Meansクラスタリング
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df['cluster'] = kmeans.fit_predict(coords)
        
        # クラスタ中心
        centers = kmeans.cluster_centers_
        
        return {
            'data': df,
            'centers': centers,
            'n_clusters': n_clusters,
            'inertia': kmeans.inertia_
        }
    
    def create_cluster_map(self, n_clusters: int = 3,
                          method: str = 'kmeans',
                          site_type: str = 'survey') -> str:
        """
        クラスタリング結果を地図に表示
        
        Args:
            n_clusters: クラスタ数
            method: 'kmeans' or 'dbscan'
            site_type: 'survey' or 'parent'
            
        Returns:
            str: 生成されたHTMLファイルのパス
        """
        # クラスタリング実行
        if method == 'kmeans':
            result = self.perform_kmeans_clustering(n_clusters, site_type)
            df = result['data']
            centers = result['centers']
        else:
            # DBSCAN（今後実装）
            raise NotImplementedError("DBSCANは今後実装予定です")
        
        # 地図作成
        m = self.create_base_map()
        
        # 色リスト
        colors = ['red', 'blue', 'green', 'purple', 'orange', 
                 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen']
        
        # 各クラスタの地点をプロット
        for cluster_id in range(n_clusters):
            cluster_data = df[df['cluster'] == cluster_id]
            color = colors[cluster_id % len(colors)]
            
            for _, site in cluster_data.iterrows():
                folium.CircleMarker(
                    location=[site['latitude'], site['longitude']],
                    radius=8,
                    popup=f"<b>{site['name']}</b><br>クラスタ {cluster_id + 1}",
                    tooltip=f"{site['name']} (クラスタ {cluster_id + 1})",
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7
                ).add_to(m)
            
            # クラスタ中心を表示
            folium.Marker(
                location=[centers[cluster_id][0], centers[cluster_id][1]],
                popup=f"クラスタ {cluster_id + 1} 中心",
                icon=folium.Icon(color=color, icon='star', prefix='fa')
            ).add_to(m)
        
        # 保存
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"cluster_map_{n_clusters}clusters_{timestamp}.html"
        filepath = os.path.join(self.map_dir, filename)
        
        m.save(filepath)
        
        return filepath
    
    def create_dendrogram(self, site_type: str = 'survey',
                         method: str = 'ward') -> plt.Figure:
        """
        階層的クラスタリングの樹形図を作成
        
        Args:
            site_type: 'survey' or 'parent'
            method: 'ward', 'single', 'complete', 'average'
            
        Returns:
            Figure: matplotlibのFigureオブジェクト
        """
        # 距離行列を取得
        dist_df = self.get_distance_matrix(site_type)
        
        if dist_df.empty:
            raise ValueError("データがありません")
        
        # 階層的クラスタリング
        condensed_dist = squareform(dist_df.values)
        linkage_matrix = linkage(condensed_dist, method=method)
        
        # 樹形図作成
        fig, ax = plt.subplots(figsize=(12, 8))
        
        dendrogram(
            linkage_matrix,
            labels=dist_df.index.tolist(),
            ax=ax,
            orientation='right',
            leaf_font_size=10
        )
        
        ax.set_xlabel('距離 (km)', fontsize=12)
        ax.set_title(f'階層的クラスタリング樹形図 ({method}法)', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        return fig
    
    def open_map_in_browser(self, filepath: str):
        """
        地図をブラウザで開く
        
        Args:
            filepath: HTMLファイルのパス
        """
        abs_path = os.path.abspath(filepath)
        webbrowser.open('file://' + abs_path)