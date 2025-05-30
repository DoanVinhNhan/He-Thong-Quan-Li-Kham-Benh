# main_gui.py
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import datetime
from typing import List, Optional 

from app_logic import HeThongQuanLyKhamBenh # Giữ nguyên
from models import PatientInQueue, BenhNhan, DATE_FORMAT_CSV # Giữ nguyên
# from custom_structures import PriorityQueue # Không cần trực tiếp

PRIORITY_LEVELS = list(PatientInQueue.PRIORITY_MAP.keys()) 

class AppGUI(ctk.CTk):
    def __init__(self, he_thong: HeThongQuanLyKhamBenh):
        super().__init__()
        self.he_thong = he_thong
        self.title("Hệ thống Quản lý Khám Bệnh")
        self.geometry("1150x800") 
        ctk.set_appearance_mode("System") 
        ctk.set_default_color_theme("blue")

        self.tab_view = ctk.CTkTabview(self, width=1130, height=780)
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_dang_ky = self.tab_view.add("Đăng ký & Cập nhật BN")
        self.tab_hang_doi = self.tab_view.add("Hàng đợi khám")
        self.tab_tim_kiem = self.tab_view.add("Tìm kiếm & DS BN")
        self.tab_da_kham = self.tab_view.add("BN Đã khám")
        
        self._setup_dang_ky_tab()
        self._setup_hang_doi_tab()
        self._setup_tim_kiem_tab()
        self._setup_da_kham_tab()

        self.benh_nhan_dang_kham: Optional[PatientInQueue] = None
        
        self._hien_thi_tat_ca_bn() 
        self._refresh_hang_doi_list() 
        self._refresh_da_kham_list()

    def _show_message(self, message: str, level: str):
        """Hàm tiện ích để hiển thị messagebox dựa trên level."""
        if level == "INFO":
            messagebox.showinfo("Thông báo", message)
        elif level == "ERROR":
            messagebox.showerror("Lỗi", message)
        elif level == "WARNING":
            messagebox.showwarning("Cảnh báo", message)
        else: # Mặc định là info
            messagebox.showinfo("Thông báo", message)

    def _setup_dang_ky_tab(self):
        main_content_frame = ctk.CTkFrame(self.tab_dang_ky, fg_color="transparent") 
        main_content_frame.pack(expand=True, fill="both", padx=5, pady=5)
        dk_kham_outer_frame = ctk.CTkFrame(main_content_frame) 
        dk_kham_outer_frame.pack(pady=(5, 10), padx=0, fill="x") 
        ctk.CTkLabel(dk_kham_outer_frame, text="ĐĂNG KÝ KHÁM CHO BỆNH NHÂN", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,5))
        actual_dk_kham_form_frame = ctk.CTkFrame(dk_kham_outer_frame)
        actual_dk_kham_form_frame.pack(fill="x", padx=5, pady=0)
        ctk.CTkLabel(actual_dk_kham_form_frame, text="Mã BN để đăng ký khám:").grid(row=0, column=0, padx=5, pady=5, sticky="w") 
        self.entry_ma_bn_kham = ctk.CTkEntry(actual_dk_kham_form_frame, width=180, placeholder_text="Nhập Mã BN hoặc Tải") 
        self.entry_ma_bn_kham.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(actual_dk_kham_form_frame, text="Mức độ ưu tiên:").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.combo_priority_dk = ctk.CTkComboBox(actual_dk_kham_form_frame, values=PRIORITY_LEVELS, width=150) 
        self.combo_priority_dk.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        if PRIORITY_LEVELS: self.combo_priority_dk.set(PRIORITY_LEVELS[1] if len(PRIORITY_LEVELS) > 1 else PRIORITY_LEVELS[0]) 
        ctk.CTkButton(actual_dk_kham_form_frame, text="Đăng ký Khám", command=self._dang_ky_kham, height=30).grid(row=0, column=4, padx=(15,5), pady=5) 
        actual_dk_kham_form_frame.grid_columnconfigure(1, weight=1); actual_dk_kham_form_frame.grid_columnconfigure(3, weight=1) 
        ctk.CTkFrame(main_content_frame, height=2, fg_color="gray50").pack(fill="x", padx=10, pady=10)
        ho_so_outer_frame = ctk.CTkFrame(main_content_frame) 
        ho_so_outer_frame.pack(pady=5, padx=0, fill="x", expand=True) 
        ctk.CTkLabel(ho_so_outer_frame, text="QUẢN LÝ HỒ SƠ BỆNH NHÂN", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,5))
        actual_ho_so_form_frame = ctk.CTkFrame(ho_so_outer_frame)
        actual_ho_so_form_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(actual_ho_so_form_frame, text="Mã BN (để trống nếu tạo mới, hoặc nhập để tải):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_ma_bn_dk = ctk.CTkEntry(actual_ho_so_form_frame, width=230) 
        self.entry_ma_bn_dk.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(actual_ho_so_form_frame, text="Tải BN để sửa", command=self._load_patient_for_edit).grid(row=0, column=2, padx=5, pady=5)
        fields = [("Họ tên (*):", "họ_tên"), ("Ngày sinh (YYYY-MM-DD) (*):", "ngày_sinh"), ("Giới tính (*):", "giới_tính"), ("CCCD (*):", "cccd"), ("SĐT (*):", "sđt"), ("Địa chỉ:", "địa_chỉ"), ("BHYT:", "bhyt"), ("Tiền sử bệnh án:", "tiền_sử_bệnh_án"), ("Dị ứng thuốc:", "dị_ứng_thuốc")]
        self.entries_dk = {}
        field_pady = 3 
        for i, (label_text, key) in enumerate(fields):
            ctk.CTkLabel(actual_ho_so_form_frame, text=label_text).grid(row=i+1, column=0, padx=5, pady=field_pady, sticky="w")
            if key in ["địa_chỉ", "tiền_sử_bệnh_án", "dị_ứng_thuốc"]: widget = ctk.CTkTextbox(actual_ho_so_form_frame, height=45, width=330, border_width=1) 
            else: widget = ctk.CTkEntry(actual_ho_so_form_frame, width=330) 
            widget.grid(row=i+1, column=1, columnspan=2, padx=5, pady=field_pady, sticky="ew"); self.entries_dk[key] = widget
        actual_ho_so_form_frame.grid_columnconfigure(1, weight=1)
        actual_btn_frame_dk = ctk.CTkFrame(ho_so_outer_frame)
        actual_btn_frame_dk.pack(pady=10, fill="x", padx=5)
        ctk.CTkButton(actual_btn_frame_dk, text="Tạo mới Hồ sơ", command=self._tao_moi_ho_so, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ctk.CTkButton(actual_btn_frame_dk, text="Cập nhật Hồ sơ", command=self._cap_nhat_ho_so, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ctk.CTkButton(actual_btn_frame_dk, text="Xóa Hồ sơ", command=self._xoa_ho_so, fg_color="red", height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ctk.CTkButton(actual_btn_frame_dk, text="Làm mới Form Hồ sơ", command=self._clear_dk_form, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x")

    def _clear_dk_form(self, clear_ma_bn=True):
        if clear_ma_bn: self.entry_ma_bn_dk.delete(0, "end")
        for widget in self.entries_dk.values():
            if isinstance(widget, ctk.CTkEntry): widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkTextbox): widget.delete("1.0", "end")

    def _load_patient_for_edit(self):
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: self._show_message("Vui lòng nhập Mã BN để tải thông tin.", "ERROR"); return
        bn = self.he_thong.tim_benh_nhan_theo_ma(ma_bn) # tim_benh_nhan_theo_ma không trả về message
        if bn:
            self._clear_dk_form(clear_ma_bn=False) 
            self.entries_dk["họ_tên"].insert(0, bn.ho_ten or ""); self.entries_dk["ngày_sinh"].insert(0, bn.ngay_sinh.strftime(DATE_FORMAT_CSV) if bn.ngay_sinh else "")
            self.entries_dk["giới_tính"].insert(0, bn.gioi_tinh or ""); self.entries_dk["cccd"].insert(0, bn.cccd or ""); self.entries_dk["sđt"].insert(0, bn.sdt or "")
            self.entries_dk["địa_chỉ"].delete("1.0", "end"); self.entries_dk["địa_chỉ"].insert("1.0", bn.dia_chi or "")
            self.entries_dk["bhyt"].insert(0, bn.bhyt or ""); 
            self.entries_dk["tiền_sử_bệnh_án"].delete("1.0", "end"); self.entries_dk["tiền_sử_bệnh_án"].insert("1.0", bn.tien_su_benh_an or "")
            self.entries_dk["dị_ứng_thuốc"].delete("1.0", "end"); self.entries_dk["dị_ứng_thuốc"].insert("1.0", bn.di_ung_thuoc or "")
            self.entry_ma_bn_kham.delete(0, "end"); self.entry_ma_bn_kham.insert(0, ma_bn)
            self._show_message(f"Đã tải thông tin BN: {ma_bn} - {bn.ho_ten} vào form.", "INFO")
        else:
            self._show_message(f"Không tìm thấy bệnh nhân với mã: {ma_bn}", "ERROR")
            self._clear_dk_form(clear_ma_bn=False); self.entry_ma_bn_kham.delete(0, "end")

    def _tao_moi_ho_so(self): 
        data = {k: (w.get("1.0", "end-1c").strip() if isinstance(w, ctk.CTkTextbox) else w.get().strip()) for k, w in self.entries_dk.items()}
        # Kiểm tra ngày sinh riêng để có thông báo lỗi cụ thể hơn từ GUI nếu cần
        ngay_sinh_str = data.get("ngày_sinh", "")
        if ngay_sinh_str:
            try: datetime.datetime.strptime(ngay_sinh_str, DATE_FORMAT_CSV)
            except ValueError: self._show_message(f"Định dạng Ngày sinh '{ngay_sinh_str}' không hợp lệ (YYYY-MM-DD).", "ERROR"); return
        
        # Các kiểm tra bắt buộc khác sẽ do app_logic xử lý và trả về message
        bn, message, level = self.he_thong.tao_ho_so_benh_nhan(
            ho_ten=data["họ_tên"], ngay_sinh_str=data["ngày_sinh"], gioi_tinh=data["giới_tính"],
            dia_chi=data["địa_chỉ"], sdt=data["sđt"], cccd=data["cccd"], 
            bhyt=data["bhyt"], tien_su=data["tiền_sử_bệnh_án"], di_ung=data["dị_ứng_thuốc"]
        )
        self._show_message(message, level)
        if bn: # Thành công
            self.entry_ma_bn_dk.delete(0, "end"); self.entry_ma_bn_dk.insert(0, bn.ma_bn) 
            self.entry_ma_bn_kham.delete(0,"end"); self.entry_ma_bn_kham.insert(0, bn.ma_bn) 
            self._refresh_all_patient_lists()

    def _cap_nhat_ho_so(self): 
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: self._show_message("Vui lòng nhập Mã BN của hồ sơ cần cập nhật (hoặc Tải BN).", "ERROR"); return
        
        update_data_raw = {k: (w.get("1.0", "end-1c").strip() if isinstance(w, ctk.CTkTextbox) else w.get().strip()) for k, w in self.entries_dk.items()}
        
        ngay_sinh_str_update = update_data_raw.get("ngày_sinh", "")
        if ngay_sinh_str_update and ngay_sinh_str_update.strip() != "": 
             try: datetime.datetime.strptime(ngay_sinh_str_update, DATE_FORMAT_CSV)
             except ValueError: self._show_message(f"Định dạng Ngày sinh '{ngay_sinh_str_update}' không hợp lệ (YYYY-MM-DD).", "ERROR"); return

        update_data = { 
            "ho_ten": update_data_raw["họ_tên"], "ngay_sinh": update_data_raw["ngày_sinh"], 
            "gioi_tinh": update_data_raw["giới_tính"], "dia_chi": update_data_raw["địa_chỉ"], 
            "sdt": update_data_raw["sđt"], "cccd": update_data_raw["cccd"], 
            "bhyt": update_data_raw["bhyt"], "tien_su_benh_an": update_data_raw["tiền_sử_bệnh_án"], 
            "di_ung_thuoc": update_data_raw["dị_ứng_thuốc"]
        }
        success, message, level = self.he_thong.cap_nhat_thong_tin_benh_nhan(ma_bn, **update_data)
        self._show_message(message, level)
        if success: self._refresh_all_patient_lists()
        
    def _xoa_ho_so(self): 
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: self._show_message("Vui lòng nhập Mã BN của hồ sơ cần xóa.", "ERROR"); return
        
        bn_in_queue = any(self.listbox_hang_doi.item(item_id)['values'][1] == ma_bn for item_id in self.listbox_hang_doi.get_children())
        warning_msg_extra = f"\nLƯU Ý: Bệnh nhân {ma_bn} có thể đang trong hàng đợi khám." if bn_in_queue else ""
        
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa hồ sơ BN: {ma_bn}? {warning_msg_extra}"):
            success, message, level = self.he_thong.xoa_ho_so_benh_nhan(ma_bn)
            self._show_message(message, level)
            if success:
                self._clear_dk_form(clear_ma_bn=True) 
                self.entry_ma_bn_kham.delete(0, "end") 
                self._refresh_all_patient_lists()

    def _dang_ky_kham(self): 
        ma_bn_kham_input = self.entry_ma_bn_kham.get().strip()
        if not ma_bn_kham_input or ma_bn_kham_input == self.entry_ma_bn_kham.cget("placeholder_text"): 
            self._show_message("Vui lòng nhập Mã BN (hoặc tải BN từ form hồ sơ) để đăng ký khám.", "ERROR"); return
        
        priority_str = self.combo_priority_dk.get()
        if not priority_str: self._show_message("Vui lòng chọn mức độ ưu tiên.", "ERROR"); return
        
        success, message, level = self.he_thong.dang_ky_kham_benh(ma_bn_kham_input, priority_str)
        self._show_message(message, level)
        if success:
            self._refresh_hang_doi_list()
            self.entry_ma_bn_kham.delete(0,"end") 

    def _setup_hang_doi_tab(self):
        frame = self.tab_hang_doi 
        self.label_dang_kham = ctk.CTkLabel(frame, text="Đang khám: Chưa có", font=("Arial", 16, "bold"), text_color="green")
        self.label_dang_kham.pack(pady=10)
        controls_frame = ctk.CTkFrame(frame); controls_frame.pack(pady=10, padx=10) 
        ctk.CTkButton(controls_frame, text="Gọi BN Tiếp theo", command=self._goi_kham).pack(side="left", padx=5, pady=5) 
        ctk.CTkButton(controls_frame, text="Hoàn thành Khám", command=self._hoan_thanh_kham).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(controls_frame, text="BN Đang Gọi Vắng mặt", command=self._bn_vang_mat, fg_color="orange").pack(side="left", padx=5, pady=5)
        ctk.CTkButton(controls_frame, text="BN Rời đi (Trong HĐ)", command=self._bn_roi_di, fg_color="tomato").pack(side="left", padx=5, pady=5)
        change_prio_outer_frame = ctk.CTkFrame(frame, fg_color="transparent"); change_prio_outer_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkLabel(change_prio_outer_frame, text="Thay đổi Ưu tiên BN trong Hàng đợi:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        change_prio_frame = ctk.CTkFrame(change_prio_outer_frame); change_prio_frame.pack(fill="x")
        ctk.CTkLabel(change_prio_frame, text="Mã BN:").grid(row=0, column=0, padx=(5,0), pady=5, sticky="e")
        self.entry_change_prio_ma_bn = ctk.CTkEntry(change_prio_frame, width=120); self.entry_change_prio_ma_bn.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(change_prio_frame, text="Ưu tiên mới:").grid(row=0, column=2, padx=(10,0), pady=5, sticky="e")
        self.combo_change_prio_new_level = ctk.CTkComboBox(change_prio_frame, values=PRIORITY_LEVELS, width=160); self.combo_change_prio_new_level.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        if PRIORITY_LEVELS: self.combo_change_prio_new_level.set(PRIORITY_LEVELS[1]) 
        ctk.CTkButton(change_prio_frame, text="Áp dụng thay đổi Ưu tiên", command=self._thay_doi_uu_tien_trong_hang_doi).grid(row=0, column=4, padx=10, pady=5)
        ctk.CTkLabel(frame, text="Danh sách bệnh nhân đang chờ khám:", font=("Arial", 12)).pack(pady=(10,0))
        tree_frame = ctk.CTkFrame(frame); tree_frame.pack(expand=True, fill="both", padx=10, pady=5)
        columns = ("STT", "MaBN", "HoTen", "UuTien", "TGDangKy", "SoLanVang")
        self.listbox_hang_doi = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10) 
        for col_name in columns: self.listbox_hang_doi.heading(col_name, text=col_name)
        self.listbox_hang_doi.column("STT", width=40, anchor="center"); self.listbox_hang_doi.column("MaBN", width=80, anchor="center")
        self.listbox_hang_doi.column("HoTen", width=220); self.listbox_hang_doi.column("UuTien", width=150, anchor="center")
        self.listbox_hang_doi.column("TGDangKy", width=100, anchor="center"); self.listbox_hang_doi.column("SoLanVang", width=50, anchor="center")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.listbox_hang_doi.yview)
        self.listbox_hang_doi.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")
        self.listbox_hang_doi.pack(expand=True, fill="both")
        self._refresh_hang_doi_list()

    def _refresh_hang_doi_list(self):
        for item in self.listbox_hang_doi.get_children(): self.listbox_hang_doi.delete(item)
        display_strings_from_logic = self.he_thong.hien_thi_hang_doi_cho_kham()
        if display_strings_from_logic and display_strings_from_logic[0] == "Hàng đợi rỗng.": pass
        else:
            for display_str in display_strings_from_logic:
                try:
                    parts = display_str.split(',')
                    stt_part = parts[0].split('.')[0].strip(); ma_bn_part = parts[0].split('ID:')[1].strip() 
                    ho_ten_part = parts[1].split('Tên:')[1].strip(); uu_tien_part = parts[2].split('Ưu tiên:')[1].strip()
                    tg_dk_part = parts[3].split('TGĐK:')[1].strip(); so_lan_vang_part = parts[4].split('Vắng:')[1].strip()
                    self.listbox_hang_doi.insert("", "end", values=(stt_part, ma_bn_part, ho_ten_part, uu_tien_part, tg_dk_part, so_lan_vang_part))
                except Exception as e:
                    print(f"Lỗi parse chuỗi hàng đợi: '{display_str}'. Lỗi: {e}")
                    self.listbox_hang_doi.insert("", "end", values=("Err", "Err", display_str, "Err", "Err", "Err"))

    def _goi_kham(self): 
        if self.benh_nhan_dang_kham:
            self._show_message(f"BN {self.benh_nhan_dang_kham.profile.ho_ten} đang trong quá trình khám. Hoàn thành khám trước.", "WARNING")
            return
        
        benh_nhan_kham_obj, message, level = self.he_thong.goi_benh_nhan_kham() 
        self._show_message(message, level) # Thông báo từ app_logic (ví dụ: "Hàng đợi rỗng")

        if benh_nhan_kham_obj: 
            self.benh_nhan_dang_kham = benh_nhan_kham_obj 
            bn_info = self.benh_nhan_dang_kham.profile
            self.label_dang_kham.configure(text=f"Đang khám: {bn_info.ma_bn} - {bn_info.ho_ten} (Ưu tiên: {self.benh_nhan_dang_kham.get_priority_display()})")
            # Không cần messagebox.showinfo ở đây nữa vì đã có _show_message
            self._refresh_hang_doi_list()
        else:
            self.label_dang_kham.configure(text="Đang khám: Hàng đợi rỗng"); self.benh_nhan_dang_kham = None

    def _hoan_thanh_kham(self): 
        if not self.benh_nhan_dang_kham: self._show_message("Chưa có bệnh nhân nào được gọi vào khám.", "ERROR"); return
        
        ma_bn_kham = self.benh_nhan_dang_kham.patientID; ho_ten_bn_kham = self.benh_nhan_dang_kham.profile.ho_ten
        ket_qua = simpledialog.askstring("Kết quả khám", f"Kết quả khám cho BN {ma_bn_kham} ({ho_ten_bn_kham}):", parent=self)
        if ket_qua is None: return # Người dùng nhấn Cancel
        
        ghi_chu = simpledialog.askstring("Ghi chú", f"Ghi chú cho BN {ma_bn_kham}:", parent=self)
        if ghi_chu is None: ghi_chu = "" # Nếu Cancel thì coi như không có ghi chú
        
        success, message, level = self.he_thong.hoan_thanh_kham(ma_bn_kham, ket_qua, ghi_chu)
        self._show_message(message, level)
        
        if success:
            self.label_dang_kham.configure(text="Đang khám: Chưa có"); self.benh_nhan_dang_kham = None
            self._refresh_hang_doi_list(); self._refresh_da_kham_list()

    def _bn_vang_mat(self): 
        if not self.benh_nhan_dang_kham:
            self._show_message("Chưa có bệnh nhân nào đang được gọi để báo vắng mặt.", "ERROR"); return
        
        patient_called_obj = self.benh_nhan_dang_kham
        if messagebox.askyesno("Xác nhận vắng mặt", 
                               f"Xác nhận BN ĐANG ĐƯỢC GỌI: {patient_called_obj.profile.ho_ten} (ID: {patient_called_obj.patientID}) vắng mặt?"):
            
            _bi_loai_bo, message, level = self.he_thong.xu_ly_benh_nhan_vang_mat(patient_called_obj) # _bi_loai_bo không dùng trực tiếp ở đây
            self._show_message(message, level)
            
            self.label_dang_kham.configure(text="Đang khám: Chưa có"); self.benh_nhan_dang_kham = None 
            self._refresh_hang_doi_list() 

    def _bn_roi_di(self): 
        selected_item_id = self.listbox_hang_doi.focus()
        ma_bn_roi_default = ""
        if selected_item_id:
            item_values = self.listbox_hang_doi.item(selected_item_id, "values")
            if item_values and len(item_values) > 1: ma_bn_roi_default = item_values[1] 
        
        ma_bn_roi = simpledialog.askstring("BN Rời Hàng Đợi", "Nhập Mã BN rời đi từ hàng đợi:", initialvalue=ma_bn_roi_default, parent=self)
        if ma_bn_roi and ma_bn_roi.strip():
            success, message, level = self.he_thong.benh_nhan_roi_di_khi_dang_cho(ma_bn_roi.strip())
            self._show_message(message, level)
            if success: self._refresh_hang_doi_list()
        elif ma_bn_roi is not None: self._show_message("Mã BN không được để trống.", "WARNING")

    def _update_priority_long_wait(self): 
        thoi_gian_cho_str = simpledialog.askstring("Cập nhật Ưu tiên (Chờ lâu)", "Thời gian chờ tối đa (giây) để tăng ưu tiên:", initialvalue="3600", parent=self)
        if thoi_gian_cho_str:
            try:
                thoi_gian_cho_giay = int(thoi_gian_cho_str)
                if thoi_gian_cho_giay <= 0: self._show_message("Thời gian chờ phải là số dương.", "ERROR"); return
                
                _num_updated, message, level = self.he_thong.cap_nhat_uu_tien_cho_benh_nhan_cho_lau(thoi_gian_cho_giay)
                self._show_message(message, level) # Thông báo số lượng BN được cập nhật hoặc không có ai
                if _num_updated > 0 : self._refresh_hang_doi_list()
            except ValueError: self._show_message("Thời gian chờ phải là một số nguyên.", "ERROR")
    
    def _thay_doi_uu_tien_trong_hang_doi(self): 
        ma_bn = self.entry_change_prio_ma_bn.get().strip()
        new_priority_str = self.combo_change_prio_new_level.get()
        if not ma_bn: self._show_message("Vui lòng nhập Mã BN cần thay đổi ưu tiên.", "ERROR"); return
        if not new_priority_str: self._show_message("Vui lòng chọn Mức ưu tiên mới.", "ERROR"); return
        
        if messagebox.askyesno("Xác nhận thay đổi", f"Thay đổi ưu tiên của BN {ma_bn} thành '{new_priority_str}'?"):
            success, message, level = self.he_thong.thay_doi_uu_tien_bn_trong_hang_doi(ma_bn, new_priority_str)
            self._show_message(message, level)
            if success:
                self._refresh_hang_doi_list() 
                self.entry_change_prio_ma_bn.delete(0, "end") 

    def _setup_tim_kiem_tab(self): 
        frame = self.tab_tim_kiem
        search_form_container = ctk.CTkFrame(frame); search_form_container.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(search_form_container, text="Tìm kiếm Hồ sơ Bệnh nhân", font=("Arial", 14, "bold")).pack()
        search_form = ctk.CTkFrame(search_form_container); search_form.pack(pady=10, fill="x")
        ctk.CTkLabel(search_form, text="Mã BN:").grid(row=0, column=0, padx=(10,5), pady=5, sticky="w")
        self.entry_search_ma_bn = ctk.CTkEntry(search_form, width=150); self.entry_search_ma_bn.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(search_form, text="Họ tên (chứa):").grid(row=1, column=0, padx=(10,5), pady=5, sticky="w")
        self.entry_search_ho_ten = ctk.CTkEntry(search_form, width=200); self.entry_search_ho_ten.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(search_form, text="SĐT (chứa):").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.entry_search_sdt = ctk.CTkEntry(search_form, width=150); self.entry_search_sdt.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(search_form, text="Ngày sinh (YYYY-MM-DD):").grid(row=1, column=2, padx=(10,5), pady=5, sticky="w")
        self.entry_search_ngay_sinh = ctk.CTkEntry(search_form, width=150); self.entry_search_ngay_sinh.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        search_form.grid_columnconfigure(1, weight=1); search_form.grid_columnconfigure(3, weight=1)
        search_button_frame = ctk.CTkFrame(search_form_container); search_button_frame.pack(pady=5)
        ctk.CTkButton(search_button_frame, text="Tìm kiếm", command=self._tim_kiem_benh_nhan).pack(side="left", padx=10)
        ctk.CTkButton(search_button_frame, text="Tất cả BN", command=self._hien_thi_tat_ca_bn).pack(side="left", padx=10)
        ctk.CTkButton(search_button_frame, text="Làm mới", command=self._clear_search_form).pack(side="left", padx=10)
        self.text_search_results = ctk.CTkTextbox(frame, height=450, width=780, font=("Arial", 13)); 
        self.text_search_results.pack(pady=10, padx=10, expand=True, fill="both")
        self._clear_search_form() 

    def _clear_search_form(self):
        self.entry_search_ma_bn.delete(0, "end"); self.entry_search_ho_ten.delete(0, "end")
        self.entry_search_sdt.delete(0, "end"); self.entry_search_ngay_sinh.delete(0, "end")
        self.text_search_results.configure(state="normal"); self.text_search_results.delete("1.0", "end")
        self.text_search_results.insert("end", "Nhập tiêu chí và tìm kiếm, hoặc hiển thị tất cả bệnh nhân."); self.text_search_results.configure(state="disabled")

    def _tim_kiem_benh_nhan(self): 
        ma_bn = self.entry_search_ma_bn.get().strip(); ho_ten = self.entry_search_ho_ten.get().strip()
        sdt = self.entry_search_sdt.get().strip(); ngay_sinh = self.entry_search_ngay_sinh.get().strip()
        results: List[BenhNhan] = []
        title = "Kết quả tìm kiếm:"
        if ma_bn: 
            bn = self.he_thong.tim_benh_nhan_theo_ma(ma_bn)
            if bn: results.append(bn)
            else: title = f"Không tìm thấy BN với mã {ma_bn}."
        elif ho_ten or sdt or ngay_sinh : 
            search_criteria = {"ho_ten": ho_ten, "sdt": sdt, "ngay_sinh": ngay_sinh}
            results = self.he_thong.tim_benh_nhan_nang_cao(**search_criteria)
            if not results: title = "Không tìm thấy BN nào khớp tiêu chí."
        else: 
            self._show_message("Nhập ít nhất một tiêu chí tìm kiếm, hoặc nhấn 'Hiển thị Tất cả BN'.", "INFO")
            self._display_search_results([], title="Vui lòng nhập tiêu chí tìm kiếm.")
            return
        self._display_search_results(results, title=title if not results and ma_bn else f"Kết quả tìm kiếm ({len(results)}):")


    def _hien_thi_tat_ca_bn(self): 
        results = self.he_thong.liet_ke_tat_ca_benh_nhan()
        self._display_search_results(results, title=f"Danh sách tất cả bệnh nhân ({len(results)}):")

    def _display_search_results(self, benh_nhan_list: List[BenhNhan], title="Kết quả tìm kiếm:"):
        self.text_search_results.configure(state="normal"); self.text_search_results.delete("1.0", "end")
        if benh_nhan_list:
            self.text_search_results.insert("end", f"{title}\n\n")
            for i, bn in enumerate(benh_nhan_list):
                self.text_search_results.insert("end", f"--- Bệnh nhân {i+1} ---\n" + bn.hien_thi_thong_tin_chi_tiet() + "\n\n" + "="*70 + "\n\n")
        else: self.text_search_results.insert("end", f"{title}\nKhông tìm thấy bệnh nhân nào khớp.")
        self.text_search_results.configure(state="disabled")

    def _setup_da_kham_tab(self): 
        frame = self.tab_da_kham
        ctk.CTkLabel(frame, text="BN đã khám trong phiên làm việc:", font=("Arial", 14, "bold")).pack(pady=(10,5))
        tree_frame_da_kham = ctk.CTkFrame(frame); tree_frame_da_kham.pack(expand=True, fill="both", padx=10, pady=5)
        cols = ("STT", "MaBN", "HoTen", "NgaySinh", "SDT", "TGDKHeThong", "KQ Kham", "GhiChuKham")
        self.listbox_da_kham = ttk.Treeview(tree_frame_da_kham, columns=cols, show="headings", height=20)
        for col_name in cols: self.listbox_da_kham.heading(col_name, text=col_name)
        self.listbox_da_kham.column("STT", width=40, anchor="center"); self.listbox_da_kham.column("MaBN", width=80, anchor="center")
        self.listbox_da_kham.column("HoTen", width=180); self.listbox_da_kham.column("NgaySinh", width=100, anchor="center")
        self.listbox_da_kham.column("SDT", width=100, anchor="center"); self.listbox_da_kham.column("TGDKHeThong", width=140, anchor="center")
        self.listbox_da_kham.column("KQ Kham", width=200); self.listbox_da_kham.column("GhiChuKham", width=200)
        scrollbar_da_kham = ttk.Scrollbar(tree_frame_da_kham, orient="vertical", command=self.listbox_da_kham.yview)
        self.listbox_da_kham.configure(yscrollcommand=scrollbar_da_kham.set); scrollbar_da_kham.pack(side="right", fill="y")
        self.listbox_da_kham.pack(expand=True, fill="both")
        ctk.CTkButton(frame, text="Làm mới DS Đã khám", command=self._refresh_da_kham_list).pack(pady=10)

    def _refresh_da_kham_list(self): 
        for item in self.listbox_da_kham.get_children(): self.listbox_da_kham.delete(item)
        da_kham_list = self.he_thong.liet_ke_benh_nhan_da_kham_hom_nay()
        for i, bn in enumerate(da_kham_list):
            kq, gc = "N/A", "N/A"
            if not bn.lich_su_kham_benh.is_empty():
                last_kham = bn.lich_su_kham_benh.get_last()
                if last_kham: kq = last_kham.get('ket_qua', "N/A"); gc = last_kham.get('ghi_chu', "N/A")
            self.listbox_da_kham.insert("", "end", values=(
                i + 1, bn.ma_bn, bn.ho_ten, bn.ngay_sinh.strftime(DATE_FORMAT_CSV) if bn.ngay_sinh else "", bn.sdt,
                bn.thoi_diem_dang_ky_he_thong.strftime("%Y-%m-%d %H:%M") if bn.thoi_diem_dang_ky_he_thong else "", kq, gc
            ))

    def _refresh_all_patient_lists(self):
        self._hien_thi_tat_ca_bn(); self._refresh_da_kham_list()

if __name__ == "__main__":
    he_thong_ql = HeThongQuanLyKhamBenh()
    app = AppGUI(he_thong_ql)
    app.mainloop()
