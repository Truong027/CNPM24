#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sinh file Draw.io (.drawio XML) và PlantUML (.puml) cho toàn bộ
Sơ đồ Tuần tự (Sequence Diagrams) của hệ thống Quản lý Bãi đỗ xe thông minh AI (CNPM24).

Được thiết kế chính xác theo đúng hướng dẫn của giảng viên:
  - Cột 1: Tác nhân (Actor)
  - Cột 2: Giao diện (File code tương ứng)
  - Cột 3: Hệ thống (File code / Hàm tương ứng)
  - Cột 4: Cơ sở dữ liệu (Database / Bảng tương ứng)
"""

import os
import sys
import xml.etree.ElementTree as ET

# Đảm bảo UTF-8 cho stdout trên Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DIAGRAMS = [
    {
        "id": "uc01_register",
        "name": "1. Đăng ký tài khoản cư dân",
        "actor": "Cư Dân\n(Resident)",
        "ui_path": "fe/templates/register.html\n(hoặc fe/templates/login.html#register)",
        "sys_path": "be/app.py: register()\nbe/database.py: register_resident_user()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\napp_users, cu_dan",
        "steps": [
            ("actor", "ui", "1. Nhập họ tên, SĐT, căn hộ, mật khẩu & Bấm 'Đăng ký'"),
            ("ui", "sys", "2. POST /register (username, password, phone, apartment)"),
            ("sys", "db", "3. SELECT * FROM app_users WHERE username = %s OR phone = %s"),
            ("db", "sys", "4. Trả về kết quả kiểm tra (Chưa tồn tại)"),
            ("sys", "sys", "5. Băm mật khẩu an toàn PBKDF2/SHA-256 (generate_password_hash)"),
            ("sys", "db", "6. INSERT INTO app_users & cu_dan (MaCuDan, HoTen, TenDangNhap...)"),
            ("db", "sys", "7. Xác nhận ghi bản ghi thành công (Affected rows = 1)"),
            ("sys", "ui", "8. Phản hồi JSON: {success: true, message: 'Đăng ký thành công'}"),
            ("ui", "actor", "9. Hiển thị Toast thông báo thành công & Chuyển hướng sang Đăng nhập")
        ]
    },
    {
        "id": "uc02_login",
        "name": "2. Đăng nhập hệ thống",
        "actor": "Người Dùng\n(Admin/Bảo vệ/Cư dân)",
        "ui_path": "fe/templates/login.html\n(Form #loginForm)",
        "sys_path": "be/app.py: login()\nbe/database.py: check_user_credentials()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\napp_users, cu_dan, nhan_vien",
        "steps": [
            ("actor", "ui", "1. Nhập tên đăng nhập, mật khẩu & Bấm 'Đăng nhập'"),
            ("ui", "sys", "2. POST /login (username, password)"),
            ("sys", "db", "3. SELECT * FROM app_users WHERE username = %s AND status = 'active'"),
            ("db", "sys", "4. Trả về thông tin user & password_hash"),
            ("sys", "sys", "5. Đối soát mật khẩu (check_password_hash) & Khởi tạo session['user']"),
            ("sys", "ui", "6. Phản hồi JSON: {success: true, role: 'Resident'/'Admin'/'Operator'}"),
            ("ui", "actor", "7. Điều hướng vào trang làm việc tương ứng (/ hoặc /resident-dashboard)")
        ]
    },
    {
        "id": "uc03_register_vehicle_cinema",
        "name": "3. Đăng ký xe & Chọn ô đỗ Cinema",
        "actor": "Cư Dân\n(Resident)",
        "ui_path": "fe/templates/resident_dashboard.html\n(Modal #registerVehicleModal, #cinemaModal)",
        "sys_path": "be/app.py: POST /api/resident/register_vehicle\nbe/database.py: register_vehicle_with_slot()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nbai_do, vehicles, phuong_tien",
        "steps": [
            ("actor", "ui", "1. Nhập biển số, màu xe & Chọn vị trí ô đỗ (VD: B1-A01) trên sơ đồ"),
            ("ui", "sys", "2. POST /api/resident/register_vehicle (plate, slot_id, months)"),
            ("sys", "db", "3. Kiểm tra ô đỗ: SELECT TrangThai FROM bai_do WHERE MaViTri = %s FOR UPDATE"),
            ("db", "sys", "4. Trả về trạng thái ô đỗ (TrangThai = 'Trong')"),
            ("sys", "db", "5. UPDATE bai_do SET TrangThai = 'DaDat', BienSoXe = %s"),
            ("sys", "db", "6. INSERT INTO vehicles & phuong_tien (BienSoXe, MaCuDan, ViTriDo, NgayHetHan)"),
            ("db", "sys", "7. Trả về kết quả ghi dữ liệu thành công"),
            ("sys", "ui", "8. Phản hồi JSON: {success: true, slot: 'B1-A01', plate: '30H-999.88'}"),
            ("ui", "actor", "9. Cập nhật thẻ xe 3D lên màn hình & Đổi màu ô đỗ thành Cyan (Xe của bạn)")
        ]
    },
    {
        "id": "uc04_change_slot",
        "name": "4. Đổi vị trí đỗ xe Cinema",
        "actor": "Cư Dân\n(Resident)",
        "ui_path": "fe/templates/resident_dashboard.html\n(Modal #changeSlotModal, renderCinemaSeats)",
        "sys_path": "be/app.py: POST /api/parking/change_slot\nbe/database.py: change_vehicle_parking_slot()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nbai_do, vehicles, phuong_tien",
        "steps": [
            ("actor", "ui", "1. Chọn xe cần đổi & Click chọn vị trí ô trống mới (VD: B1-B05)"),
            ("ui", "sys", "2. POST /api/parking/change_slot (plate: '30H-999.88', new_slot: 'B1-B05')"),
            ("sys", "db", "3. Kiểm tra ô mới: SELECT TrangThai FROM bai_do WHERE MaViTri = 'B1-B05'"),
            ("db", "sys", "4. Xác nhận ô mới còn 'Trong'"),
            ("sys", "db", "5. TRANSACTION: Giải phóng ô cũ (TrangThai = 'Trong')"),
            ("sys", "db", "6. Đặt chỗ ô mới (TrangThai = 'DaDat') & Cập nhật ViTriDo trong phuong_tien"),
            ("db", "sys", "7. Commit transaction thành công"),
            ("sys", "ui", "8. Phản hồi JSON: {success: true, message: 'Đổi vị trí đỗ thành công'}"),
            ("ui", "actor", "9. Render lại sơ đồ bãi đỗ Cinema & Hiển thị thông báo thành công")
        ]
    },
    {
        "id": "uc05_renew_pass",
        "name": "5. Gia hạn vé tháng cư dân",
        "actor": "Cư Dân\n(Resident)",
        "ui_path": "fe/templates/resident_dashboard.html\n(Modal #renewTicketModal)",
        "sys_path": "be/app.py: POST /api/resident/renew_ticket\nbe/database.py: renew_monthly_ticket()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nvehicles, phuong_tien",
        "steps": [
            ("actor", "ui", "1. Chọn gói gia hạn (1, 3 hoặc 6 tháng) & Bấm 'Xác nhận gia hạn'"),
            ("ui", "sys", "2. POST /api/resident/renew_ticket (plate: '30H-999.88', months: 3)"),
            ("sys", "db", "3. SELECT NgayHetHan FROM phuong_tien WHERE BienSoXe = %s"),
            ("db", "sys", "4. Trả về ngày hết hạn hiện tại"),
            ("sys", "sys", "5. Cộng dồn thời hạn mới (new_expiry = max(current_expiry, today) + months)"),
            ("sys", "db", "6. UPDATE phuong_tien & vehicles SET NgayHetHan = %s WHERE BienSoXe = %s"),
            ("db", "sys", "7. Xác nhận cập nhật CSDL thành công"),
            ("sys", "ui", "8. Phản hồi JSON: {success: true, new_expiry: '2026-12-31'}"),
            ("ui", "actor", "9. Cập nhật nhãn hạn vé tháng trên thẻ xe 3D và hiển thị badge 'Còn Hạn'")
        ]
    },
    {
        "id": "uc06_transfer_request",
        "name": "6. Yêu cầu chuyển nhượng xe",
        "actor": "Cư Dân\n(Resident)",
        "ui_path": "fe/templates/resident_dashboard.html\n(Modal #transferVehicleModal)",
        "sys_path": "be/app.py: POST /api/resident/transfer_vehicle\nbe/database.py: create_vehicle_transfer_request()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nchuyen_nhuong_xe, cu_dan, vehicles",
        "steps": [
            ("actor", "ui", "1. Nhập SĐT người nhận, căn hộ mới, lý do chuyển nhượng & Bấm 'Gửi yêu cầu'"),
            ("ui", "sys", "2. POST /api/resident/transfer_vehicle (plate, target_phone, reason)"),
            ("sys", "db", "3. SELECT MaCuDan FROM cu_dan WHERE SoDienThoai = %s"),
            ("db", "sys", "4. Trả về thông tin cư dân nhận hợp lệ"),
            ("sys", "db", "5. INSERT INTO chuyen_nhuong_xe (BienSoXe, NguoiChuyen, NguoiNhan, TrangThai)"),
            ("db", "sys", "6. Tạo bản ghi đơn chuyển nhượng mới với TrangThai = 'ChoDuyet'"),
            ("sys", "ui", "7. Phản hồi JSON: {success: true, request_id: 12, status: 'ChoDuyet'}"),
            ("ui", "actor", "8. Hiển thị thông báo 'Đã gửi yêu cầu đến Quản trị viên phê duyệt'")
        ]
    },
    {
        "id": "uc07_parking_history",
        "name": "7. Tra cứu lịch sử xe vào/ra",
        "actor": "Cư Dân\n(Resident)",
        "ui_path": "fe/templates/resident_dashboard.html\n(Bảng lịch sử #historySection)",
        "sys_path": "be/app.py: GET /api/resident/history\nbe/database.py: get_resident_vehicle_history()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nparking_sessions, lich_su_ra_vao",
        "steps": [
            ("actor", "ui", "1. Chọn biển số xe cần tra cứu & Khoảng ngày tra cứu"),
            ("ui", "sys", "2. GET /api/resident/history?plate=30H-999.88"),
            ("sys", "db", "3. SELECT * FROM parking_sessions WHERE plate_text = %s ORDER BY check_in_time DESC"),
            ("db", "sys", "4. Trả về danh sách phiên: Giờ vào, Giờ ra, Phí thu, Trạng thái, Ảnh chụp"),
            ("sys", "ui", "5. Phản hồi danh sách phiên gửi xe dưới dạng JSON"),
            ("ui", "actor", "6. Render bảng lịch sử trực quan kèm ảnh chụp snapshot vào-ra")
        ]
    },
    {
        "id": "uc08_auto_checkin",
        "name": "8. Nhận diện AI & Tự động Check-in xe vào",
        "actor": "Tài xế / Camera Cổng Vào\n(Gate Camera & Driver)",
        "ui_path": "fe/templates/index.html\n(Tab #recognition-page, Live Stream)",
        "sys_path": "be/app.py: gen_frames() & detect_plates_from_frame()\nbe/database.py: process_parking_transaction()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nparking_sessions, lich_su_ra_vao, detections",
        "steps": [
            ("actor", "ui", "1. Xe tiến vào làn cổng vào, camera ghi nhận luồng video (Frames)"),
            ("ui", "sys", "2. Stream video MJPEG tới backend (Camera Loop gen_frames)"),
            ("sys", "sys", "3. YOLOv8 phát hiện bounding box biển số -> CRNN đọc chuỗi ký tự (VD: '51G-123.45')"),
            ("sys", "db", "4. Tra cứu xe đang đỗ: SELECT id FROM parking_sessions WHERE plate_text = %s AND status = 'Parked'"),
            ("db", "sys", "5. Không có phiên mở -> Xe đang vào mới"),
            ("sys", "db", "6. INSERT INTO parking_sessions (plate_text, check_in_time, status='Parked', gate_in='Cổng Vào')"),
            ("sys", "db", "7. INSERT INTO lich_su_ra_vao & detections (Lưu lịch sử & độ tin cậy AI)"),
            ("db", "sys", "8. Xác nhận tạo phiên gửi xe thành công"),
            ("sys", "ui", "9. Đẩy thông báo Live Event 'Xe vào thành công' lên Bàn trực bảo vệ"),
            ("ui", "actor", "10. Mở barrier tự động & Hiển thị biển số trên bảng LED cổng vào")
        ]
    },
    {
        "id": "uc09_checkout_verification",
        "name": "9. Đối chiếu xe ra & Cảnh báo Blacklist",
        "actor": "Nhân Viên Bảo Vệ\n(Guard)",
        "ui_path": "fe/templates/index.html\n(Bàn trực #guard-station-page, checkGuardLiveEvent)",
        "sys_path": "be/app.py: GET /api/guard/verification/<plate>\nbe/database.py: get_guard_verification_info()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nvehicles, parking_sessions, bai_do",
        "steps": [
            ("actor", "ui", "1. Camera cổng ra phát hiện xe hoặc Bảo vệ click chọn xe chuẩn bị ra"),
            ("ui", "sys", "2. GET /api/guard/verification/51G-123.45"),
            ("sys", "db", "3. Truy vấn phiên đỗ: SELECT * FROM parking_sessions WHERE plate_text = %s AND status = 'Parked'"),
            ("sys", "db", "4. Truy vấn loại xe: SELECT group_type, monthly_ticket_expiry FROM vehicles WHERE plate_text = %s"),
            ("db", "sys", "5. Trả về thông tin phiên vào, ảnh snapshot vào, nhóm xe, hạn vé tháng"),
            ("sys", "sys", "6. Tính thời gian đỗ, tính cước phí (Vé tháng = 0đ, Vãng lai = theo block giờ)"),
            ("sys", "sys", "7. Kiểm tra Blacklist: Nếu group_type = 'Blacklist' -> Bật cờ cảnh báo an ninh"),
            ("sys", "ui", "8. Phản hồi JSON: {verification_data, fee: 0, is_blacklist: false}"),
            ("ui", "actor", "9. Hiển thị song song 2 ảnh [Ảnh Vào] vs [Ảnh Ra Thực Tế] & Hộp tính phí")
        ]
    },
    {
        "id": "uc10_collect_fee_barrier",
        "name": "10. Thu phí & Kích hoạt Barrier cổng ra",
        "actor": "Nhân Viên Bảo Vệ\n(Guard)",
        "ui_path": "fe/templates/index.html\n(#guardFeeBox, #guardConfirmActionBtn)",
        "sys_path": "be/app.py: POST /api/guard/collect_fee\nbe/database.py: complete_parking_session()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nparking_sessions, lich_su_ra_vao",
        "steps": [
            ("actor", "ui", "1. Bảo vệ xác nhận thu tiền mặt/QR và bấm 'Xác Nhận Thu Phí & Mở Barrier'"),
            ("ui", "sys", "2. POST /api/guard/collect_fee (session_id: 105, amount: 20000, method: 'Cash')"),
            ("sys", "db", "3. UPDATE parking_sessions SET status = 'Completed', check_out_time = NOW(), fee = %s"),
            ("sys", "db", "4. UPDATE lich_su_ra_vao SET ThoiGianRa = NOW(), TrangThai = 'DaThanhToan'"),
            ("db", "sys", "5. Trả về kết quả cập nhật thành công"),
            ("sys", "sys", "6. Kích hoạt tín hiệu mở Barrier (barrier_state = 'OPEN')"),
            ("sys", "ui", "7. Phản hồi JSON: {success: true, invoice_code: 'HD-20261002-01', barrier: 'OPEN'}"),
            ("ui", "actor", "8. In hóa đơn điện tử, bật thông báo 'Cho xe qua cổng' & Cổng Barrier nâng lên")
        ]
    },
    {
        "id": "uc11_admin_user_mgmt",
        "name": "11. Quản lý tài khoản người dùng",
        "actor": "Quản Trị Viên\n(Admin)",
        "ui_path": "fe/templates/index.html\n(Trang quản lý #users-page, Modal #editUserModal)",
        "sys_path": "be/app.py: POST /api/admin/users/update\nbe/database.py: admin_update_user_info()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\napp_users, cu_dan, nhan_vien",
        "steps": [
            ("actor", "ui", "1. Chọn tài khoản cần chỉnh sửa, cập nhật quyền hạn/trạng thái khóa & Bấm 'Lưu'"),
            ("ui", "sys", "2. POST /api/admin/users/update (user_id: 5, role: 'Operator', status: 'active')"),
            ("sys", "db", "3. UPDATE app_users SET role = %s, status = %s WHERE id = %s"),
            ("sys", "db", "4. Đồng bộ cập nhật bảng cu_dan / nhan_vien tương ứng"),
            ("db", "sys", "5. Xác nhận cập nhật thông tin thành công"),
            ("sys", "ui", "6. Phản hồi JSON: {success: true, message: 'Cập nhật tài khoản thành công'}"),
            ("ui", "actor", "7. Tải lại danh sách tài khoản & Hiển thị badge quyền hạn mới")
        ]
    },
    {
        "id": "uc12_admin_approve_transfer",
        "name": "12. Phê duyệt chuyển nhượng xe",
        "actor": "Quản Trị Viên\n(Admin)",
        "ui_path": "fe/templates/index.html\n(Trang chuyển nhượng #transfers-page)",
        "sys_path": "be/app.py: POST /api/admin/transfer_requests/<id>/action\nbe/database.py: process_transfer_request_action()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nchuyen_nhuong_xe, vehicles, phuong_tien, cu_dan",
        "steps": [
            ("actor", "ui", "1. Xem thông tin đơn chuyển nhượng đang chờ & Bấm nút 'Phê Duyệt'"),
            ("ui", "sys", "2. POST /api/admin/transfer_requests/12/action (action: 'approve')"),
            ("sys", "db", "3. Lấy thông tin đơn: SELECT * FROM chuyen_nhuong_xe WHERE MaYeuCau = 12"),
            ("db", "sys", "4. Trả về thông tin: Biển số, Người chuyển, Người nhận"),
            ("sys", "db", "5. TRANSACTION: UPDATE phuong_tien & vehicles SET MaCuDan = NguoiNhan"),
            ("sys", "db", "6. UPDATE chuyen_nhuong_xe SET TrangThai = 'DaDuyet', NgayDuyet = NOW()"),
            ("db", "sys", "7. Commit transaction thành công"),
            ("sys", "ui", "8. Phản hồi JSON: {success: true, message: 'Đã chuyển nhượng xe sang chủ sở hữu mới'}"),
            ("ui", "actor", "9. Chuyển trạng thái đơn thành 'Đã Duyệt' & Cập nhật danh mục xe")
        ]
    },
    {
        "id": "uc13_admin_analytics",
        "name": "13. Báo cáo thống kê & Doanh thu",
        "actor": "Quản Trị Viên\n(Admin)",
        "ui_path": "fe/templates/index.html\n(Trang thống kê #reports-page, renderCharts)",
        "sys_path": "be/app.py: GET /api/analytics/revenue\nbe/database.py: get_revenue_stats()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nparking_sessions, statistics",
        "steps": [
            ("actor", "ui", "1. Chọn xem báo cáo doanh thu theo tháng và biểu đồ mật độ 24 giờ"),
            ("ui", "sys", "2. GET /api/analytics/revenue & GET /api/analytics/hourly"),
            ("sys", "db", "3. SELECT DATE(check_out_time), SUM(fee), COUNT(*) FROM parking_sessions WHERE status='Completed' GROUP BY DATE(check_out_time)"),
            ("sys", "db", "4. SELECT HOUR(check_in_time), COUNT(*) FROM parking_sessions GROUP BY HOUR(check_in_time)"),
            ("db", "sys", "5. Trả về tập dữ liệu tổng hợp doanh thu và số lượt xe theo giờ"),
            ("sys", "ui", "6. Phản hồi JSON dữ liệu thống kê phân tích"),
            ("ui", "actor", "7. Vẽ biểu đồ cột doanh thu & Biểu đồ đường lưu lượng giờ cao điểm (Chart.js)")
        ]
    }
]

def build_single_diagram_elem(parent_elem, diag):
    col_x = {
        "actor": 100,
        "ui": 360,
        "sys": 690,
        "db": 1040
    }
    col_w = {
        "actor": 160,
        "ui": 230,
        "sys": 260,
        "db": 240
    }
    top_y = 60
    header_h = 100
    msg_start_y = 200
    msg_step_y = 55

    num_steps = len(diag["steps"])
    lifeline_h = msg_start_y + (num_steps + 1) * msg_step_y
    page_h = max(800, lifeline_h + 100)
    page_w = 1350

    diagram_elem = ET.SubElement(parent_elem, "diagram", attrib={"id": diag["id"], "name": diag["name"]})
    model_elem = ET.SubElement(diagram_elem, "mxGraphModel", attrib={
        "dx": "1422", "dy": "800", "grid": "1", "gridSize": "10",
        "guides": "1", "tooltips": "1", "connect": "1", "arrows": "1",
        "fold": "1", "page": "1", "pageScale": "1",
        "pageWidth": str(page_w), "pageHeight": str(page_h),
        "math": "0", "shadow": "0"
    })
    root = ET.SubElement(model_elem, "root")
    
    ET.SubElement(root, "mxCell", attrib={"id": "0"})
    ET.SubElement(root, "mxCell", attrib={"id": "1", "parent": "0"})

    # Tiêu đề
    title_val = f"<b>3.2. SƠ ĐỒ TUẦN TỰ (SEQUENCE DIAGRAM): {diag['name'].upper()}</b>"
    title_cell = ET.SubElement(root, "mxCell", attrib={
        "id": f"{diag['id']}_title",
        "parent": "1",
        "value": title_val,
        "style": "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=18;fontColor=#1E293B;fontStyle=1;",
        "vertex": "1"
    })
    ET.SubElement(title_cell, "mxGeometry", attrib={"x": "50", "y": "15", "width": "1250", "height": "35", "as": "geometry"})

    # 4 Lifelines đúng chuẩn theo chỉ dẫn bảng đen
    participants = [
        ("actor", f"<b>TÁC NHÂN</b><br/><font color='#1E40AF'>{diag['actor'].replace(chr(10), '<br/>')}</font>", "#DBEAFE", "#1D4ED8"),
        ("ui", f"<b>GIAO DIỆN</b><br/><font color='#B91C1C'><b>[File code]</b></font><br/><i>{diag['ui_path'].replace(chr(10), '<br/>')}</i>", "#FEF3C7", "#D97706"),
        ("sys", f"<b>HỆ THỐNG</b><br/><font color='#B91C1C'><b>[File code / Hàm]</b></font><br/><i>{diag['sys_path'].replace(chr(10), '<br/>')}</i>", "#E0E7FF", "#4338CA"),
        ("db", f"<b>CƠ SỞ DỮ LIỆU</b><br/><font color='#B91C1C'><b>[db / Bảng]</b></font><br/><i>{diag['db_info'].replace(chr(10), '<br/>')}</i>", "#F3E8FF", "#7E22CE")
    ]

    for p_key, p_label, fill_c, stroke_c in participants:
        ll_id = f"{diag['id']}_ll_{p_key}"
        style = (
            f"shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;"
            f"container=1;collapsible=0;recursiveResize=0;outlineConnect=0;size={header_h};"
            f"fillColor={fill_c};strokeColor={stroke_c};strokeWidth=2;fontColor=#0F172A;"
            f"rounded=1;shadow=0;fontSize=11;align=center;"
        )
        ll_cell = ET.SubElement(root, "mxCell", attrib={
            "id": ll_id,
            "parent": "1",
            "value": p_label,
            "style": style,
            "vertex": "1"
        })
        ET.SubElement(ll_cell, "mxGeometry", attrib={"x": str(col_x[p_key]), "y": str(top_y), "width": str(col_w[p_key]), "height": str(lifeline_h), "as": "geometry"})

    # Vẽ Messages
    for idx, (src_key, dst_key, msg_text) in enumerate(diag["steps"]):
        curr_y = msg_start_y + idx * msg_step_y
        msg_id = f"{diag['id']}_msg_{idx+1}"
        
        x1 = col_x[src_key] + col_w[src_key] // 2
        x2 = col_x[dst_key] + col_w[dst_key] // 2

        is_return = ("Trở về" in msg_text or "Trả về" in msg_text or "Phản hồi" in msg_text or "Hiển thị" in msg_text or "Xác nhận" in msg_text) and (x1 > x2)
        is_self = (src_key == dst_key)

        if is_self:
            edge_style = "html=1;align=left;spacingLeft=5;verticalAlign=top;endArrow=block;rounded=0;edgeStyle=orthogonalEdgeStyle;curved=0;strokeColor=#4338CA;strokeWidth=1.5;fontColor=#1E293B;fontSize=11;"
            edge_cell = ET.SubElement(root, "mxCell", attrib={
                "id": msg_id,
                "parent": "1",
                "value": msg_text,
                "style": edge_style,
                "edge": "1"
            })
            geom = ET.SubElement(edge_cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
            geom.set("x", "0")
            geom.set("y", "0")
            
            ET.SubElement(geom, "mxPoint", attrib={"x": str(x1), "y": str(curr_y), "as": "sourcePoint"})
            ET.SubElement(geom, "mxPoint", attrib={"x": str(x1), "y": str(curr_y + 25), "as": "targetPoint"})
            
            array_elem = ET.SubElement(geom, "Array", attrib={"as": "points"})
            ET.SubElement(array_elem, "mxPoint", attrib={"x": str(x1 + 45), "y": str(curr_y)})
            ET.SubElement(array_elem, "mxPoint", attrib={"x": str(x1 + 45), "y": str(curr_y + 25)})
        else:
            if is_return:
                edge_style = "html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;rounded=0;strokeColor=#475569;strokeWidth=1.5;fontColor=#334155;fontSize=11;"
            else:
                edge_style = "html=1;verticalAlign=bottom;endArrow=block;rounded=0;strokeColor=#1E293B;strokeWidth=1.5;fontColor=#0F172A;fontSize=11;"

            edge_cell = ET.SubElement(root, "mxCell", attrib={
                "id": msg_id,
                "parent": "1",
                "value": msg_text,
                "style": edge_style,
                "edge": "1"
            })
            geom = ET.SubElement(edge_cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
            ET.SubElement(geom, "mxPoint", attrib={"x": str(x1), "y": str(curr_y), "as": "sourcePoint"})
            ET.SubElement(geom, "mxPoint", attrib={"x": str(x2), "y": str(curr_y), "as": "targetPoint"})

def generate_drawio_files(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    drawio_sub_dir = os.path.join(out_dir, "drawio")
    os.makedirs(drawio_sub_dir, exist_ok=True)

    # 1. Master file chứa tất cả 13 Use Cases
    master_file = os.path.join(out_dir, "SO_DO_TUAN_TU_HE_THONG.drawio")
    mxfile_master = ET.Element("mxfile", attrib={"host": "app.diagrams.net", "modified": "2026-10-02T08:30:00.000Z", "agent": "Antigravity-CNPM24", "version": "21.6.8", "type": "device"})
    
    for diag in DIAGRAMS:
        build_single_diagram_elem(mxfile_master, diag)
        
        # 2. File riêng cho từng Use Case
        single_file = os.path.join(drawio_sub_dir, f"{diag['id']}.drawio")
        mxfile_single = ET.Element("mxfile", attrib={"host": "app.diagrams.net", "modified": "2026-10-02T08:30:00.000Z", "agent": "Antigravity-CNPM24", "version": "21.6.8", "type": "device"})
        build_single_diagram_elem(mxfile_single, diag)
        t_single = ET.ElementTree(mxfile_single)
        ET.indent(t_single, space="  ", level=0)
        t_single.write(single_file, encoding="utf-8", xml_declaration=True)

    tree_master = ET.ElementTree(mxfile_master)
    ET.indent(tree_master, space="  ", level=0)
    tree_master.write(master_file, encoding="utf-8", xml_declaration=True)

    # 3. Tạo file PlantUML tương ứng
    puml_file = os.path.join(out_dir, "SEQUENCE_DIAGRAMS.puml")
    with open(puml_file, "w", encoding="utf-8") as f:
        f.write("' ====================================================================\n")
        f.write("' SƠ ĐỒ TUẦN TỰ (SEQUENCE DIAGRAMS) - HỆ THỐNG QUẢN LÝ BÃI ĐỖ XE AI\n")
        f.write("' Đúng chuẩn: Tác nhân | Giao diện [File] | Hệ thống [File/Hàm] | CSDL [DB/Bảng]\n")
        f.write("' ====================================================================\n\n")

        for diag in DIAGRAMS:
            f.write(f"@startuml {diag['id']}\n")
            f.write("!theme plain\n")
            f.write(f"title SƠ ĐỒ TUẦN TỰ: {diag['name'].upper()}\n")
            f.write("autonumber\n\n")
            
            clean_actor = diag['actor'].replace('\n', ' ')
            clean_ui = diag['ui_path'].replace('\n', '\\n')
            clean_sys = diag['sys_path'].replace('\n', '\\n')
            clean_db = diag['db_info'].replace('\n', '\\n')

            f.write(f'actor "{clean_actor}" as Actor #DBEAFE\n')
            f.write(f'participant "Giao diện\\n[File code]\\n{clean_ui}" as UI #FEF3C7\n')
            f.write(f'participant "Hệ thống\\n[File code / Hàm]\\n{clean_sys}" as Sys #E0E7FF\n')
            f.write(f'database "Cơ sở dữ liệu\\n[db / Bảng]\\n{clean_db}" as DB #F3E8FF\n\n')

            part_map = {"actor": "Actor", "ui": "UI", "sys": "Sys", "db": "DB"}
            for s_src, s_dst, s_msg in diag["steps"]:
                p_src = part_map[s_src]
                p_dst = part_map[s_dst]
                
                # Check arrow type
                if ("Trở về" in s_msg or "Trả về" in s_msg or "Phản hồi" in s_msg or "Hiển thị" in s_msg or "Xác nhận" in s_msg) and s_src != s_dst and (list(part_map.keys()).index(s_src) > list(part_map.keys()).index(s_dst)):
                    arrow = "-->>"
                else:
                    arrow = "->>"
                
                clean_msg = s_msg.split(". ", 1)[-1]
                f.write(f"{p_src} {arrow} {p_dst}: {clean_msg}\n")

            f.write("\n@enduml\n\n")

    print(f"Master Draw.io file: {master_file}")
    print(f"Single Draw.io files: {drawio_sub_dir}")
    print(f"PlantUML file: {puml_file}")

if __name__ == "__main__":
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    generate_drawio_files(docs_dir)
