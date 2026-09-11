#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
data_generator.py - Engine sinh dữ liệu tự động dựa trên Template JSON và Validation Rules.
Hoạt động hoàn toàn trên Python Standard Library (không cần cài thêm thư viện bên ngoài).
Hỗ trợ sinh dữ liệu chuẩn ngữ nghĩa tiếng Việt: Họ tên, phòng ban, tiền lương, ngày giờ, số điện thoại, email, địa chỉ,...
"""

import os
import sys
import re
import json
import csv
import random
import string
import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Cấu hình UTF-8 cho Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ==============================================================================
# 1. KHO DỮ LIỆU MẪU TIẾNG VIỆT (VIETNAMESE CORPUS)
# ==============================================================================

VN_HO = [
    "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ",
    "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đào", "Đinh", "Đoàn"
]

VN_DEM_NAM = [
    "Văn", "Hữu", "Đức", "Đình", "Minh", "Quốc", "Thanh", "Trọng", "Duy",
    "Quang", "Công", "Bảo", "Hải", "Tuấn", "Tiến", "Việt", "Xuân"
]

VN_DEM_NU = [
    "Thị", "Ngọc", "Thanh", "Thu", "Xuân", "Hồng", "Mai", "Kim", "Ánh",
    "Phương", "Mỹ", "Diệu", "Tuyết", "Hương"
]

VN_TEN_NAM = [
    "An", "Bình", "Cường", "Dũng", "Đạt", "Hải", "Hiếu", "Hoàng", "Hùng",
    "Huy", "Khoa", "Kiên", "Long", "Minh", "Nam", "Nghĩa", "Phong", "Phúc",
    "Quân", "Quang", "Sơn", "Thắng", "Thịnh", "Toàn", "Trung", "Tuấn", "Tùng",
    "Việt", "Vinh", "Vũ"
]

VN_TEN_NU = [
    "Anh", "Bình", "Châu", "Dung", "Giang", "Hà", "Hạnh", "Hoa", "Hương",
    "Huyền", "Lan", "Linh", "Mai", "Nga", "Ngân", "Nhung", "Oanh", "Phương",
    "Quỳnh", "Tâm", "Thảo", "Thu", "Thủy", "Trang", "Trâm", "Uyên", "Vân",
    "Yến", "Thư"
]

VN_PHONG_BAN = [
    "IT", "HR", "Kế toán", "Tài chính", "Kinh doanh", "Marketing",
    "Chăm sóc khách hàng", "R&D", "Pháp chế", "Hành chính nhân sự",
    "Quản lý chất lượng", "Vận hành", "Ban Giám đốc"
]

VN_CHUC_VU = [
    "Thực tập sinh", "Nhân viên", "Chuyên viên", "Chuyên viên cao cấp",
    "Trưởng nhóm", "Phó phòng", "Trưởng phòng", "Phó Giám đốc", "Giám đốc bộ phận"
]

VN_TINH_THANH = [
    "Hà Nội", "TP. Hồ Chí Minh", "Đà Nẵng", "Hải Phòng", "Cần Thơ",
    "Quảng Ninh", "Bắc Ninh", "Hải Dương", "Nam Định", "Thái Bình",
    "Nghệ An", "Thanh Hóa", "Thừa Thiên Huế", "Khánh Hòa", "Bình Dương",
    "Đồng Nai", "Bà Rịa - Vũng Tàu", "Long An", "Tiền Giang", "Lâm Đồng"
]

VN_DUONG = [
    "Trần Phú", "Lê Lợi", "Nguyễn Trãi", "Quang Trung", "Hai Bà Trưng",
    "Lý Thường Kiệt", "Giải Phóng", "Cầu Giấy", "Hoàng Hoa Thám",
    "Kim Mã", "Đội Cấn", "Nguyễn Huệ", "Điện Biên Phủ", "Cách Mạng Tháng 8",
    "Võ Văn Kiệt", "Phan Chu Trinh", "Ngô Quyền", "Bà Triệu"
]

VN_PHONE_PREFIXES = [
    "090", "091", "092", "093", "094", "096", "097", "098",
    "086", "088", "089", "070", "076", "077", "078", "079",
    "032", "033", "034", "035", "036", "037", "038", "039"
]

EMAIL_DOMAINS = [
    "gmail.com", "outlook.com", "qnet.vn", "company.com.vn",
    "yahoo.com", "viettel.vn", "fpt.vn"
]


# ==============================================================================
# 2. TIỆN ÍCH XỬ LÝ CHUỖI & DỮ LIỆU
# ==============================================================================

def remove_vietnamese_accents(text: str) -> str:
    """Chuyển đổi chuỗi tiếng Việt có dấu thành không dấu để tạo email, username."""
    patterns = {
        '[àáạảãâầấậẩẫăằắặẳẵ]': 'a',
        '[ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴ]': 'A',
        '[èéẹẻẽêềếệểễ]': 'e',
        '[ÈÉẸẺẼÊỀẾỆỂỄ]': 'E',
        '[ìíịỉĩ]': 'i',
        '[ÌÍỊỈĨ]': 'I',
        '[òóọỏõôồốộổỗơờớợởỡ]': 'o',
        '[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]': 'O',
        '[ùúụủũưừứựửữ]': 'u',
        '[ÙÚỤỦŨƯỪỨỰỬỮ]': 'U',
        '[ỳýỵỷỹ]': 'y',
        '[ỲÝỴỶỸ]': 'Y',
        '[đ]': 'd',
        '[Đ]': 'D'
    }
    output = text
    for regex, replacement in patterns.items():
        output = re.sub(regex, replacement, output)
    return output


def generate_vietnamese_name(gender: Optional[str] = None) -> Tuple[str, str]:
    """Sinh họ tên đầy đủ người Việt và giới tính (Nam/Nữ)."""
    ho = random.choice(VN_HO)
    if gender is None:
        gender = random.choice(["Nam", "Nữ"])

    if gender == "Nam":
        dem = random.choice(VN_DEM_NAM)
        ten = random.choice(VN_TEN_NAM)
    else:
        dem = random.choice(VN_DEM_NU)
        ten = random.choice(VN_TEN_NU)

    full_name = f"{ho} {dem} {ten}"
    return full_name, gender


# ==============================================================================
# 3. SCHEMA ANALYZER (PHÂN TÍCH TỆP TEMPLATE JSON)
# ==============================================================================

class FieldMeta:
    """Lưu trữ metadata phân tích được của 1 trường dữ liệu."""
    def __init__(self, name: str):
        self.name = name
        self.inferred_type: str = "string"  # integer, float, string, datetime, date, boolean, list, dict
        self.semantic_type: str = "generic" # id, name, department, salary, email, phone, date, etc.
        self.sample_values: List[Any] = []
        self.min_val: Optional[Union[int, float]] = None
        self.max_val: Optional[Union[int, float]] = None
        self.unique_values: set = set()
        self.date_format: Optional[str] = None
        self.is_nullable: bool = False
        self.string_pattern: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "inferred_type": self.inferred_type,
            "semantic_type": self.semantic_type,
            "sample_count": len(self.sample_values),
            "min_val": self.min_val,
            "max_val": self.max_val,
            "unique_values_count": len(self.unique_values),
            "date_format": self.date_format,
            "is_nullable": self.is_nullable
        }


class SchemaAnalyzer:
    """Phân tích cấu trúc, kiểu dữ liệu và suy luận ngữ nghĩa từ Template JSON."""

    DATE_PATTERNS = [
        ("%Y-%m-%dT%H:%M:%S", r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$"),
        ("%Y-%m-%d %H:%M:%S", r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"),
        ("%Y-%m-%d", r"^\d{4}-\d{2}-\d{2}$"),
        ("%d/%m/%Y %H:%M:%S", r"^\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}$"),
        ("%d/%m/%Y", r"^\d{2}/\d{2}/\d{4}$"),
        ("%d-%m-%Y", r"^\d{2}-\d{2}-\d{4}$"),
    ]

    @classmethod
    def load_template(cls, template_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Đọc và chuẩn hóa file template thành danh sách dict."""
        with open(template_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            if not data:
                raise ValueError("Tệp template JSON là mảng rỗng!")
            return data
        elif isinstance(data, dict):
            # Nếu là 1 object đơn
            return [data]
        else:
            raise ValueError("Định dạng template JSON không hợp lệ! Phải là Array hoặc Object.")

    @classmethod
    def analyze(cls, template_path: Union[str, Path]) -> Dict[str, FieldMeta]:
        records = cls.load_template(template_path)
        fields: Dict[str, FieldMeta] = {}

        # Thu thập toàn bộ các key có trong các records
        for record in records:
            if not isinstance(record, dict):
                continue
            for k, v in record.items():
                if k not in fields:
                    fields[k] = FieldMeta(k)
                fields[k].sample_values.append(v)
                if v is None:
                    fields[k].is_nullable = True
                else:
                    try:
                        fields[k].unique_values.add(v)
                    except TypeError:
                        pass

        # Phân tích từng trường
        for name, meta in fields.items():
            non_null_samples = [v for v in meta.sample_values if v is not None]
            if not non_null_samples:
                meta.inferred_type = "string"
                meta.semantic_type = "generic"
                continue

            first_val = non_null_samples[0]

            # 1. Kiểm tra boolean
            if all(isinstance(v, bool) for v in non_null_samples):
                meta.inferred_type = "boolean"
                meta.semantic_type = "boolean"

            # 2. Kiểm tra integer (loại trừ bool vì trong Python bool là con của int)
            elif all(isinstance(v, int) and not isinstance(v, bool) for v in non_null_samples):
                meta.inferred_type = "integer"
                meta.min_val = min(non_null_samples)
                meta.max_val = max(non_null_samples)
                meta.semantic_type = cls._infer_semantic_for_number(name, meta.min_val, meta.max_val)

            # 3. Kiểm tra float
            elif all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in non_null_samples):
                meta.inferred_type = "float"
                meta.min_val = float(min(non_null_samples))
                meta.max_val = float(max(non_null_samples))
                meta.semantic_type = cls._infer_semantic_for_number(name, meta.min_val, meta.max_val)

            # 4. Kiểm tra chuỗi ngày tháng hoặc chuỗi thông thường
            elif all(isinstance(v, str) for v in non_null_samples):
                meta.inferred_type = "string"
                date_fmt = cls._detect_date_format(non_null_samples)
                if date_fmt:
                    meta.inferred_type = "datetime" if "H" in date_fmt else "date"
                    meta.date_format = date_fmt
                    meta.semantic_type = "datetime" if "H" in date_fmt else "date"
                else:
                    meta.semantic_type = cls._infer_semantic_for_string(name, non_null_samples)

            # 5. List / Dict
            elif all(isinstance(v, list) for v in non_null_samples):
                meta.inferred_type = "list"
                meta.semantic_type = "list"
            elif all(isinstance(v, dict) for v in non_null_samples):
                meta.inferred_type = "dict"
                meta.semantic_type = "dict"
            else:
                meta.inferred_type = "string"
                meta.semantic_type = "generic"

        return fields

    @classmethod
    def _detect_date_format(cls, samples: List[str]) -> Optional[str]:
        """Tự động kiểm tra xem chuỗi có phải ngày giờ theo mẫu định dạng nào."""
        for fmt, regex in cls.DATE_PATTERNS:
            if all(re.match(regex, s) for s in samples):
                try:
                    for s in samples:
                        datetime.datetime.strptime(s, fmt)
                    return fmt
                except Exception:
                    continue
        return None

    @classmethod
    def _infer_semantic_for_number(cls, name: str, min_v: Union[int, float], max_v: Union[int, float]) -> str:
        name_lower = name.lower()
        if re.search(r"\b(id|stt|index|ma|code)\b", name_lower):
            return "id"
        if re.search(r"\b(salary|luong|cost|price|amount|tien|fee|tong_tien|chi_phi)\b", name_lower):
            return "salary"
        if re.search(r"\b(age|tuoi)\b", name_lower):
            return "age"
        if re.search(r"\b(quantity|so_luong|sl)\b", name_lower):
            return "quantity"
        return "number"

    @classmethod
    def _infer_semantic_for_string(cls, name: str, samples: List[str]) -> str:
        name_lower = name.lower()
        if re.search(r"\b(name|ten|ho_ten|fullname|nhan_vien|user|buyer|seller)\b", name_lower):
            return "vietnamese_name"
        if re.search(r"\b(dept|department|phong|phong_ban|khoa|bo_phan)\b", name_lower):
            return "department"
        if re.search(r"\b(role|chuc_vu|position|title)\b", name_lower):
            return "position"
        if re.search(r"\b(email|mail)\b", name_lower):
            return "email"
        if re.search(r"\b(phone|tel|sdt|dien_thoai|mobile)\b", name_lower):
            return "phone"
        if re.search(r"\b(address|dia_chi|noi_o|que_quan)\b", name_lower):
            return "address"
        if re.search(r"\b(city|tinh|thanh_pho|province)\b", name_lower):
            return "city"
        if re.search(r"\b(status|trang_thai|tinh_trang)\b", name_lower):
            return "status"
        if re.search(r"\b(gender|gioi_tinh|sex)\b", name_lower):
            return "gender"
        if re.search(r"\b(id|code|ma|ma_so|sku|isbn)\b", name_lower):
            return "code"
        return "text"


