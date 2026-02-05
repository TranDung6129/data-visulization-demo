#!/bin/bash

# Configuration
ES_URL="http://localhost:9200"
PROJECT_DIR="/home/trandung/Downloads/Báo cáo bài tập lớn big data 20221 nhóm 28"
DATA_DIR="$PROJECT_DIR/Sample data"

echo "=== Bắt đầu Import Dữ liệu mẫu vào Elasticsearch ==="

# Check requirements
if ! command -v jq &> /dev/null; then
    echo "Lỗi: 'jq' chưa được cài đặt. Vui lòng cài đặt: sudo apt-get install jq"
    exit 1
fi

if ! curl -s "$ES_URL" > /dev/null; then
    echo "Lỗi: Không thể kết nối tới Elasticsearch tại $ES_URL."
    echo "Hãy chắc chắn bạn đã chạy 'sudo sh up.sh' và đợi các container khởi động."
    exit 1
fi

echo ">> Elasticsearch đang chạy..."

# 1. Import Stock Data (31/1)
echo "------------------------------------------------"
echo ">> Xử lý file: 31_1_data.json"
FILE_31_1="$DATA_DIR/Dữ liệu ngày 31 - 1/31_1_data.json"

if [ -f "$FILE_31_1" ]; then
    # Convert to bulk format
    jq -c '{ index: { _index: ._index } }, ._source' "$FILE_31_1" > /tmp/bulk_31_1.ndjson
    
    # Send to ES
    echo ">> Đang gửi dữ liệu vào ES (stock_data_realtime)..."
    curl -s -H "Content-Type: application/x-ndjson" \
         -XPOST "$ES_URL/_bulk" \
         --data-binary @/tmp/bulk_31_1.ndjson \
         | jq '{took, errors, items: .items | length}'
else
    echo "Cảnh báo: Không tìm thấy file $FILE_31_1"
fi

# 2. Import Stock Data (9/2 - Search Result Format)
echo "------------------------------------------------"
echo ">> Xử lý file: 1000 bản ghi dữ liệu sàn SSI..."
FILE_9_2="$DATA_DIR/1000 bản ghi dữ liệu sàn SSI buổi sáng ngày 9 - 2 lưu trên elasticsearch.json"

if [ -f "$FILE_9_2" ]; then
    # Convert Search Result format to Bulk format
    jq -c '.hits.hits[] | { index: { _index: ._index } }, ._source' "$FILE_9_2" > /tmp/bulk_9_2.ndjson
    
    # Send to ES
    echo ">> Đang gửi dữ liệu bổ sung vào ES..."
    curl -s -H "Content-Type: application/x-ndjson" \
         -XPOST "$ES_URL/_bulk" \
         --data-binary @/tmp/bulk_9_2.ndjson \
         | jq '{took, errors, items: .items | length}'
else
    echo "Cảnh báo: Không tìm thấy file $FILE_9_2"
fi

# 3. Import Article Data (Optional)
echo "------------------------------------------------"
echo ">> Xử lý file: Các bài báo trên elasticsearch.json"
FILE_ARTICLE="$DATA_DIR/Các bài báo trên elasticsearch.json"

if [ -f "$FILE_ARTICLE" ]; then
    # Convert Search Result format to Bulk format (assuming similar structure to 9/2 file since name suggests export from ES)
    # Checking structure logic would be safer, but assuming hits.hits structure based on filename context
    # Try basic inspection first or assume standard ES dump
    jq -c '.hits.hits[] | { index: { _index: ._index } }, ._source' "$FILE_ARTICLE" > /tmp/bulk_article.ndjson 2>/dev/null
    
    if [ $? -eq 0 ]; then
         echo ">> Đang gửi dữ liệu bài báo vào ES..."
         curl -s -H "Content-Type: application/x-ndjson" \
             -XPOST "$ES_URL/_bulk" \
             --data-binary @/tmp/bulk_article.ndjson \
             | jq '{took, errors, items: .items | length}'
    else
         # Fallback if structure is simple list like 31_1
         jq -c '{ index: { _index: ._index } }, ._source' "$FILE_ARTICLE" > /tmp/bulk_article.ndjson
         curl -s -H "Content-Type: application/x-ndjson" \
             -XPOST "$ES_URL/_bulk" \
             --data-binary @/tmp/bulk_article.ndjson \
             | jq '{took, errors, items: .items | length}'
    fi
else
    echo "Cảnh báo: Không tìm thấy file $FILE_ARTICLE"
fi

echo "------------------------------------------------"
echo "=== Hoàn tất! ==="
echo "Kiểm tra tổng số bản ghi chứng khoán:"
curl -s "$ES_URL/stock_data_realtime/_count" | jq '.'
