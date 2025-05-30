# main_gui.py
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import datetime
from typing import List, Optional 

# Thay đổi import:
from app_logic import HeThongQuanLyKhamBenh
from models import PatientInQueue, BenhNhan, DATE_FORMAT_CSV 
from custom_structures import PriorityQueue

PRIORITY_LEVELS = list(PatientInQueue.PRIORITY_MAP.keys()) 

class AppGUI(ctk.CTk):
    def __init__(self, he_thong: HeThongQuanLyKhamBenh):
        super().__init__()
        self.he_thong = he_thong
        self.title("Hệ thống Quản lý Khám Bệnh")
        self.geometry("1100x750") 
        ctk.set_appearance_mode("System") 
        ctk.set_default_color_theme("blue")
        self.tab_view = ctk.CTkTabview(self, width=1080, height=730)
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

    def _setup_dang_ky_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_dang_ky, label_text="Quản lý Hồ sơ Bệnh nhân") 
        frame.pack(expand=True, fill="both", padx=10, pady=10)
        form_frame = ctk.CTkFrame(frame)
        form_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(form_frame, text="Mã BN (để trống nếu tạo mới):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_ma_bn_dk = ctk.CTkEntry(form_frame, width=250)
        self.entry_ma_bn_dk.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(form_frame, text="Tải BN để sửa/đăng ký khám", command=self._load_patient_for_edit).grid(row=0, column=2, padx=5, pady=5)

        fields = [
            ("Họ tên (*):", "họ_tên"), ("Ngày sinh (YYYY-MM-DD) (*):", "ngày_sinh"), 
            ("Giới tính (Nam/Nữ/Khác) (*):", "giới_tính"), 
            ("CCCD (*):", "cccd"), # Thêm dấu (*)
            ("SĐT (*):", "sđt"), 
            ("Địa chỉ:", "địa_chỉ"), ("BHYT:", "bhyt"), 
            ("Tiền sử bệnh án:", "tiền_sử_bệnh_án"), ("Dị ứng thuốc:", "dị_ứng_thuốc")
        ]
        self.entries_dk = {}
        for i, (label_text, key) in enumerate(fields):
            ctk.CTkLabel(form_frame, text=label_text).grid(row=i+1, column=0, padx=5, pady=5, sticky="w")
            if "tiền_sử" in key or "dị_ứng" in key or "địa_chỉ" in key : 
                entry = ctk.CTkEntry(form_frame, width=350)
            else:
                entry = ctk.CTkEntry(form_frame, width=350)
            entry.grid(row=i+1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
            self.entries_dk[key] = entry
        form_frame.grid_columnconfigure(1, weight=1)

        btn_frame_dk = ctk.CTkFrame(frame)
        btn_frame_dk.pack(pady=10, fill="x", padx=10)
        ctk.CTkButton(btn_frame_dk, text="Tạo mới Hồ sơ", command=self._tao_moi_ho_so).pack(side="left", padx=10, pady=5)
        ctk.CTkButton(btn_frame_dk, text="Cập nhật Hồ sơ", command=self._cap_nhat_ho_so).pack(side="left", padx=10, pady=5)
        ctk.CTkButton(btn_frame_dk, text="Xóa Hồ sơ", command=self._xoa_ho_so, fg_color="red").pack(side="left", padx=10, pady=5)
        ctk.CTkButton(btn_frame_dk, text="Làm mới Form", command=self._clear_dk_form).pack(side="left", padx=10, pady=5)

        dk_kham_frame = ctk.CTkFrame(frame)
        dk_kham_frame.pack(pady=20, padx=10, fill="x",ipadx=5, ipady=5)
        ctk.CTkLabel(dk_kham_frame, text="ĐĂNG KÝ KHÁM CHO BỆNH NHÂN:", font=("Arial", 12, "bold")).pack(pady=5)
        sub_dk_kham_frame = ctk.CTkFrame(dk_kham_frame)
        sub_dk_kham_frame.pack(fill="x")
        ctk.CTkLabel(sub_dk_kham_frame, text="Mã BN để đăng ký khám:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.entry_ma_bn_kham = ctk.CTkEntry(sub_dk_kham_frame, width=150, placeholder_text="Tải BN ở trên hoặc nhập")
        self.entry_ma_bn_kham.grid(row=0, column=1, padx=5, pady=10)
        ctk.CTkLabel(sub_dk_kham_frame, text="Mức độ ưu tiên:").grid(row=0, column=2, padx=5, pady=10, sticky="w")
        self.combo_priority_dk = ctk.CTkComboBox(sub_dk_kham_frame, values=PRIORITY_LEVELS, width=150)
        self.combo_priority_dk.grid(row=0, column=3, padx=5, pady=10)
        if PRIORITY_LEVELS: self.combo_priority_dk.set(PRIORITY_LEVELS[1] if len(PRIORITY_LEVELS) > 1 else PRIORITY_LEVELS[0]) 
        ctk.CTkButton(sub_dk_kham_frame, text="Đăng ký Khám", command=self._dang_ky_kham, height=40).grid(row=0, column=4, padx=20, pady=10)

    def _clear_dk_form(self, clear_ma_bn=True):
        if clear_ma_bn: self.entry_ma_bn_dk.delete(0, "end")
        for widget in self.entries_dk.values():
            if isinstance(widget, ctk.CTkEntry): widget.delete(0, "end")
            elif isinstance(widget, ctk.CTkTextbox): widget.delete("1.0", "end")
        self.entry_ma_bn_kham.delete(0, "end")

    def _load_patient_for_edit(self):
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: messagebox.showerror("Lỗi", "Vui lòng nhập Mã BN để tải thông tin."); return
        bn = self.he_thong.tim_benh_nhan_theo_ma(ma_bn)
        if bn:
            self._clear_dk_form(clear_ma_bn=False)
            self.entries_dk["họ_tên"].insert(0, bn.ho_ten or "")
            self.entries_dk["ngày_sinh"].insert(0, bn.ngay_sinh.strftime(DATE_FORMAT_CSV) if bn.ngay_sinh else "")
            self.entries_dk["giới_tính"].insert(0, bn.gioi_tinh or "")
            self.entries_dk["cccd"].insert(0, bn.cccd or "") # Tải CCCD
            self.entries_dk["sđt"].insert(0, bn.sdt or "")
            self.entries_dk["địa_chỉ"].insert("1.0", bn.dia_chi or "")
            self.entries_dk["bhyt"].insert(0, bn.bhyt or "")
            self.entries_dk["tiền_sử_bệnh_án"].insert("1.0", bn.tien_su_benh_an or "")
            self.entries_dk["dị_ứng_thuốc"].insert("1.0", bn.di_ung_thuoc or "")
            self.entry_ma_bn_kham.delete(0, "end"); self.entry_ma_bn_kham.insert(0, ma_bn)
            messagebox.showinfo("Thông báo", f"Đã tải thông tin BN: {ma_bn} - {bn.ho_ten}")
        else:
            messagebox.showerror("Lỗi", f"Không tìm thấy bệnh nhân với mã: {ma_bn}")
            self._clear_dk_form(clear_ma_bn=False); self.entry_ma_bn_kham.delete(0, "end")

    def _tao_moi_ho_so(self): 
        data = {k: (w.get("1.0", "end-1c").strip() if isinstance(w, ctk.CTkTextbox) else w.get().strip()) for k, w in self.entries_dk.items()}
        # Kiểm tra các trường bắt buộc, bao gồm CCCD
        if not data["họ_tên"] or not data["ngày_sinh"] or not data["giới_tính"] or not data["sđt"] or not data["cccd"]:
             messagebox.showerror("Lỗi", "Họ tên, Ngày sinh, Giới tính, SĐT và CCCD là các trường bắt buộc.")
             return
        try: datetime.datetime.strptime(data["ngày_sinh"], DATE_FORMAT_CSV)
        except ValueError: messagebox.showerror("Lỗi", f"Định dạng Ngày sinh không hợp lệ."); return

        bn = self.he_thong.tao_ho_so_benh_nhan(
            ho_ten=data["họ_tên"], ngay_sinh_str=data["ngày_sinh"], gioi_tinh=data["giới_tính"],
            dia_chi=data["địa_chỉ"], sdt=data["sđt"], cccd=data["cccd"], # Truyền cccd
            bhyt=data["bhyt"], tien_su=data["tiền_sử_bệnh_án"], di_ung=data["dị_ứng_thuốc"]
        )
        if bn:
            messagebox.showinfo("Thành công", f"Đã tạo hồ sơ cho BN: {bn.ma_bn} - {bn.ho_ten}")
            self.entry_ma_bn_dk.delete(0, "end"); self.entry_ma_bn_dk.insert(0, bn.ma_bn) 
            self.entry_ma_bn_kham.delete(0,"end"); self.entry_ma_bn_kham.insert(0, bn.ma_bn) 
            self._refresh_all_patient_lists()
        # else: app_logic sẽ in lỗi ra console

    def _cap_nhat_ho_so(self): 
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: messagebox.showerror("Lỗi", "Vui lòng nhập Mã BN của hồ sơ cần cập nhật."); return
        
        update_data_raw = {k: (w.get("1.0", "end-1c").strip() if isinstance(w, ctk.CTkTextbox) else w.get().strip()) for k, w in self.entries_dk.items()}
        # Kiểm tra CCCD không được để trống khi cập nhật
        if not update_data_raw["cccd"]:
            messagebox.showerror("Lỗi", "Số CCCD không được để trống khi cập nhật.")
            return
        if update_data_raw.get("ngày_sinh"):
             try: datetime.datetime.strptime(update_data_raw["ngày_sinh"], DATE_FORMAT_CSV)
             except ValueError: messagebox.showerror("Lỗi", f"Định dạng Ngày sinh không hợp lệ."); return

        update_data = { # Ánh xạ key nếu cần, ở đây key giống nhau
            "ho_ten": update_data_raw["họ_tên"], "ngay_sinh": update_data_raw["ngày_sinh"], 
            "gioi_tinh": update_data_raw["giới_tính"], "dia_chi": update_data_raw["địa_chỉ"], 
            "sdt": update_data_raw["sđt"], "cccd": update_data_raw["cccd"], # Truyền cccd
            "bhyt": update_data_raw["bhyt"], "tien_su_benh_an": update_data_raw["tiền_sử_bệnh_án"], 
            "di_ung_thuoc": update_data_raw["dị_ứng_thuốc"]
        }
        if self.he_thong.cap_nhat_thong_tin_benh_nhan(ma_bn, **update_data):
            messagebox.showinfo("Thành công", f"Đã cập nhật hồ sơ cho BN: {ma_bn}")
            self._refresh_all_patient_lists()
        # else: app_logic có thể đã in lỗi hoặc trả về False nếu không có thay đổi

    def _xoa_ho_so(self): 
        # Code như trước, không thay đổi
        ma_bn = self.entry_ma_bn_dk.get().strip()
        if not ma_bn: messagebox.showerror("Lỗi", "Vui lòng nhập Mã BN của hồ sơ cần xóa."); return
        bn_in_queue = any(self.listbox_hang_doi.item(item_id)['values'][1] == ma_bn for item_id in self.listbox_hang_doi.get_children())
        warning_message = f"\nLƯU Ý: Bệnh nhân {ma_bn} đang có trong hàng đợi khám." if bn_in_queue else ""
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa hồ sơ BN: {ma_bn}? {warning_message}"):
            if self.he_thong.xoa_ho_so_benh_nhan(ma_bn):
                messagebox.showinfo("Thành công", f"Đã xóa hồ sơ BN: {ma_bn}")
                self._clear_dk_form(); self._refresh_all_patient_lists()

    def _dang_ky_kham(self): 
        # Code như trước, không thay đổi
        ma_bn_kham_input = self.entry_ma_bn_kham.get().strip()
        ma_bn_form = self.entry_ma_bn_dk.get().strip()
        final_ma_bn = ma_bn_kham_input if ma_bn_kham_input else ma_bn_form
        if not final_ma_bn: messagebox.showerror("Lỗi", "Vui lòng nhập Mã BN để đăng ký khám."); return
        priority_str = self.combo_priority_dk.get()
        if not priority_str: messagebox.showerror("Lỗi", "Vui lòng chọn mức độ ưu tiên."); return
        if self.he_thong.dang_ky_kham_benh(final_ma_bn, priority_str):
            messagebox.showinfo("Thành công", f"BN {final_ma_bn} đã được thêm vào hàng đợi.")
            self._refresh_hang_doi_list()

    def _setup_hang_doi_tab(self):
        # Code như trước, không thay đổi nhiều ở phần setup
        frame = self.tab_hang_doi
        self.label_dang_kham = ctk.CTkLabel(frame, text="Đang khám: Chưa có", font=("Arial", 16, "bold"), text_color="green")
        self.label_dang_kham.pack(pady=10)
        controls_frame = ctk.CTkFrame(frame); controls_frame.pack(pady=5, fill="x", padx=10)
        ctk.CTkButton(controls_frame, text="Gọi BN Tiếp theo", command=self._goi_kham).pack(side="left", padx=10, pady=5)
        ctk.CTkButton(controls_frame, text="Hoàn thành Khám", command=self._hoan_thanh_kham).pack(side="left", padx=10, pady=5)
        # Nút Vắng mặt sẽ áp dụng cho self.benh_nhan_dang_kham
        ctk.CTkButton(controls_frame, text="BN Đang Gọi Vắng mặt", command=self._bn_vang_mat, fg_color="orange").pack(side="left", padx=10, pady=5)
        ctk.CTkButton(controls_frame, text="BN Rời đi (Trong Hàng Đợi)", command=self._bn_roi_di, fg_color="tomato").pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(frame, text="Danh sách bệnh nhân đang chờ khám:", font=("Arial", 12)).pack(pady=(10,0))
        tree_frame = ctk.CTkFrame(frame); tree_frame.pack(expand=True, fill="both", padx=10, pady=5)
        columns = ("STT", "MaBN", "HoTen", "UuTien", "TGDangKy", "SoLanVang")
        self.listbox_hang_doi = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        for col_name in columns: self.listbox_hang_doi.heading(col_name, text=col_name)
        self.listbox_hang_doi.column("STT", width=40, anchor="center"); self.listbox_hang_doi.column("MaBN", width=80, anchor="center")
        self.listbox_hang_doi.column("HoTen", width=220); self.listbox_hang_doi.column("UuTien", width=150, anchor="center")
        self.listbox_hang_doi.column("TGDangKy", width=100, anchor="center"); self.listbox_hang_doi.column("SoLanVang", width=50, anchor="center")
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.listbox_hang_doi.yview)
        self.listbox_hang_doi.configure(yscrollcommand=scrollbar.set); scrollbar.pack(side="right", fill="y")
        self.listbox_hang_doi.pack(expand=True, fill="both")
        action_frame = ctk.CTkFrame(frame); action_frame.pack(pady=5, fill="x", padx=10)
        ctk.CTkButton(action_frame, text="Làm mới Hàng đợi", command=self._refresh_hang_doi_list).pack(side="left", padx=10, pady=5)
        ctk.CTkButton(action_frame, text="Cập nhật Ưu tiên (Chờ lâu)", command=self._update_priority_long_wait).pack(side="left", padx=10, pady=5)
        self._refresh_hang_doi_list()

    def _refresh_hang_doi_list(self):
        # Code như trước, không thay đổi
        for item in self.listbox_hang_doi.get_children(): self.listbox_hang_doi.delete(item)
        # Lấy danh sách hiển thị từ app_logic
        display_list = self.he_thong.hien_thi_hang_doi_cho_kham() # hàm này trả về List[str]
        # Cần parse lại chuỗi này hoặc có hàm trả về List[PatientInQueue] đã sắp xếp từ app_logic
        # Để đơn giản, ta sẽ dùng hàm hien_thi_hang_doi_cho_kham và parse lại thông tin STT, MaBN,...
        # Hoặc, tốt hơn là app_logic cung cấp một hàm lấy danh sách đối tượng PatientInQueue đã sắp xếp
        
        # Cách hiện tại: Tạo lại logic sắp xếp ở GUI (không lý tưởng nhưng giữ logic display_queue của PriorityQueue)
        temp_pq_display = PriorityQueue() # Import PriorityQueue từ custom_structures
        all_in_main_heap = self.he_thong.hang_doi_kham.k.get_all_elements()
        for p_item_orig in all_in_main_heap:
            profile_ref = p_item_orig.profile 
            p_copy = PatientInQueue(profile_ref, p_item_orig.get_priority_display(), p_item_orig.registrationTime)
            p_copy.priority = p_item_orig.priority 
            p_copy.absentCount = p_item_orig.absentCount
            temp_pq_display.add(p_copy)
        
        sorted_patients_for_display: List[PatientInQueue] = []
        while not temp_pq_display.is_empty():
            p = temp_pq_display.removeFirst()
            if p: sorted_patients_for_display.append(p)

        for i, p_in_q in enumerate(sorted_patients_for_display):
            self.listbox_hang_doi.insert("", "end", values=(
                i + 1, p_in_q.patientID, p_in_q.profile.ho_ten,
                f"{p_in_q.get_priority_display()} ({p_in_q.priority})",
                p_in_q.registrationTime.strftime('%H:%M:%S'), p_in_q.absentCount
            ))

    def _goi_kham(self): 
        # Code như trước, không thay đổi
        if self.benh_nhan_dang_kham:
            messagebox.showwarning("Lưu ý", f"BN {self.benh_nhan_dang_kham.profile.ho_ten} đang khám.")
            return
        benh_nhan_kham_obj = self.he_thong.goi_benh_nhan_kham() 
        if benh_nhan_kham_obj: 
            self.benh_nhan_dang_kham = benh_nhan_kham_obj 
            bn_info = self.benh_nhan_dang_kham.profile
            self.label_dang_kham.configure(text=f"Đang khám: {bn_info.ma_bn} - {bn_info.ho_ten}")
            self._refresh_hang_doi_list()
        else:
            self.label_dang_kham.configure(text="Đang khám: Hàng đợi rỗng"); self.benh_nhan_dang_kham = None

    def _hoan_thanh_kham(self): 
        # Code như trước, không thay đổi
        if not self.benh_nhan_dang_kham: messagebox.showerror("Lỗi", "Chưa có BN được gọi khám."); return
        ma_bn_kham = self.benh_nhan_dang_kham.patientID
        ho_ten_bn_kham = self.benh_nhan_dang_kham.profile.ho_ten
        ket_qua = simpledialog.askstring("Kết quả khám", f"Kết quả khám cho BN {ma_bn_kham} ({ho_ten_bn_kham}):", parent=self)
        if ket_qua is None: return 
        ghi_chu = simpledialog.askstring("Ghi chú", f"Ghi chú cho BN {ma_bn_kham}:", parent=self) or ""
        self.he_thong.hoan_thanh_kham(ma_bn_kham, ket_qua, ghi_chu)
        messagebox.showinfo("Hoàn thành", f"BN {ma_bn_kham} đã khám xong.")
        self.label_dang_kham.configure(text="Đang khám: Chưa có"); self.benh_nhan_dang_kham = None
        self._refresh_hang_doi_list(); self._refresh_da_kham_list()

    def _bn_vang_mat(self): 
        # Áp dụng cho bệnh nhân đang được gọi (self.benh_nhan_dang_kham)
        if not self.benh_nhan_dang_kham:
            messagebox.showerror("Lỗi", "Chưa có bệnh nhân nào đang được gọi để báo vắng mặt.")
            return

        patient_called_obj = self.benh_nhan_dang_kham
        
        if messagebox.askyesno("Xác nhận vắng mặt", 
                               f"Xác nhận bệnh nhân ĐANG ĐƯỢC GỌI: {patient_called_obj.profile.ho_ten} (ID: {patient_called_obj.patientID}) vắng mặt?"):
            
            # Xử lý logic nghiệp vụ
            bi_loai_bo = self.he_thong.xu_ly_benh_nhan_vang_mat(patient_called_obj)

            # Cập nhật GUI: Xóa BN khỏi vị trí "Đang khám" vì đã xử lý xong (dù vắng mặt)
            self.label_dang_kham.configure(text="Đang khám: Chưa có")
            self.benh_nhan_dang_kham = None 

            if bi_loai_bo: # Nếu BN bị loại bỏ hoàn toàn (vắng 3 lần)
                 messagebox.showinfo("Thông báo", f"Bệnh nhân {patient_called_obj.patientID} đã bị loại do vắng mặt đủ số lần.")
            else: # Nếu BN được đưa lại vào hàng đợi
                 messagebox.showinfo("Thông báo", f"Bệnh nhân {patient_called_obj.patientID} đã được ghi nhận vắng mặt và đưa lại vào hàng đợi với ưu tiên có thể đã thay đổi.")
            
            self._refresh_hang_doi_list() # Cập nhật lại hiển thị hàng đợi

    def _bn_roi_di(self): 
        # Code như trước, không thay đổi
        selected_item_id = self.listbox_hang_doi.focus()
        ma_bn_roi_default = self.listbox_hang_doi.item(selected_item_id, "values")[1] if selected_item_id and self.listbox_hang_doi.item(selected_item_id, "values") else ""
        ma_bn_roi = simpledialog.askstring("BN Rời Hàng Đợi", "Nhập Mã BN rời đi:", initialvalue=ma_bn_roi_default, parent=self)
        if ma_bn_roi and ma_bn_roi.strip():
            if self.he_thong.benh_nhan_roi_di_khi_dang_cho(ma_bn_roi.strip()):
                messagebox.showinfo("Thành công", f"Đã xóa BN {ma_bn_roi.strip()} khỏi hàng đợi.")
                self._refresh_hang_doi_list()
        elif ma_bn_roi is not None: messagebox.showwarning("Cảnh báo", "Mã BN không được để trống.")

    def _update_priority_long_wait(self): 
        # Code như trước, không thay đổi
        thoi_gian_cho_str = simpledialog.askstring("Cập nhật Ưu tiên (Chờ lâu)", "Thời gian chờ tối đa (giây):", initialvalue="3600", parent=self)
        if thoi_gian_cho_str:
            try:
                thoi_gian_cho_giay = int(thoi_gian_cho_str)
                if thoi_gian_cho_giay <= 0: messagebox.showerror("Lỗi", "Thời gian chờ phải dương."); return
                self.he_thong.cap_nhat_uu_tien_cho_benh_nhan_cho_lau(thoi_gian_cho_giay)
                self._refresh_hang_doi_list()
            except ValueError: messagebox.showerror("Lỗi", "Thời gian chờ phải là số nguyên.")

    def _setup_tim_kiem_tab(self): 
        # Code như trước, không thay đổi
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
        self.text_search_results = ctk.CTkTextbox(frame, height=400, width=780, font=("Arial", 13)); 
        self.text_search_results.pack(pady=10, padx=10, expand=True, fill="both")
        self._clear_search_form() # Khởi tạo với thông báo

    def _clear_search_form(self):
        # Code như trước, không thay đổi
        self.entry_search_ma_bn.delete(0, "end"); self.entry_search_ho_ten.delete(0, "end")
        self.entry_search_sdt.delete(0, "end"); self.entry_search_ngay_sinh.delete(0, "end")
        self.text_search_results.configure(state="normal"); self.text_search_results.delete("1.0", "end")
        self.text_search_results.insert("end", "Nhập tiêu chí và tìm kiếm, hoặc hiển thị tất cả bệnh nhân."); self.text_search_results.configure(state="disabled")

    def _tim_kiem_benh_nhan(self): 
        # Code như trước, không thay đổi
        ma_bn = self.entry_search_ma_bn.get().strip(); ho_ten = self.entry_search_ho_ten.get().strip()
        sdt = self.entry_search_sdt.get().strip(); ngay_sinh = self.entry_search_ngay_sinh.get().strip()
        results: List[BenhNhan] = []
        if ma_bn: 
            bn = self.he_thong.tim_benh_nhan_theo_ma(ma_bn)
            if bn: results.append(bn)
        elif ho_ten or sdt or ngay_sinh : 
            search_criteria = {"ho_ten": ho_ten, "sdt": sdt, "ngay_sinh": ngay_sinh}
            results = self.he_thong.tim_benh_nhan_nang_cao(**search_criteria)
        else: messagebox.showinfo("Thông báo", "Nhập ít nhất một tiêu chí tìm kiếm."); self._display_search_results([], title="Nhập tiêu chí."); return
        self._display_search_results(results)

    def _hien_thi_tat_ca_bn(self): 
        # Code như trước, không thay đổi
        results = self.he_thong.liet_ke_tat_ca_benh_nhan()
        self._display_search_results(results, title="Danh sách tất cả bệnh nhân:")

    def _display_search_results(self, benh_nhan_list: List[BenhNhan], title="Kết quả tìm kiếm:"):
        # Code như trước, không thay đổi
        self.text_search_results.configure(state="normal"); self.text_search_results.delete("1.0", "end")
        if benh_nhan_list:
            self.text_search_results.insert("end", f"{title}\nTìm thấy {len(benh_nhan_list)} bệnh nhân.\n\n")
            for i, bn in enumerate(benh_nhan_list):
                self.text_search_results.insert("end", f"--- BN {i+1} ---\n" + bn.hien_thi_thong_tin_chi_tiet() + "\n\n" + "="*70 + "\n\n")
        else: self.text_search_results.insert("end", f"{title}\nKhông tìm thấy bệnh nhân nào khớp.")
        self.text_search_results.configure(state="disabled")

    def _setup_da_kham_tab(self): 
        # Code như trước, không thay đổi
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
        self._refresh_da_kham_list()

    def _refresh_da_kham_list(self): 
        # Code như trước, không thay đổi
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
        # Code như trước, không thay đổi
        self._hien_thi_tat_ca_bn(); self._refresh_da_kham_list()

if __name__ == "__main__":
    he_thong_ql = HeThongQuanLyKhamBenh()
    app = AppGUI(he_thong_ql)
    app.mainloop()