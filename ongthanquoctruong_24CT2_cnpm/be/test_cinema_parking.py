import os
import sys
import unittest

# Ensure be folder is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import app
import database

class TestCinemaParking(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_parking_map_api(self):
        """Kiểm tra API lấy bản đồ bãi xe /api/parking/map."""
        res = self.client.get('/api/parking/map')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('slots', data)
        self.assertIn('stats', data)
        
        slots = data['slots']
        self.assertEqual(len(slots), 100, f"Kỳ vọng 100 ô đỗ ô tô, thực tế có {len(slots)}")

        # Kiểm tra tất cả các ô đều là ô tô
        for s in slots:
            self.assertIn(s['loai_cho_do'], ['Ô tô con', 'VIP Ô tô'])
            self.assertIn(s['khu_vuc'], ['Ham_B1', 'Ham_B2'])
            self.assertIn(s['trang_thai'], ['Trong', 'DaDat', 'BaoTri'])

        stats = data['stats']
        self.assertEqual(stats['total'], 100)
        print("✅ [TEST 1 PASSED] /api/parking/map trả về đầy đủ 100 ô đỗ ô tô 2 tầng hầm chuẩn phong cách cinema seat.")

    def test_02_resident_slot_assignment_flow(self):
        """Kiểm tra luồng cư dân đăng ký xe chọn ô đỗ và đổi ô đỗ."""
        # 1. Giả lập đăng nhập cư dân test
        with self.client.session_transaction() as sess:
            sess['user'] = {
                'username': 'cudan_test_cinema',
                'full_name': 'Cư Dân Cinema Test',
                'role': 'Resident'
            }

        test_plate = '30H-999.88'
        test_slot_1 = 'B1-A01'
        test_slot_2 = 'B1-B05'

        # Đảm bảo dọn dẹp trước khi test
        database.release_parking_slot(bien_so_xe=test_plate)
        database.release_parking_slot(ma_cho_do=test_slot_1)
        database.release_parking_slot(ma_cho_do=test_slot_2)

        conn = database.get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM phuong_tien WHERE BienSoXe = %s", (test_plate,))
        c.execute("DELETE FROM vehicles WHERE plate_text = %s", (test_plate,))
        conn.commit()
        conn.close()

        # 2. Đăng ký xe mới kèm chọn vị trí test_slot_1
        res_add = self.client.post('/api/resident/add_vehicle', json={
            'plate_text': test_plate,
            'color': 'Trắng Ngọc Trai',
            'vi_tri_do': test_slot_1
        })
        self.assertEqual(res_add.status_code, 200, res_add.get_data(as_text=True))
        data_add = res_add.get_json()
        self.assertTrue(data_add.get('success'))
        print(f"✅ Đăng ký xe {test_plate} tại ô {test_slot_1} thành công.")

        # 3. Kiểm tra ô đỗ test_slot_1 đã chuyển sang trạng thái DaDat
        res_map = self.client.get('/api/parking/map')
        slots = res_map.get_json()['slots']
        slot_1 = next((s for s in slots if s['ma_cho_do'] == test_slot_1), None)
        self.assertIsNotNone(slot_1)
        self.assertEqual(slot_1['trang_thai'], 'DaDat')
        self.assertEqual(slot_1['bien_so_xe'], test_plate)
        self.assertTrue(slot_1['is_my_slot'])

        # 4. Thử đăng ký xe khác vào cùng ô test_slot_1 -> Phải bị từ chối
        with self.client.session_transaction() as sess:
            sess['user'] = {
                'username': 'cudan_test_other',
                'full_name': 'Cư Dân Khác',
                'role': 'Resident'
            }
        res_conflict = self.client.post('/api/resident/add_vehicle', json={
            'plate_text': '29A-111.22',
            'color': 'Đen',
            'vi_tri_do': test_slot_1
        })
        self.assertEqual(res_conflict.status_code, 400)
        print("✅ Ngăn chặn trùng vị trí đỗ thành công (400 Conflict).")

        # 5. Đổi vị trí đỗ sang test_slot_2
        with self.client.session_transaction() as sess:
            sess['user'] = {
                'username': 'cudan_test_cinema',
                'full_name': 'Cư Dân Cinema Test',
                'role': 'Resident'
            }
        res_change = self.client.post('/api/resident/change_slot', json={
            'plate_text': test_plate,
            'new_slot_id': test_slot_2
        })
        self.assertEqual(res_change.status_code, 200, res_change.get_data(as_text=True))
        data_change = res_change.get_json()
        self.assertTrue(data_change.get('success'))
        print(f"✅ Đổi sang ô {test_slot_2} thành công.")

        # 6. Kiểm tra test_slot_1 đã giải phóng về 'Trong', test_slot_2 là 'DaDat'
        res_map2 = self.client.get('/api/parking/map')
        slots2 = res_map2.get_json()['slots']
        slot_1_after = next((s for s in slots2 if s['ma_cho_do'] == test_slot_1), None)
        slot_2_after = next((s for s in slots2 if s['ma_cho_do'] == test_slot_2), None)
        self.assertEqual(slot_1_after['trang_thai'], 'Trong')
        self.assertEqual(slot_2_after['trang_thai'], 'DaDat')
        self.assertEqual(slot_2_after['bien_so_xe'], test_plate)

        # 7. Xóa xe -> Phải giải phóng test_slot_2 về 'Trong'
        res_del = self.client.delete(f'/api/resident/vehicles/{test_plate}')
        self.assertEqual(res_del.status_code, 200)

        res_map3 = self.client.get('/api/parking/map')
        slots3 = res_map3.get_json()['slots']
        slot_2_final = next((s for s in slots3 if s['ma_cho_do'] == test_slot_2), None)
        self.assertEqual(slot_2_final['trang_thai'], 'Trong')
        print("✅ [TEST 2 PASSED] Luồng chọn ô đỗ, đổi ô đỗ và xóa xe giải phóng vị trí hoạt động hoàn hảo!")

    def test_03_admin_vehicle_slot_crud(self):
        """Kiểm tra Admin lưu và cập nhật xe kèm vị trí ô đỗ."""
        with self.client.session_transaction() as sess:
            sess['user'] = {
                'username': 'admin',
                'full_name': 'Quản Trị Viên',
                'role': 'Admin'
            }

        admin_plate = '51K-888.99'
        admin_slot = 'B2-D03'

        # Dọn dẹp
        database.release_parking_slot(bien_so_xe=admin_plate)
        database.release_parking_slot(ma_cho_do=admin_slot)

        # Lưu xe từ phía Admin
        res_save = self.client.post('/api/vehicles/save', json={
            'plate_text': admin_plate,
            'owner_name': 'Trần Văn Admin Test',
            'vehicle_type': 'Ô tô con',
            'color': 'Đỏ Ruby',
            'parking_slot': admin_slot,
            'status': 'Hoạt động',
            'province_code': '51',
            'group_type': 'Whitelist'
        })
        self.assertEqual(res_save.status_code, 200)
        self.assertTrue(res_save.get_json().get('success'))

        # Kiểm tra slot B2-C03 đã được gán
        res_map = self.client.get('/api/parking/map')
        slots = res_map.get_json()['slots']
        s = next((slot for slot in slots if slot['ma_cho_do'] == admin_slot), None)
        self.assertIsNotNone(s)
        self.assertEqual(s['trang_thai'], 'DaDat')
        self.assertEqual(s['bien_so_xe'], admin_plate)

        # Dọn dẹp sau test
        self.client.delete(f'/api/vehicles/delete/{admin_plate}')
        print("✅ [TEST 3 PASSED] Admin CRUD xe gắn vị trí ô đỗ thành công!")


if __name__ == '__main__':
    unittest.main()
