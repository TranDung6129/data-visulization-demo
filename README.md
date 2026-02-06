## Giới thiệu

Project này là **công cụ hỗ trợ phân tích thị trường chứng khoán** sử dụng Hadoop, Spark, Kafka, Elasticsearch, Kibana và một số service crawler (chứng khoán & bài báo).

File này tổng kết **cách chạy hệ thống** và **các chỉnh sửa / fix lỗi** đã thực hiện trong quá trình bạn dựng lại project trên môi trường hiện tại.

---

## Thành phần hệ thống

- **Hadoop HDFS**: lưu trữ dữ liệu thô & đã xử lý (`namenode`, `datanode`)
- **Spark**: xử lý dữ liệu (`spark-master`, `spark-worker`)
- **Kafka + Zookeeper**: truyền dữ liệu realtime giữa crawler và PySpark
- **Elasticsearch**: lưu dữ liệu để truy vấn và visualize
- **Kibana**: xây dashboard phân tích
- **stock_iboard_crawler** (Python + Spark): crawl dữ liệu realtime từ SSI, ghi vào HDFS + gửi Kafka
- **pyspark_application** (Python + Spark): đọc message từ Kafka, xử lý & ghi vào Elasticsearch (và MongoDB nếu có)
- **articles_crawler / articles_server** (Node.js): crawl & hiển thị bài báo (không còn chạy hoàn chỉnh do lỗi thư viện, xem phần “Vấn đề còn tồn tại”)

Tất cả các service (trừ MongoDB Atlas bên ngoài) chạy bằng **Docker Compose**: `big_data_20221/docker-compose.yml`.

---

## Cách chạy hệ thống từ đầu

### 1. Chuẩn bị

Yêu cầu:
- Docker & Docker Compose đã cài trên máy
- Công cụ dòng lệnh: `curl`, `jq`

Thư mục làm việc:

```bash
cd "/home/trandung/Downloads/Báo cáo bài tập lớn big data 20221 nhóm 28/big_data_20221"
```

### 2. Khởi động toàn bộ stack

Script `up.sh`:

- Cài `npm install` cho:
  - `articles_crawler/`
  - `articles_server/`
- Chạy:

```bash
sudo sh up.sh
```

Lệnh này tương đương:

```bash
cd articles_crawler && npm i
cd ../articles_server && npm i
cd ..
sudo docker compose up -d
```

Sau khi `docker compose` chạy xong, kiểm tra:

```bash
docker ps
```

Bạn sẽ thấy các container chính như:

- `namenode`, `datanode`
- `spark-master`, `spark-worker`
- `kafka`, `zookeeper`
- `elasticsearch`, `kibana`
- `stock_iboard_crawler`, `pyspark_application`
- `articles_server` (port `3000`)
- `articles_crawler` (có thể đang restart – xem phần “Vấn đề còn tồn tại”)

---

## Các chỉnh sửa & fix lỗi đã thực hiện

### 1. Mở khóa giờ giao dịch cho stock_iboard_crawler

**Vấn đề gốc**  
Crawler chứng khoán chỉ chạy trong giờ giao dịch (9:00–11:30 & 13:00–15:00, giờ VN). Ngoài khung đó, log chỉ in:

> `Not exchange time yet`

nên khi test vào thời điểm khác sẽ **không có dữ liệu mới**.

**Fix đã làm**

- File: `stock_iboard_crawler/index.py`
- File: `stock_iboard_crawler/main.py`

Trong 2 file này, hàm:

```python
def is_in_exchange_time():
    ...
```

đã được chỉnh thành:

```python
def is_in_exchange_time():
    # For testing: bypass time check
    return 1
    # Phần code gốc giữ lại dưới dạng comment
```

Ý nghĩa:
- **Luôn cho phép crawler chạy**, bất kể thời gian thực.
- Phù hợp cho mục đích test / demo mà không cần đúng giờ giao dịch thực.

> Nếu sau này muốn chạy theo giờ thật, chỉ cần khôi phục lại phần code gốc và bỏ `return 1`.

---

### 2. Khiến MongoDB trở thành tuỳ chọn trong pyspark_application

**Vấn đề gốc**

- File: `pyspark_application/dependencies/mongo.py` kết nối tới MongoDB Atlas:

```python
mongodb+srv://hai4270:hai4270@cluster-big-data.m420aoy.mongodb.net/...
```

- Cluster này hiện **không còn tồn tại / không truy cập được**, dẫn tới:
  - Container `pyspark_application` liên tục **restart** với lỗi:
    - `pymongo.errors.ConfigurationError: The DNS query name does not exist...`

**Fix đã làm**

