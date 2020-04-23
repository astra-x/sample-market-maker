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
class ClientWebsocket():
    # Don't grow a table larger than this amount. Helps cap memory usage.
    MAX_TABLE_LEN = 200

    def __init__(self):
        self.logger = logging.getLogger('root')
        self.subscriptions=[settings.ClientContract]
        self.__reset()

    def __del__(self):
        self.exit()

    def connect(self, endpoint, symbol):
        '''Connect to the websocket and initialize data stores.'''
        self.symbol = symbol
        # Get WS URL and connect.
        wsURL = endpoint
        self.logger.info("Connecting to %s" % wsURL)
        self.__connect(wsURL)
        # 订阅盘口
        self.subscribe_depath()

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

        ssl_defaults = ssl.get_default_verify_paths()
        sslopt_ca_certs = {'ca_certs': ssl_defaults.cafile}
        self.ws = websocket.WebSocketApp(wsURL,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,

                                         )

        setup_custom_logger('websocket', log_level=settings.LOG_LEVEL)
        self.wst = threading.Thread(
            target=lambda: self.ws.run_forever(sslopt=sslopt_ca_certs))
        self.wst.daemon = True
        self.wst.start()
        self.logger.info("Started thread")

        # Wait for connect before continuing
        conn_timeout = 5
        # print("self.ws.sock:",self.ws.sock)
        # print("self.ws.sock.connected:",self.ws.sock.connected)
        while (not self.ws.sock or not self.ws.sock.connected) and conn_timeout and not self._error:
            sleep(1)
            conn_timeout -= 1

        if not conn_timeout or self._error:
            self.logger.error("Couldn't connect to client WS! Exiting.")
            self.exit()
            sys.exit(1)


    def __on_message(self, message):
        '''Handler for parsing WS messages.'''
        message = json.loads(message)

        if "method" in message:
            method = message["method"]

            if method == "depth.update":
                symbol =message['params'][2]
                data_flag=symbol+"_"+method
                self.data[data_flag] = message['params']



    def __on_open(self):
        self.logger.debug("Websocket Opened.")

    def __on_close(self):
        self.logger.info('Websocket Closed')
        self.exit()

    def __on_error(self, ws, error):
        if not self.exited:
            self.error(error)

    def __reset(self):
        self.data = {}
        self.keys = {}
        self.exited = False
        self._error = None

# 订阅请求发送
    #订阅盘口
    def  subscribe_depath(self):
        for subcribe in self.subscriptions:
            data={
                "method": "depth.subscribe",
                "id": 1516681176,
                "params": [
                    subcribe,
                    20,
                    "0"
                ]
            }
            try:
                json_data = json.dumps(data)
                self.ws.send(data=json_data)
            except:
                print("error subscribe depath ")
                raise Exception("error subscribe depath ")



    def get_depath(self,symbol):
        # 为了将价格与数量按顺序排列
        for k,v in self.data.items():
            if k==symbol+"_depth.update":
                return v
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
    ws = ClientWebsocket()
    ws.logger = logger
    ws.connect("ws://47.56.8.19:19090")
    while (ws.ws.sock.connected):
        data = {
            "method": "depth.subscribe",
            "id": 1516681176,
            "params": [
                "ICPDCA",
                20,
                "0"
            ]
        }
        json_data = json.dumps(data)
        ws.ws.send(data=json_data)
        sleep(1)

