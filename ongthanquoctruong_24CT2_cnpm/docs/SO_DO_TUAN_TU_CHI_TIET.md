# BÁO CÁO PHÂN TÍCH YÊU CẦU: SƠ ĐỒ TUẦN TỰ (SEQUENCE DIAGRAMS)
## HỆ THỐNG NHẬN DIỆN BIỂN SỐ & QUẢN LÝ BÃI ĐỖ XE THÔNG MINH AI (SMART PARKING)

- **Môn học**: Công nghệ phần mềm (CNPM24)
- **Lớp**: 24CT2
- **Sinh viên thực hiện**: Ông Thân Quốc Trường
- **Trường**: Đại học Kiến trúc Đà Nẵng (DAU) - Khoa Công nghệ thông tin

---

## 📌 QUY CHUẨN THIẾT KẾ THEO YÊU CẦU CỦA GIẢNG VIÊN

Theo đúng hướng dẫn phân tích yêu cầu tại buổi học, mỗi sơ đồ tuần tự được thiết kế với **4 thực thể tham gia (Lifelines)**:

| Cột (Lifeline) | Ý Nghĩa | Quy Chuẩn Ghi Chú Theo Bài Giảng | Ánh Xạ Đến Mã Nguồn Dự Án |
| :--- | :--- | :--- | :--- |
| **1. Tác nhân** | Người dùng hoặc thiết bị tương tác | `Khách hàng / Tác nhân` | Cư Dân, Nhân Viên Bảo Vệ, Quản Trị Viên, Camera AI |
| **2. Giao diện** | Màn hình, trang web, form hoặc modal | `File code` (Đường dẫn file giao diện) | Đường dẫn mẫu template: `fe/templates/login.html`, `fe/templates/resident_dashboard.html`... |
| **3. Hệ thống** | Web Server điều phối logic & xử lý nghiệp vụ | `File code / Hàm` (Đường dẫn code & Tên hàm) | Đường dẫn backend & API: `be/app.py: login()`, `be/database.py: check_user_credentials()`... |
| **4. Cơ sở dữ liệu** | Nơi lưu trữ, truy vấn và duy trì tính toàn vẹn | `db / Bảng` (Tên CSDL / Danh sách bảng) | CSDL: `HTTT_QuanLyBaiXe_AI` / Các bảng: `cu_dan`, `vehicles`, `bai_do`, `parking_sessions`... |

---

## 📂 DANH MỤC FILE DRAW.IO ĐÃ TẠO

