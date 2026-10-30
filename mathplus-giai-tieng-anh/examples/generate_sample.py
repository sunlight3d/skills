#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script tạo file mẫu Đề thi Tiếng Anh có lời giải & dịch nghĩa toàn văn chuẩn MathPlus Academy.
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(CURRENT_DIR, "..", "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from mathplus_docx_engine import MathPlusDocxBuilder

def generate_sample():
    builder = MathPlusDocxBuilder(
        title="ĐỀ THI THỬ TUYỂN SINH VÀO LỚP 10 MÔN TIẾNG ANH",
        subtitle="Năm học 2026 – 2027",
        time_limit="60 phút",
        subject_center="Bồi dưỡng Tiếng Anh & Luyện thi",
        is_solved=True
    )

    # PHẦN I. NGỮ ÂM
    builder.add_section("PHẦN I. NGỮ ÂM (PHONETICS)", "Chọn từ có phần gạch chân phát âm khác hoặc có trọng âm chính khác.")
    builder.add_instruction("Mark the letter A, B, C, or D on your answer sheet to indicate the word whose underlined part differs from the other three in pronunciation.")

    builder.add_question("Question 1:", "", options={'A': 'arr<u>i</u>ve', 'B': 'l<u>i</u>ke', 'C': 'c<u>i</u>ty', 'D': 'n<u>i</u>ce'})
    builder.add_solution_box(
        key="C",
        explanation="Phương án C có chữ cái 'i' được phát âm là /ɪ/ (city /ˈsɪti/), trong khi các phương án A, B, D chữ 'i' đều được phát âm là /aɪ/.",
        options_meaning="A. arrive /əˈraɪv/ (đến) | B. like /laɪk/ (thích) | C. city /ˈsɪti/ (thành phố) | D. nice /naɪs/ (đẹp, tốt)",
        grammar="Quy tắc phát âm của nguyên âm 'i': thường phát âm là /aɪ/ khi đứng trước phụ âm + e tận cùng (like, nice, arrive), và phát âm là /ɪ/ trong từ ngắn hoặc âm tiết không nhấn.",
        vocab="arrive at / in: đến nơi; nice to meet you: rất vui được gặp bạn."
    )

    builder.add_question("Question 2:", "", options={'A': 'work<u>ed</u>', 'B': 'play<u>ed</u>', 'C': 'clean<u>ed</u>', 'D': 'stay<u>ed</u>'})
    builder.add_solution_box(
        key="A",
        explanation="Phương án A có đuôi '-ed' đi sau âm vô thanh /k/ nên được phát âm là /t/ (worked /wɜːkt/). Các phương án B, C, D đuôi '-ed' đi sau âm hữu thanh (/eɪ/, /n/, /eɪ/) nên đều được phát âm là /d/.",
        options_meaning="A. worked (làm việc) | B. played (chơi) | C. cleaned (lau dọn) | D. stayed (ở lại)",
        grammar="Quy tắc phát âm đuôi '-ed':\n• Phát âm là /ɪd/ sau /t/, /d/ (wanted, needed).\n• Phát âm là /t/ sau âm vô thanh: /p/, /k/, /f/, /s/, /ʃ/, /tʃ/ (worked, watched, laughed).\n• Phát âm là /d/ sau các âm hữu thanh còn lại (played, cleaned, opened)."
    )

    # PHẦN II. NGỮ PHÁP & TỪ VỰNG
    builder.add_section("PHẦN II. NGỮ PHÁP VÀ TỪ VỰNG (LEXICO - GRAMMAR)")
    builder.add_instruction("Mark the letter A, B, C, or D on your answer sheet to indicate the correct answer to each of the following questions.")

    builder.add_question("Question 3:", "If Mary _______ more free time, she would join our voluntary club.", options={
        'A': 'has',
        'B': 'had',
        'C': 'will have',
        'D': 'would have'
    })
    builder.add_solution_box(
        key="B",
        translation="Nếu Mary có nhiều thời gian rảnh hơn, cô ấy sẽ tham gia câu lạc bộ tình nguyện của chúng tôi.",
        options_meaning="A. has (thì hiện tại đơn) | B. had (quá khứ đơn) | C. will have (tương lai đơn) | D. would have (dạng điều kiện)",
        grammar="Cấu trúc Câu điều kiện loại 2 (diễn tả điều kiện không có thật ở hiện tại):\n• Mệnh đề If: If + S + V-ed / V2 (động từ 'to be' chia 'were' cho mọi ngôi).\n• Mệnh đề chính: S + would / could / might + V-bare.",
        explanation="Mệnh đề chính dùng 'would join' (would + V-bare), do đó câu thuộc câu điều kiện loại 2. Mệnh đề 'If' phải chia ở thì quá khứ đơn (had).",
        eliminate="Loại A vì là thì hiện tại (câu ĐK loại 1). Loại C vì mệnh đề If không dùng 'will'. Loại D vì 'would have' không đứng trong mệnh đề If của câu điều kiện loại 2."
    )

    # PHẦN III. BÀI ĐỌC HIỂU (READING COMPREHENSION)
    builder.add_section("PHẦN III. ĐỌC HIỂU (READING COMPREHENSION)")
    builder.add_instruction("Read the following passage and mark the letter A, B, C, or D on your answer sheet to indicate the correct answer to each of the questions.")

    passage_text = (
        "[1] Many people believe that reading books is one of the most effective ways to acquire knowledge and develop "
        "critical thinking skills. When we read, our brains are actively engaged in processing complex vocabulary, "
        "visualizing scenes, and understanding human emotions through diverse characters.\n\n"
        "[2] Furthermore, reading regularly helps expand vocabulary and improve overall communication abilities. In today's "
        "fast-paced digital era, where smartphones and social media easily distract our attention, spending at least 25 "
        "minutes a day with a good book can remarkably reduce stress and enhance academic performance."
    )
    builder.add_reading_passage(passage_text, title="THE POWER OF DAILY READING HABITS")

    # BẢN DỊCH BẮT BUỘC SANG TIẾNG VIỆT
    translation_text = (
        "[1] Nhiều người tin rằng đọc sách là một trong những phương pháp hiệu quả nhất để tiếp thu kiến thức và phát triển "
        "kỹ năng tư duy phản biện. Khi chúng ta đọc, não bộ chủ động tham gia vào quá trình xử lý từ vựng phức tạp, "
        "hình dung các bối cảnh và thấu hiểu cảm xúc con người thông qua các nhân vật đa dạng.\n\n"
        "[2] Hơn nữa, việc đọc sách thường xuyên giúp mở rộng vốn từ vựng và nâng cao toàn diện khả năng giao tiếp. Trong thời đại "
        "công nghệ số hối hả ngày nay, nơi điện thoại thông minh và mạng xã hội dễ dàng làm phân tán sự chú ý của chúng ta, "
        "việc dành ít nhất 25 phút mỗi ngày cho một cuốn sách hay có thể làm giảm căng thẳng một cách đáng kể và nâng cao kết quả học tập."
    )
    builder.add_reading_translation(translation_text, title="BẢN DỊCH TIẾNG VIỆT TOÀN VĂN BÀI ĐỌC")

    # Câu hỏi đọc hiểu
    builder.add_question("Question 4:", "What is the primary topic of the passage?", options={
        'A': 'The dangers of social media addiction',
        'B': 'The outstanding benefits of regular reading habits',
        'C': 'Methods to improve communication in the digital era',
        'D': 'Why students fail to develop critical thinking'
    })
    builder.add_solution_box(
        key="B",
        translation="Chủ đề chính của đoạn văn là gì?",
        options_meaning=(
            "A. Sự nguy hiểm của việc nghiện mạng xã hội | "
            "B. Những lợi ích vượt trội của thói quen đọc sách thường xuyên | "
            "C. Các phương pháp cải thiện giao tiếp trong thời đại số | "
            "D. Tại sao học sinh không phát triển được tư duy phản biện"
        ),
        explanation="Toàn bộ bài đọc tập trung nêu bật và phân tích các lợi ích của việc đọc sách: rèn luyện trí não, tư duy phản biện (đoạn 1), mở rộng từ vựng, giảm căng thẳng và nâng cao kết quả học tập (đoạn 2).",
        evidence="Reading books is one of the most effective ways... spending at least 25 minutes a day with a good book can remarkably reduce stress and enhance academic performance.",
        eliminate="A và C chỉ là những yếu tố ngữ cảnh phụ; D không được đề cập trong bài."
    )

    builder.add_question("Question 5:", "According to paragraph 2, spending 25 minutes a day reading can help you _______.", options={
        'A': 'become a professional writer',
        'B': 'relieve stress and improve academic achievements',
        'C': 'avoid using smartphones completely',
        'D': 'memorize all complex vocabulary'
    })
    builder.add_solution_box(
        key="B",
        translation="Theo đoạn 2, việc dành 25 phút mỗi ngày đọc sách có thể giúp bạn làm điều gì?",
        options_meaning=(
            "A. Trở thành nhà văn chuyên nghiệp | "
            "B. Giải tỏa căng thẳng và nâng cao thành tích học tập | "
            "C. Hoàn toàn tránh xa việc sử dụng điện thoại thông minh | "
            "D. Ghi nhớ toàn bộ từ vựng phức tạp"
        ),
        explanation="Trong đoạn 2, tác giả nêu rõ: 'spending at least 25 minutes a day with a good book can remarkably reduce stress and enhance academic performance'. Cụm 'reduce stress and enhance academic performance' đồng nghĩa với 'relieve stress and improve academic achievements'.",
        evidence="...spending at least 25 minutes a day with a good book can remarkably reduce stress and enhance academic performance.",
        eliminate="A, C, D đều là các suy diễn cực đoan, không có trong nội dung bài đọc."
    )

    # BẢNG ĐÁP ÁN NHANH
    builder.add_quick_answer_key({
        'Question 1': 'C',
        'Question 2': 'A',
        'Question 3': 'B',
        'Question 4': 'B',
        'Question 5': 'B'
    })

    # BẢNG TỪ VỰNG & CẤU TRÚC
    builder.add_vocabulary_table([
        ('acquire', '/əˈkwaɪər/', 'v', 'tiếp thu, thu nhận được', 'acquire knowledge (tiếp thu kiến thức)'),
        ('critical thinking', '/ˌkrɪt.ɪ.kəl ˈθɪŋ.kɪŋ/', 'n', 'tư duy phản biện', 'develop critical thinking skills'),
        ('actively engaged in', '/ˈæk.tɪv.li ɪnˈɡeɪdʒd/', 'adj phr', 'chủ động tham gia vào', 'engaged in processing vocabulary'),
        ('fast-paced', '/ˌfɑːstˈpeɪst/', 'adj', 'hối hả, nhịp độ nhanh', 'fast-paced digital era'),
        ('distract', '/dɪˈstrækt/', 'v', 'làm xao nhãng, phân tán', 'distract our attention'),
        ('remarkably', '/rɪˈmɑː.kə.bli/', 'adv', 'đáng kể, rõ rệt', 'remarkably reduce stress'),
        ('enhance', '/ɪnˈhɑːns/', 'v', 'nâng cao, tăng cường', 'enhance academic performance')
    ])

    # TỰ ĐÁNH GIÁ & NHẬN XÉT GIÁO VIÊN
    builder.add_self_evaluation([
        "Phân biệt chính xác quy tắc phát âm nguyên âm /aɪ/ và /ɪ/",
        "Nắm vững quy tắc phát âm đuôi '-ed' (/ɪd/, /t/, /d/)",
        "Áp dụng thành thạo cấu trúc Câu điều kiện loại 2",
        "Kỹ năng đọc lướt tìm ý chính (Skimming for Main Idea)",
        "Kỹ năng tìm thông tin chi tiết (Scanning for Detailed Information)"
    ])
    builder.add_teacher_feedback_and_signature(teacher_name="Nguyễn Văn Dũng – MathPlus Academy")

    out_file = os.path.join(CURRENT_DIR, "De_Thi_Tieng_Anh_Lop_10_Solved.docx")
    builder.save(out_file)
    print(f"Generated sample successfully: {out_file}")

if __name__ == "__main__":
    generate_sample()
