"""
解析・出力タブ
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from controllers.export_controller import ExportController
from controllers.analysis_controller import AnalysisController
import os


class AnalysisTab:
    """解析・出力タブクラス"""
    
    def __init__(self, parent, db_connection):
        """
        初期化
        
        Args:
            parent: 親ウィジェット
            db_connection: データベース接続
        """
        self.conn = db_connection
        self.export_controller = ExportController(db_connection)
        self.analysis_controller = AnalysisController(db_connection)
        
        # メインフレーム
        self.frame = ttk.Frame(parent)
        
        # サブタブを作成
        self.sub_notebook = ttk.Notebook(self.frame)
        self.sub_notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 各サブタブ
        self._create_export_tab()
        self._create_diversity_tab()
        self._create_scatter_tab()
        self._create_stats_tab()
    
    def _create_export_tab(self):
        """データ出力タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='データ出力')
        
        # タイトル
        title_frame = ttk.Frame(tab)
        title_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(title_frame, text='データ出力・エクスポート', 
                 style='Header.TLabel').pack(anchor='w')
        
        # エクスポート可能データのサマリー
        summary_frame = ttk.LabelFrame(tab, text='エクスポート可能なデータ', padding=10)
        summary_frame.pack(fill='x', padx=20, pady=10)
        
        self.summary_text = tk.Text(summary_frame, height=8, width=60, 
                                   state='disabled', wrap='word')
        self.summary_text.pack(fill='x')
        
        ttk.Button(summary_frame, text='🔄 更新', 
                  command=self._update_export_summary).pack(pady=5)
        
        self._update_export_summary()
        
        # エクスポートオプション
        export_frame = ttk.LabelFrame(tab, text='エクスポート', padding=15)
        export_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # アリ類群集行列
        ant_frame = ttk.Frame(export_frame)
        ant_frame.pack(fill='x', pady=10)
        
        ttk.Label(ant_frame, text='アリ類群集行列:', 
                 font=('Yu Gothic UI', 10, 'bold')).pack(anchor='w', pady=5)
        
        btn_frame1 = ttk.Frame(ant_frame)
        btn_frame1.pack(fill='x')
        
        ttk.Button(btn_frame1, text='在不在データ (0/1) を出力', 
                  command=lambda: self._export_ant_matrix('presence')).pack(
                      side='left', padx=5)
        ttk.Button(btn_frame1, text='個体数データを出力', 
                  command=lambda: self._export_ant_matrix('count')).pack(
                      side='left', padx=5)
        
        ttk.Separator(export_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # 植生データ
        veg_frame = ttk.Frame(export_frame)
        veg_frame.pack(fill='x', pady=10)
        
        ttk.Label(veg_frame, text='植生データ:', 
                 font=('Yu Gothic UI', 10, 'bold')).pack(anchor='w', pady=5)
        
        ttk.Button(veg_frame, text='植生データ行列を出力', 
                  command=self._export_vegetation).pack(side='left', padx=5)
        
        ttk.Separator(export_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # 統合データ
        combined_frame = ttk.Frame(export_frame)
        combined_frame.pack(fill='x', pady=10)
        
        ttk.Label(combined_frame, text='統合データ:', 
                 font=('Yu Gothic UI', 10, 'bold')).pack(anchor='w', pady=5)
        
        ttk.Button(combined_frame, text='植生+多様度データを出力', 
                  command=self._export_combined).pack(side='left', padx=5)
        
        ttk.Separator(export_frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Excelファイル
        excel_frame = ttk.Frame(export_frame)
        excel_frame.pack(fill='x', pady=10)
        
        ttk.Label(excel_frame, text='Excel出力:', 
                 font=('Yu Gothic UI', 10, 'bold')).pack(anchor='w', pady=5)
        
        ttk.Button(excel_frame, text='全データをExcelで出力', 
                  command=self._export_excel,
                  style='Accent.TButton').pack(side='left', padx=5)
        
        # 出力先フォルダを開く
        ttk.Button(export_frame, text='📁 出力先フォルダを開く', 
                  command=self._open_export_folder).pack(pady=10)
    
    def _create_diversity_tab(self):
        """多様度分析タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='多様度分析')
        
        # 左側：設定とボタン
        left_frame = ttk.Frame(tab)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        ttk.Label(left_frame, text='種多様度指数', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        info_text = """
計算される指標:
• 種数（Species Richness）
• Shannon多様度指数
• Simpson多様度指数
• Pielou均等度
• Berger-Parker優占度
        """
        
        ttk.Label(left_frame, text=info_text, justify='left').pack(
            anchor='w', pady=10)
        
        ttk.Button(left_frame, text='多様度指数を計算', 
                  command=self._calculate_diversity).pack(pady=10)
        
        ttk.Button(left_frame, text='比較グラフを表示', 
                  command=self._show_diversity_comparison).pack(pady=5)
        
        ttk.Button(left_frame, text='種数累積曲線を表示', 
                  command=self._show_accumulation_curve).pack(pady=5)
        
        ttk.Button(left_frame, text='CSVに出力', 
                  command=self._export_diversity).pack(pady=10)
        
        # 右側：結果表示
        right_frame = ttk.Frame(tab)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(right_frame, text='計算結果', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Treeview
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.diversity_tree = ttk.Treeview(
            tree_frame,
            columns=('site', 'richness', 'shannon', 'simpson', 'pielou'),
            show='headings',
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.diversity_tree.yview)
        
        self.diversity_tree.heading('site', text='調査地')
        self.diversity_tree.heading('richness', text='種数')
        self.diversity_tree.heading('shannon', text='Shannon')
        self.diversity_tree.heading('simpson', text='Simpson')
        self.diversity_tree.heading('pielou', text='Pielou')
        
        self.diversity_tree.column('site', width=200)
        self.diversity_tree.column('richness', width=80)
        self.diversity_tree.column('shannon', width=100)
        self.diversity_tree.column('simpson', width=100)
        self.diversity_tree.column('pielou', width=100)
        
        self.diversity_tree.pack(fill='both', expand=True)
    
    def _create_scatter_tab(self):
        """散布図タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='散布図・相関分析')
        
        # 左側：設定
        left_frame = ttk.Frame(tab)
        left_frame.pack(side='left', fill='y', padx=10, pady=10)
        
        ttk.Label(left_frame, text='散布図の作成', 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # 変数選択
        var_frame = ttk.LabelFrame(left_frame, text='変数選択', padding=10)
        var_frame.pack(fill='x', pady=10)
        
        variables = {
            'basal_area': '胸高断面積',
            'avg_tree_height': '平均樹高',
            'avg_herb_height': '平均草丈',
            'soil_temperature': '地温',
            'canopy_coverage': '樹冠被度',
            'sasa_coverage': 'ササ被度',
            'herb_coverage': '草本被度',
            'litter_coverage': 'リター被度',
            'light_condition': '光条件',
            'soil_moisture': '土湿条件',
            'vegetation_complexity': '植生複雑度'
        }
        
        self.var_dict = variables
        
        ttk.Label(var_frame, text='X軸:').pack(anchor='w', pady=2)
        self.x_var = tk.StringVar()
        x_combo = ttk.Combobox(var_frame, textvariable=self.x_var, 
                              values=list(variables.values()), 
                              state='readonly', width=25)
        x_combo.pack(fill='x', pady=2)
        x_combo.current(4)  # 樹冠被度
        
        ttk.Label(var_frame, text='Y軸:').pack(anchor='w', pady=(10, 2))
        self.y_var = tk.StringVar()
        y_combo = ttk.Combobox(var_frame, textvariable=self.y_var, 
                              values=list(variables.values()), 
                              state='readonly', width=25)
        y_combo.pack(fill='x', pady=2)
        y_combo.current(8)  # 光条件
        
        # オプション
        self.show_regression = tk.BooleanVar(value=True)
        ttk.Checkbutton(var_frame, text='回帰直線を表示', 
                       variable=self.show_regression).pack(anchor='w', pady=10)
        
        ttk.Button(left_frame, text='散布図を作成', 
                  command=self._create_scatter).pack(pady=10)
        
        # 相関係数表示
        self.corr_label = ttk.Label(left_frame, text='', 
                                   font=('Yu Gothic UI', 10))
        self.corr_label.pack(pady=10)
        
        # 右側：グラフ表示
        right_frame = ttk.Frame(tab)
        right_frame.pack(side='right', fill='both', expand=True, padx=10, pady=10)
        
        self.scatter_canvas_frame = right_frame
    
    def _create_stats_tab(self):
        """基本統計量タブを作成"""
        tab = ttk.Frame(self.sub_notebook)
        self.sub_notebook.add(tab, text='基本統計量')
        
        ttk.Label(tab, text='植生データの基本統計量', 
                 style='Header.TLabel').pack(anchor='w', padx=20, pady=10)
        
        ttk.Button(tab, text='統計量を計算', 
                  command=self._calculate_stats).pack(pady=10)
        
        # Treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        h_scrollbar = ttk.Scrollbar(tree_frame, orient='horizontal')
        h_scrollbar.pack(side='bottom', fill='x')
        
        v_scrollbar = ttk.Scrollbar(tree_frame)
        v_scrollbar.pack(side='right', fill='y')
        
        self.stats_tree = ttk.Treeview(
            tree_frame,
            columns=('variable', 'count', 'mean', 'std', 'min', 'q25', 'median', 'q75', 'max'),
            show='headings',
            xscrollcommand=h_scrollbar.set,
            yscrollcommand=v_scrollbar.set
        )
        
        h_scrollbar.config(command=self.stats_tree.xview)
        v_scrollbar.config(command=self.stats_tree.yview)
        
        headings = ['変数', '件数', '平均', '標準偏差', '最小値', '25%', '中央値', '75%', '最大値']
        for col, heading in zip(self.stats_tree['columns'], headings):
            self.stats_tree.heading(col, text=heading)
            self.stats_tree.column(col, width=100)
        
        self.stats_tree.pack(fill='both', expand=True)
    
    # エクスポート関連メソッド
    def _update_export_summary(self):
        """エクスポートサマリーを更新"""
        summary = self.export_controller.get_export_summary()
        
        self.summary_text.config(state='normal')
        self.summary_text.delete('1.0', 'end')
        
        text = "エクスポート可能なデータ件数:\n\n"
        for name, count in summary.items():
            text += f"  {name}: {count:,} 件\n"
        
        self.summary_text.insert('1.0', text)
        self.summary_text.config(state='disabled')
    
    def _export_ant_matrix(self, value_type):
        """アリ類群集行列を出力"""
        try:
            filepath = self.export_controller.export_ant_matrix(value_type)
            messagebox.showinfo('成功', 
                f'アリ類群集行列を出力しました\n\n{filepath}')
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'出力に失敗しました：{e}')
    
    def _export_vegetation(self):
        """植生データを出力"""
        try:
            filepath = self.export_controller.export_vegetation_matrix()
            messagebox.showinfo('成功', 
                f'植生データを出力しました\n\n{filepath}')
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'出力に失敗しました：{e}')
    
    def _export_combined(self):
        """統合データを出力"""
        try:
            filepath = self.export_controller.export_combined_data()
            messagebox.showinfo('成功', 
                f'統合データを出力しました\n\n{filepath}')
        except Exception as e:
            messagebox.showerror('エラー', f'出力に失敗しました：{e}')
    
    def _export_excel(self):
        """Excelファイルを出力"""
        try:
            filepath = self.export_controller.export_to_excel()
            messagebox.showinfo('成功', 
                f'Excelファイルを出力しました\n\n{filepath}')
        except Exception as e:
            messagebox.showerror('エラー', f'出力に失敗しました：{e}')
    
    def _open_export_folder(self):
        """出力先フォルダを開く"""
        import subprocess
        import platform
        
        export_dir = os.path.abspath(self.export_controller.export_dir)
        
        if platform.system() == 'Windows':
            os.startfile(export_dir)
        elif platform.system() == 'Darwin':  # macOS
            subprocess.Popen(['open', export_dir])
        else:  # Linux
            subprocess.Popen(['xdg-open', export_dir])
    
    # 多様度分析関連メソッド
    def _calculate_diversity(self):
        """多様度指数を計算"""
        try:
            df = self.analysis_controller.calculate_diversity_indices()
            
            if df.empty:
                messagebox.showwarning('警告', 'データがありません')
                return
            
            # Treeviewに表示
            for item in self.diversity_tree.get_children():
                self.diversity_tree.delete(item)
            
            for _, row in df.iterrows():
                self.diversity_tree.insert('', 'end', values=(
                    row['site_name'],
                    row['species_richness'],
                    row['shannon_index'],
                    row['simpson_index'],
                    row['pielou_evenness']
                ))
            
            messagebox.showinfo('成功', f'{len(df)}件の調査地について計算しました')
            
        except Exception as e:
            messagebox.showerror('エラー', f'計算に失敗しました：{e}')
    
    def _show_diversity_comparison(self):
        """多様度比較グラフを表示"""
        try:
            fig = self.analysis_controller.create_diversity_comparison()
            plt.show()
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'グラフ作成に失敗しました：{e}')
    
    def _show_accumulation_curve(self):
        """種数累積曲線を表示"""
        try:
            fig = self.analysis_controller.create_species_accumulation_curve()
            plt.show()
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'グラフ作成に失敗しました：{e}')
    
    def _export_diversity(self):
        """多様度データをCSV出力"""
        try:
            df = self.analysis_controller.calculate_diversity_indices()
            
            if df.empty:
                messagebox.showwarning('警告', 'データがありません')
                return
            
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"diversity_indices_{timestamp}.csv"
            filepath = os.path.join(self.export_controller.export_dir, filename)
            
            df.to_csv(filepath, encoding='utf-8-sig', index=False)
            
            messagebox.showinfo('成功', f'多様度指数を出力しました\n\n{filepath}')
            
        except Exception as e:
            messagebox.showerror('エラー', f'出力に失敗しました：{e}')
    
    # 散布図関連メソッド
    def _create_scatter(self):
        """散布図を作成"""
        try:
            x_label = self.x_var.get()
            y_label = self.y_var.get()
            
            if not x_label or not y_label:
                messagebox.showwarning('警告', 'X軸とY軸の変数を選択してください')
                return
            
            # 変数名を取得（逆引き）
            x_name = [k for k, v in self.var_dict.items() if v == x_label][0]
            y_name = [k for k, v in self.var_dict.items() if v == y_label][0]
            
            fig = self.analysis_controller.create_scatter_plot(
                x_name, y_name, x_label, y_label, 
                self.show_regression.get()
            )
            
            # 既存のキャンバスをクリア
            for widget in self.scatter_canvas_frame.winfo_children():
                widget.destroy()
            
            # 新しいキャンバスを作成
            canvas = FigureCanvasTkAgg(fig, self.scatter_canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # 相関係数を表示
            result = self.analysis_controller.calculate_correlation(x_name, y_name)
            self.corr_label.config(
                text=f"相関係数: {result['correlation']:.4f}\n"
                     f"p値: {result['p_value']:.4f}\n"
                     f"サンプル数: {result['n']}"
            )
            
        except ValueError as e:
            messagebox.showerror('エラー', str(e))
        except Exception as e:
            messagebox.showerror('エラー', f'グラフ作成に失敗しました：{e}')
    
    # 統計量関連メソッド
    def _calculate_stats(self):
        """基本統計量を計算"""
        try:
            df = self.analysis_controller.get_vegetation_summary_stats()
            
            if df.empty:
                messagebox.showwarning('警告', 'データがありません')
                return
            
            # Treeviewに表示
            for item in self.stats_tree.get_children():
                self.stats_tree.delete(item)
            
            for variable, row in df.iterrows():
                self.stats_tree.insert('', 'end', values=(
                    variable,
                    int(row['件数']),
                    f"{row['平均']:.2f}",
                    f"{row['標準偏差']:.2f}",
                    f"{row['最小値']:.2f}",
                    f"{row['25%']:.2f}",
                    f"{row['中央値']:.2f}",
                    f"{row['75%']:.2f}",
                    f"{row['最大値']:.2f}"
                ))
            
            messagebox.showinfo('成功', '基本統計量を計算しました')
            
        except Exception as e:
            messagebox.showerror('エラー', f'計算に失敗しました：{e}')
