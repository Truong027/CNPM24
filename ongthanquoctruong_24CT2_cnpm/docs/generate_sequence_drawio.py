#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script sinh file Draw.io (.drawio XML) và PlantUML (.puml) cho toàn bộ
Sơ đồ Tuần tự (Sequence Diagrams) của hệ thống Quản lý Bãi đỗ xe thông minh AI (CNPM24).

Được cập nhật theo đúng yêu cầu mới nhất của giảng viên & người dùng:
  1. Tác nhân (Actor): Thể hiện bằng hình con người (UML Actor stick figure) với tên tác nhân ghi ở dưới.
  2. Khung kiểm tra điều kiện if/else: Đặt trong frame UML dạng "alt", có vạch phân cách đứt nét giữa luồng Hợp lệ và luồng [else: Thất bại / Cảnh báo].
  3. Phân nhóm chi tiết theo từng Tác nhân:
     - Nhóm 1: Tác nhân Cư Dân (Resident) -> UC01 đến UC07
     - Nhóm 2: Tác nhân Nhân Viên Bảo Vệ (Security Guard / Operator) -> UC08 đến UC10
     - Nhóm 3: Tác nhân Quản Trị Viên (Admin) -> UC11 đến UC13
  4. Tuân thủ 100% quy chuẩn 4 Cột:
     - Cột 1: Tác nhân (Hình người + Tên ở dưới)
     - Cột 2: Giao diện [File code]
     - Cột 3: Hệ thống [File code / Hàm]
     - Cột 4: Cơ sở dữ liệu [db / Bảng]
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
    # =========================================================================
    # NHÓM 1: TÁC NHÂN CƯ DÂN (RESIDENT)
    # =========================================================================
    {
        "id": "uc01_resident_register",
        "actor_group": "Cư Dân",
        "name": "[Cư Dân] UC01 - Đăng ký tài khoản cư dân",
        "actor_role": "Cư Dân",
        "actor_sub": "Resident",
        "ui_path": "fe/templates/register.html\n(hoặc fe/templates/login.html#register)",
        "sys_path": "be/app.py: register()\nbe/database.py: register_resident_user()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\napp_users, cu_dan",
        "initial_steps": [
            ("actor", "ui", "1. Nhập Họ tên, SĐT, Căn hộ, Mật khẩu & Click 'Đăng ký'"),
            ("ui", "sys", "2. POST /register (username, password, phone, apartment)"),
            ("sys", "db", "3. SELECT * FROM app_users WHERE username = %s OR phone = %s"),
            ("db", "sys", "4. Trả về kết quả kiểm tra trùng lặp tài khoản")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra tính hợp lệ của tài khoản & SĐT]",
            "happy_cond": "Username & SĐT chưa từng đăng ký (Hợp lệ)",
            "happy_steps": [
                ("sys", "sys", "5a. Băm mật khẩu an toàn PBKDF2/SHA-256 (generate_password_hash)"),
                ("sys", "db", "6a. INSERT INTO app_users & cu_dan (MaCuDan, HoTen, TenDangNhap, Role='Resident')"),
                ("db", "sys", "7a. Xác nhận ghi bản ghi mới thành công (Affected rows = 1)"),
                ("sys", "ui", "8a. Phản hồi HTTP 200 {success: true, message: 'Đăng ký thành công'}"),
                ("ui", "actor", "9a. Hiển thị thông báo thành công & Chuyển hướng sang trang Đăng nhập")
            ],
            "else_cond": "Username hoặc SĐT đã tồn tại / Dữ liệu không hợp lệ",
            "else_steps": [
                ("sys", "ui", "5b. Phản hồi HTTP 400 {success: false, message: 'Tài khoản hoặc SĐT đã tồn tại'}"),
                ("ui", "actor", "6b. Hiển thị Toast cảnh báo lỗi màu đỏ & Yêu cầu nhập lại thông tin")
            ]
        }
    },
    {
        "id": "uc02_resident_login",
        "actor_group": "Cư Dân",
        "name": "[Cư Dân] UC02 - Đăng nhập tài khoản cư dân",
        "actor_role": "Cư Dân",
        "actor_sub": "Resident",
        "ui_path": "fe/templates/login.html\n(Form #loginForm)",
        "sys_path": "be/app.py: login()\nbe/database.py: check_user_credentials()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\napp_users, cu_dan",
        "initial_steps": [
            ("actor", "ui", "1. Nhập tên đăng nhập, mật khẩu & Bấm 'Đăng nhập'"),
            ("ui", "sys", "2. POST /login (username, password)"),
            ("sys", "db", "3. SELECT id, username, password_hash, role, status FROM app_users WHERE username = %s"),
            ("db", "sys", "4. Trả về thông tin người dùng và mã băm password_hash")
        ],
        "alt_frame": {
            "title": "alt [Đối soát mật khẩu & Phân quyền truy cập]",
            "happy_cond": "Mật khẩu chính xác & status == 'active' & role == 'Resident'",
            "happy_steps": [
                ("sys", "sys", "5a. Khởi tạo session['user'] = {id, role: 'Resident', username}"),
                ("sys", "ui", "6a. Phản hồi HTTP 200 {success: true, role: 'Resident', redirect: '/resident-dashboard'}"),
                ("ui", "actor", "7a. Điều hướng vào Cổng thông tin Cư dân (Resident Dashboard)")
            ],
            "else_cond": "Sai mật khẩu hoặc Tài khoản bị vô hiệu hóa (status != 'active')",
            "else_steps": [
                ("sys", "ui", "5b. Phản hồi HTTP 401 {success: false, message: 'Sai tên đăng nhập hoặc mật khẩu'}"),
                ("ui", "actor", "6b. Hiển thị thông báo lỗi 'Đăng nhập thất bại' & Xóa trống mật khẩu")
            ]
        }
    },
    {
        "id": "uc03_resident_register_vehicle",
        "actor_group": "Cư Dân",
        "name": "[Cư Dân] UC03 - Đăng ký xe & Chọn ô đỗ Cinema",
        "actor_role": "Cư Dân",
        "actor_sub": "Resident",
        "ui_path": "fe/templates/resident_dashboard.html\n(Modal #registerVehicleModal, #cinemaModal)",
        "sys_path": "be/app.py: POST /api/resident/register_vehicle\nbe/database.py: register_vehicle_with_slot()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nbai_do, vehicles, phuong_tien",
        "initial_steps": [
            ("actor", "ui", "1. Nhập biển số, hiệu xe & Click chọn vị trí ô đỗ Cinema (VD: B1-A01)"),
            ("ui", "sys", "2. POST /api/resident/register_vehicle (plate: '30H-999.88', slot_id: 'B1-A01', months: 3)"),
            ("sys", "db", "3. Khóa dòng kiểm tra: SELECT TrangThai FROM bai_do WHERE MaViTri = %s FOR UPDATE"),
            ("db", "sys", "4. Trả về trạng thái hiện tại của ô đỗ")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra tính khả dụng của vị trí ô đỗ]",
            "happy_cond": "Ô đỗ còn TRỐNG (TrangThai == 'Trong')",
            "happy_steps": [
                ("sys", "db", "5a. UPDATE bai_do SET TrangThai = 'DaDat', BienSoXe = %s WHERE MaViTri = %s"),
                ("sys", "db", "6a. INSERT INTO vehicles & phuong_tien (BienSoXe, MaCuDan, ViTriDo, NgayHetHan)"),
                ("db", "sys", "7a. Xác nhận lưu xe và đặt chỗ ô đỗ thành công"),
                ("sys", "ui", "8a. Phản hồi HTTP 200 {success: true, slot_id: 'B1-A01', plate: '30H-999.88'}"),
                ("ui", "actor", "9a. Đổi màu ô ghế Cinema sang Cyan (Xe của bạn) & Cập nhật thẻ xe 3D")
            ],
            "else_cond": "Vị trí ô đỗ đã có người khác đặt trước (TrangThai == 'DaDat')",
            "else_steps": [
                ("sys", "ui", "5b. Phản hồi HTTP 409 {success: false, message: 'Vị trí đỗ vừa được đặt, vui lòng chọn ô khác'}"),
                ("ui", "actor", "6b. Tô đỏ ô đỗ và hiển thị thông báo yêu cầu chọn vị trí khác trên sơ đồ Cinema")
            ]
        }
    },
    {
        "id": "uc04_resident_change_slot",
        "actor_group": "Cư Dân",
        "name": "[Cư Dân] UC04 - Đổi vị trí đỗ xe Cinema",
        "actor_role": "Cư Dân",
        "actor_sub": "Resident",
        "ui_path": "fe/templates/resident_dashboard.html\n(Modal #changeSlotModal, renderCinemaSeats)",
        "sys_path": "be/app.py: POST /api/parking/change_slot\nbe/database.py: change_vehicle_parking_slot()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nbai_do, vehicles, phuong_tien",
        "initial_steps": [
            ("actor", "ui", "1. Chọn xe cần đổi & Click chọn vị trí ô trống mới (VD: B1-B05)"),
            ("ui", "sys", "2. POST /api/parking/change_slot (plate: '30H-999.88', new_slot: 'B1-B05')"),
            ("sys", "db", "3. Tra cứu vị trí mới: SELECT TrangThai FROM bai_do WHERE MaViTri = 'B1-B05'"),
            ("db", "sys", "4. Trả về trạng thái của vị trí mới")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra vị trí ô đỗ mới]",
            "happy_cond": "Vị trí mới còn TRỐNG (TrangThai == 'Trong')",
            "happy_steps": [
                ("sys", "db", "5a. TRANSACTION: UPDATE bai_do SET TrangThai = 'Trong', BienSoXe = NULL (Ô cũ)"),
                ("sys", "db", "6a. UPDATE bai_do SET TrangThai = 'DaDat', BienSoXe = %s (Ô mới B1-B05)"),
                ("sys", "db", "7a. UPDATE phuong_tien & vehicles SET ViTriDo = 'B1-B05' WHERE BienSoXe = %s"),
                ("db", "sys", "8a. Commit transaction thành công"),
                ("sys", "ui", "9a. Phản hồi HTTP 200 {success: true, new_slot: 'B1-B05'}"),
                ("ui", "actor", "10a. Render lại sơ đồ bãi đỗ Cinema & Hiển thị thông báo đổi vị trí thành công")
            ],
            "else_cond": "Vị trí mới đã bị xe khác chiếm chỗ",
            "else_steps": [
                ("sys", "db", "5b. ROLLBACK TRANSACTION"),
                ("sys", "ui", "6b. Phản hồi HTTP 400 {success: false, message: 'Vị trí mới không khả dụng'}"),
                ("ui", "actor", "7b. Báo lỗi 'Không thể đổi sang vị trí này', giữ nguyên vị trí cũ")
            ]
        }
    },
    {
        "id": "uc05_resident_renew_pass",
        "actor_group": "Cư Dân",
        "name": "[Cư Dân] UC05 - Gia hạn vé tháng cư dân",
        "actor_role": "Cư Dân",
        "actor_sub": "Resident",
        "ui_path": "fe/templates/resident_dashboard.html\n(Modal #renewTicketModal)",
        "sys_path": "be/app.py: POST /api/resident/renew_ticket\nbe/database.py: renew_monthly_ticket()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nvehicles, phuong_tien, lich_su_thanh_toan",
        "initial_steps": [
            ("actor", "ui", "1. Chọn gói gia hạn (1, 3 hoặc 6 tháng) & Bấm 'Xác nhận gia hạn'"),
            ("ui", "sys", "2. POST /api/resident/renew_ticket (plate: '30H-999.88', months: 3)"),
            ("sys", "db", "3. SELECT NgayHetHan FROM phuong_tien WHERE BienSoXe = %s"),
            ("db", "sys", "4. Trả về ngày hết hạn hiện tại của phương tiện")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra thông tin phương tiện & Gói gia hạn]",
            "happy_cond": "Tìm thấy phương tiện hợp lệ & Gói gia hạn đúng quy định",
            "happy_steps": [
                ("sys", "sys", "5a. Tính thời hạn mới: new_expiry = max(current_expiry, today) + 3 months"),
                ("sys", "db", "6a. UPDATE phuong_tien & vehicles SET NgayHetHan = %s WHERE BienSoXe = %s"),
                ("sys", "db", "7a. INSERT INTO lich_su_thanh_toan (BienSoXe, SoTien, LoaiGiaoDich='GiaHanVeThang')"),
                ("db", "sys", "8a. Xác nhận cập nhật CSDL thành công"),
                ("sys", "ui", "9a. Phản hồi HTTP 200 {success: true, new_expiry: '2026-12-31'}"),
                ("ui", "actor", "10a. Cập nhật nhãn hạn mới trên thẻ xe 3D và hiển thị badge 'Còn Hạn'")
            ],
            "else_cond": "Biển số xe không tồn tại hoặc lỗi giao dịch",
            "else_steps": [
                ("sys", "ui", "5b. Phản hồi HTTP 404 {success: false, message: 'Không tìm thấy xe hoặc giao dịch bị hủy'}"),
                ("ui", "actor", "6b. Hiển thị thông báo thất bại & Giữ nguyên thời hạn cũ")
            ]
        }
    },
    {
        "id": "uc06_resident_transfer_request",
        "actor_group": "Cư Dân",
        "name": "[Cư Dân] UC06 - Yêu cầu chuyển nhượng xe & ô đỗ",
        "actor_role": "Cư Dân",
        "actor_sub": "Resident",
        "ui_path": "fe/templates/resident_dashboard.html\n(Modal #transferVehicleModal)",
        "sys_path": "be/app.py: POST /api/resident/transfer_vehicle\nbe/database.py: create_vehicle_transfer_request()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nchuyen_nhuong_xe, cu_dan, vehicles",
        "initial_steps": [
            ("actor", "ui", "1. Nhập SĐT người nhận, lý do chuyển nhượng & Bấm 'Gửi yêu cầu'"),
            ("ui", "sys", "2. POST /api/resident/transfer_vehicle (plate, target_phone, reason)"),
            ("sys", "db", "3. SELECT MaCuDan, HoTen FROM cu_dan WHERE SoDienThoai = %s"),
            ("db", "sys", "4. Trả về thông tin cư dân nhận theo số điện thoại")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra tính hợp lệ của người nhận chuyển nhượng]",
            "happy_cond": "Tìm thấy cư dân nhận hợp lệ & Khác chủ xe hiện tại",
            "happy_steps": [
                ("sys", "db", "5a. INSERT INTO chuyen_nhuong_xe (BienSoXe, NguoiChuyen, NguoiNhan, TrangThai='ChoDuyet')"),
                ("db", "sys", "6a. Xác nhận tạo đơn chuyển nhượng thành công (MaYeuCau = 12)"),
                ("sys", "ui", "7a. Phản hồi HTTP 200 {success: true, request_id: 12, status: 'ChoDuyet'}"),
                ("ui", "actor", "8a. Hiển thị thông báo 'Đã gửi đơn chuyển nhượng, vui lòng chờ Admin phê duyệt'")
            ],
            "else_cond": "SĐT không tồn tại hoặc Cố tình chuyển nhượng cho chính mình",
            "else_steps": [
                ("sys", "ui", "5b. Phản hồi HTTP 400 {success: false, message: 'Người nhận không phải cư dân tòa nhà'}"),
                ("ui", "actor", "6b. Báo lỗi 'Không tìm thấy cư dân nhận, vui lòng kiểm tra lại SĐT'")
            ]
        }
    },
    {
        "id": "uc07_resident_history",
        "actor_group": "Cư Dân",
        "name": "[Cư Dân] UC07 - Tra cứu lịch sử xe vào/ra",
        "actor_role": "Cư Dân",
        "actor_sub": "Resident",
        "ui_path": "fe/templates/resident_dashboard.html\n(Bảng lịch sử #historySection)",
        "sys_path": "be/app.py: GET /api/resident/history\nbe/database.py: get_resident_vehicle_history()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nparking_sessions, lich_su_ra_vao",
        "initial_steps": [
            ("actor", "ui", "1. Chọn biển số xe cần xem lịch sử & Khoảng thời gian"),
            ("ui", "sys", "2. GET /api/resident/history?plate=30H-999.88"),
            ("sys", "db", "3. SELECT * FROM parking_sessions WHERE plate_text = %s ORDER BY check_in_time DESC"),
            ("db", "sys", "4. Trả về danh sách các phiên gửi xe tương ứng")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra dữ liệu lịch sử]",
            "happy_cond": "Có dữ liệu lịch sử vào/ra trong hệ thống",
            "happy_steps": [
                ("sys", "ui", "5a. Phản hồi HTTP 200 JSON danh sách phiên: Giờ vào, Giờ ra, Phí thu, Ảnh snapshot"),
                ("ui", "actor", "6a. Hiển thị bảng lịch sử trực quan kèm nút bấm phóng to xem ảnh camera")
            ],
            "else_cond": "Chưa có lượt gửi xe nào trong khoảng thời gian đã chọn",
            "else_steps": [
                ("sys", "ui", "5b. Phản hồi HTTP 200 {sessions: [], message: 'Không có dữ liệu'}"),
                ("ui", "actor", "6b. Hiển thị thông báo trạng thái trống 'Chưa phát sinh lượt gửi xe nào'")
            ]
        }
    },

    # =========================================================================
    # NHÓM 2: TÁC NHÂN NHÂN VIÊN BẢO VỆ (SECURITY GUARD / OPERATOR)
    # =========================================================================
    {
        "id": "uc08_guard_auto_checkin",
        "actor_group": "Bảo Vệ",
        "name": "[Bảo Vệ] UC08 - Nhận diện AI & Tự động Check-in xe vào",
        "actor_role": "Nhân Viên Bảo Vệ",
        "actor_sub": "Security Guard",
        "ui_path": "fe/templates/index.html\n(Tab #recognition-page, Live Stream)",
        "sys_path": "be/app.py: gen_frames() & detect_plates_from_frame()\nbe/database.py: process_parking_transaction()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nparking_sessions, lich_su_ra_vao, detections",
        "initial_steps": [
            ("actor", "ui", "1. Xe tiến vào làn cổng, Camera gửi luồng video frames tới màn hình bàn trực"),
            ("ui", "sys", "2. Stream khung hình video trực tiếp tới backend AI xử lý"),
            ("sys", "sys", "3. YOLOv8 cắt vùng biển số -> CRNN nhận dạng ký tự (VD: '51G-123.45')"),
            ("sys", "db", "4. Tra cứu phiên đỗ: SELECT id FROM parking_sessions WHERE plate_text = %s AND status = 'Parked'"),
            ("db", "sys", "5. Trả về kết quả kiểm tra phiên đỗ hiện tại của xe")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra tính hợp lệ của lượt xe vào]",
            "happy_cond": "Không có phiên trùng lặp & Biển số nhận diện rõ ràng (Xe vào hợp lệ)",
            "happy_steps": [
                ("sys", "db", "6a. INSERT INTO parking_sessions (plate_text, check_in_time=NOW(), status='Parked', gate_in='Cổng Vào')"),
                ("sys", "db", "7a. Lưu bản ghi ảnh chụp vào detections & lich_su_ra_vao"),
                ("db", "sys", "8a. Xác nhận tạo phiên gửi xe mới thành công"),
                ("sys", "sys", "9a. Gửi tín hiệu điều khiển mở Barrier cổng vào (barrier_state = 'OPEN')"),
                ("sys", "ui", "10a. Đẩy sự kiện Live Event WebSocket: 'Xe vào thành công' kèm ảnh chụp biển số"),
                ("ui", "actor", "11a. Cần Barrier nâng lên, màn hình LED hiển thị: 'Kính chào quý khách: 51G-123.45'")
            ],
            "else_cond": "Xe đang có phiên mở chưa checkout hoặc Biển số mờ không nhận diện được",
            "else_steps": [
                ("sys", "ui", "6b. Đẩy cảnh báo an ninh về Bàn trực bảo vệ: 'Biển số trùng lặp / Nhận diện mờ'"),
                ("ui", "actor", "7b. Giữ nguyên Barrier đóng & Bật cửa sổ yêu cầu Bảo vệ kiểm tra, nhập biển số thủ công")
            ]
        }
    },
    {
        "id": "uc09_guard_checkout_verification",
        "actor_group": "Bảo Vệ",
        "name": "[Bảo Vệ] UC09 - Đối chiếu xe ra & Cảnh báo an ninh Blacklist",
        "actor_role": "Nhân Viên Bảo Vệ",
        "actor_sub": "Security Guard",
        "ui_path": "fe/templates/index.html\n(Bàn trực #guard-station-page, checkGuardLiveEvent)",
        "sys_path": "be/app.py: GET /api/guard/verification/<plate>\nbe/database.py: get_guard_verification_info()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nvehicles, parking_sessions, bai_do",
        "initial_steps": [
            ("actor", "ui", "1. Xe ra đến cổng, Camera đọc biển số hoặc Bảo vệ chọn xe kiểm tra"),
            ("ui", "sys", "2. GET /api/guard/verification/51G-123.45"),
            ("sys", "db", "3. Truy vấn phiên đỗ: SELECT * FROM parking_sessions WHERE plate_text = %s AND status = 'Parked'"),
            ("sys", "db", "4. Truy vấn phân loại xe: SELECT group_type, monthly_ticket_expiry FROM vehicles WHERE plate_text = %s"),
            ("db", "sys", "5. Trả về dữ liệu phiên vào, ảnh snapshot vào, nhóm đối tượng, hạn vé tháng")
        ],
        "alt_frame": {
            "title": "alt [Phân loại đối tượng xe & Đối soát an ninh ra]",
            "happy_cond": "Trường hợp 1: Xe Cư dân vé tháng còn hiệu lực (monthly_ticket_expiry >= NOW)",
            "happy_steps": [
                ("sys", "sys", "6a. Xác nhận miễn phí gửi xe (fee = 0đ) theo chính sách vé tháng cư dân"),
                ("sys", "ui", "7a. Phản hồi HTTP 200 {is_resident: true, fee: 0, status: 'Valid'}"),
                ("ui", "actor", "8a. Hiển thị badge xanh 'VÉ THÁNG HỢP LỆ' & So sánh khớp ảnh Vào - Ra")
            ],
            "else_cond": "Trường hợp 2: Xe thuộc Danh Sách Đen (group_type == 'Blacklist' / Cảnh báo trộm cắp)",
            "else_steps": [
                ("sys", "sys", "6b. Bật cờ cảnh báo an ninh khẩn cấp (security_alert = True, lock_barrier = True)"),
                ("sys", "ui", "7b. Phản hồi HTTP 200 {is_blacklist: true, alert_level: 'HIGH', fee: 0}"),
                ("ui", "actor", "8b. Khóa nút mở barrier, nhấp nháy đèn đỏ CẢNH BÁO XE GIAN LẬN/TRỘM CẮP & Báo động")
            ]
        }
    },
    {
        "id": "uc10_guard_collect_fee_barrier",
        "actor_group": "Bảo Vệ",
        "name": "[Bảo Vệ] UC10 - Thu phí gửi xe & Kích hoạt Barrier cổng ra",
        "actor_role": "Nhân Viên Bảo Vệ",
        "actor_sub": "Security Guard",
        "ui_path": "fe/templates/index.html\n(#guardFeeBox, #guardConfirmActionBtn)",
        "sys_path": "be/app.py: POST /api/guard/collect_fee\nbe/database.py: complete_parking_session()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nparking_sessions, lich_su_ra_vao, hoa_don",
        "initial_steps": [
            ("actor", "ui", "1. Khách thanh toán tiền mặt/quét mã VietQR, Bảo vệ bấm 'Xác Nhận Thu Phí & Mở Cổng'"),
            ("ui", "sys", "2. POST /api/guard/collect_fee (session_id: 105, amount: 20000, method: 'Cash')")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra trạng thái thanh toán & Điều khiển Barrier]",
            "happy_cond": "Xác nhận thu phí thành công (Tiền mặt hoặc Chuyển khoản QR)",
            "happy_steps": [
                ("sys", "db", "3a. UPDATE parking_sessions SET status = 'Completed', check_out_time = NOW(), fee = 20000"),
                ("sys", "db", "4a. INSERT INTO hoa_don (MaPhien, SoTien, HinhThucThanhToan, NgayLap)"),
                ("db", "sys", "5a. Xác nhận ghi nhận doanh thu và kết thúc phiên gửi xe"),
                ("sys", "sys", "6a. Gửi lệnh điều khiển phần cứng mở cần Barrier cổng ra (Barrier_Out = 'OPEN')"),
                ("sys", "ui", "7a. Phản hồi HTTP 200 {success: true, invoice_code: 'HD-20261002-01', barrier: 'OPEN'}"),
                ("ui", "actor", "8a. In hóa đơn/phiếu xuất bãi, nâng cần Barrier cho xe ra & Cập nhật số chỗ trống")
            ],
            "else_cond": "Chưa nhận được thanh toán hoặc Có tranh chấp cước phí",
            "else_steps": [
                ("sys", "ui", "3b. Phản hồi HTTP 400 {success: false, message: 'Giao dịch chưa hoàn tất'}"),
                ("ui", "actor", "4b. Giữ nguyên Barrier đóng, tiếp tục hiển thị chờ thanh toán")
            ]
        }
    },

    # =========================================================================
    # NHÓM 3: TÁC NHÂN QUẢN TRỊ VIÊN (ADMIN)
    # =========================================================================
    {
        "id": "uc11_admin_user_mgmt",
        "actor_group": "Admin",
        "name": "[Admin] UC11 - Quản lý tài khoản người dùng & Phân quyền",
        "actor_role": "Quản Trị Viên",
        "actor_sub": "System Admin",
        "ui_path": "fe/templates/index.html\n(Trang quản lý #users-page, Modal #editUserModal)",
        "sys_path": "be/app.py: POST /api/admin/users/update\nbe/database.py: admin_update_user_info()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\napp_users, cu_dan, nhan_vien",
        "initial_steps": [
            ("actor", "ui", "1. Chọn tài khoản cần chỉnh sửa, cập nhật quyền hạn/trạng thái & Bấm 'Lưu thay đổi'"),
            ("ui", "sys", "2. POST /api/admin/users/update (user_id: 5, role: 'Operator', status: 'active')"),
            ("sys", "db", "3. Tra cứu quyền hạn tài khoản mục tiêu: SELECT role FROM app_users WHERE id = %s"),
            ("db", "sys", "4. Trả về thông tin vai trò hiện tại của tài khoản")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra thẩm quyền chỉnh sửa]",
            "happy_cond": "Thao tác hợp lệ (Không tự khóa tài khoản Root Super Admin)",
            "happy_steps": [
                ("sys", "db", "5a. UPDATE app_users SET role = %s, status = %s WHERE id = %s"),
                ("sys", "db", "6a. Đồng bộ cập nhật bảng cu_dan / nhan_vien tương ứng"),
                ("db", "sys", "7a. Xác nhận cập nhật thông tin thành công (Affected rows = 1)"),
                ("sys", "ui", "8a. Phản hồi HTTP 200 {success: true, message: 'Cập nhật tài khoản thành công'}"),
                ("ui", "actor", "9a. Tải lại danh sách người dùng & Hiển thị badge quyền hạn mới")
            ],
            "else_cond": "Thao tác không hợp lệ (Cố tình vô hiệu hóa tài khoản Quản trị cao nhất)",
            "else_steps": [
                ("sys", "ui", "5b. Phản hồi HTTP 403 {success: false, message: 'Không thể vô hiệu hóa tài khoản Super Admin'}"),
                ("ui", "actor", "6b. Bật cảnh báo lỗi màu đỏ 'Từ chối thao tác bảo vệ an toàn hệ thống'")
            ]
        }
    },
    {
        "id": "uc12_admin_approve_transfer",
        "actor_group": "Admin",
        "name": "[Admin] UC12 - Phê duyệt đơn chuyển nhượng xe & ô đỗ",
        "actor_role": "Quản Trị Viên",
        "actor_sub": "System Admin",
        "ui_path": "fe/templates/index.html\n(Trang chuyển nhượng #transfers-page)",
        "sys_path": "be/app.py: POST /api/admin/transfer_requests/<id>/action\nbe/database.py: process_transfer_request_action()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nchuyen_nhuong_xe, vehicles, phuong_tien",
        "initial_steps": [
            ("actor", "ui", "1. Xem chi tiết đơn chuyển nhượng đang chờ duyệt & Bấm nút quyết định"),
            ("ui", "sys", "2. POST /api/admin/transfer_requests/12/action (action: 'approve' / 'reject')"),
            ("sys", "db", "3. Lấy thông tin đơn: SELECT * FROM chuyen_nhuong_xe WHERE MaYeuCau = 12"),
            ("db", "sys", "4. Trả về thông tin: Biển số xe, Cư dân chuyển, Cư dân nhận")
        ],
        "alt_frame": {
            "title": "alt [Quyết định xử lý của Quản Trị Viên]",
            "happy_cond": "Admin bấm 'Phê Duyệt' (action == 'approve')",
            "happy_steps": [
                ("sys", "db", "5a. TRANSACTION: UPDATE phuong_tien & vehicles SET MaCuDan = NguoiNhan WHERE BienSoXe = %s"),
                ("sys", "db", "6a. UPDATE chuyen_nhuong_xe SET TrangThai = 'DaDuyet', NgayDuyet = NOW()"),
                ("db", "sys", "7a. Commit transaction chuyển nhượng thành công"),
                ("sys", "ui", "8a. Phản hồi HTTP 200 {success: true, message: 'Đã chuyển nhượng xe sang chủ sở hữu mới'}"),
                ("ui", "actor", "9a. Đổi huy hiệu đơn sang màu xanh 'ĐÃ DUYỆT' & Cập nhật danh mục xe")
            ],
            "else_cond": "Admin bấm 'Từ Chối' (action == 'reject')",
            "else_steps": [
                ("sys", "db", "5b. UPDATE chuyen_nhuong_xe SET TrangThai = 'TuChoi', LyDo = 'Thông tin không chính xác'"),
                ("db", "sys", "6b. Xác nhận cập nhật trạng thái từ chối đơn"),
                ("sys", "ui", "7b. Phản hồi HTTP 200 {success: true, message: 'Đã từ chối đơn chuyển nhượng'}"),
                ("ui", "actor", "8b. Đổi huy hiệu đơn sang màu đỏ 'ĐÃ TỪ CHỐI'")
            ]
        }
    },
    {
        "id": "uc13_admin_analytics",
        "actor_group": "Admin",
        "name": "[Admin] UC13 - Báo cáo thống kê & Biểu đồ doanh thu",
        "actor_role": "Quản Trị Viên",
        "actor_sub": "System Admin",
        "ui_path": "fe/templates/index.html\n(Trang thống kê #reports-page, renderCharts)",
        "sys_path": "be/app.py: GET /api/analytics/revenue\nbe/database.py: get_revenue_stats()",
        "db_info": "HTTT_QuanLyBaiXe_AI /\nparking_sessions, statistics",
        "initial_steps": [
            ("actor", "ui", "1. Chọn khoảng thời gian xem báo cáo doanh thu & Bấm 'Xem phân tích'"),
            ("ui", "sys", "2. GET /api/analytics/revenue & GET /api/analytics/hourly"),
            ("sys", "db", "3. SELECT DATE(check_out_time), SUM(fee), COUNT(*) FROM parking_sessions WHERE status='Completed' GROUP BY DATE(check_out_time)"),
            ("sys", "db", "4. SELECT HOUR(check_in_time), COUNT(*) FROM parking_sessions GROUP BY HOUR(check_in_time)"),
            ("db", "sys", "5. Trả về tập dữ liệu tổng hợp doanh thu và số lượt xe theo giờ")
        ],
        "alt_frame": {
            "title": "alt [Kiểm tra dữ liệu phát sinh]",
            "happy_cond": "Có phát sinh lượt xe & Doanh thu trong kỳ báo cáo",
            "happy_steps": [
                ("sys", "ui", "6a. Phản hồi HTTP 200 JSON dữ liệu biểu đồ {dates: [...], revenues: [...], hourly: [...]}"),
                ("ui", "actor", "7a. Render biểu đồ cột doanh thu & Biểu đồ đường lưu lượng giờ cao điểm (Chart.js)")
            ],
            "else_cond": "Kỳ báo cáo chưa có lượt xe nào phát sinh",
            "else_steps": [
                ("sys", "ui", "6b. Phản hồi HTTP 200 JSON tập rỗng {dates: [], revenues: [], total: 0}"),
                ("ui", "actor", "7b. Hiển thị thông báo 'Chưa có dữ liệu thống kê trong khoảng thời gian đã chọn'")
            ]
        }
    }
]

