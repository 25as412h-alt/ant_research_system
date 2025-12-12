"""
地図・クラスタ解析タブ
"""
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from controllers.map_controller import MapController
import pandas as pd


class MapTab:
    """地図・クラスタ解析タブクラス"""
    
    def __init__(self, parent, db_connection):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            db_connection: データベース接続
        """
        self.conn = db_connection
        self.map_controller = MapController(db_connection)
        
        # メインフレーム
        self.frame = ttk.Frame(parent)
        
        # サブタブを作成
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 各サブタブ
        self._create_map_display_tab()
        self._create_cluster_tab()
        self._create_distance_tab()
    
    def _create_map_display_tab(self):
        """地図表示タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='地図表示')
        
        # 左側：設定
        left_frame = ttk.Frame(tab)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        ttk.Label(left_frame, text='地図表示設定', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # 表示オプション
        options_frame = ttk.LabelFrame(left_frame, text='表示オプション', padding=10)
        options_frame.pack(fill='x', pady=10)
        
        self.show_parent = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text='親調査地を表示', 
                       variable=self.show_parent).pack(anchor='w', pady=5)
        
        self.show_survey = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text='調査地を表示', 
                       variable=self.show_survey).pack(anchor='w', pady=5)
        
        self.show_diversity = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text='種多様度で色分け', 
                       variable=self.show_diversity).pack(anchor='w', pady=5)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # 地図生成ボタン
        ttk.Button(left_frame, text='🗺️ 地図を生成', 
                  command=self._create_map,
                  style='Accent.TButton').pack(pady=10)
        
        ttk.Button(left_frame, text='🔥 ヒートマップを生成', 
                  command=self._create_heatmap).pack(pady=5)
        
        # 説明
        info_frame = ttk.LabelFrame(left_frame, text='凡例', padding=10)
        info_frame.pack(fill='x', pady=10)
        
        info_text = """
🏠 赤マーカー: 親調査地
🔵 青マーカー: 調査地

種多様度で色分け:
• 灰色: データなし
• 水色: 1-4種
• 青: 5-9種
• 橙: 10-14種
• 濃赤: 15種以上
        """
        
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')
        
        # 右側：情報表示
        right_frame = ttk.Frame(tab)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_frame, text='地図情報', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        info_text = tk.Text(right_frame, height=20, width=60, wrap='word')
        info_text.pack(fill='both', expand=True)
        
        info_content = """
地図表示機能の使い方:

1. 表示したい項目をチェック
2. 「地図を生成」ボタンをクリック
3. 生成された地図がブラウザで自動的に開きます

地図の操作:
• ズーム: マウスホイール or +/- ボタン
• 移動: ドラッグ
• マーカークリック: 詳細情報を表示

ヒートマップ:
種多様度の空間分布を色の濃淡で表現します。
赤い地域ほど多様度が高いことを示します。

注意:
• インターネット接続が必要です
• 地図タイルはOpenStreetMapを使用
        """
        
        info_text.insert('1.0', info_content)
        info_text.config(state='disabled')
    
    def _create_cluster_tab(self):
        """クラスタ解析タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='クラスタ解析')
        
        # 左側：設定
        left_frame = ttk.Frame(tab)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        ttk.Label(left_frame, text='クラスタ解析', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # 解析設定
        settings_frame = ttk.LabelFrame(left_frame, text='解析設定', padding=10)
        settings_frame.pack(fill='x', pady=10)
        
        # 対象選択
        ttk.Label(settings_frame, text='対象:').pack(anchor='w', pady=2)
        self.cluster_target = tk.StringVar(value='survey')
        ttk.Radiobutton(settings_frame, text='調査地', 
                       variable=self.cluster_target, 
                       value='survey').pack(anchor='w', padx=20)
        ttk.Radiobutton(settings_frame, text='親調査地', 
                       variable=self.cluster_target, 
                       value='parent').pack(anchor='w', padx=20, pady=5)
        
        # クラスタ数
        ttk.Label(settings_frame, text='クラスタ数:').pack(anchor='w', pady=(10, 2))
        self.n_clusters = tk.IntVar(value=3)
        ttk.Spinbox(settings_frame, from_=2, to=10, 
                   textvariable=self.n_clusters, width=10).pack(anchor='w', pady=2)
        
        # 手法選択
        ttk.Label(settings_frame, text='手法:').pack(anchor='w', pady=(10, 2))
        self.cluster_method = tk.StringVar(value='kmeans')
        ttk.Radiobutton(settings_frame, text='K-Means法', 
                       variable=self.cluster_method, 
                       value='kmeans').pack(anchor='w', padx=20)
        ttk.Radiobutton(settings_frame, text='階層的クラスタリング', 
                       variable=self.cluster_method, 
                       value='hierarchical').pack(anchor='w', padx=20, pady=5)
        
        ttk.Separator(left_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # 実行ボタン
        ttk.Button(left_frame, text='クラスタリング実行', 
                  command=self._perform_clustering).pack(pady=10)
        
        ttk.Button(left_frame, text='樹形図を表示', 
                  command=self._show_dendrogram).pack(pady=5)
        
        ttk.Button(left_frame, text='クラスタ地図を生成', 
                  command=self._create_cluster_map).pack(pady=5)
        
        # 説明
        info_frame = ttk.LabelFrame(left_frame, text='説明', padding=10)
        info_frame.pack(fill='x', pady=10)
        
        info_text = """
