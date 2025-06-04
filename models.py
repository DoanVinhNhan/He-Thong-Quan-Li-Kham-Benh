# models.py
import datetime
from custom_structures import LinkedList, List # Sử dụng List và LinkedList tùy chỉnh

# Định dạng ngày tháng và hằng số phân tách
DATE_FORMAT_CSV = "%Y-%m-%d"
DATETIME_FORMAT_DISPLAY = "%Y-%m-%d %H:%M:%S"
HISTORY_ITEM_SEPARATOR = "|"
HISTORY_FIELD_SEPARATOR = ";"
LIST_ID_SEPARATOR = ","

class Doctor:
    """Lớp đại diện Bác sĩ."""
    def __init__(self, doctor_id, doctor_name, specialty, clinic_id_list_str=""):
        self.doctor_id = doctor_id
        self.doctor_name = doctor_name
        self.specialty = specialty # Chuyên khoa
        self.clinic_id_list = List() # Danh sách mã phòng khám bác sĩ làm việc
        if clinic_id_list_str:
            clinic_ids_py = clinic_id_list_str.split(LIST_ID_SEPARATOR)
            for pk_id in clinic_ids_py:
                if pk_id.strip():
                    self.clinic_id_list.append(pk_id.strip())

    def to_csv_row(self):
        # Chuyển đổi Doctor thành dict để ghi CSV.
        clinic_str_list_py = [self.clinic_id_list.get(i) for i in range(len(self.clinic_id_list))]
        return {
            "ma_bac_si": self.doctor_id,
            "ho_ten_bac_si": self.doctor_name,
            "chuyen_khoa": self.specialty,
            "danh_sach_ma_phong_kham": LIST_ID_SEPARATOR.join(clinic_str_list_py)
        }

    @classmethod
    def from_csv_row(cls, row_data):
        # Tạo Doctor từ dict (dữ liệu CSV).
        return cls(
            doctor_id=row_data.get("ma_bac_si", ""),
            doctor_name=row_data.get("ho_ten_bac_si", ""),
            specialty=row_data.get("chuyen_khoa", ""),
            clinic_id_list_str=row_data.get("danh_sach_ma_phong_kham", "")
        )

    def __str__(self):
        return f"BS: {self.doctor_id} - {self.doctor_name} ({self.specialty})"

class Clinic:
    """Lớp đại diện Phòng khám."""
    def __init__(self, clinic_id, clinic_name, clinic_specialty_val, doctor_id_list_str=""):
        self.clinic_id = clinic_id
        self.clinic_name = clinic_name
        self.clinic_specialty = clinic_specialty_val # Chuyên khoa phòng khám
        self.doctor_id_list = List() # Danh sách mã bác sĩ thuộc phòng khám
        if doctor_id_list_str:
            bs_ids_py = doctor_id_list_str.split(LIST_ID_SEPARATOR)
            for bs_id in bs_ids_py:
                if bs_id.strip():
                    self.doctor_id_list.append(bs_id.strip())

    def to_csv_row(self):
        # Chuyển đổi Clinic thành dict để ghi CSV.
        doctor_str_list_py = [self.doctor_id_list.get(i) for i in range(len(self.doctor_id_list))]
        return {
            "ma_phong_kham": self.clinic_id,
            "ten_phong_kham": self.clinic_name,
            "chuyen_khoa_pk": self.clinic_specialty,
            "danh_sach_ma_bac_si": LIST_ID_SEPARATOR.join(doctor_str_list_py)
        }

    @classmethod
    def from_csv_row(cls, row_data):
        # Tạo Clinic từ dict (dữ liệu CSV).
        return cls(
            clinic_id=row_data.get("ma_phong_kham", ""),
            clinic_name=row_data.get("ten_phong_kham", ""),
            clinic_specialty_val=row_data.get("chuyen_khoa_pk", ""),
            doctor_id_list_str=row_data.get("danh_sach_ma_bac_si", "")
        )

    def __str__(self):
        return f"PK: {self.clinic_id} - {self.clinic_name} ({self.clinic_specialty})"

