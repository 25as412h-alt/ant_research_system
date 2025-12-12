"""
メインウィンドウ
"""
import tkinter as tk
from tkinter import ttk, messagebox
import configparser
from pathlib import Path


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self, db_connection):
        """
        初期化
        
        Args:
            db_connection: データベース接続オブジェクト
        """
        self.conn = db_connection
        self.root = tk.Tk()
        self.config = self._load_config()
        
        # ウィンドウ設定
        self._setup_window()
        
        # スタイル設定
        self._setup_styles()
        
        # タブ作成
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 各タブを初期化（Phase 1では入力・閲覧のみ）
        self._create_tabs()
        
        # ステータスバー
        self._create_statusbar()
    
    def _load_config(self):
        """設定ファイルを読み込み"""
        config = configparser.ConfigParser()
        config_path = Path('config.ini')
        
        if config_path.exists():
            config.read(config_path, encoding='utf-8')
        else:
            # デフォルト設定
            config['UI'] = {
                'window_title': 'アリ類群集・植生データ管理システム v1.0',
                'window_width': '1400',
                'window_height': '900',
                'font_family': 'Yu Gothic UI',
                'font_size': '10'
            }
        
        return config
    
    def _setup_window(self):
        """ウィンドウの基本設定"""
        # タイトル
        title = self.config.get('UI', 'window_title', 
                                fallback='アリ類群集・植生データ管理システム')
        self.root.title(title)
        
        # サイズ
        width = self.config.getint('UI', 'window_width', fallback=1400)
        height = self.config.getint('UI', 'window_height', fallback=900)
        
        # 画面中央に配置
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # 最小サイズ
        self.root.minsize(1000, 600)
        
        # アイコン設定（オプション）
        # self.root.iconbitmap('icon.ico')
        
        # 終了時の確認
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        """スタイル設定"""
        style = ttk.Style()
        
        # テーマ設定
        theme = self.config.get('UI', 'default_theme', fallback='clam')
        try:
            style.theme_use(theme)
        except tk.TclError:
            style.theme_use('clam')  # フォールバック
        
        # フォント設定
        font_family = self.config.get('UI', 'font_family', fallback='Yu Gothic UI')
        font_size = self.config.getint('UI', 'font_size', fallback=10)
        
        # カスタムスタイル
        style.configure('Title.TLabel', 
                       font=(font_family, font_size + 4, 'bold'))
        style.configure('Header.TLabel', 
                       font=(font_family, font_size + 2, 'bold'))
        style.configure('TButton', 
                       font=(font_family, font_size))
        style.configure('TLabel', 
                       font=(font_family, font_size))
        style.configure('TEntry', 
                       font=(font_family, font_size))
        style.configure('Treeview', 
                       font=(font_family, font_size),
                       rowheight=25)
        style.configure('Treeview.Heading', 
                       font=(font_family, font_size, 'bold'))
    
    def _create_tabs(self):
        """タブを作成"""
        # Phase 1: 入力・閲覧タブ
        from views.input_tab import InputTab
        from views.view_tab import ViewTab
        
        # 入力タブ
        self.input_tab = InputTab(self.notebook, self.conn)
        self.notebook.add(self.input_tab.frame, text='📝 データ入力')
        
        # 閲覧タブ
        self.view_tab = ViewTab(self.notebook, self.conn)
        self.notebook.add(self.view_tab.frame, text='📋 データ閲覧')
        
        # 解析タブ（Phase 3で実装）
        from views.analysis_tab import AnalysisTab
        self.analysis_tab = AnalysisTab(self.notebook, self.conn)
        self.notebook.add(self.analysis_tab.frame, text='📊 解析・出力')
        
        # 地図タブ（Phase 4で実装）
        from views.map_tab import MapTab
        self.map_tab = MapTab(self.notebook, self.conn)
        self.notebook.add(self.map_tab.frame, text='🗺️ 地図')
        
        # 設定タブ（Phase 5で実装）
        from views.settings_tab import SettingsTab
        self.settings_tab = SettingsTab(self.notebook, self.conn)
        self.notebook.add(self.settings_tab.frame, text='⚙️ 設定')
    
    def _create_statusbar(self):
        """ステータスバーを作成"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side='bottom', fill='x')
        
        # ステータステキスト
        self.status_label = ttk.Label(self.statusbar, 
                                      text='準備完了', 
                                      relief='sunken',
                                      anchor='w')
        self.status_label.pack(side='left', fill='x', expand=True, padx=2, pady=2)
        
        # データベース情報
        db_path = self.config.get('Database', 'path', fallback='data/ant_database.db')
        self.db_label = ttk.Label(self.statusbar, 
                                  text=f'DB: {db_path}',
                                  relief='sunken')
        self.db_label.pack(side='right', padx=2, pady=2)
    
    def set_status(self, message: str):
        """
        ステータスバーにメッセージを表示
        
        Args:
            message: 表示するメッセージ
        """
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def _on_closing(self):
        """ウィンドウを閉じる際の処理"""
        if messagebox.askokcancel("終了確認", "アプリケーションを終了しますか？"):
            self.root.destroy()
    
    def run(self):
        """アプリケーションを実行"""
        self.root.mainloop()


if __name__ == "__main__":
    # テスト実行
    import sys
    sys.path.append('..')
    from models.database import Database
    
    db = Database()
    db.initialize_schema()
    
    app = MainWindow(db.get_connection())
    app.run()