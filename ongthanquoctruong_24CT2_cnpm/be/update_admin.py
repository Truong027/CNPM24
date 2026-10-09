import mysql.connector

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='HTTT_QuanLyBaiXe_AI'
    )
    cursor = conn.cursor()
    cursor.execute("UPDATE app_users SET phone = username WHERE role IN ('Admin', 'Operator') AND (phone IS NULL OR phone = '')")
    conn.commit()
    print("Updated admin and operator phone numbers successfully.")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
