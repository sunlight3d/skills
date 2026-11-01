---
name: mathplus-seeding
description: "Tự động tìm kiếm & tham gia các hội nhóm Facebook phụ huynh/học sinh khu vực Đống Đa - Hà Nội (tối đa 3 nhóm/lần), tự động sinh biến thể nội dung tự nhiên (đóng vai mẹ tìm lớp Toán 10, 11 cho con quanh khu vực Đống Đa, Phạm Ngọc Thạch) và đăng bài ẩn danh (Anonymous Post) an toàn bằng Playwright qua profile Chrome có sẵn (tối đa 2 bài/lần)."
---

# MathPlus Seeding (Facebook Anonymous Group Seeder)

Skill này tự động hóa quy trình seeding tìm lớp học toán trên các hội nhóm Facebook:
1. **Tìm & Tham gia nhóm mục tiêu (Target Group Joining)**: Tự động tìm kiếm các hội phụ huynh khu vực Đống Đa, Kim Liên, Phạm Ngọc Thạch và gửi yêu cầu tham gia tối đa **3 nhóm mỗi lần chạy** (tự động điền câu hỏi xét duyệt và đồng ý quy tắc nhóm).
2. **Sinh biến thể bài viết tự nhiên (Natural Content Spinning)**: Đóng vai mẹ có 2 con học lớp 10 và 11 lực học đuối/chậm hoặc mới chuyển cấp ngợp kiến thức, cần tìm thầy cô dạy nhóm nhỏ (5–8 bạn) kèm sát từng bước tại khu vực Đống Đa / Phạm Ngọc Thạch / Kim Liên. Mỗi bài đăng đều khác nhau hoàn toàn về mở đầu, tiêu chí, hành văn để chống trùng lặp và chống spam.
3. **Đăng bài ẩn danh (Anonymous Posting)**: Sử dụng Playwright qua profile Chrome có sẵn, tự động kích hoạt tính năng **Anonymous post / Đăng bài ẩn danh**, mô phỏng tốc độ gõ phím của người thật, và đăng tối đa **2 bài mỗi lần chạy** với độ trễ ngẫu nhiên an toàn (45s – 75s).

---

## ⚠️ Nguyên Tắc An Toàn & Chống Checkpoint Facebook

1. **Giới hạn số lượng**: Mỗi lần chạy **chỉ join tối đa 3 nhóm** và **chỉ đăng tối đa 2 bài**. Tuyệt đối không đăng ồ ạt.
2. **Tự động spinning nội dung**: Mỗi nhóm được đăng một biến thể nội dung hoàn toàn riêng biệt.
3. **Mô phỏng thao tác người thật (Human Typing)**: Tốc độ gõ 20ms - 50ms mỗi ký tự, thi thoảng dừng ngẫu nhiên như đang suy nghĩ.
4. **Đồng bộ phiên đăng nhập tự động**: Tự động kế thừa cookie và phiên đăng nhập Facebook từ Google Chrome của người dùng, không bao giờ yêu cầu nhập lại mật khẩu.

---

## Cấu Trúc Thư Mục Skill

```
mathplus-seeding/
├── SKILL.md                  # Hướng dẫn chi tiết cho Agent
├── run.bat                   # File thực thi nhanh trên Windows CMD
├── run.ps1                   # File thực thi nhanh trên PowerShell
└── scripts/
    ├── spinner.py            # Module sinh biến thể bài viết mẹ tìm lớp
    └── seeder.py             # Engine Playwright tự động join nhóm & đăng ẩn danh
```

---

## Hướng Dẫn Sử Dụng

### 1. Chạy mặc định (Join 3 nhóm, Đăng thật 2 bài)
```powershell
c:\code\mathplus\.agents\skills\mathplus-seeding\run.bat
```
hoặc qua PowerShell:
```powershell
& "c:\code\mathplus\.agents\skills\mathplus-seeding\run.ps1"
```

### 2. Chạy thử nghiệm / Xem trước (Dry-run, không bấm Đăng)
```powershell
& "c:\code\mathplus\.agents\skills\mathplus-seeding\run.ps1" -DryRun
```

### 3. Tùy chỉnh số lượng nhóm và bài đăng
```powershell
& "c:\code\mathplus\.agents\skills\mathplus-seeding\run.ps1" -JoinCount 2 -PostCount 1 -DelayMin 60 -DelayMax 90
```

---

## Lịch Sử Thực Thi
Mọi lượt tham gia nhóm và bài đăng đều được ghi nhận chi tiết (thời gian, URL nhóm, trạng thái, đường dẫn ảnh chụp xem trước) tại:
`~/.mathplus_seeding_history.json`
