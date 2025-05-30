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
            if self.tail:
                self.tail.next = new_node
                self.tail = new_node
            else: 
                self.head = new_node 
                self.tail = new_node
        self._size += 1

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def __iter__(self) -> Iterable[Any]:
        current = self.head
        while current:
            yield current.value
            current = current.next

    def get_all_elements(self) -> List[Any]:
        return list(self)

    def get(self, index: int) -> Any:
        if not (0 <= index < self._size):
            raise IndexError("Chỉ mục ngoài phạm vi danh sách.")
        current = self.head
        for _ in range(index):
            if current:
                current = current.next
            else: 
                raise IndexError("Lỗi logic khi duyệt danh sách.")
        if current:
            return current.value
        raise IndexError("Không tìm thấy phần tử.")

    def get_last(self) -> Optional[Any]:
        if self.tail:
            return self.tail.value
        return None
        
    def __str__(self) -> str:
        elements = [str(item) for item in self]
        return "CustomLinkedList: [" + " -> ".join(elements) + "]" if elements else "CustomLinkedList: (empty)"

# --- Phần Custom Hash Table ---
class HashNode:
    """Nút trong danh sách liên kết của mỗi bucket trong bảng băm."""
    def __init__(self, key: Any, value: Any):
        self.key = key
        self.value = value
        self.next: Optional[HashNode] = None

    def __str__(self):
        return f"({self.key}: {self.value})"

class CustomHashTable:
    """Cấu trúc Bảng băm tùy chỉnh sử dụng phương pháp Nối chuỗi (Chaining)."""
    def __init__(self, initial_size: int = 100):
        if initial_size <= 0:
            raise ValueError("Kích thước bảng băm phải là số dương.")
        self.size: int = initial_size
        self.buckets: List[Optional[HashNode]] = [None] * self.size
        self.count: int = 0

    def _hash_function(self, key: Any) -> int:
        if isinstance(key, str):
            hash_val = sum(ord(char) for char in key)
        elif isinstance(key, int):
            hash_val = key
        else:
            hash_val = hash(key)
        return hash_val % self.size

    def put(self, key: Any, value: Any) -> None:
        index = self._hash_function(key)
        current_node = self.buckets[index]
        while current_node:
            if current_node.key == key:
                current_node.value = value 
                return
            current_node = current_node.next
        new_node = HashNode(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.count += 1

    def get(self, key: Any) -> Optional[Any]:
        index = self._hash_function(key)
        current_node = self.buckets[index]
        while current_node:
            if current_node.key == key:
                return current_node.value
            current_node = current_node.next
        return None

    def delete(self, key: Any) -> bool:
        index = self._hash_function(key)
        current_node = self.buckets[index]
        prev_node: Optional[HashNode] = None
        while current_node:
            if current_node.key == key:
                if prev_node:
                    prev_node.next = current_node.next
                else: 
                    self.buckets[index] = current_node.next
                self.count -= 1
                return True 
            prev_node = current_node
            current_node = current_node.next
        return False 

    def contains(self, key: Any) -> bool:
        return self.get(key) is not None

    def get_all_values(self) -> List[Any]:
        values_list: List[Any] = []
        for bucket_head in self.buckets:
            current_node = bucket_head
            while current_node:
                values_list.append(current_node.value)
                current_node = current_node.next
        return values_list
    
    def get_all_key_value_pairs(self) -> List[Tuple[Any, Any]]:
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
# Cần import PatientInQueue từ models, nhưng models lại import từ đây.
# Để tránh circular import, PatientInQueue sẽ được truyền như một type hint dưới dạng chuỗi
# hoặc các lớp này sẽ được sử dụng bởi app_logic nơi có cả hai.
# Trong thực tế, models.py nên được import ở đây nếu không có vấn đề circular.
# Giả sử models.py được import ở nơi sử dụng (app_logic.py).

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

    def updatePriorityForLongWaiters(self, max_wait_time_seconds: int, PatientInQueue_class, priority_increase: int = 1) -> int:
        # PatientInQueue_class được truyền vào để truy cập PRIORITY_MAP
        now = datetime.datetime.now()
        updated_count = 0
        indices_to_reheapify = []

        for idx, patient_in_q in enumerate(self.k.harr):
            wait_time = (now - patient_in_q.registrationTime).total_seconds()
            if wait_time > max_wait_time_seconds:
                max_priority_numeric = max(PatientInQueue_class.PRIORITY_MAP.values())
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

    def display_queue(self, PatientInQueue_class) -> List[str]:
        if self.k.is_empty():
            return ["Hàng đợi rỗng."]
        temp_heap = MaxHeap()
        for item_orig in self.k.get_all_elements():
            profile_ref = item_orig.profile 
            copied_patient_in_q = PatientInQueue_class(
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
                display_str = (f"{stt}. ID: {p.patientID}, Tên: {p.profile.ho_ten}, "
                               f"Ưu tiên: {p.get_priority_display()} ({p.priority}), "
                               f"TGĐK: {p.registrationTime.strftime('%H:%M:%S')}, "
                               f"Vắng: {p.absentCount}")
                sorted_list_display_strings.append(display_str)
                stt += 1
        return sorted_list_display_strings

    def is_empty(self) -> bool:
        return self.k.is_empty()