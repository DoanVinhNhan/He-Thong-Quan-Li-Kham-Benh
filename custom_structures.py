# custom_structures.py
import datetime 

# --- Cấu trúc List (Mảng động tùy chỉnh) ---
class List: 
    def __init__(self, initial_capacity=10):
        self._capacity = initial_capacity
        self._size = 0
        self._elements = [None] * self._capacity 

    def __len__(self):
        return self._size

    def is_empty(self):
        return self._size == 0

    def _resize(self, new_capacity):
        new_elements = [None] * new_capacity
        for i in range(self._size):
            new_elements[i] = self._elements[i]
        self._elements = new_elements
        self._capacity = new_capacity

    def append(self, item):
        if self._size == self._capacity:
            self._resize(2 * self._capacity if self._capacity > 0 else 1) 
        self._elements[self._size] = item
        self._size += 1

    def get(self, index):
        if not (0 <= index < self._size):
            raise IndexError("List: Chỉ mục ngoài phạm vi")
        return self._elements[index]

    def set(self, index, item):
        if not (0 <= index < self._size): 
            raise IndexError("List: Chỉ mục ngoài phạm vi để đặt giá trị")
        self._elements[index] = item
        
    def insert(self, index, item):
        if not (0 <= index <= self._size): 
            raise IndexError("List: Chỉ mục chèn ngoài phạm vi")
        if self._size == self._capacity:
            self._resize(2 * self._capacity if self._capacity > 0 else 1)
        for i in range(self._size, index, -1):
            self._elements[i] = self._elements[i-1]
        self._elements[index] = item
        self._size += 1

    def pop(self, index=-1):
        if self.is_empty():
            raise IndexError("List: Pop từ danh sách rỗng")
        actual_index = index
        if index == -1: actual_index = self._size - 1
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
        for i in range(self._size):
            yield self._elements[i]
            
    def __str__(self):
        if self.is_empty(): return "List:[]"
        items_str_list = []
        for i in range(self._size): items_str_list.append(str(self._elements[i]))
        return "List:[" + ", ".join(items_str_list) + "]"

# --- LinkedList ---
class ListNode:
    def __init__(self, value):
        self.value = value; self.next_node = None 
    def __str__(self): return str(self.value)

class LinkedList: 
    def __init__(self):
        self.head_node = None; self.tail_node = None; self._list_size = 0 
    def append(self, value):
        new_node = ListNode(value)
        if not self.head_node: self.head_node = new_node; self.tail_node = new_node
        else:
            if self.tail_node: self.tail_node.next_node = new_node; self.tail_node = new_node
            else: self.head_node = new_node; self.tail_node = new_node 
        self._list_size += 1
    def __len__(self): return self._list_size
    def is_empty(self): return self._list_size == 0
    def __iter__(self):
        current = self.head_node
        while current: yield current.value; current = current.next_node
    def get_all_elements_as_list(self): 
        elements_array = List() 
        for item in self: elements_array.append(item)
        return elements_array
    def get(self, index):
        if not (0 <= index < self._list_size): raise IndexError("LinkedList: Chỉ mục ngoài phạm vi")
        current = self.head_node
        for _ in range(index):
            if current: current = current.next_node
            else: raise IndexError("LinkedList: Lỗi logic duyệt")
        if current: return current.value
        raise IndexError("LinkedList: Không tìm thấy phần tử")
    def get_last(self): return self.tail_node.value if self.tail_node else None
    def __str__(self):
        elements_str_list_py = [str(item) for item in self] 
        return "LinkedList:[" + " -> ".join(elements_str_list_py) + "]" if not self.is_empty() else "LinkedList:(empty)"

# --- HashTable ---
class HashNode:
    def __init__(self, key, value):
        self.key = key; self.value = value; self.next_node = None 
    def __str__(self): return f"({self.key}: {self.value})"