- Giữ nguyên API `save_df_to_mongodb`, nhưng:
  - Bọc phần tạo `MongoClient` trong `try/except`.
  - Nếu kết nối thất bại:
    - In cảnh báo
    - Gán `mongo_client = None`, `db = None`
  - Trong `save_df_to_mongodb`, nếu `mongo_client` hoặc `db` là `None`:
    - In thông báo `MongoDB not available, skipping MongoDB save`
    - **Không ném exception**, cho phép pipeline Spark tiếp tục chạy.

Kết quả:
- `pyspark_application` vẫn **khởi động và xử lý dữ liệu** bình thường.
- Dữ liệu chỉ **không được lưu vào MongoDB**, nhưng vẫn lưu vào:
  - HDFS (qua crawler)
  - Elasticsearch (qua pyspark_application)

---

### 3. Phân tích & xử lý lỗi articles_crawler (Node.js)

**Vấn đề gốc**

Container `articles_crawler` bị restart liên tục với lỗi:

```text
Error: libnode.so.109: cannot open shared object file: No such file or directory
...
code: 'ERR_DLOPEN_FAILED'
```

Nguyên nhân:
- Image `myracoon/racoon_node:latest` build với **Node.js version khác** so với bản hiện tại trong container, khiến module native (`node-expat`) không load được.
- Thư mục `node_modules` trong volume `/app` được sinh từ môi trường cũ, không tương thích.

**Hướng xử lý**

- Đã thử xoá `node_modules` và cài lại từ host, nhưng thư mục do container tạo ra cần quyền `sudo` để xoá, và việc rebuild chính xác theo môi trường cũ là khá phức tạp.
- Do phần **dashboard chứng khoán không phụ thuộc** vào `articles_crawler`, nên:
  - Tạm thời **chấp nhận articles_crawler lỗi**.
  - `articles_server` vẫn chạy ở `http://localhost:3000`, nhưng dữ liệu bài báo không realtime.

> Nếu cần sửa triệt để, hướng đúng là build lại image Node phù hợp, hoặc bỏ hẳn module `node-expat` và thay bằng parser thuần JS (ví dụ `fast-xml-parser`). Việc này vượt quá phạm vi “dựng lại project để demo”.

---

### 4. Vấn đề với API SSI & cách chuyển sang dùng dữ liệu mẫu

**Vấn đề gốc**

- Crawler `stock_iboard_crawler` gọi API SSI:

```text
https://wgateway-iboard.ssi.com.vn/graphql
```

- Hiện tại host này **không truy cập được** từ môi trường chạy Docker (và cả máy host), dẫn đến:
  - `HTTPSConnectionPool(host='wgateway-iboard.ssi.com.vn', port=443): Max retries exceeded...`
  - Không lấy được dữ liệu realtime → Elasticsearch **không có index `stock_data_realtime`** ban đầu → Kibana báo:
    - `index_not_found_exception: no such index [stock_data_realtime]`

**Giải pháp đã áp dụng**

Thay vì cố phụ thuộc vào API ngoài đã thay đổi, ta dùng **dữ liệu mẫu** đã được xuất sẵn trong thư mục `Sample data/`:

1. `Sample data/Dữ liệu ngày 31 - 1/31_1_data.json`
   - Mỗi dòng là 1 document: `{ "_index": "stock_data_realtime", "_type": "_doc", "_id": ..., "_source": { ... } }`
   - Đã được convert sang bulk & import vào Elasticsearch (10.000 bản ghi) để đảm bảo:
     - Index `stock_data_realtime` tồn tại.
     - Dashboard Kibana có dữ liệu cơ bản để hiển thị.

2. `Sample data/1000 bản ghi dữ liệu sàn SSI buổi sáng ngày 9 - 2 lưu trên elasticsearch.json`
   - Là kết quả `GET stock_data_realtime/_search` từ hệ thống gốc (nhiều bản ghi có `priceChange` ≠ 0, `matchedVolume` > 0).
   - Có thể import thêm để các biểu đồ “Tăng/giảm giá”, “Khối lượng khớp” hiển thị phong phú hơn (xem phần “Import dữ liệu mẫu vào Elasticsearch” bên dưới).

Kết quả:
- Index `stock_data_realtime` đã có **ít nhất 10.000 documents** → Kibana không còn báo `index_not_found_exception`.
- Các dashboard chứng khoán chạy được trên dữ liệu mẫu.

---

## Import dữ liệu mẫu vào Elasticsearch

> Các lệnh dưới đây giả định Elasticsearch đang chạy trên `http://localhost:9200` và đã cài `jq`.

