# custom_structures.py
import datetime

# --- Cấu trúc List (Danh sách tùy chỉnh dựa trên mảng động) ---
class List:
    """Mảng động tùy chỉnh, tự thay đổi kích thước."""
    def __init__(self, initial_capacity=10):
        self._capacity = initial_capacity
        self._size = 0
        self._elements = [None] * self._capacity

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def _resize(self, new_capacity):
        # Thay đổi kích thước mảng nội bộ.
        new_elements = [None] * new_capacity
        for i in range(self._size):
            new_elements[i] = self._elements[i]
        self._elements = new_elements
        self._capacity = new_capacity

    def append(self, item):
        # Thêm phần tử vào cuối.
        if self._size == self._capacity:
            self._resize(2 * self._capacity if self._capacity > 0 else 1)
        self._elements[self._size] = item
        self._size += 1

    def get(self, index):
        # Lấy phần tử tại chỉ mục.
        if not (0 <= index < self._size):
            raise IndexError("List: Chỉ mục ngoài phạm vi")
        return self._elements[index]

    def set(self, index, item):
        # Đặt giá trị phần tử tại chỉ mục.
        if not (0 <= index < self._size):
            raise IndexError("List: Chỉ mục ngoài phạm vi để đặt giá trị")
        self._elements[index] = item

    def insert(self, index, item):
        # Chèn phần tử vào chỉ mục.
        if not (0 <= index <= self._size):
            raise IndexError("List: Chỉ mục chèn ngoài phạm vi")
        if self._size == self._capacity:
            self._resize(2 * self._capacity if self._capacity > 0 else 1)
        for i in range(self._size, index, -1):
            self._elements[i] = self._elements[i-1]
        self._elements[index] = item
        self._size += 1

    def pop(self, index=-1):
        # Xóa và trả về phần tử tại chỉ mục (mặc định cuối).
        if self.is_empty():
            raise IndexError("List: Pop từ danh sách rỗng")
        actual_index = index
        if index == -1:
            actual_index = self._size - 1
        if not (0 <= actual_index < self._size):
            raise IndexError("List: Chỉ mục pop ngoài phạm vi")
        item = self._elements[actual_index]
        for i in range(actual_index, self._size - 1):
            self._elements[i] = self._elements[i+1]
        self._size -= 1
        self._elements[self._size] = None
        if self._size < self._capacity // 4 and self._capacity > 10:
            self._resize(self._capacity // 2)
        return item

    def __iter__(self):
        # Iterator cho danh sách.
        for i in range(self._size):
            yield self._elements[i]

    def __str__(self):
        if self.is_empty(): return "List:[]"
        items_str_list = []
        for i in range(self._size): items_str_list.append(str(self._elements[i]))
        return "List:[" + ", ".join(items_str_list) + "]"

# --- LinkedList (Danh sách liên kết đơn) ---
class ListNode:
    """Nút trong danh sách liên kết."""
    def __init__(self, value):
        self.value = value
        self.next_node = None
    def __str__(self): return str(self.value)

class LinkedList:
    """Danh sách liên kết đơn."""
    def __init__(self):
        self.head_node = None
        self.tail_node = None
        self._list_size = 0
    def append(self, value):
        # Thêm vào cuối danh sách.
        new_node = ListNode(value)
        if not self.head_node:
            self.head_node = new_node
            self.tail_node = new_node
        else:
            if self.tail_node: self.tail_node.next_node = new_node
            self.tail_node = new_node
        self._list_size += 1
    def __len__(self): return self._list_size
    def is_empty(self): return self._list_size == 0
    def __iter__(self):
        # Iterator cho danh sách liên kết.
        current = self.head_node
        while current: yield current.value; current = current.next_node
    def get_all_elements_as_list(self):
        # Lấy tất cả phần tử dưới dạng List tùy chỉnh.
        elements_array = List()
        for item in self: elements_array.append(item)
        return elements_array
    def get(self, index):
        # Lấy phần tử tại chỉ mục.
        if not (0 <= index < self._list_size): raise IndexError("LinkedList: Chỉ mục ngoài phạm vi")
        current = self.head_node
        for _ in range(index):
            if current: current = current.next_node
            else: raise IndexError("LinkedList: Lỗi logic duyệt")
        if current: return current.value
        raise IndexError("LinkedList: Không tìm thấy phần tử")
    def get_last(self):
        # Lấy phần tử cuối.
        return self.tail_node.value if self.tail_node else None
    def __str__(self):
        elements_str_list_py = [str(item) for item in self]
        return "LinkedList:[" + " -> ".join(elements_str_list_py) + "]" if not self.is_empty() else "LinkedList:(empty)"

# --- HashTable (Bảng băm với giải quyết xung đột bằng chaining) ---
class HashNode:
    """Nút trong bucket của bảng băm."""
    def __init__(self, key, value):
        self.key = key; self.value = value; self.next_node = None
    def __str__(self): return f"({self.key}: {self.value})"

class HashTable: # Đổi tên từ CustomHashTable
    """Bảng băm, giải quyết xung đột bằng chaining."""
    def __init__(self, initial_table_size=100):
        if initial_table_size <= 0: raise ValueError("Kích thước bảng băm phải dương.")
        self.table_size = initial_table_size
        self.buckets_array = List(self.table_size) # Mảng các bucket
        for i in range(self.table_size): self.buckets_array.append(None)
        self.item_count = 0

    def _calculate_hash_index(self, key):
        # Tính chỉ mục bucket cho khóa.
        if isinstance(key, str): hash_val = sum(ord(char) for char in key)
        elif isinstance(key, int): hash_val = key
        else: hash_val = hash(key)
        return hash_val % self.table_size

    def put_item(self, key, value):
        # Thêm/cập nhật cặp key-value.
        index = self._calculate_hash_index(key)
        current_hash_node = self.buckets_array.get(index)
        while current_hash_node:
            if current_hash_node.key == key: current_hash_node.value = value; return
            current_hash_node = current_hash_node.next_node
        new_hash_node = HashNode(key, value)
        new_hash_node.next_node = self.buckets_array.get(index)
        self.buckets_array.set(index, new_hash_node)
        self.item_count += 1

    def get_item(self, key):
        # Lấy giá trị theo khóa.
        index = self._calculate_hash_index(key)
        current_hash_node = self.buckets_array.get(index)
        while current_hash_node:
            if current_hash_node.key == key: return current_hash_node.value
            current_hash_node = current_hash_node.next_node
        return None

    def delete_item(self, key):
        # Xóa cặp key-value theo khóa.
        index = self._calculate_hash_index(key)
        current_hash_node = self.buckets_array.get(index); prev_hash_node = None
        while current_hash_node:
            if current_hash_node.key == key:
                if prev_hash_node: prev_hash_node.next_node = current_hash_node.next_node
                else: self.buckets_array.set(index, current_hash_node.next_node)
                self.item_count -= 1; return True
            prev_hash_node = current_hash_node; current_hash_node = current_hash_node.next_node
        return False

    def contains_key(self, key):
        # Kiểm tra khóa tồn tại.
        return self.get_item(key) is not None

    def get_all_values_as_list(self):
        # Lấy tất cả giá trị dạng List tùy chỉnh.
        values_custom_list = List()
        for i in range(self.table_size):
            current_hash_node = self.buckets_array.get(i)
            while current_hash_node: values_custom_list.append(current_hash_node.value); current_hash_node = current_hash_node.next_node
        return values_custom_list

    def get_all_key_value_pairs_as_list(self):
        # Lấy tất cả cặp key-value dạng List tùy chỉnh các tuple.
        pairs_custom_list = List()
        for i in range(self.table_size):
            current_hash_node = self.buckets_array.get(i)
            while current_hash_node: pairs_custom_list.append((current_hash_node.key, current_hash_node.value)); current_hash_node = current_hash_node.next_node
        return pairs_custom_list

    def __len__(self): return self.item_count
    def is_empty(self): return self.item_count == 0

# --- MaxHeap (Đống cực đại) & CustomPriorityQueue (Hàng đợi ưu tiên tùy chỉnh) ---
class MaxHeap:
    """Đống Cực Đại (Max Heap). Phần tử lớn nhất ở gốc."""
    def __init__(self): self.heap_array = List(); # Dùng List tùy chỉnh
    def _get_parent_index(self, i): return (i - 1) // 2
    def _get_left_child_index(self, i): return 2 * i + 1
    def _get_right_child_index(self, i): return 2 * i + 2
    def _swap_elements(self, i, j):
        # Hoán đổi phần tử.
        item_i = self.heap_array.get(i); item_j = self.heap_array.get(j)
        self.heap_array.set(i, item_j); self.heap_array.set(j, item_i)
    def _sift_up(self, i):
        # Di chuyển phần tử lên để duy trì thuộc tính max-heap.
        parent_index = self._get_parent_index(i)
        while i > 0 and self.heap_array.get(i) > self.heap_array.get(parent_index):
            self._swap_elements(i, parent_index); i = parent_index
            parent_index = self._get_parent_index(i)
    def _sift_down(self, i):
        # Di chuyển phần tử xuống để duy trì thuộc tính max-heap.
        current_size = len(self.heap_array)
        max_idx = i
        left_idx = self._get_left_child_index(i); right_idx = self._get_right_child_index(i)
        if left_idx < current_size and self.heap_array.get(left_idx) > self.heap_array.get(max_idx): max_idx = left_idx
        if right_idx < current_size and self.heap_array.get(right_idx) > self.heap_array.get(max_idx): max_idx = right_idx
        if i != max_idx: self._swap_elements(i, max_idx); self._sift_down(max_idx)
    def add_item(self, item):
        # Thêm phần tử vào heap.
        self.heap_array.append(item); self._sift_up(len(self.heap_array) - 1)
    def get_max_item(self):
        # Lấy phần tử lớn nhất (không xóa).
        return self.heap_array.get(0) if not self.is_empty() else None
    def remove_max_item(self):
        # Xóa và trả về phần tử lớn nhất.
        if self.is_empty(): return None
        root = self.heap_array.get(0)
        if len(self.heap_array) > 1:
            last_item = self.heap_array.pop()
            self.heap_array.set(0, last_item); self._sift_down(0)
        elif len(self.heap_array) == 1: self.heap_array.pop()
        return root
    def is_empty(self): return len(self.heap_array) == 0
    def get_all_heap_elements(self): return self.heap_array # Trả về List các phần tử heap.
    def change_item_priority(self, item_id_to_change, new_priority_str, patient_in_queue_class_ref):
        # Thay đổi độ ưu tiên của mục trong heap (cho PatientInQueue).
        found_idx = -1
        for i in range(len(self.heap_array)):
            if self.heap_array.get(i).patient_id == item_id_to_change: found_idx = i; break
        if found_idx != -1:
            patient_obj = self.heap_array.get(found_idx)
            old_numeric_priority = patient_obj.priority
            new_numeric_priority = patient_in_queue_class_ref.PRIORITY_MAP.get(new_priority_str)
            if new_numeric_priority is None: return False
            patient_obj.priority = new_numeric_priority
            if new_numeric_priority > old_numeric_priority: self._sift_up(found_idx)
            else: self._sift_down(found_idx)
            return True
        return False

# --- Cấu trúc PriorityQueue (Hàng đợi ưu tiên dựa trên MaxHeap) ---
class CustomPriorityQueue:
    """Hàng đợi ưu tiên, dùng MaxHeap. Phần tử ưu tiên cao nhất (số lớn) ra trước."""
    def __init__(self): self.internal_heap = MaxHeap()
    @property
    def current_size(self): return len(self.internal_heap.heap_array)
    def get_first_item(self): return self.internal_heap.get_max_item() # Lấy phần tử ưu tiên nhất (không xóa).
    def remove_first_item(self): return self.internal_heap.remove_max_item() # Xóa và trả về phần tử ưu tiên nhất.
    def add_item(self, item): self.internal_heap.add_item(item) # Thêm phần tử.
    def is_empty(self): return self.internal_heap.is_empty()
    def update_long_waiter_priority(self, max_wait_time_seconds, patient_in_queue_class_ref, priority_increase=1):
        # Tăng ưu tiên cho bệnh nhân chờ lâu.
        now = datetime.datetime.now(); updated_items_count = 0; indices_to_re_sift = []
        for idx in range(len(self.internal_heap.heap_array)):
            patient_item = self.internal_heap.heap_array.get(idx)
            if (now - patient_item.registration_time).total_seconds() > max_wait_time_seconds:
                max_numeric_prio = max(patient_in_queue_class_ref.PRIORITY_MAP.values())
                if patient_item.priority < max_numeric_prio:
                    old_prio = patient_item.priority; new_prio = min(patient_item.priority + priority_increase, max_numeric_prio)
                    if new_prio != old_prio: patient_item.priority = new_prio; indices_to_re_sift.append(idx); updated_items_count +=1
        for idx_to_fix in sorted(indices_to_re_sift, reverse=True): self.internal_heap._sift_up(idx_to_fix)
        return updated_items_count
    def get_display_queue_as_strings(self, patient_in_queue_class_ref):
        # Lấy danh sách chuỗi hiển thị hàng đợi (sắp xếp ưu tiên).
        display_str_list = List()
        if self.internal_heap.is_empty(): display_str_list.append("Hàng đợi rỗng."); return display_str_list
        temp_display_heap = MaxHeap() # Heap tạm để không thay đổi heap gốc
        for item_original in self.internal_heap.get_all_heap_elements():
            profile_copy = item_original.patient_profile
            patient_copy = patient_in_queue_class_ref(profile_copy, item_original.get_priority_display_name(), item_original.registration_time)
            patient_copy.priority = item_original.priority; patient_copy.absent_count = item_original.absent_count
            temp_display_heap.add_item(patient_copy)
        item_number = 1
        while not temp_display_heap.is_empty():
            p_item = temp_display_heap.remove_max_item()
            if p_item: display_str_list.append(f"{item_number}. ID:{p_item.patient_id},Tên:{p_item.patient_profile.full_name},Ưu tiên:{p_item.get_priority_display_name()}({p_item.priority}),TGĐK:{p_item.registration_time.strftime('%H:%M:%S')},Vắng:{p_item.absent_count}"); item_number+=1
        return display_str_list
    def change_queued_patient_priority(self, patient_id, new_priority_str, patient_in_queue_class_ref):
        # Thay đổi ưu tiên của bệnh nhân trong hàng đợi.
        return self.internal_heap.change_item_priority(patient_id, new_priority_str, patient_in_queue_class_ref)

# --- Cấu trúc Radix Tree (Cây cơ số hay Patricia Trie) ---
class RadixTreeNode:
    """Nút trong Cây Cơ số (Radix Tree)."""
    def __init__(self):
        self.children = HashTable(initial_table_size=10) # Con là HashTable, key: ký tự, value: RadixTreeNode
        self.is_end_of_key = False # Đánh dấu kết thúc của một khóa
        self.value = None # Giá trị liên kết với khóa (thường là patient_id)

    def __str__(self):
        return f"Node(end={self.is_end_of_key}, val={self.value}, children_count={len(self.children)})"

class RadixTree:
    """Cây Cơ số (Radix Tree/Patricia Trie) để tìm kiếm chuỗi nhanh."""
    def __init__(self):
        self.root = RadixTreeNode() # Nút gốc

    def insert(self, key_str, value):
        """Chèn cặp khóa-giá trị (chuỗi) vào cây."""
        if not isinstance(key_str, str):
            return

        current_node = self.root
        for char_code in key_str:
            char_as_str = str(char_code)
            if not current_node.children.contains_key(char_as_str):
                current_node.children.put_item(char_as_str, RadixTreeNode())
            current_node = current_node.children.get_item(char_as_str)
        current_node.is_end_of_key = True
        current_node.value = value

    def search(self, key_str):
        """Tìm kiếm khóa chuỗi. Trả về giá trị nếu tìm thấy, ngược lại None."""
        if not isinstance(key_str, str):
            return None

        current_node = self.root
        for char_code in key_str:
            char_as_str = str(char_code)
            if not current_node.children.contains_key(char_as_str):
                return None
            current_node = current_node.children.get_item(char_as_str)

        if current_node is not None and current_node.is_end_of_key:
            return current_node.value
        return None

    def delete(self, key_str):
        """Xóa khóa khỏi cây (phiên bản đơn giản)."""
        if not isinstance(key_str, str):
            return False

        node_stack_for_cleanup = List() # Dùng để dọn dẹp nút

        current_node = self.root
        for char_code in key_str:
            char_as_str = str(char_code)
            if not current_node.children.contains_key(char_as_str):
                return False
            node_stack_for_cleanup.append({'parent': current_node, 'char': char_as_str, 'child': current_node.children.get_item(char_as_str)})
            current_node = current_node.children.get_item(char_as_str)

        if not current_node.is_end_of_key:
            return False # Khóa không tồn tại đầy đủ

        current_node.is_end_of_key = False # Bỏ đánh dấu
        current_node.value = None # Xóa giá trị

        # Dọn dẹp các nút không cần thiết từ dưới lên
        for i in range(len(node_stack_for_cleanup) -1, -1, -1):
            item = node_stack_for_cleanup.get(i)
            parent_node, char_key, child_node = item['parent'], item['char'], item['child']

            if len(child_node.children) == 0 and not child_node.is_end_of_key: # Nút lá không cần thiết
                parent_node.children.delete_item(char_key)
            else:
                break # Dừng nếu nút vẫn cần thiết
        return True
