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
import subprocess

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Tự động kích hoạt/chuyển tiếp sang môi trường ảo .venv (đã có đầy đủ PyTorch, YOLO, EasyOCR)
venv_python = os.path.join(CURRENT_DIR, ".venv", "Scripts", "python.exe")
if os.path.exists(venv_python) and os.path.abspath(sys.executable).lower() != os.path.abspath(venv_python).lower():
    print(f"[*] [AUTO-VENV] Chuyen sang moi truong ao day du AI: {venv_python}")
    try:
        sys.exit(subprocess.call([venv_python] + sys.argv))
    except KeyboardInterrupt:
        sys.exit(0)

# Đảm bảo thư mục be/ luôn nằm ở đầu danh sách tìm kiếm module
BE_DIR = os.path.join(CURRENT_DIR, "be")
if BE_DIR not in sys.path:
    sys.path.insert(0, BE_DIR)

try:
    from be.app import app
except ImportError:
    from app import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    print(f"🚀 [ROOT LAUNCHER] Starting Smart Parking Web Server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
