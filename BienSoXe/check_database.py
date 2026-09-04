#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kiểm tra dữ liệu trong database HTTT_QuanLyBaiXe_AI
"""

import database

def check_database():
    """Kiểm tra dữ liệu trong database"""
    conn = database.get_db_connection()
    if not conn:
        print("❌ Không thể kết nối database")
        return
    
    cursor = conn.cursor(dictionary=True)
    
    # Kiểm tra bảng plates
    cursor.execute("SELECT COUNT(*) as cnt FROM plates")
    plates_count = cursor.fetchone()['cnt']
    print(f"\n📊 Bảng PLATES: {plates_count} dòng")
    
    if plates_count > 0:
        cursor.execute("SELECT * FROM plates LIMIT 3")
        plates = cursor.fetchall()
        for p in plates:
            print(f"   • {p['plate_text']} - Tỉnh: {p['province_code']} - Loại: {p['vehicle_type']}")
    
    # Kiểm tra bảng NHAN_VIEN
    cursor.execute("SELECT COUNT(*) as cnt FROM NHAN_VIEN")
    nv_count = cursor.fetchone()['cnt']
    print(f"\n👤 Bảng NHAN_VIEN: {nv_count} nhân viên")
    
    if nv_count > 0:
        cursor.execute("SELECT MaNV, HoTen, VaiTro FROM NHAN_VIEN LIMIT 3")
        nvs = cursor.fetchall()
        for nv in nvs:
            print(f"   • {nv['MaNV']}: {nv['HoTen']} ({nv['VaiTro']})")
    
    # Kiểm tra bảng CU_DAN
    cursor.execute("SELECT COUNT(*) as cnt FROM CU_DAN")
    cd_count = cursor.fetchone()['cnt']
    print(f"\n🏠 Bảng CU_DAN: {cd_count} cư dân")
    
    if cd_count > 0:
        cursor.execute("SELECT MaCuDan, HoTen FROM CU_DAN LIMIT 3")
        cds = cursor.fetchall()
        for cd in cds:
            print(f"   • {cd['MaCuDan']}: {cd['HoTen']}")
    
    # Kiểm tra bảng PHUONG_TIEN
    cursor.execute("SELECT COUNT(*) as cnt FROM PHUONG_TIEN")
    pt_count = cursor.fetchone()['cnt']
    print(f"\n🚗 Bảng PHUONG_TIEN: {pt_count} phương tiện")
    
    if pt_count > 0:
        cursor.execute("SELECT BienSoXe, LoaiXe, MaCuDan FROM PHUONG_TIEN LIMIT 3")
        pts = cursor.fetchall()
        for pt in pts:
            print(f"   • {pt['BienSoXe']}: {pt['LoaiXe']} ({pt['MaCuDan']})")
    
    cursor.close()
    conn.close()
    
    print(f"\n✅ Kiểm tra hoàn tất")

if __name__ == '__main__':
    print("=" * 60)
    print("📋 KIỂM TRA DỮ LIỆU DATABASE HTTT_QuanLyBaiXe_AI")
    print("=" * 60)
    check_database()
