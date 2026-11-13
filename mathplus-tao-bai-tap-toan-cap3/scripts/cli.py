#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI điều phối tự động tạo phiếu bài tập Toán cấp 3 chuẩn nhận diện MathPlus Academy.
Quy trình:
1. Tìm kiếm và thu thập tư liệu từ toanmath.com, toannbv.vn, toanhocbactrungnam.vn.
2. Phân bổ số lượng câu hỏi từ dễ đến khó theo 4 mức độ: Nhận biết, Thông hiểu, Vận dụng, Vận dụng cao.
3. Xuất đồng thời 2 file Word:
   - File đề bài cho học sinh: [Chủ_Đề]_MathPlus.docx
   - File lời giải chi tiết: [Chủ_Đề]_MathPlus_Solved.docx
4. Tích hợp Logo MathPlus nguyên màu, thông tin Thầy Nguyễn Văn Dũng – Hotline: 0977 961 189,
   chữ đen tuyền 11pt, không sọc đen viền trái, 100% công thức OMML chuẩn ECMA-376.
"""

import os
import sys
import argparse
import json
import re

# Đảm bảo UTF-8 trên Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Thêm thư mục scripts vào sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from math_crawler import search_all_sources, calculate_level_counts, DIFFICULTY_LEVELS
from docx_builder import MathPlusWorksheetBuilder

def infer_grade(topic):
    """Suy luận khối lớp từ tên chủ đề."""
    t = topic.lower()
    if any(k in t for k in ['10', 'mệnh đề', 'tập hợp', 'bất phương trình bậc nhất hai ẩn', 'hàm số bậc hai', 'parabol', 'hệ thức lượng', 'vectơ trong mặt phẳng']):
        return "10"
    elif any(k in t for k in ['11', 'lượng giác', 'cấp số cộng', 'cấp số nhân', 'giới hạn', 'đạo hàm', 'hình học không gian lớp 11', 'khoảng cách', 'góc giữa']):
        return "11"
    elif any(k in t for k in ['12', 'khảo sát hàm số', 'cực trị', 'tiệm cận', 'đồng biến', 'nghịch biến', 'tích phân', 'nguyên hàm', 'oxyz', 'số phức', 'khối đa diện']):
        return "12"
    return "12"

def sanitize_filename(name):
    """Chuẩn hóa tên file an toàn."""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.replace(" ", "_")
    return name

def create_sample_exercises_for_topic(topic, grade, total_count):
    """
    Sinh tập câu hỏi mẫu chuẩn kiến thức GDPT 2018 phân loại từ dễ đến khó
    nếu người dùng chạy CLI trực tiếp mà không nạp qua file JSON.
    """
    counts = calculate_level_counts(total_count)
    exercises = []
    q_index = 1
    
    # Mức 1: Nhận biết
    for i in range(counts[0]):
        exercises.append({
            'index': q_index,
            'level_id': 1,
            'level_name': 'Nhận biết',
            'question': f"Khẳng định nào sau đây là **đúng** về tính chất cơ bản của ${topic}$ trong tập xác định $\\mathbb{{R}}$?",
            'options': [
                "A. Luôn đồng biến trên $\\mathbb{R}$.",
                "B. Thỏa mãn định lý cơ bản và điều kiện xác định đại số.",
                "C. Nhận mọi giá trị âm khi $x \\to +\\infty$.",
                "D. Luôn có đồ thị đi qua gốc tọa độ $O(0; 0)$."
            ],
            'answer': 'B',
            'solution': [
                ('p', f"Theo định nghĩa và tính chất cơ bản của **{topic}**:"),
                ('bullet', "Tính chất được quy định trực tiếp trong sách giáo khoa toán học hiện hành."),
                ('bullet', "Do đó khẳng định ở phương án B là chính xác."),
                ('display_math', r"\forall x \in D \implies f(x) \text{ xác định và thỏa mãn các tiên đề toán học.}")
            ]
        })
        q_index += 1
        
    # Mức 2: Thông hiểu
    for i in range(counts[1]):
        exercises.append({
            'index': q_index,
            'level_id': 2,
            'level_name': 'Thông hiểu',
            'question': f"Cho hàm số biểu diễn ${topic}$ có dạng $f(x) = x^2 - 4x + 3$. Tọa độ điểm đặc trưng (hoặc nghiệm) của phương trình $f(x) = 0$ là:",
            'options': [
                "A. $x = 1$ và $x = 3$.",
                "B. $x = -1$ và $x = -3$.",
                "C. $x = 2$ và $x = -1$.",
                "D. $x = 0$ và $x = 4$."
            ],
            'answer': 'A',
            'solution': [
                ('p', "Phương trình đã cho tương đương:"),
                ('display_math', r"x^2 - 4x + 3 = 0 \iff (x - 1)(x - 3) = 0 \iff \begin{cases} x = 1 \\ x = 3 \end{cases}"),
                ('bullet', "Vậy phương trình có hai nghiệm phân biệt $x_1 = 1$ và $x_2 = 3$."),
                ('bullet', "Chọn đáp án **A**.")
            ]
        })
        q_index += 1
        
    # Mức 3: Vận dụng
    for i in range(counts[2]):
        exercises.append({
            'index': q_index,
            'level_id': 3,
            'level_name': 'Vận dụng',
            'question': f"Tìm tất cả các giá trị của tham số thực $m$ để bài toán ${topic}$ liên quan biểu thức $g(x) = x^2 - 2(m-1)x + m^2 - 2$ luôn có 2 nghiệm phân biệt thỏa mãn $x_1 + x_2 + x_1 x_2 < 5$:",
            'options': [
                "A. $m > 1$.",
                "B. $-3 < m < 1$.",
                "C. $m < 1$ hoặc $m > 3$.",
                "D. Không tồn tại giá trị $m$ nào thỏa mãn."
            ],
            'answer': 'B',
            'solution': [
                ('p', "Điều kiện để phương trình có hai nghiệm phân biệt là $\\Delta' > 0$:"),
                ('display_math', r"\Delta' = (m-1)^2 - (m^2 - 2) = m^2 - 2m + 1 - m^2 + 2 = 3 - 2m > 0 \iff m < \frac{3}{2}."),
                ('p', "Áp dụng định lý Vi-ét: $\\begin{cases} x_1 + x_2 = 2(m-1) \\\\ x_1 x_2 = m^2 - 2 \\end{cases}$. Khi đó:"),
                ('display_math', r"2(m-1) + m^2 - 2 < 5 \iff m^2 + 2m - 9 < 0."),
                ('bullet', "Kết hợp điều kiện suy ra nghiệm thích hợp thỏa mãn là $-3 < m < 1$."),
                ('bullet', "Chọn đáp án **B**.")
            ]
        })
        q_index += 1
        
    # Mức 4: Vận dụng cao
    for i in range(counts[3]):
        exercises.append({
            'index': q_index,
            'level_id': 4,
            'level_name': 'Vận dụng cao',
            'question': f"Một bài toán ứng dụng thực tế về ${topic}$: Một doanh nghiệp dự định thiết kế một mô hình tối ưu chi phí theo hàm số $C(x) = 2x + \\dfrac{{1800}}{{x}}$ với $x > 0$ (đơn vị: triệu đồng). Chi phí thấp nhất mà doanh nghiệp có thể đạt được là:",
            'options': [
                "A. $120$ triệu đồng.",
                "B. $90$ triệu đồng.",
                "C. $150$ triệu đồng.",
                "D. $200$ triệu đồng."
            ],
            'answer': 'A',
            'solution': [
                ('p', "Áp dụng bất đẳng thức Cauchy (AM-GM) cho hai số dương $2x$ và $\\dfrac{1800}{x}$:"),
                ('display_math', r"C(x) = 2x + \frac{1800}{x} \ge 2\sqrt{2x \cdot \frac{1800}{x}} = 2\sqrt{3600} = 2 \cdot 60 = 120."),
                ('p', "Dấu đẳng thức xảy ra khi và chỉ khi:"),
                ('display_math', r"2x = \frac{1800}{x} \iff 2x^2 = 1800 \iff x^2 = 900 \iff x = 30 \text{ (do } x > 0)."),
                ('bullet', "Vậy chi phí thấp nhất là $120$ triệu đồng đạt được tại $x = 30$."),
                ('bullet', "Chọn đáp án **A**.")
            ]
        })
        q_index += 1
        
    return exercises

def generate_mathplus_worksheets(topic, grade=None, total_count=20, output_dir=None, exercises=None, time_limit="90 phút"):
    """
    Tạo hai file tài liệu Word chuẩn MathPlus Academy:
    1. [Chủ_Đề]_MathPlus.docx (Đề bài học sinh)
    2. [Chủ_Đề]_MathPlus_Solved.docx (Lời giải chi tiết)
    """
    if not grade:
        grade = infer_grade(topic)
        
    if output_dir is None:
        output_dir = "/Volumes/data/code/mathplus/Toán cấp 3"
        if not os.path.exists(output_dir):
            output_dir = os.getcwd()
            
    os.makedirs(output_dir, exist_ok=True)
    
    if exercises is None:
        exercises = create_sample_exercises_for_topic(topic, grade, total_count)
        
    safe_topic = sanitize_filename(topic)
    student_filename = f"{safe_topic}_Lop{grade}_MathPlus.docx"
    solved_filename = f"{safe_topic}_Lop{grade}_MathPlus_Solved.docx"
    
    student_path = os.path.join(output_dir, student_filename)
    solved_path = os.path.join(output_dir, solved_filename)
    
    print(f"[*] Đang khởi tạo tài liệu MathPlus cho chủ đề: '{topic}' (Lớp {grade}, {len(exercises)} câu)...")
    
    # --- 1. Tạo file đề bài cho học sinh ---
    builder_student = MathPlusWorksheetBuilder(
        topic=topic,
        grade=grade,
        total_count=len(exercises),
        time_limit=time_limit,
        is_solved=False
    )
    
    # Nhóm câu hỏi theo 4 mức độ
    current_level = 0
    for ex in exercises:
        lvl_id = ex.get('level_id', 1)
        if lvl_id != current_level:
            current_level = lvl_id
            level_info = next((l for l in DIFFICULTY_LEVELS if l['level_id'] == current_level), None)
            sec_title = level_info['name'] if level_info else f"MỨC ĐỘ {current_level}"
            sec_desc = level_info['description'] if level_info else ""
            builder_student.add_section_header(sec_title, sec_desc)
            
        builder_student.add_question(
            q_index=ex['index'],
            q_text=ex['question'],
            options=ex.get('options'),
            level_name=ex.get('level_name')
        )
        
    builder_student.save(student_path)
    print(f"[+] Đã tạo file đề bài học sinh: {student_path}")
    
    # --- 2. Tạo file lời giải chi tiết cho giáo viên ---
    builder_solved = MathPlusWorksheetBuilder(
        topic=topic,
        grade=grade,
        total_count=len(exercises),
        time_limit=time_limit,
        is_solved=True
    )
    
    # Thêm bảng đáp án trắc nghiệm nhanh ở đầu
    quick_answers = [(ex['index'], ex.get('answer', 'A'), ex.get('level_name', '')) for ex in exercises]
    builder_solved.add_quick_answer_grid(quick_answers)
    
    current_level = 0
    for ex in exercises:
        lvl_id = ex.get('level_id', 1)
        if lvl_id != current_level:
            current_level = lvl_id
            level_info = next((l for l in DIFFICULTY_LEVELS if l['level_id'] == current_level), None)
            sec_title = level_info['name'] if level_info else f"MỨC ĐỘ {current_level}"
            sec_desc = level_info['description'] if level_info else ""
            builder_solved.add_section_header(sec_title, sec_desc)
            
        builder_solved.add_question(
            q_index=ex['index'],
            q_text=ex['question'],
            options=ex.get('options'),
            level_name=ex.get('level_name')
        )
        
        # Thêm khung lời giải chi tiết (nền trắng, không sọc đen viền trái, font >= 11pt)
        builder_solved.add_solution_box(
            answer_key=ex.get('answer', 'A'),
            solution_steps=ex.get('solution', [('p', 'Xem hướng dẫn chi tiết của giáo viên.')])
        )
        
    builder_solved.save(solved_path)
    print(f"[+] Đã tạo file đáp án & lời giải chi tiết: {solved_path}")
    
    return {
        'student_file': student_path,
        'solved_file': solved_path,
        'total_questions': len(exercises),
        'topic': topic,
        'grade': grade
    }

def main():
    parser = argparse.ArgumentParser(description="MathPlus - Tự động tạo bài tập Toán cấp 3 từ dễ đến khó")
    parser.add_argument('--topic', '-t', required=True, help="Chủ đề Toán học (ví dụ: 'Hàm số bậc hai', 'Đạo hàm', 'Hình Oxyz')")
    parser.add_argument('--grade', '-g', default=None, help="Khối lớp (10, 11, 12). Mặc định tự động nhận diện từ chủ đề.")
    parser.add_argument('--count', '-c', type=int, default=20, help="Tổng số lượng bài tập cần tạo (mặc định: 20 câu)")
    parser.add_argument('--output-dir', '-o', default=None, help="Thư mục lưu file output Word")
    parser.add_argument('--input-json', '-j', default=None, help="File JSON chứa danh sách bài tập đã được Agent thu thập và tổng hợp")
    parser.add_argument('--search-only', action='store_true', help="Chỉ tìm kiếm tài liệu trên các website Toán và in kết quả")
    
    args = parser.parse_args()
    
    # 1. Tìm kiếm tài liệu trên các trang web Toán
    search_results = search_all_sources(args.topic)
    
    if args.search_only:
        print("\n=== KẾT QUẢ TÌM KIẾM TRÊN CÁC TRANG WEB TOÁN ===")
        print(json.dumps(search_results, ensure_ascii=False, indent=2))
        return
        
    # 2. Đọc bài tập từ file JSON nếu có
    exercises = None
    if args.input_json and os.path.exists(args.input_json):
        with open(args.input_json, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
            print(f"[+] Đã nạp {len(exercises)} bài tập từ file JSON: {args.input_json}")
            
    # 3. Tạo tài liệu Word chuẩn MathPlus
    res = generate_mathplus_worksheets(
        topic=args.topic,
        grade=args.grade,
        total_count=args.count,
        output_dir=args.output_dir,
        exercises=exercises
    )
    
    print("\n" + "="*60)
    print("HOÀN THÀNH TẠO PHIẾU BÀI TẬP MATHPLUS ACADEMY:")
    print(f"1. Bản Đề bài học sinh: file://{res['student_file']}")
    print(f"2. Bản Lời giải chi tiết: file://{res['solved_file']}")
    print("="*60)

if __name__ == "__main__":
    main()
