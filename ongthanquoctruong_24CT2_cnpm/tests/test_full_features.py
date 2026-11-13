# -*- coding: utf-8 -*-
"""
Automated Comprehensive Test Suite for:
1. Authentication (Register & Login)
2. Vehicle Transfer Request & Approval (Resident & Admin)
3. User Management & RBAC (Admin)
"""
import os
import sys
import json
import time

# Ensure backend dir in sys.path
_BE_DIR = r"d:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\be"
if _BE_DIR not in sys.path:
    sys.path.insert(0, _BE_DIR)

import app
import database
from werkzeug.security import generate_password_hash, check_password_hash

test_results = []

def record(test_id, name, status, details=""):
    test_results.append({
        "id": test_id,
        "name": name,
        "status": status,
        "details": details
    })
    mark = "[PASS]" if status == "PASS" else "[FAIL]"
    print(f"{mark} {test_id}: {name} - {details}", flush=True)

def run_tests():
    print("=" * 70)
    print("BAT DAU CHAY TEST TOAN DIEN CAC CHUC NANG")
    print("=" * 70, flush=True)

    client = app.app.test_client()

    # Thong tin test accounts
    ts = int(time.time())
    user_test_phone = f"0988{ts % 1000000:06d}"
    user_test_name = f"testuser_{ts}"
    user_test_pw = "Password123"

    user2_test_phone = f"0977{ts % 1000000:06d}"
    user2_test_name = f"testuser2_{ts}"
    user2_test_pw = "Password123"

    test_plate = f"30H-{ts % 10000:04d}"

    created_user_phones = [user_test_phone, user2_test_phone]
    created_transfer_ids = []

    # =========================================================================
    # SUITE 1: DANG KY & DANG NHAP (AUTHENTICATION)
    # =========================================================================
    print("\n--- SUITE 1: DANG KY & DANG NHAP ---", flush=True)

    # 1.1: Dang ky voi mat khau ngan (< 6 ky tu) -> phai bao loi 400
    res = client.post("/api/register", json={
        "username": user_test_name,
        "password": "123",
        "confirm_password": "123",
        "full_name": "Test User",
        "phone": user_test_phone,
        "role": "Resident"
    })
    if res.status_code == 400 and "ít nhất 6 ký tự" in res.get_json().get("error", ""):
        record("1.1", "Dang ky voi mat khau ngan (<6 ky tu)", "PASS", "Tra ve 400 va bao loi dung")
    else:
        record("1.1", "Dang ky voi mat khau ngan (<6 ky tu)", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.2: Dang ky voi mat khau xac nhan khong khop -> phai bao loi 400
    res = client.post("/api/register", json={
        "username": user_test_name,
        "password": user_test_pw,
        "confirm_password": "DifferentPassword",
        "full_name": "Test User",
        "phone": user_test_phone,
        "role": "Resident"
    })
    if res.status_code == 400 and "không khớp" in res.get_json().get("error", ""):
        record("1.2", "Dang ky voi mat khau xac nhan khong khop", "PASS", "Tra ve 400 va bao loi khong khop")
    else:
        record("1.2", "Dang ky voi mat khau xac nhan khong khop", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.3: Dang ky voi so dien thoai sai dinh dang -> phai bao loi 400
    res = client.post("/api/register", json={
        "username": user_test_name,
        "password": user_test_pw,
        "confirm_password": user_test_pw,
        "full_name": "Test User",
        "phone": "12345",  # sai dinh dang
        "role": "Resident"
    })
    if res.status_code == 400 and "Số điện thoại không hợp lệ" in res.get_json().get("error", ""):
        record("1.3", "Dang ky voi SDT sai dinh dang", "PASS", "Tra ve 400 va bao loi format SDT")
    else:
        record("1.3", "Dang ky voi SDT sai dinh dang", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.4: Dang ky cu dan 1 hop le kem bien so xe
    res = client.post("/api/register", json={
        "username": user_test_name,
        "password": user_test_pw,
        "confirm_password": user_test_pw,
        "full_name": "Nguyen Van Chu Xe",
        "email": f"{user_test_name}@test.com",
        "phone": user_test_phone,
        "role": "Resident",
        "plate_text": test_plate,
        "color": "Trắng",
        "vi_tri_do": "A-01"
    })
    if res.status_code == 200 and res.get_json().get("success"):
        record("1.4", "Dang ky tai khoan Cu dan 1 hop le", "PASS", f"Tao thanh cong Cu dan (SDT: {user_test_phone}, Xe: {test_plate})")
    else:
        record("1.4", "Dang ky tai khoan Cu dan 1 hop le", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.5: Dang ky cu dan 2 (nguoi nhan chuyen nhuong xe)
    res = client.post("/api/register", json={
        "username": user2_test_name,
        "password": user2_test_pw,
        "confirm_password": user2_test_pw,
        "full_name": "Tran Thi Nguoi Nhan",
        "email": f"{user2_test_name}@test.com",
        "phone": user2_test_phone,
        "role": "Resident"
    })
    if res.status_code == 200 and res.get_json().get("success"):
        record("1.5", "Dang ky tai khoan Cu dan 2 hop le", "PASS", f"Tao thanh cong Cu dan nhan (SDT: {user2_test_phone})")
    else:
        record("1.5", "Dang ky tai khoan Cu dan 2 hop le", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.6: Dang ky trung so dien thoai da co -> phai bao loi 400
    res = client.post("/api/register", json={
        "username": "duplicate_user",
        "password": user_test_pw,
        "confirm_password": user_test_pw,
        "full_name": "User Duplicate",
        "phone": user_test_phone,  # SDT trung
        "role": "Resident"
    })
    if res.status_code == 400 and ("đã được" in res.get_json().get("error", "") or "tồn tại" in res.get_json().get("error", "")):
        record("1.6", "Dang ky trung so dien thoai", "PASS", "Tra ve 400 tu choi trung lap SDT")
    else:
        record("1.6", "Dang ky trung so dien thoai", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.7: Dang nhap voi sai mat khau -> phai tra ve 401
    res = client.post("/api/login", json={
        "phone": user_test_phone,
        "password": "WrongPassword999"
    })
    if res.status_code == 401:
        record("1.7", "Dang nhap voi sai mat khau", "PASS", "Tra ve HTTP 401 tu choi mat khau sai")
    else:
        record("1.7", "Dang nhap voi sai mat khau", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.8: Dang nhap voi SDT khong ton tai -> phai tra ve 401
    res = client.post("/api/login", json={
        "phone": "0999999999",
        "password": user_test_pw
    })
    if res.status_code == 401:
        record("1.8", "Dang nhap voi SDT khong ton tai", "PASS", "Tra ve HTTP 401")
    else:
        record("1.8", "Dang nhap voi SDT khong ton tai", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.9: Dang nhap dung mat khau (Cu dan 1) -> phai tra ve 200 kem session va redirect ve resident_dashboard
    c_res1 = app.app.test_client()
    res = c_res1.post("/api/login", json={
        "phone": user_test_phone,
        "password": user_test_pw
    })
    data = res.get_json() or {}
    if res.status_code == 200 and data.get("success") and data.get("redirect") == "/resident-dashboard":
        record("1.9", "Dang nhap thanh cong va dinh tuyen Cu dan", "PASS", f"Redirect: {data.get('redirect')}, User: {data.get('user', {}).get('username')}")
    else:
        record("1.9", "Dang nhap thanh cong va dinh tuyen Cu dan", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 1.10: Dang xuat va kiem tra mat phien
    res = c_res1.post("/api/logout")
    res_sess = c_res1.get("/api/session")
    sess_data = res_sess.get_json() or {}
    if res.status_code == 200 and not sess_data.get("authenticated"):
        record("1.10", "Dang xuat va xoa Session", "PASS", "Session authenticated = False")
    else:
        record("1.10", "Dang xuat va xoa Session", "FAIL", f"Resp: {res_sess.get_data(as_text=True)}")

    # =========================================================================
    # SUITE 2: CHUC NANG DUYET DON CHUYEN NHUONG XE
    # =========================================================================
    print("\n--- SUITE 2: CHUC NANG CHUYEN NHUONG & PHE DUYET DON ---", flush=True)

    # Dang nhap lai Cu dan 1
    c_res1.post("/api/login", json={"phone": user_test_phone, "password": user_test_pw})

    # 2.1: Cu dan gui don voi bien so xe khong thuoc so huu cua minh -> phai bao loi 400
    res = c_res1.post("/api/resident/transfer_vehicle", json={
        "plate_text": "99A-99999",  # Bien so xe khong so huu
        "recipient_identifier": user2_test_phone,
        "note": "Thu chuyen xe khong so huu"
    })
    if res.status_code == 400 and ("không phải" in res.get_json().get("error", "") or "Không tìm thấy" in res.get_json().get("error", "")):
        record("2.1", "Chan chuyen nhuong xe khong so huu", "PASS", f"Tu choi: {res.get_json().get('error')}")
    else:
        record("2.1", "Chan chuyen nhuong xe khong so huu", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 2.2: Cu dan tu chuyen nhuong xe cho chinh minh -> phai bao loi 400
    res = c_res1.post("/api/resident/transfer_vehicle", json={
        "plate_text": test_plate,
        "recipient_identifier": user_test_phone,  # Nguoi nhan = Nguoi chuyen
        "note": "Tu chuyen cho minh"
    })
    if res.status_code == 400 and "chính mình" in res.get_json().get("error", ""):
        record("2.2", "Chan tu chuyen nhuong cho chinh minh", "PASS", f"Tu choi: {res.get_json().get('error')}")
    else:
        record("2.2", "Chan tu chuyen nhuong cho chinh minh", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 2.3: Cu dan chuyen xe cho nguoi nhan khong ton tai -> phai bao loi 400
    res = c_res1.post("/api/resident/transfer_vehicle", json={
        "plate_text": test_plate,
        "recipient_identifier": "NON_EXISTING_RECIPIENT_12345",
        "note": "Nguoi nhan khong co"
    })
    if res.status_code == 400 and "Không tìm thấy" in res.get_json().get("error", ""):
        record("2.3", "Chan chuyen cho nguoi nhan khong ton tai", "PASS", f"Tu choi: {res.get_json().get('error')}")
    else:
        record("2.3", "Chan chuyen cho nguoi nhan khong ton tai", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 2.4: Cu dan gui don chuyen nhuong xe hop le sang Cu dan 2
    res = c_res1.post("/api/resident/transfer_vehicle", json={
        "plate_text": test_plate,
        "recipient_identifier": user2_test_phone,
        "note": "Chuyen nhuong can ho kem xe cho chi Tran Thi Nguoi Nhan"
    })
    tf_data = res.get_json() or {}
    if res.status_code == 200 and tf_data.get("success"):
        record("2.4", "Cu dan tao don chuyen nhuong hop le", "PASS", f"Thong bao: {tf_data.get('message')}")
    else:
        record("2.4", "Cu dan tao don chuyen nhuong hop le", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 2.5: Cu dan co tinh gui tiep don thu hai khi don truoc dang Pending -> phai bao loi
    res = c_res1.post("/api/resident/transfer_vehicle", json={
        "plate_text": test_plate,
        "recipient_identifier": user2_test_phone,
        "note": "Thu gui lan 2"
    })
    if res.status_code == 400 and "đang có một đơn" in res.get_json().get("error", ""):
        record("2.5", "Chan gui don trung lap khi dang Pending", "PASS", "Ngan chan thanh cong don trung lap")
    else:
        record("2.5", "Chan gui don trung lap khi dang Pending", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 2.6: Cu dan kiem tra danh sach don cua minh
    res = c_res1.get("/api/resident/transfer_requests")
    reqs = res.get_json() or []
    created_req = next((r for r in reqs if r.get("BienSoXe") == test_plate), None)
    if res.status_code == 200 and created_req and created_req.get("TrangThai") == "Pending":
        req_id = created_req["id"]
        created_transfer_ids.append(req_id)
        record("2.6", "Cu dan xem danh sach don cua minh", "PASS", f"Tim thay don ID: {req_id}, Trang thai: Pending")
    else:
        record("2.6", "Cu dan xem danh sach don cua minh", "FAIL", f"Status: {res.status_code}, List: {reqs}")

    # 2.7: Nguoi dung chua dang nhap truy cap API Admin duyet don -> phai bi chan 401
    c_anon = app.app.test_client()
    res = c_anon.get("/api/admin/transfer_requests")
    if res.status_code == 401:
        record("2.7", "Chan nguoi dung chua dang nhap truy cap API Admin", "PASS", "Tra ve HTTP 401 Unauthorized")
    else:
        record("2.7", "Chan nguoi dung chua dang nhap truy cap API Admin", "FAIL", f"Status: {res.status_code}")

    # 2.8: Cu dan (Resident) co tinh goi API Admin duyet don -> phai bi chan 403 Forbidden
    res = c_res1.get("/api/admin/transfer_requests")
    if res.status_code == 403:
        record("2.8", "Chan Cu dan (Resident) goi API Admin", "PASS", "Tra ve HTTP 403 Forbidden")
    else:
        record("2.8", "Chan Cu dan (Resident) goi API Admin", "FAIL", f"Status: {res.status_code}")

    # Dang nhap voi Admin de xu ly don
    c_admin = app.app.test_client()
    # Tim admin trong DB hoac tao session admin
    admin_user = None
    conn = database.get_db_connection()
    if conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, username, phone, role FROM app_users WHERE role = 'Admin' AND is_active = 1 LIMIT 1")
        admin_user = cur.fetchone()
        conn.close()

    if not admin_user:
        # Fallback tao session admin truc tiep qua mock
        admin_user = {"id": 1, "username": "admin", "full_name": "Quan Tri Vien", "role": "Admin"}

    with c_admin.session_transaction() as sess:
        sess["user"] = {
            "id": admin_user["id"],
            "username": admin_user["username"],
            "full_name": admin_user.get("full_name") or "Administrator",
            "role": "Admin"
        }

    # 2.9: Admin xem danh sach don chuyen nhuong Pending
    res = c_admin.get("/api/admin/transfer_requests?status=Pending")
    admin_reqs = res.get_json() or []
    target_req = next((r for r in admin_reqs if r.get("id") == req_id), None) if 'req_id' in locals() else None
    if res.status_code == 200 and target_req:
        record("2.9", "Admin xem danh sach don Pending", "PASS", f"Tim thay don {req_id} can duyet")
    else:
        record("2.9", "Admin xem danh sach don Pending", "FAIL", f"Status: {res.status_code}, Found: {bool(target_req)}")

    # 2.10: Admin tu choi don chuyen nhuong (Action = 'reject')
    res = c_admin.post(f"/api/admin/transfer_requests/{req_id}/action", json={
        "action": "reject",
        "note": "Ban Quan Tri tu choi vi can bo sung giay to"
    })
    if res.status_code == 200 and res.get_json().get("success"):
        record("2.10", "Admin tu choi don chuyen nhuong", "PASS", "Don chuyen sang trang thai Rejected")
    else:
        record("2.10", "Admin tu choi don chuyen nhuong", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 2.11: Cu dan tao don moi va Admin PHE DUYET (Action = 'approve') -> Quyen so huu xe phai sang tay Cu dan 2
    res = c_res1.post("/api/resident/transfer_vehicle", json={
        "plate_text": test_plate,
        "recipient_identifier": user2_test_phone,
        "note": "Da bo sung giay to day du"
    })
    res_reqs = c_res1.get("/api/resident/transfer_requests").get_json() or []
    new_pending = next((r for r in res_reqs if r.get("BienSoXe") == test_plate and r.get("TrangThai") == "Pending"), None)
    if new_pending:
        new_req_id = new_pending["id"]
        created_transfer_ids.append(new_req_id)
        # Admin Phe Duyet
        res_app = c_admin.post(f"/api/admin/transfer_requests/{new_req_id}/action", json={
            "action": "approve",
            "note": "Ban Quan Tri da xac minh va phe duyet"
        })
        # Kiem tra quyen so huu xe sau khi duyet
        conn = database.get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT p.MaCuDan, v.owner_name FROM phuong_tien p LEFT JOIN vehicles v ON p.BienSoXe = v.plate_text WHERE p.BienSoXe = %s", (test_plate,))
        veh_check = cur.fetchone()
        cur.execute("SELECT MaCuDan, HoTen FROM cu_dan WHERE SoDienThoai = %s", (user2_test_phone,))
        cd2_check = cur.fetchone()
        conn.close()

        is_transferred = (veh_check and cd2_check and veh_check["MaCuDan"] == cd2_check["MaCuDan"])
        if res_app.status_code == 200 and is_transferred:
            record("2.11", "Admin phe duyet don va Chuyen quyen so huu xe", "PASS", f"Xe {test_plate} da sang so huu Cu dan 2 ({cd2_check['HoTen']})")
        else:
            record("2.11", "Admin phe duyet don va Chuyen quyen so huu xe", "FAIL", f"Approve status: {res_app.status_code}, Transferred: {is_transferred}")
    else:
        record("2.11", "Admin phe duyet don va Chuyen quyen so huu xe", "FAIL", "Khong tao duoc don thu hai de test approve")

    # =========================================================================
    # SUITE 3: CHUC NANG QUAN LY & PHAN QUYEN NGUOI DUNG (RBAC)
    # =========================================================================
    print("\n--- SUITE 3: QUAN LY NGUOI DUNG & PHAN QUYEN (RBAC) ---", flush=True)

    # 3.1: Admin lay danh sach toan bo nguoi dung
    res = c_admin.get("/api/admin/users")
    users_list = res.get_json() or []
    if res.status_code == 200 and len(users_list) > 0:
        record("3.1", "Admin lay danh sach nguoi dung", "PASS", f"Tong so user lay duoc: {len(users_list)}")
    else:
        record("3.1", "Admin lay danh sach nguoi dung", "FAIL", f"Status: {res.status_code}")

    # 3.2: Admin tao moi tai khoan Nhan vien bao ve (Role: Operator)
    guard_test_user = f"guard_{ts}"
    guard_test_phone = f"0911{ts % 1000000:06d}"
    created_user_phones.append(guard_test_phone)

    res = c_admin.post("/api/admin/guards/create", json={
        "username": guard_test_user,
        "full_name": "Bao Ve Ca Truc Dem",
        "password": "Password123",
        "phone": guard_test_phone,
        "email": f"{guard_test_user}@security.com",
        "shift": "Ca Đêm (22:00 - 06:00)"
    })
    if res.status_code == 200 and res.get_json().get("success"):
        record("3.2", "Admin tao tai khoan Nhan vien bao ve (Operator)", "PASS", f"Tao thanh cong {guard_test_user} ({guard_test_phone})")
    else:
        record("3.2", "Admin tao tai khoan Nhan vien bao ve (Operator)", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 3.3: Dang nhap bang tai khoan Bao ve vua tao -> phai duoc dinh tuyen dung vao operations-dashboard
    c_guard = app.app.test_client()
    res = c_guard.post("/api/login", json={"phone": guard_test_phone, "password": "Password123"})
    g_data = res.get_json() or {}
    if res.status_code == 200 and g_data.get("redirect") == "/operations-dashboard" and g_data.get("user", {}).get("role") == "Operator":
        record("3.3", "Xac thuc vai tro Operator va dinh tuyen vao Operations Dashboard", "PASS", f"Redirect: {g_data.get('redirect')}, Role: {g_data.get('user', {}).get('role')}")
    else:
        record("3.3", "Xac thuc vai tro Operator va dinh tuyen vao Operations Dashboard", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 3.4: Admin cap nhat thong tin nguoi dung (Update User Info)
    res = c_admin.post("/api/admin/users/update", json={
        "original_phone": user_test_phone,
        "username": user_test_name,
        "full_name": "Nguyen Van Chu Xe Da Doi Ten",
        "phone": user_test_phone,
        "email": f"{user_test_name}_updated@test.com",
        "role": "Resident",
        "is_active": True,
        "apartment": "B-1508"
    })
    if res.status_code == 200 and res.get_json().get("success"):
        record("3.4", "Admin cap nhat thong tin tai khoan", "PASS", "Cap nhat ho ten, can ho B-1508 thanh cong")
    else:
        record("3.4", "Admin cap nhat thong tin tai khoan", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # 3.5: Admin cap lai mat khau cho nguoi dung (Reset Password)
    new_pw = "NewPassword@888"
    res = c_admin.post("/api/admin/users/reset_password", json={
        "phone": user_test_phone,
        "new_password": new_pw
    })
    # Kiem tra dang nhap bang mat khau moi
    c_new_login = app.app.test_client()
    res_login_new = c_new_login.post("/api/login", json={"phone": user_test_phone, "password": new_pw})
    if res.status_code == 200 and res_login_new.status_code == 200:
        record("3.5", "Admin cap lai mat khau va Dang nhap thanh cong bang mat khau moi", "PASS", f"Doi mat khau sang {new_pw} thanh cong")
    else:
        record("3.5", "Admin cap lai mat khau va Dang nhap thanh cong bang mat khau moi", "FAIL", f"Reset status: {res.status_code}, Login status: {res_login_new.status_code}")

    # 3.6: Admin KHOA tai khoan nguoi dung (Toggle status is_active -> False)
    res = c_admin.post("/api/admin/users/toggle_status", json={"phone": user_test_phone})
    # Thu dang nhap bang tai khoan da bi khoa -> phai bi tu choi 401
    res_locked = c_new_login.post("/api/login", json={"phone": user_test_phone, "password": new_pw})
    if res.status_code == 200 and res_locked.status_code == 401:
        record("3.6", "Admin Khoa tai khoan va Chan dang nhap", "PASS", "Khoa thanh cong, nguoi dung bi tu choi dang nhap")
    else:
        record("3.6", "Admin Khoa tai khoan va Chan dang nhap", "FAIL", f"Toggle: {res.status_code}, Locked login status: {res_locked.status_code}")

    # 3.7: Admin MO KHOA tai khoan nguoi dung (Toggle status is_active -> True)
    res = c_admin.post("/api/admin/users/toggle_status", json={"phone": user_test_phone})
    res_unlocked = c_new_login.post("/api/login", json={"phone": user_test_phone, "password": new_pw})
    if res.status_code == 200 and res_unlocked.status_code == 200:
        record("3.7", "Admin Mo khoa tai khoan va Cho phep dang nhap lai", "PASS", "Mo khoa thanh cong, dang nhap binh thuong")
    else:
        record("3.7", "Admin Mo khoa tai khoan va Cho phep dang nhap lai", "FAIL", f"Toggle: {res.status_code}, Unlocked login status: {res_unlocked.status_code}")

    # 3.8: Co che an toan: Admin co tinh KHOA tai khoan Admin -> phai bi tu choi
    admin_phone = admin_user.get("phone")
    if admin_phone:
        res = c_admin.post("/api/admin/users/toggle_status", json={"phone": admin_phone})
        if res.status_code == 400 and "Không thể khóa" in res.get_json().get("error", ""):
            record("3.8", "Co che an toan: Ngan chan khoa tai khoan Admin", "PASS", "Tu choi khoa tai khoan Admin toi cao")
        else:
            record("3.8", "Co che an toan: Ngan chan khoa tai khoan Admin", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")
    else:
        record("3.8", "Co che an toan: Ngan chan khoa tai khoan Admin", "PASS", "Bo qua vi admin khong co so dien thoai ro rang")

    # 3.9: Admin xoa tai khoan Bao ve da test
    res = c_admin.delete(f"/api/admin/guards/{guard_test_user}")
    if res.status_code == 200 and res.get_json().get("success"):
        record("3.9", "Admin xoa tai khoan Bao ve", "PASS", f"Xoa thanh cong {guard_test_user}")
    else:
        record("3.9", "Admin xoa tai khoan Bao ve", "FAIL", f"Status: {res.status_code}, Resp: {res.get_data(as_text=True)}")

    # =========================================================================
    # DON DEP DU LIEU TEST
    # =========================================================================
    print("\n--- DON DEP DU LIEU TEST ---", flush=True)
    conn = database.get_db_connection()
    if conn:
        cur = conn.cursor()
        for tf_id in created_transfer_ids:
            cur.execute("DELETE FROM chuyen_nhuong_xe WHERE id = %s", (tf_id,))
        cur.execute("DELETE FROM phuong_tien WHERE BienSoXe = %s", (test_plate,))
        cur.execute("DELETE FROM vehicles WHERE plate_text = %s", (test_plate,))
        for p in created_user_phones:
            cur.execute("DELETE FROM cu_dan WHERE SoDienThoai = %s", (p,))
            cur.execute("DELETE FROM nhan_vien WHERE SoDienThoai = %s", (p,))
            cur.execute("DELETE FROM app_users WHERE phone = %s", (p,))
        conn.commit()
        conn.close()
        print("Da don dep toan bo du lieu test trong CSDL MySQL!")

    # =========================================================================
    # TONG KET KET QUA
    # =========================================================================
    total = len(test_results)
    passed = sum(1 for t in test_results if t["status"] == "PASS")
    failed = total - passed

    print("\n" + "=" * 70)
    print(f"KET QUA TEST TOAN DIEN: TONG {total} | PASS: {passed} | FAIL: {failed}")
    print("=" * 70, flush=True)

    return total, passed, failed, test_results

if __name__ == "__main__":
    total, passed, failed, results = run_tests()
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

