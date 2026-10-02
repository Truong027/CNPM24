"""
Test save_plate_to_db function
"""
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "be"))
if BE_DIR not in sys.path:
    sys.path.insert(0, BE_DIR)

import database
import app

# Test 1: Save new plate với province_code
print("Test 1: Save new plate '51G-99999' với province '51'")
result = app.save_plate_to_db('51G-99999', province_code='51', vehicle_type='Ô tô con', confidence=0.99)
print(f"Result: {result}\n")

# Test 2: Check database
print("Test 2: Check database")
plates = database.get_all_plates_with_details()
target = next((p for p in plates if p['plate_text'] == '51G-99999'), None)
if target:
    print(f"Plate: {target['plate_text']}")
    print(f"Province Code: {target['province_code']}")
    print(f"Province Name: {target['province_name']}")
    print(f"Vehicle Type: {target['vehicle_type']}")
else:
    print("❌ Biển số không được tìm thấy!")

# Test 3: Save same plate again (duplicate)
print("\nTest 3: Save same plate again (should update detection_count)")
result = app.save_plate_to_db('51G-99999', province_code='51', vehicle_type='Ô tô con', confidence=0.98)
print(f"Result: {result}\n")

# Test 4: Check again
print("Test 4: Check after duplicate insert")
plates = database.get_all_plates_with_details()
target = next((p for p in plates if p['plate_text'] == '51G-99999'), None)
if target:
    print(f"Plate: {target['plate_text']}")
    print(f"Detection Count: {target['detection_count']}")
    print(f"Province Code: {target['province_code']}")
    print(f"Vehicle Type: {target['vehicle_type']}")
else:
    print("❌ Biển số không được tìm thấy!")