def build_single_diagram_elem(parent_elem, diag):
    col_x = {
        "actor": 140,
        "ui": 380,
        "sys": 710,
        "db": 1050
    }
    col_w = {
        "actor": 60,
        "ui": 240,
        "sys": 260,
        "db": 240
    }
    actor_center_x = col_x["actor"] + col_w["actor"] // 2  # 170

    top_y = 60
    header_h = 100
    msg_start_y = 200
    msg_step_y = 50

    num_initial = len(diag["initial_steps"])
    num_happy = len(diag["alt_frame"]["happy_steps"])
    num_else = len(diag["alt_frame"]["else_steps"])

    # Tính toán tọa độ Y
    # 1. Initial steps
    y_cursor = msg_start_y
    initial_step_ys = []
    for _ in diag["initial_steps"]:
        initial_step_ys.append(y_cursor)
        y_cursor += msg_step_y

    # 2. Alt frame start
    alt_start_y = y_cursor + 10
    y_cursor += 45  # chừa chỗ cho tiêu đề alt

    happy_step_ys = []
    for _ in diag["alt_frame"]["happy_steps"]:
        happy_step_ys.append(y_cursor)
        y_cursor += msg_step_y

    alt_divider_y = y_cursor + 15
    y_cursor += 45  # chừa chỗ cho nhãn else

    else_step_ys = []
    for _ in diag["alt_frame"]["else_steps"]:
        else_step_ys.append(y_cursor)
        y_cursor += msg_step_y

    alt_end_y = y_cursor + 20
    lifeline_bottom_y = alt_end_y + 40
    page_h = max(900, lifeline_bottom_y + 80)
    page_w = 1380

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

    # Tiêu đề biểu đồ
    title_val = f"<b>3.2. SƠ ĐỒ TUẦN TỰ (SEQUENCE DIAGRAM): {diag['name'].upper()}</b>"
    title_cell = ET.SubElement(root, "mxCell", attrib={
        "id": f"{diag['id']}_title",
        "parent": "1",
        "value": title_val,
        "style": "text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize=17;fontColor=#1E293B;fontStyle=1;",
        "vertex": "1"
    })
    ET.SubElement(title_cell, "mxGeometry", attrib={"x": "50", "y": "15", "width": "1280", "height": "35", "as": "geometry"})

    # -------------------------------------------------------------
    # 1. CỘT 1: TÁC NHÂN (ACTOR) - HÌNH CON NGƯỜI & TÊN Ở DƯỚI
    # -------------------------------------------------------------
    actor_label = f"<b>TÁC NHÂN</b><br/><font color='#1E40AF'><b>{diag['actor_role']}</b></font><br/><font color='#64748B'>({diag['actor_sub']})</font>"
    actor_cell = ET.SubElement(root, "mxCell", attrib={
        "id": f"{diag['id']}_actor_icon",
        "parent": "1",
        "value": actor_label,
        "style": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;fillColor=#DBEAFE;strokeColor=#1D4ED8;strokeWidth=2;fontSize=11;fontColor=#0F172A;align=center;",
        "vertex": "1"
    })
    ET.SubElement(actor_cell, "mxGeometry", attrib={"x": str(col_x["actor"]), "y": "60", "width": str(col_w["actor"]), "height": "65", "as": "geometry"})

    # Đường Lifeline đứt nét chạy dọc từ dưới hình người xuống đáy
    actor_line_cell = ET.SubElement(root, "mxCell", attrib={
        "id": f"{diag['id']}_ll_actor",
        "parent": "1",
        "value": "",
        "style": "endArrow=none;dashed=1;html=1;strokeWidth=1.5;strokeColor=#1D4ED8;",
        "edge": "1"
    })
    actor_line_geom = ET.SubElement(actor_line_cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
    ET.SubElement(actor_line_geom, "mxPoint", attrib={"x": str(actor_center_x), "y": "165", "as": "sourcePoint"})
    ET.SubElement(actor_line_geom, "mxPoint", attrib={"x": str(actor_center_x), "y": str(lifeline_bottom_y), "as": "targetPoint"})

    # -------------------------------------------------------------
    # 2, 3, 4. CÁC CỘT: GIAO DIỆN, HỆ THỐNG, CƠ SỞ DỮ LIỆU
    # -------------------------------------------------------------
    participants = [
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
        ll_height = lifeline_bottom_y - top_y
        ET.SubElement(ll_cell, "mxGeometry", attrib={"x": str(col_x[p_key]), "y": str(top_y), "width": str(col_w[p_key]), "height": str(ll_height), "as": "geometry"})

    # Hàm trợ giúp vẽ Message
    def draw_message(idx_str, src_key, dst_key, msg_text, curr_y, is_error=False):
        msg_id = f"{diag['id']}_msg_{idx_str}"
        x1 = actor_center_x if src_key == "actor" else (col_x[src_key] + col_w[src_key] // 2)
        x2 = actor_center_x if dst_key == "actor" else (col_x[dst_key] + col_w[dst_key] // 2)

        is_return = ("Trở về" in msg_text or "Trả về" in msg_text or "Phản hồi" in msg_text or "Hiển thị" in msg_text or "Xác nhận" in msg_text or "Báo lỗi" in msg_text) and (x1 > x2)
        is_self = (src_key == dst_key)

        if is_self:
            edge_style = "html=1;align=left;spacingLeft=5;verticalAlign=top;endArrow=block;rounded=0;edgeStyle=orthogonalEdgeStyle;curved=0;strokeColor=#4338CA;strokeWidth=1.5;fontColor=#1E293B;fontSize=10;"
            edge_cell = ET.SubElement(root, "mxCell", attrib={
                "id": msg_id,
                "parent": "1",
                "value": msg_text,
                "style": edge_style,
                "edge": "1"
            })
            geom = ET.SubElement(edge_cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
            ET.SubElement(geom, "mxPoint", attrib={"x": str(x1), "y": str(curr_y), "as": "sourcePoint"})
            ET.SubElement(geom, "mxPoint", attrib={"x": str(x1), "y": str(curr_y + 20), "as": "targetPoint"})
            
            array_elem = ET.SubElement(geom, "Array", attrib={"as": "points"})
            ET.SubElement(array_elem, "mxPoint", attrib={"x": str(x1 + 45), "y": str(curr_y)})
            ET.SubElement(array_elem, "mxPoint", attrib={"x": str(x1 + 45), "y": str(curr_y + 20)})
        else:
            if is_return:
                stroke_c = "#DC2626" if is_error else "#475569"
                font_c = "#991B1B" if is_error else "#334155"
                edge_style = f"html=1;verticalAlign=bottom;endArrow=open;dashed=1;endSize=8;rounded=0;strokeColor={stroke_c};strokeWidth=1.5;fontColor={font_c};fontSize=10;"
            else:
                stroke_c = "#B91C1C" if is_error else "#1E293B"
                font_c = "#7F1D1D" if is_error else "#0F172A"
                edge_style = f"html=1;verticalAlign=bottom;endArrow=block;rounded=0;strokeColor={stroke_c};strokeWidth=1.5;fontColor={font_c};fontSize=10;"

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

    # Vẽ các tin nhắn khởi tạo ban đầu (trước frame alt)
    for idx, (src_k, dst_k, m_txt) in enumerate(diag["initial_steps"]):
        draw_message(f"init_{idx+1}", src_k, dst_k, m_txt, initial_step_ys[idx])

    # -------------------------------------------------------------
    # KHUNG ALT (UML ALTERNATIVE COMBINED FRAGMENT)
    # -------------------------------------------------------------
    frame_x = 90
    frame_w = 1200
    frame_h = alt_end_y - alt_start_y

    alt_frame_val = f"<b>alt</b> [{diag['alt_frame']['happy_cond']}]"
    alt_style = (
        "shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;recursiveResize=0;"
        "container=0;collapsible=0;width=340;height=26;dashed=1;dashPattern=8 4;"
        "strokeColor=#64748B;fillColor=#F8FAFC;strokeWidth=1.5;align=left;"
        "spacingLeft=10;verticalAlign=top;fontStyle=0;fontSize=11;fontColor=#0F172A;"
    )
    frame_cell = ET.SubElement(root, "mxCell", attrib={
        "id": f"{diag['id']}_alt_frame",
        "parent": "1",
        "value": alt_frame_val,
        "style": alt_style,
        "vertex": "1"
    })
    ET.SubElement(frame_cell, "mxGeometry", attrib={"x": str(frame_x), "y": str(alt_start_y), "width": str(frame_w), "height": str(frame_h), "as": "geometry"})

    # Vẽ các tin nhắn nhánh Happy (Thành công / Hợp lệ)
    for idx, (src_k, dst_k, m_txt) in enumerate(diag["alt_frame"]["happy_steps"]):
        draw_message(f"happy_{idx+1}", src_k, dst_k, m_txt, happy_step_ys[idx], is_error=False)

    # Vạch phân cách nét đứt [else]
    else_label = f"<b>[else: {diag['alt_frame']['else_cond']}]</b>"
    divider_cell = ET.SubElement(root, "mxCell", attrib={
        "id": f"{diag['id']}_alt_divider",
        "parent": "1",
        "value": else_label,
        "style": "html=1;strokeWidth=1.5;strokeColor=#94A3B8;dashed=1;dashPattern=6 4;endArrow=none;align=left;verticalAlign=bottom;spacingLeft=15;fontColor=#B91C1C;fontSize=11;fontStyle=0;",
        "edge": "1"
    })
    div_geom = ET.SubElement(divider_cell, "mxGeometry", attrib={"relative": "1", "as": "geometry"})
    ET.SubElement(div_geom, "mxPoint", attrib={"x": str(frame_x), "y": str(alt_divider_y), "as": "sourcePoint"})
    ET.SubElement(div_geom, "mxPoint", attrib={"x": str(frame_x + frame_w), "y": str(alt_divider_y), "as": "targetPoint"})

    # Vẽ các tin nhắn nhánh Else (Thất bại / Cảnh báo lỗi)
    for idx, (src_k, dst_k, m_txt) in enumerate(diag["alt_frame"]["else_steps"]):
        draw_message(f"else_{idx+1}", src_k, dst_k, m_txt, else_step_ys[idx], is_error=True)

def generate_drawio_files(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    drawio_sub_dir = os.path.join(out_dir, "drawio")
    os.makedirs(drawio_sub_dir, exist_ok=True)

    # 1. Master file chứa tất cả 13 Use Cases
    master_file = os.path.join(out_dir, "SO_DO_TUAN_TU_HE_THONG.drawio")
    mxfile_master = ET.Element("mxfile", attrib={"host": "app.diagrams.net", "modified": "2026-10-02T08:35:00.000Z", "agent": "Antigravity-CNPM24", "version": "21.6.8", "type": "device"})
    
    for diag in DIAGRAMS:
        build_single_diagram_elem(mxfile_master, diag)
        
        # 2. File riêng cho từng Use Case
        single_file = os.path.join(drawio_sub_dir, f"{diag['id']}.drawio")
        mxfile_single = ET.Element("mxfile", attrib={"host": "app.diagrams.net", "modified": "2026-10-02T08:35:00.000Z", "agent": "Antigravity-CNPM24", "version": "21.6.8", "type": "device"})
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
        f.write("' Phân loại theo Tác nhân: Cư Dân, Bảo Vệ, Quản Trị Viên\n")
        f.write("' Chuẩn hóa: Tác nhân (Hình người) | Giao diện [File] | Hệ thống [File/Hàm] | CSDL [DB/Bảng]\n")
        f.write("' Khung điều kiện rẽ nhánh: alt / else\n")
        f.write("' ====================================================================\n\n")

        current_group = None
        for diag in DIAGRAMS:
            if diag["actor_group"] != current_group:
                current_group = diag["actor_group"]
                f.write(f"\n' --------------------------------------------------------------------\n")
                f.write(f"' NHÓM TÁC NHÂN: {current_group.upper()}\n")
                f.write(f"' --------------------------------------------------------------------\n\n")

            f.write(f"@startuml {diag['id']}\n")
            f.write("!theme plain\n")
            f.write(f"title SƠ ĐỒ TUẦN TỰ: {diag['name'].upper()}\n")
            f.write("autonumber\n\n")
            
            clean_actor = f"{diag['actor_role']}\\n({diag['actor_sub']})"
            clean_ui = diag['ui_path'].replace('\n', '\\n')
            clean_sys = diag['sys_path'].replace('\n', '\\n')
            clean_db = diag['db_info'].replace('\n', '\\n')

            f.write(f'actor "{clean_actor}" as Actor #DBEAFE\n')
            f.write(f'participant "Giao diện\\n[File code]\\n{clean_ui}" as UI #FEF3C7\n')
            f.write(f'participant "Hệ thống\\n[File code / Hàm]\\n{clean_sys}" as Sys #E0E7FF\n')
            f.write(f'database "Cơ sở dữ liệu\\n[db / Bảng]\\n{clean_db}" as DB #F3E8FF\n\n')

            part_map = {"actor": "Actor", "ui": "UI", "sys": "Sys", "db": "DB"}

            def puml_arrow(s_src, s_dst, s_msg):
                if ("Trở về" in s_msg or "Trả về" in s_msg or "Phản hồi" in s_msg or "Hiển thị" in s_msg or "Xác nhận" in s_msg or "Báo lỗi" in s_msg) and s_src != s_dst and (list(part_map.keys()).index(s_src) > list(part_map.keys()).index(s_dst)):
                    return "-->>"
                return "->>"

            for s_src, s_dst, s_msg in diag["initial_steps"]:
                p_src = part_map[s_src]
                p_dst = part_map[s_dst]
                arrow = puml_arrow(s_src, s_dst, s_msg)
                clean_msg = s_msg.split(". ", 1)[-1]
                f.write(f"{p_src} {arrow} {p_dst}: {clean_msg}\n")

            f.write(f"\nalt {diag['alt_frame']['happy_cond']}\n")
            for s_src, s_dst, s_msg in diag["alt_frame"]["happy_steps"]:
                p_src = part_map[s_src]
                p_dst = part_map[s_dst]
                arrow = puml_arrow(s_src, s_dst, s_msg)
                clean_msg = s_msg.split(". ", 1)[-1]
                f.write(f"    {p_src} {arrow} {p_dst}: {clean_msg}\n")

            f.write(f"else {diag['alt_frame']['else_cond']}\n")
            for s_src, s_dst, s_msg in diag["alt_frame"]["else_steps"]:
                p_src = part_map[s_src]
                p_dst = part_map[s_dst]
                arrow = puml_arrow(s_src, s_dst, s_msg)
                clean_msg = s_msg.split(". ", 1)[-1]
                f.write(f"    {p_src} {arrow} {p_dst}: {clean_msg}\n")

            f.write("end\n\n")
            f.write("@enduml\n\n")

    print(f"Master Draw.io file: {master_file}")
    print(f"Single Draw.io files: {drawio_sub_dir}")
    print(f"PlantUML file: {puml_file}")

if __name__ == "__main__":
    docs_dir = os.path.dirname(os.path.abspath(__file__))
    generate_drawio_files(docs_dir)
