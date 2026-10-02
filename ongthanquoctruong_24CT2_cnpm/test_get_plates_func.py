import database

print("Testing get_all_plates_with_details()...")
plates = database.get_all_plates_with_details()
print(f"Returned: {type(plates)}")
print(f"Length: {len(plates)}")
if len(plates) > 0:
    print(f"First plate: {plates[0]}")
else:
    print("❌ Empty result!")

# Also test direct query
print("\n\nTesting direct SQL query...")
conn = database.get_db_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) as cnt FROM plates")
    result = cursor.fetchone()
    print(f"Total plates in DB: {result['cnt']}")
    cursor.close()
    conn.close()
