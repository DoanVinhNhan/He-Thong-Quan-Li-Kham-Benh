# models.py
import datetime
from custom_structures import CustomLinkedList 
from typing import Any, Optional, Dict, List 

DATE_FORMAT_CSV = "%Y-%m-%d"
DATETIME_FORMAT_DISPLAY = "%Y-%m-%d %H:%M:%S"
HISTORY_ITEM_SEPARATOR = "|"
HISTORY_FIELD_SEPARATOR = ";"

class BenhNhan:
    def __init__(self, ma_bn: str, ho_ten: str, ngay_sinh: Any, gioi_tinh: str, dia_chi: str, sdt: str, cccd: str, 
                 bhyt: str = "", tien_su_benh_an: str = "", di_ung_thuoc: str = "",
                 thoi_diem_dang_ky_str: Optional[str] = None, lich_su_kham_benh_str: Optional[str] = None):
        self.ma_bn = ma_bn
        self.ho_ten = ho_ten
        
        if isinstance(ngay_sinh, str) and ngay_sinh.strip():
            try:
                self.ngay_sinh = datetime.datetime.strptime(ngay_sinh, DATE_FORMAT_CSV).date()
            except ValueError:
                self.ngay_sinh = None 
        elif isinstance(ngay_sinh, datetime.date):
            self.ngay_sinh = ngay_sinh
        else:
            self.ngay_sinh = None

        self.gioi_tinh = gioi_tinh
        self.dia_chi = dia_chi
        self.sdt = sdt
        self.cccd = cccd 
        self.bhyt = bhyt
        self.tien_su_benh_an = tien_su_benh_an
        self.di_ung_thuoc = di_ung_thuoc
        
        if thoi_diem_dang_ky_str:
            try:
                self.thoi_diem_dang_ky_he_thong = datetime.datetime.strptime(thoi_diem_dang_ky_str, DATETIME_FORMAT_DISPLAY)
            except ValueError:
                self.thoi_diem_dang_ky_he_thong = datetime.datetime.now()
        else:
            self.thoi_diem_dang_ky_he_thong = datetime.datetime.now()
            
        self.lich_su_kham_benh: CustomLinkedList = CustomLinkedList()
        if lich_su_kham_benh_str:
            self._deserialize_lich_su_kham(lich_su_kham_benh_str)

    def _serialize_lich_su_kham(self) -> str:
        items_str = []
        for item_dict in self.lich_su_kham_benh:
            ngay_kham_val = item_dict.get('ngay_kham')
            ngay_kham_str = ""
            if isinstance(ngay_kham_val, datetime.date):
                 ngay_kham_str = ngay_kham_val.strftime(DATE_FORMAT_CSV)
            elif isinstance(ngay_kham_val, str) : 
                ngay_kham_str = ngay_kham_val

            ket_qua = str(item_dict.get('ket_qua', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            ghi_chu = str(item_dict.get('ghi_chu', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            items_str.append(f"{ngay_kham_str}{HISTORY_FIELD_SEPARATOR}{ket_qua}{HISTORY_FIELD_SEPARATOR}{ghi_chu}")
        return HISTORY_ITEM_SEPARATOR.join(items_str)

    def _deserialize_lich_su_kham(self, data_str: str):
        if not data_str:
            return
        items = data_str.split(HISTORY_ITEM_SEPARATOR)
        for item_str in items:
            fields = item_str.split(HISTORY_FIELD_SEPARATOR)
            if len(fields) == 3:
                ngay_kham_obj = None
                if fields[0]: 
                    try:
                        ngay_kham_obj = datetime.datetime.strptime(fields[0], DATE_FORMAT_CSV).date()
                    except ValueError:
                        pass 
                self.lich_su_kham_benh.append({
                    "ngay_kham": ngay_kham_obj if ngay_kham_obj else fields[0], 
                    "ket_qua": fields[1],
                    "ghi_chu": fields[2]
                })

    def to_csv_row(self) -> Dict[str, Any]:
        ngay_sinh_str = self.ngay_sinh.strftime(DATE_FORMAT_CSV) if self.ngay_sinh else ""
        thoi_diem_str = self.thoi_diem_dang_ky_he_thong.strftime(DATETIME_FORMAT_DISPLAY)
        
        return {
            "ma_bn": self.ma_bn, "ho_ten": self.ho_ten, "ngay_sinh": ngay_sinh_str,
            "gioi_tinh": self.gioi_tinh, "dia_chi": self.dia_chi, "sdt": self.sdt,
            "cccd": self.cccd, "bhyt": self.bhyt, "tien_su_benh_an": self.tien_su_benh_an,
            "di_ung_thuoc": self.di_ung_thuoc, "thoi_diem_dang_ky_he_thong": thoi_diem_str,
            "lich_su_kham_benh": self._serialize_lich_su_kham()
        }

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'BenhNhan':
        return cls(
            ma_bn=row.get("ma_bn", ""), ho_ten=row.get("ho_ten", ""), ngay_sinh=row.get("ngay_sinh", ""), 
            gioi_tinh=row.get("gioi_tinh", ""), dia_chi=row.get("dia_chi", ""), sdt=row.get("sdt", ""),
            cccd=row.get("cccd", "N/A_DEFAULT"), bhyt=row.get("bhyt", ""), 
            tien_su_benh_an=row.get("tien_su_benh_an", ""), di_ung_thuoc=row.get("di_ung_thuoc", ""),
            thoi_diem_dang_ky_str=row.get("thoi_diem_dang_ky_he_thong"),
            lich_su_kham_benh_str=row.get("lich_su_kham_benh")
        )

    def __str__(self):
        return f"BN: {self.ma_bn} - {self.ho_ten} - SĐT: {self.sdt} - CCCD: {self.cccd}"

    def them_lich_su_kham(self, ngay_kham: datetime.date, ket_qua_kham: str, ghi_chu: str = ""):
        self.lich_su_kham_benh.append({
            "ngay_kham": ngay_kham, "ket_qua": ket_qua_kham, "ghi_chu": ghi_chu
        })

    def hien_thi_thong_tin_chi_tiet(self):
        ls_kham_items = []
        for lk_dict in self.lich_su_kham_benh:
            ngay_kham_display = lk_dict.get('ngay_kham')
            if isinstance(ngay_kham_display, datetime.date):
                ngay_kham_display = ngay_kham_display.strftime(DATE_FORMAT_CSV)
            else: 
                ngay_kham_display = str(ngay_kham_display) 

            ls_kham_items.append(f"{ngay_kham_display}: {lk_dict.get('ket_qua','')} (Ghi chú: {lk_dict.get('ghi_chu','')})")
        ls_kham_str = "\n  ".join(ls_kham_items)
        
        ngay_sinh_display = self.ngay_sinh.strftime(DATE_FORMAT_CSV) if self.ngay_sinh else "Chưa có"
        thoi_diem_display = self.thoi_diem_dang_ky_he_thong.strftime(DATETIME_FORMAT_DISPLAY)

        return (
            f"Mã BN: {self.ma_bn}\n" f"Họ tên: {self.ho_ten}\n"
            f"Ngày sinh: {ngay_sinh_display}\n" f"Giới tính: {self.gioi_tinh}\n"
            f"Địa chỉ: {self.dia_chi}\n" f"SĐT: {self.sdt}\n" f"CCCD: {self.cccd}\n"
            f"BHYT: {self.bhyt}\n" f"Tiền sử bệnh án: {self.tien_su_benh_an}\n"
            f"Dị ứng thuốc: {self.di_ung_thuoc}\n"
            f"Thời điểm đăng ký hệ thống: {thoi_diem_display}\n"
            f"Lịch sử khám bệnh:\n  {ls_kham_str if ls_kham_str else 'Chưa có'}"
        )

class PatientInQueue: 
    PRIORITY_MAP = { 
        'Tái khám': 1, 'Thông thường': 2, 'Ưu tiên thấp': 3,
        'Ưu tiên': 3,  'Rất ưu tiên': 4, 'Ưu tiên cao': 4, 'Cấp cứu': 5
    }
    PRIORITY_DISPLAY_MAP = {v: k for k, v in PRIORITY_MAP.items() if k in ['Tái khám', 'Thông thường', 'Ưu tiên cao', 'Cấp cứu', 'Ưu tiên thấp']}
    if 3 not in PRIORITY_DISPLAY_MAP or PRIORITY_DISPLAY_MAP[3] not in ['Ưu tiên thấp', 'Ưu tiên']:
        PRIORITY_DISPLAY_MAP[3] = 'Ưu tiên thấp'

    def __init__(self, patient_profile: BenhNhan, priority_str: str, registration_time: Optional[datetime.datetime] = None): 
        self.profile = patient_profile 
        self.patientID = patient_profile.ma_bn 
        if not self.createAndSetPriority(priority_str): 
            raise ValueError(f"Mức ưu tiên không hợp lệ: {priority_str}")
        self.registrationTime: datetime.datetime = registration_time if registration_time else datetime.datetime.now() 
        self.absentCount: int = 0 

    def createAndSetPriority(self, prr: str) -> bool: 
        if prr in self.PRIORITY_MAP:
            self.priority: int = self.PRIORITY_MAP[prr] 
            return True
        return False

    def absent(self): 
        self.absentCount += 1 

    def checkLeave(self) -> bool: 
        return self.absentCount >= 3 

    def get_priority_display(self) -> str:
        return self.PRIORITY_DISPLAY_MAP.get(self.priority, "Không xác định")

    def __str__(self):
        return (f"ID: {self.patientID}, Tên: {self.profile.ho_ten}, "
                f"Ưu tiên: {self.get_priority_display()} ({self.priority}), "
                f"TGĐK: {self.registrationTime.strftime('%H:%M:%S')}, Vắng: {self.absentCount}")

    def __gt__(self, other: 'PatientInQueue') -> bool:
        if self.priority != other.priority:
            return self.priority > other.priority
        return self.registrationTime < other.registrationTime 

    def __lt__(self, other: 'PatientInQueue') -> bool:
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.registrationTime > other.registrationTime
