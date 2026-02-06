import requests
import json
from datetime import datetime, timedelta
from constant.constant import date_format
from os import path

# Hàm lấy thông tin các doanh nghiệp và ghi ra data/stock.json


def get_company_info():
    print('Get company info start')

    # Đọc các thông tin doanh nghiệp có sẵn
    stock_info_front = {}

    if path.exists('data/stock.json'):
        with open('data/stock.json', 'r') as openfile:
            stock_info_front = json.load(openfile)
            stock_info_front = stock_info_front['data']

    print('Done read')

    try:
        # Lấy thông tin tất cả doanh nghiệp trên sàn hnx
        result = requests.post('https://iboard-query.ssi.com.vn/graphql', json={
            "operationName": "stockRealtimesByGroup",
            "query": "query stockRealtimes($exchange: String) {\n  stockRealtimes(exchange: $exchange) {\n    stockNo\n    ceiling\n    floor\n    refPrice\n    stockSymbol\n    stockType\n    exchange\n    matchedPrice\n    matchedVolume\n    priceChange\n    priceChangePercent\n    highest\n    avgPrice\n    lowest\n    nmTotalTradedQty\n    best1Bid\n    best1BidVol\n    best2Bid\n    best2BidVol\n    best3Bid\n    best3BidVol\n    best4Bid\n    best4BidVol\n    best5Bid\n    best5BidVol\n    best6Bid\n    best6BidVol\n    best7Bid\n    best7BidVol\n    best8Bid\n    best8BidVol\n    best9Bid\n    best9BidVol\n    best10Bid\n    best10BidVol\n    best1Offer\n    best1OfferVol\n    best2Offer\n    best2OfferVol\n    best3Offer\n    best3OfferVol\n    best4Offer\n    best4OfferVol\n    best5Offer\n    best5OfferVol\n    best6Offer\n    best6OfferVol\n    best7Offer\n    best7OfferVol\n    best8Offer\n    best8OfferVol\n    best9Offer\n    best9OfferVol\n    best10Offer\n    best10OfferVol\n    buyForeignQtty\n    buyForeignValue\n    sellForeignQtty\n    sellForeignValue\n    caStatus\n    tradingStatus\n    remainForeignQtty\n    currentBidQty\n    currentOfferQty\n    session\n    __typename\n  }\n}\n",
            "variables": {
                "exchange": "hnx"
            }
        })

        hnx = json.loads(result.text)['data']['stockRealtimes']
    except Exception as e:
        print(f"!!! CAUGHT ERROR HNX: {e}")
        hnx = []

    try:
        # Lấy thông tin tất cả doanh nghiệp trên sàn hose
        result = requests.post('https://iboard-query.ssi.com.vn/graphql', json={
            "operationName": "stockRealtimesByGroup",
            "query": "query stockRealtimes($exchange: String) {\n  stockRealtimes(exchange: $exchange) {\n    stockNo\n    ceiling\n    floor\n    refPrice\n    stockSymbol\n    stockType\n    exchange\n    matchedPrice\n    matchedVolume\n    priceChange\n    priceChangePercent\n    highest\n    avgPrice\n    lowest\n    nmTotalTradedQty\n    best1Bid\n    best1BidVol\n    best2Bid\n    best2BidVol\n    best3Bid\n    best3BidVol\n    best4Bid\n    best4BidVol\n    best5Bid\n    best5BidVol\n    best6Bid\n    best6BidVol\n    best7Bid\n    best7BidVol\n    best8Bid\n    best8BidVol\n    best9Bid\n    best9BidVol\n    best10Bid\n    best10BidVol\n    best1Offer\n    best1OfferVol\n    best2Offer\n    best2OfferVol\n    best3Offer\n    best3OfferVol\n    best4Offer\n    best4OfferVol\n    best5Offer\n    best5OfferVol\n    best6Offer\n    best6OfferVol\n    best7Offer\n    best7OfferVol\n    best8Offer\n    best8OfferVol\n    best9Offer\n    best9OfferVol\n    best10Offer\n    best10OfferVol\n    buyForeignQtty\n    buyForeignValue\n    sellForeignQtty\n    sellForeignValue\n    caStatus\n    tradingStatus\n    remainForeignQtty\n    currentBidQty\n    currentOfferQty\n    session\n    __typename\n  }\n}\n",
            "variables": {
                "exchange": "hose"
            }
        })

        hose = json.loads(result.text)['data']['stockRealtimes']
    except Exception as e:
        print(f"Error getting HOSE data: {e}")
        hose = []

    stock_info = {
        'time_stamp': (datetime.now() + timedelta(hours=7)).strftime('%Y-%m-%d') + 'T23:59:59',
        'data': {}
    }

    # Với mỗi doanh nghiệp gọi api lấy thông tin chi tiết
    for stock in hnx:
        info = requests.post('https://iboard-query.ssi.com.vn/graphql', json={
            "operationName": "companyProfile",
            "variables": {
                "symbol": stock['stockSymbol'],
                "language": "vn"
            },
            "query": "query companyProfile($symbol: String!, $language: String) {\n  companyProfile(symbol: $symbol, language: $language) {\n    symbol\n    subsectorcode\n    industryname\n    supersector\n    sector\n    subsector\n    foundingdate\n    chartercapital\n    numberofemployee\n    banknumberofbranch\n    companyprofile\n    listingdate\n    exchange\n    firstprice\n    issueshare\n    listedvalue\n    companyname\n    __typename\n  }\n  companyStatistics(symbol: $symbol) {\n    symbol\n    ttmtype\n    marketcap\n    sharesoutstanding\n    bv\n    beta\n    eps\n    dilutedeps\n    pe\n    pb\n    dividendyield\n    totalrevenue\n    profit\n    asset\n    roe\n    roa\n    npl\n    financialleverage\n    __typename\n  }\n}\n"
        })

        stock_info['data'][stock['stockSymbol'] + '-' +
                           'hnx'] = json.loads(info.text)['data']

    # Với mỗi doanh nghiệp gọi api lấy thông tin chi tiết
    for stock in hose:
        info = requests.post('https://iboard-query.ssi.com.vn/graphql', json={
            "operationName": "companyProfile",
            "variables": {
                "symbol": stock['stockSymbol'],
                "language": "vn"
            },
            "query": "query companyProfile($symbol: String!, $language: String) {\n  companyProfile(symbol: $symbol, language: $language) {\n    symbol\n    subsectorcode\n    industryname\n    supersector\n    sector\n    subsector\n    foundingdate\n    chartercapital\n    numberofemployee\n    banknumberofbranch\n    companyprofile\n    listingdate\n    exchange\n    firstprice\n    issueshare\n    listedvalue\n    companyname\n    __typename\n  }\n  companyStatistics(symbol: $symbol) {\n    symbol\n    ttmtype\n    marketcap\n    sharesoutstanding\n    bv\n    beta\n    eps\n    dilutedeps\n    pe\n    pb\n    dividendyield\n    totalrevenue\n    profit\n    asset\n    roe\n    roa\n    npl\n    financialleverage\n    __typename\n  }\n}\n"
        })

        stock_info['data'][stock['stockSymbol'] + '-' +
                           'hose'] = json.loads(info.text)['data']

    # Kiểm tra lại để tránh ghi 1 doanh nghiệp nhiều lần
    for key in stock_info_front:
        if key not in stock_info['data']:
            stock_info['data'][key] = stock_info_front[key]

    json_object = json.dumps(stock_info, indent=4)

    # Ghi dữ liệu ra file tương ứng
    with open('data/stock.json', 'w') as outfile:
        outfile.write(json_object)

    print('Get company info finish')