K-Means法:
地点を指定した数のグループに
分類します。各グループは地理
的に近い地点で構成されます。

階層的クラスタリング:
地点間の距離に基づいて段階的
にグループ化します。樹形図で
関係性を可視化できます。
        """
        
        ttk.Label(info_frame, text=info_text, justify='left').pack(anchor='w')
        
        # 右側：結果表示
        right_frame = ttk.Frame(tab)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_frame, text='クラスタリング結果', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Treeview
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.cluster_tree = ttk.Treeview(
            tree_frame,
            columns=('site', 'cluster', 'lat', 'lon'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.cluster_tree.yview)
        
        self.cluster_tree.heading('site', text='地点名')
        self.cluster_tree.heading('cluster', text='クラスタ')
        self.cluster_tree.heading('lat', text='緯度')
        self.cluster_tree.heading('lon', text='経度')
        
        self.cluster_tree.column('site', width=200)
        self.cluster_tree.column('cluster', width=100)
        self.cluster_tree.column('lat', width=100)
        self.cluster_tree.column('lon', width=100)
        
        self.cluster_tree.pack(fill='both', expand=True)
        
        # 統計情報
        self.cluster_stats_label = ttk.Label(right_frame, text='', 
                                            font=('Yu Gothic UI', 10))
        self.cluster_stats_label.pack(pady=10)
    
    def _create_distance_tab(self):
        """距離行列タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='距離行列')
        
        # 上部：設定
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(top_frame, text='距離行列の計算', 
                 style='Header.TLabel').pack(side='left')
        
        ttk.Label(top_frame, text='対象:').pack(side='left', padx=(20, 5))
        self.distance_target = tk.StringVar(value='survey')
        ttk.Radiobutton(top_frame, text='調査地', 
                       variable=self.distance_target, 
                       value='survey').pack(side='left')
        ttk.Radiobutton(top_frame, text='親調査地', 
                       variable=self.distance_target, 
                       value='parent').pack(side='left', padx=10)
        
        ttk.Button(top_frame, text='距離を計算', 
                  command=self._calculate_distance).pack(side='left', padx=10)
        
        ttk.Button(top_frame, text='CSVに出力', 
                  command=self._export_distance_matrix).pack(side='left', padx=5)
        
        # 下部：結果表示
        bottom_frame = ttk.Frame(tab)
        bottom_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # スクロール可能なテキスト
        text_frame = ttk.Frame(bottom_frame)
        text_frame.pack(fill='both', expand=True)
        
        h_scrollbar = ttk.Scrollbar(text_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        v_scrollbar = ttk.Scrollbar(text_frame)
        v_scrollbar.pack(side='right', fill='y')
        
        self.distance_text = tk.Text(
            text_frame,
            wrap='none',
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set,
            font=('Courier', 9)
        )
        self.distance_text.pack(fill='both', expand=True)
        
        h_scrollbar.config(command=self.distance_text.xview)
        v_scrollbar.config(command=self.distance_text.yview)
    
    # 地図表示関連メソッド
    def _create_map(self):
        """地図を生成"""
        try:
            filepath = self.map_controller.create_site_map(
                show_parent=self.show_parent.get(),
                show_survey=self.show_survey.get(),
                show_diversity=self.show_diversity.get()
            )
            
            self.map_controller.open_map_in_browser(filepath)
            
            messagebox.showinfo('成功', 
                f'地図を生成しました\n\nブラウザで開いています...\n\n{filepath}')
            
        except Exception as e:
            messagebox.showerror('エラー', f'地図の生成に失敗しました：{e}')
    
    def _create_heatmap(self):
        """ヒートマップを生成"""
        try:
            filepath = self.map_controller.create_heatmap('species_richness')
            
            self.map_controller.open_map_in_browser(filepath)
            
            messagebox.showinfo('成功', 
                f'ヒートマップを生成しました\n\nブラウザで開いています...\n\n{filepath}')
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'ヒートマップの生成に失敗しました：{e}')
    
    # クラスタ解析関連メソッド
    def _perform_clustering(self):
        """クラスタリングを実行"""
        try:
            n_clusters = self.n_clusters.get()
            target = self.cluster_target.get()
            
            result = self.map_controller.perform_kmeans_clustering(
                n_clusters=n_clusters,
                site_type=target
            )
            
            df = result['data']
            
            # Treeviewに表示
            for item in self.cluster_tree.get_children():
                self.cluster_tree.delete(item)
            
            for _, row in df.iterrows():
                self.cluster_tree.insert('', 'end', values=(
                    row['name'],
                    f"クラスタ {row['cluster'] + 1}",
                    f"{row['latitude']:.6f}",
                    f"{row['longitude']:.6f}"
                ))
            
            # 統計情報
            self.cluster_stats_label.config(
                text=f"クラスタ数: {n_clusters}  地点数: {len(df)}  "
                     f"Inertia: {result['inertia']:.2f}"
            )
            
            messagebox.showinfo('成功', 
                f'{len(df)}地点を{n_clusters}個のクラスタに分類しました')
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'クラスタリングに失敗しました：{e}')
    
    def _show_dendrogram(self):
        """樹形図を表示"""
        try:
            target = self.cluster_target.get()
            
            fig = self.map_controller.create_dendrogram(
                site_type=target,
                method='ward'
            )
            
            plt.show()
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'樹形図の作成に失敗しました：{e}')
    
    def _create_cluster_map(self):
        """クラスタ地図を生成"""
        try:
            n_clusters = self.n_clusters.get()
            target = self.cluster_target.get()
            
            filepath = self.map_controller.create_cluster_map(
                n_clusters=n_clusters,
                method='kmeans',
                site_type=target
            )
            
            self.map_controller.open_map_in_browser(filepath)
            
            messagebox.showinfo('成功', 
                f'クラスタ地図を生成しました\n\nブラウザで開いています...\n\n{filepath}')
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'地図の生成に失敗しました：{e}')
    
    # 距離行列関連メソッド
    def _calculate_distance(self):
        """距離行列を計算"""
        try:
            target = self.distance_target.get()
            
            dist_df = self.map_controller.get_distance_matrix(target)
            
            # テキストに表示
            self.distance_text.delete('1.0', 'end')
            
            # ヘッダー
            header = "地点間の距離 (km)\n" + "="*80 + "\n\n"
            self.distance_text.insert('end', header)
            
            # 距離行列を文字列化
            dist_str = dist_df.to_string()
            self.distance_text.insert('end', dist_str)
            
            # 統計情報
            stats = f"\n\n統計情報:\n"
            stats += f"地点数: {len(dist_df)}\n"
            stats += f"最小距離: {dist_df.values[dist_df.values > 0].min():.2f} km\n"
            stats += f"最大距離: {dist_df.values.max():.2f} km\n"
            stats += f"平均距離: {dist_df.values[dist_df.values > 0].mean():.2f} km\n"
            
            self.distance_text.insert('end', stats)
            
            messagebox.showinfo('成功', '距離行列を計算しました')
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'計算に失敗しました：{e}')
    
    def _export_distance_matrix(self):
        """距離行列をCSV出力"""
        try:
            target = self.distance_target.get()
            
            dist_df = self.map_controller.get_distance_matrix(target)
            
            from datetime import datetime
            import os
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"distance_matrix_{target}_{timestamp}.csv"
            filepath = os.path.join('exports', filename)
            
            dist_df.to_csv(filepath, encoding='utf-8-sig')
            
            messagebox.showinfo('成功', 
                f'距離行列を出力しました\n\n{filepath}')
            
        except Exception as e:
            messagebox.showerror('エラー', f'出力に失敗しました：{e}')