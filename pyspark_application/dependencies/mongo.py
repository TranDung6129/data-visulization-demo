import pymongo

# Try to connect to MongoDB, but make it optional
mongo_client = None
db = None

try:
    mongo_client = pymongo.MongoClient(
        'mongodb://mongo:27017/big-data',
        serverSelectionTimeoutMS=5000)
    # Test connection
    mongo_client.server_info()
    db = mongo_client['big-data']
    print('Connect to MongoDB success')
except Exception as e:
    print(f'MongoDB connection failed: {e}')
    print('WARNING: MongoDB is not available. Data will only be saved to Elasticsearch and Hadoop.')


def save_df_to_mongodb(modal, data):
    if mongo_client is None or db is None:
        print('MongoDB not available, skipping MongoDB save')
        return
    
    try:
        modal_collection = db[modal]
        insert_data = data.collect()

        for data_item in insert_data:
            try:
                modal_collection.insert_one(data_item.asDict())
            except Exception as e:
                print(e)
        print('Success save to mongodb')
    except Exception as e:
        print(f'Error saving to MongoDB: {e}')
