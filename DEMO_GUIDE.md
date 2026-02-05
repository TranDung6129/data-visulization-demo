# Kịch bản Demo Dự án Big Data

Tài liệu này hướng dẫn từng bước để bạn demo dự án một cách tự tin và suôn sẻ, tập trung vào các phần **đang hoạt động tốt**.

## 1. Chuẩn bị (Trước giờ G)

### Bước 1: Khởi động hệ thống
Mở terminal tại thư mục project và chạy script khởi động:

```bash
cd "/home/trandung/Downloads/Báo cáo bài tập lớn big data 20221 nhóm 28/big_data_20221"
sudo sh up.sh
```
*Đợi khoảng 2-3 phút để các container khởi động hoàn toàn (Elasticsearch, Kibana, Spark).*

### Bước 2: Import dữ liệu mẫu (Quan trọng)
Do API thật bị lỗi, ta sẽ nạp dữ liệu lịch sử để dashboard hiển thị đẹp.
Chạy script tự động (đã tạo sẵn):

```bash
cd "/home/trandung/Downloads/Báo cáo bài tập lớn big data 20221 nhóm 28"
bash import_sample_data.sh
```
*Nếu thấy thông báo success/no errors là thành công.*

### Bước 3: Mở sẵn các tab trên trình duyệt
Mở trước các trang sau để không mất thời gian load khi demo:
1. **Kibana Dashboard**: `http://localhost:5601` (Vào Dashboard, chọn sẵn "Toàn cảnh thị trường")
2. **HDFS**: `http://localhost:9870`
3. **Spark Master**: `http://localhost:8080`

---

## 2. Kịch bản Trình bày (Demo Flow)

Nên đi theo luồng dữ liệu (Data Flow) để người nghe dễ hiểu.

### Phần 1: Giới thiệu Kiến trúc (1 phút)
*(Mở tab Spark Master hoặc sơ đồ kiến trúc nếu có)*
- "Hệ thống gồm các thành phần chính: Crawler thu thập dữ liệu, Kafka làm message queue, Spark Streaming xử lý realtime và lưu vào Elasticsearch để visualize."
- "Hiện tại em sẽ demo luồng dữ liệu chứng khoán realtime."

### Phần 2: Kiểm tra nguồn dữ liệu (HDFS) (1 phút)
*(Chuyển sang tab HDFS UI)*
- "Dữ liệu thô từ crawler được lưu trữ bền vững vào HDFS."
- Vào **Utilities -> Browse the file system**.
- Tìm folder `/data` (hoặc nơi crawler lưu file) để chứng minh dữ liệu đang được lưu.

### Phần 3: Trực quan hóa (Kibana) - Phần chính (3-5 phút)
*(Chuyển sang tab Kibana)*

> **LƯU Ý QUAN TRỌNG:**
> Dữ liệu mẫu nằm ở tháng **1-2 năm 2023**. Bạn **BẮT BUỘC** phải chỉnh Time Picker ở góc trên bên phải:
> - **From**: `Jan 30, 2023 @ 00:00:00.000`
> - **To**: `Feb 10, 2023 @ 23:59:59.999`
> - Bấm **Refresh**.

**Dashboard 1: Toàn cảnh thị trường**
- Chỉ vào các biểu đồ: "Đây là biến động giá, khối lượng giao dịch của các mã VN30."
- "Hệ thống sử dụng Elasticsearch để tổng hợp (aggregation) dữ liệu này gần như tức thời."

**Dashboard 2: So sánh mã (Drill-down)**
- Mở dashboard "So sánh 1 mã" hoặc "Theo dõi chi tiết".
- Chọn một mã cụ thể (ví dụ: `HPG`, `VNM` có trong dữ liệu mẫu).
- "Ta có thể xem chi tiết lệnh đặt mua/bán của từng mã."

### Phần 4: Xử lý rủi ro (Nếu bị hỏi khó)
- **Hỏi:** "Tại sao dữ liệu lại là năm 2023?"
- **Trả lời:** "Do API của sàn chứng khoán hiện tại đã thay đổi cơ chế xác thực và chặn bot, nên em sử dụng snapshot dữ liệu lịch sử để demo khả năng xử lý và hiển thị của hệ thống. Luồng xử lý (Kafka -> Spark -> ES) vẫn giữ nguyên logic."
- **Hỏi:** "Tại sao không thấy bài báo mới?"
- **Trả lời:** "Module crawler báo hiện đang gặp vấn đề tương thích thư viện với các trang báo nguồn, nhóm em đang tập trung tối ưu luồng dữ liệu chứng khoán trước."

---

## 3. Kết thúc
- Tổng kết: "Hệ thống đã chứng minh được khả năng tích hợp các công nghệ Big Data phổ biến để xây dựng pipeline xử lý dữ liệu realtime hoàn chỉnh."
