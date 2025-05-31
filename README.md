# HỆ THỐNG QUẢN LÝ KHÁM BỆNH ĐA KHOA

Dự án môn Cấu trúc Dữ liệu và Giải thuật - Đại học Bách Khoa Hà Nội.
Phiên bản: 1.2 (Cập nhật ngày 31/05/2025 - Thêm Quản lý Bác sĩ, Phòng khám, Đa hàng đợi)

1. Yêu cầu về môi trường:
   - Python 3.7+
   - Thư viện customtkinter: Cài đặt bằng lệnh `python3 -m pip install -r requirements.txt`
   (Không yêu cầu thư viện bên ngoài nào khác cho logic cốt lõi của chương trình).

2. Cách chạy chương trình:
   - Đảm bảo tất cả các file mã nguồn Python (.py) sau đây nằm trong cùng một thư mục:
     - `main_gui.py`
     - `app_logic.py`
     - `models.py`
     - custom_structures.py
   - Mở terminal (hoặc Command Prompt).
   - Di chuyển (cd) vào thư mục chứa các file mã nguồn trên.
   - Chạy lệnh `python3 -m pip install -r requirements.txt` để cài đặt thư viện thực hiện.
   - Chạy file giao diện chính bằng lệnh: `python main_gui.py`
   - Các file dữ liệu CSV sau sẽ được tự động tạo/đọc trong cùng thư mục khi chương trình khởi chạy và thực hiện các thao tác lưu trữ:
     - `patients_data.csv` (Hồ sơ bệnh nhân)
     - `doctors_data.csv` (Thông tin bác sĩ)
     - `clinics_data.csv` (Thông tin phòng khám)

3. Mô tả tổng quan:
   Chương trình mô phỏng hệ thống quản lý hoạt động khám bệnh tại một cơ sở y tế đa khoa, bao gồm các chức năng chính:

   * **Quản lý Hồ sơ Bệnh nhân:**
       * Thêm mới, cập nhật, xóa, tìm kiếm thông tin chi tiết của bệnh nhân.
       * Số CCCD là trường thông tin bắt buộc và duy nhất.
       * Lưu trữ lịch sử các lần khám bệnh của bệnh nhân (bao gồm thông tin về bác sĩ và phòng khám thực hiện).
       * Toàn bộ hồ sơ bệnh nhân được lưu trữ bền vững vào file `patients_data.csv`.

   * **Quản lý Bác sĩ:**
       * Thêm mới, cập nhật, xóa thông tin bác sĩ (Mã BS, Họ tên, Chuyên khoa).
       * Lưu trữ thông tin bác sĩ vào file `doctors_data.csv`.

   * **Quản lý Phòng khám:**
       * Thêm mới, cập nhật, xóa thông tin phòng khám (Mã PK, Tên PK, Chuyên khoa PK).
       * Quản lý danh sách các bác sĩ làm việc tại mỗi phòng khám.
       * Lưu trữ thông tin phòng khám vào file `clinics_data.csv`.

   * **Đăng ký Khám Bệnh:**
       * Cho phép đăng ký bệnh nhân vào hàng đợi của một phòng khám cụ thể.
       * Gán mức độ ưu tiên cho bệnh nhân khi đăng ký (Cấp cứu, Ưu tiên cao, Thông thường, Tái khám,...).
       * Kiểm tra và ngăn không cho một bệnh nhân đăng ký khám nếu họ đã có mặt trong một hàng đợi bất kỳ của hệ thống.

   * **Quản lý Hàng đợi Khám theo từng Phòng khám:**
       * Hệ thống quản lý nhiều hàng đợi ưu tiên riêng biệt, mỗi hàng đợi tương ứng với một phòng khám.
       * Người dùng có thể chọn phòng khám để xem và thao tác với hàng đợi tương ứng.
       * Bệnh nhân trong mỗi hàng đợi được sắp xếp dựa trên mức độ ưu tiên (cao nhất được phục vụ trước) và thời gian đăng ký (đến sớm phục vụ trước nếu cùng ưu tiên).
       * Gọi bệnh nhân kế tiếp từ hàng đợi của phòng khám đã chọn.
       * Xử lý trường hợp bệnh nhân được gọi nhưng vắng mặt: Bệnh nhân sẽ được ghi nhận số lần vắng, giảm ưu tiên và đưa lại vào hàng đợi của phòng khám đó (nếu chưa vắng đủ 3 lần).
       * Xử lý trường hợp bệnh nhân tự ý rời khỏi hàng đợi của một phòng khám.
       * Cho phép nhân viên y tế thay đổi mức độ ưu tiên của một bệnh nhân cụ thể đang chờ trong hàng đợi của một phòng khám.
       * Tự động tăng ưu tiên cho bệnh nhân nếu thời gian chờ trong hàng đợi của một phòng khám vượt quá ngưỡng quy định.

   * **Hoàn thành Khám và Lịch sử:**
       * Ghi nhận kết quả khám, ghi chú, thông tin bác sĩ và phòng khám đã thực hiện khám vào lịch sử của bệnh nhân.
       * Hiển thị danh sách các bệnh nhân đã được hoàn thành khám trong phiên làm việc hiện tại.

4. Cấu trúc mã nguồn:
   - `main_gui.py`: File chính chạy giao diện người dùng (GUI) của ứng dụng, sử dụng thư viện CustomTkinter.
   - `app_logic.py`: Chứa lớp `HeThongQuanLyKhamBenh` với logic nghiệp vụ chính, điều phối các hoạt động và tương tác với các cấu trúc dữ liệu và file CSV.
   - `models.py`: Định nghĩa các lớp đối tượng dữ liệu: `BenhNhan`, `PatientInQueue`, `BacSi`, `PhongKham`.
   - `custom_structures.py`: Chứa mã nguồn cài đặt tùy chỉnh cho các cấu trúc dữ liệu cốt lõi:
        - `CustomLinkedList`: Danh sách liên kết đơn.
        - `CustomHashTable`: Bảng băm (sử dụng phương pháp nối chuỗi).
        - `CustomMaxHeap`: Cấu trúc Max Heap.
        - `CustomPriorityQueue`: Hàng đợi ưu tiên (sử dụng MaxHeap).

5. Thông tin nhóm sinh viên:
   - Đặng Thị Thuỳ Dương - 20237318
   - Nguyễn Thị Huệ     - 20237439
   - Đoàn Vĩnh Nhân     - 20237376

Lưu ý quan trọng:
Theo yêu cầu của đồ án, tất cả các cấu trúc dữ liệu cốt lõi (Bảng Băm, Hàng Đợi Ưu Tiên/Heap, Danh Sách Liên Kết) được nhóm tự xây dựng và cài đặt, không sử dụng các thư viện hay cấu trúc có sẵn của Python cho các thành phần này (ví dụ: không dùng `dict` cho bảng băm, `list` cho danh sách liên kết, module `heapq` cho heap/hàng đợi ưu tiên). Module `csv` của Python được sử dụng cho tiện ích đọc/ghi file định dạng CSV.
