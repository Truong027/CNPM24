# Hệ Thống Quản Lý Bãi Đỗ Xe Thông Minh Ứng Dụng AI Nhận Diện Biển Số Xe (Smart Parking AI)

- **Đề tài**: Hệ thống Nhận diện Biển số xe & Quản lý Bãi đỗ xe Thông minh ứng dụng AI
- **Môn học**: Công nghệ phần mềm (CNPM24) — **Lớp**: `24CT2`
- **Sinh viên thực hiện**: Ông Thân Quốc Trường
- **Đơn vị**: Khoa Công nghệ thông tin — Trường Đại học Kiến trúc Đà Nẵng (DAU)

> Xem tài liệu tổng quan cấp repository tại [`../README.md`](../README.md).

---

## 🏛️ Kiến Trúc Hệ Thống & Phân Quyền 3 Vai Trò (System Architecture & 3-Role RBAC)

```mermaid
flowchart TB
    subgraph Users["Các Tác Nhân & 3 Vai Trò Chính"]
        direction LR
        Public["Khách Vãng Lai (Public)"]
        Admin["Role 1: Quản Trị Viên (Admin)<br/>be/roles/admin_user.py"]
        Guard["Role 2: Bảo Vệ (Operator / Security)<br/>be/roles/guard_user.py"]
        Resident["Role 3: Cư Dân (Resident / User)<br/>be/roles/resident_user.py"]
    end

    subgraph Frontend["Giao Diện Người Dùng (Client Layer)"]
        FE_Public["Public & Auth<br/>fe/templates/public_dashboard.html, login.html, register.html<br/>public/public-dashboard.html, login.html, register.html"]
        FE_Ops["Bàn Trực & Quản Trị (/operations-dashboard)<br/>fe/templates/index.html | public/index.html, operations-dashboard.html"]
        FE_Res["Cổng Cư Dân (/resident-dashboard)<br/>fe/templates/resident_dashboard.html | public/resident-dashboard.html"]
    end

    subgraph Backend["Tầng Ứng Dụng & API"]
        Flask["Python Flask Backend<br/>be/app.py"]
        Vercel["Vercel Node.js Serverless API<br/>vercel.json + api/[...slug].js + api/index.js"]
    end

    subgraph AI["AI Core & Thiết Bị Cổng"]
        YOLO["YOLOv8s Detector<br/>be/yolov8s.pt"]
        OCR["CRNN-CTC + EasyOCR Fallback<br/>be/plate_ocr_integration.py, artifacts/plate_ocr/"]
        Barrier["Barrier Cổng Vào / Ra"]
    end

    subgraph DB["Cơ Sở Dữ Liệu MySQL (Dual-Sync)"]
        DBCore["be/database.py & be/sql/httt_quan_ly_bai_xe_ai.sql<br/>Auth/RBAC: app_users, cu_dan, nhan_vien, quyen_*, phan_quyen_*<br/>AI/Telemetry: plates, detections, parking_sessions, vehicles, statistics<br/>Nghiệp vụ: bai_do (100 ô B1/B2), phuong_tien, chuyen_nhuong_xe, hoa_don, bang_gia"]
    end

    Public --> FE_Public
    Admin --> FE_Ops
    Guard --> FE_Ops
    Resident --> FE_Res

    FE_Public <--> Flask
    FE_Ops <--> Flask
    FE_Res <--> Flask
    FE_Ops -.-> Vercel
    FE_Res -.-> Vercel

    Flask <--> YOLO --> OCR
    Flask --> Barrier
    Flask <--> DBCore
```

---

## 👥 Chi Tiết 3 Vai Trò Trong Đề Tài

1. **Role 1 — Quản trị viên (`Admin` | `be/roles/admin_user.py` -> `/operations-dashboard`)**:
   - Quản lý tài khoản & phân quyền (`app_users`, `nhan_vien`, `cu_dan`, `quyen_admin`, `phan_quyen_admin`): tạo Bảo vệ (`/api/admin/guards/create`), tạo Cư dân (`/api/admin/residents/create`), sửa thông tin & đổi vai trò (`/api/admin/users/update`), khóa/mở tài khoản (`/api/admin/users/toggle_status`), đặt lại mật khẩu (`/api/admin/users/reset_password`), xóa người dùng.
   - Phê duyệt đơn chuyển nhượng xe (`/api/admin/transfer_requests`, `/api/admin/transfer_requests/<id>/action`, `/update_doc` -> `chuyen_nhuong_xe`).
   - Quản lý danh mục phương tiện & phân nhóm `Normal / Whitelist / Blacklist` (`/api/vehicles`, `/api/vehicles/save`, `/api/vehicles/delete/<plate>` -> `vehicles`, `plates`).
   - Quản lý sơ đồ 100 ô đỗ Cinema (`Ham_B1`, `Ham_B2`: `/api/parking/map` -> `bai_do`).
   - Xem thống kê KPI, doanh thu, giờ cao điểm, xuất CSV & test AI ảnh tĩnh (`/get_dashboard_summary`, `/api/analytics/revenue`, `/api/analytics/peak-hours`, `/api/report_export`, `/api/recognize_image`).

