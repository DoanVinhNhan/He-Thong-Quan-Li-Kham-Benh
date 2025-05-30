# app_logic.py
import datetime
import csv 
import os 
from typing import Optional, List, Tuple, Any 

from models import BenhNhan, PatientInQueue, DATE_FORMAT_CSV, BacSi, PhongKham # Thêm BacSi, PhongKham
from custom_structures import PriorityQueue, CustomLinkedList, CustomHashTable 

PATIENTS_CSV_FILE = "patients_data.csv" 
DOCTORS_CSV_FILE = "doctors_data.csv"
CLINICS_CSV_FILE = "clinics_data.csv"

class HeThongQuanLyKhamBenh:
    def __init__(self, hash_table_initial_size: int = 100):
        # Quản lý bệnh nhân
        self.danh_sach_benh_nhan: CustomHashTable = CustomHashTable(initial_size=hash_table_initial_size)
        self.next_patient_id_counter = 1 
        self._load_data_from_csv(PATIENTS_CSV_FILE, BenhNhan, self.danh_sach_benh_nhan, self._update_next_patient_id)
        
        # Quản lý hàng đợi
        self.hang_doi_kham: PriorityQueue = PriorityQueue()
        self.danh_sach_da_kham_hom_nay: CustomLinkedList = CustomLinkedList()

        # Quản lý bác sĩ
        self.danh_sach_bac_si: CustomHashTable = CustomHashTable(initial_size=50)
        self.next_doctor_id_counter = 1
        self._load_data_from_csv(DOCTORS_CSV_FILE, BacSi, self.danh_sach_bac_si, self._update_next_doctor_id, key_attr='ma_bac_si', prefix='BS')

        # Quản lý phòng khám
        self.danh_sach_phong_kham: CustomHashTable = CustomHashTable(initial_size=20)
        self.next_clinic_id_counter = 1
        self._load_data_from_csv(CLINICS_CSV_FILE, PhongKham, self.danh_sach_phong_kham, self._update_next_clinic_id, key_attr='ma_phong_kham', prefix='PK')

    def _get_csv_fieldnames(self, model_class) -> List[str]:
        if model_class == BenhNhan:
            return ["ma_bn", "ho_ten", "ngay_sinh", "gioi_tinh", "dia_chi", "sdt", "cccd", "bhyt", "tien_su_benh_an", "di_ung_thuoc", "thoi_diem_dang_ky_he_thong", "lich_su_kham_benh"]
        elif model_class == BacSi:
            return ["ma_bac_si", "ho_ten_bac_si", "chuyen_khoa", "danh_sach_ma_phong_kham"]
        elif model_class == PhongKham:
            return ["ma_phong_kham", "ten_phong_kham", "chuyen_khoa_pk", "danh_sach_ma_bac_si"]
        return []

    def _load_data_from_csv(self, csv_file_path: str, model_class: type, target_hash_table: CustomHashTable, id_update_func, key_attr: str = 'ma_bn', prefix: str = 'BN'):
        print(f"Đang tải dữ liệu từ {csv_file_path}...")
        if not os.path.exists(csv_file_path):
            print(f"File {csv_file_path} không tồn tại. Bỏ qua việc tải.")
            return
        
        max_id_num = 0; loaded_count = 0
        fieldnames = self._get_csv_fieldnames(model_class)
        if not fieldnames: 
            print(f"Không tìm thấy fieldnames cho {model_class}. Không thể tải."); return

        required_fields_map = {
            BenhNhan: ["ma_bn", "ho_ten", "ngay_sinh", "gioi_tinh", "sdt", "cccd"],
            BacSi: ["ma_bac_si", "ho_ten_bac_si", "chuyen_khoa"],
            PhongKham: ["ma_phong_kham", "ten_phong_kham", "chuyen_khoa_pk"]
        }
        required_fields = required_fields_map.get(model_class, [key_attr])


        try:
            with open(csv_file_path, mode='r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                if not reader.fieldnames or not all(f in reader.fieldnames for f in required_fields):
                    print(f"Lỗi: File CSV {csv_file_path} thiếu header quan trọng. Không tải."); return
                
                for row_num, row in enumerate(reader, 1):
                    try:
                        if not all(key in row and row[key] for key in required_fields):
                            print(f"Cảnh báo: Dòng {row_num} trong {csv_file_path} thiếu thông tin bắt buộc. Bỏ qua."); continue
                        
                        item_obj = model_class.from_csv_row(row)
                        
                        if model_class == BenhNhan and (not item_obj.cccd or item_obj.cccd == "N/A_DEFAULT"): # Kiểm tra CCCD cho BenhNhan
                             print(f"Cảnh báo: Dòng {row_num} (BN: {item_obj.ma_bn}) thiếu CCCD. Bỏ qua."); continue

                        item_id = getattr(item_obj, key_attr)
                        target_hash_table.put(item_id, item_obj)
                        loaded_count +=1
                        if item_id.startswith(prefix):
                            try: 
                                id_num = int(item_id[len(prefix):])
                                if id_num > max_id_num: max_id_num = id_num
                            except ValueError: pass 
                    except Exception as e_row: print(f"Lỗi xử lý dòng {row_num} trong {csv_file_path}: {e_row}")
            id_update_func(max_id_num + 1)
            print(f"Đã tải thành công {loaded_count} bản ghi từ {csv_file_path}. ID tiếp theo sẽ từ: {getattr(self, f'next_{model_class.__name__.lower()}_id_counter', max_id_num + 1)}")
        except Exception as e: print(f"Lỗi nghiêm trọng khi tải file {csv_file_path}: {e}")

    def _update_next_patient_id(self, next_id: int): self.next_patient_id_counter = next_id
    def _update_next_doctor_id(self, next_id: int): self.next_doctor_id_counter = next_id
    def _update_next_clinic_id(self, next_id: int): self.next_clinic_id_counter = next_id

    def _save_data_to_csv(self, csv_file_path: str, model_class: type, source_hash_table: CustomHashTable):
        fieldnames = self._get_csv_fieldnames(model_class)
        if not fieldnames: return
        all_items = source_hash_table.get_all_values()
        try:
            with open(csv_file_path, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader(); saved_count = 0
                for item in all_items: 
                    if isinstance(item, model_class): writer.writerow(item.to_csv_row()); saved_count +=1
        except Exception as e: print(f"Lỗi khi lưu file {csv_file_path}: {e}")

    # --- Quản lý Bệnh nhân ---
    def _tao_ma_benh_nhan(self) -> str:
        ma_bn = f"BN{self.next_patient_id_counter:04d}"; self.next_patient_id_counter += 1; return ma_bn

    def tao_ho_so_benh_nhan(self, ho_ten: str, ngay_sinh_str: str, gioi_tinh: str, dia_chi: str, sdt: str, cccd: str, bhyt: str = "", tien_su: str = "", di_ung: str = "") -> Tuple[Optional[BenhNhan], str, str]:
        if not all([ho_ten.strip(), ngay_sinh_str.strip(), gioi_tinh.strip(), sdt.strip(), cccd.strip()]):
            return None, "Họ tên, Ngày sinh, Giới tính, SĐT và CCCD là các trường bắt buộc (*).", "ERROR"
        try: ngay_sinh_obj = datetime.datetime.strptime(ngay_sinh_str, DATE_FORMAT_CSV).date()
        except ValueError: return None, f"Định dạng Ngày sinh '{ngay_sinh_str}' không hợp lệ.", "ERROR"
        ma_bn = self._tao_ma_benh_nhan()
        if self.danh_sach_benh_nhan.contains(ma_bn): return None, f"Lỗi: Mã BN {ma_bn} đã tồn tại.", "ERROR"
        benh_nhan = BenhNhan(ma_bn, ho_ten, ngay_sinh_obj, gioi_tinh, dia_chi, sdt, cccd, bhyt, tien_su, di_ung)
        self.danh_sach_benh_nhan.put(ma_bn, benh_nhan); self._save_data_to_csv(PATIENTS_CSV_FILE, BenhNhan, self.danh_sach_benh_nhan)
        return benh_nhan, f"Đã tạo hồ sơ thành công cho BN: {benh_nhan.ma_bn}", "INFO"

    def tim_benh_nhan_theo_ma(self, ma_bn: str) -> Optional[BenhNhan]:
        return self.danh_sach_benh_nhan.get(ma_bn)

    def cap_nhat_thong_tin_benh_nhan(self, ma_bn: str, **kwargs) -> Tuple[bool, str, str]:
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn)
        if not benh_nhan: return False, f"BN mã {ma_bn} không tồn tại.", "ERROR"
        new_cccd = kwargs.get("cccd")
        if new_cccd is not None and not str(new_cccd).strip(): return False, f"CCCD không được để trống cho BN {ma_bn}.", "ERROR"
        updated = False
        for key, value in kwargs.items():
            if hasattr(benh_nhan, key) and value is not None:
                current_value = getattr(benh_nhan, key); new_value = value
                if key == "ngay_sinh" and isinstance(value, str):
                    if not value.strip(): new_value = None
                    else:
                        try: new_value = datetime.datetime.strptime(value, DATE_FORMAT_CSV).date()
                        except ValueError: return False, f"Ngày sinh '{value}' không hợp lệ.", "ERROR"
                if current_value != new_value: setattr(benh_nhan, key, new_value); updated = True
        if updated: self._save_data_to_csv(PATIENTS_CSV_FILE, BenhNhan, self.danh_sach_benh_nhan); return True, f"Đã cập nhật BN {ma_bn}.", "INFO"
        return False, f"Không có thông tin thay đổi cho BN {ma_bn}.", "INFO"

    def xoa_ho_so_benh_nhan(self, ma_bn: str) -> Tuple[bool, str, str]:
        if self.danh_sach_benh_nhan.delete(ma_bn):
            self._save_data_to_csv(PATIENTS_CSV_FILE, BenhNhan, self.danh_sach_benh_nhan); return True, f"Đã xóa BN {ma_bn}.", "INFO"
        return False, f"Không tìm thấy BN {ma_bn} để xóa.", "ERROR"

    # --- Quản lý Hàng đợi và Khám bệnh ---
    def dang_ky_kham_benh(self, ma_bn: str, muc_do_uu_tien_str: str) -> Tuple[bool, str, str]:
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn)
        if not benh_nhan: return False, f"Không tìm thấy BN mã {ma_bn} trong hồ sơ.", "ERROR"
        for patient_in_q_obj in self.hang_doi_kham.k.get_all_elements(): 
            if patient_in_q_obj.patientID == ma_bn: return False, f"BN {ma_bn} đã có trong hàng đợi.", "WARNING"
        try: patient_item = PatientInQueue(benh_nhan, muc_do_uu_tien_str)
        except ValueError as e: return False, f"Lỗi đăng ký: {e}", "ERROR"
        self.hang_doi_kham.add(patient_item)
        return True, f"BN {benh_nhan.ho_ten} ({ma_bn}) đã thêm vào HĐ với ưu tiên '{muc_do_uu_tien_str}'.", "INFO"

    def goi_benh_nhan_kham(self) -> Tuple[Optional[PatientInQueue], str, str]:
        bn_kham = self.hang_doi_kham.removeFirst()
        if bn_kham: return bn_kham, f"Gọi BN: {bn_kham.profile.ho_ten} (ID: {bn_kham.patientID})", "INFO"
        return None, "Hàng đợi khám rỗng.", "INFO"

    def hoan_thanh_kham(self, ma_bn_kham: str, ket_qua_kham: str, ghi_chu_kham: str = "", 
                        ma_bac_si_kham: str = "", ma_phong_kham_kham: str = "") -> Tuple[bool, str, str]: # Thêm ma_bac_si, ma_phong_kham
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn_kham)
        if benh_nhan:
            benh_nhan.them_lich_su_kham(datetime.date.today(), ket_qua_kham, ghi_chu_kham, ma_bac_si_kham, ma_phong_kham_kham)
            is_in_today = any(bn.ma_bn == benh_nhan.ma_bn for bn in self.danh_sach_da_kham_hom_nay)
            if not is_in_today: self.danh_sach_da_kham_hom_nay.append(benh_nhan)
            self._save_data_to_csv(PATIENTS_CSV_FILE, BenhNhan, self.danh_sach_benh_nhan)
            return True, f"BN {benh_nhan.ho_ten} đã khám xong.", "INFO"
        return False, f"Không tìm thấy BN {ma_bn_kham} để hoàn thành khám.", "ERROR"
            
    def xu_ly_benh_nhan_vang_mat(self, patient_obj_vang_mat: PatientInQueue) -> Tuple[bool, str, str]:
        if not patient_obj_vang_mat: return True, "Lỗi: Không có BN vắng mặt để xử lý.", "ERROR" 
        patient_obj_vang_mat.absent() 
        msg_detail = f"BN {patient_obj_vang_mat.patientID} vắng lần {patient_obj_vang_mat.absentCount}."
        if patient_obj_vang_mat.checkLeave(): 
            return True, msg_detail + f" BN bị loại khỏi HĐ.", "INFO" 
        else:
            current_prio = patient_obj_vang_mat.priority; min_prio = min(PatientInQueue.PRIORITY_MAP.values()) 
            if current_prio > min_prio: patient_obj_vang_mat.priority = max(min_prio, current_prio - 1)
            self.hang_doi_kham.add(patient_obj_vang_mat) 
            return False, msg_detail + f" BN đưa lại HĐ với ưu tiên '{patient_obj_vang_mat.get_priority_display()}'.", "INFO" 

    def benh_nhan_roi_di_khi_dang_cho(self, ma_bn_roi_di: str) -> Tuple[bool, str, str]:
        all_patients = list(self.hang_doi_kham.k.harr); idx_remove = -1
        for i, p in enumerate(all_patients):
            if p.patientID == ma_bn_roi_di: idx_remove = i; break
        if idx_remove != -1:
            all_patients.pop(idx_remove); self.hang_doi_kham.k.harr = []; self.hang_doi_kham.k.n = 0
            for p_item in all_patients: self.hang_doi_kham.k.add(p_item) 
            return True, f"BN {ma_bn_roi_di} đã xóa khỏi HĐ do rời đi.", "INFO"
        return False, f"Không tìm thấy BN {ma_bn_roi_di} trong HĐ.", "ERROR"

    def hien_thi_hang_doi_cho_kham(self) -> List[str]:
        return self.hang_doi_kham.display_queue(PatientInQueue_class_ref=PatientInQueue)

    def cap_nhat_uu_tien_cho_benh_nhan_cho_lau(self, thoi_gian_cho_toi_da_giay: int = 3600) -> Tuple[int, str, str]:
        num_updated = self.hang_doi_kham.updatePriorityForLongWaiters(thoi_gian_cho_toi_da_giay, PatientInQueue_class_ref=PatientInQueue)
        if num_updated > 0: return num_updated, f"Đã cập nhật ưu tiên cho {num_updated} BN chờ lâu.", "INFO"
        return 0, "Không có BN nào cần cập nhật ưu tiên do chờ lâu.", "INFO"

    def thay_doi_uu_tien_bn_trong_hang_doi(self, ma_bn: str, muc_uu_tien_moi_str: str) -> Tuple[bool, str, str]:
        if muc_uu_tien_moi_str not in PatientInQueue.PRIORITY_MAP:
            return False, f"Mức ưu tiên mới '{muc_uu_tien_moi_str}' không hợp lệ.", "ERROR"
        success = self.hang_doi_kham.thay_doi_uu_tien_benh_nhan(ma_bn, muc_uu_tien_moi_str, PatientInQueue_class_ref=PatientInQueue)
        if success: return True, f"Đã thay đổi ưu tiên cho BN {ma_bn} thành '{muc_uu_tien_moi_str}'.", "INFO"
        return False, f"Không thể thay đổi ưu tiên cho BN {ma_bn} (có thể không trong HĐ).", "ERROR"
    
    # --- Liệt kê và Tìm kiếm ---
    def liet_ke_tat_ca_benh_nhan(self) -> List[BenhNhan]: return self.danh_sach_benh_nhan.get_all_values()
    def liet_ke_benh_nhan_da_kham_hom_nay(self) -> List[BenhNhan]: return self.danh_sach_da_kham_hom_nay.get_all_elements()
    def tim_benh_nhan_nang_cao(self, **kwargs) -> List[BenhNhan]: 
        results: List[BenhNhan] = []; all_patients = self.danh_sach_benh_nhan.get_all_values()
        ho_ten = kwargs.get("ho_ten", "").lower().strip(); sdt = kwargs.get("sdt", "").strip()
        ngay_sinh_str = kwargs.get("ngay_sinh", "").strip(); ngay_sinh_date: Optional[datetime.date] = None
        if ngay_sinh_str:
            try: ngay_sinh_date = datetime.datetime.strptime(ngay_sinh_str, DATE_FORMAT_CSV).date()
            except ValueError: pass
        for bn in all_patients:
            match_ht = (not ho_ten) or (ho_ten in bn.ho_ten.lower())
            match_sdt = (not sdt) or (sdt in bn.sdt)
            match_ns = True
            if ngay_sinh_str: match_ns = (ngay_sinh_date is not None and bn.ngay_sinh == ngay_sinh_date)
            if match_ht and match_sdt and match_ns: results.append(bn)
        return results

    # --- Quản lý Bác sĩ ---
    def _tao_ma_bac_si(self) -> str:
        ma_bs = f"BS{self.next_doctor_id_counter:03d}"; self.next_doctor_id_counter += 1; return ma_bs

    def tao_bac_si(self, ho_ten_bac_si: str, chuyen_khoa: str) -> Tuple[Optional[BacSi], str, str]:
        if not ho_ten_bac_si.strip() or not chuyen_khoa.strip():
            return None, "Họ tên bác sĩ và chuyên khoa là bắt buộc.", "ERROR"
        ma_bs = self._tao_ma_bac_si()
        if self.danh_sach_bac_si.contains(ma_bs):
            return None, f"Lỗi: Mã bác sĩ {ma_bs} đã tồn tại.", "ERROR"
        bac_si = BacSi(ma_bs, ho_ten_bac_si, chuyen_khoa)
        self.danh_sach_bac_si.put(ma_bs, bac_si)
        self._save_data_to_csv(DOCTORS_CSV_FILE, BacSi, self.danh_sach_bac_si)
        return bac_si, f"Đã tạo bác sĩ: {ma_bs} - {ho_ten_bac_si}", "INFO"

    def tim_bac_si_theo_ma(self, ma_bs: str) -> Optional[BacSi]:
        return self.danh_sach_bac_si.get(ma_bs)

    def sua_thong_tin_bac_si(self, ma_bs: str, ho_ten_moi: Optional[str] = None, chuyen_khoa_moi: Optional[str] = None) -> Tuple[bool, str, str]:
        bac_si = self.tim_bac_si_theo_ma(ma_bs)
        if not bac_si: return False, f"Không tìm thấy bác sĩ mã {ma_bs}.", "ERROR"
        updated = False
        if ho_ten_moi is not None and ho_ten_moi.strip() and bac_si.ho_ten_bac_si != ho_ten_moi.strip():
            bac_si.ho_ten_bac_si = ho_ten_moi.strip(); updated = True
        if chuyen_khoa_moi is not None and chuyen_khoa_moi.strip() and bac_si.chuyen_khoa != chuyen_khoa_moi.strip():
            bac_si.chuyen_khoa = chuyen_khoa_moi.strip(); updated = True
        if updated: self._save_data_to_csv(DOCTORS_CSV_FILE, BacSi, self.danh_sach_bac_si); return True, f"Đã cập nhật thông tin bác sĩ {ma_bs}.", "INFO"
        return False, f"Không có thông tin thay đổi cho bác sĩ {ma_bs}.", "INFO"
        
    def xoa_bac_si(self, ma_bs: str) -> Tuple[bool, str, str]:
        # Cần kiểm tra xem bác sĩ có đang được gán cho phòng khám nào không trước khi xóa, hoặc cập nhật phòng khám.
        # Tạm thời xóa trực tiếp:
        if self.danh_sach_bac_si.delete(ma_bs):
            # Cập nhật danh sách bác sĩ trong các phòng khám
            for pk_obj in self.danh_sach_phong_kham.get_all_values():
                if ma_bs in pk_obj.danh_sach_ma_bac_si:
                    pk_obj.danh_sach_ma_bac_si.remove(ma_bs)
            self._save_data_to_csv(DOCTORS_CSV_FILE, BacSi, self.danh_sach_bac_si)
            self._save_data_to_csv(CLINICS_CSV_FILE, PhongKham, self.danh_sach_phong_kham) # Lưu lại phòng khám
            return True, f"Đã xóa bác sĩ {ma_bs}.", "INFO"
        return False, f"Không tìm thấy bác sĩ {ma_bs} để xóa.", "ERROR"
        
    def liet_ke_tat_ca_bac_si(self) -> List[BacSi]: return self.danh_sach_bac_si.get_all_values()

    # --- Quản lý Phòng khám ---
    def _tao_ma_phong_kham(self) -> str:
        ma_pk = f"PK{self.next_clinic_id_counter:03d}"; self.next_clinic_id_counter += 1; return ma_pk

    def tao_phong_kham(self, ten_phong_kham: str, chuyen_khoa_pk: str) -> Tuple[Optional[PhongKham], str, str]:
        if not ten_phong_kham.strip() or not chuyen_khoa_pk.strip():
            return None, "Tên phòng khám và chuyên khoa là bắt buộc.", "ERROR"
        ma_pk = self._tao_ma_phong_kham()
        if self.danh_sach_phong_kham.contains(ma_pk):
            return None, f"Lỗi: Mã phòng khám {ma_pk} đã tồn tại.", "ERROR"
        phong_kham = PhongKham(ma_pk, ten_phong_kham, chuyen_khoa_pk)
        self.danh_sach_phong_kham.put(ma_pk, phong_kham)
        self._save_data_to_csv(CLINICS_CSV_FILE, PhongKham, self.danh_sach_phong_kham)
        return phong_kham, f"Đã tạo phòng khám: {ma_pk} - {ten_phong_kham}", "INFO"

    def tim_phong_kham_theo_ma(self, ma_pk: str) -> Optional[PhongKham]:
        return self.danh_sach_phong_kham.get(ma_pk)

    def sua_thong_tin_phong_kham(self, ma_pk: str, ten_moi: Optional[str] = None, chuyen_khoa_moi: Optional[str] = None) -> Tuple[bool, str, str]:
        phong_kham = self.tim_phong_kham_theo_ma(ma_pk)
        if not phong_kham: return False, f"Không tìm thấy phòng khám mã {ma_pk}.", "ERROR"
        updated = False
        if ten_moi is not None and ten_moi.strip() and phong_kham.ten_phong_kham != ten_moi.strip():
            phong_kham.ten_phong_kham = ten_moi.strip(); updated = True
        if chuyen_khoa_moi is not None and chuyen_khoa_moi.strip() and phong_kham.chuyen_khoa_pk != chuyen_khoa_moi.strip():
            phong_kham.chuyen_khoa_pk = chuyen_khoa_moi.strip(); updated = True
        if updated: self._save_data_to_csv(CLINICS_CSV_FILE, PhongKham, self.danh_sach_phong_kham); return True, f"Đã cập nhật thông tin phòng khám {ma_pk}.", "INFO"
        return False, f"Không có thông tin thay đổi cho phòng khám {ma_pk}.", "INFO"

    def xoa_phong_kham(self, ma_pk: str) -> Tuple[bool, str, str]:
        # Cần kiểm tra xem phòng khám có bác sĩ nào đang làm việc không, hoặc cập nhật bác sĩ.
        # Tạm thời xóa trực tiếp:
        if self.danh_sach_phong_kham.delete(ma_pk):
            # Cập nhật danh sách phòng khám của các bác sĩ
            for bs_obj in self.danh_sach_bac_si.get_all_values():
                if ma_pk in bs_obj.danh_sach_ma_phong_kham:
                    bs_obj.danh_sach_ma_phong_kham.remove(ma_pk)
            self._save_data_to_csv(CLINICS_CSV_FILE, PhongKham, self.danh_sach_phong_kham)
            self._save_data_to_csv(DOCTORS_CSV_FILE, BacSi, self.danh_sach_bac_si) # Lưu lại bác sĩ
            return True, f"Đã xóa phòng khám {ma_pk}.", "INFO"
        return False, f"Không tìm thấy phòng khám {ma_pk} để xóa.", "ERROR"

    def liet_ke_tat_ca_phong_kham(self) -> List[PhongKham]: return self.danh_sach_phong_kham.get_all_values()

    # --- Quản lý mối quan hệ Bác sĩ - Phòng khám ---
    def them_bac_si_vao_phong_kham(self, ma_bs: str, ma_pk: str) -> Tuple[bool, str, str]:
        bac_si = self.tim_bac_si_theo_ma(ma_bs)
        phong_kham = self.tim_phong_kham_theo_ma(ma_pk)
        if not bac_si: return False, f"Không tìm thấy bác sĩ {ma_bs}.", "ERROR"
        if not phong_kham: return False, f"Không tìm thấy phòng khám {ma_pk}.", "ERROR"

        if ma_bs not in phong_kham.danh_sach_ma_bac_si:
            phong_kham.danh_sach_ma_bac_si.append(ma_bs)
        if ma_pk not in bac_si.danh_sach_ma_phong_kham: # Đảm bảo tính nhất quán 2 chiều
            bac_si.danh_sach_ma_phong_kham.append(ma_pk)
        
        self._save_data_to_csv(CLINICS_CSV_FILE, PhongKham, self.danh_sach_phong_kham)
        self._save_data_to_csv(DOCTORS_CSV_FILE, BacSi, self.danh_sach_bac_si)
        return True, f"Đã thêm bác sĩ {ma_bs} vào phòng khám {ma_pk}.", "INFO"

    def xoa_bac_si_khoi_phong_kham(self, ma_bs: str, ma_pk: str) -> Tuple[bool, str, str]:
        bac_si = self.tim_bac_si_theo_ma(ma_bs)
        phong_kham = self.tim_phong_kham_theo_ma(ma_pk)
        if not bac_si: return False, f"Không tìm thấy bác sĩ {ma_bs}.", "ERROR"
        if not phong_kham: return False, f"Không tìm thấy phòng khám {ma_pk}.", "ERROR"

        removed = False
        if ma_bs in phong_kham.danh_sach_ma_bac_si:
            phong_kham.danh_sach_ma_bac_si.remove(ma_bs); removed = True
        if ma_pk in bac_si.danh_sach_ma_phong_kham: # Đảm bảo tính nhất quán 2 chiều
            bac_si.danh_sach_ma_phong_kham.remove(ma_pk); removed = True
        
        if removed:
            self._save_data_to_csv(CLINICS_CSV_FILE, PhongKham, self.danh_sach_phong_kham)
            self._save_data_to_csv(DOCTORS_CSV_FILE, BacSi, self.danh_sach_bac_si)
            return True, f"Đã xóa bác sĩ {ma_bs} khỏi phòng khám {ma_pk}.", "INFO"
        return False, f"Bác sĩ {ma_bs} không có trong phòng khám {ma_pk} hoặc ngược lại.", "INFO"
