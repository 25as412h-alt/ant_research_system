"""
データ閲覧タブ
"""
import tkinter as tk
from tkinter import ttk
from models.parent_site import ParentSite
from models.survey_site import SurveySite


class ViewTab:
    """データ閲覧タブクラス"""
    
    def __init__(self, parent, db_connection):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            db_connection: データベース接続
        """
        self.conn = db_connection
        self.parent_site_model = ParentSite(db_connection)
        self.survey_site_model = SurveySite(db_connection)
        
        # メインフレーム
        self.frame = ttk.Frame(parent)
        
        # サブタブを作成
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 親調査地一覧タブ
        self._create_parent_site_tab()
        
        # 調査地一覧タブ
        self._create_survey_site_tab()
        
        # 調査イベント一覧タブ（Phase 2で実装）
        event_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(event_frame, text='調査イベント')
        ttk.Label(event_frame, text='Phase 2 で実装予定',
                 font=('Yu Gothic UI', 12)).pack(pady=50)
        
        # アリ類出現記録タブ（Phase 2で実装）
        ant_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(ant_frame, text='アリ類出現記録')
        ttk.Label(ant_frame, text='Phase 2 で実装予定',
                 font=('Yu Gothic UI', 12)).pack(pady=50)
    
    def _create_parent_site_tab(self):
        """親調査地一覧タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='親調査地一覧')
        
        # ツールバー
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(toolbar, text='検索:', 
                 style='Header.TLabel').pack(side='left', padx=5)
        
        self.ps_search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.ps_search_var, width=30)
        search_entry.pack(side='left', padx=5)
        
        ttk.Button(toolbar, text='🔍 検索', 
                  command=self._search_parent_sites).pack(side='left', padx=5)
        ttk.Button(toolbar, text='🔄 更新', 
                  command=self._refresh_parent_sites).pack(side='left', padx=5)
        
        # 統計情報
        self.ps_stats_label = ttk.Label(toolbar, text='')
        self.ps_stats_label.pack(side='right', padx=10)
        
        # Treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # スクロールバー
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # ツリービュー
        self.ps_view_tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'name', 'latitude', 'longitude', 'altitude', 
                    'site_count', 'remarks'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.ps_view_tree.yview)
        h_scrollbar.config(command=self.ps_view_tree.xview)
        
        # 列設定
        columns_config = {
            'id': ('ID', 60),
            'name': ('名称', 200),
            'latitude': ('緯度', 100),
            'longitude': ('経度', 100),
            'altitude': ('標高(m)', 100),
            'site_count': ('調査地数', 100),
            'remarks': ('備考', 300)
        }
        
        for col, (heading, width) in columns_config.items():
            self.ps_view_tree.heading(col, text=heading)
            self.ps_view_tree.column(col, width=width)
        
        self.ps_view_tree.pack(fill='both', expand=True)
        
        # ダブルクリックで詳細表示
        self.ps_view_tree.bind('<Double-1>', self._show_parent_site_detail)
        
        # データ読み込み
        self._refresh_parent_sites()
    
    def _create_survey_site_tab(self):
        """調査地一覧タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='調査地一覧')
        
        # ツールバー
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(toolbar, text='親調査地:', 
                 style='Header.TLabel').pack(side='left', padx=5)
        
        self.ss_filter_var = tk.StringVar()
        self.ss_filter_var.set('全て')
        self.ss_filter_combo = ttk.Combobox(toolbar, 
                                           textvariable=self.ss_filter_var,
                                           state='readonly',
                                           width=25)
        self.ss_filter_combo.pack(side='left', padx=5)
        self.ss_filter_combo.bind('<<ComboboxSelected>>', 
                                 lambda e: self._refresh_survey_sites())
        
        ttk.Label(toolbar, text='検索:').pack(side='left', padx=(20, 5))
        
        self.ss_search_var = tk.StringVar()
        ttk.Entry(toolbar, textvariable=self.ss_search_var, width=30).pack(
            side='left', padx=5)
        
        ttk.Button(toolbar, text='🔍 検索', 
                  command=self._search_survey_sites).pack(side='left', padx=5)
        ttk.Button(toolbar, text='🔄 更新', 
                  command=self._refresh_survey_sites).pack(side='left', padx=5)
        
        # 統計情報
        self.ss_stats_label = ttk.Label(toolbar, text='')
        self.ss_stats_label.pack(side='right', padx=10)
        
        # Treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        self.ss_view_tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'parent_name', 'name', 'latitude', 'longitude', 
                    'altitude', 'area', 'remarks'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        v_scrollbar.config(command=self.ss_view_tree.yview)
        h_scrollbar.config(command=self.ss_view_tree.xview)
        
        columns_config = {
            'id': ('ID', 60),
            'parent_name': ('親調査地', 150),
            'name': ('名称', 150),
            'latitude': ('緯度', 100),
            'longitude': ('経度', 100),
            'altitude': ('標高(m)', 80),
            'area': ('面積(㎡)', 80),
            'remarks': ('備考', 200)
        }
        
        for col, (heading, width) in columns_config.items():
            self.ss_view_tree.heading(col, text=heading)
            self.ss_view_tree.column(col, width=width)
        
        self.ss_view_tree.pack(fill='both', expand=True)
        
        # 親調査地フィルタの更新
        self._update_parent_site_filter()
        
        # データ読み込み
        self._refresh_survey_sites()
    
    def _refresh_parent_sites(self):
        """親調査地一覧を更新"""
        # 既存のアイテムをクリア
        for item in self.ps_view_tree.get_children():
            self.ps_view_tree.delete(item)
        
        # データを取得
        sites = self.parent_site_model.get_with_site_count()
        
        for site in sites:
            self.ps_view_tree.insert('', 'end', values=(
                site['id'],
                site['name'],
                f"{site['latitude']:.6f}",
                f"{site['longitude']:.6f}",
                site['altitude'] if site['altitude'] else '',
                site['site_count'],
                site['remarks'] if site['remarks'] else ''
            ))
        
        # 統計情報を更新
        self.ps_stats_label.config(
            text=f'親調査地: {len(sites)}件'
        )
    
    def _refresh_survey_sites(self):
        """調査地一覧を更新"""
        for item in self.ss_view_tree.get_children():
            self.ss_view_tree.delete(item)
        
        # フィルタ条件
        filter_value = self.ss_filter_var.get()
        parent_site_id = None
        
        if filter_value != '全て':
            # 親調査地IDを取得
            for name, site_id in self.parent_site_dict.items():
                if name == filter_value:
                    parent_site_id = site_id
                    break
        
        # データを取得
        sites = self.survey_site_model.get_all(parent_site_id=parent_site_id)
        
        for site in sites:
            self.ss_view_tree.insert('', 'end', values=(
                site['id'],
                site['parent_site_name'],
                site['name'],
                f"{site['latitude']:.6f}",
                f"{site['longitude']:.6f}",
                site['altitude'] if site['altitude'] else '',
                site['area'] if site['area'] else '',
                site['remarks'] if site['remarks'] else ''
            ))
        
        self.ss_stats_label.config(
            text=f'調査地: {len(sites)}件'
        )
    
    def _search_parent_sites(self):
        """親調査地を検索"""
        keyword = self.ps_search_var.get().strip()
        
        if not keyword:
            self._refresh_parent_sites()
            return
        
        for item in self.ps_view_tree.get_children():
            self.ps_view_tree.delete(item)
        
        sites = self.parent_site_model.search(keyword)
        
        for site in sites:
            # 調査地数を取得
            site_count = self.survey_site_model.count_by_parent_site(site['id'])
            
            self.ps_view_tree.insert('', 'end', values=(
                site['id'],
                site['name'],
                f"{site['latitude']:.6f}",
                f"{site['longitude']:.6f}",
                site['altitude'] if site['altitude'] else '',
                site_count,
                site['remarks'] if site['remarks'] else ''
            ))
        
        self.ps_stats_label.config(
            text=f'検索結果: {len(sites)}件'
        )
    
    def _search_survey_sites(self):
        """調査地を検索"""
        keyword = self.ss_search_var.get().strip()
        
        if not keyword:
            self._refresh_survey_sites()
            return
        
        for item in self.ss_view_tree.get_children():
            self.ss_view_tree.delete(item)
        
        sites = self.survey_site_model.search(keyword)
        
        for site in sites:
            self.ss_view_tree.insert('', 'end', values=(
                site['id'],
                site['parent_site_name'],
                site['name'],
                f"{site['latitude']:.6f}",
                f"{site['longitude']:.6f}",
                site['altitude'] if site['altitude'] else '',
                site['area'] if site['area'] else '',
                site['remarks'] if site['remarks'] else ''
            ))
        
        self.ss_stats_label.config(
            text=f'検索結果: {len(sites)}件'
        )
    
    def _update_parent_site_filter(self):
        """親調査地フィルタを更新"""
        sites = self.parent_site_model.get_all()
        self.parent_site_dict = {site['name']: site['id'] for site in sites}
        
        values = ['全て'] + list(self.parent_site_dict.keys())
        self.ss_filter_combo['values'] = values
    
    def _show_parent_site_detail(self, event):
        """親調査地の詳細を表示（今後実装）"""
        selection = self.ps_view_tree.selection()
        if selection:
            # 今後、詳細ウィンドウを実装
            pass
