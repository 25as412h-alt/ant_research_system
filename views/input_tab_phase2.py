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
    
    # 全画面化を実現するため、タブを左右2パネルのペインドウとして構成する
    paned_root = ttk.Panedwindow(tab, orient='horizontal')
    paned_root.pack(fill='both', expand=True)

    left_pane = ttk.Frame(paned_root)
    right_pane = ttk.Frame(paned_root)
    paned_root.add(left_pane, weight=1)
    paned_root.add(right_pane, weight=1)

    # 左側：入力フォームエリア（従来のコンテンツを移植）
    content_frame = ttk.Frame(left_pane)
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
    
    # 右側：登録済みデータの一覧
    list_frame = right_pane
    ttk.Label(list_frame, text='登録済み植生データ', style='Header.TLabel').pack(anchor='w', pady=(0, 10))
    tree_frame = ttk.Frame(list_frame)
    tree_frame.pack(fill='both', expand=True)

    tree_scroll = ttk.Scrollbar(tree_frame)
    tree_scroll.pack(side='right', fill='y')

    vegetation_tree = ttk.Treeview(tree_frame,
                                   columns=('id', 'survey_date', 'site_name', 'parent_site_name'),
                                   show='headings',
                                   yscrollcommand=tree_scroll.set)
    vegetation_tree.heading('id', text='ID')
    vegetation_tree.heading('survey_date', text='調査日')
    vegetation_tree.heading('site_name', text='サイト')
    vegetation_tree.heading('parent_site_name', text='親サイト')
    vegetation_tree.column('id', width=60)
    vegetation_tree.column('survey_date', width=150)
    vegetation_tree.column('site_name', width=200)
    vegetation_tree.column('parent_site_name', width=200)
    vegetation_tree.pack(fill='both', expand=True)
    tree_scroll.config(command=vegetation_tree.yview)

    def refresh_vegetation_list():
        """植生データ一覧をリフレッシュ"""
        vegetation_tree.delete(*vegetation_tree.get_children())
        try:
            for v in veg_model.get_all():
                vegetation_tree.insert('', 'end', values=(
                    v.get('id'),
                    v.get('survey_date'),
                    v.get('site_name'),
                    v.get('parent_site_name')
                ))
        except Exception:
            pass

    refresh_vegetation_list()

    def save_vegetation():
        """植生データを保存"""
        try:
            event_key = event_var.get()
            if not event_key:
                messagebox.showwarning('入力エラー', '調査イベントを選択してください')
                return
            
            event_id = event_dict.get(event_key)
            
            # 既に植生データが登録されているかチェック
            existing = any((v.get('survey_event_id') == event_id) for v in veg_model.get_all())
            if existing:
                if not messagebox.askyesno('確認', 
                    'この調査イベントには既に植生データが登録されています。\n上書きしますか？'):
                    return

            # バリデーション
            data = {}
            for field in ['dominant_tree', 'dominant_sasa', 'dominant_herb', 'litter_type']:
                val = vars_dict[field].get().strip()
                data[field] = val if val else None
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
            refresh_vegetation_list()
        except Exception as e:
            messagebox.showerror('エラー', f'保存に失敗しました：{e}')
    
    def clear_form():
        """フォームをクリア"""
        event_var.set('')
        for var in vars_dict.values():
            var.set('')
    
    # 右ペインのフォームを保持するためのイベント・フォーム構成を左右で整える
    # 右ペインのリフレッシュは save_vegetation の後に実行されるように設定

    return tab


