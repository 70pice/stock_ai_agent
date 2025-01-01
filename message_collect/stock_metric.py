import requests
import json
import logging
def get_stock_info(stock_code):
    URL = f"https://push2his.eastmoney.com/api/qt/stock/kline/get?fields1=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f11,f12,f13&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&beg=0&end=20500101&ut=fa5fd1943c7b386f172d6893dbfba10b&rtntype=6&secid=0.%s&klt=101&fqt=1&cb=jsonp1732811288019" % stock_code
    try:
        response = requests.get(URL)
        if response.status_code == 200:
            # 拿到json字符串第一个字符
            startIndex = response.text.find('(') + 1
            # 拿到json字符串第二个字符
            endIndex = response.text.rfind(')')
            rawData = response.text[startIndex:endIndex]
            rawDataJson = json.loads(rawData)
            if "data" not in rawDataJson or "klines" not in rawDataJson["data"] or len(
                    rawDataJson["data"]["klines"]) == 0:
                raise KeyError("eastmoney data invalid")
            historyStockInfoList = rawDataJson["data"]["klines"]
            closing_prices = []
            highest_prices = []
            lowest_prices = []
            for historyStockInfo in historyStockInfoList:
                detail = historyStockInfo.split(",")
                if len(detail) != 11:
                    raise KeyError("eastmoney data invalid")
                date = detail[0]
                opening_price = detail[1]
                closing_price = detail[2]
                highest_price = detail[3]
                lowest_Price = detail[4]
                trading_ratio = detail[5]
                trading_price = detail[6]
                trading_swing = detail[7]
                price_limit = detail[8]
                price_range = detail[9]
                turnOver_rate = detail[10]
                closing_prices.append(closing_price)
                lowest_prices.append(lowest_Price)
                highest_prices.append(highest_price)
            closing_prices = [float(x) for x in closing_prices]
            highest_prices = [float(x) for x in highest_prices]
            lowest_prices = [float(x) for x in lowest_prices]
            return closing_prices,highest_prices,lowest_prices
    except Exception as e:
        logging.error("FetchStockPriceFromEastMoney error: {}".format(e))
def calculate_ema(closing_prices: [],period):
    # 对于前period个元素，我们采用简单平均的方式来计算
    ema = []
    for i in range(len(closing_prices)):
        if i < period:
            ema.append(sum(closing_prices[0:i+1]) / (i+1))
        else:
            ema_value = (closing_prices[i] * (2 / (period + 1))) + (ema[i-1] * (1 - (2 / (period + 1))))
            ema.append(ema_value)
    return ema
def calculate_macd(closing_prices):
    # 计算12日指数移动平均线
    ema_12 = calculate_ema(closing_prices, 12)
    # 计算26日指数移动平均线
    ema_26 = calculate_ema(closing_prices, 26)
    # 计算DIF线
    dif = [e12 - e26 for e12, e26 in zip(ema_12, ema_26)]
    # 计算DEA线
    dea = [sum(dif[:9]) / 9]
    for i in range(1,len(dif)):
        dea_value = (dif[i] * 2 / 10) + (dea[-1] * 8 / 10)
        dea.append(dea_value)
    # 计算MACD柱状线
    macd_bar = [(d - de) * 2 for d, de in zip(dif, dea)]
    return macd_bar

def calculate_highest_price(highest_prices,period):
    h_prices = []
    for i in range(len(highest_prices)):
        if i < period:
            h_prices.append(max(highest_prices[0:i+1]))
        else:
            print(max(highest_prices[i - period:i]))
            h_prices.append(max(highest_prices[i - period,i]))
    print(highest_prices)
    return h_prices

def calculate_lowest_price(lowest_prices, period):
    l_prices = []
    for i in range(len(lowest_prices)):
        if i < period:
            l_prices[i] = min(lowest_prices[0:i+1])
        else:
            l_prices[i] = min(lowest_prices[i - period,i])
    return l_prices

def calculate_rsv(closing_prices, highest_prices, lowest_prices, period):
    rsv_values = []
    for i in range(len(closing_prices)):
        if i < period - 1:
            rsv_values.append(None)  # Not enough data to calculate RSV
        else:
            highest_high = max(highest_prices[i - period + 1:i + 1])
            lowest_low = min(lowest_prices[i - period + 1:i + 1])
            current_close = closing_prices[i]
            if highest_high == lowest_low:
                rsv = 0  # Avoid division by zero
            else:
                rsv = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100
            rsv_values.append(rsv)
    return rsv_values

def calculate_kdj(closing_prices, highest_prices, lowest_prices, period=9):
    rsv_values = calculate_rsv(closing_prices, highest_prices, lowest_prices, period)
    k_values = []
    d_values = []
    j_values = []

    # Initial values for K and D
    k = 50
    d = 50

    for rsv in rsv_values:
        if rsv is None:
            k_values.append(None)
            d_values.append(None)
            j_values.append(None)
        else:
            k = (2 / 3) * k + (1 / 3) * rsv
            d = (2 / 3) * d + (1 / 3) * k
            j = 3 * k - 2 * d

            k_values.append(k)
            d_values.append(d)
            j_values.append(j)

    return k_values, d_values, j_values

def calculate_boll(stock_price: []):
    pass

def calculate_rsi(stock_price: []):
    pass

if __name__ == "__main__":
    # # closing_prices,highest_prices,lowest_prices = get_stock_info("002371")
    # # calculate_highest_price(highest_prices,6)
    # print(1)