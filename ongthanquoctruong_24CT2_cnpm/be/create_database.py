#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tạo/cập nhật database HTTT_QuanLyBaiXe_AI
"""

import os
import mysql.connector
from mysql.connector import Error

# Tự động nạp .env nếu có
def _load_env():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    for env_path in [os.path.join(cur_dir, '.env'), os.path.join(cur_dir, '..', '.env'), os.path.join(os.getcwd(), '.env')]:
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            k, v = line.split('=', 1)
                            k, v = k.strip(), v.strip().strip("'\"")
                            if k not in os.environ:
                                os.environ[k] = v
            except Exception:
                pass
            break

_load_env()

# Thông tin kết nối MySQL an toàn
HOST = os.getenv('MYSQL_HOST', 'localhost')
USER = os.getenv('MYSQL_USER', 'root')
PASSWORD = os.getenv('MYSQL_PASSWORD', '')

def create_database():
    """Tạo database từ file SQL"""
    try:
        # Kết nối MySQL mà không có database cụ thể
        conn = mysql.connector.connect(
            host=HOST,
            user=USER,
            password=PASSWORD
        )
        
        if not conn.is_connected():
            print("❌ Không thể kết nối MySQL")
            return False
        
        cursor = conn.cursor()
        print("✅ Kết nối MySQL thành công")
        
        # Đọc file SQL
        with open('httt_quan_ly_bai_xe_ai.sql', 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Tách các câu lệnh SQL
        statements = sql_content.split(';')
        
        total = len([s for s in statements if s.strip()])
        executed = 0
        
        print(f"\n⌛ Đang thực thi {total} câu lệnh SQL...")
        
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    executed += 1
                    # In dấu tiến độ
                    if executed % 5 == 0:
                        print(f"  📊 {executed}/{total} ({executed*100//total}%)")
                except Error as e:
                    if "already exists" in str(e) or "already have a primary key" in str(e):
                        print(f"  ⚠️  {str(e)[:80]}")
                    else:
                        print(f"  ❌ Lỗi: {e}")
        
        conn.commit()
        print(f"\n✅ Đã thực thi {executed}/{total} câu lệnh thành công!")
        
        # Kiểm tra database đã được tạo
        cursor.execute("SHOW DATABASES LIKE 'HTTT_QuanLyBaiXe_AI'")
        if cursor.fetchone():
            print("✅ Database 'HTTT_QuanLyBaiXe_AI' đã được tạo thành công!")
            
            # Kiểm tra số bảng
            cursor.execute("USE HTTT_QuanLyBaiXe_AI")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✅ Tổng số bảng: {len(tables)}")
            
            # Liệt kê các bảng
            print("\n📋 Danh sách các bảng:")
            for table in tables:
                print(f"  • {table[0]}")
        else:
            print("❌ Database không được tạo!")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"❌ Lỗi MySQL: {e}")
        return False
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 TẠO DATABASE HTTT_QuanLyBaiXe_AI")
    print("=" * 60)
    print()
    
    if create_database():
        print("\n" + "=" * 60)
        print("✅ DATABASE CREATION COMPLETED!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ DATABASE CREATION FAILED!")
        print("=" * 60)
