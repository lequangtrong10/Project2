# Project 2 - Tiki Product Crawler

## 1. Giới thiệu

Dự án được xây dựng bằng Python nhằm thu thập dữ liệu sản phẩm từ API của Tiki dựa trên danh sách Product ID được cung cấp trong file CSV.

API sử dụng:

```text
https://api.tiki.vn/product-detail/api/v1/products/{id}
```

Thông tin thu thập bao gồm:

* id
* name
* url_key
* price
* description
* images

Dữ liệu sau khi xử lý được lưu thành các file JSON theo từng batch.

---

## 2. Cấu trúc thư mục

```text
Project2_tiki/
│
├── config/
│   ├── config.yaml
│   ├── settings.py
│   └── __init__.py
│
├── data/
│   ├── input/
│   └── output/
│
├── scripts/
│   ├── validate_input.py
│   ├── run_crawler.py
│   ├── retry_failed.py
│   └── reset_sample_run.py
│
├── src/
│   ├── async_api_client.py
│   ├── async_retry_handler.py
│   ├── batch_processor.py
│   ├── checkpoint.py
│   ├── cleaner.py
│   ├── error_classifier.py
│   ├── json_handler.py
│   ├── product_validator.py
│   ├── progress_tracker.py
│   ├── retry_handler.py
│   ├── summary_printer.py
│   └── summary_report.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 3. Cài đặt

Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

---

## 4. Kiểm tra dữ liệu đầu vào

Thực hiện kiểm tra và làm sạch dữ liệu:

```bash
python scripts/validate_input.py
```

Chương trình sẽ:

* Kiểm tra cột id
* Loại bỏ ID duplicate
* Loại bỏ ID không hợp lệ
* Sinh file dữ liệu sạch để crawler sử dụng

---

## 5. Chạy crawler

Thực hiện crawl dữ liệu:

```bash
python scripts/run_crawler.py
```

Quy trình xử lý:

```text
Đọc Product ID
↓
Chia batch
↓
Gọi API bất đồng bộ (Async)
↓
Làm sạch dữ liệu
↓
Kiểm tra dữ liệu
↓
Ghi file JSON
↓
Lưu checkpoint
↓
Tạo báo cáo tổng kết
```

---

## 6. Cơ chế checkpoint và resume

Hệ thống hỗ trợ tiếp tục xử lý khi chương trình bị dừng đột ngột.

Các file sử dụng:

```text
checkpoint.json
processed_ids.txt
```

Nếu máy tính bị tắt, mất điện hoặc chương trình dừng giữa chừng, lần chạy tiếp theo sẽ tự động bỏ qua các Product ID đã xử lý và tiếp tục từ vị trí gần nhất.

---

## 7. Chạy lại các sản phẩm thất bại

Sau khi crawler hoàn thành:

```bash
python scripts/retry_failed.py
```

Chương trình sẽ:

* Đọc toàn bộ Product ID thất bại
* Gọi lại API
* Lưu các sản phẩm phục hồi được
* Tạo danh sách lỗi cuối cùng

---

## 8. Kết quả thực nghiệm

Cấu hình:

```yaml
sample_size: 200000
batch_size: 1000
concurrency: 10
```

Kết quả:

```text
Input IDs     : 200000
Success       : 124373
Failed        : 75627
Warnings      : 30

Runtime       : 5702 giây
Throughput    : 35.07 products/giây
```

Phân loại lỗi:

```text
NOT_FOUND       : 75626
INVALID_PRODUCT : 1
```

Cảnh báo dữ liệu:

```text
missing_description : 21
missing_images      : 9
```

---

## 9. Kết quả Retry

Thử chạy lại toàn bộ các Product ID thất bại:

```text
Input IDs     : 75627
Recovered     : 31
Still Failed  : 75596
```

Kết quả cho thấy phần lớn lỗi NOT_FOUND là lỗi thực tế của dữ liệu đầu vào thay vì lỗi tạm thời của hệ thống.

---

## 10. Sử dụng

* Python
* asyncio
* aiohttp
* pandas
* BeautifulSoup4
* JSON
* YAML

---

## 11. Kết luận

Dự án đã triển khai thành công:

* Kiểm tra dữ liệu đầu vào
* Loại bỏ dữ liệu duplicate
* Thu thập dữ liệu bất đồng bộ
* Xử lý theo batch
* Cơ chế checkpoint và resume
* Theo dõi sản phẩm thất bại
* Retry dữ liệu lỗi
* Tạo báo cáo tổng kết
* Xử lý thành công tập dữ liệu 200.000 Product ID
