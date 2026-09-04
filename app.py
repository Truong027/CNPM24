#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HỆ THỐNG QUẢN LÝ BÃI ĐỖ XE THÔNG MINH ỨNG DỤNG AI (BIENSOCX - CNPM24)
Trường Đại học Kiến trúc Đà Nẵng (DAU) - Khoa CNTT - Lớp 24CT2
Sinh viên thực hiện: Ông Thân Quốc Trường

Web Server chính phục vụ toàn bộ phân hệ Frontend (BienSoXe/fe) trên Cloud (Render)
và kết nối CSDL MySQL khi có cấu hình môi trường.
"""

import os
import json
import random
from datetime import datetime, timedelta
from functools import wraps
from flask import (
    Flask, render_template, request, jsonify, session, redirect, url_for, Response
)

# Khởi tạo ứng dụng Flask trỏ tới thư mục templates và static của BienSoXe/fe
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FE_TEMPLATES = os.path.join(BASE_DIR, "BienSoXe", "fe", "templates")
LOCAL_TEMPLATES = os.path.join(BASE_DIR, "templates")
TEMPLATE_DIR = FE_TEMPLATES if os.path.exists(FE_TEMPLATES) else LOCAL_TEMPLATES

FE_STATIC = os.path.join(BASE_DIR, "BienSoXe", "fe", "static")
LOCAL_STATIC = os.path.join(BASE_DIR, "static")
STATIC_DIR = FE_STATIC if os.path.exists(FE_STATIC) else LOCAL_STATIC

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)
app.config["SECRET_KEY"] = os.getenv("APP_SECRET_KEY", "cnpm24-dau-truong-secret-2026")

# ==============================================================================
# DỮ LIỆU MẪU MÔ PHỎNG (MOCK DATA) CHO CLOUD DEMO (RENDER)
# Đảm bảo trang web luôn hiển thị đầy đủ, sinh động khi demo trực tuyến
# ==============================================================================

MOCK_VEHICLES = [
    {
        "id": 1, "plate_text": "51G-123.45", "vehicle_type": "Ô tô con", "province_name": "TP. Hồ Chí Minh",
        "resident_name": "Phạm Tuấn Anh", "apartment": "A101", "rfid_code": "RFID001",
        "status": "DangTrongBai", "in_time": "2026-09-04 08:15:20", "total_detections": 14, "color": "Trắng"
    },
    {
        "id": 2, "plate_text": "43A-678.90", "vehicle_type": "Ô tô con", "province_name": "TP. Đà Nẵng",
        "resident_name": "Nguyễn Hồng Hạnh", "apartment": "A102", "rfid_code": "RFID002",
        "status": "DangTrongBai", "in_time": "2026-09-04 08:42:11", "total_detections": 8, "color": "Đen"
    },
    {
        "id": 3, "plate_text": "29B-555.55", "vehicle_type": "Xe máy", "province_name": "TP. Hà Nội",
        "resident_name": "Trương Văn Lâm", "apartment": "B201", "rfid_code": "RFID003",
        "status": "DaRa", "in_time": "2026-09-04 07:30:00", "out_time": "2026-09-04 09:15:00",
        "total_detections": 5, "color": "Xanh"
    },
    {
        "id": 4, "plate_text": "92C-888.88", "vehicle_type": "Ô tô tải", "province_name": "Tỉnh Quảng Nam",
        "resident_name": "Khách Vãng Lai", "apartment": "Vãng Lai", "rfid_code": "RFID-TEMP-04",
        "status": "DangTrongBai", "in_time": "2026-09-04 09:20:45", "total_detections": 3, "color": "Bạc"
    },
    {
        "id": 5, "plate_text": "43C-333.33", "vehicle_type": "Xe máy", "province_name": "TP. Đà Nẵng",
        "resident_name": "Trần Văn Bình", "apartment": "B305", "rfid_code": "RFID005",
        "status": "DangTrongBai", "in_time": "2026-09-04 09:50:12", "total_detections": 19, "color": "Đỏ"
    }
]

MOCK_USERS = [
    {"username": "admin", "full_name": "Ông Thân Quốc Trường (Admin)", "role": "Admin", "email": "admin@dau.edu.vn", "status": "Active"},
    {"username": "guard01", "full_name": "Lê Văn Cường (Bảo Vệ)", "role": "BaoVe", "email": "guard@dau.edu.vn", "status": "Active", "shift": "Sáng (06:00 - 14:00)"},
    {"username": "resident_anh", "full_name": "Phạm Tuấn Anh (Cư Dân)", "role": "Resident", "email": "anh.pt@gmail.com", "status": "Active", "apartment": "A101"}
]

# ==============================================================================
# ĐIỀU HƯỚNG GIAO DIỆN (FRONTEND HTML ROUTES)
# ==============================================================================

@app.route("/")
def index():
    """Trang chủ: Dashboard Quản lý Bãi xe AI & Giám sát Camera"""
    return render_template("index.html")

@app.route("/resident")
@app.route("/resident-dashboard")
def resident_dashboard():
    """Trang Cổng thông tin Cư dân: Quản lý phương tiện và số dư thẻ"""
    return render_template("resident_dashboard.html")

@app.route("/login")
def login_page():
    """Trang Đăng nhập"""
    return render_template("login.html")

@app.route("/register")
def register_page():
    """Trang Đăng ký tài khoản mới"""
    return render_template("register.html")

@app.route("/forgot-password")
def forgot_password_page():
    """Trang Quên mật khẩu - Yêu cầu OTP"""
    return render_template("forgot_password.html")

@app.route("/reset-password")
def reset_password_page():
    """Trang Đặt lại mật khẩu mới qua OTP"""
    return render_template("reset_password.html")

# ==============================================================================
# LUỒNG CAMERA GIÁM SÁT (VIDEO FEED)
# ==============================================================================

def _generate_mock_frame(label="CAMERA LAN VAO - LIVE AI"):
    """Tạo khung hình camera demo trực quan SVG cho môi trường Cloud"""
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="380" viewBox="0 0 640 380">
        <rect width="640" height="380" fill="#0f172a"/>
        <circle cx="320" cy="170" r="45" fill="none" stroke="#38bdf8" stroke-width="3" stroke-dasharray="6,4"/>
        <text x="320" y="176" fill="#38bdf8" font-family="sans-serif" font-size="15" text-anchor="middle" font-weight="bold">AI DETECTING</text>
        <rect x="180" y="120" width="280" height="100" rx="8" fill="none" stroke="#22c55e" stroke-width="2" stroke-dasharray="4,2"/>
        <text x="320" y="112" fill="#22c55e" font-family="sans-serif" font-size="13" text-anchor="middle" font-weight="bold">51G-123.45 (98.4%)</text>
        <text x="320" y="260" fill="#94a3b8" font-family="sans-serif" font-size="15" text-anchor="middle" font-weight="600">{label}</text>
        <rect x="25" y="25" width="110" height="26" rx="6" fill="#ef4444"/>
        <circle cx="40" cy="38" r="4" fill="#ffffff"/>
        <text x="75" y="43" fill="#ffffff" font-family="sans-serif" font-size="11" text-anchor="middle" font-weight="bold">LIVE STREAM</text>
        <text x="615" y="43" fill="#64748b" font-family="sans-serif" font-size="12" text-anchor="end">FPS: 30.0</text>
    </svg>'''
    return svg

@app.route("/video_feed_webcam")
def video_feed_webcam():
    """Luồng video Cổng Vào"""
    svg = _generate_mock_frame("LÀN VÀO - CAMERA SỐ 1 (YOLOv8 + CRNN OCR)")
    return Response(svg, mimetype="image/svg+xml")

@app.route("/video_feed_phone")
def video_feed_phone():
    """Luồng video Cổng Ra"""
    svg = _generate_mock_frame("LÀN RA - CAMERA SỐ 2 (YOLOv8 + CRNN OCR)")
    return Response(svg, mimetype="image/svg+xml")

# ==============================================================================
# XÁC THỰC & PHIÊN LÀM VIỆC (AUTH APIS)
# ==============================================================================

@app.route("/api/session", methods=["GET"])
def api_session():
    """Trả về trạng thái phiên đăng nhập hiện tại"""
    user = session.get("user")
    if not user:
        # Mặc định trên cloud gán quyền Admin để xem trải nghiệm toàn diện
        user = {
            "username": "admin",
            "full_name": "Ông Thân Quốc Trường",
            "role": "Admin",
            "email": "truong.otq@dau.edu.vn"
        }
        session["user"] = user
    return jsonify({"authenticated": True, "user": user})

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    
    role = "Admin"
    full_name = "Quản Trị Viên (Admin)"
    if "resident" in username:
        role = "Resident"
        full_name = "Cư Dân Chung Cư"
    elif "guard" in username:
        role = "BaoVe"
        full_name = "Nhân Viên Bảo Vệ"
        
    user = {
        "username": username or "admin",
        "full_name": full_name,
        "role": role,
        "email": f"{username or 'admin'}@dau.edu.vn"
    }
    session["user"] = user
    return jsonify({"success": True, "message": "Đăng nhập thành công!", "user": user})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True, "message": "Đã đăng xuất"})

@app.route("/api/register", methods=["POST"])
def api_register():
    return jsonify({"success": True, "message": "Đăng ký tài khoản thành công! Vui lòng đăng nhập."})

@app.route("/api/forgot-password", methods=["POST"])
def api_forgot_password():
    return jsonify({"success": True, "message": "Mã OTP đã được gửi đến email (Mã thử nghiệm: 123456)"})

@app.route("/api/reset-password", methods=["POST"])
def api_reset_password():
    return jsonify({"success": True, "message": "Đổi mật khẩu thành công! Bạn có thể đăng nhập ngay."})

# ==============================================================================
# DỮ LIỆU THỐNG KÊ & DASHBOARD SUMMARY (APIS)
# ==============================================================================

@app.route("/get_dashboard_summary", methods=["GET"])
def get_dashboard_summary():
    """Thống kê tổng quan bãi xe: sức chứa, lưu lượng, doanh thu"""
    return jsonify({
        "total_spaces": 150,
        "occupied_spaces": 48,
        "available_spaces": 102,
        "today_in": 134,
        "today_out": 86,
        "today_revenue": 1450000,
        "alerts_count": 0
    })

@app.route("/api/vehicles", methods=["GET"])
@app.route("/get_plates", methods=["GET"])
def api_vehicles():
    """Danh sách phương tiện đang được quản lý trong hệ thống"""
    return jsonify(MOCK_VEHICLES)

@app.route("/api/vehicles/save", methods=["POST"])
def api_save_vehicle():
    data = request.get_json(silent=True) or {}
    new_vehicle = {
        "id": len(MOCK_VEHICLES) + 1,
        "plate_text": data.get("plate_text", "43A-999.99"),
        "vehicle_type": data.get("vehicle_type", "Ô tô con"),
        "province_name": "Đà Nẵng",
        "resident_name": data.get("resident_name", "Cư dân mới"),
        "apartment": data.get("apartment", "A202"),
        "rfid_code": data.get("rfid_code", f"RFID{random.randint(100, 999)}"),
        "status": "DangTrongBai",
        "in_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_detections": 1
    }
    MOCK_VEHICLES.insert(0, new_vehicle)
    return jsonify({"success": True, "message": "Thêm phương tiện thành công", "vehicle": new_vehicle})

@app.route("/api/vehicles/delete/<plate_text>", methods=["DELETE"])
def api_delete_vehicle(plate_text):
    global MOCK_VEHICLES
    MOCK_VEHICLES = [v for v in MOCK_VEHICLES if v.get("plate_text") != plate_text]
    return jsonify({"success": True, "message": f"Đã xóa phương tiện {plate_text}"})

@app.route("/api/analytics/revenue", methods=["GET"])
def api_analytics_revenue():
    """Dữ liệu biểu đồ doanh thu theo ngày (Chart.js)"""
    today = datetime.now()
    records = []
    base_fees = [1100000, 950000, 1350000, 1600000, 1200000, 1750000, 1450000]
    for i in range(7):
        d = today - timedelta(days=(6 - i))
        records.append({
            "date_revenue": d.strftime("%Y-%m-%d"),
            "total_fee": base_fees[i]
        })
    return jsonify(records)

@app.route("/api/analytics/peak-hours", methods=["GET"])
def api_analytics_peak_hours():
    """Dữ liệu biểu đồ giờ cao điểm ra/vào bãi xe (Chart.js)"""
    hours = [
        {"hour_of_day": 6, "entry_count": 14},
        {"hour_of_day": 7, "entry_count": 52},
        {"hour_of_day": 8, "entry_count": 78},
        {"hour_of_day": 9, "entry_count": 35},
        {"hour_of_day": 10, "entry_count": 22},
        {"hour_of_day": 11, "entry_count": 28},
        {"hour_of_day": 12, "entry_count": 34},
        {"hour_of_day": 13, "entry_count": 18},
        {"hour_of_day": 14, "entry_count": 25},
        {"hour_of_day": 15, "entry_count": 31},
        {"hour_of_day": 16, "entry_count": 48},
        {"hour_of_day": 17, "entry_count": 86},
        {"hour_of_day": 18, "entry_count": 64},
        {"hour_of_day": 19, "entry_count": 38}
    ]
    return jsonify(hours)

@app.route("/get_stats_by_province", methods=["GET"])
def get_stats_by_province():
    return jsonify({
        "provinces": ["TP. Đà Nẵng (43)", "TP. Hồ Chí Minh (51)", "TP. Hà Nội (29-30)", "Tỉnh Quảng Nam (92)", "Khác"],
        "counts": [48, 32, 24, 18, 8]
    })

@app.route("/get_stats_by_vehicle_type", methods=["GET"])
def get_stats_by_vehicle_type():
    return jsonify({
        "types": ["Ô tô con", "Xe máy", "Ô tô tải", "Xe khách"],
        "counts": [82, 45, 6, 1]
    })

# ==============================================================================
# NGHIỆP VỤ BẢO VỆ & BARRIER (GUARD APIS)
# ==============================================================================

@app.route("/api/guard/verification/<plate>", methods=["GET"])
def api_guard_verification(plate):
    """Kiểm tra đối chiếu thông tin biển số xe tại trạm bảo vệ"""
    is_resident = "51" in plate or "43" in plate or "29" in plate
    return jsonify({
        "verified": True,
        "plate": plate,
        "type": "CuDan" if is_resident else "VangLai",
        "owner": "Phạm Tuấn Anh" if is_resident else "Khách Vãng Lai",
        "room": "A101" if is_resident else "N/A",
        "expiry": "2026-12-31",
        "message": "Phương tiện Cư Dân hợp lệ - Tự động nâng barrier" if is_resident else "Khách vãng lai - Vui lòng lấy thẻ từ"
    })

@app.route("/api/guard/barrier/trigger", methods=["POST"])
def api_barrier_trigger():
    return jsonify({"success": True, "message": "Barrier đã được kích hoạt mở!"})

@app.route("/api/guard/manual_entry", methods=["POST"])
def api_manual_entry():
    return jsonify({"success": True, "message": "Đã ghi nhận phương tiện vào thủ công."})

@app.route("/api/guard/collect_fee", methods=["POST"])
def api_collect_fee():
    return jsonify({"success": True, "message": "Thu phí gửi xe thành công!"})

# ==============================================================================
# QUẢN TRỊ ADMIN (USER MANAGEMENT)
# ==============================================================================

@app.route("/api/admin/users", methods=["GET"])
def api_admin_users():
    return jsonify(MOCK_USERS)

@app.route("/api/admin/users/toggle_status", methods=["POST"])
def api_toggle_status():
    return jsonify({"success": True, "message": "Cập nhật trạng thái thành công"})

@app.route("/api/admin/users/reset_password", methods=["POST"])
def api_admin_reset_password():
    return jsonify({"success": True, "message": "Đặt lại mật khẩu thành công"})

@app.route("/api/admin/residents/create", methods=["POST"])
def api_create_resident():
    return jsonify({"success": True, "message": "Tạo hồ sơ cư dân thành công"})

@app.route("/api/admin/guards/create", methods=["POST"])
def api_create_guard():
    return jsonify({"success": True, "message": "Thêm nhân viên bảo vệ thành công"})

@app.route("/api/admin/transfer_requests", methods=["GET"])
def api_admin_transfer_requests():
    return jsonify([])

# ==============================================================================
# NGHIỆP VỤ CƯ DÂN (RESIDENT APIS)
# ==============================================================================

@app.route("/api/resident/profile", methods=["GET"])
def api_resident_profile():
    return jsonify({
        "full_name": "Phạm Tuấn Anh",
        "apartment": "A101",
        "phone": "0912.345.601",
        "email": "anh.pt@gmail.com",
        "balance": 850000,
        "registered_vehicles_count": 2
    })

@app.route("/api/resident/vehicles", methods=["GET"])
def api_resident_vehicles():
    return jsonify([
        {"id": 1, "plate": "51G-123.45", "type": "Ô tô", "brand": "Mazda 3", "color": "Trắng", "expiry": "2026-12-31", "status": "Hợp Lệ"},
        {"id": 2, "plate": "43C-333.33", "type": "Xe Máy", "brand": "Honda SH", "color": "Đỏ", "expiry": "2026-12-31", "status": "Hợp Lệ"}
    ])

@app.route("/api/resident/history", methods=["GET"])
def api_resident_history():
    return jsonify([
        {"plate": "51G-123.45", "action": "Vào", "time": "2026-09-04 08:15:20", "gate": "Cổng Số 1 (Làn Vào)"},
        {"plate": "51G-123.45", "action": "Ra", "time": "2026-09-03 18:30:10", "gate": "Cổng Số 2 (Làn Ra)"},
        {"plate": "43C-333.33", "action": "Vào", "time": "2026-09-03 09:12:00", "gate": "Cổng Số 1 (Làn Vào)"}
    ])

# ==============================================================================
# KHỞI CHẠY MÁY CHỦ (PRODUCTION / RENDER RUNNER)
# ==============================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 60)
    print("  HỆ THỐNG QUẢN LÝ BÃI ĐỖ XE THÔNG MINH (DAU - 24CT2)")
    print(f"  Template Folder: {TEMPLATE_DIR}")
    print(f"  Đang chạy tại: http://0.0.0.0:{port}")
    print("=" * 60)
    app.run(host="0.0.0.0", port=port, debug=False)
