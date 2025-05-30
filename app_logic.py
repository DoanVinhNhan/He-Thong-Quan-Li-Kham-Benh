# app_logic.py
import datetime
import csv 
import os 
from typing import Optional, List
from models import BenhNhan, PatientInQueue, DATE_FORMAT_CSV 
from custom_structures import PriorityQueue, CustomLinkedList, CustomHashTable 

PATIENTS_CSV_FILE = "patients_data.csv" 

class HeThongQuanLyKhamBenh:
    def __init__(self, hash_table_initial_size: int = 100):
        self.danh_sach_benh_nhan: CustomHashTable = CustomHashTable(initial_size=hash_table_initial_size)
        self.hang_doi_kham: PriorityQueue = PriorityQueue()
        self.next_patient_id_counter = 1 
        self.danh_sach_da_kham_hom_nay: CustomLinkedList = CustomLinkedList()
        self._load_patients_from_csv() 

    def _get_csv_fieldnames(self) -> List[str]:
        return [
            "ma_bn", "ho_ten", "ngay_sinh", "gioi_tinh", "dia_chi", "sdt",
            "cccd", "bhyt", "tien_su_benh_an", "di_ung_thuoc",
            "thoi_diem_dang_ky_he_thong", "lich_su_kham_benh"
        ]

    def _load_patients_from_csv(self):
        print(f"Đang tải dữ liệu từ {PATIENTS_CSV_FILE}...")
        if not os.path.exists(PATIENTS_CSV_FILE):
            print(f"File {PATIENTS_CSV_FILE} không tồn tại. Bỏ qua.")
            return
        max_id_num = 0
        loaded_count = 0
        try:
            with open(PATIENTS_CSV_FILE, mode='r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                if not reader.fieldnames or not all(f in reader.fieldnames for f in ["ma_bn", "ho_ten", "cccd"]):
                    print(f"Lỗi: File {PATIENTS_CSV_FILE} thiếu header 'ma_bn', 'ho_ten' hoặc 'cccd'.")
                    return
                for row_num, row in enumerate(reader, 1):
                    try:
                        # Đảm bảo các trường bắt buộc có mặt trong row từ CSV
                        if not all(key in row for key in ["ma_bn", "ho_ten", "ngay_sinh", "gioi_tinh", "dia_chi", "sdt", "cccd"]):
                            print(f"Cảnh báo: Dòng {row_num} trong CSV thiếu trường bắt buộc. Bỏ qua dòng này.")
                            continue
                        
                        benh_nhan = BenhNhan.from_csv_row(row)
                        # Kiểm tra CCCD sau khi tạo đối tượng (from_csv_row có thể gán default N/A nếu thiếu)
                        if not benh_nhan.cccd or benh_nhan.cccd == "N/A_DEFAULT":
                             print(f"Cảnh báo: Dòng {row_num} (BN: {benh_nhan.ma_bn}) thiếu CCCD hoặc CCCD không hợp lệ. Bỏ qua bệnh nhân này.")
                             continue

                        self.danh_sach_benh_nhan.put(benh_nhan.ma_bn, benh_nhan)
                        loaded_count +=1
                        if benh_nhan.ma_bn.startswith("BN"):
                            try: 
                                id_num = int(benh_nhan.ma_bn[2:])
                                if id_num > max_id_num: max_id_num = id_num
                            except ValueError: pass 
                    except Exception as e_row:
                        print(f"Lỗi xử lý dòng {row_num} trong CSV: {row}. Lỗi: {e_row}")
            self.next_patient_id_counter = max_id_num + 1
            print(f"Đã tải thành công {loaded_count} bệnh nhân. Next ID: {self.next_patient_id_counter}")
        except Exception as e: 
            print(f"Lỗi nghiêm trọng khi tải file CSV: {e}")

    def _save_patients_to_csv(self):
        print(f"Đang lưu dữ liệu vào {PATIENTS_CSV_FILE}...")
        fieldnames = self._get_csv_fieldnames()
        all_benhnhan_objects = self.danh_sach_benh_nhan.get_all_values()
        try:
            with open(PATIENTS_CSV_FILE, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction='ignore') # ignore cột thừa nếu có
                writer.writeheader()
                saved_count = 0
                for benh_nhan in all_benhnhan_objects: 
                    if isinstance(benh_nhan, BenhNhan): 
                        writer.writerow(benh_nhan.to_csv_row())
                        saved_count +=1
            print(f"Đã lưu thành công {saved_count} bệnh nhân.")
        except Exception as e: 
            print(f"Lỗi khi lưu file CSV: {e}")

    def _tao_ma_benh_nhan(self) -> str:
        ma_bn = f"BN{self.next_patient_id_counter:04d}"; self.next_patient_id_counter += 1; return ma_bn

    def tao_ho_so_benh_nhan(self, ho_ten: str, ngay_sinh_str: str, gioi_tinh: str, dia_chi: str, sdt: str, cccd: str, bhyt: str = "", tien_su: str = "", di_ung: str = "") -> Optional[BenhNhan]:
        if not all([ho_ten.strip(), ngay_sinh_str.strip(), gioi_tinh.strip(), sdt.strip(), cccd.strip()]):
            print(f"Lỗi: Họ tên, ngày sinh, giới tính, SĐT và CCCD là bắt buộc.")
            return None
        try: ngay_sinh_obj = datetime.datetime.strptime(ngay_sinh_str, DATE_FORMAT_CSV).date()
        except ValueError: print(f"Lỗi: Định dạng ngày sinh '{ngay_sinh_str}' không hợp lệ."); return None
        
        ma_bn = self._tao_ma_benh_nhan()
        if self.danh_sach_benh_nhan.contains(ma_bn): print(f"Lỗi: Mã BN {ma_bn} đã tồn tại."); return None
        
        benh_nhan = BenhNhan(ma_bn, ho_ten, ngay_sinh_obj, gioi_tinh, dia_chi, sdt, cccd, bhyt, tien_su, di_ung)
        self.danh_sach_benh_nhan.put(ma_bn, benh_nhan); self._save_patients_to_csv(); 
        print(f"Đã tạo hồ sơ cho BN: {benh_nhan.ma_bn} - {benh_nhan.ho_ten}")
        return benh_nhan

    def tim_benh_nhan_theo_ma(self, ma_bn: str) -> Optional[BenhNhan]:
        return self.danh_sach_benh_nhan.get(ma_bn)

    def cap_nhat_thong_tin_benh_nhan(self, ma_bn: str, **kwargs) -> bool:
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn)
        if not benh_nhan: print(f"BN {ma_bn} không tồn tại để cập nhật."); return False
        
        # Kiểm tra CCCD không được cập nhật thành rỗng
        new_cccd = kwargs.get("cccd")
        if new_cccd is not None and not str(new_cccd).strip(): # Nếu cccd được truyền và nó rỗng
            print(f"Lỗi: Số CCCD không được để trống khi cập nhật cho BN {ma_bn}.")
            return False

        updated = False
        for key, value in kwargs.items():
            if hasattr(benh_nhan, key) and value is not None: # Chỉ cập nhật nếu value được truyền
                current_value = getattr(benh_nhan, key)
                new_value = value
                if key == "ngay_sinh" and isinstance(value, str):
                    if not value.strip(): new_value = None # Cho phép xóa ngày sinh
                    else:
                        try: new_value = datetime.datetime.strptime(value, DATE_FORMAT_CSV).date()
                        except ValueError: 
                            print(f"Cảnh báo: Ngày sinh '{value}' không hợp lệ, bỏ qua cập nhật trường này."); continue 
                
                if current_value != new_value: 
                    setattr(benh_nhan, key, new_value); updated = True
        
        if updated: 
            self._save_patients_to_csv(); 
            print(f"Đã cập nhật thông tin cho BN {ma_bn}.")
            return True
        else:
            print(f"Không có thông tin nào được thay đổi cho BN {ma_bn}.")
            return False # Hoặc True nếu không lỗi nhưng không có gì thay đổi

    def xoa_ho_so_benh_nhan(self, ma_bn: str) -> bool:
        if self.danh_sach_benh_nhan.delete(ma_bn):
            self._save_patients_to_csv(); 
            print(f"Đã xóa hồ sơ BN {ma_bn}.")
            return True
        print(f"Không tìm thấy BN {ma_bn} để xóa.")
        return False

    def dang_ky_kham_benh(self, ma_bn: str, muc_do_uu_tien_str: str) -> bool:
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn)
        if not benh_nhan: print(f"Lỗi: Không tìm thấy BN mã {ma_bn}."); return False
        try:
            patient_item = PatientInQueue(benh_nhan, muc_do_uu_tien_str)
            self.hang_doi_kham.add(patient_item)
            print(f"BN {benh_nhan.ho_ten} ({ma_bn}) đã thêm vào HĐ với ưu tiên '{muc_do_uu_tien_str}'.")
            return True
        except ValueError as e: print(f"Lỗi tạo PatientInQueue: {e}"); return False

    def goi_benh_nhan_kham(self) -> Optional[PatientInQueue]:
        bn_kham = self.hang_doi_kham.removeFirst()
        if bn_kham: print(f"Gọi BN: {bn_kham.profile.ho_ten} (ID: {bn_kham.patientID}), Ưu tiên: {bn_kham.get_priority_display()}")
        else: print("Hàng đợi khám rỗng.")
        return bn_kham

    def hoan_thanh_kham(self, ma_bn_kham: str, ket_qua_kham: str, ghi_chu_kham: str = ""):
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn_kham)
        if benh_nhan:
            benh_nhan.them_lich_su_kham(datetime.date.today(), ket_qua_kham, ghi_chu_kham)
            is_in_today = any(bn.ma_bn == benh_nhan.ma_bn for bn in self.danh_sach_da_kham_hom_nay)
            if not is_in_today: self.danh_sach_da_kham_hom_nay.append(benh_nhan)
            self._save_patients_to_csv() 
            print(f"BN {benh_nhan.ho_ten} (ID: {ma_bn_kham}) đã khám xong. Kết quả: {ket_qua_kham}")
        else: print(f"Lỗi: Không tìm thấy BN {ma_bn_kham} để hoàn thành khám.")
            
    def xu_ly_benh_nhan_vang_mat(self, patient_obj_vang_mat: PatientInQueue) -> bool:
        if not patient_obj_vang_mat: 
            print("Lỗi: Không có đối tượng bệnh nhân vắng mặt để xử lý.")
            return True 
        patient_obj_vang_mat.absent() 
        print(f"BN {patient_obj_vang_mat.patientID} được gọi, xử lý vắng mặt lần {patient_obj_vang_mat.absentCount}.")
        if patient_obj_vang_mat.checkLeave(): 
            print(f"BN {patient_obj_vang_mat.patientID} đã vắng mặt {patient_obj_vang_mat.absentCount} lần, không đưa lại vào HĐ.")
            return True 
        else:
            current_priority_val = patient_obj_vang_mat.priority
            min_priority_numeric = min(PatientInQueue.PRIORITY_MAP.values())
            if current_priority_val > min_priority_numeric:
                patient_obj_vang_mat.priority = max(min_priority_numeric, current_priority_val - 1)
            self.hang_doi_kham.add(patient_obj_vang_mat) 
            print(f"BN {patient_obj_vang_mat.patientID} vắng, đưa lại HĐ với ưu tiên '{patient_obj_vang_mat.get_priority_display()}'.")
            return False 

    def benh_nhan_roi_di_khi_dang_cho(self, ma_bn_roi_di: str) -> bool:
        all_patients_in_queue = list(self.hang_doi_kham.k.harr) 
        patient_to_remove_index = -1
        for i, p in enumerate(all_patients_in_queue):
            if p.patientID == ma_bn_roi_di: patient_to_remove_index = i; break
        if patient_to_remove_index != -1:
            all_patients_in_queue.pop(patient_to_remove_index)
            self.hang_doi_kham.k.harr = [] 
            self.hang_doi_kham.k.n = 0
            for p_item in all_patients_in_queue: self.hang_doi_kham.k.add(p_item) 
            print(f"BN {ma_bn_roi_di} đã xóa khỏi HĐ do rời đi.")
            return True
        print(f"Không tìm thấy BN {ma_bn_roi_di} trong HĐ để xóa.")
        return False

    def hien_thi_hang_doi_cho_kham(self) -> List[str]:
        return self.hang_doi_kham.display_queue(PatientInQueue_class_ref=PatientInQueue) # DÒNG ĐÃ SỬA

    def cap_nhat_uu_tien_cho_benh_nhan_cho_lau(self, thoi_gian_cho_toi_da_giay: int = 3600):
        #num_updated = self.hang_doi_kham.updatePriorityForLongWaiters(thoi_gian_cho_toi_da_giay, PatientInQueue_class=PatientInQueue)
        num_updated = self.hang_doi_kham.updatePriorityForLongWaiters(thoi_gian_cho_toi_da_giay, PatientInQueue_class_ref=PatientInQueue) # DÒNG ĐÃ SỬA
        if num_updated > 0: print(f"Đã cập nhật ưu tiên cho {num_updated} BN chờ lâu.")
        else: print("Không có BN nào cần cập nhật ưu tiên do chờ lâu.")

    def thay_doi_uu_tien_bn_trong_hang_doi(self, ma_bn: str, muc_uu_tien_moi_str: str) -> bool:
        if muc_uu_tien_moi_str not in PatientInQueue.PRIORITY_MAP:
            print(f"Lỗi: Mức ưu tiên mới '{muc_uu_tien_moi_str}' không hợp lệ."); return False
        success = self.hang_doi_kham.thay_doi_uu_tien_benh_nhan(ma_bn, muc_uu_tien_moi_str, PatientInQueue)
        if success: print(f"Đã xử lý thay đổi ưu tiên cho BN {ma_bn} thành '{muc_uu_tien_moi_str}'.")
        else: print(f"Thay đổi ưu tiên cho BN {ma_bn} thất bại (có thể không tìm thấy trong HĐ).")
        return success
    
    def liet_ke_tat_ca_benh_nhan(self) -> List[BenhNhan]:
        return self.danh_sach_benh_nhan.get_all_values()

    def liet_ke_benh_nhan_da_kham_hom_nay(self) -> List[BenhNhan]:
        return self.danh_sach_da_kham_hom_nay.get_all_elements()
    
    def tim_benh_nhan_nang_cao(self, **kwargs) -> List[BenhNhan]:
        results: List[BenhNhan] = []
        all_patients = self.danh_sach_benh_nhan.get_all_values()
        ho_ten_query = kwargs.get("ho_ten", "").lower().strip()
        sdt_query = kwargs.get("sdt", "").strip()
        ngay_sinh_query_str = kwargs.get("ngay_sinh", "").strip()
        ngay_sinh_query_date: Optional[datetime.date] = None
        if ngay_sinh_query_str:
            try: ngay_sinh_query_date = datetime.datetime.strptime(ngay_sinh_query_str, DATE_FORMAT_CSV).date()
            except ValueError: pass
        for bn in all_patients:
            match_ho_ten = (not ho_ten_query) or (ho_ten_query in bn.ho_ten.lower())
            match_sdt = (not sdt_query) or (sdt_query in bn.sdt)
            match_ngay_sinh = True
            if ngay_sinh_query_str: # Chỉ xét nếu người dùng nhập ngày sinh
                if ngay_sinh_query_date: match_ngay_sinh = (bn.ngay_sinh == ngay_sinh_query_date)
                else: match_ngay_sinh = False # Ngày nhập không hợp lệ -> không match
            if match_ho_ten and match_sdt and match_ngay_sinh: results.append(bn)
        return results
