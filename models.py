# models.py
import datetime
from custom_structures import CustomLinkedList # Đảm bảo import này đúng
from typing import Any, Optional, Dict, List 

DATE_FORMAT_CSV = "%Y-%m-%d"
DATETIME_FORMAT_DISPLAY = "%Y-%m-%d %H:%M:%S"
HISTORY_ITEM_SEPARATOR = "|"
HISTORY_FIELD_SEPARATOR = ";"
LIST_ID_SEPARATOR = "," # Dùng để lưu danh sách ID trong một trường CSV

class BacSi:
    def __init__(self, ma_bac_si: str, ho_ten_bac_si: str, chuyen_khoa: str, 
                 danh_sach_ma_phong_kham_str: str = ""):
        self.ma_bac_si = ma_bac_si
        self.ho_ten_bac_si = ho_ten_bac_si
        self.chuyen_khoa = chuyen_khoa
        self.danh_sach_ma_phong_kham: List[str] = []
        if danh_sach_ma_phong_kham_str:
            self.danh_sach_ma_phong_kham = [pk.strip() for pk in danh_sach_ma_phong_kham_str.split(LIST_ID_SEPARATOR) if pk.strip()]

    def to_csv_row(self) -> Dict[str, str]:
        return {
            "ma_bac_si": self.ma_bac_si,
            "ho_ten_bac_si": self.ho_ten_bac_si,
            "chuyen_khoa": self.chuyen_khoa,
            "danh_sach_ma_phong_kham": LIST_ID_SEPARATOR.join(self.danh_sach_ma_phong_kham)
        }

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'BacSi':
        return cls(
            ma_bac_si=row.get("ma_bac_si", ""),
            ho_ten_bac_si=row.get("ho_ten_bac_si", ""),
            chuyen_khoa=row.get("chuyen_khoa", ""),
            danh_sach_ma_phong_kham_str=row.get("danh_sach_ma_phong_kham", "")
        )

    def __str__(self):
        return f"BS: {self.ma_bac_si} - {self.ho_ten_bac_si} ({self.chuyen_khoa})"

class PhongKham:
    def __init__(self, ma_phong_kham: str, ten_phong_kham: str, chuyen_khoa_pk: str, 
                 danh_sach_ma_bac_si_str: str = ""):
        self.ma_phong_kham = ma_phong_kham
        self.ten_phong_kham = ten_phong_kham
        self.chuyen_khoa_pk = chuyen_khoa_pk 
        self.danh_sach_ma_bac_si: List[str] = []
        if danh_sach_ma_bac_si_str:
            self.danh_sach_ma_bac_si = [bs.strip() for bs in danh_sach_ma_bac_si_str.split(LIST_ID_SEPARATOR) if bs.strip()]

    def to_csv_row(self) -> Dict[str, str]:
        return {
            "ma_phong_kham": self.ma_phong_kham,
            "ten_phong_kham": self.ten_phong_kham,
            "chuyen_khoa_pk": self.chuyen_khoa_pk,
            "danh_sach_ma_bac_si": LIST_ID_SEPARATOR.join(self.danh_sach_ma_bac_si)
        }

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'PhongKham':
        return cls(
            ma_phong_kham=row.get("ma_phong_kham", ""),
            ten_phong_kham=row.get("ten_phong_kham", ""),
            chuyen_khoa_pk=row.get("chuyen_khoa_pk", ""),
            danh_sach_ma_bac_si_str=row.get("danh_sach_ma_bac_si", "")
        )
    
    def __str__(self):
        return f"PK: {self.ma_phong_kham} - {self.ten_phong_kham} ({self.chuyen_khoa_pk})"