class Patient:
    """Lớp đại diện Bệnh nhân. Bao gồm thông tin cá nhân, y tế và lịch sử khám."""
    def __init__(self, patient_id, full_name, date_of_birth_val, gender, address, phone_number, national_id,
                 health_insurance_id="", medical_history_summary_val="", drug_allergies_val="",
                 system_registration_time_str=None, examination_history_str=None):
        self.patient_id = patient_id
        self.full_name = full_name
        # Xử lý ngày sinh
        if isinstance(date_of_birth_val, str) and date_of_birth_val.strip():
            try: self.date_of_birth = datetime.datetime.strptime(date_of_birth_val, DATE_FORMAT_CSV).date()
            except ValueError: self.date_of_birth = None
        elif isinstance(date_of_birth_val, datetime.date): self.date_of_birth = date_of_birth_val
        else: self.date_of_birth = None
        self.gender = gender
        self.address = address
        self.phone_number = phone_number
        self.national_id = national_id # CCCD
        self.health_insurance_id = health_insurance_id # BHYT
        self.medical_history_summary = medical_history_summary_val # Tiền sử bệnh
        self.drug_allergies = drug_allergies_val # Dị ứng thuốc
        # Xử lý thời điểm đăng ký hệ thống
        if system_registration_time_str:
            try: self.system_registration_time = datetime.datetime.strptime(system_registration_time_str, DATETIME_FORMAT_DISPLAY)
            except ValueError: self.system_registration_time = datetime.datetime.now()
        else: self.system_registration_time = datetime.datetime.now()
        self.examination_history = LinkedList() # Lịch sử khám bệnh dùng LinkedList
        if examination_history_str:
            self._deserialize_examination_history(examination_history_str)

    def _serialize_examination_history(self):
        # Chuyển LinkedList lịch sử khám thành chuỗi CSV.
        items_str_py_list = []
        for item_dict in self.examination_history:
            ng_kham_val = item_dict.get('ngay_kham')
            ng_kham_str = ng_kham_val.strftime(DATE_FORMAT_CSV) if isinstance(ng_kham_val, datetime.date) else str(ng_kham_val or "")
            loai_kham_val = str(item_dict.get('loai_kham', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            kq = str(item_dict.get('ket_qua', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            gc = str(item_dict.get('ghi_chu', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            ma_bs = str(item_dict.get('ma_bac_si_kham', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            ma_pk = str(item_dict.get('ma_phong_kham_kham', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            items_str_py_list.append(f"{ng_kham_str}{HISTORY_FIELD_SEPARATOR}{loai_kham_val}{HISTORY_FIELD_SEPARATOR}{kq}{HISTORY_FIELD_SEPARATOR}{gc}{HISTORY_FIELD_SEPARATOR}{ma_bs}{HISTORY_FIELD_SEPARATOR}{ma_pk}")
        return HISTORY_ITEM_SEPARATOR.join(items_str_py_list)

    def _deserialize_examination_history(self, data_str):
        # Chuyển chuỗi CSV lịch sử khám thành LinkedList các dict.
        if not data_str: return
        items = data_str.split(HISTORY_ITEM_SEPARATOR)
        for item_str in items:
            fields = item_str.split(HISTORY_FIELD_SEPARATOR)
            ng_kham_obj = None
            if fields[0]:
                try: ng_kham_obj = datetime.datetime.strptime(fields[0], DATE_FORMAT_CSV).date()
                except ValueError: pass
            if len(fields) >= 3: # Tối thiểu ngày, loại, kết quả
                kham_info = {
                    "ngay_kham": ng_kham_obj if ng_kham_obj else fields[0],
                    "loai_kham": fields[1],
                    "ket_qua": fields[2],
                    "ghi_chu": fields[3] if len(fields) > 3 else "",
                    "ma_bac_si_kham": fields[4] if len(fields) > 4 else "",
                    "ma_phong_kham_kham": fields[5] if len(fields) > 5 else ""
                }
                self.examination_history.append(kham_info)

    def to_csv_row(self):
        # Chuyển đổi Patient thành dict để ghi CSV.
        return {
            "ma_bn": self.patient_id, "ho_ten": self.full_name,
            "ngay_sinh": self.date_of_birth.strftime(DATE_FORMAT_CSV) if self.date_of_birth else "",
            "gioi_tinh": self.gender, "dia_chi": self.address, "sdt": self.phone_number,
            "cccd": self.national_id, "bhyt": self.health_insurance_id,
            "tien_su_benh_an": self.medical_history_summary, "di_ung_thuoc": self.drug_allergies,
            "thoi_diem_dang_ky_he_thong": self.system_registration_time.strftime(DATETIME_FORMAT_DISPLAY),
            "lich_su_kham_benh": self._serialize_examination_history()
        }

    @classmethod
    def from_csv_row(cls, row_data):
        # Tạo Patient từ dict (dữ liệu CSV).
        return cls(
            patient_id=row_data.get("ma_bn", ""),
            full_name=row_data.get("ho_ten", ""),
            date_of_birth_val=row_data.get("ngay_sinh", ""),
            gender=row_data.get("gioi_tinh", ""),
            address=row_data.get("dia_chi", ""),
            phone_number=row_data.get("sdt", ""),
            national_id=row_data.get("cccd", "N/A_CSV_ERROR"), # Mặc định lỗi nếu thiếu CCCD
            health_insurance_id=row_data.get("bhyt", ""),
            medical_history_summary_val=row_data.get("tien_su_benh_an", ""),
            drug_allergies_val=row_data.get("di_ung_thuoc", ""),
            system_registration_time_str=row_data.get("thoi_diem_dang_ky_he_thong"),
            examination_history_str=row_data.get("lich_su_kham_benh")
        )

    def __str__(self):
        return f"BN: {self.patient_id} - {self.full_name} - CCCD: {self.national_id}"

    def add_examination_record(self, exam_date, exam_type, result, notes="", doctor_id="", clinic_id=""):
        # Thêm một bản ghi khám bệnh mới.
        self.examination_history.append({
            "ngay_kham": exam_date, "loai_kham": exam_type, "ket_qua": result,
            "ghi_chu": notes, "ma_bac_si_kham": doctor_id, "ma_phong_kham_kham": clinic_id
        })

    def display_detailed_info(self):
        # Tạo chuỗi thông tin chi tiết bệnh nhân để hiển thị.
        history_items_py_list = []
        for hist_dict in self.examination_history:
            date_display = hist_dict.get('ngay_kham')
            bs_info = f", BS: {hist_dict.get('ma_bac_si_kham')}" if hist_dict.get('ma_bac_si_kham') else ""
            pk_info = f", PK: {hist_dict.get('ma_phong_kham_kham')}" if hist_dict.get('ma_phong_kham_kham') else ""
            date_display_str = date_display.strftime(DATE_FORMAT_CSV) if isinstance(date_display, datetime.date) else str(date_display)
            history_items_py_list.append(f"{date_display_str}: Loại: {hist_dict.get('loai_kham', 'N/A')}, Kết quả: {hist_dict.get('ket_qua', '')}{bs_info}{pk_info} (Ghi chú: {hist_dict.get('ghi_chu', '')})")
        history_str_display = "\n  ".join(history_items_py_list) if history_items_py_list else "Chưa có"
        return (
            f"Mã BN: {self.patient_id}\n"
            f"Họ tên: {self.full_name}\n"
            f"Ngày sinh: {self.date_of_birth.strftime(DATE_FORMAT_CSV) if self.date_of_birth else 'Chưa có'}\n"
            f"Giới tính: {self.gender}\n"
            f"Địa chỉ: {self.address}\n"
            f"SĐT: {self.phone_number}\n"
            f"CCCD: {self.national_id}\n"
            f"BHYT: {self.health_insurance_id}\n"
            f"Tiền sử: {self.medical_history_summary}\n"
            f"Dị ứng: {self.drug_allergies}\n"
            f"TG ĐK Hệ thống: {self.system_registration_time.strftime(DATETIME_FORMAT_DISPLAY)}\n"
            f"Lịch sử khám:\n  {history_str_display}"
        )

class PatientInQueue:
    """Lớp đại diện Bệnh nhân trong Hàng đợi Khám. Dùng trong PriorityQueue."""
    PRIORITY_MAP = {'Tái khám': 1, 'Thông thường': 2, 'Ưu tiên': 3, 'Ưu tiên cao': 4, 'Cấp cứu': 5} # Ưu tiên số lớn hơn là cao hơn
    PRIORITY_DISPLAY_MAP = {v: k for k, v in PRIORITY_MAP.items()} # Map ngược để hiển thị tên

    def __init__(self, patient_profile_obj, priority_str_val, registration_timestamp=None):
        self.patient_profile = patient_profile_obj # Hồ sơ bệnh nhân
        self.patient_id = patient_profile_obj.patient_id
        if not self.create_and_set_priority(priority_str_val):
            raise ValueError(f"Mức ưu tiên không hợp lệ: {priority_str_val}")
        self.registration_time = registration_timestamp if registration_timestamp else datetime.datetime.now() # Thời điểm đăng ký
        self.absent_count = 0 # Số lần vắng

    def create_and_set_priority(self, priority_str_val):
        # Đặt ưu tiên (số) từ chuỗi.
        if priority_str_val in self.PRIORITY_MAP:
            self.priority = self.PRIORITY_MAP[priority_str_val]
            return True
        return False

    def increment_absent_count(self): self.absent_count += 1 # Tăng số lần vắng.
    def should_leave_queue(self): return self.absent_count >= 3 # Kiểm tra nếu bị loại do vắng nhiều.
    def get_priority_display_name(self): return self.PRIORITY_DISPLAY_MAP.get(self.priority, "Không xác định") # Tên ưu tiên.

    def __str__(self):
        return (
            f"ID:{self.patient_id},Tên:{self.patient_profile.full_name},"
            f"Ưu tiên:{self.get_priority_display_name()}({self.priority}),"
            f"TGĐK:{self.registration_time.strftime('%H:%M:%S')},Vắng:{self.absent_count}"
        )

    # Phương thức so sánh cho MaxHeap: ưu tiên số cao hơn -> "lớn hơn"
    # Nếu ưu tiên bằng nhau, thời gian đăng ký sớm hơn (nhỏ hơn) -> "lớn hơn"
    def __gt__(self, other_patient_in_queue): # self > other
        if self.priority != other_patient_in_queue.priority:
            return self.priority > other_patient_in_queue.priority
        return self.registration_time < other_patient_in_queue.registration_time

    def __lt__(self, other_patient_in_queue): # self < other
        if self.priority != other_patient_in_queue.priority:
            return self.priority < other_patient_in_queue.priority
        return self.registration_time > other_patient_in_queue.registration_time
