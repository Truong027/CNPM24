# BÁO CÁO PHÂN TÍCH YÊU CẦU: SƠ ĐỒ TUẦN TỰ (SEQUENCE DIAGRAMS)
## HỆ THỐNG NHẬN DIỆN BIỂN SỐ & QUẢN LÝ BÃI ĐỖ XE THÔNG MINH AI (SMART PARKING)

- **Môn học**: Công nghệ phần mềm (CNPM24)
- **Lớp**: 24CT2
- **Sinh viên thực hiện**: Ông Thân Quốc Trường
- **Trường**: Đại học Kiến trúc Đà Nẵng (DAU) - Khoa Công nghệ thông tin

---

## 📌 QUY CHUẨN THIẾT KẾ THEO YÊU CẦU CỦA GIẢNG VIÊN

Toàn bộ sơ đồ tuần tự được thiết kế tuân thủ 100% hướng dẫn bài giảng trên lớp và quy chuẩn UML chuẩn hóa:

| Cột (Lifeline) | Hình thức thể hiện | Quy định bài giảng | Ánh xạ chi tiết trong mã nguồn đồ án (ĐƯỜNG DẪN ĐẦY ĐỦ) |
| :--- | :--- | :--- | :--- |
| **1. Tác nhân (Actor)** | **Hình con người (UML Actor stick figure)**, tên ghi ở dưới | `Khách hàng / Tác nhân` | Phân theo vai trò: **Cư Dân**, **Người Dùng**, **Nhân Viên Bảo Vệ**, **Quản Trị Viên** |
| **2. Giao diện (Boundary)** | Khối chữ nhật màu vàng (`#FEF3C7`) | **`[File code]`** | **Đường dẫn tuyệt đối đầy đủ đến file frontend**:<br/>`D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\fe\templates\...` |
| **3. Hệ thống (Control)** | Khối chữ nhật màu tím lam (`#E0E7FF`) | **`[File code / Hàm]`** | **Đường dẫn tuyệt đối đầy đủ đến file backend & Tên hàm**:<br/>`D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\be\app.py: ...` |
| **4. Cơ sở dữ liệu (Entity)** | Khối chữ nhật màu tím (`#F3E8FF`) | **`[db / Bảng]`** | Tên CSDL (`HTTT_QuanLyBaiXe_AI`) & Danh sách các bảng dữ liệu tác động |

---

### ⚡ THANH KÍCH HOẠT (ACTIVATION BAR / EXECUTION SPECIFICATION)

Toàn bộ 14 sơ đồ đã được bổ sung **Thanh kích hoạt (Activation Bar)** tiêu chuẩn:
- **Tác nhân (Actor)**: Kích hoạt trong toàn bộ thời gian tham gia phiên tương tác (từ bước gửi yêu cầu đến khi nhận kết quả hiển thị).
- **Giao diện (UI Boundary)**: Kích hoạt khi tiếp nhận thao tác của người dùng, duy trì trạng thái chờ trong suốt quá trình backend xử lý và kết thúc khi hiển thị kết quả.
- **Hệ thống (Sys Control)**: Kích hoạt liên tục từ lúc nhận HTTP Request (POST/GET) từ UI, điều phối nghiệp vụ, kiểm tra rẽ nhánh trong khung `alt`, và giải phóng khi trả về HTTP Response.
- **Cơ sở dữ liệu (DB Entity)**: Kích hoạt cục bộ **chính xác vào các khoảng thời gian thực thi truy vấn/transaction** (`SELECT` kiểm tra, `INSERT`/`UPDATE` dữ liệu, `COMMIT`/`ROLLBACK`).
- **Mũi tên thông điệp**: Gắn chính xác vào mép của thanh kích hoạt (thay vì đâm xuyên qua lifeline).

---

### ⚡ QUY CHUẨN KHUNG RẼ NHÁNH `ALT` (CHỈ TRONG HỆ THỐNG & CƠ SỞ DỮ LIỆU)

Theo đúng yêu cầu nghiệp vụ và bài giảng:
- **Phạm vi của Khung `alt`**:
  - Khung `alt` **CHỈ bao phủ Cột Hệ Thống và Cột Cơ Sở DỮ LIỆU** (Tọa độ X: `680px` -> `1490px`).
  - Khung **KHÔNG bao phủ Cột Tác Nhân và Cột Giao Diện**.
