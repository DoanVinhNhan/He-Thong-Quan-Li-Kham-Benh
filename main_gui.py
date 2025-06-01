# main_gui.py
import customtkinter as ctk
from tkinter import ttk, messagebox, simpledialog
import datetime

from app_logic import MedicalSystemLogic 
from models import PatientInQueue, Patient, DATE_FORMAT_CSV, Doctor, Clinic 
from custom_structures import List # Đây là CustomArrayList đã đổi tên

class MedicalAppGUI(ctk.CTk): 
    def __init__(self, medical_system_logic_instance): 
        super().__init__() 
        self.medical_system_logic = medical_system_logic_instance 
        self.title("Hệ thống Quản lý Khám Bệnh Đa Khoa")
        self.geometry("1350x900") 
        ctk.set_appearance_mode("System"); ctk.set_default_color_theme("blue")

        self.tab_view_widget = ctk.CTkTabview(self, width=1330, height=880) 
        self.tab_view_widget.pack(expand=True, fill="both", padx=10, pady=10)

        self.registration_profile_tab = self.tab_view_widget.add("Đăng ký & Hồ sơ BN") 
        self.examination_queue_tab = self.tab_view_widget.add("Hàng đợi Khám")  
        self.doctor_management_tab = self.tab_view_widget.add("Quản lý Bác sĩ") 
        self.clinic_management_tab = self.tab_view_widget.add("Quản lý Phòng khám") 
        self.patient_search_tab = self.tab_view_widget.add("Tìm kiếm BN")  
        self.examination_history_tab = self.tab_view_widget.add("Tra cứu Lịch sử Khám")  
        
        self.priority_level_names = List() 
        temp_priority_keys_py = list(PatientInQueue.PRIORITY_MAP.keys()) 
        for key_item in temp_priority_keys_py: self.priority_level_names.append(key_item)
        
        # Gọi các hàm setup cho từng tab
        self._setup_registration_profile_tab() 
        self._setup_examination_queue_tab() 
        self._setup_doctor_management_tab() 
        self._setup_clinic_management_tab() 
        self._setup_patient_search_tab() 
        self._setup_examination_history_tab() 

        self.current_exam_patient = None 
        self.current_exam_clinic_id = None 
        
        # Gọi các hàm làm mới dữ liệu ban đầu
        self._populate_clinic_comboboxes() 
        self._display_all_patients_in_search_tab() 
        self._refresh_clinic_queue_display() 
        self._refresh_full_examination_history_list() 
        self._refresh_doctor_list_display() 
        self._refresh_clinic_list_display()

    def _show_gui_message(self, message_text, message_level): 
        # Hiển thị messagebox dựa trên level.
        if not message_text: return 
        if message_level == "INFO": messagebox.showinfo("Thông báo", message_text)
        elif message_level == "ERROR": messagebox.showerror("Lỗi", message_text)
        elif message_level == "WARNING": messagebox.showwarning("Cảnh báo", message_text)
        else: messagebox.showinfo("Thông báo", message_text) 

    def _convert_custom_list_to_py_list(self, custom_list_obj): 
        # Chuyển đổi CustomArrayList hoặc LinkedList sang list Python.
        py_list = []
        if custom_list_obj and len(custom_list_obj) > 0: 
             for i in range(len(custom_list_obj)):
                py_list.append(custom_list_obj.get(i))
        return py_list

    def _populate_clinic_comboboxes(self): 
        all_clinics_custom_list = self.medical_system_logic.list_all_clinics() 
        
        clinic_options_py = [] 
        if len(all_clinics_custom_list) > 0:
            for i in range(len(all_clinics_custom_list)):
                clinic_obj = all_clinics_custom_list.get(i) 
                clinic_options_py.append(f"{clinic_obj.clinic_id} - {clinic_obj.clinic_name}")
        else:
            clinic_options_py = ["Chưa có phòng khám"]
        
        self.clinic_display_options_py = clinic_options_py 

        # Chỉ cập nhật các ComboBox thực sự
        combobox_attributes_to_update = [
            'clinic_combo_for_registration',      
            'clinic_selection_combo_queue_tab' 
            # Bỏ 'clinic_filter_entry' nếu nó là CTkEntry
            # Nếu bạn có một ComboBox khác tên là 'clinic_filter_combo_for_history', hãy thêm nó vào đây
        ] 
        
        for attr_name in combobox_attributes_to_update: 
            if hasattr(self, attr_name):
                combobox_widget = getattr(self, attr_name) 
                # Quan trọng: Đảm bảo đây là CTkComboBox
                if isinstance(combobox_widget, ctk.CTkComboBox):
                    current_val = combobox_widget.get() 
                    # Lệnh configure này là nơi traceback chỉ ra vấn đề.
                    # Nếu vẫn lỗi, bạn có thể cần kiểm tra phiên bản CTk hoặc cách widget được tạo.
                    combobox_widget.configure(values=self.clinic_display_options_py) 
                    
                    if self.clinic_display_options_py[0] != "Chưa có phòng khám": 
                        if current_val in self.clinic_display_options_py : 
                            combobox_widget.set(current_val) 
                        else: 
                            combobox_widget.set(self.clinic_display_options_py[0])
                    else: 
                        combobox_widget.set(self.clinic_display_options_py[0])
                else:
                    print(f"Cảnh báo: Thuộc tính '{attr_name}' được mong đợi là CTkComboBox nhưng không phải.")

        if hasattr(self, 'clinic_selection_combo_queue_tab') and isinstance(self.clinic_selection_combo_queue_tab, ctk.CTkComboBox): 
            self._refresh_clinic_queue_display()

    # --- TAB ĐĂNG KÝ & HỒ SƠ BN ---
    def _setup_registration_profile_tab(self):
        main_content_frame = ctk.CTkFrame(self.registration_profile_tab, fg_color="transparent") 
        main_content_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        exam_registration_outer_frame = ctk.CTkFrame(main_content_frame) 
        exam_registration_outer_frame.pack(pady=(5, 10), padx=0, fill="x") 
        ctk.CTkLabel(exam_registration_outer_frame, text="ĐĂNG KÝ KHÁM CHO BỆNH NHÂN", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,5))
        actual_exam_reg_form_frame = ctk.CTkFrame(exam_registration_outer_frame) 
        actual_exam_reg_form_frame.pack(fill="x", padx=5, pady=0)

        ctk.CTkLabel(actual_exam_reg_form_frame, text="Mã BN (*):").grid(row=0, column=0, padx=5, pady=5, sticky="w") 
        self.patient_id_exam_reg_entry = ctk.CTkEntry(actual_exam_reg_form_frame, width=180, placeholder_text="Nhập Mã BN hoặc Tải") 
        self.patient_id_exam_reg_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(actual_exam_reg_form_frame, text="Phòng khám (*):").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.clinic_combo_for_registration = ctk.CTkComboBox(actual_exam_reg_form_frame, values=["Đang tải..."], width=200) 
        self.clinic_combo_for_registration.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(actual_exam_reg_form_frame, text="Mức độ ưu tiên (*):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.priority_dk_combo = ctk.CTkComboBox(actual_exam_reg_form_frame, values=self._convert_custom_list_to_py_list(self.priority_level_names), width=180) 
        self.priority_dk_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        if len(self.priority_level_names) > 0 : self.priority_dk_combo.set(self.priority_level_names.get(1 if len(self.priority_level_names) > 1 else 0) )

        ctk.CTkButton(actual_exam_reg_form_frame, text="Đăng ký Khám", command=self._register_patient_for_exam, height=30).grid(row=1, column=2, columnspan=2, padx=(15,5), pady=10, sticky="ew") 
        
        actual_exam_reg_form_frame.grid_columnconfigure(1, weight=1); actual_exam_reg_form_frame.grid_columnconfigure(3, weight=1) 
        ctk.CTkFrame(main_content_frame, height=2, fg_color="gray50").pack(fill="x", padx=10, pady=10)

        profile_management_outer_frame = ctk.CTkFrame(main_content_frame) 
        profile_management_outer_frame.pack(pady=5, padx=0, fill="x", expand=True) 
        ctk.CTkLabel(profile_management_outer_frame, text="QUẢN LÝ HỒ SƠ BỆNH NHÂN", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(5,5))
        actual_profile_form_frame = ctk.CTkFrame(profile_management_outer_frame) 
        actual_profile_form_frame.pack(pady=5, padx=5, fill="x")
        ctk.CTkLabel(actual_profile_form_frame, text="Mã BN (tải/sửa, trống nếu tạo mới):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.patient_id_profile_entry = ctk.CTkEntry(actual_profile_form_frame, width=230) 
        self.patient_id_profile_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(actual_profile_form_frame, text="Tải BN để sửa", command=self._load_patient_for_editing).grid(row=0, column=2, padx=5, pady=5)
        
        form_fields_list = [("Họ tên (*):", "full_name"), ("Ngày sinh (*):", "date_of_birth"), ("Giới tính (*):", "gender"), ("CCCD (*):", "national_id"), ("SĐT (*):", "phone_number"), ("Địa chỉ:", "address"), ("BHYT:", "health_insurance_id"), ("Tiền sử:", "medical_history_summary"), ("Dị ứng:", "drug_allergies")] 
        self.patient_profile_entries = {} 
        field_pady_val = 3 
        for i, (label_text_val, field_key) in enumerate(form_fields_list): 
            ctk.CTkLabel(actual_profile_form_frame, text=label_text_val).grid(row=i+1, column=0, padx=5, pady=field_pady_val, sticky="w")
            if field_key in ["address", "medical_history_summary", "drug_allergies"]: form_widget = ctk.CTkTextbox(actual_profile_form_frame, height=40, width=330, border_width=1) 
            else: form_widget = ctk.CTkEntry(actual_profile_form_frame, width=330, placeholder_text="YYYY-MM-DD" if field_key=="date_of_birth" else "") 
            form_widget.grid(row=i+1, column=1, columnspan=2, padx=5, pady=field_pady_val, sticky="ew"); self.patient_profile_entries[field_key] = form_widget
        actual_profile_form_frame.grid_columnconfigure(1, weight=1)
        
        profile_action_buttons_frame = ctk.CTkFrame(profile_management_outer_frame) 
        profile_action_buttons_frame.pack(pady=10, fill="x", padx=5)
        ctk.CTkButton(profile_action_buttons_frame, text="Tạo mới", command=self._create_new_patient_record, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x") 
        ctk.CTkButton(profile_action_buttons_frame, text="Cập nhật", command=self._update_patient_record, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x") 
        ctk.CTkButton(profile_action_buttons_frame, text="Xóa", command=self._delete_patient_record, fg_color="red", height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x") 
        ctk.CTkButton(profile_action_buttons_frame, text="Làm mới Form", command=self._clear_registration_form, height=30).pack(side="left", padx=5, pady=5, expand=True, fill="x") 

    def _clear_registration_form(self, clear_patient_id_field=True): 
        if clear_patient_id_field: self.patient_id_profile_entry.delete(0, "end")
        for form_widget in self.patient_profile_entries.values(): 
            if isinstance(form_widget, ctk.CTkEntry): form_widget.delete(0, "end")
            elif isinstance(form_widget, ctk.CTkTextbox): form_widget.delete("1.0", "end")

    def _load_patient_for_editing(self): 
        patient_id_val = self.patient_id_profile_entry.get().strip() 
        if not patient_id_val: self._show_gui_message("Vui lòng nhập Mã BN để tải thông tin.", "ERROR"); return
        patient_obj = self.medical_system_logic.find_patient_by_id(patient_id_val) 
        if patient_obj:
            self._clear_registration_form(clear_patient_id_field=False) 
            self.patient_profile_entries["full_name"].insert(0, patient_obj.full_name or "")
            self.patient_profile_entries["date_of_birth"].insert(0, patient_obj.date_of_birth.strftime(DATE_FORMAT_CSV) if patient_obj.date_of_birth else "")
            self.patient_profile_entries["gender"].insert(0, patient_obj.gender or "")
            self.patient_profile_entries["national_id"].insert(0, patient_obj.national_id or "")
            self.patient_profile_entries["phone_number"].insert(0, patient_obj.phone_number or "")
            self.patient_profile_entries["address"].delete("1.0", "end"); self.patient_profile_entries["address"].insert("1.0", patient_obj.address or "")
            self.patient_profile_entries["health_insurance_id"].insert(0, patient_obj.health_insurance_id or "") 
            self.patient_profile_entries["medical_history_summary"].delete("1.0", "end"); self.patient_profile_entries["medical_history_summary"].insert("1.0", patient_obj.medical_history_summary or "")
            self.patient_profile_entries["drug_allergies"].delete("1.0", "end"); self.patient_profile_entries["drug_allergies"].insert("1.0", patient_obj.drug_allergies or "")
            self.patient_id_exam_reg_entry.delete(0, "end"); self.patient_id_exam_reg_entry.insert(0, patient_id_val)
            self._show_gui_message(f"Đã tải thông tin BN: {patient_id_val} - {patient_obj.full_name} vào form.", "INFO")
        else:
            self._show_gui_message(f"Không tìm thấy bệnh nhân với mã: {patient_id_val}", "ERROR")
            self._clear_registration_form(clear_patient_id_field=False); self.patient_id_exam_reg_entry.delete(0, "end")

    def _create_new_patient_record(self): 
        form_data = {key_name: (widget.get("1.0", "end-1c").strip() if isinstance(widget, ctk.CTkTextbox) else widget.get().strip()) 
                     for key_name, widget in self.patient_profile_entries.items()} 
        dob_str_val = form_data.get("date_of_birth", "") 
        if dob_str_val:
            try: datetime.datetime.strptime(dob_str_val, DATE_FORMAT_CSV)
            except ValueError: self._show_gui_message(f"Định dạng Ngày sinh '{dob_str_val}' không hợp lệ (YYYY-MM-DD).", "ERROR"); return
        
        patient_object_created, message_text, message_lvl = self.medical_system_logic.create_patient_record( 
            full_name_val=form_data["full_name"], dob_str=form_data["date_of_birth"], gender_val=form_data["gender"],
            address_val=form_data["address"], phone_val=form_data["phone_number"], national_id_val=form_data["national_id"], 
            health_insurance_id_val=form_data["health_insurance_id"], medical_history_val=form_data["medical_history_summary"], drug_allergies_val=form_data["drug_allergies"]
        )
        self._show_gui_message(message_text, message_lvl)
        if patient_object_created: 
            self.patient_id_profile_entry.delete(0, "end"); self.patient_id_profile_entry.insert(0, patient_object_created.patient_id) 
            self.patient_id_exam_reg_entry.delete(0,"end"); self.patient_id_exam_reg_entry.insert(0, patient_object_created.patient_id) 
            self._refresh_all_application_lists()

    def _update_patient_record(self): 
        patient_id_val = self.patient_id_profile_entry.get().strip()
        if not patient_id_val: self._show_gui_message("Vui lòng tải Mã BN để cập nhật.", "ERROR"); return
        update_data_raw_dict = {key_name: (widget.get("1.0", "end-1c").strip() if isinstance(widget, ctk.CTkTextbox) else widget.get().strip()) 
                           for key_name, widget in self.patient_profile_entries.items()} 
        dob_str_update = update_data_raw_dict.get("date_of_birth", "") 
        if dob_str_update and dob_str_update.strip() != "": 
             try: datetime.datetime.strptime(dob_str_update, DATE_FORMAT_CSV)
             except ValueError: self._show_gui_message(f"Định dạng Ngày sinh '{dob_str_update}' không hợp lệ.", "ERROR"); return
        update_payload = { "full_name": update_data_raw_dict["full_name"], "date_of_birth": update_data_raw_dict["date_of_birth"], "gender": update_data_raw_dict["gender"], "address": update_data_raw_dict["address"], "phone_number": update_data_raw_dict["phone_number"], "national_id": update_data_raw_dict["national_id"], "health_insurance_id": update_data_raw_dict["health_insurance_id"], "medical_history_summary": update_data_raw_dict["medical_history_summary"], "drug_allergies": update_data_raw_dict["drug_allergies"]}
        success_flag, message_text, message_lvl = self.medical_system_logic.update_patient_info(patient_id_val, **update_payload) 
        self._show_gui_message(message_text, message_lvl)
        if success_flag and message_lvl == "INFO": self._refresh_all_application_lists()
        
    def _delete_patient_record(self): 
        patient_id_val = self.patient_id_profile_entry.get().strip()
        if not patient_id_val: self._show_gui_message("Vui lòng tải Mã BN để xóa.", "ERROR"); return
        if messagebox.askyesno("Xác nhận xóa", f"Bạn chắc chắn muốn xóa hồ sơ BN: {patient_id_val}? \nLưu ý: Nếu BN đang trong hàng đợi, bạn cần xóa khỏi hàng đợi trước."):
            success_flag, message_text, message_lvl = self.medical_system_logic.delete_patient_record(patient_id_val) 
            self._show_gui_message(message_text, message_lvl)
            if success_flag: self._clear_registration_form(clear_patient_id_field=True); self.patient_id_exam_reg_entry.delete(0, "end"); self._refresh_all_application_lists()

    def _register_patient_for_exam(self): 
        patient_id_exam_input = self.patient_id_exam_reg_entry.get().strip() 
        selected_clinic_full_str = self.clinic_combo_for_registration.get() 
        if not patient_id_exam_input or patient_id_exam_input == self.patient_id_exam_reg_entry.cget("placeholder_text"): 
            self._show_gui_message("Vui lòng nhập Mã BN để đăng ký khám.", "ERROR"); return
        if not selected_clinic_full_str or selected_clinic_full_str in ["Chưa có phòng khám", "Đang tải..."]:
             self._show_gui_message("Vui lòng chọn Phòng khám.", "ERROR"); return
        clinic_id_val = selected_clinic_full_str.split(" - ")[0] 
        priority_str_val = self.priority_dk_combo.get() 
        if not priority_str_val: self._show_gui_message("Vui lòng chọn mức độ ưu tiên.", "ERROR"); return
        success_flag, message_text, message_lvl = self.medical_system_logic.register_for_examination(patient_id_exam_input, clinic_id_val, priority_str_val) 
        self._show_gui_message(message_text, message_lvl)
        if success_flag: self._refresh_clinic_queue_display(); self.patient_id_exam_reg_entry.delete(0,"end") 

    # --- TAB HÀNG ĐỢI KHÁM ---
    def _setup_examination_queue_tab(self): 
        queue_tab_frame = self.examination_queue_tab 
        
        clinic_selection_frame = ctk.CTkFrame(queue_tab_frame, fg_color="transparent") 
        clinic_selection_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(clinic_selection_frame, text="Chọn Phòng khám để xem hàng đợi:").pack(side="left", padx=(0,5))
        self.clinic_selection_combo_queue_tab = ctk.CTkComboBox(clinic_selection_frame, values=["Đang tải..."], width=450, command=self._on_clinic_selection_changed_for_queue) 
        self.clinic_selection_combo_queue_tab.pack(side="left")

        self.currently_examining_label = ctk.CTkLabel(queue_tab_frame, text="Đang khám: Chưa có BN / Chưa chọn PK", font=("Arial", 16, "bold"), text_color="green") 
        self.currently_examining_label.pack(pady=10)
        
        queue_controls_frame = ctk.CTkFrame(queue_tab_frame); queue_controls_frame.pack(pady=10, padx=10) 
        ctk.CTkButton(queue_controls_frame, text="Gọi BN Tiếp theo", command=self._call_next_exam_patient).pack(side="left", padx=5, pady=5) 
        ctk.CTkButton(queue_controls_frame, text="Hoàn thành Khám", command=self._complete_current_examination).pack(side="left", padx=5, pady=5) 
        ctk.CTkButton(queue_controls_frame, text="BN Đang Gọi Vắng mặt", command=self._handle_current_patient_absent, fg_color="orange").pack(side="left", padx=5, pady=5) 
        ctk.CTkButton(queue_controls_frame, text="BN Rời đi (Trong HĐ)", command=self._handle_patient_leaving_selected_queue, fg_color="tomato").pack(side="left", padx=5, pady=5) 
        
        change_priority_outer_frame = ctk.CTkFrame(queue_tab_frame, fg_color="transparent"); change_priority_outer_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkLabel(change_priority_outer_frame, text="Thay đổi Ưu tiên BN trong Hàng đợi (của PK đang chọn):", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0,5))
        change_priority_form_frame = ctk.CTkFrame(change_priority_outer_frame); change_priority_form_frame.pack(fill="x")
        ctk.CTkLabel(change_priority_form_frame, text="Mã BN:").grid(row=0, column=0, padx=(5,0), pady=5, sticky="e")
        self.change_priority_patient_id_entry = ctk.CTkEntry(change_priority_form_frame, width=120); self.change_priority_patient_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(change_priority_form_frame, text="Ưu tiên mới:").grid(row=0, column=2, padx=(10,0), pady=5, sticky="e")
        self.change_priority_new_level_combo = ctk.CTkComboBox(change_priority_form_frame, values=self._convert_custom_list_to_py_list(self.priority_level_names), width=160); self.change_priority_new_level_combo.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        if len(self.priority_level_names)>0: self.change_priority_new_level_combo.set(self.priority_level_names.get(1 if len(self.priority_level_names) > 1 else 0) ) 
        ctk.CTkButton(change_priority_form_frame, text="Áp dụng thay đổi Ưu tiên", command=self._apply_priority_change_in_queue).grid(row=0, column=4, padx=10, pady=5) 

        ctk.CTkLabel(queue_tab_frame, text="Danh sách bệnh nhân đang chờ khám:", font=("Arial", 12)).pack(pady=(10,0))
        queue_tree_frame = ctk.CTkFrame(queue_tab_frame); queue_tree_frame.pack(expand=True, fill="both", padx=10, pady=5)
        queue_column_names = ("STT", "MaBN", "HoTen", "UuTien", "TGDangKy", "SoLanVang") 
        self.examination_queue_treeview = ttk.Treeview(queue_tree_frame, columns=queue_column_names, show="headings", height=8) 
        for column_name_val in queue_column_names: self.examination_queue_treeview.heading(column_name_val, text=column_name_val) 
        self.examination_queue_treeview.column("STT", width=40, anchor="center"); self.examination_queue_treeview.column("MaBN", width=80, anchor="center")
        self.examination_queue_treeview.column("HoTen", width=220); self.examination_queue_treeview.column("UuTien", width=150, anchor="center")
        self.examination_queue_treeview.column("TGDangKy", width=100, anchor="center"); self.examination_queue_treeview.column("SoLanVang", width=50, anchor="center")
        queue_scrollbar = ttk.Scrollbar(queue_tree_frame, orient="vertical", command=self.examination_queue_treeview.yview) 
        self.examination_queue_treeview.configure(yscrollcommand=queue_scrollbar.set); queue_scrollbar.pack(side="right", fill="y")
        self.examination_queue_treeview.pack(expand=True, fill="both")
        
    def _on_clinic_selection_changed_for_queue(self, selected_choice_val): 
        self._refresh_clinic_queue_display()
        self.currently_examining_label.configure(text="Đang khám: Chưa có BN / Hãy gọi BN từ PK này")
        self.current_exam_patient = None; self.current_exam_clinic_id = None

    def _get_selected_clinic_id_for_queue_tab(self): 
        selected_clinic_full_str = self.clinic_selection_combo_queue_tab.get() 
        if not selected_clinic_full_str or selected_clinic_full_str in ["Chưa có phòng khám", "Đang tải..."]: return None
        return selected_clinic_full_str.split(" - ")[0]

    def _refresh_clinic_queue_display(self): 
        for item_row in self.examination_queue_treeview.get_children(): self.examination_queue_treeview.delete(item_row) 
        selected_clinic_id = self._get_selected_clinic_id_for_queue_tab() 
        if not selected_clinic_id: self.examination_queue_treeview.insert("", "end", values=("", "---", "Vui lòng chọn phòng khám", "---", "", "")); return
        
        display_strings_custom_list = self.medical_system_logic.get_clinic_queue_display_list(selected_clinic_id) 
        
        if not display_strings_custom_list.is_empty() and display_strings_custom_list.get(0).startswith(f"Hàng đợi của PK {selected_clinic_id} rỗng"):
            self.examination_queue_treeview.insert("", "end", values=("", selected_clinic_id, display_strings_custom_list.get(0), "", "", ""))
        elif not display_strings_custom_list.is_empty():
            for i in range(len(display_strings_custom_list)):
                display_str_val = display_strings_custom_list.get(i) 
                try:
                    parts_list = display_str_val.split(','); stt_val = parts_list[0].split('.')[0].strip(); patient_id_val = parts_list[0].split('ID:')[1].strip() 
                    full_name_val = parts_list[1].split('Tên:')[1].strip(); priority_val = parts_list[2].split('Ưu tiên:')[1].strip() 
                    reg_time_val = parts_list[3].split('TGĐK:')[1].strip(); absent_count_val = parts_list[4].split('Vắng:')[1].strip() 
                    self.examination_queue_treeview.insert("", "end", values=(stt_val, patient_id_val, full_name_val, priority_val, reg_time_val, absent_count_val))
                except Exception as e: print(f"Lỗi parse HĐ: '{display_str_val}'. Lỗi: {e}"); self.examination_queue_treeview.insert("", "end", values=("Err", "Err", display_str_val, "Err", "Err", "Err"))
        else: self.examination_queue_treeview.insert("", "end", values=("", selected_clinic_id, "Không có dữ liệu", "", "", ""))

    def _call_next_exam_patient(self): 
        if self.current_exam_patient: self._show_gui_message(f"BN {self.current_exam_patient.patient_profile.full_name} đang khám.", "WARNING"); return
        selected_clinic_id = self._get_selected_clinic_id_for_queue_tab() 
        if not selected_clinic_id: self._show_gui_message("Chọn Phòng khám để gọi BN.", "ERROR"); return
            
        exam_patient_obj, message_text, message_lvl = self.medical_system_logic.call_next_patient_for_exam(selected_clinic_id) 
        
        if exam_patient_obj: 
            self.current_exam_patient = exam_patient_obj; self.current_exam_clinic_id = selected_clinic_id
            patient_profile_info = self.current_exam_patient.patient_profile 
            self.currently_examining_label.configure(text=f"Đang khám (PK: {selected_clinic_id}): {patient_profile_info.patient_id} - {patient_profile_info.full_name} ({self.current_exam_patient.get_priority_display_name()})")
            self._show_gui_message(message_text, message_lvl)
            self._refresh_clinic_queue_display()
        else: 
            self._show_gui_message(message_text, message_lvl)
            self.currently_examining_label.configure(text=f"Đang khám (PK: {selected_clinic_id}): Hàng đợi rỗng"); self.current_exam_patient = None; self.current_exam_clinic_id = None

    def _complete_current_examination(self): 
        if not self.current_exam_patient: 
            self._show_gui_message("Chưa có BN được gọi khám.", "ERROR")
            return
        
        current_patient_id = self.current_exam_patient.patient_id
        current_patient_name = self.current_exam_patient.patient_profile.full_name 
        
        # HỎI THÊM LOẠI KHÁM
        exam_type_val = simpledialog.askstring("Loại khám", f"Nhập Loại khám cho BN {current_patient_id} ({current_patient_name}):", parent=self)
        if exam_type_val is None: # Người dùng bấm Cancel
            return 
        if not exam_type_val.strip(): # Nếu để trống thì thông báo
             self._show_gui_message("Loại khám không được để trống.", "WARNING")
             return

        exam_result_val = simpledialog.askstring("Kết quả khám", f"Kết quả khám cho BN {current_patient_id} ({current_patient_name}):", parent=self) 
        if exam_result_val is None: 
            return 
        
        exam_notes_val = simpledialog.askstring("Ghi chú", f"Ghi chú cho BN {current_patient_id}:", parent=self)
        exam_notes_val = exam_notes_val or "" 
        
        attending_doctor_id_val = simpledialog.askstring("Thông tin khám", "Nhập Mã Bác sĩ khám (ví dụ BS001):", parent=self) 
        attending_doctor_id_val = attending_doctor_id_val.strip().upper() if attending_doctor_id_val else ""
        
        exam_clinic_id_val = self.current_exam_clinic_id 
        if not exam_clinic_id_val:
            exam_clinic_id_val_input = simpledialog.askstring("Thông tin khám", "Nhập Mã Phòng khám thực hiện (ví dụ PK001):", parent=self)
            exam_clinic_id_val = exam_clinic_id_val_input.strip().upper() if exam_clinic_id_val_input else ""
        
        # TRUYỀN THÊM exam_type_val
        success_flag, message_text, message_lvl = self.medical_system_logic.complete_examination(
            current_patient_id, exam_type_val, exam_result_val, exam_notes_val, 
            attending_doctor_id_val, exam_clinic_id_val
        ) 
        self._show_gui_message(message_text, message_lvl)
        
        if success_flag: 
            self.currently_examining_label.configure(text="Đang khám: Chưa có BN / Chưa chọn PK")
            self.current_exam_patient = None
            self.current_exam_clinic_id = None
            self._refresh_clinic_queue_display()
            self._refresh_full_examination_history_list()
            
    def _handle_current_patient_absent(self): 
        if not self.current_exam_patient or not self.current_exam_clinic_id:
            self._show_gui_message("Chưa có BN đang được gọi hoặc không rõ PK.", "ERROR"); return
        
        absent_patient_object = self.current_exam_patient; original_clinic_id_val = self.current_exam_clinic_id 
        
        if messagebox.askyesno("Xác nhận vắng mặt", f"Xác nhận BN ĐANG GỌI: {absent_patient_object.patient_profile.full_name} (ID: {absent_patient_object.patient_id}) từ PK {original_clinic_id_val} vắng mặt?"):
            was_removed_flag, message_text, message_lvl = self.medical_system_logic.handle_absent_called_patient(absent_patient_object, original_clinic_id_val) 
            self._show_gui_message(message_text, message_lvl)
            self.currently_examining_label.configure(text="Đang khám: Chưa có BN / Chưa chọn PK"); self.current_exam_patient = None; self.current_exam_clinic_id = None 
            self._refresh_clinic_queue_display() 

    def _handle_patient_leaving_selected_queue(self): 
        selected_clinic_id = self._get_selected_clinic_id_for_queue_tab() 
        if not selected_clinic_id: self._show_gui_message("Chọn PK có BN cần xóa khỏi HĐ.", "ERROR"); return
        
        focused_item_id = self.examination_queue_treeview.focus(); patient_id_to_remove_default = "" 
        if focused_item_id: 
            item_data_values = self.examination_queue_treeview.item(focused_item_id, "values") 
            patient_id_to_remove_default = item_data_values[1] if item_data_values and len(item_data_values) > 1 else ""
        
        patient_id_leaving_val = simpledialog.askstring("BN Rời Hàng Đợi", f"Nhập Mã BN rời đi từ HĐ của PK {selected_clinic_id}:", initialvalue=patient_id_to_remove_default, parent=self) 
        if patient_id_leaving_val and patient_id_leaving_val.strip():
            success_flag, message_text, message_lvl = self.medical_system_logic.handle_patient_leaving_queue(patient_id_leaving_val.strip(), selected_clinic_id) 
            self._show_gui_message(message_text, message_lvl); 
            if success_flag: self._refresh_clinic_queue_display()
        elif patient_id_leaving_val is not None: self._show_gui_message("Mã BN không được để trống.", "WARNING")

    def _apply_priority_change_in_queue(self): 
        selected_clinic_id = self._get_selected_clinic_id_for_queue_tab() 
        if not selected_clinic_id: self._show_gui_message("Chọn PK trước khi thay đổi ưu tiên.", "ERROR"); return

        patient_id_val = self.change_priority_patient_id_entry.get().strip() 
        new_priority_level_str = self.change_priority_new_level_combo.get() 
        if not patient_id_val: self._show_gui_message("Nhập Mã BN cần thay đổi ưu tiên.", "ERROR"); return
        if not new_priority_level_str: self._show_gui_message("Chọn Mức ưu tiên mới.", "ERROR"); return
        
        if messagebox.askyesno("Xác nhận", f"Thay đổi ưu tiên của BN {patient_id_val} tại PK {selected_clinic_id} thành '{new_priority_level_str}'?"):
            success_flag, message_text, message_lvl = self.medical_system_logic.change_patient_priority_in_queue(selected_clinic_id, patient_id_val, new_priority_level_str) 
            self._show_gui_message(message_text, message_lvl)
            if success_flag: self._refresh_clinic_queue_display(); self.change_priority_patient_id_entry.delete(0, "end") 
    
    def _setup_doctor_management_tab(self): 
        main_doctor_frame = ctk.CTkFrame(self.doctor_management_tab)
        main_doctor_frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(main_doctor_frame, text="QUẢN LÝ THÔNG TIN BÁC SĨ", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        doctor_form_frame = ctk.CTkFrame(main_doctor_frame)
        doctor_form_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(doctor_form_frame, text="Mã BS (để trống nếu tạo mới):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.doctor_id_entry = ctk.CTkEntry(doctor_form_frame, width=150)
        self.doctor_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(doctor_form_frame, text="Tải BS để sửa", command=self._load_doctor_for_editing).grid(row=0, column=2, padx=5, pady=5)
        
        ctk.CTkLabel(doctor_form_frame, text="Họ tên Bác sĩ (*):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.doctor_name_entry = ctk.CTkEntry(doctor_form_frame, width=300)
        self.doctor_name_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(doctor_form_frame, text="Chuyên khoa (*):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.doctor_specialty_entry = ctk.CTkEntry(doctor_form_frame, width=300)
        self.doctor_specialty_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        doctor_form_frame.grid_columnconfigure(1, weight=1)

        doctor_buttons_frame = ctk.CTkFrame(main_doctor_frame)
        doctor_buttons_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkButton(doctor_buttons_frame, text="Thêm Bác sĩ", command=self._add_new_doctor).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(doctor_buttons_frame, text="Sửa Bác sĩ", command=self._edit_doctor_info).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(doctor_buttons_frame, text="Xóa Bác sĩ", command=self._delete_selected_doctor, fg_color="red").pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(doctor_buttons_frame, text="Làm mới Form", command=self._clear_doctor_form_fields).pack(side="left", padx=5, expand=True, fill="x")

        ctk.CTkLabel(main_doctor_frame, text="Danh sách Bác sĩ:", font=ctk.CTkFont(size=12)).pack(pady=(10,0))
        doctor_treeview_frame = ctk.CTkFrame(main_doctor_frame)
        doctor_treeview_frame.pack(expand=True, fill="both", padx=10, pady=5)
        doctor_column_names = ("MaBS", "HoTenBS", "ChuyenKhoa", "MaPhongKham")
        self.doctor_list_treeview = ttk.Treeview(doctor_treeview_frame, columns=doctor_column_names, show="headings", height=10)
        for col_name in doctor_column_names: self.doctor_list_treeview.heading(col_name, text=col_name)
        self.doctor_list_treeview.column("MaBS", width=80, anchor="w"); self.doctor_list_treeview.column("HoTenBS", width=200, anchor="w")
        self.doctor_list_treeview.column("ChuyenKhoa", width=150, anchor="w"); self.doctor_list_treeview.column("MaPhongKham", width=300, anchor="w")
        
        doctor_list_scrollbar = ttk.Scrollbar(doctor_treeview_frame, orient="vertical", command=self.doctor_list_treeview.yview)
        self.doctor_list_treeview.configure(yscrollcommand=doctor_list_scrollbar.set)
        doctor_list_scrollbar.pack(side="right", fill="y")
        self.doctor_list_treeview.pack(expand=True, fill="both")
        self.doctor_list_treeview.bind("<<TreeviewSelect>>", self._on_doctor_selected_from_tree)
    
    def _clear_doctor_form_fields(self):
        self.doctor_id_entry.delete(0, "end")
        self.doctor_name_entry.delete(0, "end")
        self.doctor_specialty_entry.delete(0, "end")

    def _refresh_doctor_list_display(self): 
        for item_row in self.doctor_list_treeview.get_children(): self.doctor_list_treeview.delete(item_row)
        doctors_custom_list = self.medical_system_logic.list_all_doctors()
        if doctors_custom_list:
            for i in range(len(doctors_custom_list)):
                doctor_obj = doctors_custom_list.get(i)
                clinic_ids_py_list = self._convert_custom_list_to_py_list(doctor_obj.clinic_id_list)
                clinic_ids_display_str = ", ".join(clinic_ids_py_list) if clinic_ids_py_list else "Chưa có"
                self.doctor_list_treeview.insert("", "end", values=(doctor_obj.doctor_id, doctor_obj.doctor_name, doctor_obj.specialty, clinic_ids_display_str))
    
    def _on_doctor_selected_from_tree(self, event_data=None): 
        try:
            selected_tree_item = self.doctor_list_treeview.selection()[0] 
            item_data_values = self.doctor_list_treeview.item(selected_tree_item, "values") 
            if item_data_values:
                self.doctor_id_entry.delete(0, "end"); self.doctor_id_entry.insert(0, item_data_values[0])
                self.doctor_name_entry.delete(0, "end"); self.doctor_name_entry.insert(0, item_data_values[1])
                self.doctor_specialty_entry.delete(0, "end"); self.doctor_specialty_entry.insert(0, item_data_values[2])
        except IndexError: pass 

    def _load_doctor_for_editing(self): 
        doctor_id_val = self.doctor_id_entry.get().strip() 
        if not doctor_id_val: self._show_gui_message("Nhập Mã Bác sĩ để tải thông tin.", "ERROR"); return
        doctor_obj = self.medical_system_logic.find_doctor_by_id(doctor_id_val) 
        if doctor_obj:
            self.doctor_name_entry.delete(0, "end"); self.doctor_name_entry.insert(0, doctor_obj.doctor_name)
            self.doctor_specialty_entry.delete(0, "end"); self.doctor_specialty_entry.insert(0, doctor_obj.specialty)
            self._show_gui_message(f"Đã tải thông tin Bác sĩ {doctor_id_val}.", "INFO")
        else: self._show_gui_message(f"Không tìm thấy Bác sĩ với mã: {doctor_id_val}.", "ERROR")

    def _add_new_doctor(self): 
        doctor_full_name = self.doctor_name_entry.get().strip() 
        doctor_specialty_val = self.doctor_specialty_entry.get().strip() 
        doctor_obj, message_text, message_lvl = self.medical_system_logic.create_doctor(doctor_full_name, doctor_specialty_val) 
        self._show_gui_message(message_text, message_lvl)
        if doctor_obj: self._refresh_doctor_list_display(); self._clear_doctor_form_fields(); self._refresh_all_application_lists()

    def _edit_doctor_info(self): 
        doctor_id_val = self.doctor_id_entry.get().strip() 
        new_doctor_name = self.doctor_name_entry.get().strip() 
        new_doctor_specialty = self.doctor_specialty_entry.get().strip() 
        if not doctor_id_val: self._show_gui_message("Vui lòng nhập hoặc tải Mã Bác sĩ cần sửa.", "ERROR"); return
        
        update_payload = {} 
        if new_doctor_name: update_payload["new_name"] = new_doctor_name 
        if new_doctor_specialty: update_payload["new_specialty"] = new_doctor_specialty
        if not update_payload: self._show_gui_message("Không có thông tin mới để cập nhật cho bác sĩ.", "INFO"); return

        success_flag, message_text, message_lvl = self.medical_system_logic.update_doctor_info(doctor_id_val, **update_payload) 
        self._show_gui_message(message_text, message_lvl)
        if success_flag and message_lvl == "INFO": self._refresh_doctor_list_display(); self._refresh_all_application_lists()

    def _delete_selected_doctor(self): 
        doctor_id_val = self.doctor_id_entry.get().strip() 
        if not doctor_id_val: self._show_gui_message("Vui lòng nhập hoặc tải Mã Bác sĩ cần xóa.", "ERROR"); return
        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa Bác sĩ {doctor_id_val}? \nThao tác này cũng sẽ xóa bác sĩ này khỏi danh sách các phòng khám liên quan."):
            success_flag, message_text, message_lvl = self.medical_system_logic.delete_doctor(doctor_id_val) 
            self._show_gui_message(message_text, message_lvl)
            if success_flag: self._refresh_doctor_list_display(); self._refresh_clinic_list_display(); self._clear_doctor_form_fields(); self._refresh_all_application_lists()

    # --- TAB QUẢN LÝ PHÒNG KHÁM ---
    def _setup_clinic_management_tab(self): 
        main_clinic_frame = ctk.CTkFrame(self.clinic_management_tab) 
        main_clinic_frame.pack(expand=True, fill="both", padx=10, pady=10)
        ctk.CTkLabel(main_clinic_frame, text="QUẢN LÝ THÔNG TIN PHÒNG KHÁM", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        clinic_form_frame = ctk.CTkFrame(main_clinic_frame) 
        clinic_form_frame.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(clinic_form_frame, text="Mã PK (trống nếu tạo mới):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.clinic_id_entry = ctk.CTkEntry(clinic_form_frame, width=150) 
        self.clinic_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkButton(clinic_form_frame, text="Tải PK để sửa", command=self._load_clinic_for_editing).grid(row=0, column=2, padx=5, pady=5) 

        ctk.CTkLabel(clinic_form_frame, text="Tên Phòng khám (*):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.clinic_name_entry = ctk.CTkEntry(clinic_form_frame, width=300) 
        self.clinic_name_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(clinic_form_frame, text="Chuyên khoa PK (*):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.clinic_specialty_entry = ctk.CTkEntry(clinic_form_frame, width=300) 
        self.clinic_specialty_entry.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky="ew")
        clinic_form_frame.grid_columnconfigure(1, weight=1)

        clinic_buttons_frame = ctk.CTkFrame(main_clinic_frame) 
        clinic_buttons_frame.pack(pady=10, fill="x", padx=10)
        ctk.CTkButton(clinic_buttons_frame, text="Thêm PK", command=self._add_new_clinic).pack(side="left", padx=5, expand=True, fill="x") 
        ctk.CTkButton(clinic_buttons_frame, text="Sửa PK", command=self._edit_clinic_info).pack(side="left", padx=5, expand=True, fill="x") 
        ctk.CTkButton(clinic_buttons_frame, text="Xóa PK", command=self._delete_selected_clinic, fg_color="red").pack(side="left", padx=5, expand=True, fill="x") 
        ctk.CTkButton(clinic_buttons_frame, text="Làm mới Form", command=self._clear_clinic_form_fields).pack(side="left", padx=5, expand=True, fill="x") 
        ctk.CTkButton(clinic_buttons_frame, text="Gán/Xóa BS cho PK", command=self._manage_doctors_for_clinic).pack(side="left", padx=5, expand=True, fill="x") 

        ctk.CTkLabel(main_clinic_frame, text="Danh sách Phòng khám:", font=ctk.CTkFont(size=12)).pack(pady=(10,0))
        clinic_treeview_frame = ctk.CTkFrame(main_clinic_frame) 
        clinic_treeview_frame.pack(expand=True, fill="both", padx=10, pady=5)
        clinic_column_names = ("MaPK", "TenPK", "ChuyenKhoaPK", "MaBacSiTrongPK") 
        self.clinic_list_treeview = ttk.Treeview(clinic_treeview_frame, columns=clinic_column_names, show="headings", height=10) 
        for col_name_val in clinic_column_names: self.clinic_list_treeview.heading(col_name_val, text=col_name_val) 
        self.clinic_list_treeview.column("MaPK", width=80, anchor="w"); self.clinic_list_treeview.column("TenPK", width=200, anchor="w")
        self.clinic_list_treeview.column("ChuyenKhoaPK", width=150, anchor="w"); self.clinic_list_treeview.column("MaBacSiTrongPK", width=300, anchor="w") # Tăng width
        clinic_list_scrollbar = ttk.Scrollbar(clinic_treeview_frame, orient="vertical", command=self.clinic_list_treeview.yview) 
        self.clinic_list_treeview.configure(yscrollcommand=clinic_list_scrollbar.set); clinic_list_scrollbar.pack(side="right", fill="y"); self.clinic_list_treeview.pack(expand=True, fill="both")
        self.clinic_list_treeview.bind("<<TreeviewSelect>>", self._on_clinic_selected_from_tree) 

    def _clear_clinic_form_fields(self): 
        self.clinic_id_entry.delete(0, "end"); self.clinic_name_entry.delete(0, "end"); self.clinic_specialty_entry.delete(0, "end")

    def _refresh_clinic_list_display(self): 
        for item_row in self.clinic_list_treeview.get_children(): self.clinic_list_treeview.delete(item_row) 
        clinics_custom_list = self.medical_system_logic.list_all_clinics() 
        if clinics_custom_list:
            for i in range(len(clinics_custom_list)):
                clinic_obj = clinics_custom_list.get(i) 
                doctor_ids_py_list = self._convert_custom_list_to_py_list(clinic_obj.doctor_id_list) 
                doctor_ids_display_str = ", ".join(doctor_ids_py_list) if doctor_ids_py_list else "Chưa có" 
                self.clinic_list_treeview.insert("", "end", values=(clinic_obj.clinic_id, clinic_obj.clinic_name, clinic_obj.clinic_specialty, doctor_ids_display_str))
    
    def _on_clinic_selected_from_tree(self, event_data=None): 
        try:
            selected_tree_item = self.clinic_list_treeview.selection()[0] 
            item_data_values = self.clinic_list_treeview.item(selected_tree_item, "values") 
            if item_data_values:
                self.clinic_id_entry.delete(0, "end"); self.clinic_id_entry.insert(0, item_data_values[0])
                self.clinic_name_entry.delete(0, "end"); self.clinic_name_entry.insert(0, item_data_values[1])
                self.clinic_specialty_entry.delete(0, "end"); self.clinic_specialty_entry.insert(0, item_data_values[2])
        except IndexError: pass

    def _load_clinic_for_editing(self): 
        clinic_id_val = self.clinic_id_entry.get().strip() 
        if not clinic_id_val: self._show_gui_message("Nhập Mã Phòng khám để tải.", "ERROR"); return
        clinic_obj = self.medical_system_logic.find_clinic_by_id(clinic_id_val) 
        if clinic_obj:
            self.clinic_name_entry.delete(0, "end"); self.clinic_name_entry.insert(0, clinic_obj.clinic_name)
            self.clinic_specialty_entry.delete(0, "end"); self.clinic_specialty_entry.insert(0, clinic_obj.clinic_specialty)
            self._show_gui_message(f"Đã tải thông tin PK {clinic_id_val}.", "INFO")
        else: self._show_gui_message(f"Không tìm thấy PK {clinic_id_val}.", "ERROR")

    def _add_new_clinic(self): 
        clinic_name_val = self.clinic_name_entry.get().strip() 
        clinic_specialty_val = self.clinic_specialty_entry.get().strip() 
        clinic_obj, message_text, message_lvl = self.medical_system_logic.create_clinic(clinic_name_val, clinic_specialty_val) 
        self._show_gui_message(message_text, message_lvl)
        if clinic_obj: self._refresh_clinic_list_display(); self._clear_clinic_form_fields(); self._refresh_all_application_lists()

    def _edit_clinic_info(self): 
        clinic_id_val = self.clinic_id_entry.get().strip() 
        new_clinic_name = self.clinic_name_entry.get().strip() 
        new_clinic_specialty = self.clinic_specialty_entry.get().strip() 
        if not clinic_id_val: self._show_gui_message("Vui lòng nhập hoặc tải Mã Phòng khám để sửa.", "ERROR"); return
        
        update_payload = {}; 
        if new_clinic_name: update_payload["new_name"] = new_clinic_name
        if new_clinic_specialty: update_payload["new_specialty"] = new_clinic_specialty
        if not update_payload: self._show_gui_message("Không có thông tin mới để cập nhật cho phòng khám.", "INFO"); return

        success_flag, message_text, message_lvl = self.medical_system_logic.update_clinic_info(clinic_id_val, **update_payload) 
        self._show_gui_message(message_text, message_lvl)
        if success_flag and message_lvl == "INFO": self._refresh_clinic_list_display(); self._refresh_all_application_lists()

    def _delete_selected_clinic(self): 
        clinic_id_val = self.clinic_id_entry.get().strip() 
        if not clinic_id_val: self._show_gui_message("Vui lòng nhập hoặc tải Mã Phòng khám để xóa.", "ERROR"); return
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Phòng khám {clinic_id_val}? \nThao tác này cũng sẽ xóa phòng khám này khỏi danh sách làm việc của các bác sĩ liên quan và hàng đợi (nếu rỗng)."):
            success_flag, message_text, message_lvl = self.medical_system_logic.delete_clinic(clinic_id_val) 
            self._show_gui_message(message_text, message_lvl)
            if success_flag: self._refresh_clinic_list_display(); self._refresh_doctor_list_display(); self._clear_clinic_form_fields(); self._refresh_all_application_lists()
            
    def _manage_doctors_for_clinic(self): 
        clinic_id_val = self.clinic_id_entry.get().strip() 
        if not clinic_id_val: self._show_gui_message("Vui lòng tải hoặc nhập Mã Phòng khám trước.", "WARNING"); return
        clinic_obj = self.medical_system_logic.find_clinic_by_id(clinic_id_val) 
        if not clinic_obj: self._show_gui_message(f"Không tìm thấy phòng khám {clinic_id_val}.", "ERROR"); return

        current_doctors_py_list = self._convert_custom_list_to_py_list(clinic_obj.doctor_id_list) 
        action_input_str = simpledialog.askstring("Quản lý Bác sĩ cho Phòng khám", 
                                        f"Phòng khám: {clinic_obj.clinic_name} ({clinic_id_val})\n"
                                        f"DS Bác sĩ hiện tại: {', '.join(current_doctors_py_list) if current_doctors_py_list else 'Chưa có'}\n\n"
                                        "Nhập 'them <Mã BS>' hoặc 'xoa <Mã BS>':", parent=self)
        if action_input_str:
            action_parts = action_input_str.strip().lower().split(); 
            command_str, doctor_id_val_action = (action_parts[0], action_parts[1].upper()) if len(action_parts) == 2 else (None, None) 
            
            success_flag = False # Khởi tạo
            if command_str == "them" and doctor_id_val_action: 
                success_flag, message_text, message_lvl = self.medical_system_logic.assign_doctor_to_clinic(doctor_id_val_action, clinic_id_val) 
            elif command_str == "xoa" and doctor_id_val_action: 
                success_flag, message_text, message_lvl = self.medical_system_logic.remove_doctor_from_clinic(doctor_id_val_action, clinic_id_val) 
            else: 
                self._show_gui_message("Lệnh không hợp lệ. Dùng 'them <Mã BS>' hoặc 'xoa <Mã BS>'.", "ERROR"); return
            
            self._show_gui_message(message_text, message_lvl)
            if success_flag and message_lvl == "INFO": self._refresh_clinic_list_display(); self._refresh_doctor_list_display()


    # --- TAB TÌM KIẾM BỆNH NHÂN --- (Giữ nguyên từ phiên bản trước, chỉ đổi tên biến/hàm)
    def _setup_patient_search_tab(self): 
        search_tab_main_frame = self.patient_search_tab
        search_form_outer_container = ctk.CTkFrame(search_tab_main_frame); search_form_outer_container.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(search_form_outer_container, text="Tìm kiếm Hồ sơ Bệnh nhân", font=ctk.CTkFont(size=14, weight="bold")).pack()
        actual_search_form_frame = ctk.CTkFrame(search_form_outer_container); actual_search_form_frame.pack(pady=10, fill="x")
        ctk.CTkLabel(actual_search_form_frame, text="Mã BN:").grid(row=0, column=0, padx=(10,5), pady=5, sticky="w")
        self.search_patient_id_entry = ctk.CTkEntry(actual_search_form_frame, width=150); self.search_patient_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(actual_search_form_frame, text="Họ tên (chứa):").grid(row=0, column=2, padx=(10,5), pady=5, sticky="w")
        self.search_full_name_entry = ctk.CTkEntry(actual_search_form_frame, width=200); self.search_full_name_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(actual_search_form_frame, text="SĐT (chứa):").grid(row=1, column=0, padx=(10,5), pady=5, sticky="w")
        self.search_phone_entry = ctk.CTkEntry(actual_search_form_frame, width=150); self.search_phone_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(actual_search_form_frame, text="Ngày sinh (YYYY-MM-DD):").grid(row=1, column=2, padx=(10,5), pady=5, sticky="w")
        self.search_dob_entry = ctk.CTkEntry(actual_search_form_frame, width=200, placeholder_text="YYYY-MM-DD"); self.search_dob_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(actual_search_form_frame, text="CCCD (chứa):").grid(row=2, column=0, padx=(10,5), pady=5, sticky="w")
        self.search_national_id_entry = ctk.CTkEntry(actual_search_form_frame, width=150); self.search_national_id_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        ctk.CTkLabel(actual_search_form_frame, text="BHYT (chứa):").grid(row=2, column=2, padx=(10,5), pady=5, sticky="w")
        self.search_health_insurance_entry = ctk.CTkEntry(actual_search_form_frame, width=200); self.search_health_insurance_entry.grid(row=2, column=3, padx=5, pady=5, sticky="ew")
        actual_search_form_frame.grid_columnconfigure(1, weight=1); actual_search_form_frame.grid_columnconfigure(3, weight=1)
        search_buttons_container = ctk.CTkFrame(search_form_outer_container); search_buttons_container.pack(pady=(10,5))
        ctk.CTkButton(search_buttons_container, text="Tìm kiếm BN", command=self._search_patients_action).pack(side="left", padx=10)
        ctk.CTkButton(search_buttons_container, text="Hiển thị Tất cả BN", command=self._display_all_patients_in_search_tab).pack(side="left", padx=10)
        ctk.CTkButton(search_buttons_container, text="Làm mới Tìm kiếm", command=self._clear_patient_search_form_fields).pack(side="left", padx=10)
        self.patient_search_results_textbox = ctk.CTkTextbox(search_tab_main_frame, height=400, width=780, font=("Arial", 13)); 
        self.patient_search_results_textbox.pack(pady=10, padx=10, expand=True, fill="both")
        self._clear_patient_search_form_fields() 

    def _clear_patient_search_form_fields(self): 
        self.search_patient_id_entry.delete(0, "end"); self.search_full_name_entry.delete(0, "end")
        self.search_phone_entry.delete(0, "end"); self.search_dob_entry.delete(0, "end")
        self.search_national_id_entry.delete(0, "end"); self.search_health_insurance_entry.delete(0, "end")
        self.patient_search_results_textbox.configure(state="normal"); self.patient_search_results_textbox.delete("1.0", "end")
        self.patient_search_results_textbox.insert("end", "Nhập tiêu chí và tìm kiếm, hoặc hiển thị tất cả bệnh nhân."); self.patient_search_results_textbox.configure(state="disabled")

    def _search_patients_action(self): 
        patient_id_query = self.search_patient_id_entry.get().strip(); full_name_query = self.search_full_name_entry.get().strip() 
        phone_query = self.search_phone_entry.get().strip(); dob_query = self.search_dob_entry.get().strip() 
        national_id_query = self.search_national_id_entry.get().strip(); health_insurance_query = self.search_health_insurance_entry.get().strip() 
        search_results_custom_list = List(); result_title = "Kết quả tìm kiếm:" 
        if patient_id_query: 
            patient_obj = self.medical_system_logic.find_patient_by_id(patient_id_query) 
            if patient_obj: search_results_custom_list.append(patient_obj)
            else: result_title = f"Không tìm thấy BN với mã {patient_id_query}."
        elif full_name_query or phone_query or dob_query or national_id_query or health_insurance_query : 
            search_criteria_dict = {"full_name": full_name_query, "phone_number": phone_query, "date_of_birth": dob_query, "national_id": national_id_query, "health_insurance_id": health_insurance_query} 
            search_results_custom_list = self.medical_system_logic.advanced_patient_search(**search_criteria_dict) 
            if search_results_custom_list.is_empty(): result_title = "Không tìm thấy BN nào khớp tiêu chí."
        else: self._show_gui_message("Nhập ít nhất một tiêu chí tìm kiếm.", "INFO"); self._display_patient_search_results(List(), search_title="Vui lòng nhập tiêu chí."); return
        self._display_patient_search_results(search_results_custom_list, search_title=result_title if search_results_custom_list.is_empty() and patient_id_query else f"Kết quả tìm kiếm ({len(search_results_custom_list)}):")

    def _display_all_patients_in_search_tab(self): 
        all_patients_results = self.medical_system_logic.list_all_patients() 
        self._display_patient_search_results(all_patients_results, search_title=f"Danh sách tất cả bệnh nhân ({len(all_patients_results)}):")

    def _display_patient_search_results(self, patient_custom_list_results, search_title="Kết quả tìm kiếm:"): 
        self.patient_search_results_textbox.configure(state="normal"); self.patient_search_results_textbox.delete("1.0", "end") 
        if not patient_custom_list_results.is_empty():
            self.patient_search_results_textbox.insert("end", f"{search_title}\n\n")
            for i in range(len(patient_custom_list_results)):
                patient_obj = patient_custom_list_results.get(i) 
                self.patient_search_results_textbox.insert("end", f"--- Bệnh nhân {i+1} ---\n" + patient_obj.display_detailed_info() + "\n\n" + "="*70 + "\n\n")
        else: self.patient_search_results_textbox.insert("end", f"{search_title}\nKhông tìm thấy bệnh nhân nào khớp.")
        self.patient_search_results_textbox.configure(state="disabled")

    # --- TAB LỊCH SỬ KHÁM ---
    def _setup_examination_history_tab(self): 
        history_tab_main_frame = self.examination_history_tab 
        ctk.CTkLabel(history_tab_main_frame, text="TRA CỨU LỊCH SỬ KHÁM BỆNH TOÀN HỆ THỐNG", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        filter_controls_frame = ctk.CTkFrame(history_tab_main_frame); filter_controls_frame.pack(pady=10, padx=10, fill="x") 
        ctk.CTkLabel(filter_controls_frame, text="Từ ngày:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.from_date_filter_entry = ctk.CTkEntry(filter_controls_frame, placeholder_text="YYYY-MM-DD", width=150); self.from_date_filter_entry.grid(row=0, column=1, padx=5, pady=5) 
        ctk.CTkLabel(filter_controls_frame, text="Đến ngày:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.to_date_filter_entry = ctk.CTkEntry(filter_controls_frame, placeholder_text="YYYY-MM-DD", width=150); self.to_date_filter_entry.grid(row=0, column=3, padx=5, pady=5) 
        ctk.CTkLabel(filter_controls_frame, text="Mã BS (chứa):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.doctor_id_filter_entry = ctk.CTkEntry(filter_controls_frame, placeholder_text="Ví dụ: BS001", width=150); self.doctor_id_filter_entry.grid(row=1, column=1, padx=5, pady=5) 
        ctk.CTkLabel(filter_controls_frame, text="Mã PK (chứa):").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.clinic_filter_entry = ctk.CTkEntry(filter_controls_frame, placeholder_text="Ví dụ: PK001", width=150); self.clinic_filter_entry.grid(row=1, column=3, padx=5, pady=5) 
        filter_action_buttons_frame = ctk.CTkFrame(filter_controls_frame); filter_action_buttons_frame.grid(row=0, column=4, rowspan=2, padx=20, pady=5, sticky="ns") 
        ctk.CTkButton(filter_action_buttons_frame, text="Lọc Lịch sử", command=self._refresh_full_examination_history_list).pack(pady=5) 
        ctk.CTkButton(filter_action_buttons_frame, text="Xóa bộ lọc", command=self._clear_examination_history_filters).pack(pady=5) 
        history_treeview_frame = ctk.CTkFrame(history_tab_main_frame); history_treeview_frame.pack(expand=True, fill="both", padx=10, pady=5) 
        
        # THÊM "LoaiKham" VÀO DANH SÁCH CỘT
        history_column_names = ("STT", "MaBN", "TenBN", "NgayKham", "LoaiKham", "KetQua", "GhiChu", "MaBS", "MaPK") 
        self.full_examination_history_treeview = ttk.Treeview(history_treeview_frame, columns=history_column_names, show="headings", height=18) 
        for col_header_name in history_column_names: 
            # CẬP NHẬT TIÊU ĐỀ CỘT
            display_name = col_header_name
            if col_header_name == "MaBN": display_name = "Mã BN"
            elif col_header_name == "TenBN": display_name = "Tên BN"
            elif col_header_name == "NgayKham": display_name = "Ngày Khám"
            elif col_header_name == "LoaiKham": display_name = "Loại Khám" # MỚI
            elif col_header_name == "KetQua": display_name = "Kết Quả"
            elif col_header_name == "GhiChu": display_name = "Ghi Chú"
            elif col_header_name == "MaBS": display_name = "Mã BS"
            elif col_header_name == "MaPK": display_name = "Mã PK"
            self.full_examination_history_treeview.heading(col_header_name, text=display_name) 
            
        self.full_examination_history_treeview.column("STT", width=40, anchor="center"); self.full_examination_history_treeview.column("MaBN", width=80, anchor="w")
        self.full_examination_history_treeview.column("TenBN", width=150, anchor="w"); self.full_examination_history_treeview.column("NgayKham", width=100, anchor="center")
        self.full_examination_history_treeview.column("LoaiKham", width=120, anchor="w") # MỚI
        self.full_examination_history_treeview.column("KetQua", width=180, anchor="w"); self.full_examination_history_treeview.column("GhiChu", width=180, anchor="w")
        self.full_examination_history_treeview.column("MaBS", width=70, anchor="w"); self.full_examination_history_treeview.column("MaPK", width=70, anchor="w")
        
        history_list_scrollbar = ttk.Scrollbar(history_treeview_frame, orient="vertical", command=self.full_examination_history_treeview.yview) 
        self.full_examination_history_treeview.configure(yscrollcommand=history_list_scrollbar.set); history_list_scrollbar.pack(side="right", fill="y")
        self.full_examination_history_treeview.pack(expand=True, fill="both")
        
    def _clear_examination_history_filters(self): 
        self.from_date_filter_entry.delete(0, "end"); self.to_date_filter_entry.delete(0, "end")
        self.doctor_id_filter_entry.delete(0, "end"); self.clinic_filter_entry.delete(0, "end")
        self._refresh_full_examination_history_list()

    def _refresh_full_examination_history_list(self): 
        for item_row in self.full_examination_history_treeview.get_children(): self.full_examination_history_treeview.delete(item_row) 
        from_date_str_val = self.from_date_filter_entry.get().strip() 
        to_date_str_val = self.to_date_filter_entry.get().strip() 
        doctor_id_val = self.doctor_id_filter_entry.get().strip().upper() 
        clinic_id_val = self.clinic_filter_entry.get().strip().upper() 
        
        history_custom_list, message_text, message_lvl = self.medical_system_logic.filter_examination_history( 
            from_date_str=from_date_str_val if from_date_str_val else None, 
            to_date_str=to_date_str_val if to_date_str_val else None,
            doctor_id_filter=doctor_id_val if doctor_id_val else None, 
            clinic_id_filter=clinic_id_val if clinic_id_val else None
        )
        
        if message_lvl == "ERROR": 
            self._show_gui_message(message_text, message_lvl)
            self.full_examination_history_treeview.insert("", "end", values=("", "", message_text, "", "", "", "", "", "")) # Cập nhật số lượng cột trống
            return
            
        if history_custom_list.is_empty():
             self._show_gui_message(message_text if message_text else "Không có lịch sử khám nào.", "INFO")
             self.full_examination_history_treeview.insert("", "end", values=("", "", message_text if message_text else "Không có lịch sử khám.", "", "", "", "", "", "")) # Cập nhật
        else:
            for i in range(len(history_custom_list)):
                history_record = history_custom_list.get(i) 
                exam_date_display = history_record.get('ngay_kham') 
                if isinstance(exam_date_display, datetime.date): 
                    exam_date_display = exam_date_display.strftime(DATE_FORMAT_CSV)
                
                # CẬP NHẬT THỨ TỰ VÀ THÊM TRƯỜNG MỚI
                self.full_examination_history_treeview.insert("", "end", values=(
                    i + 1, 
                    history_record.get('ma_bn', 'N/A'), 
                    history_record.get('ho_ten_bn', 'N/A'),
                    exam_date_display or 'N/A', 
                    history_record.get('loai_kham', 'N/A'), # MỚI
                    history_record.get('ket_qua', 'N/A'), 
                    history_record.get('ghi_chu', 'N/A'),
                    history_record.get('ma_bac_si_kham', 'N/A'), 
                    history_record.get('ma_phong_kham_kham', 'N/A')
                ))
            if message_text and message_lvl == "INFO" and len(history_custom_list) > 0 : 
                self._show_gui_message(message_text, message_lvl)
                
    def _refresh_all_application_lists(self): 
        self._display_all_patients_in_search_tab() 
        self._refresh_full_examination_history_list() 
        self._refresh_doctor_list_display() 
        self._refresh_clinic_list_display()
        self._populate_clinic_comboboxes() 

if __name__ == "__main__":
    medical_system_instance = MedicalSystemLogic() 
    app_gui_instance = MedicalAppGUI(medical_system_instance) 
    app_gui_instance.mainloop()
