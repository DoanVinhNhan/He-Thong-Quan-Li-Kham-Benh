# app_logic.py
import datetime
import csv
import os
import sys

from models import Patient, PatientInQueue, DATE_FORMAT_CSV, Doctor, Clinic
from custom_structures import CustomPriorityQueue, LinkedList, HashTable, List, RadixTree

def resource_path(relative_path):
    try: base_path = sys._MEIPASS 
    except Exception: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Tên file CSV dữ liệu
PATIENTS_CSV_FILENAME = "patients_data.csv"
DOCTORS_CSV_FILENAME = "doctors_data.csv"
CLINICS_CSV_FILENAME = "clinics_data.csv"

class MedicalSystemLogic:
    """Logic nghiệp vụ chính của hệ thống."""
    def __init__(self, hash_table_default_size=100):
        # Bảng băm lưu hồ sơ BN, key: patient_id
        self.patient_records_table = HashTable(initial_table_size=hash_table_default_size)
        self.next_patient_id_counter = 1 # Tạo mã BN tự động

        # Radix Tree tìm BN theo SĐT và CCCD
        self.phone_radix_tree = RadixTree()
        self.national_id_radix_tree = RadixTree()

        patients_data_path = resource_path(PATIENTS_CSV_FILENAME)
        doctors_data_path = resource_path(DOCTORS_CSV_FILENAME)
        clinics_data_path = resource_path(CLINICS_CSV_FILENAME)

        # Tải dữ liệu từ CSV
        self._load_data_from_csv(patients_data_path, Patient, self.patient_records_table, self._update_next_patient_id_counter, key_attribute_name='patient_id', id_prefix='BN')
        
        # Bảng băm lưu hàng đợi khám của PK, key: clinic_id, value: CustomPriorityQueue
        self.clinic_examination_queues = HashTable(initial_table_size=20)
        self.examined_patients_today_list = LinkedList() # BN đã khám trong ngày

        # Bảng băm lưu hồ sơ BS, key: doctor_id
        self.doctor_records_table = HashTable(initial_table_size=50); self.next_doctor_id_counter = 1
        self._load_data_from_csv(doctors_data_path, Doctor, self.doctor_records_table, self._update_next_doctor_id_counter, key_attribute_name='doctor_id', id_prefix='BS')

        # Bảng băm lưu hồ sơ PK, key: clinic_id
        self.clinic_records_table = HashTable(initial_table_size=20); self.next_clinic_id_counter = 1
        self._load_data_from_csv(clinics_data_path, Clinic, self.clinic_records_table, self._update_next_clinic_id_counter, key_attribute_name='clinic_id', id_prefix='PK')

        # Khởi tạo hàng đợi cho mỗi phòng khám đã tải
        all_clinics_list = self.clinic_records_table.get_all_values_as_list()
        for i in range(len(all_clinics_list)):
            clinic_obj = all_clinics_list.get(i)
            if clinic_obj and isinstance(clinic_obj, Clinic): self.clinic_examination_queues.put_item(clinic_obj.clinic_id, CustomPriorityQueue())

    def _get_csv_fieldnames(self, model_class_ref):
        # Lấy danh sách tên cột (fieldnames) cho file CSV dựa trên lớp model.
        fields_list = List()
        base_field_py_list = []
        if model_class_ref == Patient: base_field_py_list = ["ma_bn", "ho_ten", "ngay_sinh", "gioi_tinh", "dia_chi", "sdt", "cccd", "bhyt", "tien_su_benh_an", "di_ung_thuoc", "thoi_diem_dang_ky_he_thong", "lich_su_kham_benh"]
        elif model_class_ref == Doctor: base_field_py_list = ["ma_bac_si", "ho_ten_bac_si", "chuyen_khoa", "danh_sach_ma_phong_kham"]
        elif model_class_ref == Clinic: base_field_py_list = ["ma_phong_kham", "ten_phong_kham", "chuyen_khoa_pk", "danh_sach_ma_bac_si"]
        for f_name in base_field_py_list: fields_list.append(f_name)
        return fields_list

    def _convert_custom_list_to_py_list(self, custom_list_obj):
        # Chuyển đổi List tùy chỉnh sang list Python.
        py_list = []
        if custom_list_obj and len(custom_list_obj) > 0:
             for i in range(len(custom_list_obj)): py_list.append(custom_list_obj.get(i))
        return py_list

    def _load_data_from_csv(self, csv_filepath, model_class_ref, target_hash_table_obj, id_update_callback, key_attribute_name, id_prefix):
        # Tải dữ liệu từ file CSV vào bảng băm tương ứng.
        print(f"Đang tải từ: {csv_filepath}")
        if not os.path.exists(csv_filepath):
            print(f"LỖI: Tệp {csv_filepath} không tồn tại. Không thể tải dữ liệu cho {model_class_ref.__name__}.")
            return

        max_id_val = 0; loaded_items_count = 0
        csv_fieldnames_custom_array = self._get_csv_fieldnames(model_class_ref)
        if csv_fieldnames_custom_array.is_empty():
            print(f"Không có fieldnames cho {model_class_ref.__name__}. Không tải."); return

        csv_fieldnames_py_list = self._convert_custom_list_to_py_list(csv_fieldnames_custom_array)
        required_fields_map_dict = { # Các trường bắt buộc cho từng model
            Patient: ["ma_bn", "ho_ten", "ngay_sinh", "gioi_tinh", "sdt", "cccd"],
            Doctor: ["ma_bac_si", "ho_ten_bac_si", "chuyen_khoa"],
            Clinic: ["ma_phong_kham", "ten_phong_kham", "chuyen_khoa_pk"]
        }
        required_field_list = required_fields_map_dict.get(model_class_ref, [key_attribute_name])

        try:
            with open(csv_filepath, mode='r', encoding='utf-8', newline='') as csvfile:
                csv_reader = csv.DictReader(csvfile)
                if not csv_reader.fieldnames or not all(f_name in csv_reader.fieldnames for f_name in required_field_list):
                     print(f"Lỗi: Header của tệp {csv_filepath} không khớp hoặc thiếu cột quan trọng. Không tải."); return

                for row_idx, data_row in enumerate(csv_reader, 1):
                    try:
                        if not all(key in data_row and data_row[key] for key in required_field_list):
                            continue # Bỏ qua dòng thiếu dữ liệu bắt buộc

                        item_instance = model_class_ref.from_csv_row(data_row)
                        if model_class_ref == Patient and (not item_instance.national_id or item_instance.national_id in ["N/A_DEFAULT", "N/A_CSV_ERROR"]):
                            continue # Bỏ qua BN nếu CCCD không hợp lệ

                        item_unique_id = getattr(item_instance, key_attribute_name)
                        target_hash_table_obj.put_item(item_unique_id, item_instance); loaded_items_count +=1

                        # Thêm SĐT, CCCD vào Radix Tree cho BN
                        if model_class_ref == Patient and isinstance(item_instance, Patient):
                            if item_instance.phone_number and item_instance.phone_number.strip():
                                self.phone_radix_tree.insert(item_instance.phone_number.strip(), item_instance.patient_id)
                            if item_instance.national_id and item_instance.national_id.strip():
                                self.national_id_radix_tree.insert(item_instance.national_id.strip(), item_instance.patient_id)

                        # Cập nhật bộ đếm ID lớn nhất
                        if item_unique_id.startswith(id_prefix):
                            try: id_numeric_part = int(item_unique_id[len(id_prefix):])
                            except ValueError: continue
                            if id_numeric_part > max_id_val: max_id_val = id_numeric_part
                    except Exception as row_exception:
                        print(f"Lỗi xử lý dòng {row_idx} trong {csv_filepath}: {row_exception}")
            id_update_callback(max_id_val + 1) # Cập nhật bộ đếm ID tiếp theo
            print(f"Đã tải {loaded_items_count} mục từ {csv_filepath}. Next ID cho {model_class_ref.__name__}: {getattr(self, f'next_{model_class_ref.__name__.lower()}_id_counter', max_id_val + 1)}")
        except FileNotFoundError: print(f"LỖI: Tệp {csv_filepath} không tìm thấy dù đã kiểm tra.")
        except Exception as load_exception: print(f"Lỗi nghiêm trọng khi tải {csv_filepath}: {load_exception}")

    def _update_next_patient_id_counter(self, next_val): self.next_patient_id_counter = next_val
    def _update_next_doctor_id_counter(self, next_val): self.next_doctor_id_counter = next_val
    def _update_next_clinic_id_counter(self, next_val): self.next_clinic_id_counter = next_val

    def _get_save_path(self, csv_filename_const):
        # Xác định đường dẫn lưu file CSV (quan trọng cho PyInstaller).
        if getattr(sys, 'frozen', False): # Chạy từ .exe
            application_path = os.path.dirname(sys.executable)
            return os.path.join(application_path, csv_filename_const)
        else: # Chạy từ script .py
            return os.path.join(os.path.abspath("."), csv_filename_const)

    def _save_data_to_csv(self, csv_filename_const, model_class_ref, source_hash_table_obj):
        # Lưu dữ liệu từ bảng băm vào file CSV.
        actual_csv_filepath = self._get_save_path(csv_filename_const)
        print(f"Đang lưu vào: {actual_csv_filepath}")

        csv_fieldnames_custom_array = self._get_csv_fieldnames(model_class_ref)
        if csv_fieldnames_custom_array.is_empty():
            print(f"Không có fieldnames cho {model_class_ref.__name__}. Không lưu."); return

        csv_fieldnames_py_list = self._convert_custom_list_to_py_list(csv_fieldnames_custom_array)
        all_items_custom_array = source_hash_table_obj.get_all_values_as_list()
        saved_items_count = 0
        try:
            os.makedirs(os.path.dirname(actual_csv_filepath), exist_ok=True) # Tạo thư mục nếu chưa có

            with open(actual_csv_filepath, mode='w', encoding='utf-8', newline='') as csvfile:
                csv_writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames_py_list, extrasaction='ignore')
                csv_writer.writeheader()
                for i in range(len(all_items_custom_array)):
                    current_item = all_items_custom_array.get(i)
                    if isinstance(current_item, model_class_ref):
                        csv_writer.writerow(current_item.to_csv_row())
                        saved_items_count +=1
            print(f"Đã lưu {saved_items_count} mục vào {actual_csv_filepath}")
        except IOError as e: print(f"Lỗi IO khi lưu {actual_csv_filepath}: {e}.")
        except Exception as save_exception: print(f"Lỗi không xác định khi lưu {actual_csv_filepath}: {save_exception}")


    def _generate_patient_id(self): patient_id_val = f"BN{self.next_patient_id_counter:04d}"; self.next_patient_id_counter += 1; return patient_id_val
    def create_patient_record(self, full_name_val, dob_str, gender_val, address_val, phone_val, national_id_val, health_insurance_id_val="", medical_history_val="", drug_allergies_val=""):
        # Tạo hồ sơ bệnh nhân mới.
        if not all([full_name_val.strip(), dob_str.strip(), gender_val.strip(), phone_val.strip(), national_id_val.strip()]): return None, "Các trường (*) là bắt buộc.", "ERROR"
        try: dob_obj = datetime.datetime.strptime(dob_str, DATE_FORMAT_CSV).date()
        except ValueError: return None, f"Ngày sinh '{dob_str}' không hợp lệ (YYYY-MM-DD).", "ERROR"

        cleaned_national_id = national_id_val.strip()
        if self.national_id_radix_tree.search(cleaned_national_id): return None, f"Số CCCD '{cleaned_national_id}' đã tồn tại.", "ERROR"
        cleaned_phone = phone_val.strip()
        if self.phone_radix_tree.search(cleaned_phone): return None, f"Số điện thoại '{cleaned_phone}' đã tồn tại.", "ERROR"

        new_patient_id = self._generate_patient_id()
        if self.patient_records_table.contains_key(new_patient_id): return None, f"Mã BN {new_patient_id} đã tồn tại (lỗi logic).", "ERROR"

        patient_obj = Patient(new_patient_id, full_name_val, dob_obj, gender_val, address_val, cleaned_phone, cleaned_national_id, health_insurance_id_val, medical_history_val, drug_allergies_val)
        self.patient_records_table.put_item(new_patient_id, patient_obj)

        if cleaned_phone: self.phone_radix_tree.insert(cleaned_phone, new_patient_id)
        if cleaned_national_id: self.national_id_radix_tree.insert(cleaned_national_id, new_patient_id)

        self._save_data_to_csv(PATIENTS_CSV_FILENAME, Patient, self.patient_records_table)
        return patient_obj, f"Đã tạo hồ sơ BN: {new_patient_id}", "INFO"

    def find_patient_by_id(self, patient_id_val): return self.patient_records_table.get_item(patient_id_val)
    def update_patient_info(self, patient_id_val, **update_kwargs):
        # Cập nhật thông tin bệnh nhân.
        patient_obj = self.find_patient_by_id(patient_id_val)
        if not patient_obj: return False, f"BN mã {patient_id_val} không tồn tại.", "ERROR"

        old_phone = patient_obj.phone_number; old_national_id = patient_obj.national_id
        new_national_id_raw = update_kwargs.get("national_id")
        if new_national_id_raw is not None and not str(new_national_id_raw).strip(): return False, f"CCCD không được trống cho BN {patient_id_val}.", "ERROR"
        cleaned_new_national_id = str(new_national_id_raw).strip() if new_national_id_raw is not None else None
        if cleaned_new_national_id and cleaned_new_national_id != old_national_id:
            existing_patient_id_for_new_nid = self.national_id_radix_tree.search(cleaned_new_national_id)
            if existing_patient_id_for_new_nid and existing_patient_id_for_new_nid != patient_id_val:
                return False, f"Số CCCD '{cleaned_new_national_id}' đã dùng bởi BN khác ({existing_patient_id_for_new_nid}).", "ERROR"
        new_phone_raw = update_kwargs.get("phone_number")
        cleaned_new_phone = str(new_phone_raw).strip() if new_phone_raw is not None else None
        if cleaned_new_phone and cleaned_new_phone != old_phone:
            existing_patient_id_for_new_phone = self.phone_radix_tree.search(cleaned_new_phone)
            if existing_patient_id_for_new_phone and existing_patient_id_for_new_phone != patient_id_val:
                return False, f"Số điện thoại '{cleaned_new_phone}' đã dùng bởi BN khác ({existing_patient_id_for_new_phone}).", "ERROR"

        was_updated = False
        for attr_key, new_attr_value in update_kwargs.items():
            if hasattr(patient_obj, attr_key) and new_attr_value is not None:
                current_attr_value = getattr(patient_obj, attr_key); final_new_value = new_attr_value
                if attr_key == "date_of_birth" and isinstance(new_attr_value, str):
                    if not new_attr_value.strip(): final_new_value = None # Cho phép xóa ngày sinh
                    else:
                        try: final_new_value = datetime.datetime.strptime(new_attr_value, DATE_FORMAT_CSV).date()
                        except ValueError: return False, f"Ngày sinh '{new_attr_value}' không hợp lệ.", "ERROR"
                if attr_key == "phone_number": final_new_value = str(final_new_value).strip()
                if attr_key == "national_id": final_new_value = str(final_new_value).strip()
                if current_attr_value != final_new_value: setattr(patient_obj, attr_key, final_new_value); was_updated = True
        if was_updated:
            # Cập nhật Radix Trees nếu SĐT/CCCD thay đổi
            if patient_obj.phone_number != old_phone:
                if old_phone and old_phone.strip(): self.phone_radix_tree.delete(old_phone.strip())
                if patient_obj.phone_number and patient_obj.phone_number.strip(): self.phone_radix_tree.insert(patient_obj.phone_number.strip(), patient_id_val)
            if patient_obj.national_id != old_national_id:
                if old_national_id and old_national_id.strip(): self.national_id_radix_tree.delete(old_national_id.strip())
                if patient_obj.national_id and patient_obj.national_id.strip(): self.national_id_radix_tree.insert(patient_obj.national_id.strip(), patient_id_val)
            self._save_data_to_csv(PATIENTS_CSV_FILENAME, Patient, self.patient_records_table)
            return True, f"Đã cập nhật BN {patient_id_val}.", "INFO"
        return False, f"Không có thay đổi cho BN {patient_id_val}.", "INFO"

    def delete_patient_record(self, patient_id_val):
        # Xóa hồ sơ bệnh nhân.
        patient_to_delete = self.find_patient_by_id(patient_id_val)
        if not patient_to_delete: return False, f"Không tìm thấy BN {patient_id_val}.", "ERROR"
        # Kiểm tra BN có trong hàng đợi nào không
        all_queues_pairs = self.clinic_examination_queues.get_all_key_value_pairs_as_list()
        for i in range(len(all_queues_pairs)):
            clinic_id_key, clinic_queue = all_queues_pairs.get(i)
            if clinic_queue:
                all_heap_elements = clinic_queue.internal_heap.get_all_heap_elements()
                for j in range(len(all_heap_elements)):
                    if all_heap_elements.get(j).patient_id == patient_id_val: return False, f"Không thể xóa BN {patient_id_val} vì đang trong HĐ của PK {clinic_id_key}.", "ERROR"
        if self.patient_records_table.delete_item(patient_id_val):
            if patient_to_delete.phone_number and patient_to_delete.phone_number.strip(): self.phone_radix_tree.delete(patient_to_delete.phone_number.strip())
            if patient_to_delete.national_id and patient_to_delete.national_id.strip(): self.national_id_radix_tree.delete(patient_to_delete.national_id.strip())
            self._save_data_to_csv(PATIENTS_CSV_FILENAME, Patient, self.patient_records_table)
            return True, f"Đã xóa BN {patient_id_val}.", "INFO"
        return False, f"Lỗi khi xóa BN {patient_id_val} khỏi bảng băm.", "ERROR"

    def register_for_examination(self, patient_id_val, clinic_id_val, priority_level_str):
        # Đăng ký bệnh nhân vào hàng đợi khám.
        patient_obj = self.find_patient_by_id(patient_id_val)
        if not patient_obj: return False, f"Không tìm thấy BN mã {patient_id_val}.", "ERROR"
        clinic_obj = self.find_clinic_by_id(clinic_id_val)
        if not clinic_obj: return False, f"Không tìm thấy PK mã {clinic_id_val}.", "ERROR"
        # Kiểm tra BN đã có trong hàng đợi nào khác chưa
        all_queues_pairs = self.clinic_examination_queues.get_all_key_value_pairs_as_list()
        for i in range(len(all_queues_pairs)):
            _clinic_id, queue_obj = all_queues_pairs.get(i)
            if queue_obj:
                all_heap_elements = queue_obj.internal_heap.get_all_heap_elements()
                for j in range(len(all_heap_elements)):
                    if all_heap_elements.get(j).patient_id == patient_id_val: return False, f"BN {patient_id_val} đã có trong HĐ PK {_clinic_id}.", "WARNING"
        clinic_specific_queue = self.clinic_examination_queues.get_item(clinic_id_val)
        if not clinic_specific_queue: clinic_specific_queue = CustomPriorityQueue(); self.clinic_examination_queues.put_item(clinic_id_val, clinic_specific_queue)
        try: patient_queue_item = PatientInQueue(patient_obj, priority_level_str)
        except ValueError as e: return False, f"Lỗi đăng ký: {e}", "ERROR"
        clinic_specific_queue.add_item(patient_queue_item)
        return True, f"BN {patient_obj.full_name} đã thêm vào HĐ PK {clinic_id_val} ưu tiên '{priority_level_str}'.", "INFO"

    def call_next_patient_for_exam(self, clinic_id_val):
        # Gọi bệnh nhân tiếp theo từ hàng đợi của phòng khám.
        clinic_queue = self.clinic_examination_queues.get_item(clinic_id_val)
        if not clinic_queue or clinic_queue.is_empty(): return None, f"HĐ PK {clinic_id_val} rỗng.", "INFO"
        exam_patient = clinic_queue.remove_first_item()
        if exam_patient: return exam_patient, f"Gọi BN: {exam_patient.patient_profile.full_name} (ID: {exam_patient.patient_id}) từ PK {clinic_id_val}", "INFO"
        return None, f"Không có BN trong HĐ PK {clinic_id_val}.", "INFO"

    def complete_examination(self, patient_id_val, exam_type, exam_result, exam_notes="", attending_doctor_id="", exam_clinic_id=""):
        # Hoàn thành khám, lưu lịch sử khám cho bệnh nhân.
        patient_obj = self.find_patient_by_id(patient_id_val)
        if patient_obj:
            patient_obj.add_examination_record(datetime.date.today(), exam_type, exam_result, exam_notes, attending_doctor_id, exam_clinic_id)
            # Thêm vào danh sách đã khám trong ngày (nếu chưa có)
            is_in_today_list = any(patient_obj.patient_id == self.examined_patients_today_list.get(i).patient_id for i in range(len(self.examined_patients_today_list)))
            if not is_in_today_list: self.examined_patients_today_list.append(patient_obj)
            self._save_data_to_csv(PATIENTS_CSV_FILENAME, Patient, self.patient_records_table)
            return True, f"BN {patient_obj.full_name} đã khám xong (Loại: {exam_type}).", "INFO"
        return False, f"Không tìm thấy BN {patient_id_val}.", "ERROR"

    def handle_absent_called_patient(self, absent_patient_obj, original_clinic_id):
        # Xử lý bệnh nhân được gọi nhưng vắng mặt.
        if not absent_patient_obj: return True, "Lỗi: Không có BN vắng mặt.", "ERROR"
        clinic_queue = self.clinic_examination_queues.get_item(original_clinic_id)
        if not clinic_queue: return True, f"Lỗi: Không tìm thấy HĐ PK {original_clinic_id}.", "ERROR"
        absent_patient_obj.increment_absent_count()
        msg = f"BN {absent_patient_obj.patient_id} vắng lần {absent_patient_obj.absent_count} tại PK {original_clinic_id}."
        if absent_patient_obj.should_leave_queue(): return True, msg + f" BN bị loại.", "INFO" # Bị loại nếu vắng quá 3 lần
        else: # Đưa lại vào hàng đợi với ưu tiên giảm (nếu có thể)
            curr_prio = absent_patient_obj.priority; min_prio = min(PatientInQueue.PRIORITY_MAP.values())
            if curr_prio > min_prio: absent_patient_obj.priority = max(min_prio, curr_prio - 1)
            clinic_queue.add_item(absent_patient_obj)
            return False, msg + f" BN đưa lại HĐ PK {original_clinic_id} ưu tiên '{absent_patient_obj.get_priority_display_name()}'.", "INFO"

    def handle_patient_leaving_queue(self, patient_id_leaving, clinic_id_val):
        # Xử lý bệnh nhân tự ý rời hàng đợi.
        clinic_queue = self.clinic_examination_queues.get_item(clinic_id_val)
        if not clinic_queue: return False, f"Không tìm thấy HĐ PK {clinic_id_val}.", "ERROR"
        # Lấy tất cả BN trong heap, tìm BN cần xóa, tạo lại heap không có BN đó
        all_q_patients_custom_array = clinic_queue.internal_heap.get_all_heap_elements()
        temp_py_list_for_filtering = self._convert_custom_list_to_py_list(all_q_patients_custom_array)
        patient_to_remove_instance = next((p for p in temp_py_list_for_filtering if p.patient_id == patient_id_leaving), None)
        if patient_to_remove_instance:
            temp_py_list_for_filtering.remove(patient_to_remove_instance)
            clinic_queue.internal_heap.heap_array = List(); # Reset heap
            for p_item in temp_py_list_for_filtering: clinic_queue.internal_heap.add_item(p_item) # Thêm lại các BN còn lại
            return True, f"BN {patient_id_leaving} đã xóa khỏi HĐ PK {clinic_id_val}.", "INFO"
        return False, f"Không tìm thấy BN {patient_id_leaving} trong HĐ PK {clinic_id_val}.", "ERROR"

    def get_clinic_queue_display_list(self, clinic_id_val):
        # Lấy danh sách chuỗi hiển thị hàng đợi của một phòng khám.
        clinic_queue = self.clinic_examination_queues.get_item(clinic_id_val)
        empty_msg_list = List(); empty_msg_list.append(f"Hàng đợi PK {clinic_id_val} rỗng.")
        if not clinic_queue or clinic_queue.is_empty(): return empty_msg_list
        return clinic_queue.get_display_queue_as_strings(patient_in_queue_class_ref=PatientInQueue)

    def update_priority_for_long_waiters(self, clinic_id_val, max_wait_seconds=3600):
        # Tăng ưu tiên cho bệnh nhân chờ lâu (ví dụ: quá 1 giờ).
        clinic_queue = self.clinic_examination_queues.get_item(clinic_id_val)
        if not clinic_queue: return 0, f"Không tìm thấy HĐ PK {clinic_id_val}.", "ERROR"
        num_upd = clinic_queue.update_long_waiter_priority(max_wait_seconds, patient_in_queue_class_ref=PatientInQueue)
        if num_upd > 0: return num_upd, f"Đã cập nhật ưu tiên cho {num_upd} BN chờ lâu tại PK {clinic_id_val}.", "INFO"
        return 0, f"Không có BN tại PK {clinic_id_val} cần cập nhật ưu tiên.", "INFO"

    def change_patient_priority_in_queue(self, clinic_id_val, patient_id_val, new_priority_level_str):
        # Thay đổi mức độ ưu tiên của bệnh nhân trong hàng đợi.
        if new_priority_level_str not in PatientInQueue.PRIORITY_MAP: return False, f"Ưu tiên '{new_priority_level_str}' không hợp lệ.", "ERROR"
        clinic_queue = self.clinic_examination_queues.get_item(clinic_id_val)
        if not clinic_queue: return False, f"Không tìm thấy HĐ PK {clinic_id_val}.", "ERROR"
        success_flag = clinic_queue.change_queued_patient_priority(patient_id_val, new_priority_level_str, patient_in_queue_class_ref=PatientInQueue)
        if success_flag: return True, f"Đã đổi ưu tiên BN {patient_id_val} tại PK {clinic_id_val} thành '{new_priority_level_str}'.", "INFO"
        return False, f"Không thể đổi ưu tiên BN {patient_id_val} tại PK {clinic_id_val}.", "ERROR"

    def list_all_patients(self): return self.patient_records_table.get_all_values_as_list() # Lấy tất cả BN
    def list_patients_examined_today(self): return self.examined_patients_today_list # Lấy BN đã khám trong ngày

    def advanced_patient_search(self, **search_criteria):
        # Tìm kiếm bệnh nhân nâng cao theo nhiều tiêu chí.
        phone_query_exact = search_criteria.get("phone_number_exact", "").strip()
        national_id_query_exact = search_criteria.get("national_id_exact", "").strip()

        # Ưu tiên tìm kiếm chính xác bằng RadixTree nếu có SĐT hoặc CCCD chính xác
        if phone_query_exact:
            patient_id_found = self.search_patient_by_phone_radix(phone_query_exact)
            if patient_id_found:
                patient_obj = self.find_patient_by_id(patient_id_found)
                if patient_obj: result = List(); result.append(patient_obj); return result
            return List() # Trả về list rỗng nếu không tìm thấy
        if national_id_query_exact:
            patient_id_found = self.search_patient_by_national_id_radix(national_id_query_exact)
            if patient_id_found:
                patient_obj = self.find_patient_by_id(patient_id_found)
                if patient_obj: result = List(); result.append(patient_obj); return result
            return List()

        # Tìm kiếm chứa (contains) nếu không có SĐT/CCCD chính xác
        results_list = List(); all_pats = self.patient_records_table.get_all_values_as_list()
        name_query = search_criteria.get("full_name", "").lower().strip()
        phone_query_contains = search_criteria.get("phone_number", "").strip()
        dob_query_str = search_criteria.get("date_of_birth", "").strip()
        national_id_query_contains = search_criteria.get("national_id", "").strip()
        health_ins_query = search_criteria.get("health_insurance_id", "").strip()
        dob_query_date = None
        if dob_query_str:
            try: dob_query_date = datetime.datetime.strptime(dob_query_str, DATE_FORMAT_CSV).date()
            except ValueError: pass # Bỏ qua nếu ngày sinh không hợp lệ cho tìm kiếm chứa
        for i in range(len(all_pats)):
            pat = all_pats.get(i)
            match_name = (not name_query) or (name_query in pat.full_name.lower())
            match_phone = (not phone_query_contains) or (phone_query_contains in pat.phone_number)
            match_dob = True # Mặc định là true nếu không có dob_query_str
            if dob_query_str: match_dob = (dob_query_date is not None and pat.date_of_birth == dob_query_date)
            match_nat_id = (not national_id_query_contains) or (national_id_query_contains.lower() in pat.national_id.lower())
            match_health_ins = (not health_ins_query) or (health_ins_query.lower() in pat.health_insurance_id.lower())
            if match_name and match_phone and match_dob and match_nat_id and match_health_ins: results_list.append(pat)
        return results_list

    def search_patient_by_phone_radix(self, phone_number):
        # Tìm patient_id bằng SĐT (chính xác) qua RadixTree.
        if not phone_number or not isinstance(phone_number, str): return None
        return self.phone_radix_tree.search(phone_number.strip())

    def search_patient_by_national_id_radix(self, national_id):
        # Tìm patient_id bằng CCCD (chính xác) qua RadixTree.
        if not national_id or not isinstance(national_id, str): return None
        return self.national_id_radix_tree.search(national_id.strip())

    # --- Quản lý Bác sĩ ---
    def _generate_doctor_id(self): doc_id = f"BS{self.next_doctor_id_counter:03d}"; self.next_doctor_id_counter += 1; return doc_id
    def create_doctor(self, doctor_name_val, specialty_val):
        # Tạo bác sĩ mới.
        if not doctor_name_val.strip() or not specialty_val.strip(): return None, "Họ tên BS và chuyên khoa là bắt buộc.", "ERROR"
        new_doc_id = self._generate_doctor_id()
        if self.doctor_records_table.contains_key(new_doc_id): return None, f"Mã BS {new_doc_id} đã tồn tại.", "ERROR"
        doc_obj = Doctor(new_doc_id, doctor_name_val, specialty_val)
        self.doctor_records_table.put_item(new_doc_id, doc_obj); self._save_data_to_csv(DOCTORS_CSV_FILENAME, Doctor, self.doctor_records_table)
        return doc_obj, f"Đã tạo BS: {new_doc_id}", "INFO"

    def find_doctor_by_id(self, doctor_id_val): return self.doctor_records_table.get_item(doctor_id_val)
    def update_doctor_info(self, doctor_id_val, new_name=None, new_specialty=None):
        # Cập nhật thông tin bác sĩ.
        doc_obj = self.find_doctor_by_id(doctor_id_val);
        if not doc_obj: return False, f"Không tìm thấy BS {doctor_id_val}.", "ERROR"
        was_upd = False
        if new_name is not None and new_name.strip() and doc_obj.doctor_name != new_name.strip(): doc_obj.doctor_name = new_name.strip(); was_upd = True
        if new_specialty is not None and new_specialty.strip() and doc_obj.specialty != new_specialty.strip(): doc_obj.specialty = new_specialty.strip(); was_upd = True
        if was_upd: self._save_data_to_csv(DOCTORS_CSV_FILENAME, Doctor, self.doctor_records_table); return True, f"Đã cập nhật BS {doctor_id_val}.", "INFO"
        return False, f"Không có thay đổi cho BS {doctor_id_val}.", "INFO"

    def delete_doctor(self, doctor_id_val):
        # Xóa bác sĩ. Đồng thời xóa BS khỏi danh sách của các PK liên quan.
        if self.doctor_records_table.delete_item(doctor_id_val):
            all_clinics_list = self.clinic_records_table.get_all_values_as_list()
            for i in range(len(all_clinics_list)): # Duyệt qua các PK
                clinic_obj = all_clinics_list.get(i)
                # Tạo danh sách BS mới cho PK, loại bỏ BS bị xóa
                new_doc_id_list_for_clinic = List()
                for j in range(len(clinic_obj.doctor_id_list)):
                    if clinic_obj.doctor_id_list.get(j) != doctor_id_val: new_doc_id_list_for_clinic.append(clinic_obj.doctor_id_list.get(j))
                clinic_obj.doctor_id_list = new_doc_id_list_for_clinic
            self._save_data_to_csv(DOCTORS_CSV_FILENAME, Doctor, self.doctor_records_table)
            self._save_data_to_csv(CLINICS_CSV_FILENAME, Clinic, self.clinic_records_table) # Lưu lại PK vì DS BS đã đổi
            return True, f"Đã xóa BS {doctor_id_val}.", "INFO"
        return False, f"Không tìm thấy BS {doctor_id_val}.", "ERROR"
    def list_all_doctors(self): return self.doctor_records_table.get_all_values_as_list()

    # --- Quản lý Phòng khám ---
    def _generate_clinic_id(self): clinic_id_val = f"PK{self.next_clinic_id_counter:03d}"; self.next_clinic_id_counter += 1; return clinic_id_val
    def create_clinic(self, clinic_name_val, clinic_specialty_val):
        # Tạo phòng khám mới.
        if not clinic_name_val.strip() or not clinic_specialty_val.strip(): return None, "Tên PK và chuyên khoa là bắt buộc.", "ERROR"
        new_clinic_id = self._generate_clinic_id()
        if self.clinic_records_table.contains_key(new_clinic_id): return None, f"Mã PK {new_clinic_id} đã tồn tại.", "ERROR"
        clinic_obj = Clinic(new_clinic_id, clinic_name_val, clinic_specialty_val)
        self.clinic_records_table.put_item(new_clinic_id, clinic_obj)
        self.clinic_examination_queues.put_item(new_clinic_id, CustomPriorityQueue()) # Tạo hàng đợi mới cho PK
        self._save_data_to_csv(CLINICS_CSV_FILENAME, Clinic, self.clinic_records_table)
        return clinic_obj, f"Đã tạo PK: {new_clinic_id}", "INFO"

    def find_clinic_by_id(self, clinic_id_val): return self.clinic_records_table.get_item(clinic_id_val)
    def update_clinic_info(self, clinic_id_val, new_name=None, new_specialty=None):
        # Cập nhật thông tin phòng khám.
        clinic_obj = self.find_clinic_by_id(clinic_id_val);
        if not clinic_obj: return False, f"Không tìm thấy PK {clinic_id_val}.", "ERROR"
        was_upd = False
        if new_name is not None and new_name.strip() and clinic_obj.clinic_name != new_name.strip(): clinic_obj.clinic_name = new_name.strip(); was_upd = True
        if new_specialty is not None and new_specialty.strip() and clinic_obj.clinic_specialty != new_specialty.strip(): clinic_obj.clinic_specialty = new_specialty.strip(); was_upd = True
        if was_upd: self._save_data_to_csv(CLINICS_CSV_FILENAME, Clinic, self.clinic_records_table); return True, f"Đã cập nhật PK {clinic_id_val}.", "INFO"
        return False, f"Không có thay đổi cho PK {clinic_id_val}.", "INFO"

    def delete_clinic(self, clinic_id_val):
        # Xóa phòng khám. Chỉ xóa nếu hàng đợi của PK đó rỗng.
        clinic_queue = self.clinic_examination_queues.get_item(clinic_id_val)
        if clinic_queue and not clinic_queue.is_empty(): return False, f"Không thể xóa PK {clinic_id_val} vì còn BN trong HĐ.", "ERROR"
        if self.clinic_records_table.delete_item(clinic_id_val):
            self.clinic_examination_queues.delete_item(clinic_id_val) # Xóa hàng đợi của PK
            # Xóa PK này khỏi danh sách làm việc của các BS liên quan
            all_doctors_list = self.doctor_records_table.get_all_values_as_list()
            for i in range(len(all_doctors_list)):
                doc_obj = all_doctors_list.get(i)
                new_clinic_id_list_for_doc = List()
                for j in range(len(doc_obj.clinic_id_list)):
                    if doc_obj.clinic_id_list.get(j) != clinic_id_val: new_clinic_id_list_for_doc.append(doc_obj.clinic_id_list.get(j))
                doc_obj.clinic_id_list = new_clinic_id_list_for_doc
            self._save_data_to_csv(CLINICS_CSV_FILENAME, Clinic, self.clinic_records_table)
            self._save_data_to_csv(DOCTORS_CSV_FILENAME, Doctor, self.doctor_records_table) # Lưu BS vì DS PK đã đổi
            return True, f"Đã xóa PK {clinic_id_val}.", "INFO"
        return False, f"Không tìm thấy PK {clinic_id_val}.", "ERROR"
    def list_all_clinics(self): return self.clinic_records_table.get_all_values_as_list()

    def assign_doctor_to_clinic(self, doctor_id_val, clinic_id_val):
        # Gán một bác sĩ vào một phòng khám.
        doc_obj = self.find_doctor_by_id(doctor_id_val); clinic_obj = self.find_clinic_by_id(clinic_id_val)
        if not doc_obj: return False, f"Không tìm thấy BS {doctor_id_val}.", "ERROR"
        if not clinic_obj: return False, f"Không tìm thấy PK {clinic_id_val}.", "ERROR"
        was_upd = False
        # Kiểm tra và thêm BS vào danh sách của PK
        doc_already_in_clinic = any(clinic_obj.doctor_id_list.get(i) == doctor_id_val for i in range(len(clinic_obj.doctor_id_list)))
        if not doc_already_in_clinic: clinic_obj.doctor_id_list.append(doctor_id_val); was_upd = True
        # Kiểm tra và thêm PK vào danh sách của BS
        clinic_already_in_doc_list = any(doc_obj.clinic_id_list.get(i) == clinic_id_val for i in range(len(doc_obj.clinic_id_list)))
        if not clinic_already_in_doc_list: doc_obj.clinic_id_list.append(clinic_id_val); was_upd = True
        if was_upd:
            self._save_data_to_csv(CLINICS_CSV_FILENAME, Clinic, self.clinic_records_table)
            self._save_data_to_csv(DOCTORS_CSV_FILENAME, Doctor, self.doctor_records_table)
            return True, f"Đã gán BS {doctor_id_val} cho PK {clinic_id_val}.", "INFO"
        return False, f"BS {doctor_id_val} đã được gán cho PK {clinic_id_val} từ trước.", "INFO"

    def remove_doctor_from_clinic(self, doctor_id_val, clinic_id_val):
        # Xóa một bác sĩ khỏi một phòng khám.
        doc_obj = self.find_doctor_by_id(doctor_id_val); clinic_obj = self.find_clinic_by_id(clinic_id_val)
        if not doc_obj: return False, f"Không tìm thấy BS {doctor_id_val}.", "ERROR"
        if not clinic_obj: return False, f"Không tìm thấy PK {clinic_id_val}.", "ERROR"
        was_removed = False
        # Xóa BS khỏi danh sách của PK
        new_doc_id_list_for_clinic = List()
        for i in range(len(clinic_obj.doctor_id_list)):
            if clinic_obj.doctor_id_list.get(i) != doctor_id_val: new_doc_id_list_for_clinic.append(clinic_obj.doctor_id_list.get(i))
            else: was_removed = True
        clinic_obj.doctor_id_list = new_doc_id_list_for_clinic
        # Xóa PK khỏi danh sách của BS
        new_clinic_id_list_for_doc = List()
        for i in range(len(doc_obj.clinic_id_list)):
            if doc_obj.clinic_id_list.get(i) != clinic_id_val: new_clinic_id_list_for_doc.append(doc_obj.clinic_id_list.get(i))
            else: was_removed = True
        doc_obj.clinic_id_list = new_clinic_id_list_for_doc
        if was_removed:
            self._save_data_to_csv(CLINICS_CSV_FILENAME, Clinic, self.clinic_records_table)
            self._save_data_to_csv(DOCTORS_CSV_FILENAME, Doctor, self.doctor_records_table)
            return True, f"Đã xóa BS {doctor_id_val} khỏi PK {clinic_id_val}.", "INFO"
        return False, f"BS {doctor_id_val} không có trong PK {clinic_id_val}.", "INFO"

    def _collect_all_examination_history(self):
        # Thu thập tất cả lịch sử khám từ tất cả bệnh nhân.
        all_history_records_custom_array = List()
        all_patients_custom_array = self.patient_records_table.get_all_values_as_list()
        for i in range(len(all_patients_custom_array)):
            patient_obj = all_patients_custom_array.get(i)
            if isinstance(patient_obj, Patient):
                for history_item_dict in patient_obj.examination_history: # Duyệt LinkedList lịch sử của BN
                    record_copy = dict(history_item_dict) # Tạo bản sao
                    record_copy['ma_bn'] = patient_obj.patient_id # Thêm mã và tên BN vào bản ghi
                    record_copy['ho_ten_bn'] = patient_obj.full_name
                    all_history_records_custom_array.append(record_copy)
        return all_history_records_custom_array

    def filter_examination_history(self, from_date_str=None, to_date_str=None, doctor_id_filter=None, clinic_id_filter=None):
        # Lọc lịch sử khám bệnh theo các tiêu chí.
        all_history_custom_array = self._collect_all_examination_history()
        if all_history_custom_array.is_empty(): return List(), "Không có lịch sử khám.", "INFO"

        filtered_py_list = self._convert_custom_list_to_py_list(all_history_custom_array) # Chuyển sang list Python để dễ lọc

        # Xử lý bộ lọc ngày
        from_date_obj = None; to_date_obj = None
        if from_date_str:
            try: from_date_obj = datetime.datetime.strptime(from_date_str, DATE_FORMAT_CSV).date()
            except ValueError: return List(), f"Từ ngày '{from_date_str}' không hợp lệ.", "ERROR"
        if to_date_str:
            try: to_date_obj = datetime.datetime.strptime(to_date_str, DATE_FORMAT_CSV).date()
            except ValueError: return List(), f"Đến ngày '{to_date_str}' không hợp lệ.", "ERROR"
        if from_date_obj and to_date_obj and from_date_obj > to_date_obj: return List(), "'Từ ngày' không được lớn hơn 'Đến ngày'.", "ERROR"

        # Áp dụng các bộ lọc
        if from_date_obj: filtered_py_list = [r for r in filtered_py_list if isinstance(r.get('ngay_kham'), datetime.date) and r['ngay_kham'] >= from_date_obj]
        if to_date_obj: filtered_py_list = [r for r in filtered_py_list if isinstance(r.get('ngay_kham'), datetime.date) and r['ngay_kham'] <= to_date_obj]
        if doctor_id_filter and doctor_id_filter.strip(): filtered_py_list = [r for r in filtered_py_list if doctor_id_filter.strip().lower() in str(r.get('ma_bac_si_kham', '')).lower()]
        if clinic_id_filter and clinic_id_filter.strip(): filtered_py_list = [r for r in filtered_py_list if clinic_id_filter.strip().lower() in str(r.get('ma_phong_kham_kham', '')).lower()]

        # Sắp xếp kết quả theo ngày khám giảm dần
        if filtered_py_list:
            def get_sort_key_func(item_dict_val): # Hàm lấy key để sort
                exam_date_val = item_dict_val.get('ngay_kham')
                return exam_date_val if isinstance(exam_date_val, datetime.date) else datetime.date.min # Xử lý ngày không hợp lệ
            filtered_py_list.sort(key=get_sort_key_func, reverse=True)

        final_filtered_custom_array = List() # Chuyển lại List tùy chỉnh
        for item_dict in filtered_py_list: final_filtered_custom_array.append(item_dict)

        if final_filtered_custom_array.is_empty(): return List(), "Không có LS khám khớp tiêu chí.", "INFO"
        return final_filtered_custom_array, f"Tìm thấy {len(final_filtered_custom_array)} kết quả LS khám.", "INFO"