class BenhNhan:
    def __init__(self, ma_bn: str, ho_ten: str, ngay_sinh: Any, gioi_tinh: str, dia_chi: str, sdt: str, cccd: str, 
                 bhyt: str = "", tien_su_benh_an: str = "", di_ung_thuoc: str = "",
                 thoi_diem_dang_ky_str: Optional[str] = None, lich_su_kham_benh_str: Optional[str] = None):
        self.ma_bn = ma_bn
        self.ho_ten = ho_ten
        
        if isinstance(ngay_sinh, str) and ngay_sinh.strip():
            try: self.ngay_sinh = datetime.datetime.strptime(ngay_sinh, DATE_FORMAT_CSV).date()
            except ValueError: self.ngay_sinh = None 
        elif isinstance(ngay_sinh, datetime.date): self.ngay_sinh = ngay_sinh
        else: self.ngay_sinh = None

        self.gioi_tinh = gioi_tinh; self.dia_chi = dia_chi; self.sdt = sdt; self.cccd = cccd 
        self.bhyt = bhyt; self.tien_su_benh_an = tien_su_benh_an; self.di_ung_thuoc = di_ung_thuoc
        
        if thoi_diem_dang_ky_str:
            try: self.thoi_diem_dang_ky_he_thong = datetime.datetime.strptime(thoi_diem_dang_ky_str, DATETIME_FORMAT_DISPLAY)
            except ValueError: self.thoi_diem_dang_ky_he_thong = datetime.datetime.now()
        else: self.thoi_diem_dang_ky_he_thong = datetime.datetime.now()
            
        self.lich_su_kham_benh: CustomLinkedList = CustomLinkedList()
        if lich_su_kham_benh_str: self._deserialize_lich_su_kham(lich_su_kham_benh_str)

    def _serialize_lich_su_kham(self) -> str:
        items_str = []
        for item_dict in self.lich_su_kham_benh: # item_dict là dictionary
            ngay_kham_val = item_dict.get('ngay_kham')
            ngay_kham_str = ngay_kham_val.strftime(DATE_FORMAT_CSV) if isinstance(ngay_kham_val, datetime.date) else str(ngay_kham_val or "")
            
            ket_qua = str(item_dict.get('ket_qua', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            ghi_chu = str(item_dict.get('ghi_chu', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            ma_bac_si_kham = str(item_dict.get('ma_bac_si_kham', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            ma_phong_kham_kham = str(item_dict.get('ma_phong_kham_kham', "")).replace(HISTORY_FIELD_SEPARATOR, " ").replace(HISTORY_ITEM_SEPARATOR, " ")
            
            items_str.append(f"{ngay_kham_str}{HISTORY_FIELD_SEPARATOR}{ket_qua}{HISTORY_FIELD_SEPARATOR}{ghi_chu}{HISTORY_FIELD_SEPARATOR}{ma_bac_si_kham}{HISTORY_FIELD_SEPARATOR}{ma_phong_kham_kham}")
        return HISTORY_ITEM_SEPARATOR.join(items_str)

    def _deserialize_lich_su_kham(self, data_str: str):
        if not data_str: return
        items = data_str.split(HISTORY_ITEM_SEPARATOR)
        for item_str in items:
            fields = item_str.split(HISTORY_FIELD_SEPARATOR)
            if len(fields) >= 3: 
                ngay_kham_obj = None
                if fields[0]: 
                    try: ngay_kham_obj = datetime.datetime.strptime(fields[0], DATE_FORMAT_CSV).date()
                    except ValueError: pass 
                
                kham_info = {
                    "ngay_kham": ngay_kham_obj if ngay_kham_obj else fields[0], 
                    "ket_qua": fields[1],
                    "ghi_chu": fields[2],
                    "ma_bac_si_kham": fields[3] if len(fields) > 3 else "",
                    "ma_phong_kham_kham": fields[4] if len(fields) > 4 else ""
                }
                self.lich_su_kham_benh.append(kham_info)

    def to_csv_row(self) -> Dict[str, Any]:
        return {
            "ma_bn": self.ma_bn, "ho_ten": self.ho_ten, 
            "ngay_sinh": self.ngay_sinh.strftime(DATE_FORMAT_CSV) if self.ngay_sinh else "",
            "gioi_tinh": self.gioi_tinh, "dia_chi": self.dia_chi, "sdt": self.sdt,
            "cccd": self.cccd, "bhyt": self.bhyt, "tien_su_benh_an": self.tien_su_benh_an,
            "di_ung_thuoc": self.di_ung_thuoc, 
            "thoi_diem_dang_ky_he_thong": self.thoi_diem_dang_ky_he_thong.strftime(DATETIME_FORMAT_DISPLAY),
            "lich_su_kham_benh": self._serialize_lich_su_kham()
        }

    @classmethod
    def from_csv_row(cls, row: Dict[str, str]) -> 'BenhNhan':
        return cls(
            ma_bn=row.get("ma_bn", ""), ho_ten=row.get("ho_ten", ""), ngay_sinh=row.get("ngay_sinh", ""), 
            gioi_tinh=row.get("gioi_tinh", ""), dia_chi=row.get("dia_chi", ""), sdt=row.get("sdt", ""),
            cccd=row.get("cccd", "N/A_CSV_LOAD_ERROR"), 
            bhyt=row.get("bhyt", ""), tien_su_benh_an=row.get("tien_su_benh_an", ""), 
            di_ung_thuoc=row.get("di_ung_thuoc", ""),
            thoi_diem_dang_ky_str=row.get("thoi_diem_dang_ky_he_thong"),
            lich_su_kham_benh_str=row.get("lich_su_kham_benh")
        )

    def __str__(self):
        return f"BN: {self.ma_bn} - {self.ho_ten} - SĐT: {self.sdt} - CCCD: {self.cccd}"

    def them_lich_su_kham(self, ngay_kham: datetime.date, ket_qua_kham: str, ghi_chu: str = "", ma_bac_si: str = "", ma_phong_kham: str = ""):
        self.lich_su_kham_benh.append({
            "ngay_kham": ngay_kham, "ket_qua": ket_qua_kham, "ghi_chu": ghi_chu,
            "ma_bac_si_kham": ma_bac_si, "ma_phong_kham_kham": ma_phong_kham
        })

    def hien_thi_thong_tin_chi_tiet(self):
        ls_kham_items = []
        for lk_dict in self.lich_su_kham_benh:
            ngay_kham_display = lk_dict.get('ngay_kham')
            if isinstance(ngay_kham_display, datetime.date):
                ngay_kham_display = ngay_kham_display.strftime(DATE_FORMAT_CSV)
            else: ngay_kham_display = str(ngay_kham_display) 
            bs_info = f", BS: {lk_dict.get('ma_bac_si_kham')}" if lk_dict.get('ma_bac_si_kham') else ""
            pk_info = f", PK: {lk_dict.get('ma_phong_kham_kham')}" if lk_dict.get('ma_phong_kham_kham') else ""
            ls_kham_items.append(f"{ngay_kham_display}: {lk_dict.get('ket_qua','')}{bs_info}{pk_info} (Ghi chú: {lk_dict.get('ghi_chu','')})")
        ls_kham_str = "\n  ".join(ls_kham_items) if ls_kham_items else "Chưa có"
        
        return (
            f"Mã BN: {self.ma_bn}\n" f"Họ tên: {self.ho_ten}\n"
            f"Ngày sinh: {self.ngay_sinh.strftime(DATE_FORMAT_CSV) if self.ngay_sinh else 'Chưa có'}\n" 
            f"Giới tính: {self.gioi_tinh}\n" f"Địa chỉ: {self.dia_chi}\n" 
            f"SĐT: {self.sdt}\n" f"CCCD: {self.cccd}\n" f"BHYT: {self.bhyt}\n" 
            f"Tiền sử bệnh án: {self.tien_su_benh_an}\n" f"Dị ứng thuốc: {self.di_ung_thuoc}\n"
            f"TG ĐK Hệ thống: {self.thoi_diem_dang_ky_he_thong.strftime(DATETIME_FORMAT_DISPLAY)}\n"
            f"Lịch sử khám bệnh:\n  {ls_kham_str}"
        )

class PatientInQueue: 
    PRIORITY_MAP = { 'Tái khám': 1, 'Thông thường': 2, 'Ưu tiên thấp': 3, 'Ưu tiên': 3,  'Rất ưu tiên': 4, 'Ưu tiên cao': 4, 'Cấp cứu': 5}
    PRIORITY_DISPLAY_MAP = {v: k for k, v in PRIORITY_MAP.items() if k in ['Tái khám', 'Thông thường', 'Ưu tiên cao', 'Cấp cứu', 'Ưu tiên thấp']}
    if 3 not in PRIORITY_DISPLAY_MAP or PRIORITY_DISPLAY_MAP[3] not in ['Ưu tiên thấp', 'Ưu tiên']: PRIORITY_DISPLAY_MAP[3] = 'Ưu tiên thấp'

    def __init__(self, patient_profile: BenhNhan, priority_str: str, registration_time: Optional[datetime.datetime] = None): 
        self.profile = patient_profile; self.patientID = patient_profile.ma_bn 
        if not self.createAndSetPriority(priority_str): raise ValueError(f"Mức ưu tiên không hợp lệ: {priority_str}")
        self.registrationTime: datetime.datetime = registration_time if registration_time else datetime.datetime.now() 
        self.absentCount: int = 0 
    def createAndSetPriority(self, prr: str) -> bool: 
        if prr in self.PRIORITY_MAP: self.priority: int = self.PRIORITY_MAP[prr]; return True
        return False
    def absent(self): self.absentCount += 1 
    def checkLeave(self) -> bool: return self.absentCount >= 3 
    def get_priority_display(self) -> str: return self.PRIORITY_DISPLAY_MAP.get(self.priority, "Không xác định")
    def __str__(self):
        return (f"ID: {self.patientID}, Tên: {self.profile.ho_ten}, "
                f"Ưu tiên: {self.get_priority_display()} ({self.priority}), "
                f"TGĐK: {self.registrationTime.strftime('%H:%M:%S')}, Vắng: {self.absentCount}")
    def __gt__(self, other: 'PatientInQueue') -> bool:
        if self.priority != other.priority: return self.priority > other.priority
        return self.registrationTime < other.registrationTime 
    def __lt__(self, other: 'PatientInQueue') -> bool:
        if self.priority != other.priority: return self.priority < other.priority
        return self.registrationTime > other.registrationTime
