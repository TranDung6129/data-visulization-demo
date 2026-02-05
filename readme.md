Hướng dẫn sử dụng

Project: Công cụ hỗ trợ phân tích thị trường chứng khoán

Dữ liệu được lấy từ api của ssi về 2 sàn chứng khoán hose và hnx

Cách thực hiện

Sử dụng:

- Chạy 'sudo sh up.sh' và hệ thống sẽ tự động crawl dữ liệu và lưu vào elasticsearch + hadoop
- Tắt hadoop save mode nếu cần thiết: sudo docker exec namenode hdfs dfsadmin -safemode leave
- Bật http://localhost:9870/explorer.html#/project20221 để kiểm tra hệ thống file hadoop
- Vào http://localhost:5601/app/dev_tools#/console và chạy GET /stock_data_realtime/\_search để xem các bản ghi được lưu về
- Sử dụng backup của dashboard kibana để biểu diễn dữ liệu: kibana_backup.ndjson
