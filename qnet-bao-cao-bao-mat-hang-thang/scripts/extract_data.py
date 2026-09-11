import os
import sys
import json
import argparse
import openpyxl
import pandas as pd

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Trích xuất dữ liệu Excel báo cáo bảo mật")
    parser.add_argument("-i", "--input-dir", required=True, help="Thư mục chứa các tệp Excel")
    parser.add_argument("-o", "--output-dir", default=None, help="Thư mục xuất file kết quả")
    parser.add_argument("-r", "--run-app", action="store_true", help="Tự động chạy Web Dashboard sau khi trích xuất")
    parser.add_argument("-p", "--port", default=8501, type=int, help="Cổng chạy Web server")
    return parser.parse_args()

def extract_security_data(input_dir, output_dir):
    print(f"[*] Đang quét thư mục: {input_dir}")
    excel_files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx') and not f.startswith('~$')]
    
    if not excel_files:
        print("[!] Không tìm thấy tệp Excel (.xlsx) nào trong thư mục!")
        return None
        
    print(f"[*] Tìm thấy {len(excel_files)} tệp Excel: {excel_files}")
    
    # Nhận diện file báo cáo phụ lục và file dữ liệu thô
    bc_file = None
    data_file = None
    
    for f in excel_files:
        f_lower = f.lower()
        if "phuluc" in f_lower or "báo cáo" in f_lower or "bc" in f_lower:
            bc_file = os.path.join(input_dir, f)
        elif "data" in f_lower or "attt" in f_lower:
            data_file = os.path.join(input_dir, f)
            
    if not bc_file and excel_files:
        bc_file = os.path.join(input_dir, excel_files[0])
    if not data_file and len(excel_files) > 1:
        data_file = os.path.join(input_dir, excel_files[1])
    elif not data_file:
        data_file = bc_file

    summary = {}
    
    # 1. Tấn công mạng (Firewall PA5020 & PA5250)
    print("[*] Đang đọc dữ liệu Tấn công mạng (Firewall)...")
    threats = []
    try:
        df_pl1 = pd.read_excel(bc_file, sheet_name='Phụ Lục 1', header=2)
        for _, r in df_pl1.iterrows():
            name = str(r.iloc[0]).strip()
            if name and name != 'nan' and 'Tổng' not in name:
                threats.append({
                    'name': name,
                    'severity': str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else 'N/A',
                    'count': int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0,
                    'device': 'Palo Alto PA5020'
                })
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 1: {e}")
        
    try:
        df_pl5 = pd.read_excel(bc_file, sheet_name='Phụ Lục 5', header=2)
        for _, r in df_pl5.iterrows():
            name = str(r.iloc[0]).strip()
            if name and name != 'nan' and 'Tổng' not in name:
                try:
                    cnt = int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0
                except:
                    cnt = 0
                threats.append({
                    'name': name,
                    'severity': str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else 'N/A',
                    'count': cnt,
                    'device': 'Palo Alto PA5250'
                })
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 5: {e}")
        
    summary['network_threats'] = threats
    
    # 2. FireEye NX Malware (PL15)
    print("[*] Đang đọc dữ liệu Mã độc chuyên sâu (FireEye NX)...")
    malware_nx = []
    try:
        df_pl15 = pd.read_excel(bc_file, sheet_name='Phụ Lục 15', header=2)
        for _, r in df_pl15.head(20).iterrows():
            name = str(r.iloc[1]).strip()
            if name and name != 'nan':
                try:
                    cnt = int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0
                except:
                    cnt = 0
                malware_nx.append({
                    'name': name,
                    'count': cnt,
                    'device': str(r.iloc[3]).strip() if len(r) > 3 and pd.notna(r.iloc[3]) else 'FireEye NX7400'
                })
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 15: {e}")
    summary['malware_fireeye'] = malware_nx

    # 3. Fortigate Virus (PL9)
    print("[*] Đang đọc dữ liệu Virus (Fortigate)...")
    virus_forti = []
    try:
        df_pl9 = pd.read_excel(bc_file, sheet_name='Phụ Lục 9', header=2)
        for _, r in df_pl9.head(20).iterrows():
            name = str(r.iloc[1]).strip()
            if name and name != 'nan':
                try:
                    cnt = int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0
                except:
                    cnt = 0
                virus_forti.append({'name': name, 'count': cnt})
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 9: {e}")
    summary['virus_fortigate'] = virus_forti

    # 4. Top Attack Source IPs (PL2 & PL6)
    print("[*] Đang đọc IP Nguồn tấn công (Palo Alto)...")
    top_sources_pa5020 = []
    top_sources_pa5250 = []
    try:
        df_pl2 = pd.read_excel(bc_file, sheet_name='Phụ Lục 2', header=2, nrows=10000)
        for _, r in df_pl2.head(15).iterrows():
            ip = str(r.iloc[0]).strip()
            if ip and ip != 'nan':
                top_sources_pa5020.append({
                    'ip': ip,
                    'direction': str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else 'Inbound',
                    'count': int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0,
                    'device': 'PA5020'
                })
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 2: {e}")
        
    try:
        df_pl6 = pd.read_excel(bc_file, sheet_name='Phụ Lục 6', header=2, nrows=10000)
        for _, r in df_pl6.head(15).iterrows():
            ip = str(r.iloc[0]).strip()
            if ip and ip != 'nan':
                top_sources_pa5250.append({
                    'ip': ip,
                    'direction': str(r.iloc[1]).strip() if pd.notna(r.iloc[1]) else 'Inbound',
                    'count': int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0,
                    'device': 'PA5250'
                })
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 6: {e}")
    summary['top_sources_pa5020'] = top_sources_pa5020
    summary['top_sources_pa5250'] = top_sources_pa5250

    # 5. Top Target Destination IPs (PL3 & PL7)
    top_targets_pa5020 = []
    top_targets_pa5250 = []
    try:
        df_pl3 = pd.read_excel(bc_file, sheet_name='Phụ Lục 3', header=2)
        for _, r in df_pl3.head(15).iterrows():
            ip = str(r.iloc[0]).strip()
            if ip and ip != 'nan':
                top_targets_pa5020.append({
                    'ip': ip,
                    'count': int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0,
                    'device': 'PA5020'
                })
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 3: {e}")
        
    try:
        df_pl7 = pd.read_excel(bc_file, sheet_name='Phụ Lục 7', header=2)
        for _, r in df_pl7.head(15).iterrows():
            ip = str(r.iloc[0]).strip()
            if ip and ip != 'nan':
                top_targets_pa5250.append({
                    'ip': ip,
                    'count': int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0,
                    'device': 'PA5250'
                })
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 7: {e}")
    summary['top_targets_pa5020'] = top_targets_pa5020
    summary['top_targets_pa5250'] = top_targets_pa5250

    # 6. Accounts Login Fail (PL12 & PL13)
    print("[*] Đang đọc tài khoản đăng nhập thất bại (SSO & Mail)...")
    sso_fails = []
    email_fails = []
    try:
        df_pl12 = pd.read_excel(bc_file, sheet_name='Phụ Lục 12', header=2)
        for _, r in df_pl12.head(25).iterrows():
            acc = str(r.iloc[1]).strip()
            if acc and acc != 'nan':
                try:
                    cnt = int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0
                except:
                    cnt = 0
                sso_fails.append({'account': acc, 'count': cnt, 'type': 'SSO Portal'})
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 12: {e}")
        
    try:
        df_pl13 = pd.read_excel(bc_file, sheet_name='Phụ Lục 13', header=2)
        for _, r in df_pl13.head(25).iterrows():
            acc = str(r.iloc[1]).strip()
            if acc and acc != 'nan':
                try:
                    cnt = int(r.iloc[2]) if pd.notna(r.iloc[2]) else 0
                except:
                    cnt = 0
                email_fails.append({'account': acc, 'count': cnt, 'type': 'Email Server'})
    except Exception as e:
        print(f"[-] Không đọc được Phụ lục 13: {e}")
    summary['sso_login_fail_top'] = sso_fails
    summary['email_login_fail_top'] = email_fails

    # 7. Botnet CnC & Provinces
    print("[*] Đang đọc dữ liệu Botnet CnC các tỉnh...")
    cnc_details_all = []
    cnc_prov_data = []
    all_provinces = []
    try:
        sheet_cnc = 'DW Giám sát trực tiếp CnC' if 'DW Giám sát trực tiếp CnC' in pd.ExcelFile(data_file).sheet_names else 'Chi tiet CnC'
        df_cnc = pd.read_excel(data_file, sheet_name=sheet_cnc)
        
        for _, r in df_cnc.sort_values(by='Số lượng', ascending=False).iterrows():
            if pd.notna(r['Tỉnh mới']):
                cnc_details_all.append({
                    'province': str(r['Tỉnh mới']).strip(),
                    'src_ip': str(r['Địa chỉ IP LAN']).strip(),
                    'dst_cnc_ip': str(r['Địa chỉ CNC']).strip(),
                    'port': int(r['Port']) if pd.notna(r['Port']) else 0,
                    'count': int(r['Số lượng']) if pd.notna(r['Số lượng']) else 0,
                    'zone': str(r['Source Zone']).strip() if pd.notna(r['Source Zone']) else 'LAN',
                    'device': str(r['Thiết bị giám sát']).strip() if pd.notna(r['Thiết bị giám sát']) else 'N/A'
                })
        
        all_provinces = sorted(list(set(c['province'] for c in cnc_details_all if c['province'])))
        
        # Thống kê tổng hợp theo tỉnh
        cnc_prov_df = df_cnc.groupby('Tỉnh mới').agg(
            total_connections=('Số lượng', 'sum'),
            lan_count=('Địa chỉ IP LAN', 'nunique'),
            cnc_count=('Địa chỉ CNC', 'nunique')
        ).reset_index().sort_values(by='total_connections', ascending=False)
        
        cnc_prov_data = cnc_prov_df.head(15).to_dict(orient='records')
    except Exception as e:
        print(f"[-] Không đọc được dữ liệu CnC: {e}")
        
    summary['cnc_details_all'] = cnc_details_all
    summary['cnc_details_top'] = cnc_details_all[:100]
    summary['cnc_by_province'] = cnc_prov_data
    summary['provinces_list'] = all_provinces

    # 8. Patch Manager & Antivirus
    print("[*] Đang đọc dữ liệu Quản lý Bản vá & Antivirus...")
    try:
        df_patch = pd.read_excel(data_file, sheet_name='Chi tiet patch')
        top_unpatched_offices = df_patch['Remote Office'].value_counts().head(10).reset_index()
        top_unpatched_offices.columns = ['office', 'unpatched_count']
        summary['unpatched_offices'] = top_unpatched_offices.to_dict(orient='records')

        top_patch_ids = df_patch['Bulletin ID'].value_counts().head(8).reset_index()
        top_patch_ids.columns = ['bulletin_id', 'count']
        summary['top_missing_bulletins'] = top_patch_ids.to_dict(orient='records')
    except Exception as e:
        print(f"[-] Không đọc được dữ liệu Patch: {e}")
        summary['unpatched_offices'] = []
        summary['top_missing_bulletins'] = []

    # 9. Totals
    summary['totals'] = {
        'total_network_attacks_pl1_pl5': sum(t['count'] for t in summary['network_threats']),
        'total_cnc_connections': sum(c['count'] for c in cnc_details_all),
        'total_unique_sso_failed_users': len(sso_fails),
        'total_unique_email_failed_users': len(email_fails),
        'total_missing_patch_instances': len(summary.get('unpatched_offices', [])),
        'total_nx_malware_alerts': sum(m['count'] for m in malware_nx)
    }

    out_file = os.path.join(output_dir, "dashboard_data.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"[+] Thành công! Đã trích xuất dữ liệu lưu tại: {out_file}")
    return out_file

def main():
    args = parse_args()
    input_dir = os.path.abspath(args.input_dir)
    output_dir = os.path.abspath(args.output_dir) if args.output_dir else input_dir
    
    out_json = extract_security_data(input_dir, output_dir)
    if not out_json:
        sys.exit(1)
        
    if args.run_app:
        import subprocess
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        app_script = os.path.join(current_script_dir, "app.py")
        cmd = [sys.executable, "-m", "streamlit", "run", app_script, "--server.port", str(args.port), "--", "--data-dir", output_dir]
        print(f"[*] Đang khởi động Web Dashboard trên http://localhost:{args.port} ...")
        subprocess.run(cmd)

if __name__ == "__main__":
    main()
