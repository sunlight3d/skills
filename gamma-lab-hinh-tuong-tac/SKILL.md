---
name: gamma-lab-hinh-tuong-tac
description: Dựng các mô hình minh hoạ giải thích kỹ thuật, quy trình sản xuất công nghiệp và hệ thống trực quan dạng Isometric 3D tương tác theo phong cách Gamma Lab (Anatomy Card, số đọc sống, tháo rời chi tiết, tổng hợp âm thanh Web Audio). Kích hoạt khi người dùng muốn giải thích trực quan một cỗ máy, quy trình sản xuất (trà, cà phê, bia, dược phẩm, ô tô, điện gió, lọc dầu...), hệ thống cơ khí, hoặc gọi tên "Gamma Lab", "hình tương tác", "bản vẽ isometric 3D".
---

# Gamma Lab · Hình Tương Tác (Interactive Explanatory Diagrams)

Kỹ năng tạo các ứng dụng minh hoạ kỹ thuật trực quan dạng **Isometric 3D tương tác độc lập (Zero external dependencies)**, kết hợp chuẩn nhận diện thiết kế **Gamma Lab Anatomy Card**, số liệu thời gian thực (live readouts), chế độ tháo rời chi tiết máy (exploded view) và âm thanh vật lý mô phỏng bằng Web Audio API.

---

## 1. Triết lý Thiết kế & Chuẩn Nhận diện (Anatomy Design System)

Mỗi mô hình tương tác Gamma Lab tuân thủ chặt chẽ cấu trúc bố cục **Anatomy Card**:

### Bố cục Thẻ Hình 4 Góc (The 4-Corner Anatomy Card)
- **Góc trên-trái:** Chỉ số hình ảnh: `<span class="fign">Hình n</span> · Tên phân cảnh`.
- **Góc trên-phải:** Góc quan sát tiêu chuẩn: `Góc nhìn 45°` cùng nút bật/tắt âm thanh `Âm thanh: Bật/Tắt`.
- **Góc dưới-trái:** Gợi ý thao tác trực quan: `Chọn trạm · kéo thanh · chạy dây chuyền · tháo rời`.
- **Góc dưới-phải:** Trạng thái hệ thống hoặc số đọc sống (Live Readout): `<b>Sẵn sàng</b>` hoặc `<b>Tốc độ: 1.2x</b>`.

### Bảng màu Nhận diện Thương hiệu (Palette)
Hệ thống sử dụng bảng màu ấm cúng, tương phản cao, phong cách kỹ thuật hoài cổ (Warm Editorial Engineering):
- **Nền tổng thể (`--bg`):** Lúa mì kem `#F6EAD0` (Chế độ tối: `#1d1613`)
- **Mặt giấy thẻ (`--paper`):** Giấy trắng ngà `#FFFDF7` (Chế độ tối: `#2a211c`)
- **Nét mực in (`--ink`):** Nâu đen mực in `#2b1b17` (Chế độ tối: `#F6EAD0`)
- **Màu phụ trợ (`--mute`):** Nâu đất ấm `#7a6e63`
- **Đường phân cách (`--line`):** Vàng cát `#d9c9a8` (Chế độ tối: `#4a3b31`)
- **Màu điểm nhấn chính (`--brand`):** Đỏ rượu nho Gamma `#7F0220`
- **Màu phụ trợ sinh học/vận hành (`--green`):** Xanh lục trà `#1F6B3B`
- **Màu cảnh báo/nhiệt lượng (`--gold`):** Vàng đồng `#F2B33D`

### Kiểu chữ (Typography)
- **Tiêu đề & Số liệu lớn:** Font `Dela Gothic One` (đậm chất brutalist kỹ thuật, hỗ trợ tiếng Việt đầy đủ).
- **Thân bài & Nhãn điều khiển:** Font `Be Vietnam Pro` (chuẩn quốc gia hiện đại, nét thanh thoát).

---

## 2. Hệ Toạ độ & Toán học Chiếu Trục Đo (`IsoKit`)

Thư viện lõi `assets/iso-kit.js` chuyển đổi không gian toạ độ 3D $(x, y, z)$ sang màn hình SVG 2D $(sx, sy)$ mà không cần Three.js hay thư viện ngoài:

```
           +z (Thẳng đứng lên trời)
            |
            |
            |
           / \
          /   \
         /     \
  +y <--+       +--> +x
(Góc 150°)     (Góc 30°)
(Sang trái-xuống) (Sang phải-xuống)
```

### Công thức biến đổi:
$$sx = ox + (x - y) \times \cos(30^\circ) \times \text{scale} \approx ox + (x - y) \times 0.866025 \times \text{scale}$$
$$sy = oy + \left( (x + y) \times \sin(30^\circ) - z \right) \times \text{scale} = oy + \left( (x + y) \times 0.5 - z \right) \times \text{scale}$$

