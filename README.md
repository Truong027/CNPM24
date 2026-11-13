# Hệ Thống Quản Lý Bãi Đỗ Xe Thông Minh Ứng Dụng AI Nhận Diện Biển Số Xe (Smart Parking AI)

- **Đề tài**: Hệ thống Nhận diện Biển số xe & Quản lý Bãi đỗ xe Thông minh ứng dụng AI
- **Môn học**: Công nghệ phần mềm (CNPM24) — **Lớp**: `24CT2`
- **Sinh viên thực hiện**: Ông Thân Quốc Trường
- **Đơn vị**: Khoa Công nghệ thông tin — Trường Đại học Kiến trúc Đà Nẵng (DAU)
- **Repository**: [https://github.com/Truong027/CNPM24](https://github.com/Truong027/CNPM24)
- **Thư mục mã nguồn chính**: [`ongthanquoctruong_24CT2_cnpm/`](ongthanquoctruong_24CT2_cnpm/)

---

## 1. Tổng Quan Đề Tài & Kiến Trúc Hệ Thống

Hệ thống giải quyết bài toán kiểm soát phương tiện ra/vào chung cư, tòa nhà và bãi đỗ xe 2 tầng hầm (**Hầm B1** & **Hầm B2**, tổng **100 vị trí ô tô con** thiết kế theo sơ đồ rạp chiếu phim — Cinema Parking Map), kết hợp **Thị giác máy tính (YOLOv8s + CRNN-CTC + EasyOCR)** để nhận diện biển số theo thời gian thực, **phân quyền chặt chẽ 3 vai trò (RBAC: Admin, Guard/Operator, Resident)** và **kiến trúc triển khai song song** (Python Flask đầy đủ AI + MySQL chạy Local, đồng thời hỗ trợ bản Static SPA + Vercel Serverless Node.js API).

### Sơ Đồ Kiến Trúc Tổng Thể (Cho GitDiagram & Tài Liệu Hệ Thống)

```mermaid
flowchart TB
    subgraph Actors["1. Tác Nhân & Phân Quyền 3 Vai Trò (RBAC)"]
        direction LR
        Public["Khách Vãng Lai / Public Guest"]
        Admin["Role 1: Quản Trị Viên (Admin)<br/>be/roles/admin_user.py"]
        Guard["Role 2: Bảo Vệ / Vận Hành (Operator / Security)<br/>be/roles/guard_user.py"]
        Resident["Role 3: Cư Dân (Resident / User)<br/>be/roles/resident_user.py"]
    end

    subgraph Frontend["2. Tầng Giao Diện Người Dùng (Client Layer)"]
        direction TB
        FE_Public["Public Dashboard & Auth<br/>fe/templates/public_dashboard.html, login.html, register.html<br/>forgot_password.html, reset_password.html<br/>public/public-dashboard.html, login.html, register.html"]
        FE_Ops["Bàn Trực & Quản Trị (/operations-dashboard)<br/>fe/templates/index.html<br/>public/index.html & public/operations-dashboard.html"]
        FE_Res["Cổng Cư Dân (/resident-dashboard)<br/>fe/templates/resident_dashboard.html<br/>public/resident-dashboard.html"]
    end

    subgraph AppLayer["3. Tầng Ứng Dụng & API Gateway (Dual Deployment)"]
        direction LR
        Flask["Local Full-Stack Backend (Python Flask)<br/>ongthanquoctruong_24CT2_cnpm/be/app.py<br/>Auth Session, RBAC, REST API, MJPEG Stream"]
        Vercel["Cloud Serverless API (Vercel Node.js)<br/>ongthanquoctruong_24CT2_cnpm/vercel.json<br/>api/[...slug].js -> api/index.js"]
    end

    subgraph AILayer["4. Tầng Thị Giác Máy Tính AI & Thiết Bị Cổng (Computer Vision & IoT)"]
        direction TB
        Camera["Camera Luồng Vào / Ra<br/>Webcam & IP Camera RTSP/HTTP"]
        YOLO["YOLOv8s Plate Detector<br/>be/yolov8s.pt"]
        OCR["Dual OCR Engine<br/>be/plate_ocr_integration.py<br/>CRNN-CTC (be/artifacts/plate_ocr/model.pt) + EasyOCR"]
        Tracker["IOU Tracker & 3-Frame Voting Filter<br/>Loại nhiễu rung khung hình"]
        Barrier["Thiết Bị Barrier Cổng Vào / Ra<br/>/api/guard/barrier/trigger"]
    end

    subgraph DataLayer["5. Tầng Lưu Trữ Cơ Sở Dữ Liệu MySQL (Dual-Sync Database)"]
        direction TB
        DB_Mod["Module CSDL Python<br/>be/database.py & be/sql/httt_quan_ly_bai_xe_ai.sql<br/>schema.dbml"]
        DB_Auth["Nhóm Bảng Tài Khoản & RBAC<br/>app_users, cu_dan, nhan_vien, lich_su_dang_nhap<br/>quan_ly_otp_token, quyen_admin, quyen_baove<br/>quyen_user, phan_quyen_admin, phan_quyen_bao_ve"]
        DB_AI["Nhóm Bảng AI & Giám Sát Lượt Xe<br/>plates, detections, parking_sessions<br/>vehicles, provinces, vehicle_types, statistics"]
        DB_Biz["Nhóm Bảng Nghiệp Vụ Chung Cư<br/>bai_do (100 ô B1/B2), phuong_tien<br/>chuyen_nhuong_xe, lich_su_ra_vao, bang_gia, hoa_don"]
    end

    Public --> FE_Public
    Admin --> FE_Ops
    Guard --> FE_Ops
    Resident --> FE_Res
    Resident -.->|"Đăng ký / Quên MK OTP"| FE_Public

    FE_Public <-->|"HTTP / JSON"| Flask
    FE_Ops <-->|"HTTP / JSON / MJPEG"| Flask
    FE_Res <-->|"HTTP / JSON"| Flask

    FE_Public -.->|"Cloud Demo"| Vercel
    FE_Ops -.->|"Cloud Demo"| Vercel
    FE_Res -.->|"Cloud Demo"| Vercel

    Camera -->|"Video Frames"| Flask
    Flask --> YOLO --> OCR --> Tracker
    Tracker -->|"Kết quả biển số chuẩn"| Flask
    Flask -->|"Mở / Đóng cổng"| Barrier

    Flask <-->|"MySQL Connector"| DB_Mod
    DB_Mod --> DB_Auth
    DB_Mod --> DB_AI
    DB_Mod --> DB_Biz
```

---

## 2. Phân Rã Chi Tiết 3 Vai Trò (3 Roles) Theo Đúng Đề Tài

Hệ thống định nghĩa và kiểm soát quyền truy cập ở cả tầng route bảo vệ (`be/roles/admin_user.py`, `be/roles/guard_user.py`, `be/roles/resident_user.py`, `@login_required`, Flask session) lẫn tầng giao diện và bảng phân quyền trong CSDL (`app_users.role`, `quyen_admin`, `quyen_baove`, `quyen_user`, `phan_quyen_admin`, `phan_quyen_bao_ve`):

```mermaid
flowchart LR
    subgraph R1["Role 1: Admin (Quản Trị Viên)"]
        A1["Quản lý Người dùng & Phân quyền RBAC<br/>Tạo Bảo vệ/Cư dân, Sửa Role, Khóa/Mở, Reset MK"]
        A2["Phê duyệt Đơn Chuyển nhượng xe<br/>Duyệt / Từ chối / Cập nhật ảnh đơn xác nhận"]
        A3["Quản lý Phương tiện & Phân nhóm<br/>Normal / Whitelist / Blacklist"]
        A4["Quản lý Sơ đồ Bãi đỗ Cinema<br/>100 vị trí ô tô Hầm B1 & Hầm B2"]
        A5["Thống kê, Doanh thu, Giờ cao điểm<br/>Xuất CSV & Kiểm thử AI ảnh tĩnh"]
    end

    subgraph R2["Role 2: Guard / Operator (Bảo Vệ Ca Trực)"]
        G1["Giám sát Camera Live Vào / Ra<br/>Chế độ AI Auto hoặc Thủ công"]
        G2["Kiểm soát Check-In / Check-Out<br/>Đối chiếu ảnh xe Vào - Ra & Nhập biển số tay"]
        G3["An ninh Cổng & Blacklist Alert<br/>Phát hiện xe cấm, từ chối mở Barrier"]
        G4["Thu phí & Điều khiển Barrier<br/>Tính cước tự động, Xác nhận thu tiền, Mở cổng"]
    end

    subgraph R3["Role 3: Resident (Cư Dân Căn Hộ)"]
        C1["Đăng ký / Đăng nhập / OTP Quên MK<br/>Cập nhật hồ sơ & Đổi mật khẩu"]
        C2["Quản lý Phương tiện Căn hộ<br/>Thêm / Sửa / Xóa xe ô tô con"]
        C3["Chọn & Đổi Vị trí Bãi đỗ Cinema<br/>Đặt chỗ trống tại Hầm B1 & Hầm B2"]
        C4["Vé tháng, Chuyển nhượng & Lịch sử<br/>Gia hạn vé, Lập đơn chuyển xe, Xem lịch sử ra vào"]
    end

    SharedDB[("MySQL Dual-Sync Core<br/>be/database.py")]
    R1 <--> SharedDB
    R2 <--> SharedDB
    R3 <--> SharedDB
```

### Chi Tiết Trách Nhiệm & Thành Phần Mã Nguồn Từng Role

| Role | Giá trị `app_users.role` | Module kiểm tra quyền | Màn hình chính | Bảng CSDL liên quan |
| :--- | :--- | :--- | :--- | :--- |
| **1. Quản trị viên (`Admin`)** | `Admin` | `be/roles/admin_user.py` (`is_admin`) | `/operations-dashboard` (`fe/templates/index.html`, `public/operations-dashboard.html`) | `app_users`, `nhan_vien`, `cu_dan`, `quyen_admin`, `phan_quyen_admin`, `chuyen_nhuong_xe`, `vehicles`, `phuong_tien`, `bai_do`, `hoa_don`, `statistics` |
| **2. Bảo vệ (`Guard / Operator`)** | `Operator`, `Security` | `be/roles/guard_user.py` (`is_guard`) | `/operations-dashboard` (`fe/templates/index.html`, `public/operations-dashboard.html`) | `app_users`, `nhan_vien`, `quyen_baove`, `phan_quyen_bao_ve`, `plates`, `detections`, `parking_sessions`, `lich_su_ra_vao`, `bang_gia`, `hoa_don`, `vehicles` |
| **3. Cư dân (`Resident`)** | `Resident` (hoặc `User` khi tự đăng ký) | `be/roles/resident_user.py` (`is_resident`) | `/resident-dashboard` (`fe/templates/resident_dashboard.html`, `public/resident-dashboard.html`) | `app_users`, `cu_dan`, `quyen_user`, `quan_ly_otp_token`, `phuong_tien`, `vehicles`, `bai_do`, `chuyen_nhuong_xe`, `lich_su_ra_vao`, `parking_sessions` |
| **4. Khách vãng lai (`Public`)** | Chưa đăng nhập | Public routes | `/` (`fe/templates/public_dashboard.html`, `public/public-dashboard.html`) | `bai_do`, `plates`, `detections`, `parking_sessions` (chỉ đọc thống kê công khai) |

### Luồng Nghiệp Vụ Liên Thông Giữa 3 Vai Trò (Cross-Role Workflow)

1. **Cư dân (`Resident`)** đăng ký tài khoản trực tuyến tại `/register` (có thể chọn ngay biển số & ô đỗ tại Hầm B1/B2), hoặc đăng nhập tại `/login` để vào `/resident-dashboard`: thêm/sửa xe, đổi chỗ đỗ kiểu rạp phim, gia hạn vé tháng, hoặc **lập đơn chuyển nhượng quyền sử dụng xe** kèm ảnh giấy xác nhận gửi lên bảng `chuyen_nhuong_xe` (`TrangThai = 'Pending'`).
2. **Quản trị viên (`Admin`)** đăng nhập `/operations-dashboard` để quản lý toàn bộ người dùng (tạo tài khoản Bảo vệ/Cư dân, đổi role, khóa/mở tài khoản, reset mật khẩu), **xem và phê duyệt/từ chối đơn chuyển nhượng** (`/api/admin/transfer_requests/<id>/action` — khi duyệt sẽ tự động cập nhật chủ sở hữu mới ở `phuong_tien` & `bai_do`), phân loại xe `Normal / Whitelist / Blacklist`, theo dõi doanh thu và giờ cao điểm.
3. **Nhân viên Bảo vệ (`Operator / Security`)** trực ca tại `/operations-dashboard`: quan sát 2 luồng Camera Live Cổng Vào/Ra, tiếp nhận kết quả nhận diện tự động từ AI (`YOLOv8 + CRNN-CTC + EasyOCR`), xử lý cảnh báo xe `Blacklist`, đối chiếu ảnh chụp Vào – Ra, nhập biển số thủ công khi cần, thu phí theo `bang_gia` -> xuất `hoa_don` và kích hoạt mở Barrier.

---

## 3. Pipeline AI Nhận Diện Biển Số & Xử Lý Ra/Vào

```mermaid
sequenceDiagram
    autonumber
    participant Cam as Camera Cổng Vào/Ra
    participant AI as YOLOv8 + Dual OCR (be/app.py)
    participant Track as IOU Tracker & 3-Frame Voting
    participant DB as MySQL (be/database.py)
    participant GuardUI as Bàn Trực Bảo Vệ

    Cam->>AI: Frame video (gen_frames / /api/recognize_image)
    AI->>AI: 1. YOLOv8s (be/yolov8s.pt) khoanh vùng biển số
    AI->>AI: 2. CRNN-CTC (be/artifacts/plate_ocr/model.pt)<br/>+ EasyOCR fallback đọc & chuẩn hóa ký tự
    AI->>Track: Đối chiếu vị trí IOU & cộng phiếu (>= 3 frames ổn định)
    Track->>DB: process_parking_transaction(plate, gate_type)
    DB->>DB: Kiểm tra vehicles.group_type
    alt Xe thuộc Blacklist
        DB-->>GuardUI: Phát cảnh báo ĐỎ & khóa Barrier
    else Xe hợp lệ (Whitelist / Vé tháng / Vãng lai)
        alt Cổng Vào (Gate IN)
            DB->>DB: Tạo phiên parking_sessions ('Parked') & lich_su_ra_vao ('DangTrongBai')
            DB-->>GuardUI: Hiển thị trạng thái & cho phép mở Barrier vào
        else Cổng Ra (Gate OUT)
            DB->>DB: Tính duration_minutes & cước phí (bang_gia / vé tháng)
            DB-->>GuardUI: /api/guard/verification/<plate> đối chiếu ảnh Vào - Ra
            GuardUI->>DB: POST /api/guard/collect_fee -> Completed & Mở Barrier ra
        end
    end
```

- **Phát hiện vùng biển số**: [`ongthanquoctruong_24CT2_cnpm/be/yolov8s.pt`](ongthanquoctruong_24CT2_cnpm/be/yolov8s.pt) (`ultralytics` YOLOv8s).
- **Nhận diện ký tự quang học kép (Dual OCR)**:
  - [`ongthanquoctruong_24CT2_cnpm/be/plate_ocr_inference.py`](ongthanquoctruong_24CT2_cnpm/be/plate_ocr_inference.py) & [`artifacts/plate_ocr/model.pt`](ongthanquoctruong_24CT2_cnpm/be/artifacts/plate_ocr/model.pt) + [`vocab.json`](ongthanquoctruong_24CT2_cnpm/be/artifacts/plate_ocr/vocab.json): mô hình CRNN-CTC huấn luyện chuyên biệt cho biển số Việt Nam.
  - [`ongthanquoctruong_24CT2_cnpm/be/crnn_ocr_wrapper.py`](ongthanquoctruong_24CT2_cnpm/be/crnn_ocr_wrapper.py) & [`plate_ocr_integration.py`](ongthanquoctruong_24CT2_cnpm/be/plate_ocr_integration.py): kết hợp EasyOCR fallback khi khung hình mờ/nghiêng và chuẩn hóa định dạng biển số Việt Nam.
- **Lọc nhiễu chuyển động**: Tracking dựa trên IOU và bỏ phiếu 3 khung hình liên tiếp trước khi ghi DB.

---

## 4. Thiết Kế Cơ Sở Dữ Liệu MySQL (Dual-Sync Architecture)

Mã nguồn CSDL được định nghĩa trong [`ongthanquoctruong_24CT2_cnpm/be/database.py`](ongthanquoctruong_24CT2_cnpm/be/database.py), [`be/sql/httt_quan_ly_bai_xe_ai.sql`](ongthanquoctruong_24CT2_cnpm/be/sql/httt_quan_ly_bai_xe_ai.sql) và mô tả trực quan tại [`schema.dbml`](ongthanquoctruong_24CT2_cnpm/schema.dbml):

1. **Nhóm bảng Tài khoản, OTP & Phân quyền 3 Role**:
   - `app_users`, `nhan_vien`, `cu_dan`, `lich_su_dang_nhap`, `quan_ly_otp_token`
   - `quyen_admin`, `quyen_baove`, `quyen_user`, `phan_quyen_admin`, `phan_quyen_bao_ve`
2. **Nhóm bảng AI Nhận diện & Phiên đỗ xe**:
   - `provinces`, `vehicle_types`, `plates`, `detections`, `parking_sessions`, `vehicles`, `statistics`
3. **Nhóm bảng Nghiệp vụ Chung cư & Thanh toán**:
   - `bai_do` (100 vị trí ô tô 2 tầng `Ham_B1` và `Ham_B2`, chia theo dãy `A..E`, trạng thái `Trong` / `DaDat` / `BaoTri`)
   - `phuong_tien`, `chuyen_nhuong_xe`, `lich_su_ra_vao`, `bang_gia`, `hoa_don`
   - Trigger toàn vẹn `trg_KhongXoaCuDan_KhiXeTrongBai` ngăn xóa cư dân khi phương tiện vẫn đang trong bãi (`DangTrongBai`).

---

## 5. Danh Mục API Endpoints Đầy Đủ (Backend Flask & Vercel Serverless)

### A. Xác thực & Công khai (Public / Auth)
| Method | Endpoint | Chức năng |
| :--- | :--- | :--- |
| `GET` | `/`, `/api/public/dashboard` | Trang tổng quan công khai & số liệu B1/B2 real-time |
| `GET`, `POST` | `/login`, `/api/login`, `/api/session`, `/api/logout` | Đăng nhập, kiểm tra phiên làm việc và điều hướng theo role |
| `GET`, `POST` | `/register`, `/api/register` | Đăng ký tài khoản cư dân mới (kèm xe & vị trí đỗ) |
| `GET`, `POST` | `/forgot-password`, `/api/forgot-password`, `/reset-password`, `/api/reset-password` | Tạo mã OTP & đặt lại mật khẩu |

### B. Role 1 — Quản trị viên (`Admin`)
| Method | Endpoint | Chức năng |
| :--- | :--- | :--- |
| `GET` | `/operations-dashboard` | Bảng điều khiển quản trị & vận hành |
| `GET`, `POST`, `DELETE` | `/api/admin/users`, `/api/admin/guards/create`, `/api/admin/residents/create`, `/api/admin/users/update`, `/api/admin/users/toggle_status`, `/api/admin/users/reset_password`, `/api/admin/users/<phone>`, `/api/admin/guards/update`, `/api/admin/guards/<username>` | Quản lý toàn bộ tài khoản Bảo vệ & Cư dân, phân vai trò, khóa/mở, đặt lại mật khẩu |
| `GET`, `POST` | `/api/admin/transfer_requests`, `/api/admin/transfer_requests/<id>/action`, `/api/admin/transfer_requests/<id>/update_doc` | Xem danh sách đơn chuyển nhượng, phê duyệt/từ chối và cập nhật ảnh hồ sơ |
| `GET`, `POST`, `DELETE` | `/api/vehicles`, `/api/vehicles/save`, `/api/vehicles/delete/<plate_text>` | Quản lý danh mục xe & phân nhóm `Normal / Whitelist / Blacklist` |
| `GET` | `/get_dashboard_summary`, `/get_statistics`, `/get_stats_by_province`, `/get_stats_by_vehicle_type`, `/api/analytics/revenue`, `/api/analytics/peak-hours`, `/api/report_export` | Thống kê KPI, doanh thu, giờ cao điểm, tỷ lệ tỉnh/loại xe và xuất báo cáo CSV |
| `POST` | `/api/recognize_image` | Tải ảnh tĩnh lên kiểm thử nhận diện biển số AI |

### C. Role 2 — Nhân viên Bảo vệ (`Operator / Security`)
| Method | Endpoint | Chức năng |
| :--- | :--- | :--- |
| `GET` | `/video_feed_webcam`, `/video_feed_phone` | Luồng video MJPEG trực tiếp kèm khung nhận diện AI |
| `GET`, `POST` | `/api/guard/camera_mode`, `/api/guard/latest_event`, `/api/guard/initial_plate` | Chuyển chế độ AI Auto/Thủ công & cập nhật sự kiện xe mới nhất |
| `GET`, `POST` | `/api/guard/verification/<plate>`, `/api/guard/manual_entry`, `/api/guard/collect_fee`, `/api/guard/barrier/trigger` | Đối chiếu ảnh Vào – Ra, nhập tay biển số, thu cước phí & kích hoạt Barrier |
| `GET`, `POST` | `/api/parking/sessions`, `/api/parking/checkin`, `/api/parking/checkout/<session_id>` | Quản lý phiên xe vào/ra và checkout thủ công |
| `GET` | `/get_plates`, `/get_plate_details/<plate_text>`, `/get_plate_detections/<plate_text>` | Tra cứu lịch sử biển số & chi tiết các lần quét AI |

### D. Role 3 — Cư dân (`Resident`)
| Method | Endpoint | Chức năng |
| :--- | :--- | :--- |
| `GET` | `/resident-dashboard` | Cổng dịch vụ Cư dân |
| `GET`, `POST` | `/api/resident/profile`, `/api/resident/update_profile`, `/api/resident/change_password` | Xem, cập nhật hồ sơ cá nhân & đổi mật khẩu |
| `GET`, `POST`, `PUT`, `DELETE` | `/api/resident/vehicles`, `/api/resident/add_vehicle`, `/api/resident/vehicles/<plate>` | Quản lý danh sách xe đã đăng ký của căn hộ |
| `GET`, `POST` | `/api/parking/map`, `/api/resident/change_slot` | Xem sơ đồ bãi đỗ 100 chỗ B1/B2 & chọn/đổi vị trí đỗ xe |
| `GET`, `POST` | `/api/resident/renew_ticket`, `/api/resident/transfer_vehicle`, `/api/resident/transfer_requests`, `/api/resident/history` | Gia hạn vé tháng, lập/theo dõi đơn chuyển nhượng xe & xem lịch sử ra vào |

---

## 6. Tài Liệu Phân Tích, Thiết Kế & Quản Trị Dự Án (`docs/`)

- **Biểu đồ Tuần tự (Sequence Diagrams)** — `docs/Tuần Tự/`:
  - Chức năng Đăng ký người dùng, Đăng nhập đa vai trò, Phê duyệt đơn chuyển nhượng Admin, Quản lý và phân quyền người dùng Admin (`.drawio` + `.png`).
- **Biểu đồ Luồng Xử Lý & Wireframe** — `docs/LUONGXULY/` & `docs/Wireframe/`:
  - Các sơ đồ luồng xử lý chi tiết + bộ phác thảo Wireframe cho Dashboard công khai, Đăng ký, Đăng nhập, Duyệt đơn chuyển nhượng, Phân quyền Admin.
- **Sơ đồ Mạng PERT / CPM** — `docs/PERT/` ([`BANG_THONG_SO_PERT.md`](ongthanquoctruong_24CT2_cnpm/docs/PERT/BANG_THONG_SO_PERT.md), [`SO_DO_PERT_DE_1.drawio`](ongthanquoctruong_24CT2_cnpm/docs/PERT/SO_DO_PERT_DE_1.drawio)):
  - Tính toán theo phương pháp $t_s(i)$, $t_m(i)$ và $t_{df}(cv)$ với đỉnh tách `7` (`4 → 7: t_G = 15`, hai cung giả `t'_G` tới `5` và `8`): **Đường găng `A → D → G → J`** (`[0] → (1) → (4) → (7) --t'G--> (8) → [9]`), tổng thời gian hoàn thành dự án **$T_{max} = 38$ ngày**.
- **Báo cáo Tổng hợp Word / PDF** — `docs/Word báo cáo/BAOCAOBANNOP.docx` & `BAOCAOBANNOP.pdf`:
  - Đầy đủ Chương 1 & Chương 2 (41 trang): Lý thuyết, Tuần tự, PERT/CPM, Demo 3 bước thiết kế UI/UX, truy vấn SQL thống kê tổng/từng hầm (`Ham_B1`, `Ham_B2`) & thống kê vai trò (`app_users`), ERD & Data Dictionary.

---

## 7. Cấu Trúc Thư Mục Dự Án (Project Tree)

```text
CNPM24/
├── README.md                                         # Tài liệu tổng quan kiến trúc & 3 Role (GitHub & GitDiagram)
├── .gitignore                                        # Quy tắc loại trừ file môi trường (.env), cache & dataset thô
└── ongthanquoctruong_24CT2_cnpm/
    ├── README.md                                     # Tài liệu chi tiết bên trong thư mục dự án
    ├── vercel.json                                   # Cấu hình rewrite & deploy Vercel (Static SPA + Serverless API)
    ├── package.json                                  # Metadata Node.js cho môi trường frontend/Vercel
    ├── requirements.txt                              # Danh sách thư viện Python (Flask, Torch, Ultralytics, EasyOCR, MySQL)
    ├── schema.dbml                                   # Lược đồ quan hệ DBML phục vụ trực quan hóa ERD & 3 Role
    ├── .env.example                                  # Mẫu biến môi trường kết nối MySQL & APP_SECRET_KEY
    │
    ├── api/                                          # TẦNG SERVERLESS API TRÊN VERCEL (NODE.JS)
    │   ├── index.js                                  # Serverless API handler (Auth, Admin, Guard, Resident, Map, Analytics)
    │   └── [...slug].js                              # Catch-all dynamic route chuyển tiếp về api/index.js
    │
    ├── public/                                       # FRONTEND STATIC SPA (VERCEL DEPLOYMENT)
    │   ├── index.html                                # Giao diện Vận hành chính / Guard Station
    │   ├── public-dashboard.html / public_dashboard.html
    │   ├── operations-dashboard.html / operations_dashboard.html
    │   ├── resident-dashboard.html / resident_dashboard.html
    │   ├── login.html, register.html
    │   ├── forgot-password.html / forgot_password.html
    │   ├── reset-password.html / reset_password.html
    │   └── camera_entry.svg, camera_exit.svg
    │
    ├── fe/                                           # PHÂN HỆ FRONTEND LOCAL (JINJA2 TEMPLATES)
    │   ├── templates/
    │   │   ├── public_dashboard.html                 # Trang chủ công khai (/)
    │   │   ├── index.html                            # Bàn trực Bảo vệ & Bảng điều khiển Admin (/operations-dashboard)
    │   │   ├── resident_dashboard.html               # Cổng dịch vụ Cư dân & Sơ đồ bãi xe Cinema (/resident-dashboard)
    │   │   ├── login.html, register.html
    │   │   └── forgot_password.html, reset_password.html
    │   └── README.md
    │
    ├── be/                                           # PHÂN HỆ BACKEND FLASK + AI CORE + MYSQL
    │   ├── app.py                                    # Web Server Flask, RESTful APIs, Camera Streaming & Auth Session
    │   ├── database.py                               # Module kết nối MySQL, khởi tạo bảng, seed tài khoản & nghiệp vụ Dual-Sync
    │   ├── setup_bai_do.py                           # Khởi tạo 100 vị trí đỗ ô tô (Ham_B1, Ham_B2)
    │   ├── plate_ocr_inference.py                    # Suy luận OCR CRNN-CTC biển số xe
    │   ├── plate_ocr_integration.py                  # Tích hợp YOLOv8 + CRNN-CTC + EasyOCR fallback
    │   ├── crnn_ocr_wrapper.py                       # Wrapper chuẩn hóa đầu ra OCR
    │   ├── yolov8s.pt                                # Trọng số YOLOv8 phát hiện biển số
    │   ├── artifacts/plate_ocr/                      # model.pt & vocab.json (CRNN-CTC)
    │   ├── roles/                                    # Phân rã hàm kiểm tra & điều hướng 3 Vai trò
    │   │   ├── admin_user.py                         # Role Admin
    │   │   ├── guard_user.py                         # Role Operator / Security (Bảo vệ)
    │   │   └── resident_user.py                      # Role Resident (Cư dân)
    │   ├── sql/
    │   │   ├── httt_quan_ly_bai_xe_ai.sql            # Script DDL + Trigger MySQL đầy đủ
    │   │   └── bien_so_xe_sample.sql                 # Dữ liệu mẫu biển số & tỉnh thành
    │   ├── scripts/                                  # Công cụ tạo/kiểm tra DB & huấn luyện OCR
    │   ├── requirements.txt
    │   └── README.md
    │
    ├── tests/                                        # BỘ KIỂM THỬ TỰ ĐỘNG (UNIT & INTEGRATION TESTS)
    │   ├── test_full_features.py                     # Kiểm thử toàn trình 3 Role, chuyển nhượng xe & phân quyền
    │   ├── test_user_management.py                   # Kiểm thử quản lý người dùng, reset mật khẩu & RBAC
    │   ├── test_cinema_parking.py                    # Kiểm thử sơ đồ 100 ô đỗ B1/B2
    │   ├── test_sample_logins.py, test_api_simple.py, test_detection.py, test_save_plate.py, test_get_plates_func.py, test_http_request.py
    │   └── README.md
    │
    ├── docs/                                         # TÀI LIỆU CNPM, BIỂU ĐỒ & BÁO CÁO
    │   ├── Tuần Tự/                                  # Sơ đồ tuần tự (.drawio & .png)
    │   ├── LUONGXULY/                                # Sơ đồ luồng xử lý (.drawio, .png & script render)
    │   ├── PERT/                                     # Sơ đồ PERT/CPM Đề 1, bảng thông số & tài liệu hướng dẫn
    │   ├── Wireframe/                                # Wireframe giao diện các màn hình chính
    │   ├── Word báo cáo/                             # BAOCAOBANNOP.docx, BAOCAOBANNOP.pdf
    │   ├── drawio/                                   # Bộ 13 Use Case chi tiết (uc01 -> uc13)
    │   ├── KHAO_SAT_YEU_CAU.md, HE_THONG_VA_LUONG_XU_LY.md, ERD_DIAGRAM.md
    │   └── USE_CASE_DIAGRAMS.puml, USE_CASE_ACTORS_DETAILED.puml, SEQUENCE_DIAGRAMS.puml
    │
    └── doc_images/                                   # Kho ảnh sơ đồ & giao diện thực tế chèn báo cáo
```

---

## 8. Hướng Dẫn Cài Đặt, Khởi Chạy & Kiểm Thử

### A. Chạy Cục Bộ (Local Full-Stack: Flask + YOLOv8/CRNN + MySQL)

1. **Di chuyển vào thư mục dự án và kích hoạt môi trường ảo (`.venv`):**
   ```powershell
   cd ongthanquoctruong_24CT2_cnpm
   .venv\Scripts\activate
   ```
2. **Cài đặt thư viện (nếu chưa có `.venv`):**
   ```powershell
   pip install -r requirements.txt
   ```
3. **Cấu hình MySQL:**
   - Khởi động MySQL (`localhost:3306`), sao chép `.env.example` thành `.env` và điền `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`, `APP_SECRET_KEY`.
   - Khởi tạo bảng và dữ liệu 100 chỗ đỗ Cinema:
     ```powershell
     python be/setup_bai_do.py
     ```
4. **Khởi chạy máy chủ Backend Flask (tự động kích hoạt `.venv` nếu chạy từ Python hệ thống):**
   ```powershell
   python be/app.py
   ```
   Truy cập: **http://127.0.0.1:5000**

5. **Tài khoản mẫu khởi tạo sẵn (`be/database.py` -> `seed_default_users`)**:
   - **Admin**: SĐT `0900000001` (`admin`) | **Bảo vệ (Operator)**: `0912345678` (`baove1`), `0923456789` (`baove2`) | **Cư dân (Resident)**: `0901234567` (`cudan1`), `0907654321` (`cudan2`) *(xem mật khẩu seed trong `be/database.py`)*

### B. Chạy Kiểm Thử Tự Động

```powershell
cd ongthanquoctruong_24CT2_cnpm
python -m unittest discover -s tests -p "test_*.py"
```

### C. Triển Khai Cloud Demo (Vercel)

- Cấu hình [`ongthanquoctruong_24CT2_cnpm/vercel.json`](ongthanquoctruong_24CT2_cnpm/vercel.json) phục vụ giao diện tĩnh từ `public/` và định tuyến `/api/*` tới Serverless Function [`api/index.js`](ongthanquoctruong_24CT2_cnpm/api/index.js) (hỗ trợ đầy đủ luồng demo cho cả 3 Role: Admin, Bảo vệ/Operator, Cư dân).
