// ==============================================================================
// FIGMA PLUGIN SCRIPT: Parking AI - Admin Wireframe & Prototype Generator
// Bao gồm trọn bộ 8 màn hình phác thảo chuẩn Wireframe cho 2 chức năng Admin:
//
// [NHÓM 1] PHÊ DUYỆT ĐƠN CHUYỂN NHƯỢNG XE (4 Screens):
//   - Frame A1: Danh sách đơn chờ duyệt (Transfer List - Chờ duyệt)
//   - Frame A2: Modal xác nhận phê duyệt (Modal Approve Prompt)
//   - Frame A3: Modal từ chối đơn chuyển nhượng (Modal Reject Prompt)
//   - Frame A4: Trạng thái đã duyệt thành công + Toast thông báo (Approved Success)
//
// [NHÓM 2] QUẢN LÝ VÀ PHÂN QUYỀN NGƯỜI DÙNG (4 Screens):
//   - Frame B1: Danh sách tài khoản người dùng & Thống kê Role (Users List Overview)
//   - Frame B2: Modal chỉnh sửa thông tin & Phân quyền Role (#editUserModal)
//   - Frame B3: Trạng thái báo lỗi Validation mật khẩu/SĐT (Validation Error State)
//   - Frame B4: Trạng thái cập nhật thành công + Toast + Cập nhật Role (Updated Success)
//
// [NHÓM 3] CƯ DÂN (Tùy chọn qua menu 'generate_resident'):
//   - Public Dashboard, Login, Register
// ==============================================================================

const fontRegular = { family: "Inter", style: "Regular" };
const fontBold = { family: "Inter", style: "Bold" };

// Bảng màu phác thảo Wireframe đồng bộ theo chuẩn bản vẽ thiết kế bài giảng
const colors = {
  paperBg: { r: 0.965, g: 0.855, b: 0.855 },    // Màu nền hồng phấn/da nhạt bảng vẽ (#F6DBDB)
  boxFill: { r: 0.985, g: 0.920, b: 0.920 },    // Nền ô phác thảo nhẹ (#FAF0F0)
  whiteFill: { r: 1.000, g: 1.000, b: 1.000 },  // Nền trắng cho modal, bảng (#FFFFFF)
  borderBlack: { r: 0.10, g: 0.10, b: 0.12 },   // Viền đen sắc nét của phác thảo (#1A1A1E)
  borderMuted: { r: 0.50, g: 0.45, b: 0.45 },   // Viền phân cách mờ
  textBlack: { r: 0.08, g: 0.08, b: 0.10 },     // Chữ đen đậm
  textMuted: { r: 0.40, g: 0.40, b: 0.45 },     // Chữ phụ ghi chú
  markerRed: { r: 0.88, g: 0.18, b: 0.18 },     // Màu đỏ nét bút lông / ghi chú prototype
  badgeGreenBg: { r: 0.86, g: 0.95, b: 0.86 },  // Badge xanh lá nhạt (Thành công / Đã duyệt)
  badgeGreenText: { r: 0.10, g: 0.55, b: 0.18 },
  badgeYellowBg: { r: 0.99, g: 0.94, b: 0.80 }, // Badge vàng chờ duyệt
  badgeYellowText: { r: 0.65, g: 0.45, b: 0.05 },
  badgeBlueBg: { r: 0.88, g: 0.92, b: 0.99 },   // Badge xanh dương phân quyền
  badgeBlueText: { r: 0.12, g: 0.35, b: 0.75 },
  badgeRedBg: { r: 0.99, g: 0.88, b: 0.88 },    // Badge đỏ từ chối / khóa
  badgeRedText: { r: 0.75, g: 0.12, b: 0.12 },
  modalBackdrop: { r: 0.10, g: 0.10, b: 0.12 }  // Lớp phủ mờ nền modal
};

function solidPaint(color, opacity = 1) {
  return [{ type: "SOLID", color, opacity }];
}

// Hàm tiện ích tạo Frame khối hộp
function createBox(parent, options = {}) {
  const box = figma.createFrame();
  box.name = options.name || "Box";
  box.x = options.x || 0;
  box.y = options.y || 0;
  box.resize(options.width || 100, options.height || 100);
  box.fills = options.fill !== undefined ? (options.fill ? solidPaint(options.fill, options.opacity || 1) : []) : solidPaint(colors.boxFill);
  if (options.stroke !== null) {
    box.strokes = solidPaint(options.stroke || colors.borderBlack);
    box.strokeWeight = options.strokeWeight !== undefined ? options.strokeWeight : 1.5;
  } else {
    box.strokes = [];
  }
  box.cornerRadius = options.cornerRadius || 0;
  box.clipsContent = true;
  parent.appendChild(box);
  return box;
}

// Hàm tiện ích tạo Text
function createText(parent, options = {}) {
  const t = figma.createText();
  t.name = options.name || "Text";
  t.fontName = options.bold ? fontBold : fontRegular;
  t.fontSize = options.size || 13;
  t.characters = options.characters || "";
  t.x = options.x || 0;
  t.y = options.y || 0;
  t.fills = solidPaint(options.color || colors.textBlack);
  t.textAlignHorizontal = options.align || "LEFT";
  t.textAlignVertical = "CENTER";
  if (options.width) {
    t.resize(options.width, options.height || t.height);
    t.textAutoResize = "HEIGHT";
  }
  parent.appendChild(t);
  return t;
}

// Hàm tiện ích tạo Badge trạng thái
function createBadge(parent, text, x, y, width, height, type = "yellow") {
  let bg = colors.badgeYellowBg;
  let fg = colors.badgeYellowText;
  if (type === "green") {
    bg = colors.badgeGreenBg;
    fg = colors.badgeGreenText;
  } else if (type === "blue") {
    bg = colors.badgeBlueBg;
    fg = colors.badgeBlueText;
  } else if (type === "red") {
    bg = colors.badgeRedBg;
    fg = colors.badgeRedText;
  }

  const badge = createBox(parent, {
    name: `Badge_${text}`,
    x: x, y: y,
    width: width, height: height,
    fill: bg,
    stroke: fg,
    strokeWeight: 1
  });
  createText(badge, {
    characters: text,
    x: 0, y: Math.floor((height - 14) / 2),
    width: width,
    size: 11, bold: true,
    color: fg, align: "CENTER"
  });
  return badge;
}

// Hàm tiện ích tạo Nút Bấm phác thảo
function createButton(parent, text, x, y, width, height, options = {}) {
  const btn = createBox(parent, {
    name: `Btn_${text}`,
    x: x, y: y,
    width: width, height: height,
    fill: options.fill || colors.boxFill,
    stroke: options.stroke || colors.borderBlack,
    strokeWeight: options.strokeWeight || 1.5
  });
  createText(btn, {
    characters: text,
    x: 0, y: Math.floor((height - (options.size || 12)) / 2),
    width: width,
    size: options.size || 12,
    bold: options.bold !== undefined ? options.bold : true,
    color: options.textColor || colors.textBlack,
    align: "CENTER"
  });
  return btn;
}

// Hàm ghi chú Marker Đỏ hỗ trợ làm Prototype
function createMarkerNote(parent, text, x, y, width = 360, height = 36) {
  const noteBox = createBox(parent, {
    name: "Prototype_Marker_Note",
    x: x, y: y,
    width: width, height: height,
    fill: colors.boxFill,
    stroke: colors.markerRed,
    strokeWeight: 2
  });
  createText(noteBox, {
    characters: text,
    x: 10, y: Math.floor((height - 12) / 2),
    width: width - 20,
    size: 11, bold: true,
    color: colors.markerRed
  });
  return noteBox;
}

