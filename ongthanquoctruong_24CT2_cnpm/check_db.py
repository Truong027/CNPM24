import database

plates = database.get_all_plates_with_details()
print(f'Tổng biển số: {len(plates)}')
for p in plates[:5]:
    print(f"{p['plate_text']} -> Tỉnh: {p['province_name']}, Loại xe: {p['type_name']}")
