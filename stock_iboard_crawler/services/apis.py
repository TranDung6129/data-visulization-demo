import requests
import json
from datetime import datetime, timedelta
from constant.constant import time_zone, time_format

# Hàm lấy dữ liệu chứng khoán hiện tại từ api của ssi


def get_stock_real_times_by_group(url, body):
    try:
        # Use variables from body directly to support both 'group' and 'exchange'
        payload_variables = body.get('variables', {})
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json'
        }
        
        print(f"DEBUG: Requesting {url}", flush=True)
        result = requests.post(url, headers=headers, json={
            'operationName': body['operationName'],
            'query': body['query'],
            'variables': payload_variables
        })

        print(f"DEBUG: Response status {result.status_code}", flush=True)

        if result.status_code == 200:
            json_data = json.loads(result.text)
            # Handle different response keys (stockRealtimes OR stockRealtimesByGroup)
            data_key = 'stockRealtimes'
            if 'stockRealtimesByGroup' in json_data['data']:
                data_key = 'stockRealtimesByGroup'
                
            return {
                'timestamp': datetime.now() + timedelta(hours=time_zone),
                'data': json_data['data'][data_key]
            }

        print('Request stock_real_times_by_group fail' +
              (datetime.now() + timedelta(hours=time_zone)).strftime(time_format))

    except Exception as e:
        print(e)