# ==============================================================================
# 4. VALIDATION ENGINE (BỘ KIỂM TRA RÀNG BUỘC)
# ==============================================================================

class ValidationResult:
    def __init__(self, is_valid: bool, errors: List[str]):
        self.is_valid = is_valid
        self.errors = errors


class ValidationEngine:
    """Quản lý và thực thi các quy tắc validation trên từng trường và bản ghi."""

    def __init__(self, rules: Optional[Dict[str, Any]] = None):
        self.rules: Dict[str, Dict[str, Any]] = rules or {}

    def validate_record(self, record: Dict[str, Any], all_records: Optional[List[Dict[str, Any]]] = None) -> ValidationResult:
        errors = []

        for field_name, rule in self.rules.items():
            if field_name not in record:
                if rule.get("required", False):
                    errors.append(f"Trường bắt buộc '{field_name}' bị thiếu.")
                continue

            val = record[field_name]

            # 1. Nullable check
            if val is None:
                if not rule.get("nullable", True):
                    errors.append(f"Trường '{field_name}' không được phép null.")
                continue

            # 2. Choices / Enum check
            if "choices" in rule and rule["choices"]:
                if val not in rule["choices"]:
                    errors.append(f"Trường '{field_name}' có giá trị '{val}' không nằm trong danh sách cho phép {rule['choices']}.")

            # 3. Min / Max (Số lượng, giá trị, độ dài chuỗi)
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                if "min" in rule and val < rule["min"]:
                    errors.append(f"Trường '{field_name}' ({val}) nhỏ hơn min ({rule['min']}).")
                if "max" in rule and val > rule["max"]:
                    errors.append(f"Trường '{field_name}' ({val}) lớn hơn max ({rule['max']}).")
            elif isinstance(val, str):
                if "min_length" in rule and len(val) < rule["min_length"]:
                    errors.append(f"Độ dài '{field_name}' ({len(val)}) nhỏ hơn min_length ({rule['min_length']}).")
                if "max_length" in rule and len(val) > rule["max_length"]:
                    errors.append(f"Độ dài '{field_name}' ({len(val)}) lớn hơn max_length ({rule['max_length']}).")

            # 4. Regex Pattern check
            if "pattern" in rule or "regex" in rule:
                pat = rule.get("pattern") or rule.get("regex")
                if isinstance(val, str) and not re.search(pat, val):
                    errors.append(f"Trường '{field_name}' ('{val}') không khớp regex {pat}.")

            # 5. Type check
            if "type" in rule:
                expected_type = rule["type"]
                if expected_type == "integer" and not (isinstance(val, int) and not isinstance(val, bool)):
                    errors.append(f"Trường '{field_name}' phải là integer.")
                elif expected_type == "float" and not isinstance(val, (int, float)):
                    errors.append(f"Trường '{field_name}' phải là float.")
                elif expected_type == "string" and not isinstance(val, str):
                    errors.append(f"Trường '{field_name}' phải là string.")
                elif expected_type == "boolean" and not isinstance(val, bool):
                    errors.append(f"Trường '{field_name}' phải là boolean.")

        return ValidationResult(len(errors) == 0, errors)

    def validate_dataset(self, records: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
        """Kiểm tra toàn bộ dataset (bao gồm unique check)."""
        dataset_errors = []

        # Unique checks
        for field_name, rule in self.rules.items():
            if rule.get("unique", False):
                seen = set()
                for idx, r in enumerate(records):
                    val = r.get(field_name)
                    if val is not None:
                        if val in seen:
                            dataset_errors.append({
                                "index": idx,
                                "field": field_name,
                                "error": f"Trùng lặp giá trị '{val}' ở trường unique '{field_name}'"
                            })
                        else:
                            seen.add(val)

        # Record level checks
        for idx, r in enumerate(records):
            res = self.validate_record(r, records)
            if not res.is_valid:
                for err in res.errors:
                    dataset_errors.append({
                        "index": idx,
                        "field": "record",
                        "error": err
                    })

        return len(dataset_errors) == 0, dataset_errors


# ==============================================================================
# 5. DATA GENERATOR (ENGINE SINH DỮ LIỆU CHÍNH)
# ==============================================================================

class DataGenerator:
    """Điều phối toàn bộ quá trình sinh dữ liệu tuân thủ template và validation rules."""

    def __init__(
        self,
        template_path: Union[str, Path],
        rules: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None
    ):
        self.template_path = Path(template_path)
        if seed is not None:
            random.seed(seed)

        # Phân tích schema từ template
        self.fields_meta = SchemaAnalyzer.analyze(self.template_path)
        self.raw_records = SchemaAnalyzer.load_template(self.template_path)

        # Khởi tạo rules: Kết hợp rules suy luận tự động + rules người dùng chỉ định
        self.rules = self._merge_rules(rules or {})
        self.validator = ValidationEngine(self.rules)

    def _merge_rules(self, user_rules: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Hợp nhất các ràng buộc ngầm định từ template với quy tắc tùy biến của user."""
        merged: Dict[str, Dict[str, Any]] = {}

        for field_name, meta in self.fields_meta.items():
            field_rule: Dict[str, Any] = {
                "type": meta.inferred_type,
                "semantic": meta.semantic_type,
                "nullable": meta.is_nullable
            }

            # Nếu là ID -> mặc định unique và auto_increment
            if meta.semantic_type == "id":
                field_rule["unique"] = True
                field_rule["auto_increment"] = (meta.inferred_type == "integer")
                field_rule["start"] = meta.min_val or 1

            # Nếu là số (ngoại trừ ID) -> lấy min / max từ template làm căn cứ
            if meta.inferred_type in ("integer", "float") and meta.semantic_type != "id":
                if meta.min_val is not None:
                    field_rule["min"] = meta.min_val
                if meta.max_val is not None:
                    field_rule["max"] = max(meta.max_val, (meta.min_val or 0) + 10)

            # Nếu trường string là dạng phân loại (department, status, gender...) hoặc text có ít giá trị lặp lại
            CATEGORICAL_SEMANTICS = {"department", "status", "gender", "position"}
            if (meta.semantic_type in CATEGORICAL_SEMANTICS or (meta.semantic_type == "text" and meta.inferred_type == "string")) and 1 < len(meta.unique_values) <= 15:
                field_rule["choices"] = list(meta.unique_values)

            # Ngày tháng
            if meta.date_format:
                field_rule["date_format"] = meta.date_format

            merged[field_name] = field_rule

        # Ghi đè bởi user_rules nếu có
        for k, v in user_rules.items():
            if k in merged:
                merged[k].update(v)
            else:
                merged[k] = v

        return merged

    def generate(self, count: int) -> List[Dict[str, Any]]:
        """Sinh ra danh sách gồm `count` bản ghi đáp ứng 100% schema và validation."""
        records: List[Dict[str, Any]] = []
        unique_trackers: Dict[str, set] = {
            fname: set() for fname, rule in self.rules.items() if rule.get("unique", False)
        }

        # Khởi tạo auto increment counters
        auto_inc_counters: Dict[str, int] = {}
        for fname, rule in self.rules.items():
            if rule.get("auto_increment", False):
                auto_inc_counters[fname] = rule.get("start", 1)

        print_interval = max(count // 10, 50000) if count >= 50000 else 0

        for i in range(count):
            if print_interval and (i + 1) % print_interval == 0:
                percent = int((i + 1) * 100 / count)
                sys.stdout.write(f"   ⏳ Tiến độ: {i + 1:,} / {count:,} bản ghi ({percent}%)...\n")
                sys.stdout.flush()
            record = self._generate_single_record(i, auto_inc_counters, unique_trackers)
            records.append(record)

        # Thẩm định lại toàn bộ tập dữ liệu (với dataset lớn hơn 100k bản ghi, lấy mẫu 50,000 bản ghi để tối ưu tốc độ)
        if count > 100000:
            sample_records = random.sample(records, 50000)
            is_valid, errors = self.validator.validate_dataset(sample_records)
        else:
            is_valid, errors = self.validator.validate_dataset(records)

        if not is_valid:
            sys.stderr.write(f"[Cảnh báo Validation] Phát hiện {len(errors)} vấn đề: {errors[:3]}\n")

        return records

    def _generate_single_record(
        self,
        index: int,
        auto_inc_counters: Dict[str, int],
        unique_trackers: Dict[str, set]
    ) -> Dict[str, Any]:
        """Sinh 1 bản ghi duy nhất đảm bảo pass các rule."""
        max_retries = 100

        for _ in range(max_retries):
            record: Dict[str, Any] = {}
            full_name, gender = generate_vietnamese_name()

            for fname, meta in self.fields_meta.items():
                rule = self.rules.get(fname, {})

                # Kiểm tra auto increment (lấy giá trị hiện tại, chưa tăng vội)
                if rule.get("auto_increment", False):
                    val = auto_inc_counters[fname]
                    record[fname] = val
                    continue

                val = self._generate_field_value(fname, meta, rule, full_name, gender, index)

                # Nếu là unique thì phải thử giá trị chưa xuất hiện
                if rule.get("unique", False):
                    retry_unique = 0
                    while val in unique_trackers[fname] and retry_unique < 50:
                        val = self._generate_field_value(fname, meta, rule, full_name, gender, index + retry_unique + 1)
                        retry_unique += 1

                record[fname] = val

            # Validate nhanh bản ghi này
            val_res = self.validator.validate_record(record)
            if val_res.is_valid:
                # Ghi nhận unique và tăng auto increment
                for fname, r_rule in self.rules.items():
                    if r_rule.get("auto_increment", False):
                        auto_inc_counters[fname] += r_rule.get("step", 1)
                    if r_rule.get("unique", False) and fname in record:
                        unique_trackers[fname].add(record[fname])
                return record

        # Fallback ghi nhận unique và tăng auto inc nếu hết số lần retry
        for fname, r_rule in self.rules.items():
            if r_rule.get("auto_increment", False):
                auto_inc_counters[fname] += r_rule.get("step", 1)
            if r_rule.get("unique", False) and fname in record:
                unique_trackers[fname].add(record[fname])
        return record

    def _generate_field_value(
        self,
        fname: str,
        meta: FieldMeta,
        rule: Dict[str, Any],
        full_name: str,
        gender: str,
        index: int
    ) -> Any:
        # 1. Nullable simulation
        if rule.get("nullable", False) and random.random() < rule.get("null_ratio", 0.05):
            return None

        # 2. Explicit choices / enum
        if "choices" in rule and rule["choices"]:
            return random.choice(rule["choices"])

        semantic = rule.get("semantic", meta.semantic_type)
        val_type = rule.get("type", meta.inferred_type)

        # 3. Theo ngữ nghĩa chuyên biệt
        if semantic == "vietnamese_name":
            return full_name

        if semantic == "gender":
            return gender

        if semantic == "department":
            if "choices" in rule and rule["choices"]:
                return random.choice(rule["choices"])
            if meta.unique_values:
                pool = list(meta.unique_values) + VN_PHONG_BAN[:3]
                return random.choice(pool)
            return random.choice(VN_PHONG_BAN)

        if semantic == "position":
            return random.choice(VN_CHUC_VU)

        if semantic == "salary":
            min_sal = rule.get("min", meta.min_val or 10000000)
            max_sal = rule.get("max", meta.max_val or 50000000)
            if min_sal > max_sal:
                min_sal, max_sal = max_sal, min_sal
            step = rule.get("step", 500000)
            if step <= 0:
                step = 500000
            min_steps = int(min_sal / step)
            max_steps = int(max_sal / step)
            if min_steps >= max_steps:
                max_steps = min_steps + 10
            val = random.randint(min_steps, max_steps) * step
            return float(val) if val_type == "float" else int(val)

        if semantic in ("datetime", "date"):
            fmt = rule.get("date_format") or meta.date_format or "%Y-%m-%dT%H:%M:%S"
            start_date_str = rule.get("start_date", "2026-01-01")
            end_date_str = rule.get("end_date", "2026-12-31")
            try:
                dt_start = datetime.datetime.fromisoformat(start_date_str)
                dt_end = datetime.datetime.fromisoformat(end_date_str)
            except Exception:
                dt_start = datetime.datetime(2026, 1, 1)
                dt_end = datetime.datetime(2026, 12, 31)

            delta = (dt_end - dt_start).total_seconds()
            random_second = random.uniform(0, max(delta, 1))
            res_dt = dt_start + datetime.timedelta(seconds=random_second)
            return res_dt.strftime(fmt)

        if semantic == "email":
            clean_name = remove_vietnamese_accents(full_name).lower().replace(" ", ".")
            domain = random.choice(EMAIL_DOMAINS)
            suffix = random.randint(10, 999)
            return f"{clean_name}{suffix}@{domain}"

        if semantic == "phone":
            prefix = random.choice(VN_PHONE_PREFIXES)
            suffix = "".join([str(random.randint(0, 9)) for _ in range(7)])
            return f"{prefix}{suffix}"

        if semantic == "address":
            street_num = random.randint(1, 999)
            street = random.choice(VN_DUONG)
            city = random.choice(VN_TINH_THANH)
            return f"Số {street_num} đường {street}, {city}"

        if semantic == "city":
            return random.choice(VN_TINH_THANH)

        if semantic == "status":
            return random.choice(["Active", "Inactive", "Pending", "Approved"])

        if semantic == "code":
            pattern = rule.get("pattern") or rule.get("regex")
            if pattern:
                return self._generate_from_pattern(pattern)
            prefix = re.sub(r"[^A-Za-z]", "", fname).upper()[:3] or "CODE"
            return f"{prefix}{index + 1:04d}"

        if semantic == "age":
            min_age = rule.get("min", 22)
            max_age = rule.get("max", 60)
            return random.randint(min_age, max_age)

        # 4. Fallback theo kiểu dữ liệu cơ bản
        if val_type == "integer":
            min_v = rule.get("min", meta.min_val or 1)
            max_v = rule.get("max", meta.max_val or 100)
            if min_v > max_v:
                min_v, max_v = max_v, min_v
            return random.randint(int(min_v), int(max_v))

        if val_type == "float":
            min_v = rule.get("min", meta.min_val or 0.0)
            max_v = rule.get("max", meta.max_val or 100.0)
            if min_v > max_v:
                min_v, max_v = max_v, min_v
            return round(random.uniform(float(min_v), float(max_v)), 2)

        if val_type == "boolean":
            return random.choice([True, False])

        # Chuỗi chung
        if meta.sample_values:
            return str(random.choice(meta.sample_values))
        return f"{fname}_{index + 1}"

    def _generate_from_pattern(self, pattern: str) -> str:
        """Sinh chuỗi đơn giản theo pattern cơ bản (hỗ trợ \\d, \\w, prefix)."""
        res = []
        i = 0
        while i < len(pattern):
            if pattern[i] == "^" or pattern[i] == "$":
                i += 1
                continue
            if pattern[i:i+2] == "\\d":
                res.append(str(random.randint(0, 9)))
                i += 2
            elif pattern[i:i+2] == "\\w":
                res.append(random.choice(string.ascii_letters + string.digits))
                i += 2
            elif pattern[i] == "[":
                end = pattern.find("]", i)
                if end != -1:
                    opts = pattern[i+1:end]
                    res.append(random.choice(opts))
                    i = end + 1
                else:
                    res.append(pattern[i])
                    i += 1
            else:
                res.append(pattern[i])
                i += 1
        return "".join(res)

    def export(self, records: List[Dict[str, Any]], output_path: Union[str, Path], file_format: str = "json") -> Path:
        """Xuất dữ liệu sinh ra tệp JSON hoặc CSV."""
        out_path = Path(output_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if file_format.lower() == "csv" or out_path.suffix.lower() == ".csv":
            if not records:
                with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
                    pass
                return out_path

            fieldnames = list(records[0].keys())
            with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(records)
        else:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

        return out_path
