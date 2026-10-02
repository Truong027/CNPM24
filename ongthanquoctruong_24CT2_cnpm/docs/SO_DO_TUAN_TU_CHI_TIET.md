# BÁO CÁO PHÂN TÍCH YÊU CẦU: SƠ ĐỒ TUẦN TỰ (SEQUENCE DIAGRAMS)
## HỆ THỐNG NHẬN DIỆN BIỂN SỐ & QUẢN LÝ BÃI ĐỖ XE THÔNG MINH AI (SMART PARKING)

- **Môn học**: Công nghệ phần mềm (CNPM24)
- **Lớp**: 24CT2
- **Sinh viên thực hiện**: Ông Thân Quốc Trường
- **Trường**: Đại học Kiến trúc Đà Nẵng (DAU) - Khoa Công nghệ thông tin

---

## 📌 QUY CHUẨN THIẾT KẾ THEO YÊU CẦU MỚI CỦA GIẢNG VIÊN

Toàn bộ sơ đồ tuần tự được thiết kế tuân thủ 100% hướng dẫn bài giảng trên lớp và quy chuẩn UML chuẩn hóa:

| Cột (Lifeline) | Hình thức thể hiện | Quy định bài giảng | Ánh xạ chi tiết trong mã nguồn đồ án |
| :--- | :--- | :--- | :--- |
| **1. Tác nhân (Actor)** | **Hình con người (UML Actor stick figure)**, tên ghi ở dưới | `Khách hàng / Tác nhân` | Phân theo 3 vai trò: **Cư Dân**, **Nhân Viên Bảo Vệ**, **Quản Trị Viên** |
| **2. Giao diện (Boundary)** | Khối chữ nhật màu vàng (`#FEF3C7`) | **`[File code]`** | Đường dẫn chính xác file giao diện (`fe/templates/login.html`, `resident_dashboard.html`,...) |
| **3. Hệ thống (Control)** | Khối chữ nhật màu tím lam (`#E0E7FF`) | **`[File code / Hàm]`** | Đường dẫn file backend & Tên hàm (`be/app.py: ...`, `be/database.py: ...`) |
| **4. Cơ sở dữ liệu (Entity)** | Khối chữ nhật màu tím (`#F3E8FF`) | **`[db / Bảng]`** | Tên CSDL (`HTTT_QuanLyBaiXe_AI`) & Danh sách các bảng dữ liệu tác động |

### ⚡ Quy chuẩn khung rẽ nhánh `alt` (UML Alternative Combined Fragment):
- Mọi điều kiện kiểm tra (if/else) được bao bọc trong **Khung `alt`** với viền nét đứt (`dashed=1`).
- **Nửa trên**: Trường hợp hợp lệ / thành công (`[Happy Path]`).
- **Vạch ngăn cách nét đứt**: Nhãn **`[else: Điều kiện không hợp lệ / Thất bại / Cảnh báo]`**.
- **Nửa dưới**: Các bước xử lý ngoại lệ (mã lỗi HTTP 400/401/403/409, cảnh báo an ninh, thông báo Toast màu đỏ đến người dùng).

---

## 📂 DANH MỤC FILE DRAW.IO ĐÃ TẠO

