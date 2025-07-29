import pandas as pd
import json

file_path = r"C:\Users\pk\Desktop\карта\карта\karta_vue\public\111.xlsx"
df = pd.read_excel(file_path)

# Автоматический поиск столбцов по ключевым словам
def find_col(keyword):
    for col in df.columns:
        if keyword.lower() in col.lower():
            return col
    raise ValueError(f"Столбец с ключевым словом '{keyword}' не найден")

col_id           = find_col("№")
col_name         = find_col("Краткое наименование организации")
col_address      = find_col("Адрес организации")
col_website      = find_col("сайт")
col_phone        = find_col("телефон")
col_coords       = find_col("координаты")
col_rehab_form   = find_col("форма провед")
col_age_group    = find_col("возрастная")
col_access       = find_col("доступ")
col_profile      = find_col("профиль")
col_services     = find_col("услуг")
col_specialists  = find_col("специалист")

features = []

for idx, row in df.iterrows():
    # Пропуск пустых координат
    coords = row[col_coords]
    if pd.isna(coords):
        continue
    try:
        lat_str, lon_str = str(coords).split(',')
        lat, lon = float(lat_str.strip()), float(lon_str.strip())
    except Exception:
        continue

    feature = {
        "type": "Feature",
        "id": int(row[col_id]) if not pd.isna(row[col_id]) else idx + 1,
        "geometry": {
            "type": "Point",
            "coordinates": [lat, lon]
        },
        "properties": {
            "name": str(row[col_name]).strip(),
            "address": str(row[col_address]).strip(),
            "website": str(row[col_website]).strip(),
            "phone": str(row[col_phone]).strip(),
            "rehab_form": str(row[col_rehab_form]).strip(),
            "age_group": str(row[col_age_group]).strip(),
            "accessibility": str(row[col_access]).strip(),
            "profile": str(row[col_profile]).strip(),
            "services": str(row[col_services]).strip(),
            "specialists": str(row[col_specialists]).strip(),
            "description": f"{row[col_profile]}\n{row[col_services]}"
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open("output.json", "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)
