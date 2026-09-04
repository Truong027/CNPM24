# 🗄️ Hướng Dẫn Cài Đặt MySQL

## 1️⃣ Cài Đặt MySQL Server

### Trên Windows:
- Tải MySQL Community Server từ: https://dev.mysql.com/downloads/mysql/
- Chọn phiên bản mới nhất (hiện tại 8.0.x)
- Cài đặt và ghi nhớ:
  - **Root Password**: Đặt mật khẩu cho tài khoản root
  - **MySQL Server Instance Name**: Để mặc định hoặc đặt tên
  - **Port**: 3306 (mặc định)

### Trên macOS (với Homebrew):
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

### Trên Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo mysql_secure_installation
```

## 2️⃣ Kiểm Tra Kết Nối MySQL

Mở Command Prompt/Terminal và chạy:
```bash
mysql -u root -p
```

Nhập mật khẩu mà bạn đã đặt. Nếu thấy `mysql>`, kết nối thành công ✅

## 3️⃣ Cấu Hình Kết Nối (Cực Kỳ Quan Trọng)

Mở file `database.py` và cập nhật:

```python
MYSQL_CONFIG = {
    'host': 'localhost',           # Nếu MySQL trên máy này: localhost
    'user': 'root',                # Tên đăng nhập (mặc định: root)
    'password': 'your_password',   # ⚠️ THAY ĐỔI THÀNH MẬT KHẨU CỦA BẠN
    'database': 'bien_so_xe',      # Tên database (tự động tạo)
    'port': 3306,                  # Cổng (mặc định 3306)
    'autocommit': True
}
```

### Ví dụ Cấu Hình Khác Nhau:

**Nếu bạn tạo tài khoản MySQL mới:**
```sql
mysql -u root -p
mysql> CREATE USER 'bien_user'@'localhost' IDENTIFIED BY 'bien123456';
mysql> GRANT ALL PRIVILEGES ON bien_so_xe.* TO 'bien_user'@'localhost';
mysql> FLUSH PRIVILEGES;
```

Sau đó trong `database.py`:
```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'bien_user',          # ← Tài khoản mới
    'password': 'bien123456',     # ← Mật khẩu của tài khoản mới
    'database': 'bien_so_xe',
    'port': 3306,
    'autocommit': True
}
```

## 4️⃣ Khởi Tạo Database

Chạy Python script để tạo database:

```bash
python database.py
```

Bạn sẽ thấy:
```
✅ Database 'bien_so_xe' đã được tạo/kiểm tra.
✅ Bảng 'plates' đã được khởi tạo thành công.
```

## 5️⃣ Kiểm Tra Database Đã Tạo

Trong MySQL CLI:
```sql
mysql -u root -p
mysql> USE bien_so_xe;
mysql> SHOW TABLES;
mysql> DESC plates;
```

Bạn sẽ thấy bảng `plates` với các cột:
- `id` (INT, AUTO_INCREMENT)
- `plate_text` (VARCHAR)
- `timestamp` (DATETIME)

## 6️⃣ Chạy App

```bash
python app.py
```

App sẽ tự động kết nối MySQL và lưu biển số nhận diện được.

---

## ⚠️ Gặp Lỗi? Khắc Phục:

### "Access denied for user 'root'@'localhost'"
→ Kiểm tra lại mật khẩu trong `database.py`

### "Can't connect to MySQL server"
→ Kiểm tra MySQL có chạy không:
- Windows: Mở Services, tìm "MySQL80" (hoặc tương tự), chắc chắn Running
- Linux: `sudo systemctl status mysql`
- macOS: `brew services list`

### "Table already exists"
→ Bình thường, database.py sẽ tự bỏ qua nếu bảng đã tồn tại

### Module 'mysql.connector' not found
→ Chạy: `pip install mysql-connector-python`

---

## 📊 Xem Dữ Liệu Biển Số

Trong MySQL CLI:
```sql
USE bien_so_xe;
SELECT * FROM plates ORDER BY timestamp DESC LIMIT 10;
```

Xem tất cả biển số đã nhận diện! 📸
