# -*- coding: utf-8 -*-
"""
Kịch bản kiểm thử toàn diện Chức năng Quản lý Tài khoản:
1. Thêm tài khoản cư dân và bảo vệ (Create)
2. Sửa thông tin tài khoản (Update)
3. Cập nhật quyền / Phân quyền (Update Role)
4. Thay đổi mật khẩu / Cấp lại mật khẩu (Change Password)
5. Xóa tài khoản và dữ liệu liên quan (Delete)
"""

import os
import sys
import unittest

# Đảm bảo đường dẫn import be
current_dir = os.path.dirname(os.path.abspath(__file__))
be_dir = os.path.abspath(os.path.join(current_dir, "..", "be"))
if be_dir not in sys.path:
    sys.path.insert(0, be_dir)

import database
from werkzeug.security import check_password_hash

class TestUserManagement(unittest.TestCase):
    @classmethod
    def clean_test_data(cls):
        try:
            conn = database.get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM app_users WHERE username IN ('test_resident_01', 'test_guard_unit', 'cudan_photo_test') OR phone IN ('0911223344', '0988776655', '0933445566')")
            cur.execute("DELETE FROM cu_dan WHERE TaiKhoan IN ('test_resident_01', 'cudan_photo_test') OR SoDienThoai IN ('0911223344', '0933445566')")
            cur.execute("DELETE FROM nhan_vien WHERE TaiKhoan IN ('test_guard_unit', 'test_resident_01')")
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print("Lỗi dọn dẹp:", e)

    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("  BẮT ĐẦU TEST TOÀN DIỆN QUẢN LÝ TÀI KHOẢN")
        print("=======================================================")
        cls.clean_test_data()

    @classmethod
    def tearDownClass(cls):
        cls.clean_test_data()
        print("\n=======================================================")
        print("  HOÀN THÀNH TEST TOÀN BỘ QUẢN LÝ TÀI KHOẢN (CLEANUP OK)")
        print("=======================================================")

    def test_01_create_resident_and_guard(self):
        print("\n--- [TEST 1] THÊM TÀI KHOẢN (CREATE) ---")
        # 1.1 Thêm tài khoản Cư Dân
        ok_res, msg_res = database.admin_create_resident(
            username="test_resident_01",
            full_name="Nguyễn Văn Test Cư Dân",
            password="password123",
            phone="0911223344",
            email="resident01@test.com",
            apartment_number="B-1201",
            cccd="048099001122",
            initial_plate="43A-999.88"
        )
        print(f" [+] Tạo Cư Dân: success={ok_res}, msg={msg_res}")
        self.assertTrue(ok_res, msg_res)

        # Kiểm tra tồn tại trong CSDL
        conn = database.get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM app_users WHERE phone = %s", ("0911223344",))
        user_db = cur.fetchone()
        self.assertIsNotNone(user_db)
        self.assertEqual(user_db["username"], "test_resident_01")
        self.assertEqual(user_db["role"], "Resident")
        print("     -> Xác minh app_users: Tồn tại Cư dân với vai trò 'Resident'")

        # 1.2 Thêm tài khoản Bảo Vệ
        ok_guard, msg_guard = database.admin_create_guard(
            username="test_guard_unit",
            full_name="Trần Văn Bảo Vệ Test",
            password="guardpass123",
            phone="0988776655",
            email="guard01@test.com",
            shift="Ca Sáng (06:00 - 14:00)"
        )
        print(f" [+] Tạo Bảo Vệ: success={ok_guard}, msg={msg_guard}")
        self.assertTrue(ok_guard, msg_guard)

        cur.execute("SELECT * FROM nhan_vien WHERE TaiKhoan = %s", ("test_guard_unit",))
        guard_db = cur.fetchone()
        self.assertIsNotNone(guard_db)
        self.assertIn(guard_db["VaiTro"], ["BaoVe", "Bảo vệ"])
        print("     -> Xác minh nhan_vien: Tồn tại Nhân viên với vai trò 'Bảo vệ'")
        cur.close()
        conn.close()

    def test_02_edit_user_info(self):
        print("\n--- [TEST 2] SỬA THÔNG TIN TÀI KHOẢN (UPDATE) ---")
        ok_update, msg_update = database.admin_update_user_info(
            original_phone="0911223344",
            username="test_resident_01",
            full_name="Nguyễn Văn Test Cư Dân (ĐÃ SỬA TÊN)",
            phone="0911223344",
            email="resident_edited@test.com",
            role="Resident",
            is_active=True,
            apartment="B-1205",
            shift="",
            new_password=""
        )
        print(f" [+] Sửa thông tin Cư dân: success={ok_update}, msg={msg_update}")
        self.assertTrue(ok_update, msg_update)

        # Kiểm tra CSDL sau khi sửa
        conn = database.get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM app_users WHERE phone = %s", ("0911223344",))
        u = cur.fetchone()
        self.assertEqual(u["full_name"], "Nguyễn Văn Test Cư Dân (ĐÃ SỬA TÊN)")
        self.assertEqual(u["email"], "resident_edited@test.com")
        print("     -> Xác minh app_users: Họ tên và email đã được cập nhật thành công!")
        cur.close()
        conn.close()

    def test_03_update_user_role(self):
        print("\n--- [TEST 3] CẬP NHẬT QUYỀN / PHÂN QUYỀN (UPDATE ROLE) ---")
        # Chuyển quyền người dùng từ Resident sang Operator/User
        ok_role, msg_role = database.admin_update_user_info(
            original_phone="0911223344",
            username="test_resident_01",
            full_name="Nguyễn Văn Test Cư Dân (ĐÃ SỬA TÊN)",
            phone="0911223344",
            email="resident_edited@test.com",
            role="Operator",
            is_active=True,
            apartment="",
            shift="Ca Tối (22:00 - 06:00)",
            new_password=""
        )
        print(f" [+] Cập nhật quyền sang Operator: success={ok_role}, msg={msg_role}")
        self.assertTrue(ok_role, msg_role)

        conn = database.get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT role FROM app_users WHERE phone = %s", ("0911223344",))
        u = cur.fetchone()
        self.assertEqual(u["role"], "Operator")
        print("     -> Xác minh app_users: Quyền tài khoản đã đổi thành 'Operator' thành công!")

        # Chuyển lại về Resident
        database.admin_update_user_info(
            original_phone="0911223344",
            username="test_resident_01",
            full_name="Nguyễn Văn Test Cư Dân",
            phone="0911223344",
            email="resident_edited@test.com",
            role="Resident",
            is_active=True,
            apartment="B-1205"
        )
        cur.close()
        conn.close()

    def test_04_change_and_reset_password(self):
        print("\n--- [TEST 4] THAY ĐỔI MẬT KHẨU (RESET PASSWORD) ---")
        new_pass = "newSecurePass@2026"
        ok_reset, msg_reset = database.admin_reset_user_password("0911223344", new_pass)
        print(f" [+] Cấp lại mật khẩu mới: success={ok_reset}, msg={msg_reset}")
        self.assertTrue(ok_reset, msg_reset)

        # Kiểm tra mật khẩu trong DB
        conn = database.get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT password_hash FROM app_users WHERE phone = %s", ("0911223344",))
        u = cur.fetchone()
        self.assertIsNotNone(u)
        
        # Mật khẩu mới phải khớp
        self.assertTrue(check_password_hash(u["password_hash"], new_pass))
        print("     -> Xác minh mật khẩu mới: ĐĂNG NHẬP THÀNH CÔNG VỚI MẬT KHẨU MỚI!")
        
        # Mật khẩu cũ không được khớp
        self.assertFalse(check_password_hash(u["password_hash"], "password123"))
        print("     -> Xác minh mật khẩu cũ: ĐÃ BỊ VÔ HIỆU HÓA CHÍNH XÁC!")
        cur.close()
        conn.close()

    def test_05_delete_user(self):
        print("\n--- [TEST 5] XÓA TÀI KHOẢN (DELETE) ---")
        # 5.1 Xóa Cư dân
        ok_del_u, msg_del_u = database.admin_delete_user("0911223344")
        print(f" [+] Xóa Cư Dân: success={ok_del_u}, msg={msg_del_u}")
        self.assertTrue(ok_del_u, msg_del_u)

        # 5.2 Xóa Bảo vệ
        ok_del_g, msg_del_g = database.admin_delete_guard("test_guard_unit")
        print(f" [+] Xóa Bảo Vệ: success={ok_del_g}, msg={msg_del_g}")
        self.assertTrue(ok_del_g, msg_del_g)

        # Kiểm tra CSDL không còn tài khoản
        conn = database.get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id FROM app_users WHERE phone = %s", ("0911223344",))
        self.assertIsNone(cur.fetchone())
        cur.execute("SELECT id FROM app_users WHERE username = %s", ("test_guard_unit",))
        self.assertIsNone(cur.fetchone())
        print("     -> Xác minh CSDL: Toàn bộ tài khoản đã được xóa triệt để khỏi hệ thống!")
        cur.close()
        conn.close()

    def test_06_registration_with_uploaded_photo(self):
        print("\n--- [TEST 6] ĐĂNG KÝ VỚI ẢNH CHỤP ĐƠN DO CƯ DÂN TẢI LÊN (REGISTER WITH PHOTO) ---")
        # Giả lập cư dân đăng ký từ register.html với ảnh chụp thực tế (base64)
        sample_doc_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA="
        
        # Đăng ký user
        user, err = database.register_user(
            username="cudan_photo_test",
            password="password123",
            full_name="Nguyễn Văn Chụp Ảnh",
            email="cudan_photo@test.com",
            role="Resident",
            phone="0933445566"
        )
        self.assertIsNone(err)
        self.assertIsNotNone(user)
        print(" [+] Đăng ký tài khoản cư dân thành công")

        # Giả lập luồng app.py lưu ảnh chụp đơn xác nhận của Phường/TP
        conn = database.get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT MaCuDan FROM cu_dan WHERE TaiKhoan = %s", ("cudan_photo_test",))
        cd = cur.fetchone()
        self.assertIsNotNone(cd)

        ma_don = "DON_TEST_PHOTO_999"
        cur.execute("""
            INSERT INTO chuyen_nhuong_xe (
                MaDon, BienSoXe, MaCuDanChuyen, TenCuDanChuyen, CanHoChuyen,
                MaCuDanNhan, TenCuDanNhan, CanHoNhan, TrangThai, GhiChu, HinhAnhDon
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Pending', %s, %s)
        """, (
            ma_don, "43A-888.99",
            "CD_CHUYEN", "UBND Phường / Chủ phương tiện cũ", "Địa phương",
            cd["MaCuDan"], "Nguyễn Văn Chụp Ảnh", "A-1205",
            "Đơn đăng ký kèm ảnh chụp văn bản xác nhận từ Phường do cư dân đưa lên",
            sample_doc_image
        ))
        conn.commit()

        # Kiểm tra truy vấn danh sách đơn chuyển nhượng cho Admin
        cur.execute("SELECT * FROM chuyen_nhuong_xe WHERE MaDon = %s", (ma_don,))
        req = cur.fetchone()
        self.assertIsNotNone(req)
        self.assertEqual(req["HinhAnhDon"], sample_doc_image)
        print("     -> Xác minh ảnh chụp: HinhAnhDon trong CSDL lưu đúng chuỗi ảnh thực tế của cư dân chụp!")

        # Dọn dẹp
        cur.execute("DELETE FROM chuyen_nhuong_xe WHERE MaDon = %s", (ma_don,))
        conn.commit()
        cur.close()
        conn.close()
        database.admin_delete_user("0933445566")
        print(" [+] Dọn dẹp dữ liệu test thành công.")

if __name__ == '__main__':
    unittest.main()
