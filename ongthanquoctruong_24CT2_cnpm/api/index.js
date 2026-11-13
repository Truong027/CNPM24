// ==============================================================================
// VERCEL SERVERLESS API ENGINE FOR PARKING AI (EXTENDED)
// Phục vụ đầy đủ 100% tất cả các endpoints cho Resident & Admin Dashboard
// ==============================================================================

let mockStats = {
  total_slots: 100,
  available_slots: 94,
  occupied_slots: 6,
  occupancy_rate: 6.0,
  ham_b1: { total: 50, available: 46, occupied: 4, pct: 8.0 },
  ham_b2: { total: 50, available: 48, occupied: 2, pct: 4.0 },
  total_vehicles: 116,
  total_plates: 42,
  total_detections: 363,
  avg_confidence: 98.5,
  total_sessions: 363,
  active_parked: 6,
  peak_hours: [
    { hour_label: "07h", count: 18, height_pct: 40 },
    { hour_label: "08h", count: 42, height_pct: 95 },
    { hour_label: "11h", count: 26, height_pct: 58 },
    { hour_label: "14h", count: 38, height_pct: 85 },
    { hour_label: "17h", count: 45, height_pct: 100 },
    { hour_label: "19h", count: 22, height_pct: 50 }
  ],
  recent_sessions: [
    { plate_text: "30F-123.45", status: "Parked", status_label: "Đang trong bãi", time_str: "09:30 05/11" },
    { plate_text: "29A-678.90", status: "Completed", status_label: "Đã hoàn tất", time_str: "14:15 04/11" }
  ]
};

let mockTransfers = [
  {
    id: 1,
    MaDon: "DON_1793845989451",
    BienSo: "30F-123.45",
    plate_text: "30F-123.45",
    vehicle_type: "Ô tô con",
    from_owner: "Lê Văn Cư Dân",
    HoTenNguoiChuyen: "Lê Văn Cư Dân",
    from_apartment: "A-1205",
    MaCanHoChuyen: "A-1205",
    from_phone: "0901234567",
    to_owner: "Trần Thị Cư Dân",
    HoTenNguoiNhan: "Trần Thị Cư Dân",
    to_apartment: "A-1206",
    MaCanHoNhan: "A-1206",
    to_phone: "0907654321",
    created_at: "05/11/2026 09:33",
    NgayGui: "05/11/2026 09:33",
    status: "Approved",
    TrangThai: "Approved",
    status_label: "Đã duyệt",
    NguoiDuyet: "admin",
    note: "Ban Quản Trị đã duyệt chuyển nhượng theo quy định",
    GhiChu: "Ban Quản Trị đã duyệt chuyển nhượng theo quy định",
    HinhAnhDon: ""
  },
  {
    id: 2,
    MaDon: "DON_1793845989867",
    BienSo: "30F-123.45",
    plate_text: "30F-123.45",
    vehicle_type: "Ô tô con",
    from_owner: "Trần Thị Cư Dân",
    HoTenNguoiChuyen: "Trần Thị Cư Dân",
    from_apartment: "A-1206",
    MaCanHoChuyen: "A-1206",
    from_phone: "0907654321",
    to_owner: "Lê Văn Cư Dân",
    HoTenNguoiNhan: "Lê Văn Cư Dân",
    to_apartment: "A-1205",
    MaCanHoNhan: "A-1205",
    to_phone: "0901234567",
    created_at: "05/11/2026 09:33",
    NgayGui: "05/11/2026 09:33",
    status: "Pending",
    TrangThai: "Pending",
    status_label: "Chờ duyệt",
    NguoiDuyet: "---",
    note: "Hồ sơ chuyển giao quyền sở hữu xe",
    GhiChu: "Hồ sơ chuyển giao quyền sở hữu xe",
    HinhAnhDon: ""
  }
];

