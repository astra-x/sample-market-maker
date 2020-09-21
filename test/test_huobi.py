#
from websocket import create_connection
import ssl
import gzip
import time
import json
ws = create_connection("wss://api-cloud.huobi.co.kr/ws", http_proxy_host="127.0.0.1", http_proxy_port="7890",
                       sslopt={"cert_reqs": ssl.CERT_NONE})
print(ws)
# single-market mode subscription
ws.send('{"sub": "market.usdtkrw.depth.step0","id": "id1"}')

while 1:
    try:
        # if type(ws.recv()) == bytes:
        #     print("type:", type(ws.recv()))
        recv = gzip.decompress(ws.recv()).decode("utf-8")
        data=json.loads(recv)
        print("ungzip data: ", type(data))
        time.sleep(1)
    except:
        print("connect err")
        ws = create_connection("wss://api-cloud.huobi.co.kr/ws", http_proxy_host="127.0.0.1", http_proxy_port="7890",
                               sslopt={"cert_reqs": ssl.CERT_NONE})
        ws.send('{"sub": "market.usdtkrw.depth.step0","id": "id1"}')
