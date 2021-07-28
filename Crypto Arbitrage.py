import ccxt
import datetime
import FinanceDataReader as fdr
import pyupbit
import time
import requests

p_exchange = 1150  # 환율 초기값
binance = ccxt.binance({
    'apiKey': 'dd',
    'secret': 'sd',
})  # 바이낸스 API
upbit = pyupbit.Upbit('asd', 'asdasd')
myToken = "aa"  # slack
ticker = 'EOS'  # 종목
count = 20  # 주문 수량
mount = 100000  # 주문 금액
status = 0.6  # 프리미엄 기준
gap = 0.5  # 갭


def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )


def get_exchange():
    today = str(datetime.date.today())
    today = int(today.replace('-', ''))
    today = str(today - 7)  # 주말 오류 방지
    exchange = fdr.DataReader('USD/KRW', today).iloc[-1, 0]
    print('환율: ' + str(exchange))
    return exchange


def binance_balance(tk):
    balance = binance.fetch_balance()  # 잔고 조회
    b_balance = balance[tk]['free']
    print(tk + ' Binance 잔고: ' + str(b_balance))
    return b_balance


def binance_price(tk):
    b_ticker = binance.fetch_ticker(tk+'/USDT')  # 현재가 조회
    price = b_ticker['close']
    price2 = price * p_exchange # 원화 계산
    # print(tk + ' Binance 현재가: ' + str(price2))
    return price2


def binance_usd_price(tk):
    b_ticker = binance.fetch_ticker(tk+'/USDT')  # 현재가 조회
    price = b_ticker['close']
    return price


def binance_buy(tk, cnt):
    order = binance.create_market_buy_order(tk + '/USDT', cnt)  # 시장가 매수 주문
    print(order)
    post_message(myToken, "#stock", print(order))
    print('바이낸스 시장가 매수')


def binance_sell(tk, cnt):
    order = binance.create_market_sell_order(tk + '/USDT', cnt)  # 시장가 매도 주문
    print(order)
    post_message(myToken, "#stock", print(order))
    print('바이낸스 시장가 매도')


def upbit_price(tk):
    u_price = pyupbit.get_current_price('KRW-' + tk)
    # print(tk + ' Upbit 현재가: ' + str(u_price))
    return u_price


def upbit_buy(tk, mnt):  # 업비트 시장가 매수는 금액 기준
    u_ticker = 'KRW-' + tk
    market_price_buy = upbit.buy_market_order(u_ticker, mnt)
    print(market_price_buy)
    post_message(myToken, "#stock", print(market_price_buy))
    print('업비트 시장가 매수')


def upbit_sell(tk, cnt):
    u_ticker = 'KRW-' + tk
    market_price_sell = upbit.sell_market_order(u_ticker, cnt)
    print(market_price_sell)
    post_message(myToken, "#stock", print(market_price_sell))
    print('업비트 시장가 매도')


def get_premium(b_price, u_price, tk):
    premium = 100*(u_price-b_price)/u_price
    print(tk + ' 프리미엄: ' + str(round(premium, 3)) + '%')
    return premium


while True:
    try:
        p_exchange = get_exchange()  # 환율
        if binance_balance('USDT') > (count*binance_usd_price(ticker)+50) and upbit.get_balance('KRW-' + ticker) > count:
            print('김프 잔고 가능')
            if get_premium(binance_price(ticker), upbit_price(ticker), ticker) > (status+gap):
                print('김프 매매')
                upbit_sell(ticker, count)
                binance_buy(ticker, count)
                post_message(myToken, "#stock", print(get_premium(binance_price(ticker), upbit_price(ticker), ticker)))
            else:
                print('김프 stop')
        else:
            print('바이낸스 USDT 부족')

        if upbit.get_balance('KRW') > mount + 50000 and binance_balance(ticker) > mount/binance_price(ticker):
            print('역프 잔고 가능')
            if get_premium(binance_price(ticker), upbit_price(ticker), ticker) < (status-gap):
                print('역프 매매')
                upbit_buy(ticker, mount)
                count2 = mount/(upbit_price(ticker)+5)
                binance_sell(ticker, count2)
                post_message(myToken, "#stock", print(get_premium(binance_price(ticker), upbit_price(ticker), ticker)))
            else:
                print('역프 stop')
        else:
            print('업비트 KRW 부족')
        time.sleep(300)

    except Exception as e:
        print(e)
        post_message(myToken, "#crypto", e)
        time.sleep(30)