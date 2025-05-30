# HỆ THỐNG QUẢN LÝ KHÁM BỆNH

Dự án môn Cấu trúc Dữ liệu và Giải thuật - Đại học Bách Khoa Hà Nội.

1. Yêu cầu về môi trường:
   - Python 3.7+
   - Thư viện customtkinter: Cài đặt bằng lệnh `pip install customtkinter`
   (Liệt kê các thư viện khác nếu có)

2. Cách chạy chương trình:
   - Mở terminal (hoặc Command Prompt).
   - Di chuyển (cd) vào thư mục chứa mã nguồn của dự án.
   - Chạy file giao diện chính: `python main_gui.py`

3. Mô tả tổng quan:
   Chương trình mô phỏng hệ thống quản lý bệnh nhân và hàng đợi khám bệnh ưu tiên tại một cơ sở y tế. Các chức năng chính bao gồm:
   - Quản lý hồ sơ bệnh nhân: Thêm mới, cập nhật, xóa, tìm kiếm thông tin.
   - Đăng ký khám: Thêm bệnh nhân vào hàng đợi với mức độ ưu tiên (Cấp cứu, Ưu tiên cao, Thông thường, Tái khám,...).
   - Hàng đợi khám: Sử dụng hàng đợi ưu tiên (MaxHeap) để sắp xếp bệnh nhân. Bệnh nhân ưu tiên cao hơn và đến sớm hơn (nếu cùng ưu tiên) sẽ được khám trước.
   - Xử lý khám: Gọi bệnh nhân, cập nhật trạng thái sau khám, xử lý vắng mặt, rời đi.
   - Tính năng khác: Tăng ưu tiên cho bệnh nhân chờ quá lâu.

4. Cấu trúc mã nguồn:
   - main_gui.py: Giao diện người dùng chính của ứng dụng.
   - app_logic.py: Logic nghiệp vụ, quản lý các thao tác chính.
   - models.py: Định nghĩa các lớp dữ liệu (BenhNhan, PatientInQueue).
   - custom_hash_table.py: Cài đặt cấu trúc Bảng Băm tùy chỉnh.
   - data_structures.py: Cài đặt MaxHeap, PriorityQueue (và CustomLinkedList nếu bạn đặt ở đây).
   - custom_linked_list.py: (Nếu bạn tạo file riêng) Cài đặt Danh sách liên kết tùy chỉnh.
   - (Các file/thư mục khác nếu có)

5. Thông tin nhóm sinh viên:
   - Đặng Thị Thuỳ Dương - 20237318
   - Nguyễn Thị Huệ     - 20237439
   - Đoàn Vĩnh Nhân     - 20237376

Lưu ý quan trọng:
Theo yêu cầu của đồ án, các cấu trúc dữ liệu cốt lõi như Bảng Băm (Hash Table), Hàng Đợi Ưu Tiên (Priority Queue dựa trên Max Heap), và Danh Sách Liên Kết (Linked List) được nhóm tự xây dựng và cài đặt, không sử dụng các thư viện hay cấu trúc có sẵn của Python cho các thành phần này.
