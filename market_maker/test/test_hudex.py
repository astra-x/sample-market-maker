import json
import time
from websocket import create_connection
ws = create_connection("ws://18.183.178.183:19090")
data = {
    "method": "depth.query",
    "id": 1516681176,
    "params": [
        "BTC/USDT",
        20,
        "0"
    ]
}
json_data = json.dumps(data)

ws.send(json_data)

while True:
    start=time.time()
    print("------------------------开始-----------------")
    print(ws.recv())
    end=time.time()
    spend_time=end-start
    print("耗时多少：{}".format(spend_time))
    print("------------------------结束-----------------")

