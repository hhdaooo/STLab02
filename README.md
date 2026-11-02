STLab02 - EduCommerce Automated Testing

Dự án này chứa mã nguồn và kịch bản kiểm thử tự động cho hệ thống EduCommerce, thuộc bài tập STLab02 - Môn Software Testing.

Dự án áp dụng phương pháp Data-driven Testing bằng Python, đọc kịch bản từ file CSV, thực thi kiểm thử độc lập (Test Isolation) trên in-memory data, và xuất báo cáo tự động (Excel, CSV, HTML Dashboard).

1. Cấu trúc thư mục (Repository Structure)

ecommerce_app.py: Mã nguồn mô phỏng các nghiệp vụ của EduCommerce (Catalog, Cart, Inventory, Payment, Checkout).

test_runner.py: Script chạy kiểm thử tự động, đọc file CSV, điều phối thực thi, so sánh Assertions và xuất Report.

STLab02_Ecommerce_TestCases.csv: Bộ dữ liệu Test Cases chi tiết (Input, Expected, Config).

reports/: Thư mục chứa kết quả thực thi (được tự động sinh ra sau khi chạy).

2. Hướng dẫn chạy trên Google Colab

Bước 1: Truy cập Google Colab và tạo một Notebook mới (New Notebook).

Bước 2: Trong một Cell Code mới, dán đoạn lệnh sau để tải source code về và di chuyển vào thư mục dự án:

!git clone https://github.com/hhdaooo/STLab02.git
%cd STLab02


Bước 3: Cài đặt các thư viện cần thiết:

!pip install -q pandas openpyxl matplotlib gradio


Bước 4: Thực thi bộ kiểm thử:

!python test_runner.py


(Kết quả PASS/FAIL sẽ in ra màn hình.).

Bước 5: Tải báo cáo về máy:

from google.colab import files
files.download("reports/test_report.xlsx")

Bước 4: Xem kết quả (Test Reports)
Sau khi script chạy xong:

Console sẽ in ra tổng số lượng PASS/FAIL.

Truy cập thư mục reports/ để xem file test_report.xlsx và test_execution.csv.

4. Ghi chú Bảo mật (Security Notes)

Dự án này được thiết lập chạy in-memory và không yêu cầu bất kỳ API Key, Database Credentials hay Access Token thực tế nào.

Các file rác hoặc thông tin môi trường đã được loại trừ qua file .gitignore.
