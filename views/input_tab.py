"""
データ入力タブ
"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.parent_site import ParentSite
from models.survey_site import SurveySite
from models.survey_event import SurveyEvent
from models.vegetation import Vegetation
from models.species import Species
from models.ant_record import AntRecord
from utils.validators import Validators
from datetime import datetime


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
        self.survey_event_model = SurveyEvent(db_connection)
        self.vegetation_model = Vegetation(db_connection)
        self.species_model = Species(db_connection)
        self.ant_record_model = AntRecord(db_connection)
        
        # メインフレーム
        self.frame = ttk.Frame(parent)
        
        # サブタブを作成
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 親調査地入力タブ
        self._create_parent_site_tab()
        
        # 調査地入力タブ
        self._create_survey_site_tab()
        
        # 調査イベント入力タブ
        self._create_survey_event_tab()
        
        # 植生データ入力タブ
        self._create_vegetation_tab()
        
        # アリ類データ入力タブ
        self._create_ant_data_tab()
    
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

"""
Phase 2 データ入力タブ拡張
調査イベント、植生データ、アリ類データの入力機能
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.validators import Validators


def create_survey_event_tab(parent, conn, models):
    """調査イベント入力タブを作成"""
    from models.survey_event import SurveyEvent
    from models.survey_site import SurveySite
    
    tab = ttk.Frame(parent)
    parent.add(tab, text='調査イベント')
    
    event_model = SurveyEvent(conn)
    site_model = SurveySite(conn)
    
    # 左側：入力フォーム
    left_frame = ttk.Frame(tab)
    left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
    
    ttk.Label(left_frame, text='調査イベントの登録', 
             style='Header.TLabel').pack(anchor='w', pady=(0, 10))
    
    form_frame = ttk.Frame(left_frame)
    form_frame.pack(fill='x', pady=5)
    
    # 調査地選択
    ttk.Label(form_frame, text='調査地 *').grid(row=0, column=0, sticky='w', pady=5)
    site_var = tk.StringVar()
    site_combo = ttk.Combobox(form_frame, textvariable=site_var, 
                              state='readonly', width=38)
    site_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
    
    # 調査地リストを取得
    sites = site_model.get_all()
    site_dict = {f"{s['parent_site_name']} - {s['name']}": s['id'] for s in sites}
    site_combo['values'] = list(site_dict.keys())
    
    # 調査日
    ttk.Label(form_frame, text='調査日 *').grid(row=1, column=0, sticky='w', pady=5)
    date_frame = ttk.Frame(form_frame)
    date_frame.grid(row=1, column=1, sticky='w', padx=5, pady=5)
    
    date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
    ttk.Entry(date_frame, textvariable=date_var, width=15).pack(side='left')
    ttk.Label(date_frame, text='時刻:', padx=(10, 5)).pack(side='left')
    time_var = tk.StringVar(value='09:00')
    ttk.Entry(date_frame, textvariable=time_var, width=8).pack(side='left')
    
    # 調査者名
    ttk.Label(form_frame, text='調査者名').grid(row=2, column=0, sticky='w', pady=5)
    surveyor_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=surveyor_var, width=40).grid(
        row=2, column=1, sticky='w', padx=5, pady=5)
    
    # 天候
    ttk.Label(form_frame, text='天候').grid(row=3, column=0, sticky='w', pady=5)
    weather_var = tk.StringVar()
    weather_combo = ttk.Combobox(form_frame, textvariable=weather_var,
                                 values=['晴れ', '曇り', '雨', '雪'],
                                 state='readonly', width=15)
    weather_combo.grid(row=3, column=1, sticky='w', padx=5, pady=5)
    
    # 気温
    ttk.Label(form_frame, text='気温 (℃)').grid(row=4, column=0, sticky='w', pady=5)
    temp_var = tk.StringVar()
    ttk.Entry(form_frame, textvariable=temp_var, width=15).grid(
        row=4, column=1, sticky='w', padx=5, pady=5)
    
    # 備考
    ttk.Label(form_frame, text='備考').grid(row=5, column=0, sticky='nw', pady=5)
    remarks_text = tk.Text(form_frame, width=40, height=4, wrap='word')
    remarks_text.grid(row=5, column=1, sticky='ew', padx=5, pady=5)
    
    form_frame.columnconfigure(1, weight=1)
    
    def save_event():
        """調査イベントを保存"""
        try:
            site_key = site_var.get()
            if not site_key:
                messagebox.showwarning('入力エラー', '調査地を選択してください')
                return
            
            site_id = site_dict.get(site_key)
            date_str = date_var.get().strip()
            time_str = time_var.get().strip()
            
            # 日時バリデーション
            is_valid, datetime_str, msg = Validators.validate_datetime(f"{date_str} {time_str}")
            if not is_valid:
                messagebox.showerror('入力エラー', msg)
                return
            
            surveyor = surveyor_var.get().strip() or None
            weather = weather_var.get() or None
            
            temp = None
            if temp_var.get().strip():
                is_valid, temp, msg = Validators.validate_positive_number(
                    temp_var.get(), '気温')
                if not is_valid:
                    messagebox.showerror('入力エラー', msg)
                    return
            
            remarks = remarks_text.get('1.0', 'end-1c').strip() or None
            
            event_id = event_model.create(
                survey_site_id=site_id,
                survey_date=datetime_str,
                surveyor_name=surveyor,
                weather=weather,
                temperature=temp,
                remarks=remarks
            )
            
            messagebox.showinfo('成功', f'調査イベントを登録しました（ID: {event_id}）\n\n次は植生データまたはアリ類データを入力してください。')
            clear_form()
            refresh_list()
            
        except Exception as e:
            messagebox.showerror('エラー', f'保存に失敗しました：{e}')
    
    def clear_form():
        """フォームをクリア"""
        site_var.set('')
        date_var.set(datetime.now().strftime('%Y-%m-%d'))
        time_var.set('09:00')
        surveyor_var.set('')
        weather_var.set('')
        temp_var.set('')
        remarks_text.delete('1.0', 'end')
    
    # ボタン
    button_frame = ttk.Frame(left_frame)
    button_frame.pack(fill='x', pady=10)
    
    ttk.Button(button_frame, text='登録', command=save_event).pack(side='left', padx=5)
    ttk.Button(button_frame, text='クリア', command=clear_form).pack(side='left', padx=5)
    
    # 右側：登録済みリスト
    right_frame = ttk.Frame(tab)
    right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
    
    ttk.Label(right_frame, text='登録済み調査イベント', 
             style='Header.TLabel').pack(anchor='w', pady=(0, 10))
    
    tree_frame = ttk.Frame(right_frame)
    tree_frame.pack(fill='both', expand=True)
    
    scrollbar = ttk.Scrollbar(tree_frame)
    scrollbar.pack(side='right', fill='y')
    
    event_tree = ttk.Treeview(tree_frame,
                             columns=('id', 'date', 'site', 'weather', 'temp'),
                             show='headings',
                             yscrollcommand=scrollbar.set)
    scrollbar.config(command=event_tree.yview)
    
    event_tree.heading('id', text='ID')
    event_tree.heading('date', text='調査日時')
    event_tree.heading('site', text='調査地')
    event_tree.heading('weather', text='天候')
    event_tree.heading('temp', text='気温(℃)')
    
    event_tree.column('id', width=50)
    event_tree.column('date', width=150)
    event_tree.column('site', width=200)
    event_tree.column('weather', width=80)
    event_tree.column('temp', width=80)
    
    event_tree.pack(fill='both', expand=True)
    
    def refresh_list():
        """リストを更新"""
        for item in event_tree.get_children():
            event_tree.delete(item)
        
        events = event_model.get_recent(20)
        for event in events:
            event_tree.insert('', 'end', values=(
                event['id'],
                event['survey_date'],
                f"{event['parent_site_name']} - {event['site_name']}",
                event['weather'] or '',
                event['temperature'] if event['temperature'] else ''
            ))
    
    refresh_list()
    
    return tab


