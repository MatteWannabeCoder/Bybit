'''BYBIT V5 API'''
'''Credit: Matteo D'Ambrogio telegram: @I_Am_Matte email: myfakemail38@gmail.com'''
from datetime import datetime as dt
import numpy as np
import time
import talib as ta
import requests
import traceback
import time
import hashlib
import hmac
import uuid

API_KEY = ''
PRIVATE_KEY = ''
SUBS = ["instrument_info.100ms.ETHUSDT"]
SYMBOL = 'ETHUSDT'
TIMEFRAME = 45
SOURCE = 'low'
EQUITY = 0.9
N_CANDELE = 3
POLLING_RATE = 30
LEVERAGE = 1
SL = 3

increased_count = 0
httpClient=requests.Session()
recv_window=str(5000)
url="https://api.bytick.com" 
#url = "https://api-testnet.bybit.com"

def HTTP_R(endpoint,method,params,Info):
    global time_stamp
    time_stamp=str(int(time.time() * 10 ** 3))
    signature=genS(params)
    headers = {
        'X-BAPI-API-KEY': API_KEY,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if(method=="POST"):
        response = httpClient.request(method, url+endpoint, headers=headers, data=params)
    else:
        response = httpClient.request(method, url+endpoint+"?"+params, headers=headers)
    return response.json()
def HTTP(endpoint,method,params,Info):
    global time_stamp
    time_stamp=str(int(time.time() * 10 ** 3))
    signature=genS(params)
    headers = {
        'X-BAPI-API-KEY': API_KEY,
        'X-BAPI-SIGN': signature,
        'X-BAPI-SIGN-TYPE': '2',
        'X-BAPI-TIMESTAMP': time_stamp,
        'X-BAPI-RECV-WINDOW': recv_window,
        'Content-Type': 'application/json'
    }
    if(method=="POST"):
        response = httpClient.request(method, url+endpoint, headers=headers, data=params)
    else:
        response = httpClient.request(method, url+endpoint+"?"+params, headers=headers)
def genS(params):
    param_str= str(time_stamp) + API_KEY + recv_window + params
    hash = hmac.new(bytes(PRIVATE_KEY, "utf-8"), param_str.encode("utf-8"),hashlib.sha256)
    signature = hash.hexdigest()
    return signature
#get open position size
def get_size():
    endpoint="/v5/position/list"
    method="GET"
    params='category=linear&symbol=ETHUSDT'
    return float(HTTP_R(endpoint,method,params,"")["result"]["list"][0]["size"])

def get_candles(TIMEFRAME, n_candele, choice):
    endpoint="/v5/market/kline"
    method="GET"
    from_time = int(time.time()-n_candele*TIMEFRAME*60),
    limit = str(n_candele)
    params='category=linear&symbol=ETHUSDT&interval='+str(TIMEFRAME)+'&start='+str(from_time)+'&limit='+limit
    candles = (HTTP_R(endpoint,method,params,""))
    b=0
    lista = []
    for a in candles["result"]["list"]:
        open = candles["result"]["list"][b][1] #0
        high = candles["result"]["list"][b][2] #1
        low = candles["result"]["list"][b][3] #2
        close = candles["result"]["list"][b][4] #3
        volume = candles["result"]["list"][b][5] #4
        candela = np.array([open, high, low, close, volume])
        lista.append(candela)
        b+=1
    ndarray = np.array(lista, dtype='float')
    if choice =='open':
        return ndarray[:,0]
    if choice =='high':
        return ndarray[:,1]
    if choice =='low':
        return ndarray[:,2]
    if choice =='close':
        return ndarray[:,3]
    if choice =='volume':
        return ndarray[:,4]
def unpnl():
    endpoint="/v5/position/list"
    method="GET"
    params='category=linear&symbol=ETHUSDT'
    return float(HTTP_R(endpoint,method,params,"")["result"]["list"][0]["unrealisedPnl"])
def l_s():
    endpoint="/v5/position/list"
    method="GET"
    params='category=linear&symbol=ETHUSDT'
    x = float(HTTP_R(endpoint,method,params,"")["result"]["list"][0]["size"])
    if x > 0:
        signal = 'Buy'
        return signal
    elif float(HTTP_R(endpoint,method,params,"")["result"]["list"][1]["size"]) > 0:
        signal = 'Sell'
        return signal
    else:
        signal = 'uncertain'
        return signal
def entry_price():
    endpoint="/v5/position/list"
    method="GET"
    params='category=linear&symbol=ETHUSDT'
    if signal == 'Buy':
        x = (HTTP_R(endpoint,method,params,"")["result"]["list"][0]["avgPrice"])
    else:
        x = (HTTP_R(endpoint,method,params,"")["result"]["list"][1]["avgPrice"])
    return float(x)
#get leverage
def get_leverage():
    endpoint="/v5/position/list"
    method="GET"
    params='category=linear&symbol=ETHUSDT'
    x = float(HTTP_R(endpoint,method,params,"")["result"]["list"][0]["leverage"])
    if x > 0:
        return x
    if x == 0:
        x = float(HTTP_R(endpoint,method,params,"")["result"]["list"][1]["leverage"])
        return x
def set_leverage(leverage): 
    endpoint = "/v5/position/set-leverage"
    params = '{"category":"linear","symbol":"'+SYMBOL+'","buyLeverage":"'+str(leverage)+'","sellLeverage":"'+str(leverage)+'"}'
    method="POST"
    HTTP(endpoint,method,params,"Create")
def place_order(c): 
    endpoint="/v5/order/create"
    method="POST"
    orderLinkId=uuid.uuid4().hex
    # if signal == 'Buy':
    #     psid = 1
    # if signal == 'Sell':
    #     psid = 2
    psid = 0
    params='{"category":"linear","symbol": "'+SYMBOL+'","side": "'+signal+'","orderType": "Market","qty": "'+str(c)+'","positionIdx": "'+str(psid)+'","orderLinkId": "' + orderLinkId + '"}'
    HTTP(endpoint,method,params,"Create")
def close_position(): 
    endpoint="/v5/order/create"
    method="POST"
    orderLinkId=uuid.uuid4().hex
    c = get_size()
    if signal == 'Buy':
        psid = 1
        clo = 'Sell'
    if signal == 'Sell':
        psid = 2
        clo = 'Buy'
    psid = 0
    params='{"category":"linear","symbol": "'+SYMBOL+'","side": "'+clo+'","orderType": "Market","qty": "'+str(c)+'","positionIdx": "'+str(psid)+'","orderLinkId": "' + orderLinkId + '","reduceOnly": "' + 'true' + '"}'
    HTTP(endpoint,method,params,"Create")
def get_balance(): 
    endpoint = '/v5/account/wallet-balance'
    params = 'accountType=UNIFIED&coin=USDT'
    method = "GET"
    return float(HTTP_R(endpoint,method,params,'')["result"]["list"][0]["totalAvailableBalance"])
def last_price():
    endpoint="/v5/market/tickers"
    method="GET"
    params='category=linear&symbol=ETHUSDT'
    return float(HTTP_R(endpoint,method,params,"")["result"]["list"][0]["lastPrice"]) 
def leva():
    endpoint="/v5/position/closed-pnl"
    method="GET"
    params='category=linear&symbol=ETHUSDT'
    x = (HTTP_R(endpoint,method,params,""))['result']["list"]
    if float(x[0]["closedPnl"]) < 0 and float(x[1]["closedPnl"]) < 0 and float(x[2]["closedPnl"]) < 0:
        lev = 20
    elif float(x[0]["closedPnl"]) < 0:
        lev = 3
    else:
        lev = 2
    return lev
def get_cpnl():
    endpoint="/v5/position/closed-pnl"
    method="GET"
    params='category=linear&symbol=ETHUSDT'
    return float(HTTP_R(endpoint,method,params,"")['result']["list"][0]["closedPnl"])
def send_telegram_msg(bot_msg):
    token_id = ""
    chat_id = ""
    send_text = "https://api.telegram.org/bot"+token_id+"/sendMessage?chat_id="+chat_id+"&parse_mode=MarkdownV2&text="+bot_msg
    response = requests.get(send_text)
    return response.json()
def active_status(bot_msg):
    token_id = ""
    chat_id = ""
    send_text = "https://api.telegram.org/bot"+token_id+"/sendMessage?chat_id="+chat_id+"&parse_mode=MarkdownV2&text="+bot_msg
    response = requests.get(send_text)
    return response.json()
def _print(message, level='INFO'):
    """
    Just a custom print function. Better than logging.
    """
    if level == 'position':
        print(f'{dt.now()} - {message}.', end='\r')
    else:
        print(f'{dt.now()} - {level} - {message}.')
def print_info():
    print(f'{dt.now()}, last price: {last_price()}')
    print('')
def print_DATA():
    #print(f'{dt.now()}, last price: {last_price()}, rsi -1: {rsi()[-1]}, rsi -2: {rsi()[-2]}, basis: {basis()}, dev: {dev()}, lower: {lower()}, upper: {upper()}')
    print('')

def get_45_min_candles(TIMEFRAME, n_candele, choice):
    b=0
    lista = []
    endpoint="/v5/market/kline"
    method="GET"
    from_time = int(time.time()-n_candele*TIMEFRAME*60),
    limit = str(n_candele*3)
    interval = int(45/3)
    params='category=linear&symbol=ETHUSDT&interval='+str(interval)+'&start='+str(from_time)+'&limit='+limit
    candles = (HTTP_R(endpoint,method,params,""))
    contatore = 0
    temp_dic ={}
    apertura = []
    alto = []
    minimo = []
    chiusura = []
    vol = []
    for a in candles["result"]["list"]:
        open = float(candles["result"]["list"][b][1] )
        high = float(candles["result"]["list"][b][2] )
        low = float(candles["result"]["list"][b][3] )
        close = float(candles["result"]["list"][b][4] )
        volume = float(candles["result"]["list"][b][5] )
        apertura.append(open)
        alto.append(high)
        minimo.append(low)
        chiusura.append(close)
        vol.append(volume)
        temp_dic["open"] = apertura
        temp_dic["high"] = alto
        temp_dic["low"] = minimo
        temp_dic["close"] = chiusura
        temp_dic["volume"] = vol
        contatore +=1
        if contatore == 3:
            candela = np.array([temp_dic["open"][2], max(temp_dic["high"]), min(temp_dic["low"]), temp_dic["close"][0], sum(temp_dic["volume"])])
            lista.append(candela)
            contatore = 0
            temp_dic = {}
            apertura = []
            alto = []
            minimo = []
            chiusura = []
            vol = []
        b+=1
    lista.reverse()
    ndarray = np.array(lista, dtype='float')
    if choice =='open':
        return ndarray[:,0]
    if choice =='high':
        return ndarray[:,1]
    if choice =='low':
        return ndarray[:,2]
    if choice =='close':
        return ndarray[:,3]
    if choice =='volume':
        return ndarray[:,4]

##--strategy specific--#

def should_long():
    candele = get_45_min_candles(TIMEFRAME,N_CANDELE, SOURCE)
    return True
    
def should_short():
    candele = get_45_min_candles(TIMEFRAME,N_CANDELE, SOURCE)
    return True
    
def long_exit():
    return True
    
def short_exit():
    return True

        

while True:
    while True:
        try:
            _print('--matted--')
            #AUTH TEST
            if get_balance() >0:
                _print("AUTH TEST PASSED")
            active_status('AUTH')
            print_info()
            if get_size() == 0:
                signal = 'uncertain'
            else:
                _print("ALREADY IN A POSITION")
                signal = l_s()
                balanceusdt = get_balance()
                size = get_size()
                LEVERAGE = get_leverage()

            #----STRATEGY LOGIC----#
            t0 = int(time.time())
            while signal == 'uncertain':
                if should_long() == True:
                    signal = 'Buy'
                    print(' ')
                    _print('--LONG--')
                    print(' ')
                    v = str(last_price())
                    v = v.replace('.', ',')
                    msg = (f'\U0001F9ECmatted\n\U0001F4CDSymbol {SYMBOL}\n\U0001F4B0Price {v} \n\U0001F4C8Direction {signal} ')
                    send_telegram_msg(msg)
                    
                elif should_short() == True:
                    signal = 'Sell'
                    print(' ')
                    v = str(last_price())
                    v = v.replace('.', ',')
                    msg = (f'\U0001F9ECmatted\n\U0001F4CDSymbol {SYMBOL}\n\U0001F4B0Price {v} \n\U0001F4C8Direction {signal} ')
                    send_telegram_msg(msg)
                    _print('--SHORT--')
                    print(' ')
                else:
                    signal = 'uncertain'
                t1 = int(time.time())
                if t1-t0 > 3600:
                    active_status("matteALIVEWaitingForSIGNAL")
                    print_info()
                    print_DATA()
                    t0 = int(time.time())
                #----STRATEGY EXECUTION---#
                balanceusdt = round(get_balance(),3)
                last = last_price()
                balanceSYMBOL = balanceusdt/last
                LEVERAGE = leva()
                size = round(balanceSYMBOL * EQUITY * LEVERAGE * (1 - (0.0006 * 2)) ,2)
                if size < 0.01:
                    size = 0.01
                if LEVERAGE < 1:
                    LEVERAGE = 1
            if get_leverage() != LEVERAGE:
                try:
                    set_leverage(LEVERAGE)
                except:
                    pass
            _print(f'balanceusdt: {balanceusdt}, size: {size}, leva: {LEVERAGE}')
            if get_size() == 0:
                place_order(size)
                print_DATA()
                print_info()
                _print(f'{signal} {size} {SYMBOL} at {last}')
            else:
                print('error - already in a position')
            #wait to get the position
            while get_size() == 0:
                time.sleep(2)
            #positioned
            signal_t0=time.time()
            entry = entry_price()
            _print(f'Executed at {entry}')  
            t0 =int(time.time())     

            #----STRATEGY MONITORING---#
            while get_size() != 0:
                candele = get_45_min_candles(TIMEFRAME,N_CANDELE, SOURCE)
                if signal == 'Buy' and long_exit() == True:
                    close_position()
                    print_DATA()
                    print(' ')
                    _print('--LONG EXIT--')
                    print(' ')
                if signal == 'Sell' and short_exit() == True:
                    close_position()
                    print_DATA()
                    print(' ')
                    _print('--SHORT EXIT--')
                    print(' ')
                if signal == 'Sell':
                    #SL FOR SHORT
                    if (entry-last_price())/entry*100 <= -SL and should_short()==False:
                        close_position()
                        print_DATA()
                        signal_t1 = time.time() 
                        v = str(last_price())
                        v = v.replace('.', ',')
                        msg = (f'matted: STOP LOSS CLOSE PREVIOUS SHORT \n\U0001F4CDSymbol {SYMBOL}\n\U0001F4B0Price {v}')
                        send_telegram_msg(msg)
                    #dynamic leverage
                    # if LEVERAGE >= 15 or LEVERAGE == 2:
                    #     #x1
                    #     if increased_count==0 and (-last_price() + entry)/entry*100 >= 1.7:
                    #         LEVERAGE = LEVERAGE*2
                    #         if get_leverage() != LEVERAGE:
                    #             set_leverage(LEVERAGE)
                    #         place_order(get_size())
                    #         print_DATA()
                    #         increased_count = 1
                    #     #x2
                    #     if increased_count==1 and (-last_price() + entry)/entry*100 >= 2.3:
                    #         LEVERAGE = LEVERAGE*2
                    #         if get_leverage() != LEVERAGE:
                    #             set_leverage(LEVERAGE)
                    #         place_order(get_size())
                    #         print_DATA()
                    #         increased_count = 2
                if signal == 'Buy':
                    #SL FOR LONG
                    if (entry-last_price())/entry*100 >= SL and should_long()==False:
                        close_position()
                        print_DATA()
                        signal_t1 = time.time() 
                        v = str(last_price())
                        v = v.replace('.', ',')
                        msg = (f'Matte: STOP LOSS CLOSE PREVIOUS LONG \n\U0001F4CDSymbol {SYMBOL}\n\U0001F4B0Price {v}')                        
                        send_telegram_msg(msg)
                    #dynamic leverage
                    # if LEVERAGE >= 15 or LEVERAGE == 2:
                    #     #x1
                    #     if increased_count==0 and (last_price() - entry)/entry*100 >= 1.7:
                    #         LEVERAGE = LEVERAGE*2
                    #         if get_leverage() != LEVERAGE:
                    #             set_leverage(LEVERAGE)
                    #         place_order(get_size())
                    #         print_DATA()
                    #         increased_count = 1
                    #     #x2
                    #     if increased_count==1 and (last_price() - entry)/entry*100 >= 2.3:
                    #         LEVERAGE = LEVERAGE*2
                    #         if get_leverage() != LEVERAGE:
                    #             set_leverage(LEVERAGE)
                    #         place_order(get_size())
                    #         print_DATA()
                    #         increased_count = 2
                time.sleep(5)
                t1 = int(time.time())
                if t1-t0 > 3600:
                    active_status("ALIVEHoldingPosition")
                    _print(f'HOLDING POSITION, size: {get_size()}, un_pnl: {unpnl()}')    
                    print_info()
                    t0 = int(time.time())
                time.sleep(1)
            #----TRADING RESULTS----#
            signal_t1 = time.time()
            holding_time = signal_t1-signal_t0
            time.sleep(10)
            cpnl = get_cpnl()
            print(f'{signal}: {cpnl["avg_entry_price"]}->{cpnl["avg_exit_price"]}, PNL: {cpnl["closed_pnl"]}')
            v = str(last_price())
            v = v.replace('.', ',')
            msg = (f'matted: CLOSE PREVIOUS TRADE \n\U0001F4CDSymbol {SYMBOL}\n\U0001F4B0Price {v}')
            send_telegram_msg(msg)

        except Exception as e:
            _print(e)
            e = str(e)
            e = e.partition('(')[0]
            print(traceback.format_exc())
            try:
                send_telegram_msg(e)
                time.sleep(2)
            finally:
                time.sleep(10)
                break
