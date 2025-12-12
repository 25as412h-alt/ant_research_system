"""
データ閲覧タブ
"""
import tkinter as tk
from tkinter import ttk
from models.parent_site import ParentSite
from models.survey_site import SurveySite
from models.survey_event import SurveyEvent
from models.ant_record import AntRecord


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
        self.survey_event_model = SurveyEvent(db_connection)
        self.ant_record_model = AntRecord(db_connection)
        
        # メインフレーム
        self.frame = ttk.Frame(parent)
        
        # サブタブを作成
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 親調査地一覧タブ
        self._create_parent_site_tab()
        
        # 調査地一覧タブ
        self._create_survey_site_tab()
        
        # 調査イベント一覧タブ
        self._create_survey_event_tab()
        
        # アリ類出現記録タブ
        self._create_ant_record_tab()
    
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
    
    def _create_survey_event_tab(self):
        """調査イベント一覧タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='調査イベント')
        
        # ツールバー
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(toolbar, text='期間:', style='Header.TLabel').pack(side='left', padx=5)
        
        # 日付フィルタは簡略化
        ttk.Button(toolbar, text='🔄 更新', 
                  command=self._refresh_events).pack(side='left', padx=5)
        
        self.event_stats_label = ttk.Label(toolbar, text='')
        self.event_stats_label.pack(side='right', padx=10)
        
        # Treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        self.event_tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'date', 'parent_site', 'site', 'surveyor', 'weather', 'temp'),
            show='headings',
            yscrollcommand=v_scrollbar.set
        )
        
        v_scrollbar.config(command=self.event_tree.yview)
        
        columns_config = {
            'id': ('ID', 50),
            'date': ('調査日時', 150),
            'parent_site': ('親調査地', 150),
            'site': ('調査地', 150),
            'surveyor': ('調査者', 100),
            'weather': ('天候', 80),
            'temp': ('気温(℃)', 80)
        }
        
        for col, (heading, width) in columns_config.items():
            self.event_tree.heading(col, text=heading)
            self.event_tree.column(col, width=width)
        
        self.event_tree.pack(fill='both', expand=True)
        
        self._refresh_events()
    
    def _create_ant_record_tab(self):
        """アリ類出現記録タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='アリ類出現記録')
        
        # ツールバー
        toolbar = ttk.Frame(tab)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(toolbar, text='🔄 更新', 
                  command=self._refresh_ant_records).pack(side='left', padx=5)
        ttk.Button(toolbar, text='📊 種別統計', 
                  command=self._show_species_stats).pack(side='left', padx=5)
        
        self.ant_stats_label = ttk.Label(toolbar, text='')
        self.ant_stats_label.pack(side='right', padx=10)
        
        # Treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        v_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical')
        v_scrollbar.pack(side='right', fill='y')
        
        self.ant_tree = ttk.Treeview(
            tree_frame,
            columns=('id', 'date', 'site', 'species', 'genus', 'count'),
            show='headings',
            yscrollcommand=v_scrollbar.set
        )
        
        v_scrollbar.config(command=self.ant_tree.yview)
        
        columns_config = {
            'id': ('ID', 50),
            'date': ('調査日', 100),
            'site': ('調査地', 200),
            'species': ('種名', 200),
            'genus': ('属', 120),
            'count': ('個体数', 80)
        }
        
        for col, (heading, width) in columns_config.items():
            self.ant_tree.heading(col, text=heading)
            self.ant_tree.column(col, width=width)
        
        self.ant_tree.pack(fill='both', expand=True)
        
        self._refresh_ant_records()
    
    def _refresh_events(self):
        """調査イベント一覧を更新"""
        for item in self.event_tree.get_children():
            self.event_tree.delete(item)
        
        events = self.survey_event_model.get_all()
        
        for event in events:
            self.event_tree.insert('', 'end', values=(
                event['id'],
                event['survey_date'],
                event['parent_site_name'],
                event['site_name'],
                event['surveyor_name'] or '',
                event['weather'] or '',
                event['temperature'] if event['temperature'] else ''
            ))
        
        self.event_stats_label.config(text=f'調査イベント: {len(events)}件')
    
    def _refresh_ant_records(self):
        """アリ類出現記録を更新"""
        for item in self.ant_tree.get_children():
            self.ant_tree.delete(item)
        
        records = self.ant_record_model.get_all()
        
        for record in records:
            self.ant_tree.insert('', 'end', values=(
                record['id'],
                record['survey_date'][:10],  # 日付のみ
                record['site_name'],
                record['species_name'],
                record.get('genus', ''),
                record['count']
            ))
        
        total_records = len(records)
        total_individuals = sum(r['count'] for r in records)
        self.ant_stats_label.config(
            text=f'記録: {total_records}件  総個体数: {total_individuals}'
        )
    
    def _show_species_stats(self):
        """種別統計を表示"""
        from tkinter import messagebox
        
        stats = self.ant_record_model.get_species_frequency()
        
        if not stats:
            messagebox.showinfo('情報', '出現記録がありません')
            return
        
        # 新しいウィンドウで表示
        stats_window = tk.Toplevel()
        stats_window.title('種別出現統計')
        stats_window.geometry('700x500')
        
        ttk.Label(stats_window, text='種別出現統計', 
                 font=('Yu Gothic UI', 14, 'bold')).pack(pady=10)
        
        tree_frame = ttk.Frame(stats_window)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        stats_tree = ttk.Treeview(
            tree_frame,
            columns=('species', 'genus', 'sites', 'occurrences', 'total', 'avg'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=stats_tree.yview)
        
        stats_tree.heading('species', text='種名')
        stats_tree.heading('genus', text='属')
        stats_tree.heading('sites', text='出現地点数')
        stats_tree.heading('occurrences', text='出現回数')
        stats_tree.heading('total', text='総個体数')
        stats_tree.heading('avg', text='平均個体数')
        
        stats_tree.column('species', width=180)
        stats_tree.column('genus', width=100)
        stats_tree.column('sites', width=100)
        stats_tree.column('occurrences', width=100)
        stats_tree.column('total', width=100)
        stats_tree.column('avg', width=100)
        
        for stat in stats:
            stats_tree.insert('', 'end', values=(
                stat['species_name'],
                stat['genus'] or '',
                stat['site_count'],
                stat['occurrence_count'],
                stat['total_count'],
                f"{stat['avg_count']:.1f}"
            ))
        
        stats_tree.pack(fill='both', expand=True)
        
        ttk.Button(stats_window, text='閉じる', 
                  command=stats_window.destroy).pack(pady=10)