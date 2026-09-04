# Phân hệ Frontend (FE) - Hệ thống Quản lý Bãi xe AI

Thư mục này chứa toàn bộ mã nguồn giao diện người dùng (UI/UX) của hệ thống.

## Cấu trúc thư mục
```text
fe/
├── templates/
│   ├── index.html              # Dashboard quản trị & Giám sát làn xe thời gian thực (Admin/Bảo vệ)
│   ├── resident_dashboard.html # Dashboard quản lý xe cá nhân & lịch sử gửi xe (Cư dân/Khách)
│   ├── login.html              # Giao diện Đăng nhập hệ thống
│   ├── register.html           # Giao diện Đăng ký tài khoản (Admin, Resident, User)
│   ├── forgot_password.html    # Giao diện Yêu cầu mã OTP khôi phục mật khẩu
│   └── reset_password.html     # Giao diện Nhập mã OTP và Đổi mật khẩu mới
└── static/                     # Chứa tài nguyên tĩnh (CSS, JS, hình ảnh)
```

## Phân quyền hiển thị theo vai trò (Role-based Views)
- **Admin / Staff (Bảo vệ)**: Truy cập trang chủ `/` (`index.html`) để giám sát camera biển số, đối soát lượt vào/ra, điều khiển barrier, xem biểu đồ lưu lượng và thống kê doanh thu.
- **Resident (Cư dân)**: Truy cập `/resident-dashboard` (`resident_dashboard.html`) để quản lý các phương tiện cá nhân đã đăng ký, tra cứu lịch sử ra vào và quản lý phí gửi xe.
- **Khách vãng lai**: Màn hình đăng nhập/đăng ký với giao diện hiện đại, hỗ trợ khôi phục mật khẩu qua OTP.
