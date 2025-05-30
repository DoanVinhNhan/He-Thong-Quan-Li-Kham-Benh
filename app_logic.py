# app_logic.py
import datetime
import csv 
import os 
from typing import Optional, List
# Thay đổi import:
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
        if not os.path.exists(PATIENTS_CSV_FILE):
            return
        max_id_num = 0
        try:
            with open(PATIENTS_CSV_FILE, mode='r', encoding='utf-8', newline='') as file:
                reader = csv.DictReader(file)
                if not reader.fieldnames or not all(f in reader.fieldnames for f in ["ma_bn", "ho_ten", "cccd"]): # Kiểm tra có cột cccd
                    print(f"Lỗi: File {PATIENTS_CSV_FILE} có header không hợp lệ hoặc thiếu cột CCCD.")
                    return
                for row in reader:
                    benh_nhan = BenhNhan.from_csv_row(row)
                    self.danh_sach_benh_nhan.put(benh_nhan.ma_bn, benh_nhan)
                    if benh_nhan.ma_bn.startswith("BN"):
                        try: id_num = int(benh_nhan.ma_bn[2:])
                        except ValueError: continue
                        if id_num > max_id_num: max_id_num = id_num
            self.next_patient_id_counter = max_id_num + 1
        except Exception as e: print(f"Lỗi khi tải file CSV: {e}")

    def _save_patients_to_csv(self):
        fieldnames = self._get_csv_fieldnames()
        all_benhnhan_objects = self.danh_sach_benh_nhan.get_all_values()
        try:
            with open(PATIENTS_CSV_FILE, mode='w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for benh_nhan in all_benhnhan_objects: 
                    if isinstance(benh_nhan, BenhNhan):
                        writer.writerow(benh_nhan.to_csv_row())
        except Exception as e: print(f"Lỗi khi lưu file CSV: {e}")

    def _tao_ma_benh_nhan(self) -> str:
        ma_bn = f"BN{self.next_patient_id_counter:04d}"
        self.next_patient_id_counter += 1
        return ma_bn

    def tao_ho_so_benh_nhan(self, ho_ten: str, ngay_sinh_str: str, gioi_tinh: str,
                              dia_chi: str, sdt: str, cccd: str, # cccd là tham số bắt buộc
                              bhyt: str = "", tien_su: str = "", di_ung: str = "") -> Optional[BenhNhan]:
        if not ho_ten.strip() or not ngay_sinh_str.strip() or not gioi_tinh.strip() or not sdt.strip() or not cccd.strip(): # Kiểm tra cccd
            print(f"Lỗi: Họ tên, ngày sinh, giới tính, SĐT và CCCD là bắt buộc. CCCD hiện tại: '{cccd}'")
            return None
        try:
            ngay_sinh_obj = datetime.datetime.strptime(ngay_sinh_str, DATE_FORMAT_CSV).date()
        except ValueError:
            print(f"Lỗi: Định dạng ngày sinh '{ngay_sinh_str}' không hợp lệ.")
            return None

        ma_bn = self._tao_ma_benh_nhan()
        if self.danh_sach_benh_nhan.contains(ma_bn):
            print(f"Lỗi: Mã bệnh nhân {ma_bn} đã tồn tại.")
            return None

        benh_nhan = BenhNhan(ma_bn, ho_ten, ngay_sinh_obj, gioi_tinh, dia_chi, sdt, cccd,
                             bhyt, tien_su, di_ung)
        self.danh_sach_benh_nhan.put(ma_bn, benh_nhan)
        self._save_patients_to_csv() 
        return benh_nhan

    def tim_benh_nhan_theo_ma(self, ma_bn: str) -> Optional[BenhNhan]:
        return self.danh_sach_benh_nhan.get(ma_bn)

    def cap_nhat_thong_tin_benh_nhan(self, ma_bn: str, **kwargs) -> bool:
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn)
        if not benh_nhan:
            print(f"Không tìm thấy bệnh nhân {ma_bn} để cập nhật.")
            return False
        
        # Kiểm tra CCCD nếu được cung cấp trong kwargs và nó rỗng
        if "cccd" in kwargs and not str(kwargs["cccd"]).strip():
            print(f"Lỗi: Số CCCD không được để trống khi cập nhật cho BN {ma_bn}.")
            return False # Không cho phép cập nhật CCCD thành rỗng

        updated = False
        for key, value in kwargs.items():
            if hasattr(benh_nhan, key) and value is not None:
                current_value = getattr(benh_nhan, key)
                new_value = value
                if key == "ngay_sinh" and isinstance(value, str):
                    if not value: new_value = None
                    else:
                        try: new_value = datetime.datetime.strptime(value, DATE_FORMAT_CSV).date()
                        except ValueError: continue 
                
                if current_value != new_value:
                    setattr(benh_nhan, key, new_value)
                    updated = True
        
        if updated:
            self._save_patients_to_csv() 
            return True
        return False 

    def xoa_ho_so_benh_nhan(self, ma_bn: str) -> bool:
        if self.danh_sach_benh_nhan.delete(ma_bn):
            self._save_patients_to_csv() 
            return True
        return False

    def dang_ky_kham_benh(self, ma_bn: str, muc_do_uu_tien_str: str) -> bool:
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn)
        if not benh_nhan: return False
        try:
            patient_item = PatientInQueue(benh_nhan, muc_do_uu_tien_str)
            self.hang_doi_kham.add(patient_item)
            return True
        except ValueError: return False

    def goi_benh_nhan_kham(self) -> Optional[PatientInQueue]:
        return self.hang_doi_kham.removeFirst()

    def hoan_thanh_kham(self, ma_bn_kham: str, ket_qua_kham: str, ghi_chu_kham: str = ""):
        benh_nhan = self.tim_benh_nhan_theo_ma(ma_bn_kham)
        if benh_nhan:
            benh_nhan.them_lich_su_kham(datetime.date.today(), ket_qua_kham, ghi_chu_kham)
            is_in_today = any(bn.ma_bn == benh_nhan.ma_bn for bn in self.danh_sach_da_kham_hom_nay)
            if not is_in_today: self.danh_sach_da_kham_hom_nay.append(benh_nhan)
            self._save_patients_to_csv() 

    def xu_ly_benh_nhan_vang_mat(self, patient_obj_vang_mat: PatientInQueue) -> bool:
        """
        Xử lý bệnh nhân đã được gọi nhưng vắng mặt.
        Trả về True nếu bệnh nhân bị loại bỏ hoàn toàn, False nếu được đưa lại vào hàng đợi.
        """
        if not patient_obj_vang_mat: return True # Không có đối tượng để xử lý

        patient_obj_vang_mat.absent() # Tăng số lần vắng
        print(f"BN {patient_obj_vang_mat.patientID} đã gọi, xử lý vắng mặt lần {patient_obj_vang_mat.absentCount}.")

        if patient_obj_vang_mat.checkLeave(): # Vắng >= 3 lần
            print(f"Bệnh nhân {patient_obj_vang_mat.patientID} đã vắng mặt {patient_obj_vang_mat.absentCount} lần và sẽ không được đưa lại vào hàng đợi.")
            # Không làm gì thêm, bệnh nhân này không quay lại hàng đợi
            return True # Bị loại bỏ
        else:
            # Giảm mức độ ưu tiên
            current_priority_val = patient_obj_vang_mat.priority
            min_priority_numeric = min(PatientInQueue.PRIORITY_MAP.values())
            if current_priority_val > min_priority_numeric:
                patient_obj_vang_mat.priority = max(min_priority_numeric, current_priority_val - 1)
            
            # Không thay đổi registrationTime để giữ thứ tự FCFS trong mức ưu tiên mới nếu có nhiều người cùng mức
            self.hang_doi_kham.add(patient_obj_vang_mat) # Đưa lại vào hàng đợi
            print(f"Bệnh nhân {patient_obj_vang_mat.patientID} được đưa lại vào hàng đợi với ưu tiên '{patient_obj_vang_mat.get_priority_display()}' ({patient_obj_vang_mat.priority}).")
            return False # Được đưa lại vào hàng đợi

    def benh_nhan_roi_di_khi_dang_cho(self, ma_bn_roi_di: str) -> bool:
        # Code như trước
        all_patients_in_queue = list(self.hang_doi_kham.k.harr)
        patient_to_remove_index = -1
        for i, p in enumerate(all_patients_in_queue):
            if p.patientID == ma_bn_roi_di:
                patient_to_remove_index = i
                break
        if patient_to_remove_index != -1:
            all_patients_in_queue.pop(patient_to_remove_index)
            self.hang_doi_kham.k.harr = [] 
            self.hang_doi_kham.k.n = 0
            for p_item in all_patients_in_queue:
                self.hang_doi_kham.k.add(p_item) 
            return True
        return False

    def hien_thi_hang_doi_cho_kham(self) -> List[str]:
        return self.hang_doi_kham.display_queue(PatientInQueue_class=PatientInQueue) # Truyền lớp PatientInQueue

    def cap_nhat_uu_tien_cho_benh_nhan_cho_lau(self, thoi_gian_cho_toi_da_giay: int = 3600):
        num_updated = self.hang_doi_kham.updatePriorityForLongWaiters(thoi_gian_cho_toi_da_giay, PatientInQueue_class=PatientInQueue) # Truyền lớp
        if num_updated > 0: print(f"Đã cập nhật ưu tiên cho {num_updated} bệnh nhân chờ lâu.")
        else: print("Không có bệnh nhân nào cần cập nhật ưu tiên do chờ lâu.")


    def liet_ke_tat_ca_benh_nhan(self) -> List[BenhNhan]:
        return self.danh_sach_benh_nhan.get_all_values()

    def liet_ke_benh_nhan_da_kham_hom_nay(self) -> List[BenhNhan]:
        return self.danh_sach_da_kham_hom_nay.get_all_elements()
    
    def tim_benh_nhan_nang_cao(self, **kwargs) -> List[BenhNhan]:
        # Code như trước
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
            if ngay_sinh_query_str:
                if ngay_sinh_query_date: match_ngay_sinh = (bn.ngay_sinh == ngay_sinh_query_date)
                else: match_ngay_sinh = False 
            if match_ho_ten and match_sdt and match_ngay_sinh: results.append(bn)
        return results