### 1. Import dữ liệu ngày 31-1 (`31_1_data.json`)

File:  
`Sample data/Dữ liệu ngày 31 - 1/31_1_data.json`

Mỗi dòng có dạng:

```json
{"_index":"stock_data_realtime","_type":"_doc","_id":"...","_source":{...}}
```

#### Bước 1: Tạo file bulk NDJSON

```bash
cd "/home/trandung/Downloads/Báo cáo bài tập lớn big data 20221 nhóm 28/Sample data/Dữ liệu ngày 31 - 1"

jq -c '{ index: { _index: ._index } }, ._source' 31_1_data.json > /tmp/bulk_31_1.ndjson
```

#### Bước 2: Gửi bulk lên Elasticsearch (theo lô cho nhẹ)

Ví dụ import 10.000 documents đầu tiên:

```bash
head -20000 /tmp/bulk_31_1.ndjson \
  | curl -s -H "Content-Type: application/x-ndjson" \
        -XPOST "http://localhost:9200/_bulk" \
        --data-binary @- \
  | jq '{took, errors, items: .items | length}'
```

Sau khi chạy, nên thấy:

```json
{
  "took": 6xxx,
  "errors": false,
  "items": 10000
}
```

#### Bước 3: Kiểm tra số lượng

```bash
curl -s "http://localhost:9200/stock_data_realtime/_count" | jq '.'
```

---

### 2. Import dữ liệu buổi sáng 9-2 (`1000 bản ghi…`)

File:  
`Sample data/1000 bản ghi dữ liệu sàn SSI buổi sáng ngày 9 - 2 lưu trên elasticsearch.json`

Đây là kết quả full của `GET stock_data_realtime/_search`, cấu trúc:

```json
{
  "hits": {
    "hits": [
      {
        "_index": "stock_data_realtime",
        "_type": "_doc",
        "_id": "...",
        "_source": { ... }
      },
      ...
    ]
  }
}
```

#### Bước 1: Tạo file bulk NDJSON

```bash
cd "/home/trandung/Downloads/Báo cáo bài tập lớn big data 20221 nhóm 28/Sample data"

jq -c '.hits.hits[] | { index: { _index: ._index } }, ._source' \
  "1000 bản ghi dữ liệu sàn SSI buổi sáng ngày 9 - 2 lưu trên elasticsearch.json" \
  > /tmp/bulk_9_2.ndjson
```

#### Bước 2: Import vào Elasticsearch

```bash
curl -s -H "Content-Type: application/x-ndjson" \
  -XPOST "http://localhost:9200/_bulk" \
  --data-binary @/tmp/bulk_9_2.ndjson \
  | jq '{took, errors, items: .items | length}'
```

Sau đó kiểm tra lại tổng số bản ghi:

```bash
curl -s "http://localhost:9200/stock_data_realtime/_count" | jq '.'
```

---

## Import dashboard Kibana

File backup:  
`big_data_20221/kibana_backup.ndjson`

### Các bước import

1. Mở Kibana:  
   `http://localhost:5601`
2. Vào menu: **Stack Management → Saved Objects**.
3. Bấm **Import**, chọn file `kibana_backup.ndjson`.
4. Chọn **Overwrite** nếu được hỏi (để ghi đè object cũ, nếu có).

Sau khi import, trong **Saved Objects** bạn sẽ thấy:

- Index patterns:
  - `stock_data_realtime`
  - `article`
- Dashboards:
  - `Toàn cảnh thị trường`
  - `So sánh 1 mã`
  - `Theo dõi 1 mã cổ phiếu trên sàn`

### Mở dashboard & chỉnh time range

1. Vào menu **Dashboard**.
2. Chọn một trong các dashboard trên.
3. Góc trên bên phải, chỉnh time range (vì dữ liệu mẫu nằm trong năm 2023):
   - `From`: khoảng 2023‑01‑31
   - `To`: khoảng 2023‑02‑09
4. Bấm **Refresh**.

Lưu ý:
- Một số panel có filter chặt (ví dụ `exchange : "hnx"`, `priceChangePercent > 0`), nếu dataset đang dùng không có bản ghi thỏa mãn thì vẫn sẽ hiện `No results found`. Điều này là **bình thường**, không phải lỗi dashboard.
- Panel liên quan đến bài báo (`tag.keyword`) sẽ trống cho đến khi bạn import thêm dữ liệu bài báo vào Elasticsearch (xem phần dưới).

---

## (Tuỳ chọn) Import dữ liệu bài báo

Trong `Sample data/` có hai file cho phần article:

