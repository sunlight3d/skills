#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import shutil
import glob

def run_media_sync(target_dir="/Users/hoangnd/Downloads/Lich_Su_Chat_COLE_KHOA_HOC_UNG_DUNG_AI_LOGISTIC"):
    os.makedirs(target_dir, exist_ok=True)
    
    src_cache = "/Users/hoangnd/Library/Application Support/ZaloData/media/1859138295562840254/ZaloDownloads/resource/g4269552121585403442/Cache"
    src_file = "/Users/hoangnd/Library/Application Support/ZaloData/media/1859138295562840254/ZaloDownloads/resource/g4269552121585403442/file"

    image_mapping = [
        ("1795150163021_6452293759002619897_g4269552121585403442_n", "Anh_01_DanhSach_HocVien_ThangLoi_1.jpg"),
        ("1795155803993_1121652544162783970_g4269552121585403442_n", "Anh_02_Loi_DoiMatKhau_LMS.jpg"),
        ("1795168312857_1111515452578799134_g4269552121585403442_n", "Anh_03_DanhSach_HocVien_ThangLoi_2.jpg"),
        ("1795223668994_7816289939485517835_g4269552121585403442_n", "Anh_04_Slide_KhaiMac_KhoaHoc.jpg"),
        ("1795226939131_3126146118168294416_g4269552121585403442_n", "Anh_05_RustDesk_DoHongHanh.jpg"),
        ("1795230628814_2247572612573516354_g4269552121585403442_n", "Anh_06_RustDesk_Remote.jpg"),
        ("1795311085215_4229392537865123523_g4269552121585403442_n", "Anh_07_Teams_PhongCho_DoHongHanh.jpg"),
        ("1795311111415_1859138295562840254_g4269552121585403442_n", "Anh_08_Teams_PhongCho_NguyenDucHoang.jpg"),
        ("1795311160667_8780349592057568936_g4269552121585403442_n", "Anh_09_Teams_PhongCho_LeVanDien.jpg"),
        ("1795311556905_2839465244787490069_g4269552121585403442_n", "Anh_10_Teams_PhongCho_VietAnh.jpg"),
        ("1795311586154_5387198584249021617_g4269552121585403442_n", "Anh_11_Teams_PhongCho_PhamAnhTai.jpg"),
        ("1795312224741_5387198584249021617_g4269552121585403442_n", "Anh_12_Teams_PhongCho_PhamAnhTai_2.jpg"),
    ]

    copied_images = []
    for src_id, dest_name in image_mapping:
        src_path = os.path.join(src_cache, src_id)
        dst_path = os.path.join(target_dir, dest_name)
        if os.path.exists(src_path) and not os.path.exists(dst_path):
            shutil.copy2(src_path, dst_path)
            copied_images.append(dest_name)

    # Attached file
    attached_src = os.path.join(src_file, "1795275284698_1859138295562840254_g4269552121585403442")
    attached_dst = os.path.join(target_dir, "File_DinhKem_01_Note_Bai_Hoc_Ngay_21_11_2026.txt")
    if os.path.exists(attached_src) and not os.path.exists(attached_dst):
        shutil.copy2(attached_src, attached_dst)

    return copied_images

if __name__ == "__main__":
    run_media_sync()
