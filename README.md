# HỆ THỐNG QUẢN LÝ KHÁM BỆNH ĐA KHOA

Bài tập Lớn môn Cấu trúc Dữ liệu và Giải thuật - Đại học Bách Khoa Hà Nội.

## 1. Mô tả tổng quan
Chương trình mô phỏng hệ thống quản lý hoạt động khám bệnh tại một cơ sở y tế đa khoa, bao gồm các chức năng chính:
* **Quản lý Hồ sơ Bệnh nhân**: Thêm mới, cập nhật, xóa, tìm kiếm (bao gồm tìm kiếm nhanh theo SĐT/CCCD bằng Radix Tree). Lưu trữ lịch sử khám.
* **Quản lý Bác sĩ**: Thêm mới, cập nhật, xóa thông tin bác sĩ.
* **Quản lý Phòng khám**: Thêm mới, cập nhật, xóa thông tin phòng khám, quản lý danh sách bác sĩ.
* **Đăng ký Khám Bệnh**: Đăng ký bệnh nhân vào hàng đợi của phòng khám với mức độ ưu tiên.
* **Quản lý Hàng đợi Khám**: Theo từng phòng khám, sắp xếp theo ưu tiên và thời gian đăng ký. Xử lý gọi bệnh nhân, vắng mặt, rời hàng đợi, thay đổi ưu tiên.
* **Hoàn thành Khám và Lịch sử**: Ghi nhận kết quả khám vào lịch sử bệnh nhân.

Dữ liệu được lưu trữ trong các tệp CSV: `patients_data.csv`, `doctors_data.csv`, `clinics_data.csv`.
Định dạng ngày tháng sử dụng trong hệ thống và tệp CSV là `DD/MM/YY`.

## 2. Hướng dẫn sử dụng nhanh (Cho người dùng cuối - Phiên bản đóng gói sẵn)
Đây là cách dễ nhất để chạy ứng dụng mà không cần cài đặt Python hay các thư viện.
1.  **Tải toàn bộ dự án**:
    * Nhấn vào nút màu xanh lá cây có chữ **"< > Code"**.
    * Chọn **"Download ZIP"**.
    * Lưu tệp ZIP này vào máy tính của bạn.

2.  **Giải nén**:
    * Tìm tệp ZIP bạn vừa tải về (ví dụ: `He-Thong-Quan-Li-Kham-Benh-main.zip`).
    * Giải nén tệp ZIP này ra một thư mục. Bạn sẽ có một thư mục ví dụ như `He-Thong-Quan-Li-Kham-Benh-main`.

3.  **Chạy ứng dụng**:
    * Đi vào thư mục bạn vừa giải nén, sau đó vào thư mục con `dist`.
    * **Trên Windows**:
        * Tìm và nháy đúp chuột vào tệp `QuanLyKhamBenh.exe`.
    * **Trên macOS**:
        * Tìm và nháy đúp chuột vào tệp ứng dụng`QuanLyKhamBenh` .
        * Lần đầu tiên chạy, bạn có thể cần:
            * Click chuột phải vào ứng dụng và chọn "Open".
            * Sau đó, trong hộp thoại cảnh báo, chọn "Open" một lần nữa.
            * (Nếu bạn đã kéo ứng dụng vào thư mục "Applications", hãy chạy từ đó).

## 3. Hướng dẫn cài đặt và chạy chương trình (Cho nhà phát triển)
* Python 3.9+
* Các thư viện được liệt kê trong `requirements.txt` (chủ yếu là `customtkinter`).


**QUAN TRỌNG**: Để đảm bảo ứng dụng GUI (sử dụng CustomTkinter) hoạt động ổn định, việc thiết lập môi trường Python với phiên bản Tcl/Tk tương thích là rất cần thiết, đặc biệt trên macOS.

### 3.1. Bước chung cho mọi hệ điều hành:
1.  Tải về toàn bộ mã nguồn của dự án.
2.  Đảm bảo các tệp mã nguồn Python (`.py`) và các tệp dữ liệu (`.csv`) nằm trong cùng một thư mục.

