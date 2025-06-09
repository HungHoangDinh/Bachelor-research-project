## Cách thiết lập và triển khai lại hệ thống

- [Cách thiết lập và triển khai lại hệ thống](#cách-thiết-lập-và-triển-khai-lại-hệ-thống)
- [1. Backend](#1-backend)
  - [1.1. Yêu cầu hệ thống](#11-yêu-cầu-hệ-thống)
  - [1.2 Các bước triển khai](#12-các-bước-triển-khai)
- [2. Frontend](#2-frontend)
  - [2.1. Yêu cầu hệ thống](#21-yêu-cầu-hệ-thống)
  - [2.2 Các bước triển khai](#22-các-bước-triển-khai)
- [3. Evaluate](#3-evaluate)
  - [3.1. Yêu cầu hệ thống](#31-yêu-cầu-hệ-thống)
  - [3.2 Các bước triển khai](#32-các-bước-triển-khai)



## 1. Backend
### 1.1. Yêu cầu hệ thống

- Python >= 3.9  
- Docker và Docker Compose.
### 1.2 Các bước triển khai
1. Di chuyển vào thư mục backend:
```bash
cd backend
```
2. Tạo file .env dựa trên file mẫu env_example:

```bash
cp .env_example .env

```
Thay thế các key bằng key thực tế, các thông số còn lại có thể thay đổi tùy theo nhu cầu.

3. Tạo thư mục dữ liệu:
- Thư mục data trong rag
```bash
mkdir src/rag/data
```
- Thư mục input trong graphrag
```bash
mkdir src/graphrag/graphrag_db/input
```
4. Thêm dữ liệu là các file markdown vào thư mục data, thêm dữ liệu là các file txt vào thư mục input

5. Tạo cơ sở dữ liệu bằng lệnh:

```bash
python main_process_data.py
```
6. Chạy Docker Compose để khởi động dịch vụ:

```bash
docker-compose up --build
```
## 2. Frontend
### 2.1. Yêu cầu hệ thống

- Python >= 3.9  
### 2.2 Các bước triển khai
Tạo terminal mới trước khi thực hiện các bước dưới đây:
1. Di chuyển vào thư mục frontend:
```bash
cd frontend
```
2. Tạo file .env dựa trên file mẫu env_example:

```bash
cp .env_example .env
```
3. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```
4. Khởi động giao diện web

```bash
streamlit run app.py
```
## 3. Evaluate
### 3.1. Yêu cầu hệ thống

- Python >= 3.9
### 3.2 Các bước triển khai
Tạo terminal mới trước khi thực hiện các bước dưới đây:
1. Di chuyển vào thư mục evaluate:
```bash
cd frontend
```
1. Tạo file .env dựa trên file mẫu env_example:

```bash
cp .env_example .env
```
3. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```
4. Thay đổi số số lượng câu trong bộ kiểm thử bằng tham số TESTSET_SIZE trong file constants.
5. Sinh bộ kiểm thử
```bash
python main_create_test_set.py
```
6. Tạo kết quả đánh giá
   
```bash
python main_eval.py
```
7. Trực quan hóa kết quả đánh giá

```bash
python visualize.py
```
Chi tiết kết quả đánh giá xem tại: [Đánh giá](./evaluate/results/images/)