- **Các bước bên trong Khung `alt`**:
  - **Nhánh `[Điều kiện Hợp lệ]`**: Hệ thống xử lý logic nghiệp vụ nội bộ (băm mật khẩu, tính toán phí, sinh mã OTP) -> Ghi/cập nhật CSDL (`INSERT`/`UPDATE`) -> CSDL xác nhận thành công.
  - **Vạch phân cách `[else: Điều kiện Không hợp lệ / Thất bại]`**: Hệ thống hủy thao tác / rollback transaction / thiết lập mã lỗi nội bộ.
- **Các bước sau khi kết thúc Khung `alt`**:
  - Hệ thống gửi kết quả / thông báo về Giao diện (`Sys -> UI`).
  - Giao diện hiển thị kết quả tương ứng lên màn hình cho Tác nhân (`UI -> Actor`).

---

## 📂 DANH MỤC FILE DRAW.IO ĐÃ TẠO

Các file Draw.io đã sẵn sàng để mở trực tiếp trên [app.diagrams.net](https://app.diagrams.net):

1. **File Master (Tổng hợp 14 Use Cases trong 1 file, chia thành các Tab có gắn nhãn nhóm Tác nhân)**:
   - 📄 [`docs/SO_DO_TUAN_TU_HE_THONG.drawio`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/SO_DO_TUAN_TU_HE_THONG.drawio)
2. **Thư mục 14 file riêng lẻ theo từng Tác nhân & Chức năng**:
   - 📁 [`docs/drawio/`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/drawio)
     - **Nhóm Cư Dân & Người Dùng**:
       - `uc01_resident_register.drawio` (Đăng ký tài khoản cư dân)
       - `uc02_resident_login.drawio` (Đăng nhập cư dân)
       - `uc02b_forgot_password.drawio` (**Quên mật khẩu & Xác thực OTP**)
       - `uc03_resident_register_vehicle.drawio` (Đăng ký xe & Chọn ô đỗ Cinema)
       - `uc04_resident_change_slot.drawio` (Đổi vị trí đỗ xe Cinema)
       - `uc05_resident_renew_pass.drawio` (Gia hạn vé tháng cư dân)
       - `uc06_resident_transfer_request.drawio` (Yêu cầu chuyển nhượng xe & ô đỗ)
       - `uc07_resident_history.drawio` (Tra cứu lịch sử xe vào/ra)
     - **Nhóm Nhân Viên Bảo Vệ**:
       - `uc08_guard_auto_checkin.drawio` (Nhận diện AI & Tự động Check-in xe vào)
       - `uc09_guard_checkout_verification.drawio` (Đối chiếu xe ra & Cảnh báo Blacklist)
       - `uc10_guard_collect_fee_barrier.drawio` (Thu phí & Mở Barrier cổng ra)
     - **Nhóm Quản Trị Viên (Admin)**:
       - `uc11_admin_user_mgmt.drawio` (Quản lý tài khoản người dùng & Phân quyền)
       - `uc12_admin_approve_transfer.drawio` (Phê duyệt đơn chuyển nhượng)
       - `uc13_admin_analytics.drawio` (Báo cáo thống kê & Biểu đồ doanh thu)
3. **Mã Nguồn PlantUML**:
   - 📄 [`docs/SEQUENCE_DIAGRAMS.puml`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/SEQUENCE_DIAGRAMS.puml)
4. **Script Sinh Tự Động Draw.io XML**:
   - 🐍 [`docs/generate_sequence_drawio.py`](file:///d:/CNPM24CT2_OngThanQuocTruong/ongthanquoctruong_24CT2_cnpm/docs/generate_sequence_drawio.py)

---

## 📊 BẢNG TỔNG HỢP ÁNH XẠ CODE & ĐIỀU KIỆN ALT (HỆ THỐNG & CSDL)

### 👤 NHÓM 1: TÁC NHÂN CƯ DÂN & NGƯỜI DÙNG (RESIDENT / APP USERS)

| Mã UC | Chức Năng Chi Tiết | Giao Diện `[File code đầy đủ]` | Hệ Thống `[File code / Hàm đầy đủ]` | CSDL `[db / Bảng]` | Điều Kiện Khung `alt` (Chỉ Hệ Thống & CSDL) |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **UC01** | Đăng ký tài khoản cư dân | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\register.html` | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: register()`<br/>`be\database.py: register_resident_user()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan` | **`alt`**: Chưa tồn tại (Băm pass, ghi CSDL app_users, cu_dan)<br/>**`else`**: Đã tồn tại (Hủy thao tác, gán status 400) |
| **UC02** | Đăng nhập cư dân | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\login.html` | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: login()`<br/>`be\database.py: check_user_credentials()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan` | **`alt`**: Mật khẩu khớp & active (Tạo session, cập nhật last_login)<br/>**`else`**: Sai pass/bị khóa (Từ chối xác thực, gán status 401) |
| **UC02b** | Quên mật khẩu & OTP | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\forgot_password.html`<br/>*(kèm `reset_password.html`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: api_forgot_password()`<br/>`be\database.py: generate_otp(), verify_and_reset_password()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, password_reset_tokens` | **`alt`**: Email tồn tại (Sinh OTP, lưu password_reset_tokens, gửi mail)<br/>**`else`**: Email không tồn tại (Hủy yêu cầu cấp OTP) |
| **UC03** | Đăng ký xe & Chọn ô Cinema | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\resident_dashboard.html`<br/>*(Modal `#cinemaModal`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: POST /api/resident/register_vehicle`<br/>`be\database.py: register_vehicle_with_slot()` | `HTTT_QuanLyBaiXe_AI /`<br/>`bai_do, vehicles, phuong_tien` | **`alt`**: Ô đỗ 'Trong' (UPDATE bai_do DaDat, INSERT vehicles)<br/>**`else`**: Ô đã 'DaDat' (Hủy giao dịch đặt chỗ, gán status 409) |
| **UC04** | Đổi vị trí đỗ xe Cinema | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\resident_dashboard.html`<br/>*(Modal `#changeSlotModal`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: POST /api/parking/change_slot`<br/>`be\database.py: change_vehicle_parking_slot()` | `HTTT_QuanLyBaiXe_AI /`<br/>`bai_do, vehicles, phuong_tien` | **`alt`**: Ô mới 'Trong' (Transaction: nhả ô cũ, gán ô mới, commit)<br/>**`else`**: Ô mới đã bận (Rollback transaction) |
| **UC05** | Gia hạn vé tháng cư dân | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\resident_dashboard.html`<br/>*(Modal `#renewTicketModal`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: POST /api/resident/renew_ticket`<br/>`be\database.py: renew_monthly_ticket()` | `HTTT_QuanLyBaiXe_AI /`<br/>`vehicles, phuong_tien, lich_su_thanh_toan` | **`alt`**: Xe hợp lệ (Cộng dồn thời hạn, UPDATE phuong_tien, INSERT thanh toán)<br/>**`else`**: Biển số không tồn tại (Hủy giao dịch gia hạn) |
| **UC06** | Yêu cầu chuyển nhượng xe | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\resident_dashboard.html`<br/>*(Modal `#transferVehicleModal`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: POST /api/resident/transfer_vehicle`<br/>`be\database.py: create_vehicle_transfer_request()` | `HTTT_QuanLyBaiXe_AI /`<br/>`chuyen_nhuong_xe, cu_dan, vehicles` | **`alt`**: Cư dân nhận hợp lệ (INSERT chuyen_nhuong_xe ChoDuyet)<br/>**`else`**: SĐT không thuộc cư dân (Từ chối tạo đơn) |
| **UC07** | Tra cứu lịch sử xe vào/ra | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\resident_dashboard.html`<br/>*(Bảng `#historySection`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: GET /api/resident/history`<br/>`be\database.py: get_resident_vehicle_history()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, lich_su_ra_vao` | **`alt`**: Có bản ghi (Tổng hợp danh sách kèm ảnh snapshot)<br/>**`else`**: Không có bản ghi (Khởi tạo mảng rỗng) |

---

#### 🛡️ NHÓM 2: TÁC NHÂN NHÂN VIÊN BẢO VỆ (SECURITY GUARD)

| Mã UC | Chức Năng Chi Tiết | Giao Diện `[File code đầy đủ]` | Hệ Thống `[File code / Hàm đầy đủ]` | CSDL `[db / Bảng]` | Điều Kiện Khung `alt` (Chỉ Hệ Thống & CSDL) |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **UC08** | AI Check-in xe vào tự động | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\index.html`<br/>*(Tab `#recognition-page`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: gen_frames(), detect_plates_from_frame()`<br/>`be\database.py: process_parking_transaction()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, detections, lich_su_ra_vao` | **`alt`**: Không trùng phiên (INSERT parking_sessions, kích hoạt Barrier OPEN)<br/>**`else`**: Trùng phiên/biển mờ (Giữ Barrier đóng, bật cờ kiểm tra) |
| **UC09** | Đối chiếu xe ra & Blacklist | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\index.html`<br/>*(Bàn trực `#guard-station-page`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: GET /api/guard/verification/<plate>`<br/>`be\database.py: get_guard_verification_info()` | `HTTT_QuanLyBaiXe_AI /`<br/>`vehicles, parking_sessions, bai_do` | **`alt`**: Vé tháng còn hạn (Xác nhận fee = 0đ)<br/>**`else`**: Xe Blacklist (Bật cờ cảnh báo an ninh khẩn cấp, khóa barrier) |
| **UC10** | Thu phí & Mở Barrier xe ra | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\index.html`<br/>*(`#guardFeeBox`, `#guardConfirmActionBtn`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: POST /api/guard/collect_fee`<br/>`be\database.py: complete_parking_session()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, lich_su_ra_vao, hoa_don` | **`alt`**: Đã thu tiền (UPDATE parking_sessions, INSERT hoa_don, Barrier OPEN)<br/>**`else`**: Chưa thanh toán (Giữ Barrier đóng, bật cảnh báo) |

---

#### ⚙️ NHÓM 3: TÁC NHÂN QUẢN TRỊ VIÊN (SYSTEM ADMIN)

| Mã UC | Chức Năng Chi Tiết | Giao Diện `[File code đầy đủ]` | Hệ Thống `[File code / Hàm đầy đủ]` | CSDL `[db / Bảng]` | Điều Kiện Khung `alt` (Chỉ Hệ Thống & CSDL) |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **UC11** | Quản lý người dùng & Phân quyền | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\index.html`<br/>*(Tab `#users-page`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: POST /api/admin/users/update`<br/>`be\database.py: admin_update_user_info()` | `HTTT_QuanLyBaiXe_AI /`<br/>`app_users, cu_dan, nhan_vien` | **`alt`**: Hợp lệ (UPDATE app_users, đồng bộ cu_dan/nhan_vien)<br/>**`else`**: Khóa Super Admin (Từ chối cập nhật, gán status 403) |
| **UC12** | Phê duyệt đơn chuyển nhượng | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\index.html`<br/>*(Tab `#transfers-page`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: POST /api/admin/transfer_requests/<id>/action`<br/>`be\database.py: process_transfer_request_action()` | `HTTT_QuanLyBaiXe_AI /`<br/>`chuyen_nhuong_xe, vehicles, phuong_tien` | **`alt`**: Admin Duyệt (Transaction: UPDATE phuong_tien, chuyen_nhuong_xe DaDuyet)<br/>**`else`**: Admin Từ chối (UPDATE chuyen_nhuong_xe TuChoi) |
| **UC13** | Báo cáo thống kê & Doanh thu | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`fe\templates\index.html`<br/>*(Tab `#reports-page`, `renderCharts`)* | `D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\`<br/>`be\app.py: GET /api/analytics/revenue`<br/>`be\database.py: get_revenue_stats()` | `HTTT_QuanLyBaiXe_AI /`<br/>`parking_sessions, statistics` | **`alt`**: Có lượt xe trong kỳ (Tổng hợp mảng dates, revenues, hourly)<br/>**`else`**: Không có lượt xe (Khởi tạo mảng rỗng) |

---

## 📝 MINH HỌA SƠ ĐỒ TUẦN TỰ KÈM THANH KÍCH HOẠT (MERMAID)

### 1. UC01 - Đăng Ký Tài Khoản Cư Dân
```mermaid
sequenceDiagram
    autonumber
    actor Resident as Cư Dân<br/>(Resident)
    participant UI as Giao diện<br/>[File code đầy đủ]<br/>D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\<br/>fe\templates\register.html
    participant Sys as Hệ thống<br/>[File code / Hàm đầy đủ]<br/>D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\<br/>be\app.py: register()<br/>be\database.py: register_resident_user()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / app_users, cu_dan

    Resident->>UI: 1. Nhập Họ tên, SĐT, Căn hộ, Mật khẩu & Click 'Đăng ký'
    activate UI
    UI->>Sys: 2. POST /register (username, password, phone, apartment)
    activate Sys
    Sys->>DB: 3. SELECT * FROM app_users WHERE username = %s OR phone = %s
    activate DB
    DB-->>Sys: 4. Trả về kết quả kiểm tra trùng lặp tài khoản
    deactivate DB

    Note over Sys,DB: KHUNG ALT: Chỉ kiểm tra điều kiện & tác động CSDL trong Hệ thống và CSDL
    alt Username & SĐT chưa từng đăng ký (Hợp lệ)
        Sys->>Sys: 5a. Băm mật khẩu an toàn PBKDF2/SHA-256 (generate_password_hash)
        Sys->>DB: 6a. INSERT INTO app_users & cu_dan (MaCuDan, HoTen, TenDangNhap...)
        activate DB
        DB-->>Sys: 7a. Xác nhận ghi bản ghi mới thành công (Affected rows = 1)
        deactivate DB
    else Username hoặc SĐT đã tồn tại / Dữ liệu không hợp lệ
        Sys->>Sys: 5b. Hủy thao tác đăng ký & Thiết lập mã trạng thái lỗi (status = 400)
    end

    Note over UI,Sys: Sau khi kết thúc alt, Hệ thống phản hồi Giao diện và hiển thị cho người dùng
    Sys-->>UI: 8. Phản hồi thông báo kết quả đăng ký (HTTP 200 Thành công hoặc HTTP 400 Lỗi)
    deactivate Sys
    UI-->>Resident: 9. Hiển thị kết quả lên giao diện (Chuyển sang trang Đăng nhập hoặc Toast cảnh báo đỏ)
    deactivate UI
```

---

### 2. UC02b - Quên Mật Khẩu & Đặt Lại Mật Khẩu OTP (`forgot_password.html`)
```mermaid
sequenceDiagram
    autonumber
    actor User as Người Dùng<br/>(Cư Dân / Nhân Viên)
    participant UI as Giao diện<br/>[File code đầy đủ]<br/>D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\<br/>fe\templates\forgot_password.html
    participant Sys as Hệ thống<br/>[File code / Hàm đầy đủ]<br/>D:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm\<br/>be\app.py: api_forgot_password()<br/>be\database.py: generate_otp()
    participant DB as Cơ sở dữ liệu<br/>[db / Bảng]<br/>HTTT_QuanLyBaiXe_AI / app_users, password_reset_tokens

    User->>UI: 1. Nhập Email đăng ký & Bấm 'Gửi mã xác thực OTP'
    activate UI
    UI->>Sys: 2. POST /api/forgot-password (email: 'cu_dan@example.com')
    activate Sys
    Sys->>DB: 3. SELECT id, username FROM app_users WHERE email = %s AND status = 'active'
    activate DB
    DB-->>Sys: 4. Trả về kết quả tìm kiếm tài khoản theo email
    deactivate DB

    Note over Sys,DB: KHUNG ALT: Xử lý mã OTP và lưu trữ CSDL
    alt Email hợp lệ & Khớp tài khoản đang hoạt động
        Sys->>Sys: 5a. Sinh mã OTP ngẫu nhiên 6 chữ số (Hiệu lực trong 5 phút)
        Sys->>DB: 6a. INSERT INTO password_reset_tokens (email, otp_hash, expires_at)
        activate DB
        DB-->>Sys: 7a. Xác nhận lưu trữ mã OTP thành công
        deactivate DB
        Sys->>Sys: 8a. Gửi Email chứa mã OTP bảo mật đến hòm thư người dùng
    else Email không tồn tại trong hệ thống hoặc định dạng không hợp lệ
        Sys->>Sys: 5b. Hủy yêu cầu cấp OTP & Thiết lập thông báo lỗi (Email not found)
    end

    Note over UI,Sys: Sau khi kết thúc alt, phản hồi về Giao diện
    Sys-->>UI: 9. Phản hồi kết quả xử lý (HTTP 200 Đã gửi OTP hoặc HTTP 400 Email không tồn tại)
    deactivate Sys
    UI-->>User: 10. Chuyển sang trang reset_password.html hoặc Báo lỗi đỏ yêu cầu kiểm tra lại email
    deactivate UI
```
