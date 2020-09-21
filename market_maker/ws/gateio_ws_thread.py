import sys, os
# RootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(RootDir)
import websocket
import threading
import ssl
from time import sleep
import json
import logging
from market_maker import settings
from market_maker.utils.log import setup_custom_logger

from future.standard_library import hooks

with hooks():  # Python 2/3 compat
    from urllib.parse import urlparse, urlunparse

# poll as often as it wants.
class GateioWebsocket():
    # Don't grow a table larger than this amount. Helps cap memory usage.
    MAX_TABLE_LEN = 200
    def __init__(self):
        self.logger = logging.getLogger('root')
        self.__reset()

    def __del__(self):
        self.exit()

    def connect(self, endpoint, symbol):
        '''Connect to the websocket and initialize data stores.'''
        self.symbol = symbol
        # Get WS URL and connect.
        wsURL= os.path.join(endpoint,self.symbol)
        self.logger.info("Connecting to %s" % wsURL)
        self.__connect(wsURL)
        # 订阅盘口
        self.subscribe()
        self.logger.info('Connected to WS. Waiting for data images, this may take a moment...')


    # Lifecycle methods
    def error(self, err):
        self._error = err
        self.logger.error(err)
        self.exit()

    def exit(self):
        self.exited = True
        self.ws.close()

    #
    # Private methods
    def __connect(self, wsURL):
        '''Connect to the websocket in a thread.'''
        self.logger.debug("Starting thread")

        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error)

        setup_custom_logger('websocket', log_level=settings.LOG_LEVEL)
        if settings.PROXY:
            self.wst = threading.Thread(
                target=lambda: self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE},http_proxy_host="127.0.0.1",http_proxy_port="7890"))
        else:
            self.wst = threading.Thread(
                target=lambda: self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE}))
        self.wst.daemon = True
        self.wst.start()
        self.logger.info("Started thread")

        # Wait for connect before continuing
        conn_timeout = 10
        # print("self.ws.sock:",self.ws.sock)
        # print("self.ws.sock.connected:",self.ws.sock.connected)
        while (not self.ws.sock or not self.ws.sock.connected) and conn_timeout and not self._error:
            sleep(1)
            conn_timeout -= 1

        if not conn_timeout or self._error:
            self.logger.error("Couldn't connect to gateio WS! Exiting.")
            self.exit()
            sys.exit(1)


    def __on_message(self, message):
        '''Handler for parsing WS messages.'''
        message = json.loads(message)
        channel = message['method'] if 'method' in message else None
        if channel=="ticker.update":
            self.data[message["params"][0]]=message["params"][1]

    def __on_open(self):
        self.logger.debug("Websocket Opened.")

    def __on_close(self):
        self.logger.info('Websocket Closed')
        self.exit()

    def __on_error(self,  error):
        if not self.exited:
            self.error(error)

    def __reset(self):
        self.data = {}
        self.keys = {}
        self.exited = False
        self._error = None

    def subscribe(self):
        self.subscribe_ticker()
        self.subscribe_trades()


# 订阅请求发送
    #订阅盘口
    def  subscribe_ticker(self):
        data={
            "id": 12312,
            "method": settings.SUB_TOPIC_TICKER,
            "params": [settings.CONTRACT]
        }
        try:
            json_data = json.dumps(data)
            self.ws.send(data=json_data)
        except:
            print("error subscribe ticker ")
            raise Exception("error subscribe ticker ")

    def subscribe_trades(self):
       pass

    def get_ticker(self):
        contract=settings.CONTRACT
        ticker=[]
        if  contract in self.data:
            ticker=self.data[contract] if self.data[contract] else []
        return ticker

    def get_trades(self):
        return []



if __name__ == "__main__":
    # create console handler and set level to debug
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    # create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    ws = GateioWebsocket()
    ws.logger = logger
    ws.connect("wss://fx-ws-testnet.gateio.ws/v4/ws")
    while (ws.ws.sock.connected):
        data = {
            "channel": "futures.tickers",
            "time": 1,
            "event": "subscribe",
            "payload": [settings.CONTRACT]
        }
        json_data = json.dumps(data)
        ws.ws.send(data=json_data)
        sleep(1)