def create_ant_data_tab(parent, conn, models):
    """アリ類データ入力タブを作成"""
    from models.ant_record import AntRecord
    from models.species import Species
    from models.survey_event import SurveyEvent
    
    tab = ttk.Frame(parent)
    parent.add(tab, text='アリ類データ')
    
    ant_model = AntRecord(conn)
    species_model = Species(conn)
    event_model = SurveyEvent(conn)
    
    # 左側：入力フォーム
    left_frame = ttk.Frame(tab)
    left_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
    
    ttk.Label(left_frame, text='アリ類出現記録の入力', 
             style='Header.TLabel').pack(anchor='w', pady=(0, 10))
    
    # 調査イベント選択
    event_frame = ttk.LabelFrame(left_frame, text='1. 調査イベントを選択', padding=10)
    event_frame.pack(fill='x', pady=10)
    
    event_var = tk.StringVar()
    event_combo = ttk.Combobox(event_frame, textvariable=event_var, 
                               state='readonly', width=50)
    event_combo.pack(fill='x', pady=5)
    
    # イベントリストを取得
    events = event_model.get_recent(50)
    event_dict = {
        f"{e['survey_date']} - {e['parent_site_name']} {e['site_name']}": e['id'] 
        for e in events
    }
    event_combo['values'] = list(event_dict.keys())
    
    # 種名管理
    species_frame = ttk.LabelFrame(left_frame, text='2. 種名を選択または新規登録', padding=10)
    species_frame.pack(fill='x', pady=10)
    
    # 既存種選択
    ttk.Label(species_frame, text='既存種から選択:').pack(anchor='w', pady=(0, 5))
    species_var = tk.StringVar()
    species_combo = ttk.Combobox(species_frame, textvariable=species_var, width=50)
    species_combo.pack(fill='x', pady=5)
    
    def update_species_list():
        """種名リストを更新"""
        species_list = species_model.get_all()
        species_dict = {s['name']: s['id'] for s in species_list}
        species_combo['values'] = list(species_dict.keys())
        return species_dict
    
    species_dict = update_species_list()
    
    # 新規種登録
    ttk.Separator(species_frame, orient='horizontal').pack(fill='x', pady=10)
    ttk.Label(species_frame, text='新規種を登録:').pack(anchor='w', pady=(0, 5))
    
    new_species_frame = ttk.Frame(species_frame)
    new_species_frame.pack(fill='x')
    
    ttk.Label(new_species_frame, text='種名 (学名):').grid(row=0, column=0, sticky='w', pady=3)
    new_species_name_var = tk.StringVar()
    ttk.Entry(new_species_frame, textvariable=new_species_name_var, width=30).grid(
        row=0, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(new_species_frame, text='属名:').grid(row=1, column=0, sticky='w', pady=3)
    new_species_genus_var = tk.StringVar()
    ttk.Entry(new_species_frame, textvariable=new_species_genus_var, width=30).grid(
        row=1, column=1, sticky='w', padx=5, pady=3)
    
    ttk.Label(new_species_frame, text='亜科名:').grid(row=2, column=0, sticky='w', pady=3)
    new_species_subfamily_var = tk.StringVar()
    ttk.Entry(new_species_frame, textvariable=new_species_subfamily_var, width=30).grid(
        row=2, column=1, sticky='w', padx=5, pady=3)
    
    def register_new_species():
        """新種を登録"""
        try:
            name = new_species_name_var.get().strip()
            if not name:
                messagebox.showwarning('入力エラー', '種名を入力してください')
                return
            
            genus = new_species_genus_var.get().strip() or None
            subfamily = new_species_subfamily_var.get().strip() or None
            
            species_id = species_model.create(name=name, genus=genus, subfamily=subfamily)
            
            messagebox.showinfo('成功', f'種「{name}」を登録しました')
            
            # リストを更新して選択
            nonlocal species_dict
            species_dict = update_species_list()
            species_var.set(name)
            
            # フォームをクリア
            new_species_name_var.set('')
            new_species_genus_var.set('')
            new_species_subfamily_var.set('')
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'登録に失敗しました：{e}')
    
    ttk.Button(new_species_frame, text='種を登録', 
              command=register_new_species).grid(row=3, column=1, sticky='w', padx=5, pady=10)
    
    # 個体数入力
    count_frame = ttk.LabelFrame(left_frame, text='3. 個体数を入力', padding=10)
    count_frame.pack(fill='x', pady=10)
    
    ttk.Label(count_frame, text='個体数 *:').pack(side='left', padx=(0, 10))
    count_var = tk.StringVar()
    count_spinbox = ttk.Spinbox(count_frame, from_=0, to=10000, 
                                textvariable=count_var, width=15)
    count_spinbox.pack(side='left')
    
    ttk.Label(count_frame, text='備考:').pack(side='left', padx=(20, 10))
    record_remarks_var = tk.StringVar()
    ttk.Entry(count_frame, textvariable=record_remarks_var, width=30).pack(
        side='left', fill='x', expand=True)
    
    def save_ant_record():
        """アリ類記録を保存"""
        try:
            # 調査イベントチェック
            event_key = event_var.get()
            if not event_key:
                messagebox.showwarning('入力エラー', '調査イベントを選択してください')
                return
            
            event_id = event_dict.get(event_key)
            
            # 種名チェック
            species_name = species_var.get().strip()
            if not species_name:
                messagebox.showwarning('入力エラー', '種を選択してください')
                return
            
            species_id = species_dict.get(species_name)
            if not species_id:
                messagebox.showerror('エラー', '選択された種が見つかりません')
                return
            
            # 個体数チェック
            is_valid, count, msg = Validators.validate_integer(count_var.get(), '個体数')
            if not is_valid:
                messagebox.showerror('入力エラー', msg)
                return
            
            remarks = record_remarks_var.get().strip() or None
            
            record_id = ant_model.create(
                survey_event_id=event_id,
                species_id=species_id,
                count=count,
                remarks=remarks
            )
            
            messagebox.showinfo('成功', f'出現記録を登録しました（ID: {record_id}）')
            
            # 個体数と備考のみクリア（連続入力しやすいように）
            count_var.set('0')
            record_remarks_var.set('')
            species_var.set('')
            
            refresh_event_records()
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'保存に失敗しました：{e}')
    
    def clear_all():
        """全フォームをクリア"""
        event_var.set('')
        species_var.set('')
        count_var.set('0')
        record_remarks_var.set('')
        new_species_name_var.set('')
        new_species_genus_var.set('')
        new_species_subfamily_var.set('')
        
        # 右側のリストもクリア
        for item in event_records_tree.get_children():
            event_records_tree.delete(item)
    
    # ボタン
    button_frame = ttk.Frame(left_frame)
    button_frame.pack(fill='x', pady=10)
    
    ttk.Button(button_frame, text='記録を追加', 
              command=save_ant_record, 
              style='Accent.TButton').pack(side='left', padx=5)
    ttk.Button(button_frame, text='全クリア', 
              command=clear_all).pack(side='left', padx=5)
    
    # 右側：選択中の調査イベントの記録一覧
    right_frame = ttk.Frame(tab)
    right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
    
    ttk.Label(right_frame, text='選択中イベントの出現記録', 
             style='Header.TLabel').pack(anchor='w', pady=(0, 10))
    
    tree_frame = ttk.Frame(right_frame)
    tree_frame.pack(fill='both', expand=True)
    
    scrollbar = ttk.Scrollbar(tree_frame)
    scrollbar.pack(side='right', fill='y')
    
    event_records_tree = ttk.Treeview(tree_frame,
                                     columns=('species', 'count', 'remarks'),
                                     show='headings',
                                     yscrollcommand=scrollbar.set)
    scrollbar.config(command=event_records_tree.yview)
    
    event_records_tree.heading('species', text='種名')
    event_records_tree.heading('count', text='個体数')
    event_records_tree.heading('remarks', text='備考')
    
    event_records_tree.column('species', width=250)
    event_records_tree.column('count', width=100)
    event_records_tree.column('remarks', width=200)
    
    event_records_tree.pack(fill='both', expand=True)
    
    def refresh_event_records(*args):
        """選択中のイベントの記録を表示"""
        for item in event_records_tree.get_children():
            event_records_tree.delete(item)
        
        event_key = event_var.get()
        if not event_key:
            return
        
        event_id = event_dict.get(event_key)
        if not event_id:
            return
        
        records = ant_model.get_by_event(event_id)
        
        total_species = len(records)
        total_individuals = sum(r['count'] for r in records)
        
        for record in records:
            event_records_tree.insert('', 'end', values=(
                record['species_name'],
                record['count'],
                record['remarks'] or ''
            ))
        
        # サマリー表示
        summary_label.config(
            text=f"種数: {total_species}種  総個体数: {total_individuals}個体"
        )
    
    # イベント選択時に記録を更新
    event_combo.bind('<<ComboboxSelected>>', refresh_event_records)
    
    # サマリーラベル
    summary_label = ttk.Label(right_frame, text='', font=('Yu Gothic UI', 10, 'bold'))
    summary_label.pack(pady=5)
    
    # 削除ボタン
    def delete_selected_record():
        """選択中の記録を削除"""
        selection = event_records_tree.selection()
        if not selection:
            messagebox.showwarning('警告', '削除する記録を選択してください')
            return
        
        if messagebox.askyesno('確認', '選択した記録を削除しますか？'):
            # 実装はシンプルに：リストから種名を取得して該当レコードを削除
            messagebox.showinfo('情報', '削除機能は今後のバージョンで実装予定です')
    
    ttk.Button(right_frame, text='選択した記録を削除', 
              command=delete_selected_record).pack(pady=5)
    
    return tab
