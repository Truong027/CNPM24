#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HỆ THỐNG QUẢN LÝ BÃI ĐỖ XE THÔNG MINH ỨNG DỤNG AI
Trường Đại học Kiến trúc Đà Nẵng (DAU) - Khoa CNTT - Lớp 24CT2
Sinh viên thực hiện: Ông Thân Quốc Trường

Entry point chuyển tiếp tới Backend Flask Server (be/app.py).
Cho phép khởi chạy trực tiếp từ thư mục gốc hoặc thư mục be/:
    python app.py
hoặc:
    python be/app.py
"""

import os
import sys

# Đảm bảo thư mục be/ luôn nằm ở đầu danh sách tìm kiếm module
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BE_DIR = os.path.join(CURRENT_DIR, "be")
if BE_DIR not in sys.path:
    sys.path.insert(0, BE_DIR)

from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    print(f"🚀 [ROOT LAUNCHER] Starting Smart Parking Web Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