let mockUsers = [
  {
    id: 1,
    phone: "0900000001",
    username: "admin",
    full_name: "Ban Quản Trị / Admin",
    email: "admin@system.com",
    role: "Admin",
    status: "Active",
    is_active: 1,
    apartment: "",
    shift: "Văn phòng BQT Tầng 1",
    created_at: "01/10/2026"
  },
  {
    id: 7,
    phone: "0912345678",
    username: "baove1",
    full_name: "Nguyễn Văn An (Bảo vệ)",
    email: "an.nguyen@security.com",
    role: "Operator",
    status: "Active",
    is_active: 1,
    apartment: "",
    shift: "Ca Sáng (06:00 - 14:00)",
    created_at: "28/08/2026"
  },
  {
    id: 8,
    phone: "0923456789",
    username: "baove2",
    full_name: "Trần Văn Bình (Bảo vệ)",
    email: "binh.tran@security.com",
    role: "Operator",
    status: "Active",
    is_active: 1,
    apartment: "",
    shift: "Ca Chiều (14:00 - 22:00)",
    created_at: "28/08/2026"
  },
  {
    id: 27,
    phone: "0901234567",
    username: "cudan1",
    full_name: "Lê Văn Cư Dân",
    email: "cudan1@resident.com",
    role: "Resident",
    status: "Active",
    is_active: 1,
    apartment: "A-1205",
    shift: "",
    created_at: "05/11/2026"
  },
  {
    id: 28,
    phone: "0907654321",
    username: "cudan2",
    full_name: "Trần Thị Cư Dân",
    email: "cudan2@resident.com",
    role: "Resident",
    status: "Active",
    is_active: 1,
    apartment: "A-1206",
    shift: "",
    created_at: "05/11/2026"
  }
];

let mockVehicles = [
  { id: 1, plate_text: "30F-123.45", vehicle_type: "Ô tô con", owner_name: "Lê Văn Cư Dân", apartment: "A-1205", slot_code: "B1-A01", status: "Hoạt động", color: "Trắng" },
  { id: 2, plate_text: "29A-678.90", vehicle_type: "Ô tô con", owner_name: "Trần Thị Cư Dân", apartment: "A-1206", slot_code: "B1-A02", status: "Hoạt động", color: "Đen" },
  { id: 3, plate_text: "51F-889.99", vehicle_type: "Ô tô con", owner_name: "Nguyễn Văn An", apartment: "A-1207", slot_code: "B1-A03", status: "Hoạt động", color: "Xám" }
];

let mockSessions = [
  { id: 1, plate_text: "30F-123.45", vehicle_type: "Ô tô con", owner_name: "Lê Văn Cư Dân", apartment: "A-1205", slot_code: "B1-A01", check_in: "05/11/2026 08:30", check_out: null, status: "Parked", fee: "0 đ (Vé tháng)" },
  { id: 2, plate_text: "29A-678.90", vehicle_type: "Ô tô con", owner_name: "Trần Thị Cư Dân", apartment: "A-1206", slot_code: "B1-A02", check_in: "04/11/2026 14:15", check_out: "04/11/2026 18:20", status: "Completed", fee: "0 đ (Vé tháng)" }
];

