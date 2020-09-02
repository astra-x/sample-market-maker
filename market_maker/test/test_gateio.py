from websocket import create_connection
ws = create_connection("wss://ws.gate.io/v3/")
print(ws)
# single-market mode subscription
ws.send('{"id":12312, "method":"depth.subscribe", "params":["ETH_USDT", 5, "0.0001"]}')
print(ws.recv())

# ---------------------------------------------------------------------------------
# If you want to subscribe multi market depth, just replace ws.send as below.
# ---------------------------------------------------------------------------------
# multi-market mode subscription
ws.send('{"id":12312, "method":"depth.subscribe", "params":[["BTC_USDT", 5, "0.01"], ["ETH_USDT", 5, "0"]]}')
print(ws.recv())