def create_vegetation_tab(parent, conn, models):
    """植生データ入力タブを作成"""
    from models.vegetation import Vegetation
    from models.survey_event import SurveyEvent
    
    tab = ttk.Frame(parent)
    parent.add(tab, text='植生データ')
    
    veg_model = Vegetation(conn)
    event_model = SurveyEvent(conn)
    
    # スクロール可能なフレーム
    canvas = tk.Canvas(tab)
    scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # 内容
    content_frame = ttk.Frame(scrollable_frame)
    content_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    ttk.Label(content_frame, text='植生データの入力', 
             style='Header.TLabel').pack(anchor='w', pady=(0, 10))
    
    # 調査イベント選択
    event_frame = ttk.Frame(content_frame)
    event_frame.pack(fill='x', pady=10)
    
    ttk.Label(event_frame, text='調査イベント *').pack(side='left', padx=(0, 10))
    event_var = tk.StringVar()
    event_combo = ttk.Combobox(event_frame, textvariable=event_var, 
                               state='readonly', width=50)
    event_combo.pack(side='left', fill='x', expand=True)
    
    # イベントリストを取得
    events = event_model.get_recent(50)
    event_dict = {
        f"{e['survey_date']} - {e['parent_site_name']} {e['site_name']}": e['id'] 
        for e in events
    }
    event_combo['values'] = list(event_dict.keys())
    
    # 入力フォーム
    form_frame = ttk.LabelFrame(content_frame, text='環境測定値', padding=10)
    form_frame.pack(fill='x', pady=10)
    
    vars_dict = {}
    
    # 優占種
    ttk.Label(form_frame, text='優占樹種').grid(row=0, column=0, sticky='w', pady=3)
    vars_dict['dominant_tree'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['dominant_tree'], width=30).grid(
        row=0, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='優占ササ種').grid(row=0, column=2, sticky='w', padx=(20, 5), pady=3)
    vars_dict['dominant_sasa'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['dominant_sasa'], width=30).grid(
        row=0, column=3, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='優占草本').grid(row=1, column=0, sticky='w', pady=3)
    vars_dict['dominant_herb'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['dominant_herb'], width=30).grid(
        row=1, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='リター種類').grid(row=1, column=2, sticky='w', padx=(20, 5), pady=3)
    vars_dict['litter_type'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['litter_type'], width=30).grid(
        row=1, column=3, sticky='w', padx=5, pady=3)
    
    # 数値データ
    ttk.Separator(form_frame, orient='horizontal').grid(
        row=2, column=0, columnspan=4, sticky='ew', pady=10)
    
    ttk.Label(form_frame, text='胸高断面積 (㎡/ha)').grid(row=3, column=0, sticky='w', pady=3)
    vars_dict['basal_area'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['basal_area'], width=15).grid(
        row=3, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='平均樹高 (m)').grid(row=3, column=2, sticky='w', padx=(20, 5), pady=3)
    vars_dict['avg_tree_height'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['avg_tree_height'], width=15).grid(
        row=3, column=3, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='平均草丈 (cm)').grid(row=4, column=0, sticky='w', pady=3)
    vars_dict['avg_herb_height'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['avg_herb_height'], width=15).grid(
        row=4, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='地温 (℃)').grid(row=4, column=2, sticky='w', padx=(20, 5), pady=3)
    vars_dict['soil_temperature'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['soil_temperature'], width=15).grid(
        row=4, column=3, sticky='w', padx=5, pady=3)
    
    # 被度データ
    ttk.Separator(form_frame, orient='horizontal').grid(
        row=5, column=0, columnspan=4, sticky='ew', pady=10)
    
    ttk.Label(form_frame, text='樹冠被度 (%)').grid(row=6, column=0, sticky='w', pady=3)
    vars_dict['canopy_coverage'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['canopy_coverage'], width=15).grid(
        row=6, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='ササ被度 (%)').grid(row=6, column=2, sticky='w', padx=(20, 5), pady=3)
    vars_dict['sasa_coverage'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['sasa_coverage'], width=15).grid(
        row=6, column=3, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='草本被度 (%)').grid(row=7, column=0, sticky='w', pady=3)
    vars_dict['herb_coverage'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['herb_coverage'], width=15).grid(
        row=7, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='リター被度 (%)').grid(row=7, column=2, sticky='w', padx=(20, 5), pady=3)
    vars_dict['litter_coverage'] = tk.StringVar()
    ttk.Entry(form_frame, textvariable=vars_dict['litter_coverage'], width=15).grid(
        row=7, column=3, sticky='w', padx=5, pady=3)
    
    # 段階評価
    ttk.Separator(form_frame, orient='horizontal').grid(
        row=8, column=0, columnspan=4, sticky='ew', pady=10)
    
    ttk.Label(form_frame, text='光条件 (1:暗～5:明)').grid(row=9, column=0, sticky='w', pady=3)
    vars_dict['light_condition'] = tk.StringVar()
    ttk.Spinbox(form_frame, from_=1, to=5, textvariable=vars_dict['light_condition'], 
                width=10).grid(row=9, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='土湿条件 (1:乾～5:湿)').grid(row=9, column=2, sticky='w', padx=(20, 5), pady=3)
    vars_dict['soil_moisture'] = tk.StringVar()
    ttk.Spinbox(form_frame, from_=1, to=5, textvariable=vars_dict['soil_moisture'], 
                width=10).grid(row=9, column=3, sticky='w', padx=5, pady=3)
    
    ttk.Label(form_frame, text='植生複雑度 (1:単～5:複)').grid(row=10, column=0, sticky='w', pady=3)
    vars_dict['vegetation_complexity'] = tk.StringVar()
    ttk.Spinbox(form_frame, from_=1, to=5, textvariable=vars_dict['vegetation_complexity'], 
                width=10).grid(row=10, column=1, sticky='w', padx=5, pady=3)
    
    def save_vegetation():
        """植生データを保存"""
        try:
            event_key = event_var.get()
            if not event_key:
                messagebox.showwarning('入力エラー', '調査イベントを選択してください')
                return
            
            event_id = event_dict.get(event_key)
            
            # 既に植生データが登録されているかチェック
            if veg_model.exists_for_event(event_id):
                if not messagebox.askyesno('確認', 
                    'この調査イベントには既に植生データが登録されています。\n上書きしますか？'):
                    return
            
            # バリデーション
            data = {}
            
            # テキスト項目
            for field in ['dominant_tree', 'dominant_sasa', 'dominant_herb', 'litter_type']:
                val = vars_dict[field].get().strip()
                data[field] = val if val else None
            
            # 数値項目
            for field in ['basal_area', 'avg_tree_height', 'avg_herb_height', 'soil_temperature']:
                val = vars_dict[field].get().strip()
                if val:
                    is_valid, num, msg = Validators.validate_positive_number(val, field)
                    if not is_valid:
                        messagebox.showerror('入力エラー', msg)
                        return
                    data[field] = num
                else:
                    data[field] = None
            
            # 被度項目
            for field in ['canopy_coverage', 'sasa_coverage', 'herb_coverage', 'litter_coverage']:
                val = vars_dict[field].get().strip()
                if val:
                    is_valid, num, msg = Validators.validate_percentage(val, field)
                    if not is_valid:
                        messagebox.showerror('入力エラー', msg)
                        return
                    data[field] = num
                else:
                    data[field] = None
            
            # 段階評価
            for field in ['light_condition', 'soil_moisture', 'vegetation_complexity']:
                val = vars_dict[field].get().strip()
                if val:
                    is_valid, num, msg = Validators.validate_scale_1_to_5(val, field)
                    if not is_valid:
                        messagebox.showerror('入力エラー', msg)
                        return
                    data[field] = num
                else:
                    data[field] = None
            
            veg_id = veg_model.create(survey_event_id=event_id, **data)
            
            messagebox.showinfo('成功', f'植生データを登録しました（ID: {veg_id}）')
            clear_form()
            
        except Exception as e:
            messagebox.showerror('エラー', f'保存に失敗しました：{e}')
    
    def clear_form():
        """フォームをクリア"""
        event_var.set('')
        for var in vars_dict.values():
            var.set('')
    
    # ボタン
    button_frame = ttk.Frame(content_frame)
    button_frame.pack(fill='x', pady=10)
    
    ttk.Button(button_frame, text='登録', command=save_vegetation).pack(side='left', padx=5)
    ttk.Button(button_frame, text='クリア', command=clear_form).pack(side='left', padx=5)
    
    return tab


def create_ant_data_tab(parent, conn, models):
    """アリ類データ入力タブを作成（次のメッセージで実装）"""
    tab = ttk.Frame(parent)
    parent.add(tab, text='アリ類データ')
    
    ttk.Label(tab, text='アリ類データ入力機能は次のメッセージで実装します',
             font=('Yu Gothic UI', 12)).pack(pady=50)
    
    return tab