### Nguyên tắc Ánh sáng 1 Màu Gốc $\to$ 4 Sắc độ (`IsoKit.tones(col)`):
Mỗi bộ phận chỉ cần cung cấp **MỘT** màu chủ đạo, bộ dựng hình tự tính toán:
1. **Mặt đỉnh (`top`):** Tươi sáng nhất (+18% độ sáng), hứng ánh sáng từ trên cao.
2. **Mặt phải (`right`):** Giữ nguyên sắc độ gốc (Mặt chính diện bán sáng).
3. **Mặt trái (`left`):** Tối hơn (-16% độ sáng), mặt khuất bóng.
4. **Viền mực (`edge`):** Đường stroke mực sắc nét nâu đen `#2b1b17`.
5. **Bóng dưới chân (`halo`):** Vùng bóng mờ elip SVG đổ lên bề mặt bên dưới.

---

## 3. Các Khối Hình Học Cơ Bản (Primitives)

Trong hàm `draw(g, ctx)` của từng bộ phận:

### 1. Khối hộp (`box`) & Tấm phẳng (`slab`)
```javascript
// Khối hộp máy (có bóng đổ chân, đường phân rã seam, đinh ốc screws)
ctx.box(g, x, y, z, w, d, h, '#c9c5bb', {
  halo: true,       // Tạo bóng đổ mờ elip dưới đáy sàn
  seam: true,       // Khắc rãnh ghép giữa các tấm kim loại
  screws: [10, 20]  // Vị trí đinh vít trang trí
});

// Tấm phẳng/sàn mỏng (như khay đựng, đế đỡ mỏng)
ctx.slab(g, x, y, z, w, d, h, '#a28356');
```

### 2. Hình trụ đứng (`cyl`)
```javascript
// Trụ máy có gradient ánh sáng mượt mà tự động
ctx.cyl(g, x, y, z, radius, height, '#7F0220', {
  bands: [30, 60],  // Các vành đai gia cố bằng kim loại
  halo: true        // Bóng đổ chân trụ
});
```

### 3. Đường ống kết nối 3D (`tube`)
```javascript
// Đường ống dẫn khí, nước, dung dịch đi qua các toạ độ 3D
ctx.tube(g, [
  [x1, y1, z1],
  [x2, y2, z2],
  [x3, y3, z3]
], radius, '#5aa9d6', { dots: true }); // dots: tạo đầu bịt tròn không bị hẫng
```

### 4. Ghim số chỉ mục & Số đọc sống (`pin`)
```javascript
// Quả cầu ghim số 1, 2, 3... nổi bật tại vị trí 3D
// kèm theo nhãn chữ hiển thị số liệu động
ctx.pin(g, x, y, z, 1, '#7F0220', { title: 'Nhiệt độ', value: '250°C' });
```

### 5. Lưới mặt sàn (`grid`) & Chữ khắc chìm (`engrave`)
```javascript
// Sàn lưới thông gió, khay sấy
ctx.grid(g, x, y, z, width, depth, stepSize, '#d9c9a8');

// Chữ khắc chìm trên mặt máy
ctx.engrave(g, x, y, z, 'GAMMA LAB', '#2b1b17', 9);
```

---

## 4. Cơ chế Tương tác Nâng cao

### A. Chế độ Tháo rời Chi tiết (Exploded View)
Mỗi bộ phận khai báo một vector tháo rời 3D `apart: [dx, dy, dz]`:
```javascript
const parts = [
  {
    id: 'base',
    n: 1,
    h: 'Khung đế chịu lực',
    p: 'Gia công bằng thép đúc...',
    draw(g, c) { c.slab(g, -100, -60, 0, 200, 120, 15, '#8e8a80'); },
    apart: [0, 0, -40] // Khi tháo rời: hạ xuống dưới theo trục Z
  },
  {
    id: 'tank',
    n: 2,
    h: 'Thùng áp suất',
    p: 'Buồng ủ men vi sinh...',
    draw(g, c) { c.cyl(g, 0, 0, 15, 35, 70, '#7F0220'); },
    apart: [0, 0, 50]  // Khi tháo rời: nhấc lên trên theo trục Z
  }
];

const fig = figure(ctx, parts);

// Kích hoạt tháo rời/ráp lại bằng một lệnh:
fig.setApart(true);  // Bung các chi tiết ra không gian
fig.setApart(false); // Ráp lại vị trí ban đầu
```

### B. Cập nhật Số đọc Sống Động (Live Reactive Tags)
Khi người dùng kéo thanh trượt điều khiển:
```javascript
bindRange(['temp_slider', 'speed_slider'], (values) => {
  // Cập nhật nhãn động bay theo ghim số của bộ phận
  fig.setTag('tank', `${values.temp_slider}°C`);
  
  // Cập nhật các ô đo lường trong bảng điều khiển
  document.getElementById('stat-temp').textContent = values.temp_slider;
});
```

