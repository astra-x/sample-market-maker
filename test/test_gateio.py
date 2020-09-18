
import hmac
import base64
import hashlib
import json
import time
from websocket import create_connection

# api_key = 'your api key'
# secret_key = 'your secret key'
#
# def get_sign(secret_key, message):
#     h = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha512)
#     return base64.b64encode(h.digest()).decode()
#
#
# ws = create_connection("wss://ws.gateio.io/v3/")
#
# nonce = int(time.time() * 1000)
# signature = get_sign(secret_key, str(nonce))
#
# ws.send(json.dumps({
#     "id": 12312,
#     "method": "server.sign",
#     "params": [api_key, signature, nonce]
#     }))
# print(ws.recv())


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





import ssl
from websocket import create_connection
ws = create_connection("wss://ws.gate.io/v3/",http_proxy_host="127.0.0.1",http_proxy_port="7890",sslopt={"cert_reqs": ssl.CERT_NONE})

# ws.send('{"id":12312, "method":"ticker.query", "params":["EOS_USDT", 86400]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["BOT_USDT"]}')
# ws.send('{"id":12309, "method":"trades.query", "params":["EOS_USDT", 2, 7177813]}')
# ws.send('{"id":12312, "method":"trades.subscribe", "params":["BSV_USDT"]}')

# ws.send('{"id":12312, "method":"depth.query", "params":["BSV_USTD", 5, "0.0001"]}')

ws.send('{"id":12312, "method":"depth.subscribe", "params":[["BSV_USTD", 5, "0.01"]]}')


while 1:
    print(ws.recv())
    time.sleep(1)

# import ssl
#
# from websocket import create_connection
# ws = create_connection("wss://fx-ws-testnet.gateio.ws/v4/ws",sslopt={"cert_reqs": ssl.CERT_NONE})
# ws.send('{"id":12309, "method":"trades.query", "params":["EOS_USDT", 2, 7177813]}')
# print(ws.recv())

#
# from websocket import create_connection
# import ssl
#
# ws = create_connection("wss://fx-ws-testnet.gateio.ws/v4/ws/btc",sslopt={"cert_reqs": ssl.CERT_NONE})
# ws.send('{"time" : 123456, "channel" : "futures.tickers", "event": "subscribe", "payload" : ["YFV_USD"]}')
# while 1:
#     print(ws.recv())
#     time.sleep(1)


