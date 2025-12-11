"""
データ入力タブ
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.parent_site import ParentSite
from models.survey_site import SurveySite


class InputTab:
    """データ入力タブクラス"""
    
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
        
        # 親調査地入力タブ
        self._create_parent_site_tab()
        
        # 調査地入力タブ
        self._create_survey_site_tab()
        
        # 調査イベント入力タブ（Phase 2で実装）
        event_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(event_frame, text='調査イベント')
        ttk.Label(event_frame, text='Phase 2 で実装予定').pack(pady=50)
        
        # 植生データ入力タブ（Phase 2で実装）
        veg_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(veg_frame, text='植生データ')
        ttk.Label(veg_frame, text='Phase 2 で実装予定').pack(pady=50)
        
        # アリ類データ入力タブ（Phase 2で実装）
        ant_frame = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(ant_frame, text='アリ類データ')
        ttk.Label(ant_frame, text='Phase 2 で実装予定').pack(pady=50)
    
    def _create_parent_site_tab(self):
        """親調査地入力タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='親調査地')
        
        # 左側：入力フォーム
        left_frame = ttk.Frame(tab)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # タイトル
        ttk.Label(left_frame, text='親調査地の登録', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # 入力フォーム
        form_frame = ttk.Frame(left_frame)
        form_frame.pack(fill='x', pady=5)
        
        # 名称（必須）
        ttk.Label(form_frame, text='名称 *').grid(row=0, column=0, sticky='w', pady=5)
        self.ps_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ps_name_var, width=40).grid(
            row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # 緯度（必須）
        ttk.Label(form_frame, text='緯度 *').grid(row=1, column=0, sticky='w', pady=5)
        self.ps_lat_var = tk.StringVar()
        lat_entry = ttk.Entry(form_frame, textvariable=self.ps_lat_var, width=20)
        lat_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        ttk.Label(form_frame, text='（-90 ~ 90）', 
                 foreground='gray').grid(row=1, column=2, sticky='w')
        
        # 経度（必須）
        ttk.Label(form_frame, text='経度 *').grid(row=2, column=0, sticky='w', pady=5)
        self.ps_lon_var = tk.StringVar()
        lon_entry = ttk.Entry(form_frame, textvariable=self.ps_lon_var, width=20)
        lon_entry.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        ttk.Label(form_frame, text='（-180 ~ 180）', 
                 foreground='gray').grid(row=2, column=2, sticky='w')
        
        # 標高（任意）
        ttk.Label(form_frame, text='標高 (m)').grid(row=3, column=0, sticky='w', pady=5)
        self.ps_alt_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ps_alt_var, width=20).grid(
            row=3, column=1, sticky='w', padx=5, pady=5)
        
        # 備考（任意）
        ttk.Label(form_frame, text='備考').grid(row=4, column=0, sticky='nw', pady=5)
        self.ps_remarks_text = tk.Text(form_frame, width=40, height=4, wrap='word')
        self.ps_remarks_text.grid(row=4, column=1, columnspan=2, 
                                  sticky='ew', padx=5, pady=5)
        
        # 列の幅調整
        form_frame.columnconfigure(1, weight=1)
        
        # ボタンフレーム
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text='登録', 
                  command=self._save_parent_site).pack(side='left', padx=5)
        ttk.Button(button_frame, text='クリア', 
                  command=self._clear_parent_site_form).pack(side='left', padx=5)
        
        # 右側：登録済みリスト
        right_frame = ttk.Frame(tab)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_frame, text='登録済み親調査地', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Treeview
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        # ツリービュー
        self.ps_tree = ttk.Treeview(tree_frame, 
                                   columns=('id', 'name', 'lat', 'lon', 'alt'),
                                   show='headings',
                                   yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.ps_tree.yview)
        
        # 列設定
        self.ps_tree.heading('id', text='ID')
        self.ps_tree.heading('name', text='名称')
        self.ps_tree.heading('lat', text='緯度')
        self.ps_tree.heading('lon', text='経度')
        self.ps_tree.heading('alt', text='標高')
        
        self.ps_tree.column('id', width=50)
        self.ps_tree.column('name', width=200)
        self.ps_tree.column('lat', width=100)
        self.ps_tree.column('lon', width=100)
        self.ps_tree.column('alt', width=80)
        
        self.ps_tree.pack(fill='both', expand=True)
        
        # ダブルクリックで編集
        self.ps_tree.bind('<Double-1>', self._on_parent_site_double_click)
        
        # リスト更新
        self._refresh_parent_site_list()
    
    def _create_survey_site_tab(self):
        """調査地入力タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='調査地')
        
        # 左側：入力フォーム
        left_frame = ttk.Frame(tab)
        left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(left_frame, text='調査地の登録', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        form_frame = ttk.Frame(left_frame)
        form_frame.pack(fill='x', pady=5)
        
        # 親調査地選択（必須）
        ttk.Label(form_frame, text='親調査地 *').grid(row=0, column=0, sticky='w', pady=5)
        self.ss_parent_var = tk.StringVar()
        self.ss_parent_combo = ttk.Combobox(form_frame, 
                                           textvariable=self.ss_parent_var,
                                           state='readonly',
                                           width=38)
        self.ss_parent_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        self._update_parent_site_combo()
        
        # 名称（必須）
        ttk.Label(form_frame, text='名称 *').grid(row=1, column=0, sticky='w', pady=5)
        self.ss_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ss_name_var, width=40).grid(
            row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # 緯度（必須）
        ttk.Label(form_frame, text='緯度 *').grid(row=2, column=0, sticky='w', pady=5)
        self.ss_lat_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ss_lat_var, width=20).grid(
            row=2, column=1, sticky='w', padx=5, pady=5)
        
        # 経度（必須）
        ttk.Label(form_frame, text='経度 *').grid(row=3, column=0, sticky='w', pady=5)
        self.ss_lon_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ss_lon_var, width=20).grid(
            row=3, column=1, sticky='w', padx=5, pady=5)
        
        # 標高（任意）
        ttk.Label(form_frame, text='標高 (m)').grid(row=4, column=0, sticky='w', pady=5)
        self.ss_alt_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ss_alt_var, width=20).grid(
            row=4, column=1, sticky='w', padx=5, pady=5)
        
        # 面積（任意）
        ttk.Label(form_frame, text='面積 (㎡)').grid(row=5, column=0, sticky='w', pady=5)
        self.ss_area_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.ss_area_var, width=20).grid(
            row=5, column=1, sticky='w', padx=5, pady=5)
        
        # 備考（任意）
        ttk.Label(form_frame, text='備考').grid(row=6, column=0, sticky='nw', pady=5)
        self.ss_remarks_text = tk.Text(form_frame, width=40, height=4, wrap='word')
        self.ss_remarks_text.grid(row=6, column=1, columnspan=2, 
                                  sticky='ew', padx=5, pady=5)
        
        form_frame.columnconfigure(1, weight=1)
        
        # ボタン
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text='登録', 
                  command=self._save_survey_site).pack(side='left', padx=5)
        ttk.Button(button_frame, text='クリア', 
                  command=self._clear_survey_site_form).pack(side='left', padx=5)
        
        # 右側：登録済みリスト
        right_frame = ttk.Frame(tab)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_frame, text='登録済み調査地', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.ss_tree = ttk.Treeview(tree_frame,
                                   columns=('id', 'parent', 'name', 'lat', 'lon'),
                                   show='headings',
                                   yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.ss_tree.yview)
        
        self.ss_tree.heading('id', text='ID')
        self.ss_tree.heading('parent', text='親調査地')
        self.ss_tree.heading('name', text='名称')
        self.ss_tree.heading('lat', text='緯度')
        self.ss_tree.heading('lon', text='経度')
        
        self.ss_tree.column('id', width=50)
        self.ss_tree.column('parent', width=150)
        self.ss_tree.column('name', width=150)
        self.ss_tree.column('lat', width=100)
        self.ss_tree.column('lon', width=100)
        
        self.ss_tree.pack(fill='both', expand=True)
        
        self._refresh_survey_site_list()
    
    def _save_parent_site(self):
        """親調査地を保存"""
        try:
            name = self.ps_name_var.get().strip()
            lat_str = self.ps_lat_var.get().strip()
            lon_str = self.ps_lon_var.get().strip()
            alt_str = self.ps_alt_var.get().strip()
            remarks = self.ps_remarks_text.get('1.0', 'end-1c').strip()
            
            # バリデーション
            if not name:
                messagebox.showwarning('入力エラー', '名称を入力してください')
                return
            
            if not lat_str or not lon_str:
                messagebox.showwarning('入力エラー', '緯度・経度を入力してください')
                return
            
            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
            except ValueError:
                messagebox.showerror('入力エラー', '緯度・経度は数値で入力してください')
                return
            
            altitude = float(alt_str) if alt_str else None
            
            # 保存
            site_id = self.parent_site_model.create(
                name=name,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                remarks=remarks if remarks else None
            )
            
            messagebox.showinfo('成功', f'親調査地「{name}」を登録しました（ID: {site_id}）')
            self._clear_parent_site_form()
            self._refresh_parent_site_list()
            self._update_parent_site_combo()
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'予期しないエラーが発生しました：{e}')
    
    def _save_survey_site(self):
        """調査地を保存"""
        try:
            parent_name = self.ss_parent_var.get()
            name = self.ss_name_var.get().strip()
            lat_str = self.ss_lat_var.get().strip()
            lon_str = self.ss_lon_var.get().strip()
            alt_str = self.ss_alt_var.get().strip()
            area_str = self.ss_area_var.get().strip()
            remarks = self.ss_remarks_text.get('1.0', 'end-1c').strip()
            
            if not parent_name:
                messagebox.showwarning('入力エラー', '親調査地を選択してください')
                return
            
            if not name:
                messagebox.showwarning('入力エラー', '名称を入力してください')
                return
            
            if not lat_str or not lon_str:
                messagebox.showwarning('入力エラー', '緯度・経度を入力してください')
                return
            
            # 親調査地IDを取得
            parent_id = self.parent_site_dict.get(parent_name)
            if not parent_id:
                messagebox.showerror('エラー', '親調査地が見つかりません')
                return
            
            try:
                latitude = float(lat_str)
                longitude = float(lon_str)
                altitude = float(alt_str) if alt_str else None
                area = float(area_str) if area_str else None
            except ValueError:
                messagebox.showerror('入力エラー', '数値の形式が正しくありません')
                return
            
            site_id = self.survey_site_model.create(
                parent_site_id=parent_id,
                name=name,
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                area=area,
                remarks=remarks if remarks else None
            )
            
            messagebox.showinfo('成功', f'調査地「{name}」を登録しました（ID: {site_id}）')
            self._clear_survey_site_form()
            self._refresh_survey_site_list()
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'予期しないエラーが発生しました：{e}')
    
    def _clear_parent_site_form(self):
        """親調査地フォームをクリア"""
        self.ps_name_var.set('')
        self.ps_lat_var.set('')
        self.ps_lon_var.set('')
        self.ps_alt_var.set('')
        self.ps_remarks_text.delete('1.0', 'end')
    
    def _clear_survey_site_form(self):
        """調査地フォームをクリア"""
        self.ss_parent_var.set('')
        self.ss_name_var.set('')
        self.ss_lat_var.set('')
        self.ss_lon_var.set('')
        self.ss_alt_var.set('')
        self.ss_area_var.set('')
        self.ss_remarks_text.delete('1.0', 'end')
    
    def _refresh_parent_site_list(self):
        """親調査地リストを更新"""
        # 既存のアイテムをクリア
        for item in self.ps_tree.get_children():
            self.ps_tree.delete(item)
        
        # データを取得して追加
        sites = self.parent_site_model.get_all()
        for site in sites:
            self.ps_tree.insert('', 'end', values=(
                site['id'],
                site['name'],
                f"{site['latitude']:.6f}",
                f"{site['longitude']:.6f}",
                site['altitude'] if site['altitude'] else ''
            ))
    
    def _refresh_survey_site_list(self):
        """調査地リストを更新"""
        for item in self.ss_tree.get_children():
            self.ss_tree.delete(item)
        
        sites = self.survey_site_model.get_all()
        for site in sites:
            self.ss_tree.insert('', 'end', values=(
                site['id'],
                site['parent_site_name'],
                site['name'],
                f"{site['latitude']:.6f}",
                f"{site['longitude']:.6f}"
            ))
    
    def _update_parent_site_combo(self):
        """親調査地のコンボボックスを更新"""
        sites = self.parent_site_model.get_all()
        self.parent_site_dict = {site['name']: site['id'] for site in sites}
        self.ss_parent_combo['values'] = list(self.parent_site_dict.keys())
    
    def _on_parent_site_double_click(self, event):
        """親調査地をダブルクリックした時の処理（編集機能は今後実装）"""
        selection = self.ps_tree.selection()
        if selection:
            item = self.ps_tree.item(selection[0])
            messagebox.showinfo('情報', '編集機能は今後のバージョンで実装予定です')