Các file Draw.io đã sẵn sàng để mở trực tiếp trên [app.diagrams.net](https://app.diagrams.net):

1. **File Master (Tổng hợp 13 Use Cases trong 1 file, chia thành 13 Tab riêng biệt)**:
   - 📄 [`docs/SO_DO_TUAN_TU_HE_THONG.drawio`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/SO_DO_TUAN_TU_HE_THONG.drawio)
2. **Thư mục 13 file riêng lẻ theo từng Tác nhân & Chức năng**:
   - 📁 [`docs/drawio/`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/drawio)
     - **Nhóm Cư Dân**:
       - `uc01_resident_register.drawio`
       - `uc02_resident_login.drawio`
       - `uc03_resident_register_vehicle.drawio`
       - `uc04_resident_change_slot.drawio`
       - `uc05_resident_renew_pass.drawio`
       - `uc06_resident_transfer_request.drawio`
       - `uc07_resident_history.drawio`
     - **Nhóm Nhân Viên Bảo Vệ**:
       - `uc08_guard_auto_checkin.drawio`
       - `uc09_guard_checkout_verification.drawio`
       - `uc10_guard_collect_fee_barrier.drawio`
     - **Nhóm Quản Trị Viên (Admin)**:
       - `uc11_admin_user_mgmt.drawio`
       - `uc12_admin_approve_transfer.drawio`
       - `uc13_admin_analytics.drawio`
3. **Mã Nguồn PlantUML**:
   - 📄 [`docs/SEQUENCE_DIAGRAMS.puml`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/SEQUENCE_DIAGRAMS.puml)
4. **Script Sinh Tự Động Draw.io XML**:
   - 🐍 [`docs/generate_sequence_drawio.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/generate_sequence_drawio.py)

---

## 📊 BẢNG TỔNG HỢP ÁNH XẠ CODE THEO TỪNG TÁC NHÂN (13 SƠ ĐỒ)

### 👤 NHÓM 1: TÁC NHÂN CƯ DÂN (RESIDENT)

| Mã UC | Chức Năng Chi Tiết | Giao Diện `[File code]` | Hệ Thống `[File code / Hàm]` | CSDL `[db / Bảng]` | Điều Kiện `alt` / `else` |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **UC01** | Đăng ký tài khoản cư dân | `fe/templates/register.html` | `be/app.py: register()`<br/>`be/database.py: register_resident_user()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan` | `alt`: SĐT chưa đăng ký (Tạo user 200)<br/>`else`: SĐT đã tồn tại (Lỗi 400) |
| **UC02** | Đăng nhập cư dân | `fe/templates/login.html` | `be/app.py: login()`<br/>`be/database.py: check_user_credentials()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan` | `alt`: Đúng pass & active (Vào Dashboard)<br/>`else`: Sai pass/khóa (Báo lỗi 401) |
| **UC03** | Đăng ký xe & Chọn ô Cinema | `fe/templates/resident_dashboard.html`<br/>*(Modal `#cinemaModal`)* | `be/app.py: POST /api/resident/register_vehicle`<br/>`be/database.py: register_vehicle_with_slot()` | `HTTT_QuanLyBaiXe_AI /`<br/>`bai_do, vehicles, phuong_tien` | `alt`: Ô còn 'Trong' (Cấp ô, đổi màu Cyan)<br/>`else`: Ô đã 'DaDat' (Báo lỗi 409) |
| **UC04** | Đổi vị trí đỗ xe Cinema | `fe/templates/resident_dashboard.html`<br/>*(Modal `#changeSlotModal`)* | `be/app.py: POST /api/parking/change_slot`<br/>`be/database.py: change_vehicle_parking_slot()` | `HTTT_QuanLyBaiXe_AI /`<br/>`bai_do, vehicles, phuong_tien` | `alt`: Ô mới 'Trong' (Giải phóng ô cũ & cấp mới)<br/>`else`: Ô mới bận (Rollback transaction) |
| **UC05** | Gia hạn vé tháng cư dân | `fe/templates/resident_dashboard.html`<br/>*(Modal `#renewTicketModal`)* | `be/app.py: POST /api/resident/renew_ticket`<br/>`be/database.py: renew_monthly_ticket()` | `HTTT_QuanLyBaiXe_AI /`<br/>`vehicles, phuong_tien, lich_su_thanh_toan` | `alt`: Xe hợp lệ (Cộng hạn mới, lưu thanh toán)<br/>`else`: Không tìm thấy xe (Báo lỗi 404) |
| **UC06** | Yêu cầu chuyển nhượng xe | `fe/templates/resident_dashboard.html`<br/>*(Modal `#transferVehicleModal`)* | `be/app.py: POST /api/resident/transfer_vehicle`<br/>`be/database.py: create_vehicle_transfer_request()` | `HTTT_QuanLyBaiXe_AI /`<br/>`chuyen_nhuong_xe, cu_dan, vehicles` | `alt`: Tìm thấy cư dân nhận (Lập đơn Chờ duyệt)<br/>`else`: SĐT không tồn tại (Báo lỗi 400) |
| **UC07** | Tra cứu lịch sử xe vào/ra | `fe/templates/resident_dashboard.html`<br/>*(Bảng `#historySection`)* | `be/app.py: GET /api/resident/history`<br/>`be/database.py: get_resident_vehicle_history()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, lich_su_ra_vao` | `alt`: Có lịch sử (Render bảng & ảnh snapshot)<br/>`else`: Không có dữ liệu (Thông báo rỗng) |

---

### 🛡️ NHÓM 2: TÁC NHÂN NHÂN VIÊN BẢO VỆ (SECURITY GUARD / OPERATOR)

| Mã UC | Chức Năng Chi Tiết | Giao Diện `[File code]` | Hệ Thống `[File code / Hàm]` | CSDL `[db / Bảng]` | Điều Kiện `alt` / `else` |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **UC08** | AI Check-in xe vào tự động | `fe/templates/index.html`<br/>*(Tab `#recognition-page`, Camera Live)* | `be/app.py: gen_frames(), detect_plates_from_frame()`<br/>`be/database.py: process_parking_transaction()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, detections, lich_su_ra_vao` | `alt`: Nhận diện rõ & không trùng phiên (Mở Barrier)<br/>`else`: Phiên trùng/biển mờ (Báo động, giữ barrier) |
| **UC09** | Đối chiếu ra & Blacklist | `fe/templates/index.html`<br/>*(Bàn trực `#guard-station-page`)* | `be/app.py: GET /api/guard/verification/<plate>`<br/>`be/database.py: get_guard_verification_info()` | `HTTT_QuanLyBaiXe_AI /`<br/>`vehicles, parking_sessions, bai_do` | `alt`: Vé tháng còn hạn (Fee = 0đ, khớp ảnh)<br/>`else`: Xe Blacklist (Khóa barrier, còi báo động) |
| **UC10** | Thu phí & Mở Barrier cổng ra | `fe/templates/index.html`<br/>*(`#guardFeeBox`, `#guardConfirmActionBtn`)* | `be/app.py: POST /api/guard/collect_fee`<br/>`be/database.py: complete_parking_session()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, lich_su_ra_vao, hoa_don` | `alt`: Đã thu tiền (In hóa đơn, mở Barrier ra)<br/>`else`: Chưa thanh toán (Giữ nguyên Barrier đóng) |

---

### ⚙️ NHÓM 3: TÁC NHÂN QUẢN TRỊ VIÊN (SYSTEM ADMIN)

| Mã UC | Chức Năng Chi Tiết | Giao Diện `[File code]` | Hệ Thống `[File code / Hàm]` | CSDL `[db / Bảng]` | Điều Kiện `alt` / `else` |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **UC11** | Quản lý người dùng & Phân quyền | `fe/templates/index.html`<br/>*(Tab `#users-page`, `#editUserModal`)* | `be/app.py: POST /api/admin/users/update`<br/>`be/database.py: admin_update_user_info()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan, nhan_vien` | `alt`: Thao tác hợp lệ (Cập nhật role/status 200)<br/>`else`: Khóa Super Admin (Từ chối lỗi 403) |
| **UC12** | Phê duyệt đơn chuyển nhượng | `fe/templates/index.html`<br/>*(Tab `#transfers-page`)* | `be/app.py: POST /api/admin/transfer_requests/<id>/action`<br/>`be/database.py: process_transfer_request_action()` | `HTTT_QuanLyBaiXe_AI /`<br/>`chuyen_nhuong_xe, vehicles, phuong_tien` | `alt`: Bấm 'Duyệt' (Đổi chủ xe sang người nhận)<br/>`else`: Bấm 'Từ chối' (Đổi trạng thái đơn TuChoi) |
| **UC13** | Báo cáo thống kê & Doanh thu | `fe/templates/index.html`<br/>*(Tab `#reports-page`, `renderCharts`)* | `be/app.py: GET /api/analytics/revenue`<br/>`be/database.py: get_revenue_stats()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, statistics` | `alt`: Có giao dịch (Vẽ biểu đồ doanh thu & giờ)<br/>`else`: Không có giao dịch (Hiển thị biểu đồ 0) |

---

## 📝 CHI TIẾT SƠ ĐỒ TUẦN TỰ KÈM KHUNG ALT (MERMAID)

### 1. UC01 - Đăng Ký Tài Khoản Cư Dân (Tác nhân: Cư Dân)
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân<br/>(Resident)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/register.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: register()<br/>be/database.py: register_resident_user()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / app_users, cu_dan

    Resident->>UI: 1. Nhập Họ tên, SĐT, Căn hộ, Mật khẩu & Click 'Đăng ký'
    UI->>Sys: 2. POST /register (username, password, phone, apartment)
    Sys->>DB: 3. SELECT * FROM app_users WHERE username = %s OR phone = %s
    DB-->>Sys: 4. Trả về kết quả kiểm tra trùng lặp tài khoản

    alt Username & SĐT chưa từng đăng ký (Hợp lệ)
        Sys->>Sys: 5a. Băm mật khẩu an toàn PBKDF2/SHA-256 (generate_password_hash)
        Sys->>DB: 6a. INSERT INTO app_users & cu_dan (MaCuDan, HoTen, TenDangNhap, Role='Resident')
        DB-->>Sys: 7a. Xác nhận ghi bản ghi mới thành công (Affected rows = 1)
        Sys-->>UI: 8a. Phản hồi HTTP 200 {success: true, message: 'Đăng ký thành công'}
        UI-->>Resident: 9a. Hiển thị thông báo thành công & Chuyển hướng sang trang Đăng nhập
    else Username hoặc SĐT đã tồn tại / Dữ liệu không hợp lệ
        Sys-->>UI: 5b. Phản hồi HTTP 400 {success: false, message: 'Tài khoản hoặc SĐT đã tồn tại'}
        UI-->>Resident: 6b. Hiển thị Toast cảnh báo lỗi màu đỏ & Yêu cầu nhập lại thông tin
    end
```

---

### 2. UC02 - Đăng Nhập Cư Dân (Tác nhân: Cư Dân)
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân<br/>(Resident)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/login.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: login()<br/>be/database.py: check_user_credentials()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / app_users, cu_dan

    Resident->>UI: 1. Nhập tên đăng nhập, mật khẩu & Bấm 'Đăng nhập'
    UI->>Sys: 2. POST /login (username, password)
    Sys->>DB: 3. SELECT id, username, password_hash, role, status FROM app_users WHERE username = %s
    DB-->>Sys: 4. Trả về thông tin người dùng và mã băm password_hash

    alt Mật khẩu chính xác & status == 'active' & role == 'Resident'
        Sys->>Sys: 5a. Khởi tạo session['user'] = {id, role: 'Resident', username}
        Sys-->>UI: 6a. Phản hồi HTTP 200 {success: true, role: 'Resident', redirect: '/resident-dashboard'}
        UI-->>Resident: 7a. Điều hướng vào Cổng thông tin Cư dân (Resident Dashboard)
    else Sai mật khẩu hoặc Tài khoản bị vô hiệu hóa (status != 'active')
        Sys-->>UI: 5b. Phản hồi HTTP 401 {success: false, message: 'Sai tên đăng nhập hoặc mật khẩu'}
        UI-->>Resident: 6b. Hiển thị thông báo lỗi 'Đăng nhập thất bại' & Xóa trống mật khẩu
    end
```

---

### 3. UC03 - Đăng Ký Xe & Chọn Ô Đỗ Cinema (Tác nhân: Cư Dân)
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân<br/>(Resident)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/resident_dashboard.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/resident/register_vehicle<br/>be/database.py: register_vehicle_with_slot()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / bai_do, vehicles, phuong_tien

    Resident->>UI: 1. Nhập biển số, hiệu xe & Click chọn vị trí ô đỗ Cinema (VD: B1-A01)
    UI->>Sys: 2. POST /api/resident/register_vehicle (plate: '30H-999.88', slot_id: 'B1-A01', months: 3)
    Sys->>DB: 3. Khóa dòng kiểm tra: SELECT TrangThai FROM bai_do WHERE MaViTri = %s FOR UPDATE
    DB-->>Sys: 4. Trả về trạng thái hiện tại của ô đỗ

    alt Ô đỗ còn TRỐNG (TrangThai == 'Trong')
        Sys->>DB: 5a. UPDATE bai_do SET TrangThai = 'DaDat', BienSoXe = %s WHERE MaViTri = %s
        Sys->>DB: 6a. INSERT INTO vehicles & phuong_tien (BienSoXe, MaCuDan, ViTriDo, NgayHetHan)
        DB-->>Sys: 7a. Xác nhận lưu xe và đặt chỗ ô đỗ thành công
        Sys-->>UI: 8a. Phản hồi HTTP 200 {success: true, slot_id: 'B1-A01', plate: '30H-999.88'}
        UI-->>Resident: 9a. Đổi màu ô ghế Cinema sang Cyan (Xe của bạn) & Cập nhật thẻ xe 3D
    else Vị trí ô đỗ đã có người khác đặt trước (TrangThai == 'DaDat')
        Sys-->>UI: 5b. Phản hồi HTTP 409 {success: false, message: 'Vị trí đỗ vừa được đặt, vui lòng chọn ô khác'}
        UI-->>Resident: 6b. Tô đỏ ô đỗ và hiển thị thông báo yêu cầu chọn vị trí khác trên sơ đồ Cinema
    end
```

---

### 4. UC08 - AI Check-in Xe Vào Cổng (Tác nhân: Nhân Viên Bảo Vệ & Camera Cổng)
```mermaid
sequenceDiagram
    autonumber
    actor Guard as Nhân Viên Bảo Vệ<br/>(Security Guard)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: gen_frames(), detect_plates_from_frame()<br/>be/database.py: process_parking_transaction()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / parking_sessions, lich_su_ra_vao, detections

    Guard->>UI: 1. Xe tiến vào làn cổng, Camera gửi luồng video frames tới màn hình bàn trực
    UI->>Sys: 2. Stream khung hình video trực tiếp tới backend AI xử lý
    Sys->>Sys: 3. YOLOv8 cắt vùng biển số -> CRNN nhận dạng ký tự (VD: '51G-123.45')
    Sys->>DB: 4. Tra cứu phiên đỗ: SELECT id FROM parking_sessions WHERE plate_text = %s AND status = 'Parked'
    DB-->>Sys: 5. Trả về kết quả kiểm tra phiên đỗ hiện tại của xe

    alt Không có phiên trùng lặp & Biển số nhận diện rõ ràng (Xe vào hợp lệ)
        Sys->>DB: 6a. INSERT INTO parking_sessions (plate_text, check_in_time=NOW(), status='Parked', gate_in='Cổng Vào')
        Sys->>DB: 7a. Lưu bản ghi ảnh chụp vào detections & lich_su_ra_vao
        DB-->>Sys: 8a. Xác nhận tạo phiên gửi xe mới thành công
        Sys->>Sys: 9a. Gửi tín hiệu điều khiển mở Barrier cổng vào (barrier_state = 'OPEN')
        Sys-->>UI: 10a. Đẩy sự kiện Live Event WebSocket: 'Xe vào thành công' kèm ảnh chụp biển số
        UI-->>Guard: 11a. Cần Barrier nâng lên, màn hình LED hiển thị: 'Kính chào quý khách: 51G-123.45'
    else Xe đang có phiên mở chưa checkout hoặc Biển số mờ không nhận diện được
        Sys-->>UI: 6b. Đẩy cảnh báo an ninh về Bàn trực bảo vệ: 'Biển số trùng lặp / Nhận diện mờ'
        UI-->>Guard: 7b. Giữ nguyên Barrier đóng & Bật cửa sổ yêu cầu Bảo vệ kiểm tra, nhập biển số thủ công
    end
```

---

### 5. UC09 - Đối Chiếu Xe Ra & Cảnh Báo Blacklist (Tác nhân: Nhân Viên Bảo Vệ)
```mermaid
sequenceDiagram
    autonumber
    actor Guard as Nhân Viên Bảo Vệ<br/>(Security Guard)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: GET /api/guard/verification/<plate><br/>be/database.py: get_guard_verification_info()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / vehicles, parking_sessions, bai_do

    Guard->>UI: 1. Xe ra đến cổng, Camera đọc biển số hoặc Bảo vệ chọn xe kiểm tra
    UI->>Sys: 2. GET /api/guard/verification/51G-123.45
    Sys->>DB: 3. Truy vấn phiên đỗ: SELECT * FROM parking_sessions WHERE plate_text = %s AND status = 'Parked'
    Sys->>DB: 4. Truy vấn phân loại xe: SELECT group_type, monthly_ticket_expiry FROM vehicles WHERE plate_text = %s
    DB-->>Sys: 5. Trả về dữ liệu phiên vào, ảnh snapshot vào, nhóm đối tượng, hạn vé tháng

    alt Trường hợp 1: Xe Cư dân vé tháng còn hiệu lực (monthly_ticket_expiry >= NOW)
        Sys->>Sys: 6a. Xác nhận miễn phí gửi xe (fee = 0đ) theo chính sách vé tháng cư dân
        Sys-->>UI: 7a. Phản hồi HTTP 200 {is_resident: true, fee: 0, status: 'Valid'}
        UI-->>Guard: 8a. Hiển thị badge xanh 'VÉ THÁNG HỢP LỆ' & So sánh khớp ảnh Vào - Ra
    else Trường hợp 2: Xe thuộc Danh Sách Đen (group_type == 'Blacklist' / Cảnh báo trộm cắp)
        Sys->>Sys: 6b. Bật cờ cảnh báo an ninh khẩn cấp (security_alert = True, lock_barrier = True)
        Sys-->>UI: 7b. Phản hồi HTTP 200 {is_blacklist: true, alert_level: 'HIGH', fee: 0}
        UI-->>Guard: 8b. Khóa nút mở barrier, nhấp nháy đèn đỏ CẢNH BÁO XE GIAN LẬN/TRỘM CẮP & Báo động
    end
```

---

### 6. UC10 - Thu Phí Gửi Xe & Mở Barrier Cổng Ra (Tác nhân: Nhân Viên Bảo Vệ)
```mermaid
sequenceDiagram
    autonumber
    actor Guard as Nhân Viên Bảo Vệ<br/>(Security Guard)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/guard/collect_fee<br/>be/database.py: complete_parking_session()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / parking_sessions, lich_su_ra_vao, hoa_don

    Guard->>UI: 1. Khách thanh toán tiền mặt/quét mã VietQR, Bảo vệ bấm 'Xác Nhận Thu Phí & Mở Cổng'
    UI->>Sys: 2. POST /api/guard/collect_fee (session_id: 105, amount: 20000, method: 'Cash')

    alt Xác nhận thu phí thành công (Tiền mặt hoặc Chuyển khoản QR)
        Sys->>DB: 3a. UPDATE parking_sessions SET status = 'Completed', check_out_time = NOW(), fee = 20000
        Sys->>DB: 4a. INSERT INTO hoa_don (MaPhien, SoTien, HinhThucThanhToan, NgayLap)
        DB-->>Sys: 5a. Xác nhận ghi nhận doanh thu và kết thúc phiên gửi xe
        Sys->>Sys: 6a. Gửi lệnh điều khiển phần cứng mở cần Barrier cổng ra (Barrier_Out = 'OPEN')
        Sys-->>UI: 7a. Phản hồi HTTP 200 {success: true, invoice_code: 'HD-20261002-01', barrier: 'OPEN'}
        UI-->>Guard: 8a. In hóa đơn/phiếu xuất bãi, nâng cần Barrier cho xe ra & Cập nhật số chỗ trống
    else Chưa nhận được thanh toán hoặc Có tranh chấp cước phí
        Sys-->>UI: 3b. Phản hồi HTTP 400 {success: false, message: 'Giao dịch chưa hoàn tất'}
        UI-->>Guard: 4b. Giữ nguyên Barrier đóng, tiếp tục hiển thị chờ thanh toán
    end
```

---

### 7. UC11 - Quản Lý Người Dùng & Phân Quyền (Tác nhân: Quản Trị Viên)
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Quản Trị Viên<br/>(System Admin)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/admin/users/update<br/>be/database.py: admin_update_user_info()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / app_users, cu_dan, nhan_vien

    Admin->>UI: 1. Chọn tài khoản cần chỉnh sửa, cập nhật quyền hạn/trạng thái & Bấm 'Lưu thay đổi'
    UI->>Sys: 2. POST /api/admin/users/update (user_id: 5, role: 'Operator', status: 'active')
    Sys->>DB: 3. Tra cứu quyền hạn tài khoản mục tiêu: SELECT role FROM app_users WHERE id = %s
    DB-->>Sys: 4. Trả về thông tin vai trò hiện tại của tài khoản

    alt Thao tác hợp lệ (Không tự khóa tài khoản Root Super Admin)
        Sys->>DB: 5a. UPDATE app_users SET role = %s, status = %s WHERE id = %s
        Sys->>DB: 6a. Đồng bộ cập nhật bảng cu_dan / nhan_vien tương ứng
        DB-->>Sys: 7a. Xác nhận cập nhật thông tin thành công (Affected rows = 1)
        Sys-->>UI: 8a. Phản hồi HTTP 200 {success: true, message: 'Cập nhật tài khoản thành công'}
        UI-->>Admin: 9a. Tải lại danh sách người dùng & Hiển thị badge quyền hạn mới
    else Thao tác không hợp lệ (Cố tình vô hiệu hóa tài khoản Quản trị cao nhất)
        Sys-->>UI: 5b. Phản hồi HTTP 403 {success: false, message: 'Không thể vô hiệu hóa tài khoản Super Admin'}
        UI-->>Admin: 6b. Bật cảnh báo lỗi màu đỏ 'Từ chối thao tác bảo vệ an toàn hệ thống'
    end
```

---

### 8. UC12 - Phê Duyệt Đơn Chuyển Nhượng Xe (Tác nhân: Quản Trị Viên)
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Quản Trị Viên<br/>(System Admin)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: POST /api/admin/transfer_requests/<id>/action<br/>be/database.py: process_transfer_request_action()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / chuyen_nhuong_xe, vehicles, phuong_tien

    Admin->>UI: 1. Xem chi tiết đơn chuyển nhượng đang chờ duyệt & Bấm nút quyết định
    UI->>Sys: 2. POST /api/admin/transfer_requests/12/action (action: 'approve' / 'reject')
    Sys->>DB: 3. Lấy thông tin đơn: SELECT * FROM chuyen_nhuong_xe WHERE MaYeuCau = 12
    DB-->>Sys: 4. Trả về thông tin: Biển số xe, Cư dân chuyển, Cư dân nhận

    alt Admin bấm 'Phê Duyệt' (action == 'approve')
        Sys->>DB: 5a. TRANSACTION: UPDATE phuong_tien & vehicles SET MaCuDan = NguoiNhan WHERE BienSoXe = %s
        Sys->>DB: 6a. UPDATE chuyen_nhuong_xe SET TrangThai = 'DaDuyet', NgayDuyet = NOW()
        DB-->>Sys: 7a. Commit transaction chuyển nhượng thành công
        Sys-->>UI: 8a. Phản hồi HTTP 200 {success: true, message: 'Đã chuyển nhượng xe sang chủ sở hữu mới'}
        UI-->>Admin: 9a. Đổi huy hiệu đơn sang màu xanh 'ĐÃ DUYỆT' & Cập nhật danh mục xe
    else Admin bấm 'Từ Chối' (action == 'reject')
        Sys->>DB: 5b. UPDATE chuyen_nhuong_xe SET TrangThai = 'TuChoi', LyDo = 'Thông tin không chính xác'
        DB-->>Sys: 6b. Xác nhận cập nhật trạng thái từ chối đơn
        Sys-->>UI: 7b. Phản hồi HTTP 200 {success: true, message: 'Đã từ chối đơn chuyển nhượng'}
        UI-->>Admin: 8b. Đổi huy hiệu đơn sang màu đỏ 'ĐÃ TỪ CHỐI'
    end
```

---

### 9. UC13 - Báo Cáo Thống Kê & Doanh Thu (Tác nhân: Quản Trị Viên)
```mermaid
sequenceDiagram
    autonumber
    actor Admin as Quản Trị Viên<br/>(System Admin)
    participant UI as Giao diện<br/>[File code]<br/>fe/templates/index.html
    participant Sys as Hệ thống<br/>[File code / Hàm]<br/>be/app.py: GET /api/analytics/revenue<br/>be/database.py: get_revenue_stats()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / parking_sessions, statistics

    Admin->>UI: 1. Chọn khoảng thời gian xem báo cáo doanh thu & Bấm 'Xem phân tích'
    UI->>Sys: 2. GET /api/analytics/revenue & GET /api/analytics/hourly
    Sys->>DB: 3. SELECT DATE(check_out_time), SUM(fee), COUNT(*) FROM parking_sessions WHERE status='Completed' GROUP BY DATE(check_out_time)
    Sys->>DB: 4. SELECT HOUR(check_in_time), COUNT(*) FROM parking_sessions GROUP BY HOUR(check_in_time)
    DB-->>Sys: 5. Trả về tập dữ liệu tổng hợp doanh thu và số lượt xe theo giờ

    alt Có phát sinh lượt xe & Doanh thu trong kỳ báo cáo
        Sys-->>UI: 6a. Phản hồi HTTP 200 JSON dữ liệu biểu đồ {dates: [...], revenues: [...], hourly: [...]}
        UI-->>Admin: 7a. Render biểu đồ cột doanh thu & Biểu đồ đường lưu lượng giờ cao điểm (Chart.js)
    else Kỳ báo cáo chưa có lượt xe nào phát sinh
        Sys-->>UI: 6b. Phản hồi HTTP 200 JSON tập rỗng {dates: [], revenues: [], total: 0}
        UI-->>Admin: 7b. Hiển thị thông báo 'Chưa có dữ liệu thống kê trong khoảng thời gian đã chọn'
    end
```
