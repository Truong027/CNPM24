#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Import Dữ Liệu Mẫu vào MySQL
Sử dụng để import file bien_so_xe_sample.sql
"""

import mysql.connector
from mysql.connector import Error
import os
import sys

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

# ==================== CẤU HÌNH AN TOÀN ====================
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
}

SQL_FILE = 'bien_so_xe_sample.sql'

# ==================== HÀM IMPORT ====================
def import_sql_file(config, sql_file):
    """Import file SQL vào MySQL"""
    
    # Kiểm tra file tồn tại
    if not os.path.exists(sql_file):
        print(f"❌ Không tìm thấy file: {sql_file}")
        return False
    
    conn = None
    try:
        # Kết nối MySQL
        print(f"⌛ Đang kết nối MySQL: {config['host']}...")
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("✅ Kết nối thành công!")
        
        # Đọc file SQL
        print(f"⌛ Đang đọc file: {sql_file}...")
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(f"✅ Đã đọc {len(sql_content)} ký tự.")
        
        # Chia thành các câu lệnh
        statements = sql_content.split(';')
        total_statements = len([s for s in statements if s.strip()])
        
        print(f"⌛ Tìm thấy {total_statements} câu lệnh SQL...")
        print("⌛ Đang thực thi...\n")
        
        executed = 0
        for i, statement in enumerate(statements):
            stmt_stripped = statement.strip()
            
            if not stmt_stripped:
                continue
            
            # Bỏ qua các comment
            if stmt_stripped.startswith('--') or stmt_stripped.startswith('/*'):
                continue
            
            try:
                # Nếu là SELECT hoặc SHOW, không commit
                if stmt_stripped.upper().startswith(('SELECT', 'SHOW', 'DESC')):
                    cursor.execute(stmt_stripped)
                    results = cursor.fetchall()
                    if results:
                        print(f"  📊 Query: {stmt_stripped[:50]}...")
                        for row in results[:3]:  # In 3 dòng đầu
                            print(f"     {row}")
                        if len(results) > 3:
                            print(f"     ... ({len(results)} hàng)")
                else:
                    cursor.execute(stmt_stripped)
                    executed += 1
                    
                    # Progress bar
                    progress = (executed / total_statements) * 100
                    bar_length = 40
                    filled = int(bar_length * executed // total_statements)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    print(f"  [{bar}] {executed}/{total_statements} ({progress:.0f}%)", end='\r')
                    
            except Error as e:
                # Bỏ qua lỗi duplicate key (bảng đã tồn tại)
                if 'already exists' in str(e) or 'Duplicate' in str(e):
                    pass
                else:
                    print(f"\n⚠️  Lỗi SQL: {e}")
                    print(f"   Statement: {stmt_stripped[:100]}...")
        
        print(f"\n✅ Đã thực thi {executed} câu lệnh thành công!\n")
        
        # Commit
        conn.commit()
        print("💾 Dữ liệu đã được lưu lại.")
        
        # Kiểm tra dữ liệu
        print("\n📊 ===== KIỂM TRA DỮ LIỆU =====")
        cursor.execute("USE bien_so_xe")
        
        # Bảng plates
        cursor.execute("SELECT COUNT(*) FROM plates")
        plates_count = cursor.fetchone()[0]
        print(f"✅ Bảng 'plates': {plates_count} biển số")
        
        # Bảng detections
        cursor.execute("SELECT COUNT(*) FROM detections")
        detections_count = cursor.fetchone()[0]
        print(f"✅ Bảng 'detections': {detections_count} lần phát hiện")
        
        # Bảng provinces
        cursor.execute("SELECT COUNT(*) FROM provinces")
        provinces_count = cursor.fetchone()[0]
        print(f"✅ Bảng 'provinces': {provinces_count} tỉnh/thành phố")
        
        # Bảng vehicle_types
        cursor.execute("SELECT COUNT(*) FROM vehicle_types")
        vehicle_types_count = cursor.fetchone()[0]
        print(f"✅ Bảng 'vehicle_types': {vehicle_types_count} loại xe")
        
        # Bảng statistics
        cursor.execute("SELECT COUNT(*) FROM statistics")
        statistics_count = cursor.fetchone()[0]
        print(f"✅ Bảng 'statistics': {statistics_count} dòng thống kê")
        
        # Top 5 biển số
        print("\n📍 ===== TOP 5 BIỂN SỐ PHÁT HIỆN NHIỀU =====")
        cursor.execute("""
            SELECT plate_text, detection_count, province_code, vehicle_type
            FROM plates
            ORDER BY detection_count DESC
            LIMIT 5
        """)
        for plate, count, prov, vtype in cursor.fetchall():
            print(f"  {plate:<15} | {count:2d} lần | Tỉnh: {prov} | Loại: {vtype}")
        
        print("\n✅ ===== IMPORT THÀNH CÔNG! =====\n")
        print("📝 Dữ liệu sẵn sàng để tạo query MySQL!")
        print("📚 Xem 'IMPORT_DATA_GUIDE.md' để học cách viết query")
        
        return True
        
    except Error as e:
        print(f"\n❌ LỖI MYSQL: {e}")
        return False
        
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("\n✅ Đóng kết nối MySQL.")

# ==================== MAIN ====================
def main():
    print("\n" + "="*60)
    print("🗄️  IMPORT DỮ LIỆU MẪU MYSQL - NHẬN DIỆN BIỂN SỐ XE")
    print("="*60 + "\n")
    
    # Kiểm tra cấu hình
    print("⚙️  CẤU HÌNH:")
    print(f"   Host: {MYSQL_CONFIG['host']}")
    print(f"   User: {MYSQL_CONFIG['user']}")
    print(f"   Port: {MYSQL_CONFIG['port']}")
    print(f"   SQL File: {SQL_FILE}\n")
    
    # Hỏi mật khẩu nếu là default
    if MYSQL_CONFIG['password'] == 'your_password':
        print("⚠️  CẬP NHẬT MẬT KHẨU MYSQL")
        print("   Nhận thấy mật khẩu chưa được cập nhật!\n")
        
        password = input("🔐 Nhập mật khẩu MySQL root: ")
        if password:
            MYSQL_CONFIG['password'] = password
        else:
            print("❌ Mật khẩu không thể để trống!")
            return
    
    # Import
    success = import_sql_file(MYSQL_CONFIG, SQL_FILE)
    
    if not success:
        print("\n💡 Gợi ý:")
        print("   1. Kiểm tra MySQL đang chạy")
        print("   2. Kiểm tra mật khẩu MySQL")
        print("   3. Kiểm tra file bien_so_xe_sample.sql tồn tại")
        sys.exit(1)

if __name__ == '__main__':
    main()