2. **Role 2 — Nhân viên Bảo vệ (`Operator` / `Security` | `be/roles/guard_user.py` -> `/operations-dashboard`)**:
   - Giám sát Camera Live Stream (`/video_feed_webcam`, `/video_feed_phone`) & chuyển đổi chế độ camera (`/api/guard/camera_mode`, `/api/guard/latest_event`).
   - Kiểm soát xe vào/ra, đối chiếu ảnh chụp lúc vào và lúc ra (`/api/guard/verification/<plate>`, `/api/guard/manual_entry`, `/api/parking/checkin`, `/api/parking/checkout/<id>`).
   - Tiếp nhận cảnh báo đỏ xe `Blacklist`, từ chối mở cổng.
   - Tra cứu cước phí gửi xe, thu tiền & kích hoạt mở/đóng Barrier (`/api/guard/collect_fee`, `/api/guard/barrier/trigger` -> `bang_gia`, `hoa_don`, `lich_su_ra_vao`, `quyen_baove`, `phan_quyen_bao_ve`).

3. **Role 3 — Cư dân (`Resident` / `User` | `be/roles/resident_user.py` -> `/resident-dashboard`)**:
   - Đăng ký tài khoản cư dân (`/register`, `/api/register`), Đăng nhập (`/login`, `/api/login`), Quên & Đặt lại mật khẩu qua OTP (`/forgot-password`, `/reset-password` -> `quan_ly_otp_token`).
   - Cập nhật hồ sơ & đổi mật khẩu (`/api/resident/profile`, `/api/resident/update_profile`, `/api/resident/change_password`).
   - Quản lý xe căn hộ (`/api/resident/vehicles`, `/api/resident/add_vehicle`, `PUT/DELETE /api/resident/vehicles/<plate>` -> `phuong_tien`, `vehicles`).
   - Xem sơ đồ bãi đỗ xe Cinema `Ham_B1` & `Ham_B2`, chọn / đổi vị trí đỗ (`/api/parking/map`, `/api/resident/change_slot` -> `bai_do`).
   - Gia hạn vé tháng, lập/theo dõi đơn chuyển nhượng xe & xem lịch sử ra/vào cá nhân (`/api/resident/renew_ticket`, `/api/resident/transfer_vehicle`, `/api/resident/transfer_requests`, `/api/resident/history`).

---

## 🏗️ Cấu Trúc Dự Án

```text
ongthanquoctruong_24CT2_cnpm/
├── api/                              # Vercel Serverless API (index.js, [...slug].js)
├── public/                           # Giao diện tĩnh cho Vercel SPA deployment
├── fe/                               # Frontend Jinja2 Templates & Static assets (Local Flask)
├── be/                               # Backend Flask + YOLOv8 + CRNN/EasyOCR + MySQL + roles/ + sql/ + scripts/
├── tests/                            # Bộ kiểm thử tự động (test_full_features.py, test_user_management.py, ...)
├── docs/                             # Tuần Tự/, LUONGXULY/, PERT/, Wireframe/, Word báo cáo/, drawio/
├── doc_images/                       # Ảnh sơ đồ & UI demo dùng cho báo cáo
├── schema.dbml                       # Lược đồ quan hệ DBML phục vụ GitDiagram
├── vercel.json                       # Cấu hình định tuyến Vercel
├── package.json                      # Thông tin package phục vụ Vercel/static serve
├── requirements.txt                  # Thư viện Python cho Backend & AI
└── .env.example                      # Mẫu biến môi trường MySQL & SECRET_KEY
```

---

## 🚀 Hướng Dẫn Cài Đặt & Khởi Chạy Local

1. **Kích hoạt môi trường ảo:**
   ```powershell
   .venv\Scripts\activate
   ```
2. **Cài đặt các thư viện cần thiết:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Cấu hình MySQL (tạo `.env` từ `.env.example`):**
   ```env
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_DATABASE=HTTT_QuanLyBaiXe_AI
   MYSQL_PORT=3306
   APP_SECRET_KEY=dev-secret-change-me
   ```
   Khởi tạo bảng và dữ liệu 100 chỗ đỗ:
   ```powershell
   python be/setup_bai_do.py
   ```
4. **Khởi chạy Server Flask:**
   ```powershell
   python be/app.py
   ```
   Truy cập: **http://127.0.0.1:5000**

---

## 🧪 Chạy Kiểm Thử (Run Tests)

```powershell
python -m unittest discover -s tests -p "test_*.py"
```