// Header chung cho các màn hình Admin Desktop
function renderAdminHeader(master, currentTitle, currentTab = "transfers") {
  const HEADER_W = 1050;

  // Thanh Top Bar
  const topBar = createBox(master, {
    name: "Admin_Header_TopBar",
    x: 15, y: 15, width: HEADER_W, height: 50,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(topBar, { characters: "PARKING AI - BAN QUẢN TRỊ ADMIN", x: 16, y: 10, size: 15, bold: true });
  createText(topBar, { characters: `Hệ Thống Quản Trị  >  ${currentTitle}`, x: 16, y: 30, size: 10, color: colors.textMuted });

  // Thông tin Admin đăng nhập bên phải
  const adminBadge = createBox(topBar, {
    name: "Admin_Profile_Pill",
    x: 770, y: 9, width: 265, height: 32,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1
  });
  createText(adminBadge, {
    characters: "👤 Admin BQT (0988888888)  |  [ Đăng Xuất ]",
    x: 0, y: 8, width: 265, size: 11, bold: true, align: "CENTER"
  });

  // Thanh Menu Điều Hướng Tabs Admin
  const navBar = createBox(master, {
    name: "Admin_Nav_Tabs",
    x: 15, y: 65, width: HEADER_W, height: 38,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });

  const tabWidth = 205;
  const tabs = [
    { id: "overview", label: "📊 Tổng Quan Bãi Xe" },
    { id: "transfers", label: "📋 Duyệt Chuyển Nhượng (03)" },
    { id: "users", label: "👥 Quản Lý & Phân Quyền" },
    { id: "shifts", label: "🛡️ Ca Trực Bảo Vệ" },
    { id: "settings", label: "⚙️ Cài Đặt Hệ Thống" }
  ];

  tabs.forEach((tab, index) => {
    const isActive = tab.id === currentTab;
    const tabBox = createBox(navBar, {
      name: `Tab_${tab.id}`,
      x: index * (tabWidth + 4) + 4, y: 4,
      width: tabWidth, height: 30,
      fill: isActive ? colors.paperBg : colors.boxFill,
      stroke: isActive ? colors.borderBlack : colors.borderMuted,
      strokeWeight: isActive ? 2 : 1
    });
    createText(tabBox, {
      characters: tab.label,
      x: 0, y: 8, width: tabWidth,
      size: 11, bold: isActive,
      color: isActive ? colors.textBlack : colors.textMuted,
      align: "CENTER"
    });
  });
}

// ==============================================================================
// [NHÓM 1] PHÊ DUYỆT ĐƠN CHUYỂN NHƯỢNG XE (ADMIN)
// ==============================================================================

// Frame A1 & A4: Danh sách đơn chuyển nhượng (A1: Chưa duyệt, A4: Đã duyệt + Toast)
function buildTransferListFrame(posX, posY, isSuccessState = false) {
  const master = createBox(figma.currentPage, {
    name: isSuccessState
      ? "Wireframe A4: Transfer List (State: Đã Duyệt Thành Công + Toast)"
      : "Wireframe A1: Transfer List (State: Chờ Duyệt - Click Duyệt/Từ Chối)",
    x: posX, y: posY,
    width: 1080, height: 680,
    fill: colors.paperBg,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  renderAdminHeader(master, "Quản Lý & Phê Duyệt Đơn Chuyển Nhượng Xe", "transfers");

  // TOAST THÔNG BÁO THÀNH CÔNG (Nếu là A4)
  if (isSuccessState) {
    const toastBox = createBox(master, {
      name: "Toast_Success_Approved",
      x: 15, y: 112, width: 1050, height: 40,
      fill: colors.badgeGreenBg,
      stroke: colors.badgeGreenText,
      strokeWeight: 2
    });
    createText(toastBox, {
      characters: "✅ PHÊ DUYỆT THÀNH CÔNG: Đơn #TRF-089 đã được chấp thuận! Quyền sở hữu xe 51F-889.99 đã cập nhật sang cư dân Trần Thị B (Căn 08.02).",
      x: 18, y: 12, size: 12, bold: true, color: colors.badgeGreenText
    });
    createMarkerNote(master, "👉 PROTOTYPE RESULT: Dòng 1 cập nhật [ĐÃ DUYỆT], Toast xanh hiển thị, CSDL accounts/vehicles cập nhật!", 15, 630, 1050, 36);
  } else {
    createMarkerNote(master, "👉 PROTOTYPE STEP 1: Click nút [ PHÊ DUYỆT ] ở dòng đầu tiên để kích hoạt Modal xác nhận (Screen A2)", 15, 630, 520, 36);
    createMarkerNote(master, "👉 LUỒNG PHỤ: Click nút [ TỪ CHỐI ] để mở Modal từ chối và nhập lý do (Screen A3)", 545, 630, 520, 36);
  }

  const contentTop = isSuccessState ? 160 : 115;

  // Thanh Bộ lọc & Thống kê
  const filterBox = createBox(master, {
    name: "Filter_Toolbar",
    x: 15, y: contentTop, width: 1050, height: 46,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });

  // Tabs lọc trạng thái
  const subTabs = [
    { text: "Tất Cả Đơn (33)", w: 120, active: false },
    { text: isSuccessState ? "Chờ Phê Duyệt (02)" : "Chờ Phê Duyệt (03)", w: 140, active: true },
    { text: isSuccessState ? "Đã Phê Duyệt (29)" : "Đã Phê Duyệt (28)", w: 140, active: false },
    { text: "Đã Từ Chối (02)", w: 120, active: false }
  ];
  let curTabX = 8;
  subTabs.forEach(st => {
    const stb = createBox(filterBox, {
      name: `SubTab_${st.text}`,
      x: curTabX, y: 7, width: st.w, height: 32,
      fill: st.active ? colors.paperBg : colors.boxFill,
      stroke: st.active ? colors.borderBlack : colors.borderMuted,
      strokeWeight: st.active ? 1.5 : 1
    });
    createText(stb, { characters: st.text, x: 0, y: 8, width: st.w, size: 11, bold: st.active, align: "CENTER" });
    curTabX += st.w + 6;
  });

  // Ô tìm kiếm bên phải
  const searchInput = createBox(filterBox, {
    name: "Search_Input",
    x: 690, y: 7, width: 345, height: 32,
    stroke: colors.borderBlack, strokeWeight: 1
  });
  createText(searchInput, { characters: "🔍 Tìm kiếm theo biển số, tên cư dân, số căn hộ...", x: 10, y: 8, size: 11, color: colors.textMuted });

  // BẢNG DỮ LIỆU ĐƠN CHUYỂN NHƯỢNG
  const tableY = contentTop + 54;
  const tableBox = createBox(master, {
    name: "Table_Transfers",
    x: 15, y: tableY, width: 1050, height: 370,
    fill: colors.whiteFill,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });

  // Hàng Tiêu Đề Bảng
  const thBox = createBox(tableBox, {
    name: "Table_Header",
    x: 0, y: 0, width: 1050, height: 38,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1
  });

  const columns = [
    { label: "MÃ ĐƠN", x: 12, w: 90 },
    { label: "BIỂN SỐ XE", x: 110, w: 120 },
    { label: "CƯ DÂN CHUYỂN (CHỦ CŨ)", x: 235, w: 180 },
    { label: "CƯ DÂN NHẬN (CHỦ MỚI)", x: 425, w: 180 },
    { label: "CHUYỂN CĂN HỘ", x: 615, w: 120 },
    { label: "NGÀY TẠO", x: 745, w: 95 },
    { label: "TRẠNG THÁI", x: 845, w: 105 },
    { label: "HÀNH ĐỘNG", x: 955, w: 90 }
  ];

  columns.forEach(col => {
    createText(thBox, { characters: col.label, x: col.x, y: 12, size: 10, bold: true });
  });

  // Dữ liệu dòng 1 (Trọng tâm kịch bản duyệt)
  const row1Y = 38;
  const r1 = createBox(tableBox, {
    name: "Row_1_TRF_089",
    x: 0, y: row1Y, width: 1050, height: 75,
    fill: isSuccessState ? colors.badgeGreenBg : colors.whiteFill,
    stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(r1, { characters: "TRF-089", x: 12, y: 28, size: 11, bold: true });
  createText(r1, { characters: "51F-889.99\n(Ô tô 4 chỗ)", x: 110, y: 20, size: 11, bold: true });
  createText(r1, { characters: "Nguyễn Văn A\nSĐT: 0901234567", x: 235, y: 20, size: 11 });
  createText(r1, { characters: "Trần Thị B\nSĐT: 0912345678", x: 425, y: 20, size: 11 });
  createText(r1, { characters: "Căn 12.04\n→ Căn 08.02", x: 615, y: 20, size: 11, bold: true });
  createText(r1, { characters: "15/10/2026\n09:30", x: 745, y: 20, size: 11, color: colors.textMuted });

  if (isSuccessState) {
    createBadge(r1, "ĐÃ DUYỆT", 845, 24, 95, 26, "green");
    createButton(r1, "Xem Chi Tiết", 950, 23, 90, 28, { fill: colors.boxFill, stroke: colors.borderBlack });
  } else {
    createBadge(r1, "CHỜ DUYỆT", 845, 24, 95, 26, "yellow");
    createButton(r1, "Phê Duyệt", 945, 12, 95, 25, { fill: colors.paperBg, stroke: colors.borderBlack, strokeWeight: 2 });
    createButton(r1, "Từ Chối", 945, 40, 95, 24, { fill: colors.boxFill, stroke: colors.markerRed, textColor: colors.markerRed });
  }

  // Dữ liệu dòng 2 (Chờ duyệt)
  const row2Y = 113;
  const r2 = createBox(tableBox, {
    name: "Row_2_TRF_088",
    x: 0, y: row2Y, width: 1050, height: 75,
    fill: colors.whiteFill, stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(r2, { characters: "TRF-088", x: 12, y: 28, size: 11, bold: true });
  createText(r2, { characters: "29A-678.90\n(Xe máy SH)", x: 110, y: 20, size: 11, bold: true });
  createText(r2, { characters: "Lê Hoàng C\nSĐT: 0934567890", x: 235, y: 20, size: 11 });
  createText(r2, { characters: "Phạm Minh D\nSĐT: 0945678901", x: 425, y: 20, size: 11 });
  createText(r2, { characters: "Căn 05.11\n→ Căn 05.11", x: 615, y: 20, size: 11 });
  createText(r2, { characters: "14/10/2026\n14:15", x: 745, y: 20, size: 11, color: colors.textMuted });
  createBadge(r2, "CHỜ DUYỆT", 845, 24, 95, 26, "yellow");
  createButton(r2, "Phê Duyệt", 945, 12, 95, 25, { fill: colors.boxFill, stroke: colors.borderBlack });
  createButton(r2, "Từ Chối", 945, 40, 95, 24, { fill: colors.boxFill, stroke: colors.markerRed, textColor: colors.markerRed });

  // Dữ liệu dòng 3 (Lịch sử đã hoàn tất)
  const row3Y = 188;
  const r3 = createBox(tableBox, {
    name: "Row_3_TRF_085",
    x: 0, y: row3Y, width: 1050, height: 75,
    fill: colors.whiteFill, stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(r3, { characters: "TRF-085", x: 12, y: 28, size: 11, bold: true });
  createText(r3, { characters: "30E-123.45\n(Ô tô Mazda)", x: 110, y: 20, size: 11, bold: true });
  createText(r3, { characters: "Hoàng Văn E\nSĐT: 0966778899", x: 235, y: 20, size: 11 });
  createText(r3, { characters: "Đỗ Thị G\nSĐT: 0977889900", x: 425, y: 20, size: 11 });
  createText(r3, { characters: "Căn 03.01\n→ Căn 09.05", x: 615, y: 20, size: 11 });
  createText(r3, { characters: "12/10/2026\n16:00", x: 745, y: 20, size: 11, color: colors.textMuted });
  createBadge(r3, "ĐÃ DUYỆT", 845, 24, 95, 26, "green");
  createButton(r3, "Xem Chi Tiết", 950, 23, 90, 28, { fill: colors.boxFill, stroke: colors.borderBlack });

  // Chân bảng phân trang
  const paginationBox = createBox(tableBox, {
    name: "Table_Pagination",
    x: 0, y: 325, width: 1050, height: 45,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1
  });
  createText(paginationBox, {
    characters: "Hiển thị 1 - 3 trong tổng số 33 yêu cầu chuyển nhượng",
    x: 15, y: 15, size: 11, color: colors.textMuted
  });
  createText(paginationBox, {
    characters: "Trang:  [ 1 ]   2   3   4   >   >>",
    x: 820, y: 15, size: 11, bold: true
  });

  return master;
}

// Frame A2: Modal Xác nhận Phê duyệt Đơn (Approve Modal)
function buildTransferApproveModalFrame(posX, posY) {
  const master = createBox(figma.currentPage, {
    name: "Wireframe A2: Modal Approve Prompt (Xác Nhận Duyệt Đơn Chuyển Nhượng)",
    x: posX, y: posY,
    width: 1080, height: 680,
    fill: colors.paperBg,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  // Nền mờ Backdrop thể hiện màn hình A1 phía sau
  const backdrop = createBox(master, {
    name: "Modal_Backdrop_Dimmed",
    x: 0, y: 0, width: 1080, height: 680,
    fill: colors.modalBackdrop,
    opacity: 0.45,
    stroke: null
  });

  // HỘP THOẠI MODAL PHÊ DUYỆT
  const MODAL_W = 600;
  const MODAL_H = 550;
  const modalBox = createBox(master, {
    name: "Dialog_Approve_Transfer",
    x: Math.floor((1080 - MODAL_W) / 2),
    y: Math.floor((680 - MODAL_H) / 2),
    width: MODAL_W, height: MODAL_H,
    fill: colors.whiteFill,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  // Modal Header
  const mHeader = createBox(modalBox, {
    name: "Modal_Header",
    x: 0, y: 0, width: MODAL_W, height: 48,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(mHeader, { characters: "XÁC NHẬN PHÊ DUYỆT ĐƠN CHUYỂN NHƯỢNG", x: 18, y: 14, size: 14, bold: true });
  createText(mHeader, { characters: "[ Đóng ✕ ]", x: 530, y: 14, size: 12, bold: true, color: colors.markerRed });

  // Khối thông tin chi tiết đơn TRF-089
  const detailBox = createBox(modalBox, {
    name: "Transfer_Summary_Card",
    x: 20, y: 64, width: 560, height: 195,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(detailBox, { characters: "THÔNG TIN HỒ SƠ CHUYỂN NHƯỢNG #TRF-089", x: 14, y: 12, size: 12, bold: true });

  const summaryRows = [
    { label: "Phương tiện:", val: "51F-889.99 (Ô tô 4 chỗ - Mercedes C200)" },
    { label: "Chủ hiện tại (Bên chuyển):", val: "Nguyễn Văn A · SĐT: 0901234567 · Căn hộ: 12.04" },
    { label: "Chủ mới (Bên nhận):", val: "Trần Thị B · SĐT: 0912345678 · Căn hộ: 08.02" },
    { label: "Kiểm tra hạn mức ô tô căn 08.02:", val: "HỢP LỆ (Hiện có 0/1 ô tô trong danh ngạch)" },
    { label: "Hồ sơ đính kèm:", val: "Đầy đủ: Hợp đồng mua bán / Giấy đăng ký xe hợp lệ" }
  ];

  summaryRows.forEach((row, i) => {
    createText(detailBox, { characters: `• ${row.label}`, x: 14, y: 36 + i * 31, size: 11, bold: true });
    createText(detailBox, { characters: row.val, x: 220, y: 36 + i * 31, size: 11, color: colors.textBlack });
  });

  // Textarea Ghi chú phê duyệt của BQT
  createText(modalBox, {
    characters: "Ghi chú phê duyệt của Ban Quản Trị (Lưu vào lịch sử hệ thống):",
    x: 20, y: 272, size: 11, bold: true
  });
  const noteInput = createBox(modalBox, {
    name: "Textarea_Approval_Note",
    x: 20, y: 294, width: 560, height: 75,
    fill: colors.whiteFill, stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(noteInput, {
    characters: "Ban Quản Trị đã đối chiếu giấy tờ xe và hợp đồng cư dân hợp lệ. Chấp thuận chuyển nhượng phương tiện sang căn hộ 08.02.",
    x: 12, y: 12, width: 536, size: 11, color: colors.textBlack
  });

  // Checkbox xác thực
  const checkOption = createBox(modalBox, {
    name: "Checkbox_Confirm",
    x: 20, y: 382, width: 560, height: 36,
    fill: colors.boxFill, stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(checkOption, {
    characters: "[x] Xác nhận cập nhật quyền sở hữu xe và gửi thông báo SMS/App tới cả 2 cư dân.",
    x: 12, y: 10, size: 11, bold: true
  });

  // Hàng Nút Hành Động
  const btnCancel = createButton(modalBox, "HỦY BỎ [Quay lại]", 20, 440, 260, 44, {
    fill: colors.boxFill, stroke: colors.borderBlack
  });
  const btnApprove = createButton(modalBox, "XÁC NHẬN PHÊ DUYỆT ➔", 300, 440, 280, 44, {
    fill: colors.paperBg, stroke: colors.borderBlack, strokeWeight: 2
  });

  // Marker đỏ chỉ dẫn Prototype
  createMarkerNote(modalBox, "👉 STEP 2: Click [XÁC NHẬN PHÊ DUYỆT] ➔ Chuyển sang Screen A4 (State Đã duyệt)", 20, 498, 560, 36);

  return master;
}

// Frame A3: Modal Từ chối Đơn Chuyển nhượng (Reject Modal)
function buildTransferRejectModalFrame(posX, posY) {
  const master = createBox(figma.currentPage, {
    name: "Wireframe A3: Modal Reject Prompt (Từ Chối Đơn Chuyển Nhượng)",
    x: posX, y: posY,
    width: 1080, height: 680,
    fill: colors.paperBg,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  // Nền mờ Backdrop
  createBox(master, {
    name: "Modal_Backdrop_Dimmed",
    x: 0, y: 0, width: 1080, height: 680,
    fill: colors.modalBackdrop,
    opacity: 0.45,
    stroke: null
  });

  // HỘP THOẠI MODAL TỪ CHỐI
  const MODAL_W = 580;
  const MODAL_H = 500;
  const modalBox = createBox(master, {
    name: "Dialog_Reject_Transfer",
    x: Math.floor((1080 - MODAL_W) / 2),
    y: Math.floor((680 - MODAL_H) / 2),
    width: MODAL_W, height: MODAL_H,
    fill: colors.whiteFill,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  // Header Modal với viền đỏ
  const mHeader = createBox(modalBox, {
    name: "Modal_Header",
    x: 0, y: 0, width: MODAL_W, height: 48,
    fill: colors.boxFill, stroke: colors.markerRed, strokeWeight: 2
  });
  createText(mHeader, { characters: "TỪ CHỐI ĐƠN CHUYỂN NHƯỢNG PHƯƠNG TIỆN", x: 18, y: 14, size: 14, bold: true, color: colors.markerRed });
  createText(mHeader, { characters: "[ Đóng ✕ ]", x: 510, y: 14, size: 12, bold: true, color: colors.textMuted });

  // Tóm tắt đơn cần từ chối
  const detailBox = createBox(modalBox, {
    name: "Transfer_Reject_Summary",
    x: 20, y: 64, width: 540, height: 80,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(detailBox, { characters: "Mã đơn: #TRF-088  |  Biển số: 29A-678.90 (Xe máy SH)", x: 14, y: 14, size: 12, bold: true });
  createText(detailBox, { characters: "Bên chuyển: Lê Hoàng C (Căn 05.11)  →  Bên nhận: Phạm Minh D (Căn 05.11)", x: 14, y: 40, size: 11 });

  // Lý do từ chối (Bắt buộc theo luồng xử lý)
  createText(modalBox, {
    characters: "Lý do từ chối (Bắt buộc - Sẽ gửi thông báo giải thích cho cư dân):",
    x: 20, y: 160, size: 11, bold: true, color: colors.markerRed
  });
  const reasonInput = createBox(modalBox, {
    name: "Textarea_Reject_Reason",
    x: 20, y: 182, width: 540, height: 110,
    fill: colors.whiteFill, stroke: colors.markerRed, strokeWeight: 2
  });
  createText(reasonInput, {
    characters: "Hồ sơ chứng minh mối quan hệ sở hữu chưa rõ ràng hoặc căn hộ bên nhận đã đăng ký đủ 02 xe máy theo hạn mức bãi đỗ xe của tòa nhà.",
    x: 12, y: 14, width: 516, size: 11, color: colors.textBlack
  });

  // Hướng dẫn cư dân
  const guideBox = createBox(modalBox, {
    name: "Guide_Reapply",
    x: 20, y: 308, width: 540, height: 60,
    fill: colors.boxFill, stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(guideBox, {
    characters: "• Cư dân có thể nộp lại hồ sơ bổ sung sau khi khắc phục lý do trên.\n• Đơn từ chối sẽ được lưu vào lịch sử tra cứu của BQT.",
    x: 12, y: 14, size: 11, color: colors.textMuted
  });

  // Nút hành động
  createButton(modalBox, "QUAY LẠI [Hủy]", 20, 385, 240, 42, {
    fill: colors.boxFill, stroke: colors.borderBlack
  });
  createButton(modalBox, "XÁC NHẬN TỪ CHỐI ĐƠN", 280, 385, 280, 42, {
    fill: colors.boxFill, stroke: colors.markerRed, strokeWeight: 2, textColor: colors.markerRed
  });

  // Marker đỏ Prototype
  createMarkerNote(modalBox, "👉 LUỒNG TỪ CHỐI: Click [XÁC NHẬN TỪ CHỐI] ➔ Trạng thái chuyển thành [ĐÃ TỪ CHỐI]", 20, 440, 540, 36);

  return master;
}

// ==============================================================================
// [NHÓM 2] QUẢN LÝ VÀ PHÂN QUYỀN NGƯỜI DÙNG (ADMIN)
// ==============================================================================

// Frame B1 & B4: Danh sách người dùng & Phân quyền (B1: Tổng quan, B4: Đã cập nhật + Toast)
function buildUsersListFrame(posX, posY, isSuccessState = false) {
  const master = createBox(figma.currentPage, {
    name: isSuccessState
      ? "Wireframe B4: Users List (State: Cập Nhật Phân Quyền Thành Công + Toast)"
      : "Wireframe B1: Users List (State: Danh Sách & Thống Kê Phân Quyền)",
    x: posX, y: posY,
    width: 1080, height: 680,
    fill: colors.paperBg,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  renderAdminHeader(master, "Quản Lý Tài Khoản & Phân Quyền Hệ Thống", "users");

  // TOAST THÔNG BÁO THÀNH CÔNG (Nếu là B4)
  if (isSuccessState) {
    const toastBox = createBox(master, {
      name: "Toast_Success_UserUpdated",
      x: 15, y: 112, width: 1050, height: 40,
      fill: colors.badgeGreenBg,
      stroke: colors.badgeGreenText,
      strokeWeight: 2
    });
    createText(toastBox, {
      characters: "✅ CẬP NHẬT THÀNH CÔNG: Tài khoản 0901234567 đã được phân quyền thành [ Operator (Bảo Vệ) ] và lưu vào CSDL accounts.json!",
      x: 18, y: 12, size: 12, bold: true, color: colors.badgeGreenText
    });
    createMarkerNote(master, "👉 PROTOTYPE RESULT: Dòng 1 cập nhật Role mới [Operator], Toast hiển thị, Thống kê Operator tăng 1!", 15, 630, 1050, 36);
  } else {
    createMarkerNote(master, "👉 PROTOTYPE STEP 1: Click [ SỬA / PHÂN QUYỀN ] ở dòng 0901234567 để mở Modal #editUserModal (Screen B2)", 15, 630, 680, 36);
    createMarkerNote(master, "👉 Nút [ + THÊM BẢO VỆ MỚI ]", 710, 630, 355, 36);
  }

  const contentTop = isSuccessState ? 160 : 115;

  // 4 THẺ THỐNG KÊ NGƯỜI DÙNG & VAI TRÒ
  const cardW = 252;
  const cards = [
    { title: "TỔNG TÀI KHOẢN", val: "148 tài khoản", sub: "Hoạt động: 145 | Khóa: 3" },
    { title: "CƯ DÂN (RESIDENT)", val: isSuccessState ? "135 cư dân" : "136 cư dân", sub: "Quản lý 142 phương tiện" },
    { title: "BẢO VỆ (OPERATOR)", val: isSuccessState ? "9 nhân viên" : "8 nhân viên", sub: "Trực ca cổng vào / cổng ra" },
    { title: "QUẢN TRỊ VIÊN (ADMIN)", val: "4 quản trị viên", sub: "Toàn quyền hệ thống BQT" }
  ];

  cards.forEach((c, idx) => {
    const cardBox = createBox(master, {
      name: `Card_Metric_${c.title}`,
      x: 15 + idx * (cardW + 14), y: contentTop,
      width: cardW, height: 60,
      stroke: colors.borderBlack, strokeWeight: 1.5
    });
    createText(cardBox, { characters: c.title, x: 12, y: 8, size: 10, bold: true, color: colors.textMuted });
    createText(cardBox, { characters: c.val, x: 12, y: 26, size: 14, bold: true });
    createText(cardBox, { characters: c.sub, x: 12, y: 44, size: 10, color: colors.textMuted });
  });

  // THANH CÔNG CỤ TÌM KIẾM & BỘ LỌC
  const toolBarY = contentTop + 68;
  const toolBar = createBox(master, {
    name: "User_Toolbar",
    x: 15, y: toolBarY, width: 1050, height: 44,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });

  const searchBox = createBox(toolBar, {
    name: "Search_Users",
    x: 10, y: 6, width: 360, height: 32,
    stroke: colors.borderBlack, strokeWeight: 1
  });
  createText(searchBox, { characters: "🔍 Tìm kiếm theo SĐT, Tên tài khoản, Họ tên, Căn hộ...", x: 10, y: 8, size: 11, color: colors.textMuted });

  const filterRole = createBox(toolBar, {
    name: "Filter_Role_Select",
    x: 380, y: 6, width: 200, height: 32,
    stroke: colors.borderBlack, strokeWeight: 1
  });
  createText(filterRole, { characters: "Vai trò: Tất Cả Vai Trò ▾", x: 10, y: 8, size: 11 });

  const filterStatus = createBox(toolBar, {
    name: "Filter_Status_Select",
    x: 590, y: 6, width: 180, height: 32,
    stroke: colors.borderBlack, strokeWeight: 1
  });
  createText(filterStatus, { characters: "Trạng thái: Hoạt Động ▾", x: 10, y: 8, size: 11 });

  createButton(toolBar, "+ THÊM BẢO VỆ MỚI", 840, 6, 200, 32, {
    fill: colors.paperBg, stroke: colors.borderBlack, strokeWeight: 2
  });

  // BẢNG DANH SÁCH NGƯỜI DÙNG & VAI TRÒ
  const tableY = toolBarY + 52;
  const tableBox = createBox(master, {
    name: "Table_Users",
    x: 15, y: tableY, width: 1050, height: 280,
    fill: colors.whiteFill,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });

  // Table Header
  const thBox = createBox(tableBox, {
    name: "Table_Header",
    x: 0, y: 0, width: 1050, height: 36,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1
  });

  const uColumns = [
    { label: "SĐT (KEY ID)", x: 12, w: 120 },
    { label: "TÊN TÀI KHOẢN", x: 140, w: 130 },
    { label: "HỌ VÀ TÊN", x: 280, w: 170 },
    { label: "VAI TRÒ (ROLE)", x: 460, w: 140 },
    { label: "TRẠNG THÁI", x: 610, w: 110 },
    { label: "PHÒNG / CA TRỰC", x: 730, w: 140 },
    { label: "NGÀY TẠO", x: 880, w: 80 },
    { label: "HÀNH ĐỘNG", x: 970, w: 70 }
  ];

  uColumns.forEach(c => {
    createText(thBox, { characters: c.label, x: c.x, y: 11, size: 10, bold: true });
  });

  // Dòng 1: Target sửa đổi (0901234567)
  const r1 = createBox(tableBox, {
    name: "Row_User_0901234567",
    x: 0, y: 36, width: 1050, height: 60,
    fill: isSuccessState ? colors.badgeGreenBg : colors.whiteFill,
    stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(r1, { characters: "0901234567", x: 12, y: 22, size: 12, bold: true });
  createText(r1, { characters: isSuccessState ? "cudan_1204" : "cudan_1204", x: 140, y: 22, size: 11 });
  createText(r1, { characters: "Nguyễn Văn A\nnguyenvana@gmail.com", x: 280, y: 15, size: 11 });

  if (isSuccessState) {
    createBadge(r1, "Operator (Bảo Vệ)", 460, 18, 130, 24, "blue");
    createBadge(r1, "Hoạt Động", 610, 18, 90, 24, "green");
    createText(r1, { characters: "Ca 2 (14h - 22h)\nCổng vào tầng B1", x: 730, y: 15, size: 11, bold: true });
  } else {
    createBadge(r1, "Resident (Cư Dân)", 460, 18, 130, 24, "yellow");
    createBadge(r1, "Hoạt Động", 610, 18, 90, 24, "green");
    createText(r1, { characters: "Căn hộ: 12.04\n(2 xe máy, 1 ô tô)", x: 730, y: 15, size: 11 });
  }

  createText(r1, { characters: "10/01/2026", x: 880, y: 22, size: 11, color: colors.textMuted });
  createButton(r1, "Sửa / Phân Quyền", 945, 16, 95, 28, {
    fill: colors.paperBg, stroke: colors.borderBlack, size: 10, bold: true
  });

  // Dòng 2: Operator mẫu (0987654321)
  const r2 = createBox(tableBox, {
    name: "Row_User_0987654321",
    x: 0, y: 96, width: 1050, height: 60,
    fill: colors.whiteFill, stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(r2, { characters: "0987654321", x: 12, y: 22, size: 12, bold: true });
  createText(r2, { characters: "bv_truongca", x: 140, y: 22, size: 11 });
  createText(r2, { characters: "Trần Bảo Vệ\ntranbaove@parking.vn", x: 280, y: 15, size: 11 });
  createBadge(r2, "Operator (Bảo Vệ)", 460, 18, 130, 24, "blue");
  createBadge(r2, "Hoạt Động", 610, 18, 90, 24, "green");
  createText(r2, { characters: "Ca 1 (06h - 14h)\nCổng chính bãi xe", x: 730, y: 15, size: 11 });
  createText(r2, { characters: "15/12/2025", x: 880, y: 22, size: 11, color: colors.textMuted });
  createButton(r2, "Sửa / Phân Quyền", 945, 16, 95, 28, {
    fill: colors.boxFill, stroke: colors.borderBlack, size: 10
  });

  // Dòng 3: Admin mẫu (0988888888)
  const r3 = createBox(tableBox, {
    name: "Row_User_0988888888",
    x: 0, y: 156, width: 1050, height: 60,
    fill: colors.whiteFill, stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(r3, { characters: "0988888888", x: 12, y: 22, size: 12, bold: true });
  createText(r3, { characters: "admin_bqt", x: 140, y: 22, size: 11 });
  createText(r3, { characters: "Ban Quản Trị Tòa Nhà\nbqt@building.com", x: 280, y: 15, size: 11 });
  createBadge(r3, "Admin (Quản Trị)", 460, 18, 130, 24, "red");
  createBadge(r3, "Hoạt Động", 610, 18, 90, 24, "green");
  createText(r3, { characters: "Văn phòng BQT\nTầng 1 Tòa nhà", x: 730, y: 15, size: 11 });
  createText(r3, { characters: "01/10/2025", x: 880, y: 22, size: 11, color: colors.textMuted });
  createButton(r3, "Sửa / Phân Quyền", 945, 16, 95, 28, {
    fill: colors.boxFill, stroke: colors.borderBlack, size: 10
  });

  // Chân bảng phân trang
  const uPage = createBox(tableBox, {
    name: "Table_Pagination",
    x: 0, y: 235, width: 1050, height: 45,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1
  });
  createText(uPage, {
    characters: "Hiển thị 1 - 3 trong tổng số 148 tài khoản người dùng",
    x: 15, y: 15, size: 11, color: colors.textMuted
  });
  createText(uPage, {
    characters: "Trang:  [ 1 ]   2   3   4   ...   15   >   >>",
    x: 770, y: 15, size: 11, bold: true
  });

  return master;
}

// Frame B2 & B3: Modal Chỉnh Sửa & Phân Quyền Người Dùng (B2: Bình thường, B3: Validation Error)
function buildUserEditModalFrame(posX, posY, isErrorState = false) {
  const master = createBox(figma.currentPage, {
    name: isErrorState
      ? "Wireframe B3: Modal Validation Error (Báo Lỗi Mật Khẩu < 6 Ký Tự)"
      : "Wireframe B2: Modal Edit User & Permissions (#editUserModal)",
    x: posX, y: posY,
    width: 1080, height: 680,
    fill: colors.paperBg,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  // Nền mờ Backdrop
  createBox(master, {
    name: "Modal_Backdrop_Dimmed",
    x: 0, y: 0, width: 1080, height: 680,
    fill: colors.modalBackdrop,
    opacity: 0.45,
    stroke: null
  });

  // HỘP THOẠI MODAL #editUserModal
  const MODAL_W = 640;
  const MODAL_H = 610;
  const modalBox = createBox(master, {
    name: "Dialog_Edit_User_Permissions",
    x: Math.floor((1080 - MODAL_W) / 2),
    y: Math.floor((680 - MODAL_H) / 2),
    width: MODAL_W, height: MODAL_H,
    fill: colors.whiteFill,
    stroke: isErrorState ? colors.markerRed : colors.borderBlack,
    strokeWeight: 2
  });

  // Modal Header
  const mHeader = createBox(modalBox, {
    name: "Modal_Header",
    x: 0, y: 0, width: MODAL_W, height: 46,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(mHeader, { characters: "CHỈNH SỬA THÔNG TIN & PHÂN QUYỀN TÀI KHOẢN", x: 18, y: 14, size: 14, bold: true });
  createText(mHeader, { characters: "[ Đóng ✕ ]", x: 570, y: 14, size: 12, bold: true, color: colors.markerRed });

  let formStartY = 58;

  // BANNER BÁO LỖI NẾU LÀ SCREEN B3
  if (isErrorState) {
    const errorBanner = createBox(modalBox, {
      name: "Banner_Validation_Error",
      x: 20, y: 54, width: 600, height: 40,
      fill: colors.badgeRedBg,
      stroke: colors.markerRed,
      strokeWeight: 2
    });
    createText(errorBanner, {
      characters: "⚠️ LỖI VALIDATION: Mật khẩu mới quá ngắn! Mật khẩu phải có tối thiểu 6 ký tự trở lên.",
      x: 12, y: 12, size: 11, bold: true, color: colors.markerRed
    });
    formStartY = 104;
  }

  // Field 1: SĐT Đăng nhập (Readonly Key ID)
  createText(modalBox, { characters: "Số điện thoại đăng nhập (Mã ID CSDL - Khóa chính không thể sửa):", x: 20, y: formStartY, size: 11, bold: true });
  const fPhone = createBox(modalBox, {
    name: "Input_Phone_Disabled",
    x: 20, y: formStartY + 20, width: 600, height: 36,
    fill: colors.boxFill, stroke: colors.borderMuted, strokeWeight: 1
  });
  createText(fPhone, { characters: "0901234567  [ 🔒 KHÓA CHÍNH TÀI KHOẢN ]", x: 12, y: 10, size: 11, bold: true, color: colors.textMuted });

  // Field 2 & 3: Tên tài khoản & Họ tên (2 Cột)
  const colW = 292;
  const row2Y = formStartY + 64;

  createText(modalBox, { characters: "Tên tài khoản (Username):", x: 20, y: row2Y, size: 11, bold: true });
  const fUser = createBox(modalBox, { name: "Input_Username", x: 20, y: row2Y + 20, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(fUser, { characters: "cudan_1204", x: 12, y: 10, size: 11 });

  createText(modalBox, { characters: "Họ và tên người dùng:", x: 328, y: row2Y, size: 11, bold: true });
  const fName = createBox(modalBox, { name: "Input_FullName", x: 328, y: row2Y + 20, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(fName, { characters: "Nguyễn Văn A", x: 12, y: 10, size: 11 });

  // Field 4 & 5: SĐT liên hệ mới & Email (2 Cột)
  const row3Y = row2Y + 64;

  createText(modalBox, { characters: "Số điện thoại liên hệ mới:", x: 20, y: row3Y, size: 11, bold: true });
  const fNewPhone = createBox(modalBox, { name: "Input_ContactPhone", x: 20, y: row3Y + 20, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(fNewPhone, { characters: "0901234567", x: 12, y: 10, size: 11 });

  createText(modalBox, { characters: "Địa chỉ Email:", x: 328, y: row3Y, size: 11, bold: true });
  const fEmail = createBox(modalBox, { name: "Input_Email", x: 328, y: row3Y + 20, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(fEmail, { characters: "nguyenvana@gmail.com", x: 12, y: 10, size: 11 });

  // Field 6 & 7: PHÂN QUYỀN VAI TRÒ (ROLE) & TRẠNG THÁI (2 Cột)
  const row4Y = row3Y + 64;

  createText(modalBox, { characters: "Phân quyền vai trò (Role):", x: 20, y: row4Y, size: 11, bold: true, color: colors.markerRed });
  const fRole = createBox(modalBox, {
    name: "Select_Role",
    x: 20, y: row4Y + 20, width: colW, height: 36,
    fill: colors.paperBg, stroke: colors.borderBlack, strokeWeight: 2
  });
  createText(fRole, { characters: "Operator (Nhân Viên Bảo Vệ) ▾", x: 12, y: 10, size: 11, bold: true });

  createText(modalBox, { characters: "Trạng thái tài khoản:", x: 328, y: row4Y, size: 11, bold: true });
  const fStatus = createBox(modalBox, {
    name: "Select_Status",
    x: 328, y: row4Y + 20, width: colW, height: 36,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(fStatus, { characters: "Hoạt Động (Active) ▾", x: 12, y: 10, size: 11 });

  // Field 8 & 9: Thông tin đặc thù vai trò (Căn hộ / Ca trực)
  const row5Y = row4Y + 64;

  createText(modalBox, { characters: "Mã căn hộ (Nếu là Cư dân):", x: 20, y: row5Y, size: 11, bold: true });
  const fApt = createBox(modalBox, { name: "Input_Apartment", x: 20, y: row5Y + 20, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(fApt, { characters: "12.04", x: 12, y: 10, size: 11 });

  createText(modalBox, { characters: "Phân công ca trực (Nếu là Bảo vệ):", x: 328, y: row5Y, size: 11, bold: true, color: colors.markerRed });
  const fShift = createBox(modalBox, {
    name: "Input_Shift",
    x: 328, y: row5Y + 20, width: colW, height: 36,
    fill: colors.boxFill, stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(fShift, { characters: "Ca 2 (14h00 - 22h00) - Tầng B1", x: 12, y: 10, size: 11, bold: true });

  // Field 10: Mật khẩu mới (Có validation test)
  const row6Y = row5Y + 64;
  createText(modalBox, { characters: "Mật khẩu mới (Để trống nếu không đổi, tối thiểu 6 ký tự):", x: 20, y: row6Y, size: 11, bold: true });
  const fPass = createBox(modalBox, {
    name: "Input_NewPassword",
    x: 20, y: row6Y + 20, width: 600, height: 36,
    fill: colors.whiteFill,
    stroke: isErrorState ? colors.markerRed : colors.borderBlack,
    strokeWeight: isErrorState ? 2 : 1.5
  });

  if (isErrorState) {
    createText(fPass, { characters: "123  (LỖI: Độ dài chỉ có 3 ký tự, yêu cầu ≥ 6 ký tự)", x: 12, y: 10, size: 11, bold: true, color: colors.markerRed });
  } else {
    createText(fPass, { characters: "Nhập mật khẩu mới nếu muốn đặt lại...", x: 12, y: 10, size: 11, color: colors.textMuted });
  }

  // Hàng Nút Hành Động
  const btnRowY = row6Y + 68;
  createButton(modalBox, "ĐÓNG / HỦY BỎ", 20, btnRowY, 280, 42, {
    fill: colors.boxFill, stroke: colors.borderBlack
  });
  createButton(modalBox, "LƯU THAY ĐỔI & PHÂN QUYỀN ➔", 320, btnRowY, 300, 42, {
    fill: colors.paperBg, stroke: colors.borderBlack, strokeWeight: 2
  });

  // Marker đỏ Prototype
  if (isErrorState) {
    createMarkerNote(modalBox, "👉 NHÁNH VALIDATION: Sửa mật khẩu ≥ 6 ký tự rồi bấm lại [LƯU THAY ĐỔI] để sang Screen B4", 20, btnRowY + 48, 600, 36);
  } else {
    createMarkerNote(modalBox, "👉 STEP 2: Click [LƯU THAY ĐỔI] ➔ Nhánh thành công chuyển sang Screen B4 | Nhập sai mật khẩu sang Screen B3", 20, btnRowY + 48, 600, 36);
  }

  return master;
}

// ==============================================================================
// [NHÓM 3] CÁC MÀN HÌNH CƯ DÂN (PUBLIC DASHBOARD, LOGIN, REGISTER)
// ==============================================================================

function buildPublicDashboardFrame(posX, posY = 0) {
  const master = createBox(figma.currentPage, {
    name: "1. Wireframe: Public Dashboard",
    x: posX, y: posY,
    width: 1100, height: 640,
    fill: colors.paperBg,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  const headerBox = createBox(master, {
    name: "Header_Top",
    x: 15, y: 15, width: 835, height: 60,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(headerBox, { characters: "LOGO: Parking AI", x: 18, y: 12, size: 16, bold: true });
  createText(headerBox, { characters: "Quản lý bãi xe thông minh", x: 18, y: 34, size: 11, color: colors.textMuted });
  createText(headerBox, { characters: "SEARCH", x: 560, y: 12, size: 15, bold: true });
  createText(headerBox, { characters: "Tra cứu biển số / chỗ đỗ", x: 560, y: 34, size: 11, color: colors.textMuted });

  const authMarkerBox = createBox(master, {
    name: "Auth_Marker_Red",
    x: 850, y: 15, width: 235, height: 60,
    stroke: colors.markerRed, strokeWeight: 2
  });
  createText(authMarkerBox, { characters: "ĐN / ĐK", x: 0, y: 12, width: 235, size: 18, bold: true, color: colors.markerRed, align: "CENTER" });
  createText(authMarkerBox, { characters: "Đăng nhập | Đăng ký", x: 0, y: 36, width: 235, size: 11, bold: true, color: colors.markerRed, align: "CENTER" });

  const navBox = createBox(master, {
    name: "Menu_Navigasi",
    x: 15, y: 75, width: 835, height: 42,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(navBox, { characters: "MENU NAVIGASI", x: 18, y: 12, size: 14, bold: true });
  createText(navBox, { characters: "Trang Chủ  |  Tầng Hầm B1 & B2  |  Nhận Diện Biển Số  |  Báo Cáo  |  Liên Hệ", x: 180, y: 14, size: 11, color: colors.textMuted });

  const featBox = createBox(master, { name: "Featured", x: 15, y: 117, width: 90, height: 28, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(featBox, { characters: "Featured:", x: 8, y: 6, size: 12, bold: true });

  const bigFeatureBox = createBox(master, { name: "Big_Feature", x: 105, y: 117, width: 745, height: 180, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(bigFeatureBox, { characters: "Big Feature\n(Tổng Quan Bãi Xe Real-Time)", x: 0, y: 45, width: 745, size: 19, bold: true, align: "CENTER" });
  createText(bigFeatureBox, {
    characters: "• Ô đỗ trống: 94/100  |  116 phương tiện trong bãi  |  363 lượt nhận diện AI\n• Trạng thái tầng hầm B1 (46 trống) & B2 (48 trống)  |  Biểu đồ lưu lượng giờ cao điểm",
    x: 20, y: 105, width: 705, size: 12, color: colors.textMuted, align: "CENTER"
  });

  const sfWidth = 241;
  const sfHeight = 240;
  const sfY = 297;

  const sf1 = createBox(master, { name: "Small_Feature_1", x: 105, y: sfY, width: sfWidth, height: sfHeight, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(sf1, { characters: "Small Feature\n(Nhận Diện Biển Số AI)", x: 0, y: 75, width: sfWidth, size: 14, bold: true, align: "CENTER" });
  createText(sf1, { characters: "Tự động nhận diện biển số qua camera\ncổng vào/ra, độ chính xác cao.", x: 15, y: 125, width: sfWidth - 30, size: 11, color: colors.textMuted, align: "CENTER" });

  const sf2 = createBox(master, { name: "Small_Feature_2", x: 357, y: sfY, width: sfWidth, height: sfHeight, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(sf2, { characters: "Small Feature\n(Quản Lý Chỗ Đỗ)", x: 0, y: 75, width: sfWidth, size: 14, bold: true, align: "CENTER" });
  createText(sf2, { characters: "Theo dõi tình trạng ô đỗ theo thời gian\nthực và vị trí đỗ xe tại tầng hầm.", x: 15, y: 125, width: sfWidth - 30, size: 11, color: colors.textMuted, align: "CENTER" });

  const sf3 = createBox(master, { name: "Small_Feature_3", x: 609, y: sfY, width: sfWidth, height: sfHeight, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(sf3, { characters: "Small Feature\n(Báo Cáo Trực Quan)", x: 0, y: 75, width: sfWidth, size: 14, bold: true, align: "CENTER" });
  createText(sf3, { characters: "Thống kê lưu lượng lượt xe, doanh thu\nvà hoạt động vận hành.", x: 15, y: 125, width: sfWidth - 30, size: 11, color: colors.textMuted, align: "CENTER" });

  const recentBox = createBox(master, { name: "Recent_Post", x: 850, y: 75, width: 235, height: 222, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(recentBox, { characters: "Recent Post\n(Lượt Xe Gần Nhất)", x: 0, y: 70, width: 235, size: 15, bold: true, align: "CENTER" });
  createText(recentBox, { characters: "Danh sách biển số xe vừa quét:\n• 30F-557.75 - Đã hoàn tất\n• 30F-507.74 - Đã hoàn tất", x: 15, y: 120, width: 205, size: 11, color: colors.textMuted, align: "CENTER" });

  const newsBox = createBox(master, { name: "News", x: 850, y: sfY, width: 235, height: sfHeight, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(newsBox, { characters: "News\n(Bảng Tin Bãi Xe)", x: 0, y: 80, width: 235, size: 15, bold: true, align: "CENTER" });
  createText(newsBox, { characters: "• Thông báo bảo trì camera AI\n• Quy định đỗ xe tầng hầm B1/B2\n• Hướng dẫn đăng ký vé tháng", x: 15, y: 130, width: 205, size: 11, color: colors.textMuted, align: "CENTER" });

  const footerBox = createBox(master, { name: "Footer", x: 15, y: 547, width: 1070, height: 42, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(footerBox, { characters: "Copyright @ 2019", x: 18, y: 12, size: 13, bold: true });
  createText(footerBox, { characters: "© 2026 Parking AI · Hệ thống quản lý bãi xe thông minh", x: 450, y: 14, width: 600, size: 11, color: colors.textMuted, align: "RIGHT" });

  return master;
}

function buildLoginFrame(posX, posY = 0) {
  const FRAME_W = 440;
  const FRAME_H = 640;

  const master = createBox(figma.currentPage, {
    name: "2. Wireframe: Login (Đăng Nhập - Hình Dọc)",
    x: posX, y: posY,
    width: FRAME_W, height: FRAME_H,
    fill: colors.paperBg,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  const topLogo = createBox(master, {
    name: "PhacThao_Logo",
    x: Math.floor((FRAME_W - 80) / 2), y: 24,
    width: 80, height: 44,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(topLogo, { characters: "LOGO", x: 0, y: 14, width: 80, size: 13, bold: true, align: "CENTER" });

  const titleBox = createBox(master, {
    name: "PhacThao_TieuDe",
    x: 25, y: 78, width: 390, height: 58,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(titleBox, { characters: "ĐĂNG NHẬP", x: 0, y: 10, width: 390, size: 18, bold: true, align: "CENTER" });
  createText(titleBox, { characters: "Hệ Thống Quản Lý Bãi Đỗ Xe & Biển Số AI", x: 0, y: 34, width: 390, size: 11, color: colors.textMuted, align: "CENTER" });

  const tabBox = createBox(master, {
    name: "PhacThao_Tabs",
    x: 25, y: 146, width: 390, height: 44,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  const t1 = createBox(tabBox, { name: "Tab_Admin", x: 4, y: 4, width: 189, height: 34, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(t1, { characters: "Quản Trị / Bảo Vệ", x: 0, y: 10, width: 189, size: 12, bold: true, align: "CENTER" });
  const t2 = createBox(tabBox, { name: "Tab_Resident", x: 197, y: 4, width: 189, height: 34, stroke: colors.borderMuted, strokeWeight: 1 });
  createText(t2, { characters: "Cư Dân", x: 0, y: 10, width: 189, size: 12, color: colors.textMuted, align: "CENTER" });

  createText(master, { characters: "Số điện thoại đăng nhập:", x: 25, y: 202, size: 12, bold: true });
  const inputPhone = createBox(master, { name: "Input_Phone", x: 25, y: 222, width: 390, height: 38, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(inputPhone, { characters: "Nhập số điện thoại", x: 14, y: 11, width: 360, size: 12, color: colors.textMuted });

  createText(master, { characters: "Mật khẩu:", x: 25, y: 272, size: 12, bold: true });
  createText(master, { characters: "Quên mật khẩu?", x: 25, y: 272, width: 390, size: 11, color: colors.markerRed, align: "RIGHT" });
  const inputPass = createBox(master, { name: "Input_Password", x: 25, y: 292, width: 390, height: 38, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(inputPass, { characters: "Nhập mật khẩu", x: 14, y: 11, width: 360, size: 12, color: colors.textMuted });

  const btnLogin = createBox(master, { name: "Button_DangNhap", x: 25, y: 344, width: 390, height: 42, stroke: colors.borderBlack, strokeWeight: 2 });
  createText(btnLogin, { characters: "NÚT BẤM: ĐĂNG NHẬP", x: 0, y: 13, width: 390, size: 13, bold: true, align: "CENTER" });

  const quickBox = createBox(master, { name: "PhacThao_TaiKhoanMau", x: 25, y: 400, width: 390, height: 115, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(quickBox, { characters: "Tài khoản mẫu thử nghiệm (Click để điền):", x: 12, y: 8, size: 11, bold: true });
  const p1 = createBox(quickBox, { name: "Pill_Admin", x: 12, y: 30, width: 366, height: 32, stroke: colors.borderBlack, strokeWeight: 1 });
  createText(p1, { characters: "Admin: admin / admin123", x: 12, y: 8, width: 340, size: 11, bold: true });
  const p2 = createBox(quickBox, { name: "Pill_Resident", x: 12, y: 68, width: 366, height: 32, stroke: colors.borderBlack, strokeWeight: 1 });
  createText(p2, { characters: "Cư dân: cudan1 / 123456", x: 12, y: 8, width: 340, size: 11, bold: true });

  const footerLink = createBox(master, { name: "Footer_DangKy", x: 25, y: 528, width: 390, height: 40, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(footerLink, { characters: "Chưa có tài khoản cư dân? Đăng ký ngay", x: 0, y: 12, width: 390, size: 12, bold: true, align: "CENTER" });

  const copyrightBox = createBox(master, { name: "Copyright_Bar", x: 25, y: 578, width: 390, height: 32, stroke: colors.borderBlack, strokeWeight: 1 });
  createText(copyrightBox, { characters: "Copyright @ 2019 - 2026 Parking AI", x: 0, y: 9, width: 390, size: 11, color: colors.textMuted, align: "CENTER" });

  return master;
}

function buildRegisterFrame(posX, posY = 0) {
  const FRAME_W = 480;
  const FRAME_H = 740;

  const master = createBox(figma.currentPage, {
    name: "3. Wireframe: Register (Đăng Ký - Hình Dọc)",
    x: posX, y: posY,
    width: FRAME_W, height: FRAME_H,
    fill: colors.paperBg,
    stroke: colors.borderBlack,
    strokeWeight: 2
  });

  const topLogo = createBox(master, {
    name: "PhacThao_Logo",
    x: Math.floor((FRAME_W - 80) / 2), y: 20,
    width: 80, height: 42,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(topLogo, { characters: "LOGO", x: 0, y: 13, width: 80, size: 13, bold: true, align: "CENTER" });

  const titleBox = createBox(master, {
    name: "PhacThao_TieuDe",
    x: 25, y: 70, width: 430, height: 56,
    stroke: colors.borderBlack, strokeWeight: 1.5
  });
  createText(titleBox, { characters: "TẠO TÀI KHOẢN MỚI", x: 0, y: 9, width: 430, size: 17, bold: true, align: "CENTER" });
  createText(titleBox, { characters: "Đăng ký thành viên hệ thống quản lý bãi xe", x: 0, y: 32, width: 430, size: 11, color: colors.textMuted, align: "CENTER" });

  createText(master, { characters: "Vai trò tài khoản:", x: 25, y: 136, size: 12, bold: true });
  const dropRole = createBox(master, { name: "Dropdown_VaiTro", x: 25, y: 154, width: 430, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(dropRole, { characters: "Cư dân tòa nhà (Xem xe & Vé tháng) ▾", x: 12, y: 10, width: 400, size: 11 });

  createText(master, { characters: "Tên tài khoản (Mã căn hộ):", x: 25, y: 198, size: 12, bold: true });
  const inputUser = createBox(master, { name: "Input_Username", x: 25, y: 216, width: 430, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(inputUser, { characters: "Ví dụ: cudan2_10 (Có thể trùng)", x: 12, y: 10, width: 400, size: 11, color: colors.textMuted });

  createText(master, { characters: "Họ và tên:", x: 25, y: 260, size: 12, bold: true });
  const inputName = createBox(master, { name: "Input_FullName", x: 25, y: 278, width: 430, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(inputName, { characters: "Nguyễn Văn A", x: 12, y: 10, width: 400, size: 11, color: colors.textMuted });

  const colW = 210;
  createText(master, { characters: "Số điện thoại *:", x: 25, y: 322, size: 12, bold: true });
  const inputPhone = createBox(master, { name: "Input_Phone", x: 25, y: 340, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(inputPhone, { characters: "0901234567", x: 10, y: 10, width: colW - 20, size: 11, color: colors.textMuted });

  createText(master, { characters: "Địa chỉ Email:", x: 245, y: 322, size: 12, bold: true });
  const inputEmail = createBox(master, { name: "Input_Email", x: 245, y: 340, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(inputEmail, { characters: "email@domain.com", x: 10, y: 10, width: colW - 20, size: 11, color: colors.textMuted });

  createText(master, { characters: "Mật khẩu:", x: 25, y: 384, size: 12, bold: true });
  const inputPass = createBox(master, { name: "Input_Password", x: 25, y: 402, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(inputPass, { characters: "Tối thiểu 6 ký tự", x: 10, y: 10, width: colW - 20, size: 11, color: colors.textMuted });

  createText(master, { characters: "Xác nhận:", x: 245, y: 384, size: 12, bold: true });
  const inputConfirm = createBox(master, { name: "Input_ConfirmPassword", x: 245, y: 402, width: colW, height: 36, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(inputConfirm, { characters: "Nhập lại mật khẩu", x: 10, y: 10, width: colW - 20, size: 11, color: colors.textMuted });

  const btnRegister = createBox(master, { name: "Button_TaoTaiKhoan", x: 25, y: 452, width: 430, height: 42, stroke: colors.borderBlack, strokeWeight: 2 });
  createText(btnRegister, { characters: "NÚT BẤM: TẠO TÀI KHOẢN", x: 0, y: 13, width: 430, size: 13, bold: true, align: "CENTER" });

  const noteBox = createBox(master, { name: "PhacThao_QuyenLoi", x: 25, y: 506, width: 430, height: 100, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(noteBox, { characters: "Lưu ý & Quyền lợi khi đăng ký tài khoản:", x: 12, y: 8, size: 11, bold: true });
  createText(noteBox, {
    characters: "• Tự động mở barrier qua nhận diện biển số AI 0.3s\n• Đăng ký & gia hạn vé tháng online không cần tiền mặt\n• Số điện thoại bắt buộc gồm 10 chữ số (bắt đầu bằng số 0)\n• Mỗi căn hộ đăng ký tối đa 2 xe máy và 1 ô tô",
    x: 12, y: 28, width: 406, size: 11, color: colors.textBlack
  });

  const footerLink = createBox(master, { name: "Footer_DangNhap", x: 25, y: 618, width: 430, height: 40, stroke: colors.borderBlack, strokeWeight: 1.5 });
  createText(footerLink, { characters: "Đã có tài khoản? Đăng nhập ngay", x: 0, y: 12, width: 430, size: 12, bold: true, align: "CENTER" });

  const copyrightBox = createBox(master, { name: "Copyright_Bar", x: 25, y: 670, width: 430, height: 32, stroke: colors.borderBlack, strokeWeight: 1 });
  createText(copyrightBox, { characters: "Copyright @ 2019 - 2026 Parking AI", x: 0, y: 9, width: 430, size: 11, color: colors.textMuted, align: "CENTER" });

  return master;
}

// ==============================================================================
// HÀM ĐIỀU HƯỚNG VÀ KHỞI CHẠY PLUGIN THEO COMMAND
// ==============================================================================
async function main() {
  try {
    await figma.loadFontAsync(fontRegular);
    await figma.loadFontAsync(fontBold);

    const GAP_X = 80;
    const GAP_Y = 80;
    const FRAME_W = 1080;
    const FRAME_H = 680;
    let createdFrames = [];

    const cmd = figma.command || "generate_all_admin";

    if (cmd === "generate_transfers") {
      // Chỉ tạo 4 màn hình của luồng Phê duyệt đơn chuyển nhượng Admin
      const a1 = buildTransferListFrame(0, 0, false);
      const a2 = buildTransferApproveModalFrame(FRAME_W + GAP_X, 0);
      const a3 = buildTransferRejectModalFrame((FRAME_W + GAP_X) * 2, 0);
      const a4 = buildTransferListFrame((FRAME_W + GAP_X) * 3, 0, true);
      createdFrames = [a1, a2, a3, a4];
      figma.closePlugin("✓ Đã tạo thành công: 4 màn hình Wireframe Phê duyệt đơn chuyển nhượng Admin!");
    } else if (cmd === "generate_users") {
      // Chỉ tạo 4 màn hình của luồng Quản lý & Phân quyền người dùng Admin
      const b1 = buildUsersListFrame(0, 0, false);
      const b2 = buildUserEditModalFrame(FRAME_W + GAP_X, 0, false);
      const b3 = buildUserEditModalFrame((FRAME_W + GAP_X) * 2, 0, true);
      const b4 = buildUsersListFrame((FRAME_W + GAP_X) * 3, 0, true);
      createdFrames = [b1, b2, b3, b4];
      figma.closePlugin("✓ Đã tạo thành công: 4 màn hình Wireframe Quản lý & Phân quyền người dùng Admin!");
    } else if (cmd === "generate_resident") {
      // Tạo các màn hình Cư dân
      const r1 = buildPublicDashboardFrame(0, 0);
      const r2 = buildLoginFrame(1100 + GAP_X, 0);
      const r3 = buildRegisterFrame(1100 + GAP_X + 440 + GAP_X, 0);
      createdFrames = [r1, r2, r3];
      figma.closePlugin("✓ Đã tạo thành công: 3 màn hình Cư dân (Dashboard, Đăng nhập, Đăng ký)!");
    } else {
      // MẶC ĐỊNH HOẶC "generate_all_admin": TẠO TRỌN BỘ 8 MÀN HÌNH ADMIN (2 HÀNG ĐỐI XỨNG HOÀN CHỈNH)

      // HÀNG 1 (Y = 0): 4 màn hình Luồng Phê duyệt đơn chuyển nhượng
      const a1 = buildTransferListFrame(0, 0, false);
      const a2 = buildTransferApproveModalFrame(FRAME_W + GAP_X, 0);
      const a3 = buildTransferRejectModalFrame((FRAME_W + GAP_X) * 2, 0);
      const a4 = buildTransferListFrame((FRAME_W + GAP_X) * 3, 0, true);

      // HÀNG 2 (Y = 760): 4 màn hình Luồng Quản lý & Phân quyền người dùng
      const row2Y = FRAME_H + GAP_Y;
      const b1 = buildUsersListFrame(0, row2Y, false);
      const b2 = buildUserEditModalFrame(FRAME_W + GAP_X, row2Y, false);
      const b3 = buildUserEditModalFrame((FRAME_W + GAP_X) * 2, row2Y, true);
      const b4 = buildUsersListFrame((FRAME_W + GAP_X) * 3, row2Y, true);

      createdFrames = [a1, a2, a3, a4, b1, b2, b3, b4];
      figma.closePlugin("✓ Đã tạo thành công: TRỌN BỘ 8 MÀN HÌNH WIREFRAME ADMIN PHỤC VỤ LÀM PROTOTYPE (2 luồng chuyển nhượng & phân quyền)!");
    }

    if (createdFrames.length > 0) {
      figma.currentPage.selection = createdFrames;
      figma.viewport.scrollAndZoomIntoView(createdFrames);
    }
  } catch (error) {
    console.error(error);
    figma.closePlugin(`❌ Lỗi: ${error.message}`);
  }
}

main();
