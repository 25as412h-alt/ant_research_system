"""
サンプルデータ生成ユーティリティ
"""
import random
from models.parent_site import ParentSite
from models.survey_site import SurveySite


def generate_sample_data(database, num_parent_sites=10, num_survey_sites=50):
    """
    サンプルデータを生成
    
    Args:
        database: Databaseオブジェクト
        num_parent_sites: 生成する親調査地の数
        num_survey_sites: 生成する調査地の数
    """
    conn = database.connect()
    
    parent_site_model = ParentSite(conn)
    survey_site_model = SurveySite(conn)
    
    # 日本の代表的な地域の座標範囲
    regions = [
        # (名称プレフィックス, 緯度中心, 経度中心, 標高範囲)
        ('北海道', 43.0, 141.3, (50, 500)),
        ('東北', 38.5, 140.5, (100, 800)),
        ('関東', 36.0, 139.5, (50, 1500)),
        ('中部', 35.5, 138.0, (200, 2000)),
        ('近畿', 35.0, 135.5, (50, 1000)),
        ('中国', 34.5, 133.5, (100, 1200)),
        ('四国', 33.5, 133.5, (50, 1500)),
        ('九州', 32.5, 130.5, (50, 1300)),
    ]
    
    # 環境タイプ
    environment_types = [
        '森林', '草地', '山地', '平地', '丘陵', '河川敷', '湿地', '海岸'
    ]
    
    # 樹種例
    tree_species = [
        'ブナ', 'ミズナラ', 'コナラ', 'スギ', 'ヒノキ', 
        'カラマツ', 'アカマツ', 'クロマツ', 'シイ', 'カシ'
    ]
    
    parent_site_ids = []
    
    print(f"  親調査地を {num_parent_sites} 件生成中...")
    
    # 親調査地を生成
    for i in range(num_parent_sites):
        region_name, base_lat, base_lon, alt_range = random.choice(regions)
        env_type = random.choice(environment_types)
        
        # ランダムな位置（基準点から±0.5度の範囲）
        latitude = base_lat + random.uniform(-0.5, 0.5)
        longitude = base_lon + random.uniform(-0.5, 0.5)
        altitude = random.uniform(*alt_range)
        
        name = f"{region_name}_{env_type}地点{i+1:02d}"
        
        try:
            parent_id = parent_site_model.create(
                name=name,
                latitude=round(latitude, 6),
                longitude=round(longitude, 6),
                altitude=round(altitude, 1),
                remarks=f"{region_name}地域の{env_type}に位置する調査地点"
            )
            parent_site_ids.append(parent_id)
        except Exception as e:
            print(f"    ⚠ 親調査地の生成でエラー: {e}")
    
    print(f"  ✓ {len(parent_site_ids)} 件の親調査地を生成しました")
    print(f"\n  調査地を {num_survey_sites} 件生成中...")
    
    # 調査地を生成
    survey_count = 0
    for i in range(num_survey_sites):
        if not parent_site_ids:
            break
        
        # ランダムに親調査地を選択
        parent_id = random.choice(parent_site_ids)
        parent_data = parent_site_model.get_by_id(parent_id)
        
        if not parent_data:
            continue
        
        # 親調査地の周辺（±0.01度以内）
        latitude = parent_data['latitude'] + random.uniform(-0.01, 0.01)
        longitude = parent_data['longitude'] + random.uniform(-0.01, 0.01)
        altitude = parent_data['altitude'] + random.uniform(-50, 50)
        
        # 面積（10-1000平方メートル）
        area = round(random.uniform(10, 1000), 1)
        
        # プロット名
        plot_type = random.choice(['A', 'B', 'C', 'D'])
        name = f"プロット{plot_type}{i+1:02d}"
        
        # 優占種
        dominant_tree = random.choice(tree_species)
        
        remarks = f"優占種: {dominant_tree}林"
        
        try:
            survey_site_model.create(
                parent_site_id=parent_id,
                name=name,
                latitude=round(latitude, 6),
                longitude=round(longitude, 6),
                altitude=round(altitude, 1),
                area=area,
                remarks=remarks
            )
            survey_count += 1
        except Exception as e:
            # 同名のプロットが既に存在する場合はスキップ
            pass
    
    print(f"  ✓ {survey_count} 件の調査地を生成しました")
    
    conn.commit()
    database.close()
    
    print(f"\n  📊 サンプルデータ生成完了:")
    print(f"     - 親調査地: {len(parent_site_ids)} 件")
    print(f"     - 調査地:   {survey_count} 件")


if __name__ == "__main__":
    # テスト実行
    import sys
    sys.path.append('..')
    from models.database import Database
    
    db = Database()
    db.initialize_schema()
    generate_sample_data(db)
