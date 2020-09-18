
import hmac
import base64
import hashlib
import json
import time




# BCH/USDT，BSV/USDT，ETC/USDT，LINK/USDT，
# YFI/USDT，YFII/USDT，YFV/USDT

import ssl
from websocket import create_connection
ws = create_connection("wss://ws.gate.io/v3/",http_proxy_host="127.0.0.1",http_proxy_port="7890",sslopt={"cert_reqs": ssl.CERT_NONE})



ws.send('{"id":12312, "method":"ticker.subscribe", "params":["BTC_USDT"]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["EOS_USDT"]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["ETH_USDT"]}')

# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["BCH_USDT"]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["BCHSV_USDT"]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["ETC_USDT"]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["LINK_USDT"]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["YFI_USDT"]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["YFII_USDT"]}')
# ws.send('{"id":12312, "method":"ticker.subscribe", "params":["YFV_USDT"]}')


while 1:
    print(ws.recv())
    time.sleep(1)