class HashTable: # Đổi tên từ CustomHashTable
    def __init__(self, initial_table_size=100): # Sử dụng initial_table_size
        if initial_table_size <= 0: raise ValueError("Kích thước bảng băm phải dương.")
        self.table_size = initial_table_size 
        self.buckets_array = List(self.table_size) 
        for i in range(self.table_size): self.buckets_array.append(None) 
        self.item_count = 0 

    def _calculate_hash_index(self, key): 
        if isinstance(key, str): hash_val = sum(ord(char) for char in key)
        elif isinstance(key, int): hash_val = key
        else: hash_val = hash(key)
        return hash_val % self.table_size

    def put_item(self, key, value): 
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
        index = self._calculate_hash_index(key)
        current_hash_node = self.buckets_array.get(index)
        while current_hash_node:
            if current_hash_node.key == key: return current_hash_node.value
            current_hash_node = current_hash_node.next_node
        return None

    def delete_item(self, key): 
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
        return self.get_item(key) is not None

    def get_all_values_as_list(self): # Trả về List (CustomArrayList)
        values_custom_list = List() 
        for i in range(self.table_size):
            current_hash_node = self.buckets_array.get(i)
            while current_hash_node: values_custom_list.append(current_hash_node.value); current_hash_node = current_hash_node.next_node
        return values_custom_list
    
    def get_all_key_value_pairs_as_list(self): # Trả về List (CustomArrayList) các tuple
        pairs_custom_list = List() 
        for i in range(self.table_size):
            current_hash_node = self.buckets_array.get(i)
            while current_hash_node: pairs_custom_list.append((current_hash_node.key, current_hash_node.value)); current_hash_node = current_hash_node.next_node
        return pairs_custom_list

    def __len__(self): return self.item_count
    def is_empty(self): return self.item_count == 0

# --- MaxHeap & CustomPriorityQueue ---
class MaxHeap:
    def __init__(self): self.heap_array = List(); 
    def _get_parent_index(self, i): return (i - 1) // 2 
    def _get_left_child_index(self, i): return 2 * i + 1 
    def _get_right_child_index(self, i): return 2 * i + 2 
    def _swap_elements(self, i, j): 
        item_i = self.heap_array.get(i); item_j = self.heap_array.get(j)
        self.heap_array.set(i, item_j); self.heap_array.set(j, item_i)
    def _sift_up(self, i): 
        parent_index = self._get_parent_index(i)
        while i > 0 and self.heap_array.get(i) > self.heap_array.get(parent_index): 
            self._swap_elements(i, parent_index); i = parent_index
            parent_index = self._get_parent_index(i)
    def _sift_down(self, i): 
        current_size = len(self.heap_array)
        max_idx = i
        left_idx = self._get_left_child_index(i); right_idx = self._get_right_child_index(i)
        if left_idx < current_size and self.heap_array.get(left_idx) > self.heap_array.get(max_idx): max_idx = left_idx
        if right_idx < current_size and self.heap_array.get(right_idx) > self.heap_array.get(max_idx): max_idx = right_idx
        if i != max_idx: self._swap_elements(i, max_idx); self._sift_down(max_idx)
    def add_item(self, item): self.heap_array.append(item); self._sift_up(len(self.heap_array) - 1) 
    def get_max_item(self): return self.heap_array.get(0) if not self.is_empty() else None 
    def remove_max_item(self): 
        if self.is_empty(): return None
        root = self.heap_array.get(0)
        if len(self.heap_array) > 1:
            last_item = self.heap_array.pop() 
            self.heap_array.set(0, last_item); self._sift_down(0) 
        elif len(self.heap_array) == 1: self.heap_array.pop()
        return root
    def is_empty(self): return len(self.heap_array) == 0
    def get_all_heap_elements(self): return self.heap_array 
    def change_item_priority(self, item_id_to_change, new_priority_str, patient_in_queue_class_ref): 
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

class CustomPriorityQueue: 
    def __init__(self): self.internal_heap = MaxHeap() 
    @property
    def current_size(self): return len(self.internal_heap.heap_array) 
    def get_first_item(self): return self.internal_heap.get_max_item() 
    def remove_first_item(self): return self.internal_heap.remove_max_item() 
    def add_item(self, item): self.internal_heap.add_item(item) 
    def is_empty(self): return self.internal_heap.is_empty()
    def update_long_waiter_priority(self, max_wait_time_seconds, patient_in_queue_class_ref, priority_increase=1): 
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
        display_str_list = List() 
        if self.internal_heap.is_empty(): display_str_list.append("Hàng đợi rỗng."); return display_str_list
        temp_display_heap = MaxHeap()
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
        return self.internal_heap.change_item_priority(patient_id, new_priority_str, patient_in_queue_class_ref)