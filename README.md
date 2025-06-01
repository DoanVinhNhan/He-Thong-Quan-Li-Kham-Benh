# HỆ THỐNG QUẢN LÝ KHÁM BỆNH ĐA KHOA

Bài tập Lớn môn Cấu trúc Dữ liệu và Giải thuật - Đại học Bách Khoa Hà Nội.

## 1. Mô tả tổng quan

Chương trình mô phỏng hệ thống quản lý hoạt động khám bệnh tại một cơ sở y tế đa khoa, bao gồm các chức năng chính:

* **Quản lý Hồ sơ Bệnh nhân**: Thêm mới, cập nhật, xóa, tìm kiếm (bao gồm tìm kiếm nhanh theo SĐT/CCCD bằng Radix Tree). Lưu trữ lịch sử khám.
* **Quản lý Bác sĩ**: Thêm mới, cập nhật, xóa thông tin bác sĩ.
* **Quản lý Phòng khám**: Thêm mới, cập nhật, xóa thông tin phòng khám, quản lý danh sách bác sĩ trực thuộc.
* **Đăng ký Khám Bệnh**: Đăng ký bệnh nhân vào hàng đợi của phòng khám với các mức độ ưu tiên khác nhau.
* **Quản lý Hàng đợi Khám**: Theo dõi hàng đợi tại từng phòng khám, sắp xếp bệnh nhân theo mức độ ưu tiên và thời gian đăng ký. Hỗ trợ các thao tác như gọi bệnh nhân kế tiếp, xử lý bệnh nhân vắng mặt, cho bệnh nhân rời hàng đợi, hoặc thay đổi mức độ ưu tiên.
* **Hoàn thành Khám và Lưu Lịch sử**: Ghi nhận thông tin và kết quả khám vào lịch sử khám bệnh của bệnh nhân.

Dữ liệu của hệ thống được lưu trữ trong các tệp CSV: `patients_data.csv`, `doctors_data.csv`, `clinics_data.csv`.
Định dạng ngày tháng được sử dụng trong toàn bộ hệ thống và các tệp CSV là `YYYY/MM/DD`.

## 2. Hướng dẫn sử dụng nhanh (Cho người dùng cuối - Phiên bản đóng gói sẵn)

Đây là cách đơn giản nhất để trải nghiệm ứng dụng mà không cần cài đặt Python hay bất kỳ thư viện phức tạp nào.

1.  **Tải ứng dụng**:
    * Truy cập trang GitHub của dự án.
    * Tìm đến mục **"Releases"** (thường nằm ở thanh bên phải hoặc trong menu chính của kho chứa).
    * Chọn phiên bản mới nhất (ví dụ: **Phiên bản 1.3 - Ứng dụng Quản lý Khám Bệnh "latest"**).
    * Trong mục "Assets" của release đó, tải về tệp **ZIP** phù hợp với hệ điều hành của bạn (ví dụ: `QuanLyKhamBenh-Windows.zip`, `QuanLyKhamBenh-macOS-Intel.zip`, `QuanLyKhamBenh-macOS-Silicon.zip`).
    * Lưu tệp ZIP này vào máy tính.

2.  **Giải nén tệp ZIP**:
    * Sau khi tải về, tìm đến tệp ZIP và giải nén nó ra một thư mục trên máy tính của bạn.

3.  **Chạy ứng dụng**:
    * Mở thư mục bạn vừa giải nén.
    * **Trên Windows**:
        * Tìm và nháy đúp chuột vào tệp `QuanLyKhamBenh.exe`.
    * **Trên macOS**:
        * Tìm và nháy đúp chuột vào tệp ứng dụng `QuanLyKhamBenh` (biểu tượng ứng dụng).
        * **Lưu ý quan trọng cho lần chạy đầu tiên trên macOS**: Do ứng dụng được tải từ internet và chưa được ký bởi Apple, bạn có thể cần thực hiện thêm các bước sau:
            1.  Nhấp chuột phải (hoặc Control-click) vào biểu tượng ứng dụng `QuanLyKhamBenh`.
            2.  Chọn **"Open"** từ menu ngữ cảnh.
            3.  Một hộp thoại cảnh báo có thể xuất hiện. Hãy nhấp vào nút **"Open"** một lần nữa để xác nhận.
            * (Nếu bạn đã kéo ứng dụng vào thư mục "Applications", hãy chạy từ đó).
    * **Lưu ý chung**: Thời gian khởi động ứng dụng lần đầu có thể hơi chậm một chút.