### C. Mô phỏng Âm thanh Vật lý Bằng Web Audio API (Không cần tải file mp3)
Hệ thống tích hợp bộ tổng hợp âm thanh chuyên dụng:
1. **Âm động cơ rền nhẹ (Motor Rumble):** Dùng sóng `triangle` qua bộ lọc `BiquadFilter` tần số thấp (80Hz - 180Hz) gắn với tốc độ dây chuyền.
2. **Âm xả hơi nóng (Steam Hiss):** Dùng `AudioBuffer` sinh tiếng ồn trắng (White Noise) lọc qua Bandpass Filter (800Hz - 2400Hz).
3. **Âm gõ kim loại/giọt nước (Click / Pop):** Dùng sóng `sine` hạ tần số cực nhanh trong 40ms.
4. **Hợp âm ngũ cung hoàn thành (Chime):** Chuỗi 3 nốt nhạc Pentatonic tươi vui khi sản phẩm hoàn thành mẻ chế biến.

---

## 5. Cấu trúc Tài nguyên & Công cụ Ghép File

Tất cả mã nguồn mẫu và thư viện dùng chung được đặt tại thư mục skill:
```
gamma-lab-hinh-tuong-tac/
├── SKILL.md                              # Hướng dẫn chi tiết này
├── assets/
│   ├── the.css                           # Bảng phong cách CSS nhận diện Gamma Lab
│   ├── iso-kit.js                        # Bộ công cụ vẽ Isometric SVG & tương tác
│   └── ghep.mjs                          # CLI tự động đóng gói thành file HTML độc lập
└── examples/
    └── day-chuyen-che-bien-tra.html      # Mô hình mẫu thực tế: Dây chuyền chế biến trà 6 trạm
```

### Sử dụng công cụ `assets/ghep.mjs`:
- **Tạo khung bài mới:**
  ```bash
  node /Volumes/data/code/skills/gamma-lab-hinh-tuong-tac/assets/ghep.mjs --new <ten-file.html> "Tên Mô Hình"
  ```
- **Đóng gói file đã viết xong thành một file độc lập:**
  ```bash
  node /Volumes/data/code/skills/gamma-lab-hinh-tuong-tac/assets/ghep.mjs <input.html> -o <output.html>
  ```

---

## 6. Quy trình 5 Bước Tạo Bản Vẽ Kỹ Thuật Tương Tác cho Agent

Khi người dùng yêu cầu: *"Hãy giải thích nguyên lý hoạt động của [hệ thống X] bằng hình tương tác Gamma Lab"*:

1. **Phân tích Kiến trúc Hệ thống:**
   - Chia hệ thống thành **4 đến 8 phân đoạn/bộ phận** then chốt theo trình tự dòng chảy vật chất hoặc nguyên lý cơ học.
   - Chọn từ 1 đến 3 biến số cốt lõi làm thanh trượt điều khiển (Ví dụ: Nhiệt độ, Áp suất, Thời gian, Lưu lượng).

2. **Dựng Khung Giao diện Anatomy Card:**
   - Dùng mẫu HTML chuẩn từ `assets/ghep.mjs --new`.
   - Đặt tên chỉ số phân cảnh (`Hình 1 · Dây chuyền...`), ghi rõ thông điệp dẫn nhập súc tích trong `.lead`.

3. **Vẽ Không gian Isometric 3D với `IsoKit`:**
   - Đặt gốc toạ độ máy `(ox, oy)` căn giữa khung nhìn SVG (thường `viewBox="0 0 960 540"` hoặc `680 440`).
   - Sắp đặt các bộ phận theo trục $x$ (xuống-phải) hoặc trục $y$ (xuống-trái).
   - Thiết lập vector `apart` hợp lý (thường tách ra theo trục $z$ lên/xuống hoặc dạt ra hai bên $x, y$) để khi bấm "Tháo rời" không bị chồng lấn.

4. **Kết nối Dòng Chảy & Phản hồi Trực quan:**
   - Dùng `requestAnimationFrame` tạo hiệu ứng hạt chuyển động theo ống dẫn hoặc băng chuyền.
   - Cập nhật số đọc sống, thẻ kết luận (`.verdict`), và màu sắc dung dịch tương ứng với thông số thanh trượt.

5. **Xuất Bản & Kiểm Thử:**
   - Đảm bảo toàn bộ HTML, CSS, JS nằm gọn trong một tệp duy nhất, người dùng có thể nhấp đúp mở ngay trên bất kỳ trình duyệt nào mà không cần cài đặt web server hay phụ thuộc mạng Internet.
