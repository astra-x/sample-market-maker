import threading
import json
import logging
import ssl
import gzip
import time
from market_maker import settings
from websocket import create_connection


# poll as often as it wants.
class GateioWebsocket():

    def __init__(self):
        self.retries = 0  # initialize counter
        self.data = {}
        self.connect(endpoint=settings.GATEIO_URL)
        self.subscribe_ticker(settings.SUB_TOPIC_TICKER)
        self.put_data()
        time.sleep(5)

    def connect(self, endpoint, max_retries=7):
        def retry():
            self.retries += 1
            if self.retries > max_retries:
                raise Exception("already max_retries ...")
            return self.connect(endpoint=settings.GATEIO_URL)

        try:
            if settings.PROXY:
                self.ws = create_connection(endpoint, sslopt={"cert_reqs": ssl.CERT_NONE}, http_proxy_host="127.0.0.1",
                                            http_proxy_port="7890")
            else:
                self.ws = create_connection(endpoint, sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            logging.error("cannot connect gateio")
            retry()

    def put_data(self):
        def put_data_thread():
            while True:
                try:
                    recv = self.ws.recv()
                    message = json.loads(recv)
                    channel = message['method'] if 'method' in message else None
                    if channel == "ticker.update":
                        self.data[message["params"][0]] = message["params"][1]
                        print("self.data:",self.data)
                except:
                    logging.error("connect gateio err")
                    self.connect(settings.GATEIO_URL)
                    self.subscribe_ticker(settings.SUB_TOPIC_TICKER)
                time.sleep(0.1)

        t = threading.Thread(target=put_data_thread)
        t.daemon = True
        t.start()

    # 订阅请求发送
    # 订阅盘口
    def subscribe_ticker(self, topic):
        data = {
            "id": 12312,
            "method": topic,
            "params": [settings.CONTRACT]
        }
        try:
            json_data = json.dumps(data)
            self.ws.send(json_data)
        except:
            print("error subscribe ticker ")
            raise Exception("error subscribe ticker ")

    def get_ticker(self):
        contract=settings.CONTRACT
        ticker=[]
        if  contract in self.data:
            ticker=self.data[contract] if self.data[contract] else []
        return ticker


if __name__ == "__main__":
    # create console handler and set level to debug
    GateioWebsocket()
    time.sleep(1000)