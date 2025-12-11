"""
サンプルデータ生成ユーティリティ
"""
import random
from datetime import datetime, timedelta
from models.parent_site import ParentSite
from models.survey_site import SurveySite
from models.survey_event import SurveyEvent
from models.vegetation import Vegetation
from models.species import Species
from models.ant_record import AntRecord


def generate_sample_data(database, num_parent_sites=10, num_survey_sites=50, 
                         num_events=20, num_species=30):
    """
    サンプルデータを生成
    
    Args:
        database: Databaseオブジェクト
        num_parent_sites: 生成する親調査地の数
        num_survey_sites: 生成する調査地の数
        num_events: 生成する調査イベントの数
        num_species: 生成するアリ種の数
    """
    conn = database.connect()
    
    parent_site_model = ParentSite(conn)
    survey_site_model = SurveySite(conn)
    survey_event_model = SurveyEvent(conn)
    vegetation_model = Vegetation(conn)
    species_model = Species(conn)
    ant_record_model = AntRecord(conn)
    
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
    
    # Phase 2: アリ種マスタを生成
    print(f"\n  アリ種を {num_species} 種生成中...")
    
    ant_species_data = [
        ('Formica japonica', 'Formica', 'Formicinae'),
        ('Camponotus japonicus', 'Camponotus', 'Formicinae'),
        ('Lasius japonicus', 'Lasius', 'Formicinae'),
        ('Tetramorium tsushimae', 'Tetramorium', 'Myrmicinae'),
        ('Pheidole noda', 'Pheidole', 'Myrmicinae'),
        ('Crematogaster matsumurai', 'Crematogaster', 'Myrmicinae'),
        ('Myrmica kotokui', 'Myrmica', 'Myrmicinae'),
        ('Aphaenogaster famelica', 'Aphaenogaster', 'Myrmicinae'),
        ('Leptothorax congruus', 'Leptothorax', 'Myrmicinae'),
        ('Stenamma owstoni', 'Stenamma', 'Myrmicinae'),
        ('Vollenhovia emeryi', 'Vollenhovia', 'Myrmicinae'),
        ('Paratrechina sakurae', 'Paratrechina', 'Formicinae'),
        ('Polyrhachis lamellidens', 'Polyrhachis', 'Formicinae'),
        ('Prenolepis imparis', 'Prenolepis', 'Formicinae'),
        ('Nylanderia flavipes', 'Nylanderia', 'Formicinae'),
    ]
    
    species_ids = []
    for name, genus, subfamily in ant_species_data[:min(num_species, len(ant_species_data))]:
        try:
            species_id = species_model.create(name=name, genus=genus, subfamily=subfamily)
            species_ids.append(species_id)
        except Exception as e:
            print(f"    ⚠ 種の生成でエラー: {e}")
    
    # 不足分はランダム生成
    while len(species_ids) < num_species:
        genera = ['Formica', 'Camponotus', 'Lasius', 'Pheidole', 'Tetramorium']
        genus = random.choice(genera)
        species_name = f"{genus} sp.{len(species_ids) + 1}"
        try:
            species_id = species_model.create(name=species_name, genus=genus, subfamily='Formicinae')
            species_ids.append(species_id)
        except:
            pass
    
    print(f"  ✓ {len(species_ids)} 種のアリを生成しました")
    
    # Phase 2: 調査イベントを生成
    print(f"\n  調査イベントを {num_events} 件生成中...")
    
    # 調査地リストを取得
    survey_sites = survey_site_model.get_all()
    if not survey_sites:
        print("    ⚠ 調査地がないため調査イベントを生成できません")
        conn.commit()
        database.close()
        return
    
    weather_options = ['晴れ', '曇り', '雨', '雪']
    event_ids = []
    
    # 過去6ヶ月間のランダムな日付で生成
    base_date = datetime.now()
    
    for i in range(num_events):
        site = random.choice(survey_sites)
        
        # ランダムな日付（過去6ヶ月）
        days_ago = random.randint(0, 180)
        survey_date = base_date - timedelta(days=days_ago)
        survey_datetime = survey_date.strftime('%Y-%m-%d') + ' ' + f"{random.randint(8, 16):02d}:00"
        
        weather = random.choice(weather_options)
        temperature = round(random.uniform(5, 30), 1)
        
        try:
            event_id = survey_event_model.create(
                survey_site_id=site['id'],
                survey_date=survey_datetime,
                surveyor_name=random.choice(['研究者A', '研究者B', '研究者C', None]),
                weather=weather,
                temperature=temperature,
                remarks=f"サンプル調査イベント {i+1}"
            )
            event_ids.append(event_id)
        except Exception as e:
            print(f"    ⚠ イベントの生成でエラー: {e}")
    
    print(f"  ✓ {len(event_ids)} 件の調査イベントを生成しました")
    
    # Phase 2: 植生データを生成
    print(f"\n  植生データを生成中...")
    
    tree_species_list = ['ブナ', 'ミズナラ', 'コナラ', 'スギ', 'ヒノキ', 
                         'カラマツ', 'アカマツ', 'クロマツ', 'シイ', 'カシ']
    sasa_species = ['スズタケ', 'チシマザサ', 'ミヤコザサ', None]
    
    veg_count = 0
    for event_id in event_ids:
        try:
            vegetation_model.create(
                survey_event_id=event_id,
                dominant_tree=random.choice(tree_species_list),
                dominant_sasa=random.choice(sasa_species),
                dominant_herb=random.choice(['イタドリ', 'ススキ', 'オオバコ', None]),
                litter_type=random.choice(['広葉樹', '針葉樹', '混合', None]),
                basal_area=round(random.uniform(10, 50), 1),
                avg_tree_height=round(random.uniform(5, 25), 1),
                avg_herb_height=round(random.uniform(10, 100), 1),
                soil_temperature=round(random.uniform(5, 25), 1),
                canopy_coverage=round(random.uniform(20, 95), 1),
                sasa_coverage=round(random.uniform(0, 80), 1),
                herb_coverage=round(random.uniform(5, 60), 1),
                litter_coverage=round(random.uniform(30, 90), 1),
                light_condition=random.randint(1, 5),
                soil_moisture=random.randint(1, 5),
                vegetation_complexity=random.randint(1, 5)
            )
            veg_count += 1
        except Exception as e:
            print(f"    ⚠ 植生データの生成でエラー: {e}")
    
    print(f"  ✓ {veg_count} 件の植生データを生成しました")
    
    # Phase 2: アリ類出現記録を生成
    print(f"\n  アリ類出現記録を生成中...")
    
    record_count = 0
    for event_id in event_ids:
        # 各イベントで3-10種のアリが出現
        num_species_in_event = random.randint(3, min(10, len(species_ids)))
        selected_species = random.sample(species_ids, num_species_in_event)
        
        for species_id in selected_species:
            try:
                # 個体数は1-100の範囲
                count = random.randint(1, 100)
                
                ant_record_model.create(
                    survey_event_id=event_id,
                    species_id=species_id,
                    count=count,
                    remarks=None
                )
                record_count += 1
            except Exception as e:
                # UNIQUE制約違反などは無視
                pass
    
    print(f"  ✓ {record_count} 件のアリ類出現記録を生成しました")
    
    conn.commit()
    database.close()
    
    print(f"\n  📊 Phase 2 サンプルデータ生成完了:")
    print(f"     - 親調査地:         {len(parent_site_ids)} 件")
    print(f"     - 調査地:           {survey_count} 件")
    print(f"     - アリ種:           {len(species_ids)} 種")
    print(f"     - 調査イベント:     {len(event_ids)} 件")
    print(f"     - 植生データ:       {veg_count} 件")
    print(f"     - アリ類出現記録:   {record_count} 件")


if __name__ == "__main__":
    # テスト実行
    import sys
    sys.path.append('..')
    from models.database import Database
    
    db = Database()
    db.initialize_schema()
    generate_sample_data(db)