- `Các bài báo trên elasticsearch.json`: dữ liệu article đã được lưu trên Elasticsearch.
- `Các bài báo lưu trên mongodb.json`: dữ liệu article dạng MongoDB (không cần thiết nếu chỉ muốn xem dashboard trên Elasticsearch).

Nếu muốn dashboard về bài báo hiển thị:

3. Đảm bảo index tương ứng (thường là `article`) tồn tại và có dữ liệu.

### Hướng dẫn chi tiết (Copy & Run)

Để sửa lỗi đồ thị **"Độ phổ biến trên phương tiện truyền thông"**, bạn cần import file `Các bài báo trên elasticsearch.json`:

**Bước 1: Tạo file bulk NDJSON**

```bash
cd "/home/trandung/Downloads/Báo cáo bài tập lớn big data 20221 nhóm 28/Sample data"

jq -c '.hits.hits[] | { index: { _index: "article" } }, ._source' \
  "Các bài báo trên elasticsearch.json" \
  > /tmp/bulk_articles.ndjson
```

**Bước 2: Import vào Elasticsearch**

```bash
curl -s -H "Content-Type: application/x-ndjson" \
  -XPOST "http://localhost:9200/_bulk" \
  --data-binary @/tmp/bulk_articles.ndjson \
  | jq '{took, errors, items: .items | length}'
```

**Bước 3: Kiểm tra**

```bash
curl -s "http://localhost:9200/article/_count" | jq '.'
```

Sau đó quay lại Dashboard Kibana và Refresh.

---

## Hướng dẫn truy cập MongoDB

Hệ thống có sử dụng MongoDB (container `mongo`) để lưu trữ dữ liệu nếu cần. Do cổng mặc định `27017` bị bận, hệ thống đã được cấu hình sang cổng **27018**.

### Cách 1: Truy cập qua Docker (CLI)

```bash
docker exec -it mongo mongo
```

Các lệnh cơ bản:
```javascript
show dbs
use big-data
db.article.find().pretty()
```

### Cách 2: Truy cập qua MongoDB Compass / Studio 3T

Kết nối với thông tin sau:
- **Host**: `localhost`
- **Port**: `27018`
- **Database**: `big-data`

---

## Đường dẫn giao diện web

- **Kibana**:  
  `http://localhost:5601`

- **Hadoop HDFS NameNode UI**:  
  `http://localhost:9870/explorer.html#/project20221`

- **Spark Master UI**:  
  `http://localhost:8080`

- **Elasticsearch (thông tin cluster)**:  
  `http://localhost:9200`

- **Articles Server (web app bài báo)**:  
  `http://localhost:3000`  
  (Dữ liệu article realtime có thể thiếu do `articles_crawler` chưa chạy ổn định.)

---

## Vấn đề còn tồn tại & gợi ý nếu muốn hoàn thiện thêm

1. **`articles_crawler` (Node.js) lỗi `libnode.so.109`**
   - Hướng khắc phục triệt để:
     - Build lại image Node chính xác version tương ứng với `node-expat`.
     - Hoặc loại bỏ `node-expat`, dùng thư viện XML thuần JS.

2. **API SSI thực (`wgateway-iboard.ssi.com.vn`) không ổn định / không truy cập được**
   - Hệ thống hiện đang dựa trên **dữ liệu mẫu** để demo.
   - Nếu muốn dữ liệu realtime:
     - Cần cập nhật lại endpoint, body GraphQL, hoặc sử dụng API nguồn khác (SSI/VNDirect, v.v.).

3. **MongoDB Atlas cũ không còn**
   - Hiện PySpark pipeline đã **không còn phụ thuộc** vào MongoDB (chỉ log cảnh báo).
   - Nếu muốn lưu lại vào MongoDB:
     - Tạo cluster mới, cập nhật connection string trong `pyspark_application/dependencies/mongo.py`.

---

## Tóm tắt nhanh quy trình chạy demo

1. Vào thư mục project:

```bash
cd "/home/trandung/Downloads/Báo cáo bài tập lớn big data 20221 nhóm 28/big_data_20221"
```

2. Khởi động toàn bộ stack:

```bash
sudo sh up.sh
```

3. (Nếu cần) Import dữ liệu mẫu vào Elasticsearch như hướng dẫn ở trên.

4. Mở Kibana (`http://localhost:5601`), import `kibana_backup.ndjson` nếu chưa import.

5. Mở các dashboard:
   - `Toàn cảnh thị trường`
   - `So sánh 1 mã`
   - `Theo dõi 1 mã cổ phiếu trên sàn`

6. Chỉnh time range về khoảng dữ liệu mẫu (cuối 01/2023 – đầu 02/2023) và **Refresh** để xem kết quả.


