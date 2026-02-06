from constant.constant import works, hadoop_namenode
from services.crawl import start_crawl
from dependencies import spark
import time
from datetime import datetime, timedelta
# import config.config

print('Craler stared')

elasticsearch_time_format = '%Y-%m-%dT%H:%M:%S'

# Hàm trả về 1 nếu thời gian hiện tại trong giờ giao dịch, 0 ngược lại
# MODIFIED: Always return 1 for testing purposes


def is_in_exchange_time():
    # For testing: bypass time check
    return 1
    
    # Original code (commented out for testing):
    # now = datetime.now() + timedelta(hours=7)
    # today = now.strftime('%Y-%m-%d')
    #
    # start_mor = datetime.strptime(
    #     today + 'T' + '09:00:00', elasticsearch_time_format)
    # end_mor = datetime.strptime(
    #     today + 'T' + '11:30:00', elasticsearch_time_format)
    # start_eve = datetime.strptime(
    #     today + 'T' + '13:00:00', elasticsearch_time_format)
    # end_eve = datetime.strptime(
    #     today + 'T' + '15:00:00', elasticsearch_time_format)
    #
    # if (now >= start_mor and now <= end_mor) or (now >= start_eve and now <= end_eve):
    #     return 1
    # else:
    #     return 0


def crawl(spark_sess, work):
    # Đọc file config được chỉ định để xử lý
    config = (spark_sess
              .read
              .option("multiLine", "true")
              .json(hadoop_namenode + work['config'])
              .rdd
              .map(lambda row: row.asDict()).collect())

    if (len(config) == 1):
        start_crawl(spark_sess, config[0])


def start_crawler():
    spark_sess = spark.start_spark()

    while True:
        if is_in_exchange_time() == 1:
            print(f'DEBUG: Starting crawl loop at {datetime.now()}', flush=True)
            for work in works:
                print(f'DEBUG: Processing work {work.get("config", "unknown")}', flush=True)
                crawl(spark_sess, work)

            time.sleep(60)
        else:
            print('Not exchange time yet')


if __name__ == '__main__':
    try:
        start_crawler()
    except Exception as e:
        print(e)
