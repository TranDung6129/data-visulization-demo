import json
from services.apis import get_stock_real_times_by_group
from constant.constant import ssi_stock_data_api, hadoop_namenode, time_format, kafka_bootstrap_servers, kafka_topic
from dependencies import kafka_producer


def process_ssi_data(spark, data, work):
    kafka_producer_instance = kafka_producer.start_kafka_producer(
        kafka_bootstrap_servers)

    df = spark.sparkContext.parallelize(
        data['data']).map(lambda x: json.dumps(x))
    df = spark.read.json(df)

    # Ghi dữ liệu nhận được vào file trung gian
    data_dir = hadoop_namenode + work['hadoop_dir'] + \
        data['timestamp'].strftime(time_format) + '.parquet'

    (df
        .write
        .format('parquet')
        .mode('overwrite')
        .save(data_dir))

    # Gửi thông tin lên kafka bao gồm địa chỉ file dữ liệu cần xử lý, địa chỉ file config hướng dẫn sử lý và time stamp
    kafka_producer_instance.send(kafka_topic, {
        'data_dir': work['hadoop_dir'] + data['timestamp'].strftime(time_format) + '.parquet',
        'config_dir': work['config_dir'],
        'time_stamp': data['timestamp'].strftime(time_format)
    })

    print('Success get data from ' +
          work['data'] + ' at ' + data['timestamp'].strftime(time_format))


def start_crawl(spark, work):
    print(f"DEBUG: start_crawl called with data={work.get('data')}", flush=True)
    # Nếu loại dữ liệu được chỉ định trong work là data thì gọi hàm lấy data từ ssi
    if work['data'] == ssi_stock_data_api:
        print("DEBUG: Calling get_stock_real_times_by_group", flush=True)
        data = get_stock_real_times_by_group(
            work['source']['url'], work['source']['body'])
        if (data):
            process_ssi_data(spark, data, work)
