# -*- coding: utf-8 -*-
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
be_dir = os.path.abspath(os.path.join(current_dir, "..", "be"))
if be_dir not in sys.path:
    sys.path.insert(0, be_dir)

import database

test_accounts = [
    ('0900000001', 'admin123', 'Admin'),
    ('0912345678', '123456', 'Operator'),
    ('0923456789', '123456', 'Operator'),
    ('0901234567', '123456', 'Resident'),
    ('0907654321', '123456', 'Resident'),
    ('admin', 'admin123', 'Admin'),
]

all_ok = True
for phone_or_user, pwd, expected_role in test_accounts:
    u = database.authenticate_user(phone_or_user, pwd)
    if not u or u.get('role') != expected_role:
        print(f"❌ FAILED login for {phone_or_user}: got {u}")
        all_ok = False
    else:
        name = u.get("full_name") or u.get("username")
        role = u.get("role")
        print(f"✅ SUCCESS login for [{phone_or_user}] -> User: {name} (Vai trò: {role})")

if all_ok:
    print("\n🎉 TẤT CẢ 6/6 TÀI KHOẢN MẪU ĐĂNG NHẬP CHUẨN SĐT THÀNH CÔNG 100%!")