Các file Draw.io đã được sinh sẵn sàng để mở trực tiếp trên [app.diagrams.net](https://app.diagrams.net):

1. **File Tổng Hợp (Tất cả 13 Use Cases trong 1 file - chuyển tab bên dưới)**:
   - 📄 [`docs/SO_DO_TUAN_TU_HE_THONG.drawio`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/SO_DO_TUAN_TU_HE_THONG.drawio)
2. **Thư Mục File Từng Use Case Riêng Biệt**:
   - 📁 [`docs/drawio/`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/drawio)
     - `uc01_register.drawio` (Đăng ký tài khoản cư dân)
     - `uc02_login.drawio` (Đăng nhập hệ thống)
     - `uc03_register_vehicle_cinema.drawio` (Đăng ký xe & Chọn ô đỗ Cinema)
     - `uc04_change_slot.drawio` (Đổi vị trí đỗ xe Cinema)
     - `uc05_renew_pass.drawio` (Gia hạn vé tháng cư dân)
     - `uc06_transfer_request.drawio` (Yêu cầu chuyển nhượng xe)
     - `uc07_parking_history.drawio` (Tra cứu lịch sử vào/ra)
     - `uc08_auto_checkin.drawio` (Nhận diện AI & Tự động Check-in xe vào)
     - `uc09_checkout_verification.drawio` (Đối chiếu xe ra & Cảnh báo Blacklist)
     - `uc10_collect_fee_barrier.drawio` (Thu phí & Mở Barrier cổng ra)
     - `uc11_admin_user_mgmt.drawio` (Quản lý tài khoản người dùng)
     - `uc12_admin_approve_transfer.drawio` (Phê duyệt đơn chuyển nhượng)
     - `uc13_admin_analytics.drawio` (Báo cáo thống kê & Doanh thu)
3. **Mã Nguồn PlantUML**:
   - 📄 [`docs/SEQUENCE_DIAGRAMS.puml`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/SEQUENCE_DIAGRAMS.puml)

---

## 📊 BẢNG TỔNG HỢP ÁNH XẠ CODE CHI TIẾT (13 SƠ ĐỒ)

| STT | Tên Use Case | Tác Nhân | Giao Diện `[File code]` | Hệ Thống `[File code / Hàm]` | Cơ Sở Dữ Liệu `[db / Bảng]` |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **01** | Đăng ký tài khoản cư dân | Cư Dân | `fe/templates/register.html`<br/>*(hoặc `login.html#register`)* | `be/app.py: register()`<br/>`be/database.py: register_resident_user()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan` |
| **02** | Đăng nhập hệ thống | Người Dùng<br/>*(Admin/Bảo vệ/Cư dân)* | `fe/templates/login.html`<br/>*(Form `#loginForm`)* | `be/app.py: login()`<br/>`be/database.py: check_user_credentials()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan, nhan_vien` |
| **03** | Đăng ký xe & Chọn ô đỗ Cinema | Cư Dân | `fe/templates/resident_dashboard.html`<br/>*(Modal `#registerVehicleModal`, `#cinemaModal`)* | `be/app.py: POST /api/resident/register_vehicle`<br/>`be/database.py: register_vehicle_with_slot()` | `HTTT_QuanLyBaiXe_AI /`<br/>`bai_do, vehicles, phuong_tien` |
| **04** | Đổi vị trí đỗ xe Cinema | Cư Dân | `fe/templates/resident_dashboard.html`<br/>*(Modal `#changeSlotModal`, `renderCinemaSeats`)* | `be/app.py: POST /api/parking/change_slot`<br/>`be/database.py: change_vehicle_parking_slot()` | `HTTT_QuanLyBaiXe_AI /`<br/>`bai_do, vehicles, phuong_tien` |
| **05** | Gia hạn vé tháng cư dân | Cư Dân | `fe/templates/resident_dashboard.html`<br/>*(Modal `#renewTicketModal`)* | `be/app.py: POST /api/resident/renew_ticket`<br/>`be/database.py: renew_monthly_ticket()` | `HTTT_QuanLyBaiXe_AI /`<br/>`vehicles, phuong_tien` |
| **06** | Yêu cầu chuyển nhượng xe | Cư Dân | `fe/templates/resident_dashboard.html`<br/>*(Modal `#transferVehicleModal`)* | `be/app.py: POST /api/resident/transfer_vehicle`<br/>`be/database.py: create_vehicle_transfer_request()` | `HTTT_QuanLyBaiXe_AI /`<br/>`chuyen_nhuong_xe, cu_dan, vehicles` |
| **07** | Tra cứu lịch sử xe vào/ra | Cư Dân | `fe/templates/resident_dashboard.html`<br/>*(Bảng lịch sử `#historySection`)* | `be/app.py: GET /api/resident/history`<br/>`be/database.py: get_resident_vehicle_history()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, lich_su_ra_vao` |
| **08** | Nhận diện AI & Tự động Check-in | Tài xế / Camera Cổng | `fe/templates/index.html`<br/>*(Tab `#recognition-page`, Live MJPEG)* | `be/app.py: gen_frames(), detect_plates_from_frame()`<br/>`be/database.py: process_parking_transaction()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, lich_su_ra_vao, detections` |
| **09** | Đối chiếu xe ra & Cảnh báo Blacklist | Nhân Viên Bảo Vệ | `fe/templates/index.html`<br/>*(Bàn trực `#guard-station-page`, `checkGuardLiveEvent`)* | `be/app.py: GET /api/guard/verification/<plate>`<br/>`be/database.py: get_guard_verification_info()` | `HTTT_QuanLyBaiXe_AI /`<br/>`vehicles, parking_sessions, bai_do` |
| **10** | Thu phí & Mở Barrier cổng ra | Nhân Viên Bảo Vệ | `fe/templates/index.html`<br/>*(Hộp tính phí `#guardFeeBox`, nút `#guardConfirmActionBtn`)* | `be/app.py: POST /api/guard/collect_fee`<br/>`be/database.py: complete_parking_session()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, lich_su_ra_vao` |
| **11** | Quản lý tài khoản người dùng | Quản Trị Viên | `fe/templates/index.html`<br/>*(Trang quản lý `#users-page`, Modal `#editUserModal`)* | `be/app.py: POST /api/admin/users/update`<br/>`be/database.py: admin_update_user_info()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan, nhan_vien` |
| **12** | Phê duyệt đơn chuyển nhượng | Quản Trị Viên | `fe/templates/index.html`<br/>*(Trang chuyển nhượng `#transfers-page`)* | `be/app.py: POST /api/admin/transfer_requests/<id>/action`<br/>`be/database.py: process_transfer_request_action()` | `HTTT_QuanLyBaiXe_AI /`<br/>`chuyen_nhuong_xe, vehicles, phuong_tien, cu_dan` |
| **13** | Báo cáo thống kê & Doanh thu | Quản Trị Viên | `fe/templates/index.html`<br/>*(Trang thống kê `#reports-page`, `renderCharts`)* | `be/app.py: GET /api/analytics/revenue`<br/>`be/database.py: get_revenue_stats()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, statistics` |

---

## 📝 CHI TIẾT CÁC BƯỚC TUẦN TỰ TỪNG USE CASE

### 1. Đăng Ký Tài Khoản Cư Dân
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/register.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: register()<br/>be/database.py: register_resident_user()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / app_users, cu_dan

    Resident->>UI: 1. Nhập họ tên, SĐT, căn hộ, mật khẩu & Bấm 'Đăng ký'
    UI->>Sys: 2. POST /register (username, password, phone, apartment)
    Sys->>DB: 3. SELECT * FROM app_users WHERE username = %s OR phone = %s
    DB-->>Sys: 4. Trả về kết quả kiểm tra (Chưa tồn tại)
    Sys->>Sys: 5. Băm mật khẩu an toàn PBKDF2/SHA-256 (generate_password_hash)
    Sys->>DB: 6. INSERT INTO app_users & cu_dan (MaCuDan, HoTen, TenDangNhap...)
    DB-->>Sys: 7. Xác nhận ghi bản ghi thành công (Affected rows = 1)
    Sys-->>UI: 8. Phản hồi JSON: {success: true, message: 'Đăng ký thành công'}
    UI-->>Resident: 9. Hiển thị Toast thông báo thành công & Chuyển sang Đăng nhập
```

### 2. Đăng Nhập Hệ Thống
```mermaid
sequenceDiagram
    autonumber
    actor User as Người Dùng (Admin/Bảo vệ/Cư dân)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/login.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: login()<br/>be/database.py: check_user_credentials()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / app_users, cu_dan, nhan_vien

    User->>UI: 1. Nhập tên đăng nhập, mật khẩu & Bấm 'Đăng nhập'
    UI->>Sys: 2. POST /login (username, password)
    Sys->>DB: 3. SELECT * FROM app_users WHERE username = %s AND status = 'active'
    DB-->>Sys: 4. Trả về thông tin user & password_hash
    Sys->>Sys: 5. Đối soát mật khẩu (check_password_hash) & Khởi tạo session['user']
    Sys-->>UI: 6. Phản hồi JSON: {success: true, role: 'Resident'/'Admin'/'Operator'}
    UI-->>User: 7. Điều hướng vào trang làm việc tương ứng (/ hoặc /resident-dashboard)
```

### 3. Đăng Ký Xe & Chọn Ô Đỗ Cinema
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/resident_dashboard.html<br/>(#registerVehicleModal, #cinemaModal)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/resident/register_vehicle<br/>be/database.py: register_vehicle_with_slot()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / bai_do, vehicles, phuong_tien

    Resident->>UI: 1. Nhập biển số, màu xe & Chọn vị trí ô đỗ (VD: B1-A01) trên sơ đồ
    UI->>Sys: 2. POST /api/resident/register_vehicle (plate, slot_id, months)
    Sys->>DB: 3. Kiểm tra ô đỗ: SELECT TrangThai FROM bai_do WHERE MaViTri = %s FOR UPDATE
    DB-->>Sys: 4. Trả về trạng thái ô đỗ (TrangThai = 'Trong')
    Sys->>DB: 5. UPDATE bai_do SET TrangThai = 'DaDat', BienSoXe = %s
    Sys->>DB: 6. INSERT INTO vehicles & phuong_tien (BienSoXe, MaCuDan, ViTriDo, NgayHetHan)
    DB-->>Sys: 7. Trả về kết quả ghi dữ liệu thành công
    Sys-->>UI: 8. Phản hồi JSON: {success: true, slot: 'B1-A01', plate: '30H-999.88'}
    UI-->>Resident: 9. Cập nhật thẻ xe 3D lên màn hình & Đổi màu ô đỗ thành Cyan (Xe của bạn)
```

### 4. Đổi Vị Trí Đỗ Xe Cinema
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/resident_dashboard.html<br/>(#changeSlotModal, renderCinemaSeats)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/parking/change_slot<br/>be/database.py: change_vehicle_parking_slot()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / bai_do, vehicles, phuong_tien

    Resident->>UI: 1. Chọn xe cần đổi & Click chọn vị trí ô trống mới (VD: B1-B05)
    UI->>Sys: 2. POST /api/parking/change_slot (plate: '30H-999.88', new_slot: 'B1-B05')
    Sys->>DB: 3. Kiểm tra ô mới: SELECT TrangThai FROM bai_do WHERE MaViTri = 'B1-B05'
    DB-->>Sys: 4. Xác nhận ô mới còn 'Trong'
    Sys->>DB: 5. TRANSACTION: Giải phóng ô cũ (TrangThai = 'Trong')
    Sys->>DB: 6. Đặt chỗ ô mới (TrangThai = 'DaDat') & Cập nhật ViTriDo trong phuong_tien
    DB-->>Sys: 7. Commit transaction thành công
    Sys-->>UI: 8. Phản hồi JSON: {success: true, message: 'Đổi vị trí đỗ thành công'}
    UI-->>Resident: 9. Render lại sơ đồ bãi đỗ Cinema & Hiển thị thông báo thành công
```

### 5. Gia Hạn Vé Tháng Cư Dân
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/resident_dashboard.html<br/>(#renewTicketModal)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/resident/renew_ticket<br/>be/database.py: renew_monthly_ticket()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / vehicles, phuong_tien

    Resident->>UI: 1. Chọn gói gia hạn (1, 3 hoặc 6 tháng) & Bấm 'Xác nhận gia hạn'
    UI->>Sys: 2. POST /api/resident/renew_ticket (plate: '30H-999.88', months: 3)
    Sys->>DB: 3. SELECT NgayHetHan FROM phuong_tien WHERE BienSoXe = %s
    DB-->>Sys: 4. Trả về ngày hết hạn hiện tại
    Sys->>Sys: 5. Cộng dồn thời hạn mới (new_expiry = max(current_expiry, today) + months)
    Sys->>DB: 6. UPDATE phuong_tien & vehicles SET NgayHetHan = %s WHERE BienSoXe = %s
    DB-->>Sys: 7. Xác nhận cập nhật CSDL thành công
    Sys-->>UI: 8. Phản hồi JSON: {success: true, new_expiry: '2026-12-31'}
    UI-->>Resident: 9. Cập nhật nhãn hạn vé tháng trên thẻ xe 3D và hiển thị badge 'Còn Hạn'
```

### 6. Yêu Cầu Chuyển Nhượng Xe
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/resident_dashboard.html<br/>(#transferVehicleModal)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/resident/transfer_vehicle<br/>be/database.py: create_vehicle_transfer_request()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / chuyen_nhuong_xe, cu_dan, vehicles

    Resident->>UI: 1. Nhập SĐT người nhận, căn hộ mới, lý do & Bấm 'Gửi yêu cầu'
    UI->>Sys: 2. POST /api/resident/transfer_vehicle (plate, target_phone, reason)
    Sys->>DB: 3. SELECT MaCuDan FROM cu_dan WHERE SoDienThoai = %s
    DB-->>Sys: 4. Trả về thông tin cư dân nhận hợp lệ
    Sys->>DB: 5. INSERT INTO chuyen_nhuong_xe (BienSoXe, NguoiChuyen, NguoiNhan, TrangThai)
    DB-->>Sys: 6. Tạo bản ghi đơn chuyển nhượng mới với TrangThai = 'ChoDuyet'
    Sys-->>UI: 7. Phản hồi JSON: {success: true, request_id: 12, status: 'ChoDuyet'}
    UI-->>Resident: 8. Hiển thị thông báo 'Đã gửi yêu cầu đến Quản trị viên phê duyệt'
```

### 7. Tra Cứu Lịch Sử Vào/Ra
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/resident_dashboard.html<br/>(#historySection)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: GET /api/resident/history<br/>be/database.py: get_resident_vehicle_history()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / parking_sessions, lich_su_ra_vao

    Resident->>UI: 1. Chọn biển số xe cần tra cứu & Khoảng ngày tra cứu
    UI->>Sys: 2. GET /api/resident/history?plate=30H-999.88
    Sys->>DB: 3. SELECT * FROM parking_sessions WHERE plate_text = %s ORDER BY check_in_time DESC
    DB-->>Sys: 4. Trả về danh sách phiên: Giờ vào, Giờ ra, Phí thu, Trạng thái, Ảnh chụp
    Sys-->>UI: 5. Phản hồi danh sách phiên gửi xe dưới dạng JSON
    UI-->>Resident: 6. Render bảng lịch sử trực quan kèm ảnh chụp snapshot vào-ra
```

### 8. Nhận Diện AI & Tự Động Check-In Xe Vào
```mermaid
sequenceDiagram
    autonumber
    actor Driver as Tài xế / Camera Cổng Vào
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html<br/>(#recognition-page, Live MJPEG)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: gen_frames(), detect_plates_from_frame()<br/>be/database.py: process_parking_transaction()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / parking_sessions, lich_su_ra_vao, detections

    Driver->>UI: 1. Xe tiến vào làn cổng vào, camera ghi nhận luồng video (Frames)
    UI->>Sys: 2. Stream video MJPEG tới backend (Camera Loop gen_frames)
    Sys->>Sys: 3. YOLOv8 phát hiện bounding box biển số -> CRNN đọc chuỗi ký tự (VD: '51G-123.45')
    Sys->>DB: 4. Tra cứu xe đang đỗ: SELECT id FROM parking_sessions WHERE plate_text = %s AND status = 'Parked'
    DB-->>Sys: 5. Không có phiên mở -> Xe đang vào mới
    Sys->>DB: 6. INSERT INTO parking_sessions (plate_text, check_in_time, status='Parked', gate_in='Cổng Vào')
    Sys->>DB: 7. INSERT INTO lich_su_ra_vao & detections (Lưu lịch sử & độ tin cậy AI)
    DB-->>Sys: 8. Xác nhận tạo phiên gửi xe thành công
    Sys-->>UI: 9. Đẩy thông báo Live Event 'Xe vào thành công' lên Bàn trực bảo vệ
    UI-->>Driver: 10. Mở barrier tự động & Hiển thị biển số trên bảng LED cổng vào
```

### 9. Đối Chiếu Xe Ra & Cảnh Báo Blacklist
```mermaid
sequenceDiagram
    autonumber
    actor Guard as Nhân Viên Bảo Vệ
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html<br/>(#guard-station-page, checkGuardLiveEvent)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: GET /api/guard/verification/<plate><br/>be/database.py: get_guard_verification_info()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / vehicles, parking_sessions, bai_do

    Guard->>UI: 1. Camera cổng ra phát hiện xe hoặc Bảo vệ click chọn xe chuẩn bị ra
    UI->>Sys: 2. GET /api/guard/verification/51G-123.45
    Sys->>DB: 3. Truy vấn phiên đỗ: SELECT * FROM parking_sessions WHERE plate_text = %s AND status = 'Parked'
    Sys->>DB: 4. Truy vấn loại xe: SELECT group_type, monthly_ticket_expiry FROM vehicles WHERE plate_text = %s
    DB-->>Sys: 5. Trả về thông tin phiên vào, ảnh snapshot vào, nhóm xe, hạn vé tháng
    Sys->>Sys: 6. Tính thời gian đỗ, tính cước phí (Vé tháng = 0đ, Vãng lai = theo block giờ)
    Sys->>Sys: 7. Kiểm tra Blacklist: Nếu group_type = 'Blacklist' -> Bật cờ cảnh báo an ninh
    Sys-->>UI: 8. Phản hồi JSON: {verification_data, fee: 0, is_blacklist: false}
    UI-->>Guard: 9. Hiển thị song song 2 ảnh [Ảnh Vào] vs [Ảnh Ra Thực Tế] & Hộp tính phí
```

### 10. Thu Phí & Kích Hoạt Barrier Cổng Ra
```mermaid
sequenceDiagram
    autonumber
    actor Guard as Nhân Viên Bảo Vệ
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html<br/>(#guardFeeBox, #guardConfirmActionBtn)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/guard/collect_fee<br/>be/database.py: complete_parking_session()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / parking_sessions, lich_su_ra_vao

    Guard->>UI: 1. Bảo vệ xác nhận thu tiền mặt/QR và bấm 'Xác Nhận Thu Phí & Mở Barrier'
    UI->>Sys: 2. POST /api/guard/collect_fee (session_id: 105, amount: 20000, method: 'Cash')
    Sys->>DB: 3. UPDATE parking_sessions SET status = 'Completed', check_out_time = NOW(), fee = %s
    Sys->>DB: 4. UPDATE lich_su_ra_vao SET ThoiGianRa = NOW(), TrangThai = 'DaThanhToan'
    DB-->>Sys: 5. Trả về kết quả cập nhật thành công
    Sys->>Sys: 6. Kích hoạt tín hiệu mở Barrier (barrier_state = 'OPEN')
    Sys-->>UI: 7. Phản hồi JSON: {success: true, invoice_code: 'HD-20261002-01', barrier: 'OPEN'}
    UI-->>Guard: 8. In hóa đơn điện tử, bật thông báo 'Cho xe qua cổng' & Cổng Barrier nâng lên
```

### 11. Quản Lý Tài Khoản Người Dùng (Admin)
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Quản Trị Viên
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html<br/>(Trang quản lý #users-page, Modal #editUserModal)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/admin/users/update<br/>be/database.py: admin_update_user_info()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / app_users, cu_dan, nhan_vien

    Admin->>UI: 1. Chọn tài khoản cần sửa, cập nhật quyền hạn/khóa tài khoản & Bấm 'Lưu'
    UI->>Sys: 2. POST /api/admin/users/update (user_id: 5, role: 'Operator', status: 'active')
    Sys->>DB: 3. UPDATE app_users SET role = %s, status = %s WHERE id = %s
    Sys->>DB: 4. Đồng bộ cập nhật bảng cu_dan / nhan_vien tương ứng
    DB-->>Sys: 5. Xác nhận cập nhật thông tin thành công
    Sys-->>UI: 6. Phản hồi JSON: {success: true, message: 'Cập nhật tài khoản thành công'}
    UI-->>Admin: 7. Tải lại danh sách tài khoản & Hiển thị badge quyền hạn mới
```

### 12. Phê Duyệt Đơn Chuyển Nhượng Xe (Admin)
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Quản Trị Viên
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html<br/>(Trang chuyển nhượng #transfers-page)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/admin/transfer_requests/<id>/action<br/>be/database.py: process_transfer_request_action()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / chuyen_nhuong_xe, vehicles, phuong_tien, cu_dan

    Admin->>UI: 1. Xem thông tin đơn chuyển nhượng đang chờ & Bấm nút 'Phê Duyệt'
    UI->>Sys: 2. POST /api/admin/transfer_requests/12/action (action: 'approve')
    Sys->>DB: 3. Lấy thông tin đơn: SELECT * FROM chuyen_nhuong_xe WHERE MaYeuCau = 12
    DB-->>Sys: 4. Trả về thông tin: Biển số, Người chuyển, Người nhận
    Sys->>DB: 5. TRANSACTION: UPDATE phuong_tien & vehicles SET MaCuDan = NguoiNhan
    Sys->>DB: 6. UPDATE chuyen_nhuong_xe SET TrangThai = 'DaDuyet', NgayDuyet = NOW()
    DB-->>Sys: 7. Commit transaction thành công
    Sys-->>UI: 8. Phản hồi JSON: {success: true, message: 'Đã chuyển nhượng xe sang chủ sở hữu mới'}
    UI-->>Admin: 9. Chuyển trạng thái đơn thành 'Đã Duyệt' & Cập nhật danh mục xe
```

### 13. Báo Cáo Thống Kê & Doanh Thu (Admin)
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Quản Trị Viên
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html<br/>(Trang thống kê #reports-page, renderCharts)
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: GET /api/analytics/revenue<br/>be/database.py: get_revenue_stats()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / parking_sessions, statistics

    Admin->>UI: 1. Chọn xem báo cáo doanh thu theo tháng và biểu đồ mật độ 24 giờ
    UI->>Sys: 2. GET /api/analytics/revenue & GET /api/analytics/hourly
    Sys->>DB: 3. SELECT DATE(check_out_time), SUM(fee), COUNT(*) FROM parking_sessions WHERE status='Completed' GROUP BY DATE(check_out_time)
    Sys->>DB: 4. SELECT HOUR(check_in_time), COUNT(*) FROM parking_sessions GROUP BY HOUR(check_in_time)
    DB-->>Sys: 5. Trả về tập dữ liệu tổng hợp doanh thu và số lượt xe theo giờ
    Sys-->>UI: 6. Phản hồi JSON dữ liệu thống kê phân tích
    UI-->>Admin: 7. Vẽ biểu đồ cột doanh thu & Biểu đồ đường lưu lượng giờ cao điểm (Chart.js)
```

---

## 🎯 CÁCH MỞ VÀ SỬ DỤNG TRÊN DRAW.IO

1. Truy cập trình duyệt web: 👉 **[https://app.diagrams.net](https://app.diagrams.net)** (hoặc dùng ứng dụng Draw.io Desktop).
2. Chọn **Open Existing Diagram** (Mở biểu đồ đã có).
3. Duyệt và chọn file:
   - File tổng thể 13 tabs: [`docs/SO_DO_TUAN_TU_HE_THONG.drawio`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/SO_DO_TUAN_TU_HE_THONG.drawio)
   - Hoặc các file con trong thư mục: [`docs/drawio/`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/drawio)
4. Bạn có thể xuất sang **PNG**, **PDF**, **SVG** hoặc chèn trực tiếp vào Slide PowerPoint / Word báo cáo học phần.
