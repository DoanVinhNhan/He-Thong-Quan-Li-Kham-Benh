# HỆ THỐNG QUẢN LÝ KHÁM BỆNH

Bài tập Lớn môn Cấu trúc Dữ liệu và Giải thuật - Đại học Bách Khoa Hà Nội.
Phiên bản: 1.1 (Cập nhật ngày 30/05/2025)

1. Yêu cầu về môi trường:
   - Python 3.7+
   - Thư viện customtkinter: Cài đặt bằng lệnh `pip install customtkinter`
   (Không yêu cầu thư viện bên ngoài nào khác cho logic cốt lõi).

2. Cách chạy chương trình:
   - Đảm bảo tất cả các file mã nguồn (.py) nằm trong cùng một thư mục.
   - Mở terminal (hoặc Command Prompt).
   - Di chuyển (cd) vào thư mục chứa mã nguồn của dự án.
   - Chạy file giao diện chính: `python main_gui.py`
   - File dữ liệu `patients_data.csv` sẽ được tự động tạo/đọc trong cùng thư mục khi chương trình khởi chạy và thực hiện các thao tác lưu trữ hồ sơ.

3. Mô tả tổng quan:
   Chương trình mô phỏng hệ thống quản lý bệnh nhân và hàng đợi khám bệnh ưu tiên tại một cơ sở y tế. Các chức năng chính bao gồm:
   - Quản lý hồ sơ bệnh nhân: Thêm mới, cập nhật, xóa, tìm kiếm thông tin. Dữ liệu hồ sơ được lưu trữ lâu dài trong file `patients_data.csv`. Số CCCD là trường thông tin bắt buộc.
   - Đăng ký khám: Thêm bệnh nhân vào hàng đợi với các mức độ ưu tiên khác nhau (Cấp cứu, Ưu tiên cao, Thông thường, Tái khám,...).
   - Hàng đợi khám: Sử dụng hàng đợi ưu tiên (triển khai bằng MaxHeap tùy chỉnh) để sắp xếp bệnh nhân. Bệnh nhân ưu tiên cao hơn và đến sớm hơn (nếu cùng ưu tiên) sẽ được khám trước.
   - Xử lý khám: Gọi bệnh nhân kế tiếp, cập nhật trạng thái sau khám, xử lý bệnh nhân vắng mặt khi được gọi (bệnh nhân đang được gọi), xử lý bệnh nhân tự ý rời hàng đợi.
   - Tính năng khác: Tăng ưu tiên tự động cho bệnh nhân trong hàng đợi nếu họ phải chờ quá một khoảng thời gian nhất định.

4. Cấu trúc mã nguồn:
   - `main_gui.py`: File chính chạy giao diện người dùng (GUI) của ứng dụng, sử dụng customtkinter.
   - `app_logic.py`: Chứa logic nghiệp vụ của ứng dụng, điều phối các hoạt động và tương tác với cấu trúc dữ liệu.
   - `models.py`: Định nghĩa các lớp đối tượng dữ liệu chính là `BenhNhan` (Hồ sơ bệnh nhân) và `PatientInQueue` (Bệnh nhân trong hàng đợi).
   - `custom_structures.py`: Chứa cài đặt các cấu trúc dữ liệu tùy chỉnh được yêu cầu bởi đề bài, bao gồm:
        - `CustomLinkedList`: Danh sách liên kết đơn tùy chỉnh.
        - `CustomHashTable`: Bảng băm tùy chỉnh (sử dụng phương pháp nối chuỗi).
        - `MaxHeap`: Cấu trúc Max Heap tùy chỉnh (dùng cho hàng đợi ưu tiên).
        - `PriorityQueue`: Hàng đợi ưu tiên tùy chỉnh (sử dụng MaxHeap).

5. Thông tin nhóm sinh viên:
   - Đặng Thị Thuỳ Dương - 20237318
   - Nguyễn Thị Huệ     - 20237439
   - Đoàn Vĩnh Nhân     - 20237376