## 3. Hướng dẫn cài đặt và chạy chương trình (Cho nhà phát triển)

Phần này dành cho những ai muốn chạy ứng dụng từ mã nguồn hoặc đóng góp phát triển.

**Yêu cầu hệ thống**:
* Python 3.9+
* Các thư viện được liệt kê trong file `requirements.txt` (chủ yếu là `customtkinter`).

**LƯU Ý QUAN TRỌNG**: Để đảm bảo ứng dụng giao diện đồ họa (GUI) sử dụng CustomTkinter hoạt động ổn định, việc thiết lập một môi trường Python với phiên bản Tcl/Tk tương thích là rất cần thiết, đặc biệt trên hệ điều hành macOS.

### 3.1. Bước chung cho mọi hệ điều hành:

1.  **Tải mã nguồn**:
    * Clone kho chứa GitHub này về máy của bạn:
        ```bash
        git clone [URL_KHO_CHUA_CUA_BAN]
        ```
    * Hoặc tải về dưới dạng ZIP và giải nén.
2.  **Cấu trúc thư mục**: Đảm bảo các tệp mã nguồn Python (`.py`) và các tệp dữ liệu (`.csv` như `patients_data.csv`, `doctors_data.csv`, `clinics_data.csv`) nằm trong cùng một thư mục gốc của dự án.

### 3.2. Hướng dẫn cho người dùng Windows:

1.  **Cài đặt Python**:
    * Tải bản cài đặt Python (phiên bản 3.9 trở lên) từ trang chủ [python.org](https://www.python.org/).
    * Trong quá trình cài đặt, **quan trọng: đảm bảo bạn tick vào ô "Add Python to PATH"** hoặc "Add python.exe to PATH".
2.  **Tạo và kích hoạt môi trường ảo (khuyến nghị)**:
    * Mở Command Prompt (CMD) hoặc PowerShell.
    * Di chuyển đến thư mục gốc của dự án.
    * Chạy các lệnh sau:
        ```bash
        python -m venv venv_qlykhambenh
        .\venv_qlykhambenh\Scripts\activate
        ```
3.  **Cài đặt các thư viện cần thiết**:
    * Trong môi trường ảo đã kích hoạt, chạy:
        ```bash
        pip install -r requirements.txt
        ```
4.  **Chạy ứng dụng**:
    ```bash
    python main_gui.py
    ```
5.  **Thoát môi trường ảo (khi dùng xong)**:
    ```bash
    deactivate
    ```

### 3.3. Hướng dẫn cho người dùng Linux:

1.  **Cài đặt Python và Tkinter**:
    * Hầu hết các bản phân phối Linux hiện đại đã có sẵn Python 3. Kiểm tra bằng lệnh `python3 --version`.
    * Cài đặt gói Tkinter cho Python 3 (nếu chưa có). Đây là thư viện nền tảng cho CustomTkinter:
        * Trên các hệ thống dựa trên Debian/Ubuntu:
            ```bash
            sudo apt-get update
            sudo apt-get install python3-tk
            ```
        * Trên các hệ thống dựa trên Fedora:
            ```bash
            sudo dnf install python3-tkinter
            ```
        * (Các bản phân phối khác có thể có lệnh tương tự, ví dụ `pacman -S tk` trên Arch Linux).
2.  **Tạo và kích hoạt môi trường ảo (khuyến nghị)**:
    * Di chuyển đến thư mục gốc của dự án.
    * Chạy các lệnh sau:
        ```bash
        python3 -m venv venv_qlykhambenh
        source venv_qlykhambenh/bin/activate
        ```
3.  **Cài đặt các thư viện cần thiết**:
    * Trong môi trường ảo đã kích hoạt, chạy:
        ```bash
        pip install -r requirements.txt
        ```
4.  **Chạy ứng dụng**:
    ```bash
    python3 main_gui.py
    ```
5.  **Thoát môi trường ảo (khi dùng xong)**:
    ```bash
    deactivate
    ```

### 3.4. Hướng dẫn cho người dùng macOS:

Do phiên bản Tcl/Tk đi kèm với Python hệ thống trên macOS thường đã cũ (ví dụ: 8.5.x) và có thể không tương thích tốt hoặc gây ra các vấn đề hiển thị với CustomTkinter, chúng tôi **khuyến nghị mạnh mẽ** sử dụng trình quản lý gói Homebrew để cài đặt một phiên bản Python và Tcl/Tk mới hơn.

1.  **Cài đặt Homebrew (Nếu bạn chưa có)**:
    * Mở ứng dụng Terminal.
    * Chạy lệnh sau và làm theo hướng dẫn trên màn hình:
        ```bash
        /bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"
        ```
    * Sau khi cài đặt, đảm bảo Homebrew đã được thêm vào `PATH` của bạn (thường Homebrew sẽ tự động hướng dẫn bạn làm điều này).

2.  **Cài đặt Python qua Homebrew**:
    * Cài đặt một phiên bản Python 3.9+ (ví dụ, Python 3.11):
        ```bash
        brew install python@3.11
        ```
        (Bạn cũng có thể dùng `brew install python3` để cài phiên bản Python 3 mới nhất do Homebrew quản lý).

3.  **Cài đặt Tcl/Tk qua Homebrew**:
    * CustomTkinter sẽ hoạt động tốt hơn với phiên bản Tcl/Tk mới:
        ```bash
        brew install tcl-tk
        ```

4.  **Tạo và kích hoạt môi trường ảo sử dụng Python từ Homebrew**:
    * Xác định đường dẫn chính xác đến file thực thi Python bạn vừa cài bằng Homebrew. Ví dụ:
        * Cho Apple Silicon (M1/M2/M3): `/opt/homebrew/opt/python@3.11/bin/python3.11`
        * Cho Intel Mac: `/usr/local/opt/python@3.11/bin/python3.11`
        (Hoặc nếu bạn dùng `brew install python3`, đường dẫn có thể là `/opt/homebrew/bin/python3` hoặc `/usr/local/bin/python3`).
    * Di chuyển đến thư mục gốc của dự án.
    * Tạo môi trường ảo (thay thế `/đường/dẫn/tới/python_homebrew` bằng đường dẫn đúng của bạn):
        ```bash
        /đường/dẫn/tới/python_homebrew -m venv venv_qlykhambenh_hb
        source venv_qlykhambenh_hb/bin/activate
        ```
        Ví dụ cho Apple Silicon với Python 3.11:
        ```bash
        /opt/homebrew/opt/python@3.11/bin/python3.11 -m venv venv_qlykhambenh_hb
        source venv_qlykhambenh_hb/bin/activate
        ```

5.  **Cài đặt các thư viện cần thiết**:
    * Trong môi trường ảo đã kích hoạt, chạy:
        ```bash
        pip install --upgrade pip
        pip install -r requirements.txt
        ```

6.  **Chạy ứng dụng**:
    ```bash
    python main_gui.py
    ```

7.  **Thoát môi trường ảo (khi dùng xong)**:
    ```bash
    deactivate
    ```

## 4. Cấu trúc mã nguồn

* `main_gui.py`: Chứa mã nguồn cho giao diện người dùng đồ họa (GUI) của ứng dụng, sử dụng thư viện CustomTkinter. Đây là điểm khởi đầu chính của chương trình.
* `app_logic.py`: Bao gồm logic nghiệp vụ cốt lõi của hệ thống, điều phối các hoạt động giữa giao diện người dùng và các module xử lý dữ liệu.
* `models.py`: Định nghĩa các lớp đối tượng dữ liệu được sử dụng trong toàn bộ hệ thống, ví dụ: `Patient` (Bệnh nhân), `Doctor` (Bác sĩ), `Clinic` (Phòng khám), `PatientInQueue` (Bệnh nhân trong hàng đợi).
* `custom_structures.py`: Chứa các cài đặt tùy chỉnh cho những cấu trúc dữ liệu và giải thuật được sử dụng trong dự án, như `LinkedList` (Danh sách liên kết), `HashTable` (Bảng băm), `MaxHeap` (Đống cực đại), `PriorityQueue` (Hàng đợi ưu tiên), `RadixTree` (Cây cơ số).
* `requirements.txt`: Liệt kê tất cả các thư viện Python bên ngoài cần thiết để chạy dự án.
* Các tệp `.csv` (ví dụ: `patients_data.csv`, `doctors_data.csv`, `clinics_data.csv`): Được sử dụng để lưu trữ và tải dữ liệu cố định của hệ thống.

## 5. Thông tin nhóm sinh viên

* Đặng Thị Thuỳ Dương - 20237318
* Nguyễn Thị Huệ - 20237439
* Đoàn Vĩnh Nhân - 20237376