### 3.2. Hướng dẫn cho người dùng Windows:
1.  **Cài đặt Python**:
    * Tải bản cài đặt Python (phiên bản 3.9 trở lên) từ [python.org](https://www.python.org/).
    * Trong quá trình cài đặt, **đảm bảo tick vào ô "Add Python to PATH"**.
2.  **Tạo và kích hoạt môi trường ảo (khuyến nghị)**:
    Mở Command Prompt hoặc PowerShell, di chuyển đến thư mục dự án và chạy:
    ```bash
    python -m venv venv_khambenh
    .\venv_khambenh\Scripts\activate
    ```
3.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Chạy ứng dụng**:
    ```bash
    python main_gui.py
    ```
5.  **Thoát môi trường ảo**:
    ```bash
    deactivate
    ```

### 3.3. Hướng dẫn cho người dùng Linux:
1.  **Cài đặt Python và Tkinter**:
    * Hầu hết các bản phân phối Linux đã có Python 3. Kiểm tra bằng `python3 --version`.
    * Cài đặt gói Tkinter cho Python 3 (nếu chưa có):
        * Trên Debian/Ubuntu: `sudo apt-get update && sudo apt-get install python3-tk`
        * Trên Fedora: `sudo dnf install python3-tkinter`
        * (Các bản phân phối khác có thể có lệnh tương tự)
2.  **Tạo và kích hoạt môi trường ảo (khuyến nghị)**:
    Di chuyển đến thư mục dự án và chạy:
    ```bash
    python3 -m venv venv_khambenh
    source venv_khambenh/bin/activate
    ```
3.  **Cài đặt thư viện**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Chạy ứng dụng**:
    ```bash
    python3 main_gui.py
    ```
5.  **Thoát môi trường ảo**:
    ```bash
    deactivate
    ```
### 3.4. Hướng dẫn cho người dùng macOS

Do phiên bản Tcl/Tk đi kèm với Python hệ thống trên macOS thường cũ (8.5.x) và không tương thích tốt với CustomTkinter, chúng tôi **khuyến nghị mạnh mẽ** sử dụng Homebrew để cài đặt Python và Tcl/Tk mới hơn:

1.  **Cài đặt Homebrew (Nếu chưa có)**:
    Mở Terminal và chạy:
    ```bash
    /bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"
    ```
    Làm theo hướng dẫn và đảm bảo Homebrew được thêm vào PATH của bạn.
2.  **Cài đặt Python qua Homebrew**:
    ```bash
    brew install python@3.9 # Hoặc python@3.10, python@3.11, python3
    ```
3.  **Cài đặt Tcl/Tk qua Homebrew**:
    ```bash
    brew install tcl-tk
    ```
4.  **Tạo và kích hoạt môi trường ảo bằng Python từ Homebrew**:
    * Xác định đường dẫn đến Python của Homebrew (ví dụ: `/opt/homebrew/opt/python@3.9/bin/python3.9` cho Apple Silicon, hoặc trong `/usr/local/opt/` cho Intel).
    * Di chuyển đến thư mục dự án và chạy (thay thế đường dẫn Python nếu cần):
        ```bash
        /opt/homebrew/opt/python@3.9/bin/python3.9 -m venv venv_khambenh_hb
        source venv_khambenh_hb/bin/activate
        ```
5.  **Cài đặt thư viện**:
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
6.  **Chạy ứng dụng**:
    ```bash
    python main_gui.py
    ```
7.  **Thoát môi trường ảo**:
    ```bash
    deactivate
    ```

## 4. Cấu trúc mã nguồn
* `main_gui.py`: Giao diện người dùng (GUI) của ứng dụng (sử dụng CustomTkinter).
* `app_logic.py`: Logic nghiệp vụ chính, điều phối hoạt động.
* `models.py`: Định nghĩa các lớp đối tượng dữ liệu (`Patient`, `Doctor`, `Clinic`, `PatientInQueue`).
* `custom_structures.py`: Cài đặt tùy chỉnh cho các cấu trúc dữ liệu (`LinkedList`, `HashTable`, `MaxHeap`, `PriorityQueue`, `RadixTree`).
* `requirements.txt`: Danh sách các thư viện Python cần thiết.
* Các tệp `.csv`: Lưu trữ dữ liệu (ví dụ: `patients_data.csv`).

## 5. Thông tin nhóm sinh viên
* Đặng Thị Thuỳ Dương - 20237318
* Nguyễn Thị Huệ     - 20237439
* Đoàn Vĩnh Nhân     - 20237376
