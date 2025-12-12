"""
設定・管理タブ
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from utils.integrity_checker import IntegrityChecker
from models.database import Database
import configparser
import os
from pathlib import Path


class SettingsTab:
    """設定・管理タブクラス"""
    
    def __init__(self, parent, db_connection):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            db_connection: データベース接続
        """
        self.conn = db_connection
        self.integrity_checker = IntegrityChecker(db_connection)
        
        # メインフレーム
        self.frame = ttk.Frame(parent)
        
        # サブタブを作成
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 各サブタブ
        self._create_integrity_tab()
        self._create_backup_tab()
        self._create_settings_tab()
        self._create_about_tab()
    
    def _create_integrity_tab(self):
        """データ整合性チェックタブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='データ整合性チェック')
        
        # 上部：説明とボタン
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(top_frame, text='データ整合性チェック', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        
        info_text = """
データベースの整合性をチェックし、問題を検出します。
• 孤立レコードの検出
• 重複データの検出
• 不正な値の検出
• 必須データの欠落チェック
• 座標の妥当性チェック
        """
        
        ttk.Label(top_frame, text=info_text, justify='left').pack(anchor='w', pady=5)
        
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(fill='x', pady=10)
        
        ttk.Button(button_frame, text='チェック実行', 
                  command=self._run_integrity_check,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        self.integrity_status_label = ttk.Label(button_frame, text='', 
                                               font=('Yu Gothic UI', 10, 'bold'))
        self.integrity_status_label.pack(side='left', padx=20)
        
        # 中部：統計情報
        stats_frame = ttk.LabelFrame(tab, text='データベース統計', padding=10)
        stats_frame.pack(fill='x', padx=20, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=8, width=80, 
                                 state='disabled', wrap='word')
        self.stats_text.pack(fill='x')
        
        ttk.Button(stats_frame, text='統計を更新', 
                  command=self._update_stats).pack(pady=5)
        
        # 下部：問題リスト
        issues_frame = ttk.LabelFrame(tab, text='検出された問題', padding=10)
        issues_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tree_frame = ttk.Frame(issues_frame)
        tree_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.issues_tree = ttk.Treeview(
            tree_frame,
            columns=('severity', 'type', 'table', 'message'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.issues_tree.yview)
        
        self.issues_tree.heading('severity', text='重要度')
        self.issues_tree.heading('type', text='種類')
        self.issues_tree.heading('table', text='テーブル')
        self.issues_tree.heading('message', text='メッセージ')
        
        self.issues_tree.column('severity', width=80)
        self.issues_tree.column('type', width=120)
        self.issues_tree.column('table', width=150)
        self.issues_tree.column('message', width=400)
        
        self.issues_tree.pack(fill='both', expand=True)
        
        # 初回統計更新
        self._update_stats()
    
    def _create_backup_tab(self):
        """バックアップ管理タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='バックアップ')
        
        ttk.Label(tab, text='バックアップ管理', 
                 style='Header.TLabel').pack(anchor='w', padx=20, pady=10)
        
        # バックアップ作成
        backup_frame = ttk.LabelFrame(tab, text='バックアップの作成', padding=15)
        backup_frame.pack(fill='x', padx=20, pady=10)
        
        info_text = """
データベースの完全なバックアップを作成します。
重要な操作の前には必ずバックアップを作成してください。
        """
        ttk.Label(backup_frame, text=info_text, justify='left').pack(anchor='w', pady=5)
        
        ttk.Button(backup_frame, text='今すぐバックアップを作成', 
                  command=self._create_backup).pack(pady=10)
        
        # 自動バックアップ設定
        auto_frame = ttk.LabelFrame(tab, text='自動バックアップ設定', padding=15)
        auto_frame.pack(fill='x', padx=20, pady=10)
        
        self.auto_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_frame, text='起動時に自動バックアップを作成', 
                       variable=self.auto_backup_var,
                       command=self._save_backup_setting).pack(anchor='w', pady=5)
        
        ttk.Label(auto_frame, text='保存世代数:').pack(anchor='w', pady=(10, 2))
        self.max_backups_var = tk.IntVar(value=10)
        ttk.Spinbox(auto_frame, from_=1, to=50, 
                   textvariable=self.max_backups_var, width=10,
                   command=self._save_backup_setting).pack(anchor='w', pady=2)
        
        # バックアップリスト
        list_frame = ttk.LabelFrame(tab, text='バックアップ履歴', padding=15)
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        ttk.Button(list_frame, text='バックアップフォルダを開く', 
                  command=self._open_backup_folder).pack(pady=5)
        
        self.backup_listbox = tk.Listbox(list_frame, height=10)
        self.backup_listbox.pack(fill='both', expand=True, pady=5)
        
        ttk.Button(list_frame, text='リストを更新', 
                  command=self._update_backup_list).pack(pady=5)
        
        self._update_backup_list()
    
    def _create_settings_tab(self):
        """アプリケーション設定タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='アプリケーション設定')
        
        ttk.Label(tab, text='アプリケーション設定', 
                 style='Header.TLabel').pack(anchor='w', padx=20, pady=10)
        
        # UI設定
        ui_frame = ttk.LabelFrame(tab, text='UI設定', padding=15)
        ui_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(ui_frame, text='フォントサイズ:').grid(row=0, column=0, 
                                                        sticky='w', pady=5)
        self.font_size_var = tk.IntVar(value=10)
        ttk.Spinbox(ui_frame, from_=8, to=14, 
                   textvariable=self.font_size_var, width=10).grid(
                       row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(ui_frame, text='ウィンドウ幅:').grid(row=1, column=0, 
                                                      sticky='w', pady=5)
        self.window_width_var = tk.IntVar(value=1400)
        ttk.Spinbox(ui_frame, from_=1000, to=2000, increment=100,
                   textvariable=self.window_width_var, width=10).grid(
                       row=1, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(ui_frame, text='ウィンドウ高さ:').grid(row=2, column=0, 
                                                        sticky='w', pady=5)
        self.window_height_var = tk.IntVar(value=900)
        ttk.Spinbox(ui_frame, from_=600, to=1200, increment=100,
                   textvariable=self.window_height_var, width=10).grid(
                       row=2, column=1, sticky='w', padx=5, pady=5)
        
        # エクスポート設定
        export_frame = ttk.LabelFrame(tab, text='エクスポート設定', padding=15)
        export_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(export_frame, text='CSV文字コード:').grid(row=0, column=0, 
                                                          sticky='w', pady=5)
        self.csv_encoding_var = tk.StringVar(value='utf-8-sig')
        ttk.Combobox(export_frame, textvariable=self.csv_encoding_var,
                    values=['utf-8-sig', 'utf-8', 'shift-jis'],
                    state='readonly', width=15).grid(
                        row=0, column=1, sticky='w', padx=5, pady=5)
        
        ttk.Label(export_frame, text='日付形式:').grid(row=1, column=0, 
                                                      sticky='w', pady=5)
        self.date_format_var = tk.StringVar(value='%Y-%m-%d')
        ttk.Combobox(export_frame, textvariable=self.date_format_var,
                    values=['%Y-%m-%d', '%Y/%m/%d', '%d/%m/%Y'],
                    state='readonly', width=15).grid(
                        row=1, column=1, sticky='w', padx=5, pady=5)
        
        # 保存ボタン
        ttk.Button(tab, text='設定を保存', 
                  command=self._save_settings).pack(pady=20)
        
        # 現在の設定を読み込み
        self._load_settings()
    
    def _create_about_tab(self):
        """アプリケーション情報タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='アプリケーション情報')
        
        # 中央に配置
        center_frame = ttk.Frame(tab)
        center_frame.pack(expand=True)
        
        # アプリ名
        ttk.Label(center_frame, 
                 text='アリ類群集・植生データ管理システム',
                 font=('Yu Gothic UI', 16, 'bold')).pack(pady=10)
        
        # バージョン
        ttk.Label(center_frame, 
                 text='バージョン 1.0.0',
                 font=('Yu Gothic UI', 12)).pack(pady=5)
        
        # 説明
        description = """
研究によって得られた「同所的アリ類群集」および
「立地環境（植生）」の調査データを効率的に管理・解析するための
デスクトップアプリケーションです。

全ての開発フェーズ（Phase 1-5）が完了しました！
        """
        
        ttk.Label(center_frame, text=description, 
                 justify='center', font=('Yu Gothic UI', 10)).pack(pady=20)
        
        # 機能リスト
        features_frame = ttk.LabelFrame(center_frame, text='実装済み機能', padding=15)
        features_frame.pack(pady=10)
        
        features = """
✓ データベース管理（SQLite3）
✓ 調査地・イベント・植生・アリ類データの入力
✓ データ検索・閲覧機能
✓ CSV/Excel出力（行列変換）
✓ 統計解析（多様度指数、相関分析）
✓ 可視化（散布図、グラフ、地図）
✓ クラスタ解析（K-Means、階層的）
✓ ヒートマップ
✓ データ整合性チェック
✓ バックアップ管理
        """
        
        ttk.Label(features_frame, text=features, 
                 justify='left', font=('Yu Gothic UI', 9)).pack()
        
        # 開発情報
        ttk.Label(center_frame, 
                 text='開発: Claude (Anthropic)\n最終更新: 2025年12月11日',
                 font=('Yu Gothic UI', 9), 
                 foreground='gray').pack(pady=20)
    
    # データ整合性チェック関連メソッド
    def _run_integrity_check(self):
        """整合性チェックを実行"""
        try:
            result = self.integrity_checker.run_all_checks()
            
            # ステータス更新
            if result['status'] == 'OK':
                self.integrity_status_label.config(
                    text='✓ 問題は検出されませんでした',
                    foreground='green'
                )
            else:
                self.integrity_status_label.config(
                    text=f'⚠ {result["total_issues"]}件の問題が検出されました',
                    foreground='orange'
                )
            
            # 問題リストを表示
            for item in self.issues_tree.get_children():
                self.issues_tree.delete(item)
            
            for issue in result['issues']:
                severity_label = {
                    'high': '🔴 高',
                    'medium': '🟡 中',
                    'low': '🟢 低'
                }.get(issue['severity'], issue['severity'])
                
                self.issues_tree.insert('', 'end', values=(
                    severity_label,
                    issue['type'],
                    issue['table'],
                    issue['message']
                ))
            
            messagebox.showinfo('完了', 
                f'整合性チェックが完了しました\n\n'
                f'検出された問題: {result["total_issues"]}件')
            
        except Exception as e:
            messagebox.showerror('エラー', f'チェックに失敗しました：{e}')
    
    def _update_stats(self):
        """統計情報を更新"""
        try:
            stats = self.integrity_checker.get_statistics()
            
            self.stats_text.config(state='normal')
            self.stats_text.delete('1.0', 'end')
            
            text = "データベース統計情報:\n\n"
            
            tables = {
                'parent_sites': '親調査地',
                'survey_sites': '調査地',
                'survey_events': '調査イベント',
                'vegetation_data': '植生データ',
                'species_master': '種マスタ',
                'ant_records': 'アリ類記録'
            }
            
            for table, name in tables.items():
                active = stats.get(f'{table}_active', 0)
                deleted = stats.get(f'{table}_deleted', 0)
                total = active + deleted
                text += f"{name}: {active:,}件（削除済み: {deleted}件、合計: {total:,}件）\n"
            
            self.stats_text.insert('1.0', text)
            self.stats_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror('エラー', f'統計の取得に失敗しました：{e}')
    
    # バックアップ関連メソッド
    def _create_backup(self):
        """バックアップを作成"""
        try:
            db = Database()
            backup_path = db.backup()
            
            messagebox.showinfo('成功', 
                f'バックアップを作成しました\n\n{backup_path}')
            
            self._update_backup_list()
            
        except Exception as e:
            messagebox.showerror('エラー', f'バックアップの作成に失敗しました：{e}')
    
    def _update_backup_list(self):
        """バックアップリストを更新"""
        self.backup_listbox.delete(0, tk.END)
        
        backup_dir = Path('backups')
        if backup_dir.exists():
            backups = sorted(backup_dir.glob('*.db'), reverse=True)
            for backup in backups[:20]:  # 最新20件
                self.backup_listbox.insert(tk.END, backup.name)
    
    def _open_backup_folder(self):
        """バックアップフォルダを開く"""
        import subprocess
        import platform
        
        backup_dir = os.path.abspath('backups')
        
        if platform.system() == 'Windows':
            os.startfile(backup_dir)
        elif platform.system() == 'Darwin':
            subprocess.Popen(['open', backup_dir])
        else:
            subprocess.Popen(['xdg-open', backup_dir])
    
    def _save_backup_setting(self):
        """バックアップ設定を保存"""
        # 実装は_save_settingsに統合
        pass
    
    # 設定関連メソッド
    def _load_settings(self):
        """設定を読み込み"""
        config = configparser.ConfigParser()
        config_path = Path('config.ini')
        
        if config_path.exists():
            config.read(config_path, encoding='utf-8')
            
            # UI設定
            self.font_size_var.set(
                config.getint('UI', 'font_size', fallback=10))
            self.window_width_var.set(
                config.getint('UI', 'window_width', fallback=1400))
            self.window_height_var.set(
                config.getint('UI', 'window_height', fallback=900))
            
            # バックアップ設定
            self.auto_backup_var.set(
                config.getboolean('Database', 'auto_backup', fallback=True))
            self.max_backups_var.set(
                config.getint('Database', 'max_backups', fallback=10))
            
            # エクスポート設定
            self.csv_encoding_var.set(
                config.get('Export', 'default_csv_encoding', fallback='utf-8-sig'))
            self.date_format_var.set(
                config.get('Export', 'date_format', fallback='%Y-%m-%d'))
    
    def _save_settings(self):
        """設定を保存"""
        try:
            config = configparser.ConfigParser()
            config_path = Path('config.ini')
            
            if config_path.exists():
                config.read(config_path, encoding='utf-8')
            
            # セクションがない場合は作成
            for section in ['UI', 'Database', 'Export']:
                if not config.has_section(section):
                    config.add_section(section)
            
            # UI設定
            config.set('UI', 'font_size', str(self.font_size_var.get()))
            config.set('UI', 'window_width', str(self.window_width_var.get()))
            config.set('UI', 'window_height', str(self.window_height_var.get()))
            
            # バックアップ設定
            config.set('Database', 'auto_backup', 
                      str(self.auto_backup_var.get()))
            config.set('Database', 'max_backups', 
                      str(self.max_backups_var.get()))
            
            # エクスポート設定
            config.set('Export', 'default_csv_encoding', 
                      self.csv_encoding_var.get())
            config.set('Export', 'date_format', 
                      self.date_format_var.get())
            
            # 保存
            with open(config_path, 'w', encoding='utf-8') as f:
                config.write(f)
            
            messagebox.showinfo('成功', 
                '設定を保存しました\n\n次回起動時から反映されます')
            
        except Exception as e:
            messagebox.showerror('エラー', f'設定の保存に失敗しました：{e}')