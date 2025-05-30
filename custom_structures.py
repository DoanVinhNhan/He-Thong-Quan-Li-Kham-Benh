# custom_structures.py
import datetime
from typing import Any, List, Optional, Tuple, Iterable

# --- Phần Custom Linked List ---
class ListNode:
    """Nút trong danh sách liên kết."""
    def __init__(self, value: Any):
        self.value = value
        self.next: Optional[ListNode] = None

    def __str__(self) -> str:
        return str(self.value)

class CustomLinkedList:
    """Cấu trúc Danh sách liên kết tùy chỉnh."""
    def __init__(self):
        self.head: Optional[ListNode] = None
        self.tail: Optional[ListNode] = None
        self._size: int = 0

    def append(self, value: Any) -> None:
        new_node = ListNode(value)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            if self.tail: # Should always be true if head is not None
                self.tail.next = new_node
                self.tail = new_node
            else: # Should not happen if logic is correct
                self.head = new_node 
                self.tail = new_node
        self._size += 1

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def __iter__(self) -> Iterable[Any]:
        """Cho phép duyệt qua danh sách."""
        current = self.head
        while current:
            yield current.value
            current = current.next

    def get_all_elements(self) -> List[Any]:
        """Trả về một Python list chứa tất cả các phần tử (dùng cho tiện lợi khi cần list)."""
        return list(self)

    def get(self, index: int) -> Any:
        """Lấy phần tử tại vị trí index."""
        if not (0 <= index < self._size):
            raise IndexError("Chỉ mục ngoài phạm vi danh sách.")
        current = self.head
        for _ in range(index):
            if current:
                current = current.next
            else: # Không nên xảy ra nếu logic đúng
                raise IndexError("Lỗi logic khi duyệt danh sách.")
        if current:
            return current.value
        raise IndexError("Không tìm thấy phần tử.") # Không nên xảy ra

    def get_last(self) -> Optional[Any]:
        """Lấy phần tử cuối cùng của danh sách."""
        if self.tail:
            return self.tail.value
        return None
        
    def __str__(self) -> str:
        elements = [str(item) for item in self]
        return "CustomLinkedList: [" + " -> ".join(elements) + "]" if elements else "CustomLinkedList: (empty)"

# --- Phần Custom Hash Table ---
class HashNode:
    """
    Nút trong danh sách liên kết của mỗi bucket trong bảng băm.
    """
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.next: Optional[HashNode] = None

    def __str__(self):
        return f"({self.key}: {self.value})"

