# import time
# from websocket import create_connection
# ws = create_connection("ws://18.183.178.183:19090")
# ws.send('{"method":"depth.query","id":1516681176,"params":["BTC/USDT",20,"0"]}')
# while True:
#     print(ws.recv())
#     time.sleep(1)



# import time
# from websocket import create_connection
# ws = create_connection("wss://api.huobi.pro/ws")
# ws.send('{"sub":"market.btcusdt.trade.detail","id":"id1"}')
# while True:
#     print(ws.recv())
#     time.sleep(1)


import ssl
import time
from websocket import create_connection
# ws = create_connection("wss://fx-ws-testnet.gateio.ws/v4/ws/btc",sslopt={"cert_reqs": ssl.CERT_NONE})
# ws.send('{"time" : 123456, "channel" : "futures.trades", "event": "subscribe", "payload" : ["BTC_USD"]}')
# while True:
#     print(ws.recv())
#     time.sleep(1)
#

# from websocket import create_connection
# ws = create_connection("wss://ws.gate.io/v3/")
# # single-market mode subscription
# ws.send('{"id":12312, "method":"depth.subscribe", "params":["ETH_USDT", 5, "0.0001"]}')
# print(ws.recv())
#
# # ---------------------------------------------------------------------------------
# # If you want to subscribe multi market depth, just replace ws.send as below.
# # ---------------------------------------------------------------------------------
# # multi-market mode subscription
# ws.send('{"id":12312, "method":"depth.subscribe", "params":[["BTC_USDT", 5, "0.01"], ["ETH_USDT", 5, "0"]]}')
# print(ws.recv())



# from websocket import create_connection
# ws = create_connection("wss://ws.gate.io/v3/")
# ws.send('{"id":12312, "method":"server.ping", "params":[]}')
# print(ws.recv())
# a=1.111
# print("%.4f"%a)