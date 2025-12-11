"""
データバリデーションユーティリティ
"""
import re
from datetime import datetime
from typing import Optional, Tuple


class Validators:
    """バリデーションクラス"""
    
    @staticmethod
    def validate_latitude(value: str) -> Tuple[bool, Optional[float], str]:
        """
        緯度のバリデーション
        
        Args:
            value: 入力値
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return False, None, "緯度を入力してください"
        
        try:
            lat = float(value)
            if -90 <= lat <= 90:
                return True, lat, ""
            else:
                return False, None, "緯度は-90～90の範囲で入力してください"
        except ValueError:
            return False, None, "緯度は数値で入力してください"
    
    @staticmethod
    def validate_longitude(value: str) -> Tuple[bool, Optional[float], str]:
        """
        経度のバリデーション
        
        Args:
            value: 入力値
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return False, None, "経度を入力してください"
        
        try:
            lon = float(value)
            if -180 <= lon <= 180:
                return True, lon, ""
            else:
                return False, None, "経度は-180～180の範囲で入力してください"
        except ValueError:
            return False, None, "経度は数値で入力してください"
    
    @staticmethod
    def validate_positive_number(value: str, field_name: str = "値") -> Tuple[bool, Optional[float], str]:
        """
        正の数のバリデーション
        
        Args:
            value: 入力値
            field_name: フィールド名
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return True, None, ""  # 任意項目として扱う
        
        try:
            num = float(value)
            if num >= 0:
                return True, num, ""
            else:
                return False, None, f"{field_name}は0以上の数値で入力してください"
        except ValueError:
            return False, None, f"{field_name}は数値で入力してください"
    
    @staticmethod
    def validate_percentage(value: str, field_name: str = "被度") -> Tuple[bool, Optional[float], str]:
        """
        パーセンテージ（0-100）のバリデーション
        
        Args:
            value: 入力値
            field_name: フィールド名
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return True, None, ""  # 任意項目として扱う
        
        try:
            num = float(value)
            if 0 <= num <= 100:
                return True, num, ""
            else:
                return False, None, f"{field_name}は0～100の範囲で入力してください"
        except ValueError:
            return False, None, f"{field_name}は数値で入力してください"
    
    @staticmethod
    def validate_scale_1_to_5(value: str, field_name: str = "段階評価") -> Tuple[bool, Optional[int], str]:
        """
        1-5段階評価のバリデーション
        
        Args:
            value: 入力値
            field_name: フィールド名
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return True, None, ""  # 任意項目として扱う
        
        try:
            num = int(value)
            if 1 <= num <= 5:
                return True, num, ""
            else:
                return False, None, f"{field_name}は1～5の範囲で入力してください"
        except ValueError:
            return False, None, f"{field_name}は整数で入力してください"
    
    @staticmethod
    def validate_integer(value: str, field_name: str = "個体数", 
                        min_val: int = 0) -> Tuple[bool, Optional[int], str]:
        """
        整数のバリデーション
        
        Args:
            value: 入力値
            field_name: フィールド名
            min_val: 最小値
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return False, None, f"{field_name}を入力してください"
        
        try:
            num = int(value)
            if num >= min_val:
                return True, num, ""
            else:
                return False, None, f"{field_name}は{min_val}以上の整数で入力してください"
        except ValueError:
            return False, None, f"{field_name}は整数で入力してください"
    
    @staticmethod
    def validate_date(value: str) -> Tuple[bool, Optional[str], str]:
        """
        日付のバリデーション
        
        Args:
            value: 入力値（YYYY-MM-DD形式）
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return False, None, "日付を入力してください"
        
        try:
            # YYYY-MM-DD形式のチェック
            datetime.strptime(value, '%Y-%m-%d')
            return True, value, ""
        except ValueError:
            return False, None, "日付はYYYY-MM-DD形式で入力してください（例: 2025-12-10）"
    
    @staticmethod
    def validate_datetime(value: str) -> Tuple[bool, Optional[str], str]:
        """
        日時のバリデーション
        
        Args:
            value: 入力値（YYYY-MM-DD HH:MM形式）
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return False, None, "日時を入力してください"
        
        try:
            # YYYY-MM-DD HH:MM形式のチェック
            datetime.strptime(value, '%Y-%m-%d %H:%M')
            return True, value, ""
        except ValueError:
            # YYYY-MM-DD形式も許可（時刻は00:00とする）
            try:
                datetime.strptime(value, '%Y-%m-%d')
                return True, f"{value} 00:00", ""
            except ValueError:
                return False, None, "日時はYYYY-MM-DD HH:MM形式で入力してください（例: 2025-12-10 14:30）"
    
    @staticmethod
    def validate_species_name(value: str) -> Tuple[bool, Optional[str], str]:
        """
        種名（学名）のバリデーション
        
        Args:
            value: 入力値
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return False, None, "種名を入力してください"
        
        name = value.strip()
        
        # 学名の基本形式チェック（属名 + 種小名）
        # 例: Formica japonica
        pattern = r'^[A-Z][a-z]+\s+[a-z]+.*$'
        
        if re.match(pattern, name):
            return True, name, ""
        else:
            # 警告のみで許可（日本語名なども許容）
            return True, name, ""
    
    @staticmethod
    def validate_text_length(value: str, max_length: int = 1000, 
                           field_name: str = "テキスト") -> Tuple[bool, Optional[str], str]:
        """
        テキストの長さをバリデーション
        
        Args:
            value: 入力値
            max_length: 最大文字数
            field_name: フィールド名
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return True, None, ""  # 空は許可
        
        text = value.strip()
        
        if len(text) <= max_length:
            return True, text, ""
        else:
            return False, None, f"{field_name}は{max_length}文字以内で入力してください"
    
    @staticmethod
    def validate_required(value: str, field_name: str = "項目") -> Tuple[bool, str]:
        """
        必須項目のバリデーション
        
        Args:
            value: 入力値
            field_name: フィールド名
            
        Returns:
            (有効か, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return False, f"{field_name}は必須項目です"
        return True, ""
    
    @staticmethod
    def validate_weather(value: str) -> Tuple[bool, Optional[str], str]:
        """
        天候のバリデーション
        
        Args:
            value: 入力値
            
        Returns:
            (有効か, 変換後の値, エラーメッセージ)
        """
        if not value or value.strip() == '':
            return True, None, ""  # 任意項目
        
        valid_weather = ['晴れ', '曇り', '雨', '雪']
        
        if value in valid_weather:
            return True, value, ""
        else:
            return False, None, f"天候は「{', '.join(valid_weather)}」のいずれかを選択してください"


class ValidationError(Exception):
    """バリデーションエラー"""
    pass


def validate_form_data(data: dict, rules: dict) -> dict:
    """
    フォームデータを一括バリデーション
    
    Args:
        data: 検証するデータ
        rules: バリデーションルール
        
    Returns:
        dict: 検証済みデータ
        
    Raises:
        ValidationError: バリデーションエラー
    """
    validated = {}
    errors = []
    
    for field, rule in rules.items():
        value = data.get(field, '')
        
        if rule['type'] == 'latitude':
            is_valid, val, msg = Validators.validate_latitude(value)
        elif rule['type'] == 'longitude':
            is_valid, val, msg = Validators.validate_longitude(value)
        elif rule['type'] == 'positive':
            is_valid, val, msg = Validators.validate_positive_number(value, rule.get('name', field))
        elif rule['type'] == 'percentage':
            is_valid, val, msg = Validators.validate_percentage(value, rule.get('name', field))
        elif rule['type'] == 'scale':
            is_valid, val, msg = Validators.validate_scale_1_to_5(value, rule.get('name', field))
        elif rule['type'] == 'integer':
            is_valid, val, msg = Validators.validate_integer(value, rule.get('name', field))
        elif rule['type'] == 'date':
            is_valid, val, msg = Validators.validate_date(value)
        elif rule['type'] == 'datetime':
            is_valid, val, msg = Validators.validate_datetime(value)
        else:
            is_valid, val, msg = True, value, ""
        
        if not is_valid:
            errors.append(msg)
        else:
            if val is not None:
                validated[field] = val
    
    if errors:
        raise ValidationError("\n".join(errors))
    
    return validated