class CustomHashTable:
    """
    Cấu trúc Bảng băm tùy chỉnh sử dụng phương pháp Nối chuỗi (Chaining).
    """
    def __init__(self, initial_size: int = 100):
        if initial_size <= 0:
            raise ValueError("Kích thước bảng băm phải là số dương.")
        self.size: int = initial_size
        self.buckets: List[Optional[HashNode]] = [None] * self.size
        self.count: int = 0 # Số lượng phần tử hiện có

    def _hash_function(self, key: Any) -> int:
        """
        Hàm băm đơn giản cho khóa (key).
        Đối với chuỗi, tính tổng giá trị ASCII của các ký tự.
        """
        if isinstance(key, str):
            hash_val = sum(ord(char) for char in key)
        elif isinstance(key, int):
            hash_val = key
        else:
            # Sử dụng hàm hash() tích hợp của Python cho các kiểu khác và xử lý thêm
            hash_val = hash(key)
        
        return hash_val % self.size

    def put(self, key: Any, value: Any) -> None:
        """
        Thêm hoặc cập nhật một cặp key-value vào bảng băm.
        """
        index = self._hash_function(key)
        current_node = self.buckets[index]

        # Duyệt qua danh sách liên kết tại bucket
        while current_node:
            if current_node.key == key:
                current_node.value = value # Cập nhật giá trị nếu khóa đã tồn tại
                return
            current_node = current_node.next
        
        # Nếu khóa chưa tồn tại, thêm nút mới vào đầu danh sách liên kết
        new_node = HashNode(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.count += 1
        
    def get(self, key: Any) -> Optional[Any]:
        """
        Lấy giá trị tương ứng với khóa (key).
        Trả về None nếu khóa không tồn tại.
        """
        index = self._hash_function(key)
        current_node = self.buckets[index]

        while current_node:
            if current_node.key == key:
                return current_node.value
            current_node = current_node.next
        
        return None # Khóa không tìm thấy

    def delete(self, key: Any) -> bool:
        """
        Xóa một cặp key-value khỏi bảng băm dựa vào khóa.
        Trả về True nếu xóa thành công, False nếu khóa không tồn tại.
        """
        index = self._hash_function(key)
        current_node = self.buckets[index]
        prev_node: Optional[HashNode] = None

        while current_node:
            if current_node.key == key:
                if prev_node:
                    prev_node.next = current_node.next
                else: # Nút cần xóa là nút đầu tiên của bucket
                    self.buckets[index] = current_node.next
                self.count -= 1
                return True # Xóa thành công
            prev_node = current_node
            current_node = current_node.next
            
        return False # Khóa không tìm thấy để xóa

    def contains(self, key: Any) -> bool:
        """
        Kiểm tra xem một khóa (key) có tồn tại trong bảng băm không.
        """
        return self.get(key) is not None

    def get_all_values(self) -> List[Any]:
        """
        Trả về một danh sách tất cả các giá trị (values) trong bảng băm.
        Thứ tự không được đảm bảo.
        """
        values_list: List[Any] = []
        for bucket_head in self.buckets:
            current_node = bucket_head
            while current_node:
                values_list.append(current_node.value)
                current_node = current_node.next
        return values_list
    
    def get_all_key_value_pairs(self) -> List[Tuple[Any, Any]]:
        """
        Trả về một danh sách tất cả các cặp (key, value) trong bảng băm.
        """
        pairs_list: List[Tuple[Any, Any]] = []
        for bucket_head in self.buckets:
            current_node = bucket_head
            while current_node:
                pairs_list.append((current_node.key, current_node.value))
                current_node = current_node.next
        return pairs_list

    def __len__(self) -> int:
        return self.count

    def is_empty(self) -> bool:
        return self.count == 0

    def __str__(self) -> str:
        elements_str = []
        for i, bucket_head in enumerate(self.buckets):
            if bucket_head:
                bucket_elements = []
                current_node = bucket_head
                while current_node:
                    bucket_elements.append(str(current_node))
                    current_node = current_node.next
                elements_str.append(f"  Bucket {i}: {' -> '.join(bucket_elements)}")
        if not elements_str:
            return "CustomHashTable: (empty)"
        return "CustomHashTable:\n" + "\n".join(elements_str)

# --- Phần MaxHeap và PriorityQueue ---
class MaxHeap:
    def __init__(self):
        self.harr: List['PatientInQueue'] = [] 
        self.n = 0

    def _parent(self, i: int) -> int:
        return (i - 1) // 2

    def _left_child(self, i: int) -> int:
        return 2 * i + 1

    def _right_child(self, i: int) -> int:
        return 2 * i + 2

    def _swap(self, i: int, j: int):
        self.harr[i], self.harr[j] = self.harr[j], self.harr[i]

    def _heapify_up(self, i: int):
        while i > 0 and self.harr[i] > self.harr[self._parent(i)]: 
            self._swap(i, self._parent(i))
            i = self._parent(i)

    def _heapify_down(self, i: int):
        max_index = i
        l = self._left_child(i)
        if l < self.n and self.harr[l] > self.harr[max_index]:
            max_index = l
        
        r = self._right_child(i)
        if r < self.n and self.harr[r] > self.harr[max_index]:
            max_index = r
        
        if i != max_index:
            self._swap(i, max_index)
            self._heapify_down(max_index)

    def add(self, x: 'PatientInQueue'): 
        self.harr.append(x)
        self.n += 1
        self._heapify_up(self.n - 1)

    def getMax(self) -> Optional['PatientInQueue']: 
        if self.n == 0:
            return None
        return self.harr[0]

    def removeMax(self) -> Optional['PatientInQueue']: 
        if self.n == 0:
            return None
        
        root = self.harr[0]
        if self.n > 1:
            self.harr[0] = self.harr[self.n - 1]
            self.harr.pop()
            self.n -= 1 
            self._heapify_down(0) 
        elif self.n == 1: 
            self.harr.pop()
            self.n -= 1
        return root

    def is_empty(self) -> bool:
        return self.n == 0

    def get_all_elements(self) -> List['PatientInQueue']:
        return list(self.harr)

    def changePriority(self, patientID_to_change: str, new_priority_str: str, PatientInQueue_class_ref) -> bool: # Thêm PatientInQueue_class_ref
        found_index = -1
        for i in range(self.n):
            if self.harr[i].patientID == patientID_to_change:
                found_index = i
                break
        
        if found_index != -1:
            old_priority_numeric = self.harr[found_index].priority
            # Sử dụng PatientInQueue_class_ref để truy cập PRIORITY_MAP
            new_priority_numeric = PatientInQueue_class_ref.PRIORITY_MAP.get(new_priority_str)
            
            if new_priority_numeric is None:
                # print(f"Lỗi Heap: Mức ưu tiên mới '{new_priority_str}' không hợp lệ.") # app_logic sẽ xử lý log
                return False

            self.harr[found_index].priority = new_priority_numeric
            
            if new_priority_numeric > old_priority_numeric:
                self._heapify_up(found_index)
            else: # new_priority_numeric <= old_priority_numeric
                self._heapify_down(found_index)
            return True
        return False

class PriorityQueue: 
    def __init__(self):
        self.k: MaxHeap = MaxHeap()

    @property
    def Size(self) -> int: 
        return self.k.n

    def getFirst(self) -> Optional['PatientInQueue']: 
        return self.k.getMax()

    def removeFirst(self) -> Optional['PatientInQueue']: 
        return self.k.removeMax()

    def add(self, x: 'PatientInQueue'): 
        self.k.add(x)

    def is_empty(self) -> bool:
        return self.k.is_empty()

    def updatePriorityForLongWaiters(self, max_wait_time_seconds: int, PatientInQueue_class_ref, priority_increase: int = 1) -> int:
        now = datetime.datetime.now()
        updated_count = 0
        indices_to_reheapify = []

        for idx, patient_in_q in enumerate(self.k.harr): 
            wait_time = (now - patient_in_q.registrationTime).total_seconds()
            if wait_time > max_wait_time_seconds:
                max_priority_numeric = max(PatientInQueue_class_ref.PRIORITY_MAP.values())
                if patient_in_q.priority < max_priority_numeric:
                    old_priority_val = patient_in_q.priority
                    new_priority_val = min(patient_in_q.priority + priority_increase, max_priority_numeric)
                    if new_priority_val != old_priority_val:
                        patient_in_q.priority = new_priority_val 
                        indices_to_reheapify.append(idx) 
                        updated_count +=1
        
        for idx_to_fix in sorted(indices_to_reheapify, reverse=True): 
             self.k._heapify_up(idx_to_fix) 
        
        return updated_count

    def display_queue(self, PatientInQueue_class_ref) -> List[str]: 
        if self.k.is_empty():
            return ["Hàng đợi rỗng."]
        temp_heap = MaxHeap()
        for item_orig in self.k.get_all_elements(): 
            profile_ref = item_orig.profile 
            copied_patient_in_q = PatientInQueue_class_ref( # Sử dụng PatientInQueue_class_ref
                patient_profile=profile_ref, 
                priority_str=item_orig.get_priority_display(), 
                registration_time=item_orig.registrationTime 
            )
            copied_patient_in_q.priority = item_orig.priority 
            copied_patient_in_q.absentCount = item_orig.absentCount
            temp_heap.add(copied_patient_in_q)

        sorted_list_display_strings: List[str] = []
        stt = 1
        while not temp_heap.is_empty():
            p = temp_heap.removeMax()
            if p:
                display_str = (f"{stt}. ID:{p.patientID},Tên:{p.profile.ho_ten},"
                               f"Ưu tiên:{p.get_priority_display()}({p.priority}),"
                               f"TGĐK:{p.registrationTime.strftime('%H:%M:%S')},"
                               f"Vắng:{p.absentCount}") # Thay đổi dấu phẩy cho dễ parse ở GUI
                sorted_list_display_strings.append(display_str)
                stt += 1
        return sorted_list_display_strings
        
    def thay_doi_uu_tien_benh_nhan(self, patient_id: str, new_priority_str: str, PatientInQueue_class_ref) -> bool:
        return self.k.changePriority(patient_id, new_priority_str, PatientInQueue_class_ref)