async function getRequestBody(req) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string" && req.body.length > 0) {
    try { return JSON.parse(req.body); } catch (_) {}
  }
  return new Promise((resolve) => {
    let data = "";
    req.on("data", chunk => { data += chunk; });
    req.on("end", () => {
      try { resolve(JSON.parse(data)); } catch (_) { resolve({}); }
    });
  });
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

  if (req.method === "OPTIONS") {
    res.status(200).end();
    return;
  }

  let pathname = "";
  if (req.query && req.query.path) {
    pathname = "/api/" + req.query.path;
  } else if (req.query && req.query.slug) {
    const slugParts = Array.isArray(req.query.slug) ? req.query.slug : [req.query.slug];
    pathname = "/api/" + slugParts.join("/");
  } else {
    const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
    pathname = url.pathname;
    if (!pathname.startsWith("/api")) pathname = "/api" + pathname;
  }
  pathname = pathname.split("?")[0].replace(/\/+$/, "");

  // 1. PUBLIC DASHBOARD
  if (pathname === "/api/public/dashboard" || pathname === "/api/public/stats") {
    return res.status(200).json({ success: true, stats: mockStats });
  }

  // 2. AUTHENTICATION
  if (pathname === "/api/login" && req.method === "POST") {
    const body = await getRequestBody(req);
    const phone = (body.phone || body.username || "").trim();
    const password = body.password || "";

    if (!phone || !password) {
      return res.status(400).json({ error: "Vui lòng nhập số điện thoại và mật khẩu" });
    }

    let role = "Admin";
    let fullName = "Ban Quản Trị / Admin";
    let redirectUrl = "/";
    let username = "admin";

    if (phone === "0901234567" || phone === "cudan1") {
      role = "Resident";
      fullName = "Lê Văn Cư Dân";
      username = "cudan1";
      redirectUrl = "/resident-dashboard";
    } else if (phone === "0907654321" || phone === "cudan2") {
      role = "Resident";
      fullName = "Trần Thị Cư Dân";
      username = "cudan2";
      redirectUrl = "/resident-dashboard";
    } else if (phone === "0912345678" || phone === "baove1") {
      role = "Operator";
      fullName = "Nguyễn Văn An (Bảo vệ)";
      username = "baove1";
      redirectUrl = "/operations-dashboard";
    } else if (phone === "0923456789" || phone === "baove2") {
      role = "Operator";
      fullName = "Trần Văn Bình (Bảo vệ)";
      username = "baove2";
      redirectUrl = "/operations-dashboard";
    }

    const userObj = {
      id: 1,
      username: username,
      full_name: fullName,
      phone: phone,
      role: role,
      email: `${username}@parking.vn`
    };

    res.setHeader("Set-Cookie", `auth_user=${encodeURIComponent(JSON.stringify(userObj))}; Path=/; HttpOnly; SameSite=Lax`);
    return res.status(200).json({ success: true, user: userObj, redirect: redirectUrl });
  }

  if (pathname === "/api/session") {
    return res.status(200).json({
      authenticated: true,
      user: {
        id: 1,
        username: "admin",
        full_name: "Ban Quản Trị / Admin",
        role: "Admin",
        email: "admin@system.com"
      }
    });
  }

  if (pathname === "/api/logout") {
    res.setHeader("Set-Cookie", "auth_user=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT");
    return res.status(200).json({ success: true, message: "Đã đăng xuất" });
  }

  if (pathname === "/api/register" && req.method === "POST") {
    return res.status(200).json({
      success: true,
      message: "Đăng ký tài khoản thành công!",
      redirect: "/login"
    });
  }

  // 3. RESIDENT PROFILE & VEHICLES
  if (pathname === "/api/resident/profile") {
    return res.status(200).json({
      success: true,
      user: {
        id: 27,
        username: "cudan1",
        full_name: "Lê Văn Cư Dân",
        phone: "0901234567",
        email: "cudan1@resident.com",
        apartment: "A-1205",
        role: "Resident"
      }
    });
  }

  if (pathname === "/api/resident/vehicles") {
    return res.status(200).json({
      success: true,
      vehicles: mockVehicles.filter(v => v.apartment === "A-1205")
    });
  }

  if (pathname === "/api/resident/transfer_requests" || pathname === "/api/resident/transfer-request" || pathname === "/api/resident/transfer_vehicle") {
    if (req.method === "POST") {
      const body = await getRequestBody(req);
      const newId = `DON_${Date.now()}`;
      const newTransfer = {
        id: mockTransfers.length + 1,
        MaDon: newId,
        plate_text: body.plate_text || "30F-123.45",
        BienSo: body.plate_text || "30F-123.45",
        vehicle_type: "Ô tô con",
        from_owner: "Lê Văn Cư Dân",
        HoTenNguoiChuyen: "Lê Văn Cư Dân",
        from_phone: "0901234567",
        from_apartment: "A-1205",
        MaCanHoChuyen: "A-1205",
        to_owner: body.to_owner || "Trần Thị Cư Dân",
        HoTenNguoiNhan: body.to_owner || "Trần Thị Cư Dân",
        to_phone: body.to_phone || "0907654321",
        to_apartment: body.to_apartment || "A-1206",
        MaCanHoNhan: body.to_apartment || "A-1206",
        created_at: new Date().toLocaleString("vi-VN"),
        NgayGui: new Date().toLocaleString("vi-VN"),
        status: "Pending",
        TrangThai: "Pending",
        status_label: "Chờ duyệt",
        NguoiDuyet: "---",
        note: body.note || "Đơn chuyển nhượng quyền sử dụng xe",
        GhiChu: body.note || "Đơn chuyển nhượng quyền sử dụng xe",
        HinhAnhDon: body.document_image || body.hinh_anh_don || ""
      };
      mockTransfers.unshift(newTransfer);
      return res.status(200).json({ success: true, message: "Đã gửi đơn chuyển nhượng thành công!", transfer: newTransfer, request: newTransfer });
    }
    return res.status(200).json(mockTransfers);
  }

  if (pathname === "/api/resident/history") {
    return res.status(200).json({
      success: true,
      history: [
        { plate_text: "30F-123.45", check_in: "08:15 05/11", check_out: "Đang đỗ", gate: "Cổng Vào #1", status: "Parked", fee: "0 đ (Vé tháng)" },
        { plate_text: "30F-123.45", check_in: "07:30 04/11", check_out: "18:45 04/11", gate: "Cổng Ra #1", status: "Completed", fee: "0 đ (Vé tháng)" }
      ]
    });
  }

  // 4. ADMIN TRANSFERS & USERS
  if (pathname === "/api/admin/transfers" || pathname === "/api/admin/transfer_requests" || pathname === "/api/admin/transfer-requests") {
    return res.status(200).json(mockTransfers);
  }

  if (pathname.includes("/update_doc")) {
    const body = await getRequestBody(req);
    const urlParts = pathname.split('/');
    const docIdx = urlParts.indexOf('update_doc');
    const pathId = docIdx > 0 ? urlParts[docIdx - 1] : null;
    const target = mockTransfers.find(t => t.id == pathId || t.MaDon == pathId);
    if (target) {
      target.HinhAnhDon = body.document_image || "";
    }
    return res.status(200).json({ success: true, message: "Đã cập nhật ảnh đơn thành công!" });
  }

  if (pathname.includes("/action") || pathname === "/api/admin/transfers/approve" || pathname === "/api/admin/transfers/reject") {
    const body = await getRequestBody(req);
    const urlParts = pathname.split('/');
    const actionIdx = urlParts.indexOf('action');
    const pathId = actionIdx > 0 ? urlParts[actionIdx - 1] : null;
    const id = body.id || body.request_id || pathId;
    const action = body.action || (pathname.includes("approve") ? "approve" : "reject");
    const target = mockTransfers.find(t => t.id == id || t.MaDon == id);
    if (target) {
      target.note = body.note || target.note;
      target.GhiChu = body.note || target.GhiChu;
      target.NguoiDuyet = "admin";
      if (action === "approve") {
        target.status = "Approved";
        target.TrangThai = "Approved";
        target.status_label = "Đã duyệt";
      } else {
        target.status = "Rejected";
        target.TrangThai = "Rejected";
        target.status_label = "Đã từ chối";
      }
    }
    return res.status(200).json({ success: true, message: `Thao tác thành công trên đơn #${id}!`, transfer: target });
  }

  if (pathname === "/api/admin/users") {
    return res.status(200).json(mockUsers);
  }

  if (pathname === "/api/admin/residents/create" && req.method === "POST") {
    const body = await getRequestBody(req);
    const newUser = {
      id: mockUsers.length + 10,
      username: body.username || `cudan_${Date.now()}`,
      phone: body.phone || body.so_dien_thoai || "0900000000",
      full_name: body.full_name || body.ho_ten || "Cư Dân Mới",
      email: body.email || "",
      apartment: body.apartment || body.ma_can_ho || "A-0000",
      role: "Resident",
      status: "Active",
      is_active: 1,
      created_at: new Date().toLocaleDateString("vi-VN")
    };
    mockUsers.push(newUser);
    return res.status(200).json({ success: true, message: "Tạo tài khoản cư dân thành công!", user: newUser });
  }

  if (pathname === "/api/admin/guards/create" && req.method === "POST") {
    const body = await getRequestBody(req);
    const newUser = {
      id: mockUsers.length + 10,
      username: body.username || `baove_${Date.now()}`,
      phone: body.phone || body.so_dien_thoai || "0900000000",
      full_name: body.full_name || body.ho_ten || "Bảo Vệ Mới",
      email: body.email || "",
      shift: body.shift || body.ca_truc || "Ca Sáng",
      role: "Operator",
      status: "Active",
      is_active: 1,
      created_at: new Date().toLocaleDateString("vi-VN")
    };
    mockUsers.push(newUser);
    return res.status(200).json({ success: true, message: "Thêm tài khoản bảo vệ thành công!", user: newUser });
  }

  if (pathname === "/api/admin/users/update") {
    const body = await getRequestBody(req);
    const phone = body.phone || body.so_dien_thoai;
    const user = mockUsers.find(u => u.phone === phone || u.username === body.username || u.id == body.id);
    if (user) {
      if (body.role) user.role = body.role;
      if (body.full_name) user.full_name = body.full_name;
      if (body.email) user.email = body.email;
    }
    return res.status(200).json({ success: true, message: "Cập nhật thông tin thành công!", user });
  }

  if (pathname === "/api/admin/users/reset_password") {
    return res.status(200).json({ success: true, message: "Cấp lại mật khẩu thành công! Mật khẩu mới là 123456" });
  }

  if (pathname === "/api/admin/users/toggle_status") {
    const body = await getRequestBody(req);
    const user = mockUsers.find(u => u.id == body.user_id || u.phone === body.phone);
    if (user) {
      user.is_active = user.is_active ? 0 : 1;
      user.status = user.is_active ? "Active" : "Locked";
    }
    return res.status(200).json({ success: true, message: "Đã đổi trạng thái tài khoản thành công!", user });
  }

  if (pathname.startsWith("/api/admin/users/") && req.method === "DELETE") {
    const parts = pathname.split('/');
    const deleteId = parts[parts.length - 1];
    mockUsers = mockUsers.filter(u => u.id != deleteId && u.phone != deleteId && u.username != deleteId);
    return res.status(200).json({ success: true, message: "Đã xóa tài khoản thành công!" });
  }

  // 5. PARKING MAP (CINEMA SLOTS)
  if (pathname === "/api/parking/map") {
    const slots = [];
    // Hầm B1
    for (let i = 1; i <= 50; i++) {
      const dayLetter = String.fromCharCode(65 + Math.floor((i - 1) / 10)); // A, B, C, D, E
      const numInRow = ((i - 1) % 10) + 1;
      const code = `B1-${dayLetter}${numInRow < 10 ? '0' + numInRow : numInRow}`;
      const isOccupied = (i === 1 || i === 2 || i === 3);
      slots.push({
        ma_cho_do: code,
        ten_cho_do: `Vị trí ${dayLetter}-${numInRow} (Hầm B1)`,
        khu_vuc: "Ham_B1",
        day: dayLetter,
        so_thu_tu: numInRow,
        loai_cho_do: "Ô tô con",
        trang_thai: isOccupied ? "DaDat" : "Trong",
        bien_so_xe: (i === 1) ? "30F-123.45" : ((i === 2) ? "29A-678.90" : ((i === 3) ? "51F-889.99" : null)),
        ten_chu_xe: (i === 1) ? "Lê Văn Cư Dân" : ((i === 2) ? "Trần Thị Cư Dân" : ((i === 3) ? "Nguyễn Văn An" : null)),
        ma_can_ho: (i === 1) ? "A-1205" : ((i === 2) ? "A-1206" : ((i === 3) ? "A-1207" : null))
      });
    }
    // Hầm B2
    for (let i = 1; i <= 50; i++) {
      const dayLetter = String.fromCharCode(65 + Math.floor((i - 1) / 10));
      const numInRow = ((i - 1) % 10) + 1;
      const code = `B2-${dayLetter}${numInRow < 10 ? '0' + numInRow : numInRow}`;
      slots.push({
        ma_cho_do: code,
        ten_cho_do: `Vị trí ${dayLetter}-${numInRow} (Hầm B2)`,
        khu_vuc: "Ham_B2",
        day: dayLetter,
        so_thu_tu: numInRow,
        loai_cho_do: "Ô tô con",
        trang_thai: "Trong",
        bien_so_xe: null,
        ten_chu_xe: null,
        ma_can_ho: null
      });
    }
    return res.status(200).json({ success: true, slots: slots, total: 100 });
  }

  // 6. SESSIONS & VEHICLES
  if (pathname === "/api/parking/sessions") {
    return res.status(200).json(mockSessions);
  }

  if (pathname === "/api/vehicles") {
    return res.status(200).json(mockVehicles);
  }

  if (pathname === "/get_plates" || pathname === "/api/get_plates") {
    return res.status(200).json([
      { id: 1, plate_text: "30F-123.45", vehicle_type: "Ô tô con", confidence: 0.988, timestamp: new Date().toISOString(), gate: "Cổng Vào #1" },
      { id: 2, plate_text: "29A-678.90", vehicle_type: "Ô tô con", confidence: 0.975, timestamp: new Date().toISOString(), gate: "Cổng Ra #1" }
    ]);
  }

  // 7. ANALYTICS
  if (pathname === "/api/summary") {
    return res.status(200).json({
      total_vehicles: 116,
      parked_vehicles: 6,
      today_revenue: "1.450.000 đ",
      total_slots: 100,
      free_slots: 94
    });
  }

  if (pathname === "/api/analytics/revenue") {
    return res.status(200).json([
      { date_revenue: "01/11", total_fee: 1200000 },
      { date_revenue: "02/11", total_fee: 1450000 },
      { date_revenue: "03/11", total_fee: 1300000 },
      { date_revenue: "04/11", total_fee: 1600000 },
      { date_revenue: "05/11", total_fee: 1850000 }
    ]);
  }

  if (pathname === "/api/analytics/peak" || pathname === "/api/analytics/peak-hours") {
    return res.status(200).json([
      { scan_hour: 7, scan_count: 24 },
      { scan_hour: 8, scan_count: 52 },
      { scan_hour: 11, scan_count: 31 },
      { scan_hour: 14, scan_count: 40 },
      { scan_hour: 17, scan_count: 65 },
      { scan_hour: 19, scan_count: 28 }
    ]);
  }

  if (pathname.startsWith("/api/guard/")) {
    return res.status(200).json({
      success: true,
      mode: "AI_AUTO",
      plate: "30F-123.45",
      event: { plate_text: "30F-123.45", gate: "Cổng Vào #1", time: new Date().toLocaleTimeString("vi-VN") }
    });
  }

  return res.status(200).json({ success: true, message: "Parking AI Serverless API Active" });
}
