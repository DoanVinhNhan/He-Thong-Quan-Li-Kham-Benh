# main_gui.py
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import datetime
from typing import List, Optional 

from app_logic import HeThongQuanLyKhamBenh
from models import PatientInQueue, BenhNhan, DATE_FORMAT_CSV, BacSi, PhongKham

PRIORITY_LEVELS = list(PatientInQueue.PRIORITY_MAP.keys()) 

class AppGUI(ctk.CTk):
    def __init__(self, he_thong: HeThongQuanLyKhamBenh):
        super().__init__() # Đảm bảo gọi đầu tiên
        self.he_thong = he_thong
        self.title("Hệ thống Quản lý Khám Bệnh Đa Khoa")
        self.geometry("1300x900") 
        ctk.set_appearance_mode("System") 
        ctk.set_default_color_theme("blue")

        self.tab_view = ctk.CTkTabview(self, width=1280, height=880)
        self.tab_view.pack(expand=True, fill="both", padx=10, pady=10)

        self.tab_dang_ky = self.tab_view.add("Đăng ký & Hồ sơ BN")
        self.tab_hang_doi = self.tab_view.add("Hàng đợi Khám") 
        self.tab_bac_si = self.tab_view.add("Quản lý Bác sĩ")
        self.tab_phong_kham = self.tab_view.add("Quản lý Phòng khám")
        self.tab_tim_kiem = self.tab_view.add("Tìm kiếm BN") 
        self.tab_da_kham = self.tab_view.add("Lịch sử Khám") 
        
        # Gọi các hàm setup cho từng tab
        self._setup_dang_ky_tab()
        self._setup_hang_doi_tab()
        self._setup_bac_si_tab()
        self._setup_phong_kham_tab()
        self._setup_tim_kiem_tab()
        self._setup_da_kham_tab()

        self.benh_nhan_dang_kham: Optional[PatientInQueue] = None
        self.phong_kham_bn_dang_kham: Optional[str] = None 
        
        self._populate_phong_kham_comboboxes() 
        self._hien_thi_tat_ca_bn() 
        self._refresh_hang_doi_list() 
        self._refresh_da_kham_list() 
        self._refresh_bac_si_list() 
        self._refresh_phong_kham_list()

    def _show_message(self, message: str, level: str):
        if not message: return 
        if level == "INFO": messagebox.showinfo("Thông báo", message)
        elif level == "ERROR": messagebox.showerror("Lỗi", message)
        elif level == "WARNING": messagebox.showwarning("Cảnh báo", message)
        else: messagebox.showinfo("Thông báo", message)

    def _populate_phong_kham_comboboxes(self):
        phong_kham_list = self.he_thong.liet_ke_tat_ca_phong_kham()
        self.ma_pk_options = [f"{pk.ma_phong_kham} - {pk.ten_phong_kham}" for pk in phong_kham_list]
        if not self.ma_pk_options: self.ma_pk_options = ["Chưa có phòng khám"]

        if hasattr(self, 'combo_phong_kham_dk'):
            self.combo_phong_kham_dk.configure(values=self.ma_pk_options)
            if self.ma_pk_options[0] != "Chưa có phòng khám": self.combo_phong_kham_dk.set(self.ma_pk_options[0])
            else: self.combo_phong_kham_dk.set("")


        if hasattr(self, 'combo_chon_pk_hang_doi'):
            self.combo_chon_pk_hang_doi.configure(values=self.ma_pk_options)
            if self.ma_pk_options[0] != "Chưa có phòng khám": self.combo_chon_pk_hang_doi.set(self.ma_pk_options[0])
            else: self.combo_chon_pk_hang_doi.set("")
            self._refresh_hang_doi_list() 

    def _setup_dang_ky_tab(self):
        main_content_frame = ctk.CTkFrame(self.tab_dang_ky, fg_color="transparent") 
        main_content_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        dk_kham_outer_frame = ctk.CTkFrame(main_content_frame) 
        dk_kham_outer_frame.pack(pady=(5, 10), padx=0, fill="x") 
        ctk.CTkLabel(dk_kham_outer_frame, text="ĐĂNG KÝ KHÁM CHO BỆNH NHÂN", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,5))
        actual_dk_kham_form_frame = ctk.CTkFrame(dk_kham_outer_frame)
        actual_dk_kham_form_frame.pack(fill="x", padx=5, pady=0)

        ctk.CTkLabel(actual_dk_kham_form_frame, text="Mã BN (*):").grid(row=0, column=0, padx=5, pady=5, sticky="w") 
        self.entry_ma_bn_kham = ctk.CTkEntry(actual_dk_kham_form_frame, width=180, placeholder_text="Nhập Mã BN hoặc Tải") 
        self.entry_ma_bn_kham.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(actual_dk_kham_form_frame, text="Phòng khám (*):").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.combo_phong_kham_dk = ctk.CTkComboBox(actual_dk_kham_form_frame, values=["Đang tải..."], width=200) 
        self.combo_phong_kham_dk.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(actual_dk_kham_form_frame, text="Mức độ ưu tiên (*):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.combo_priority_dk = ctk.CTkComboBox(actual_dk_kham_form_frame, values=PRIORITY_LEVELS, width=180) 
        self.combo_priority_dk.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        if PRIORITY_LEVELS: self.combo_priority_dk.set(PRIORITY_LEVELS[1] if len(PRIORITY_LEVELS) > 1 else PRIORITY_LEVELS[0]) 

        ctk.CTkButton(actual_dk_kham_form_frame, text="Đăng ký Khám", command=self._dang_ky_kham, height=30).grid(row=1, column=2, columnspan=2, padx=(15,5), pady=10, sticky="ew") 
        
        actual_dk_kham_form_frame.grid_columnconfigure(1, weight=1) 
        actual_dk_kham_form_frame.grid_columnconfigure(3, weight=1) 

        ctk.CTkFrame(main_content_frame, height=2, fg_color="gray50").pack(fill="x", padx=10, pady=10)
        ho_so_outer_frame = ctk.CTkFrame(main_content_frame); ho_so_outer_frame.pack(pady=5, padx=0, fill="x", expand=True) 
        ctk.CTkLabel(ho_so_outer_frame, text="QUẢN LÝ HỒ SƠ BỆNH NHÂN", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,5))
        actual_ho_so_form_frame = ctk.CTkFrame(ho_so_outer_frame); actual_ho_so_form_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(actual_ho_so_form_frame, text="Mã BN (tải/sửa, trống nếu tạo mới):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_ma_bn_dk = ctk.CTkEntry(actual_ho_so_form_frame, width=230) 
        self.entry_ma_bn_dk.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(actual_ho_so_form_frame, text="Tải BN để sửa", command=self._load_patient_for_edit).grid(row=0, column=2, padx=5, pady=5)
        fields = [("Họ tên (*):", "họ_tên"), ("Ngày sinh (*):", "ngày_sinh"), ("Giới tính (*):", "giới_tính"), ("CCCD (*):", "cccd"), ("SĐT (*):", "sđt"), ("Địa chỉ:", "địa_chỉ"), ("BHYT:", "bhyt"), ("Tiền sử:", "tiền_sử_bệnh_án"), ("Dị ứng:", "dị_ứng_thuốc")]
        self.entries_dk = {}
        field_pady = 3 
        for i, (label_text, key) in enumerate(fields):
            ctk.CTkLabel(actual_ho_so_form_frame, text=label_text).grid(row=i+1, column=0, padx=5, pady=field_pady, sticky="w")
            if key in ["địa_chỉ", "tiền_sử_bệnh_án", "dị_ứng_thuốc"]: widget = ctk.CTkTextbox(actual_ho_so_form_frame, height=40, width=330, border_width=1) 
            else: widget = ctk.CTkEntry(actual_ho_so_form_frame, width=330, placeholder_text="YYYY-MM-DD" if key=="ngày_sinh" else "") 
            widget.grid(row=i+1, column=1, columnspan=2, padx=5, pady=field_pady, sticky="ew"); self.entries_dk[key] = widget
        actual_ho_so_form_frame.grid_columnconfigure(1, weight=1)
        actual_btn_frame_dk = ctk.CTkFrame(ho_so_outer_frame); actual_btn_frame_dk.pack(pady=10, fill="x", padx=5)
        ctk.CTkButton(actual_btn_frame_dk, text="Tạo mới", command=self._tao_moi_ho_so, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ctk.CTkButton(actual_btn_frame_dk, text="Cập nhật", command=self._cap_nhat_ho_so, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ctk.CTkButton(actual_btn_frame_dk, text="Xóa", command=self._xoa_ho_so, fg_color="red", height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x")
        ctk.CTkButton(actual_btn_frame_dk, text="Làm mới Form", command=self._clear_dk_form, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x")

    def _clear_dk_form(self, clear_ma_bn=True):
        if clear_ma_bn: self.entry_ma_bn_dk.delete(0, "end")
        for widget in self.entries_dk.values():
            if isinstance(widget, ctk.CTkEntry): widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkTextbox): widget.delete("1.0", "end")

    def _load_patient_for_edit(self):
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: self._show_message("Vui lòng nhập Mã BN để tải thông tin.", "ERROR"); return
        bn = self.he_thong.tim_benh_nhan_theo_ma(ma_bn)
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
        ngay_sinh_str = data.get("ngày_sinh", "")
        if ngay_sinh_str:
            try: datetime.datetime.strptime(ngay_sinh_str, DATE_FORMAT_CSV)
            except ValueError: self._show_message(f"Định dạng Ngày sinh '{ngay_sinh_str}' không hợp lệ (YYYY-MM-DD).", "ERROR"); return
        
        bn_obj, message, level = self.he_thong.tao_ho_so_benh_nhan(ho_ten=data["họ_tên"], ngay_sinh_str=data["ngày_sinh"], gioi_tinh=data["giới_tính"], dia_chi=data["địa_chỉ"], sdt=data["sđt"], cccd=data["cccd"], bhyt=data["bhyt"], tien_su=data["tiền_sử_bệnh_án"], di_ung=data["dị_ứng_thuốc"])
        self._show_message(message, level)
        if bn_obj: self.entry_ma_bn_dk.delete(0, "end"); self.entry_ma_bn_dk.insert(0, bn_obj.ma_bn); self.entry_ma_bn_kham.delete(0,"end"); self.entry_ma_bn_kham.insert(0, bn_obj.ma_bn); self._refresh_all_patient_lists()

    def _cap_nhat_ho_so(self): 
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: self._show_message("Vui lòng tải Mã BN để cập nhật.", "ERROR"); return
        update_data_raw = {k: (w.get("1.0", "end-1c").strip() if isinstance(w, ctk.CTkTextbox) else w.get().strip()) for k, w in self.entries_dk.items()}
        ngay_sinh_str_update = update_data_raw.get("ngày_sinh", "")
        if ngay_sinh_str_update and ngay_sinh_str_update.strip() != "": 
             try: datetime.datetime.strptime(ngay_sinh_str_update, DATE_FORMAT_CSV)
             except ValueError: self._show_message(f"Định dạng Ngày sinh '{ngay_sinh_str_update}' không hợp lệ.", "ERROR"); return
        update_data = { "ho_ten": update_data_raw["họ_tên"], "ngay_sinh": update_data_raw["ngày_sinh"], "gioi_tinh": update_data_raw["giới_tính"], "dia_chi": update_data_raw["địa_chỉ"], "sdt": update_data_raw["sđt"], "cccd": update_data_raw["cccd"], "bhyt": update_data_raw["bhyt"], "tien_su_benh_an": update_data_raw["tiền_sử_bệnh_án"], "di_ung_thuoc": update_data_raw["dị_ứng_thuốc"]}
        success, message, level = self.he_thong.cap_nhat_thong_tin_benh_nhan(ma_bn, **update_data)
        self._show_message(message, level)
        if success and level == "INFO": self._refresh_all_patient_lists()
        
    def _xoa_ho_so(self): 
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: self._show_message("Vui lòng tải Mã BN để xóa.", "ERROR"); return
        if messagebox.askyesno("Xác nhận xóa", f"Bạn chắc chắn muốn xóa hồ sơ BN: {ma_bn}? \nLưu ý: Nếu BN đang trong hàng đợi, bạn cần xóa khỏi hàng đợi trước."):
            success, message, level = self.he_thong.xoa_ho_so_benh_nhan(ma_bn)
            self._show_message(message, level)
            if success: self._clear_dk_form(clear_ma_bn=True); self.entry_ma_bn_kham.delete(0, "end"); self._refresh_all_patient_lists()

    def _dang_ky_kham(self): 
        ma_bn_kham_input = self.entry_ma_bn_kham.get().strip()
        selected_pk_full = self.combo_phong_kham_dk.get()

        if not ma_bn_kham_input or ma_bn_kham_input == self.entry_ma_bn_kham.cget("placeholder_text"): 
            self._show_message("Vui lòng nhập Mã BN để đăng ký khám.", "ERROR"); return
        if not selected_pk_full or selected_pk_full in ["Chưa có phòng khám", "Đang tải..."]:
             self._show_message("Vui lòng chọn Phòng khám.", "ERROR"); return
        
        ma_phong_kham = selected_pk_full.split(" - ")[0] 

        priority_str = self.combo_priority_dk.get()
        if not priority_str: self._show_message("Vui lòng chọn mức độ ưu tiên.", "ERROR"); return
        
        success, message, level = self.he_thong.dang_ky_kham_benh(ma_bn_kham_input, ma_phong_kham, priority_str)
        self._show_message(message, level)
        if success: self._refresh_hang_doi_list(); self.entry_ma_bn_kham.delete(0,"end") 

    def _setup_hang_doi_tab(self):
        frame = self.tab_hang_doi 
        
        chon_pk_frame = ctk.CTkFrame(frame, fg_color="transparent")
        chon_pk_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(chon_pk_frame, text="Chọn Phòng khám để xem hàng đợi:").pack(side="left", padx=(0,5))
        self.combo_chon_pk_hang_doi = ctk.CTkComboBox(chon_pk_frame, values=["Đang tải..."], width=250, command=self._on_chon_pk_hang_doi_changed)
        self.combo_chon_pk_hang_doi.pack(side="left")

        self.label_dang_kham = ctk.CTkLabel(frame, text="Đang khám: Chưa có BN / Chưa chọn PK", font=("Arial", 16, "bold"), text_color="green")
        self.label_dang_kham.pack(pady=10)
        
        controls_frame = ctk.CTkFrame(frame); controls_frame.pack(pady=10, padx=10) 
        ctk.CTkButton(controls_frame, text="Gọi BN Tiếp theo", command=self._goi_kham).pack(side="left", padx=5, pady=5) 
        ctk.CTkButton(controls_frame, text="Hoàn thành Khám", command=self._hoan_thanh_kham).pack(side="left", padx=5, pady=5)
        ctk.CTkButton(controls_frame, text="BN Đang Gọi Vắng mặt", command=self._bn_vang_mat, fg_color="orange").pack(side="left", padx=5, pady=5)
        ctk.CTkButton(controls_frame, text="BN Rời đi (Trong HĐ)", command=self._bn_roi_di, fg_color="tomato").pack(side="left", padx=5, pady=5)
        
        change_prio_outer_frame = ctk.CTkFrame(frame, fg_color="transparent"); change_prio_outer_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkLabel(change_prio_outer_frame, text="Thay đổi Ưu tiên BN trong Hàng đợi (của PK đang chọn):", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
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
        self.listbox_hang_doi = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8) 
        for col_name in columns: self.listbox_hang_doi.heading(col_name, text=col_name)
        self.listbox_hang_doi.column("STT", width=40, anchor="center"); self.listbox_hang_doi.column("MaBN", width=80, anchor="center")
        self.listbox_hang_doi.column("HoTen", width=220); self.listbox_hang_doi.column("UuTien", width=150, anchor="center")
        self.listbox_hang_doi.column("TGDangKy", width=100, anchor="center"); self.listbox_hang_doi.column("SoLanVang", width=50, anchor="center")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.listbox_hang_doi.yview)
        self.listbox_hang_doi.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")
        self.listbox_hang_doi.pack(expand=True, fill="both")
        
    def _on_chon_pk_hang_doi_changed(self, choice): # choice là giá trị được chọn
        self._refresh_hang_doi_list()
        self.label_dang_kham.configure(text="Đang khám: Chưa có BN / Hãy gọi BN từ PK này")
        self.benh_nhan_dang_kham = None; self.phong_kham_bn_dang_kham = None

    def _get_selected_ma_pk_hang_doi(self) -> Optional[str]:
        selected_pk_full = self.combo_chon_pk_hang_doi.get()
        if not selected_pk_full or selected_pk_full in ["Chưa có phòng khám", "Đang tải..."]: return None
        return selected_pk_full.split(" - ")[0]

    def _refresh_hang_doi_list(self):
        for item in self.listbox_hang_doi.get_children(): self.listbox_hang_doi.delete(item)
        ma_pk_selected = self._get_selected_ma_pk_hang_doi()
        if not ma_pk_selected: self.listbox_hang_doi.insert("", "end", values=("", "---", "Vui lòng chọn phòng khám", "---", "", "")); return
        display_strings = self.he_thong.hien_thi_hang_doi_cho_kham(ma_pk_selected)
        if display_strings and display_strings[0].startswith(f"Hàng đợi của Phòng khám {ma_pk_selected} rỗng"):
            self.listbox_hang_doi.insert("", "end", values=("", ma_pk_selected, display_strings[0], "", "", ""))
        elif display_strings:
            for display_str in display_strings:
                try:
                    parts = display_str.split(','); stt = parts[0].split('.')[0].strip(); ma_bn = parts[0].split('ID:')[1].strip() 
                    ho_ten = parts[1].split('Tên:')[1].strip(); uu_tien = parts[2].split('Ưu tiên:')[1].strip()
                    tg_dk = parts[3].split('TGĐK:')[1].strip(); so_lan_vang = parts[4].split('Vắng:')[1].strip()
                    self.listbox_hang_doi.insert("", "end", values=(stt, ma_bn, ho_ten, uu_tien, tg_dk, so_lan_vang))
                except Exception as e: print(f"Parse HĐ Error: '{display_str}', {e}"); self.listbox_hang_doi.insert("", "end", values=("Err",display_str,"Err","Err","Err","Err"))
        else: self.listbox_hang_doi.insert("", "end", values=("", ma_pk_selected, "Không có dữ liệu", "", "", ""))

    def _goi_kham(self): 
        if self.benh_nhan_dang_kham: self._show_message(f"BN {self.benh_nhan_dang_kham.profile.ho_ten} đang khám.", "WARNING"); return
        ma_pk_selected = self._get_selected_ma_pk_hang_doi()
        if not ma_pk_selected: self._show_message("Chọn Phòng khám để gọi BN.", "ERROR"); return
        bn_kham_obj, message, level = self.he_thong.goi_benh_nhan_kham(ma_pk_selected) 
        if bn_kham_obj: 
            self.benh_nhan_dang_kham = bn_kham_obj; self.phong_kham_bn_dang_kham = ma_pk_selected
            bn_info = self.benh_nhan_dang_kham.profile
            self.label_dang_kham.configure(text=f"Đang khám (PK: {ma_pk_selected}): {bn_info.ma_bn} - {bn_info.ho_ten} ({self.benh_nhan_dang_kham.get_priority_display()})")
            self._show_message(message, level)
            self._refresh_hang_doi_list()
        else: self._show_message(message, level); self.label_dang_kham.configure(text=f"Đang khám (PK: {ma_pk_selected}): Hàng đợi rỗng"); self.benh_nhan_dang_kham = None; self.phong_kham_bn_dang_kham = None

    def _hoan_thanh_kham(self): 
        if not self.benh_nhan_dang_kham: self._show_message("Chưa có BN được gọi khám.", "ERROR"); return
        ma_bn_kham = self.benh_nhan_dang_kham.patientID; ho_ten_bn_kham = self.benh_nhan_dang_kham.profile.ho_ten
        ket_qua = simpledialog.askstring("Kết quả khám", f"Kết quả khám cho BN {ma_bn_kham} ({ho_ten_bn_kham}):", parent=self)
        if ket_qua is None: return 
        ghi_chu = simpledialog.askstring("Ghi chú", f"Ghi chú cho BN {ma_bn_kham}:", parent=self); ghi_chu = ghi_chu or ""
        
        # Lấy danh sách bác sĩ và phòng khám để người dùng chọn (hoặc nhập mã nếu danh sách quá dài/phức tạp cho simpledialog)
        all_bac_si = self.he_thong.liet_ke_tat_ca_bac_si()
        bs_options = [f"{bs.ma_bac_si} - {bs.ho_ten_bac_si}" for bs in all_bac_si] if all_bac_si else ["Không có BS"]
        pk_options = self.ma_pk_options # Đã có từ _populate_phong_kham_comboboxes

        # Đơn giản là nhập mã BS và PK qua simpledialog
        ma_bac_si_kham = simpledialog.askstring("Thông tin khám", "Nhập Mã Bác sĩ khám (ví dụ BS001):", parent=self)
        ma_bac_si_kham = ma_bac_si_kham.strip().upper() if ma_bac_si_kham else ""
        
        ma_phong_kham_thuc_hien = simpledialog.askstring("Thông tin khám", "Nhập Mã Phòng khám (ví dụ PK001):", initialvalue=self.phong_kham_bn_dang_kham or "", parent=self)
        ma_phong_kham_thuc_hien = ma_phong_kham_thuc_hien.strip().upper() if ma_phong_kham_thuc_hien else ""

        success, message, level = self.he_thong.hoan_thanh_kham(ma_bn_kham, ket_qua, ghi_chu, ma_bac_si_kham, ma_phong_kham_thuc_hien)
        self._show_message(message, level)
        if success: self.label_dang_kham.configure(text="Đang khám: Chưa có BN / Chưa chọn PK"); self.benh_nhan_dang_kham = None; self.phong_kham_bn_dang_kham = None; self._refresh_hang_doi_list(); self._refresh_da_kham_list()

    def _bn_vang_mat(self): 
        if not self.benh_nhan_dang_kham or not self.phong_kham_bn_dang_kham:
            self._show_message("Chưa có BN đang được gọi hoặc không rõ PK.", "ERROR"); return
        patient_obj = self.benh_nhan_dang_kham; ma_pk_origine = self.phong_kham_bn_dang_kham
        if messagebox.askyesno("Xác nhận vắng mặt", f"Xác nhận BN ĐANG GỌI: {patient_obj.profile.ho_ten} (ID: {patient_obj.patientID}) từ PK {ma_pk_origine} vắng mặt?"):
            _bi_loai_bo, message, level = self.he_thong.xu_ly_benh_nhan_vang_mat(patient_obj, ma_pk_origine)
            self._show_message(message, level)
            self.label_dang_kham.configure(text="Đang khám: Chưa có BN / Chưa chọn PK"); self.benh_nhan_dang_kham = None; self.phong_kham_bn_dang_kham = None 
            self._refresh_hang_doi_list() 

    def _bn_roi_di(self): 
        ma_pk_selected = self._get_selected_ma_pk_hang_doi()
        if not ma_pk_selected: self._show_message("Chọn PK có BN cần xóa khỏi HĐ.", "ERROR"); return
        selected_item_id = self.listbox_hang_doi.focus(); ma_bn_roi_default = ""
        if selected_item_id: item_values = self.listbox_hang_doi.item(selected_item_id, "values"); ma_bn_roi_default = item_values[1] if item_values and len(item_values) > 1 else ""
        ma_bn_roi = simpledialog.askstring("BN Rời Hàng Đợi", f"Nhập Mã BN rời đi từ HĐ của PK {ma_pk_selected}:", initialvalue=ma_bn_roi_default, parent=self)
        if ma_bn_roi and ma_bn_roi.strip():
            success, message, level = self.he_thong.benh_nhan_roi_di_khi_dang_cho(ma_bn_roi.strip(), ma_pk_selected)
            self._show_message(message, level); 
            if success: self._refresh_hang_doi_list()
        elif ma_bn_roi is not None: self._show_message("Mã BN không được để trống.", "WARNING")

    def _thay_doi_uu_tien_trong_hang_doi(self): 
        ma_pk_selected = self._get_selected_ma_pk_hang_doi()
        if not ma_pk_selected: self._show_message("Chọn PK trước khi thay đổi ưu tiên.", "ERROR"); return
        ma_bn = self.entry_change_prio_ma_bn.get().strip(); new_priority_str = self.combo_change_prio_new_level.get()
        if not ma_bn: self._show_message("Nhập Mã BN cần thay đổi ưu tiên.", "ERROR"); return
        if not new_priority_str: self._show_message("Chọn Mức ưu tiên mới.", "ERROR"); return
        if messagebox.askyesno("Xác nhận", f"Thay đổi ưu tiên của BN {ma_bn} tại PK {ma_pk_selected} thành '{new_priority_str}'?"):
            success, message, level = self.he_thong.thay_doi_uu_tien_bn_trong_hang_doi(ma_pk_selected, ma_bn, new_priority_str)
            self._show_message(message, level)
            if success: self._refresh_hang_doi_list(); self.entry_change_prio_ma_bn.delete(0, "end") 

    def _setup_tim_kiem_tab(self): 
        frame = self.tab_tim_kiem; search_form_container = ctk.CTkFrame(frame); search_form_container.pack(pady=10, padx=10, fill="x")
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
        self.text_search_results.pack(pady=10, padx=10, expand=True, fill="both"); self._clear_search_form() 

    def _clear_search_form(self):
        self.entry_search_ma_bn.delete(0, "end"); self.entry_search_ho_ten.delete(0, "end")
        self.entry_search_sdt.delete(0, "end"); self.entry_search_ngay_sinh.delete(0, "end")
        self.text_search_results.configure(state="normal"); self.text_search_results.delete("1.0", "end")
        self.text_search_results.insert("end", "Nhập tiêu chí và tìm kiếm, hoặc hiển thị tất cả bệnh nhân."); self.text_search_results.configure(state="disabled")

    def _tim_kiem_benh_nhan(self): 
        ma_bn = self.entry_search_ma_bn.get().strip(); ho_ten = self.entry_search_ho_ten.get().strip()
        sdt = self.entry_search_sdt.get().strip(); ngay_sinh = self.entry_search_ngay_sinh.get().strip()
        results: List[BenhNhan] = []; title = "Kết quả tìm kiếm:"
        if ma_bn: 
            bn = self.he_thong.tim_benh_nhan_theo_ma(ma_bn)
            if bn: results.append(bn)
            else: title = f"Không tìm thấy BN với mã {ma_bn}."
        elif ho_ten or sdt or ngay_sinh : 
            results = self.he_thong.tim_benh_nhan_nang_cao(ho_ten=ho_ten, sdt=sdt, ngay_sinh=ngay_sinh)
            if not results: title = "Không tìm thấy BN nào khớp tiêu chí."
        else: self._show_message("Nhập ít nhất một tiêu chí tìm kiếm.", "INFO"); self._display_search_results([], title="Vui lòng nhập tiêu chí."); return
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
        ctk.CTkLabel(frame, text="Lịch sử Khám Bệnh (trong phiên làm việc):", font=("Arial", 14, "bold")).pack(pady=(10,5))
        tree_frame_da_kham = ctk.CTkFrame(frame); tree_frame_da_kham.pack(expand=True, fill="both", padx=10, pady=5)
        cols = ("STT", "MaBN", "HoTen", "NgaySinh", "SDT", "TGDKHeThong", "KQ Kham", "GhiChuKham", "BS Khám", "PK Khám") 
        self.listbox_da_kham = ttk.Treeview(tree_frame_da_kham, columns=cols, show="headings", height=20)
        for col_name in cols: self.listbox_da_kham.heading(col_name, text=col_name)
        self.listbox_da_kham.column("STT", width=30, anchor="center"); self.listbox_da_kham.column("MaBN", width=70, anchor="center")
        self.listbox_da_kham.column("HoTen", width=150); self.listbox_da_kham.column("NgaySinh", width=90, anchor="center")
        self.listbox_da_kham.column("SDT", width=90, anchor="center"); self.listbox_da_kham.column("TGDKHeThong", width=120, anchor="center")
        self.listbox_da_kham.column("KQ Kham", width=180); self.listbox_da_kham.column("GhiChuKham", width=180)
        self.listbox_da_kham.column("BS Khám", width=80, anchor="w"); self.listbox_da_kham.column("PK Khám", width=80, anchor="w")
        scrollbar_da_kham = ttk.Scrollbar(tree_frame_da_kham, orient="vertical", command=self.listbox_da_kham.yview)
        self.listbox_da_kham.configure(yscrollcommand=scrollbar_da_kham.set); scrollbar_da_kham.pack(side="right", fill="y")
        self.listbox_da_kham.pack(expand=True, fill="both")
        ctk.CTkButton(frame, text="Làm mới Danh sách Đã khám", command=self._refresh_da_kham_list).pack(pady=10)

    def _refresh_da_kham_list(self): 
        for item in self.listbox_da_kham.get_children(): self.listbox_da_kham.delete(item)
        da_kham_list = self.he_thong.liet_ke_benh_nhan_da_kham_hom_nay()
        for i, bn in enumerate(da_kham_list):
            kq, gc, bs_kham, pk_kham = "N/A", "N/A", "N/A", "N/A"
            if not bn.lich_su_kham_benh.is_empty():
                last_kham = bn.lich_su_kham_benh.get_last()
                if last_kham: 
                    kq = last_kham.get('ket_qua', "N/A"); gc = last_kham.get('ghi_chu', "N/A")
                    bs_kham = last_kham.get('ma_bac_si_kham', "N/A"); pk_kham = last_kham.get('ma_phong_kham_kham', "N/A")
            self.listbox_da_kham.insert("", "end", values=(
                i + 1, bn.ma_bn, bn.ho_ten, bn.ngay_sinh.strftime(DATE_FORMAT_CSV) if bn.ngay_sinh else "", bn.sdt,
                bn.thoi_diem_dang_ky_he_thong.strftime("%Y-%m-%d %H:%M") if bn.thoi_diem_dang_ky_he_thong else "", 
                kq, gc, bs_kham, pk_kham
            ))

    def _refresh_all_patient_lists(self): self._hien_thi_tat_ca_bn(); self._refresh_da_kham_list()
    def _refresh_all_doctor_clinic_lists(self): self._refresh_bac_si_list(); self._refresh_phong_kham_list(); self._populate_phong_kham_comboboxes()

    # --- CÁC HÀM XỬ LÝ CHO TAB BÁC SĨ VÀ PHÒNG KHÁM ---
    def _setup_bac_si_tab(self):
        frame = ctk.CTkFrame(self.tab_bac_si); frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="QUẢN LÝ THÔNG TIN BÁC SĨ", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        form_bs = ctk.CTkFrame(frame); form_bs.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(form_bs, text="Mã BS (trống nếu tạo mới):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_ma_bs = ctk.CTkEntry(form_bs, width=150); self.entry_ma_bs.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(form_bs, text="Tải BS để sửa", command=self._load_bac_si_for_edit).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(form_bs, text="Họ tên Bác sĩ (*):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_hoten_bs = ctk.CTkEntry(form_bs, width=300); self.entry_hoten_bs.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_bs, text="Chuyên khoa (*):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_chuyenkhoa_bs = ctk.CTkEntry(form_bs, width=300); self.entry_chuyenkhoa_bs.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        form_bs.grid_columnconfigure(1, weight=1)
        btn_frame_bs = ctk.CTkFrame(frame); btn_frame_bs.pack(pady=10, fill="x", padx=10)
        ctk.CTkButton(btn_frame_bs, text="Thêm BS", command=self._them_bac_si).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame_bs, text="Sửa BS", command=self._sua_bac_si).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame_bs, text="Xóa BS", command=self._xoa_bac_si, fg_color="red").pack(side="left", padx=10)
        ctk.CTkButton(btn_frame_bs, text="Làm mới", command=self._clear_bac_si_form).pack(side="left", padx=10)
        ctk.CTkLabel(frame, text="Danh sách Bác sĩ:", font=ctk.CTkFont(size=12)).pack(pady=(10,0))
        bs_tree_frame = ctk.CTkFrame(frame); bs_tree_frame.pack(expand=True, fill="both", padx=10, pady=5)
        cols_bs = ("MaBS", "HoTenBS", "ChuyenKhoa", "MaPhongKham")
        self.tree_bac_si = ttk.Treeview(bs_tree_frame, columns=cols_bs, show="headings", height=10)
        for col in cols_bs: self.tree_bac_si.heading(col, text=col)
        self.tree_bac_si.column("MaBS", width=80, anchor="w"); self.tree_bac_si.column("HoTenBS", width=200, anchor="w")
        self.tree_bac_si.column("ChuyenKhoa", width=150, anchor="w"); self.tree_bac_si.column("MaPhongKham", width=250, anchor="w")
        bs_scrollbar = ttk.Scrollbar(bs_tree_frame, orient="vertical", command=self.tree_bac_si.yview)
        self.tree_bac_si.configure(yscrollcommand=bs_scrollbar.set); bs_scrollbar.pack(side="right", fill="y"); self.tree_bac_si.pack(expand=True, fill="both")
        self.tree_bac_si.bind("<<TreeviewSelect>>", self._on_bac_si_select)

    def _setup_phong_kham_tab(self):
        frame = ctk.CTkFrame(self.tab_phong_kham); frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(frame, text="QUẢN LÝ THÔNG TIN PHÒNG KHÁM", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        form_pk = ctk.CTkFrame(frame); form_pk.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(form_pk, text="Mã PK (trống nếu tạo mới):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_ma_pk = ctk.CTkEntry(form_pk, width=150); self.entry_ma_pk.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(form_pk, text="Tải PK để sửa", command=self._load_phong_kham_for_edit).grid(row=0, column=2, padx=5, pady=5)
        ctk.CTkLabel(form_pk, text="Tên Phòng khám (*):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_ten_pk = ctk.CTkEntry(form_pk, width=300); self.entry_ten_pk.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(form_pk, text="Chuyên khoa PK (*):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_chuyenkhoa_pk = ctk.CTkEntry(form_pk, width=300); self.entry_chuyenkhoa_pk.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        form_pk.grid_columnconfigure(1, weight=1)
        btn_frame_pk = ctk.CTkFrame(frame); btn_frame_pk.pack(pady=10, fill="x", padx=10)
        ctk.CTkButton(btn_frame_pk, text="Thêm PK", command=self._them_phong_kham).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame_pk, text="Sửa PK", command=self._sua_phong_kham).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame_pk, text="Xóa PK", command=self._xoa_phong_kham, fg_color="red").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame_pk, text="Làm mới Form", command=self._clear_phong_kham_form).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame_pk, text="Gán/Xóa BS cho PK", command=self._quan_ly_bs_cho_pk).pack(side="left", padx=5)
        ctk.CTkLabel(frame, text="Danh sách Phòng khám:", font=ctk.CTkFont(size=12)).pack(pady=(10,0))
        pk_tree_frame = ctk.CTkFrame(frame); pk_tree_frame.pack(expand=True, fill="both", padx=10, pady=5)
        cols_pk = ("MaPK", "TenPK", "ChuyenKhoaPK", "MaBacSiTrongPK")
        self.tree_phong_kham = ttk.Treeview(pk_tree_frame, columns=cols_pk, show="headings", height=10)
        for col in cols_pk: self.tree_phong_kham.heading(col, text=col)
        self.tree_phong_kham.column("MaPK", width=80, anchor="w"); self.tree_phong_kham.column("TenPK", width=200, anchor="w")
        self.tree_phong_kham.column("ChuyenKhoaPK", width=150, anchor="w"); self.tree_phong_kham.column("MaBacSiTrongPK", width=250, anchor="w")
        pk_scrollbar = ttk.Scrollbar(pk_tree_frame, orient="vertical", command=self.tree_phong_kham.yview)
        self.tree_phong_kham.configure(yscrollcommand=pk_scrollbar.set); pk_scrollbar.pack(side="right", fill="y"); self.tree_phong_kham.pack(expand=True, fill="both")
        self.tree_phong_kham.bind("<<TreeviewSelect>>", self._on_phong_kham_select)

    def _clear_bac_si_form(self): self.entry_ma_bs.delete(0, "end"); self.entry_hoten_bs.delete(0, "end"); self.entry_chuyenkhoa_bs.delete(0, "end")
    def _refresh_bac_si_list(self):
        for i in self.tree_bac_si.get_children(): self.tree_bac_si.delete(i)
        for bs in self.he_thong.liet_ke_tat_ca_bac_si(): self.tree_bac_si.insert("", "end", values=(bs.ma_bac_si, bs.ho_ten_bac_si, bs.chuyen_khoa, ", ".join(bs.danh_sach_ma_phong_kham) or "Chưa có"))
    def _on_bac_si_select(self, event=None):
        try:
            item = self.tree_bac_si.selection()[0]; values = self.tree_bac_si.item(item, "values")
            if values: self.entry_ma_bs.delete(0, "end"); self.entry_ma_bs.insert(0, values[0]); self.entry_hoten_bs.delete(0, "end"); self.entry_hoten_bs.insert(0, values[1]); self.entry_chuyenkhoa_bs.delete(0, "end"); self.entry_chuyenkhoa_bs.insert(0, values[2])
        except IndexError: pass
    def _load_bac_si_for_edit(self):
        ma_bs = self.entry_ma_bs.get().strip(); 
        if not ma_bs: self._show_message("Nhập Mã BS để tải.", "ERROR"); return
        bs = self.he_thong.tim_bac_si_theo_ma(ma_bs)
        if bs: self.entry_hoten_bs.delete(0, "end"); self.entry_hoten_bs.insert(0, bs.ho_ten_bac_si); self.entry_chuyenkhoa_bs.delete(0, "end"); self.entry_chuyenkhoa_bs.insert(0, bs.chuyen_khoa); self._show_message(f"Đã tải BS {ma_bs}.", "INFO")
        else: self._show_message(f"Không tìm thấy BS {ma_bs}.", "ERROR")
    def _them_bac_si(self):
        ht = self.entry_hoten_bs.get().strip(); ck = self.entry_chuyenkhoa_bs.get().strip()
        _obj, msg, lvl = self.he_thong.tao_bac_si(ht, ck); self._show_message(msg, lvl)
        if _obj: self._refresh_bac_si_list(); self._clear_bac_si_form(); self._refresh_all_doctor_clinic_lists()
    def _sua_bac_si(self):
        ma = self.entry_ma_bs.get().strip(); ht = self.entry_hoten_bs.get().strip(); ck = self.entry_chuyenkhoa_bs.get().strip()
        if not ma: self._show_message("Tải Mã BS để sửa.", "ERROR"); return
        upd = {}; 
        if ht: upd["ho_ten_moi"] = ht
        if ck: upd["chuyen_khoa_moi"] = ck
        if not upd: self._show_message("Không có thông tin mới.", "INFO"); return
        s, msg, lvl = self.he_thong.sua_thong_tin_bac_si(ma, **upd); self._show_message(msg, lvl)
        if s and lvl == "INFO": self._refresh_bac_si_list(); self._refresh_all_doctor_clinic_lists()
    def _xoa_bac_si(self):
        ma = self.entry_ma_bs.get().strip()
        if not ma: self._show_message("Tải Mã BS để xóa.", "ERROR"); return
        if messagebox.askyesno("Xác nhận", f"Xóa BS {ma}? Sẽ xóa BS khỏi các PK liên quan."):
            s, msg, lvl = self.he_thong.xoa_bac_si(ma); self._show_message(msg, lvl)
            if s: self._refresh_bac_si_list(); self._refresh_phong_kham_list(); self._clear_bac_si_form(); self._refresh_all_doctor_clinic_lists()
    def _clear_phong_kham_form(self): self.entry_ma_pk.delete(0, "end"); self.entry_ten_pk.delete(0, "end"); self.entry_chuyenkhoa_pk.delete(0, "end")
    def _refresh_phong_kham_list(self):
        for i in self.tree_phong_kham.get_children(): self.tree_phong_kham.delete(i)
        for pk in self.he_thong.liet_ke_tat_ca_phong_kham(): self.tree_phong_kham.insert("", "end", values=(pk.ma_phong_kham, pk.ten_phong_kham, pk.chuyen_khoa_pk, ", ".join(pk.danh_sach_ma_bac_si) or "Chưa có"))
    def _on_phong_kham_select(self, event=None):
        try:
            item = self.tree_phong_kham.selection()[0]; values = self.tree_phong_kham.item(item, "values")
            if values: self.entry_ma_pk.delete(0, "end"); self.entry_ma_pk.insert(0, values[0]); self.entry_ten_pk.delete(0, "end"); self.entry_ten_pk.insert(0, values[1]); self.entry_chuyenkhoa_pk.delete(0, "end"); self.entry_chuyenkhoa_pk.insert(0, values[2])
        except IndexError: pass
    def _load_phong_kham_for_edit(self):
        ma = self.entry_ma_pk.get().strip()
        if not ma: self._show_message("Nhập Mã PK để tải.", "ERROR"); return
        pk = self.he_thong.tim_phong_kham_theo_ma(ma)
        if pk: self.entry_ten_pk.delete(0, "end"); self.entry_ten_pk.insert(0, pk.ten_phong_kham); self.entry_chuyenkhoa_pk.delete(0, "end"); self.entry_chuyenkhoa_pk.insert(0, pk.chuyen_khoa_pk); self._show_message(f"Đã tải PK {ma}.", "INFO")
        else: self._show_message(f"Không tìm thấy PK {ma}.", "ERROR")
    def _them_phong_kham(self):
        ten = self.entry_ten_pk.get().strip(); ck = self.entry_chuyenkhoa_pk.get().strip()
        _obj, msg, lvl = self.he_thong.tao_phong_kham(ten, ck); self._show_message(msg, lvl)
        if _obj: self._refresh_phong_kham_list(); self._clear_phong_kham_form(); self._refresh_all_doctor_clinic_lists()
    def _sua_phong_kham(self):
        ma = self.entry_ma_pk.get().strip(); ten = self.entry_ten_pk.get().strip(); ck = self.entry_chuyenkhoa_pk.get().strip()
        if not ma: self._show_message("Tải Mã PK để sửa.", "ERROR"); return
        upd = {}; 
        if ten: upd["ten_moi"] = ten
        if ck: upd["chuyen_khoa_moi"] = ck
        if not upd: self._show_message("Không có thông tin mới.", "INFO"); return
        s, msg, lvl = self.he_thong.sua_thong_tin_phong_kham(ma, **upd); self._show_message(msg, lvl)
        if s and lvl=="INFO": self._refresh_phong_kham_list(); self._refresh_all_doctor_clinic_lists()
    def _xoa_phong_kham(self):
        ma = self.entry_ma_pk.get().strip()
        if not ma: self._show_message("Tải Mã PK để xóa.", "ERROR"); return
        if messagebox.askyesno("Xác nhận", f"Xóa PK {ma}? Sẽ xóa PK khỏi DS làm việc của BS liên quan."):
            s, msg, lvl = self.he_thong.xoa_phong_kham(ma); self._show_message(msg, lvl)
            if s: self._refresh_phong_kham_list(); self._refresh_bac_si_list(); self._clear_phong_kham_form(); self._refresh_all_doctor_clinic_lists()
    def _quan_ly_bs_cho_pk(self):
        ma_pk = self.entry_ma_pk.get().strip()
        if not ma_pk: self._show_message("Tải hoặc nhập Mã PK trước.", "WARNING"); return
        pk = self.he_thong.tim_phong_kham_theo_ma(ma_pk)
        if not pk: self._show_message(f"Không tìm thấy PK {ma_pk}.", "ERROR"); return
        action = simpledialog.askstring("Quản lý BS cho PK", f"PK: {pk.ten_phong_kham} ({ma_pk})\nDS BS hiện tại: {', '.join(pk.danh_sach_ma_bac_si) or 'Chưa có'}\n\nNhập 'them <Mã BS>' hoặc 'xoa <Mã BS>':", parent=self)
        if action:
            parts = action.strip().lower().split(); cmd, ma_bs = (parts[0], parts[1].upper()) if len(parts) == 2 else (None, None)
            if cmd == "them" and ma_bs: s, msg, lvl = self.he_thong.them_bac_si_vao_phong_kham(ma_bs, ma_pk)
            elif cmd == "xoa" and ma_bs: s, msg, lvl = self.he_thong.xoa_bac_si_khoi_phong_kham(ma_bs, ma_pk)
            else: self._show_message("Lệnh không hợp lệ. Dùng 'them <Mã BS>' hoặc 'xoa <Mã BS>'.", "ERROR"); return
            self._show_message(msg, lvl)
            if s and lvl == "INFO": self._refresh_phong_kham_list(); self._refresh_bac_si_list() # Làm mới cả 2 list

    def _refresh_all_patient_lists(self): self._hien_thi_tat_ca_bn(); self._refresh_da_kham_list()
    def _refresh_all_doctor_clinic_lists(self): self._refresh_bac_si_list(); self._refresh_phong_kham_list(); self._populate_phong_kham_comboboxes()

if __name__ == "__main__":
    he_thong_ql = HeThongQuanLyKhamBenh()
    app = AppGUI(he_thong_ql)
    app.mainloop()
