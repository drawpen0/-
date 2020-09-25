import datetime
import time
import math
from decimal import getcontext, Decimal, ROUND_DOWN
getcontext().prec = 6
from binance.client import Client

##### WBTC BTC ETH三角套利策略 WBTC本位
#
#     交易順序(A) WBTC > BTC > ETH > WBTC
#     交易市場(A)  WBTCBTC(bid) > ETHBTC(ask) > WBTCETH(ask)
#
#     交易順序(B) WBTC > ETH > BTC > WBTC
#     交易市場(B) WBTCETH(bid) > ETHBTC(bid) > WBTCBTC(ask)

client = Client(api_key='', api_secret='')
x = 0
y = 0
z = 0

####基礎參數
depth = 0.5    #成交深度閥值(BTC)
refreshtime = 10  #更新頻率(秒)
Fee = 0.00075   #手續費
L_Profit = 0.000  #最低獲利門檻

while True :

    ####0_重置參數
    all_ETHbids = 0
    all_BTCbids = 0
    all_WBTCasks = 0
    all_ETHbids2 = 0
    all_BTCbids2 = 0
    all_WBTCasks2 = 0

    ####1_取得帳戶WBTC餘額
    WBTCbalance = client.get_asset_balance(asset='WBTC')
    time.sleep(0.1)
    WBTC = Decimal(WBTCbalance['free']).quantize(Decimal('.0001'), rounding=ROUND_DOWN)

    ####2_計算三個市場的掛單深度  WBTCETH取得bid  ETHBTC取得bid  WBTCBTC取得ask
    WBTCETH_market_depth = client.get_order_book(symbol='WBTCETH')
    ETHBTC_market_depth = client.get_order_book(symbol='ETHBTC')
    WBTCBTC_market_depth = client.get_order_book(symbol='WBTCBTC')

    ####3_計算各個市場達深度門檻的價格
    for k in range(0, len(WBTCBTC_market_depth['bids']), 1) :
        WBTCask = float(WBTCBTC_market_depth['bids'][k][1])
        all_WBTCasks = all_WBTCasks + WBTCask
        if all_WBTCasks >= depth :
            WBTC_Price = float(WBTCBTC_market_depth['bids'][k][0])
            print('WBTCBTC賣價為:', WBTC_Price)
            #print('WBTCBTC深度為:', all_WBTCasks, 'WBTC')
            break

    for i in range(0, len(WBTCETH_market_depth['asks']), 1) :
        ETHbid = float(WBTCETH_market_depth['asks'][i][1])
        all_ETHbids = all_ETHbids + ETHbid
        if all_ETHbids >= depth :
            ETH_price = float(WBTCETH_market_depth['asks'][i][0])
            print('WBTCETH買價為:', ETH_price)
            #print('WBTCETH深度為:', all_ETHbids, 'WBTC')
            break

    for j in range(0, len(ETHBTC_market_depth['asks']), 1) :
        BTCbid = float(ETHBTC_market_depth['asks'][j][1])
        all_BTCbids = all_BTCbids + BTCbid
        if all_BTCbids >= depth * ETH_price :
            BTC_Price = float(ETHBTC_market_depth['asks'][j][0])
            print('ETHBTC買價為:', BTC_Price)
            #print('ETHBTC深度為:', all_BTCbids, 'ETH')
            break

        ####4_套利方式B
    for i in range(0, len(WBTCETH_market_depth['bids']), 1) :
        ETHbid2 = float(WBTCETH_market_depth['bids'][i][1])
        all_ETHbids2 = all_ETHbids2 + ETHbid2
        if all_ETHbids2 >= depth :
            ETH_price2 = float(WBTCETH_market_depth['bids'][i][0])
            print('WBTCETH賣價為:', ETH_price2)
            #print('WBTCETH深度為:', all_ETHbids2, 'WBTC')
            break
    
    for j in range(0, len(ETHBTC_market_depth['bids']), 1) :
        ETH_price2 = float(WBTCETH_market_depth['bids'][i][0])
        BTCbid2 = float(ETHBTC_market_depth['bids'][j][1])
        all_BTCbids2 = all_BTCbids2 + BTCbid2
        if all_BTCbids2 >= depth * ETH_price2 :
            BTC_Price2 = float(ETHBTC_market_depth['bids'][j][0])
            print('ETHBTC賣價為:', BTC_Price2)
            #print('ETHBTC深度為:', all_BTCbids2, 'ETH')
            break

    for k in range(0, len(WBTCBTC_market_depth['asks']), 1) :
        WBTCask2 = float(WBTCBTC_market_depth['asks'][k][1])
        all_WBTCasks2 = all_WBTCasks2 + WBTCask2
        if all_WBTCasks2 >= depth :
            WBTC_Price2 = float(WBTCBTC_market_depth['asks'][k][0])
            print('WBTCBTC買價為:', WBTC_Price2)
            #print('WBTCBTC深度為:', all_WBTCasks2, 'WBTC')
            break




    #計算預期獲利
    P1 = WBTC_Price*(1-Fee) / BTC_Price*(1-Fee) /  ETH_price *(1-Fee)-1
    P2 = ETH_price2*(1-Fee) * BTC_Price2*(1-Fee) / WBTC_Price2*(1-Fee)-1

    if P1 >= L_Profit:
        print('執行三角套利, 預期利潤為', P1)
        x = x + 1
    else:
        print('A_價差不足,預期利潤為', P1)
    
    if P2 >= L_Profit:
        print('執行三角套利, 預期利潤為', P2)
        z = z + 1
    else:
        print('B_價差不足,預期利潤為', P2)
    
    y = y + 1

    print('套利機會A' , x )
    print('套利機會B' , z )
    print('週期', y)

    time.sleep(10)
