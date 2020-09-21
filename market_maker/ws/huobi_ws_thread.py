
import threading
import json
import logging
import ssl
import gzip
import time
from market_maker import settings
from websocket import create_connection



# poll as often as it wants.
class HuobiWebsocket():
    
    def __init__(self):
        self.retries = 0  # initialize counter
        self.data={}
        self.connect(endpoint=settings.HUOBI_URL)
        self.subscribe_depath(settings.SubTopicDepath)
        self.put_data()
        time.sleep(5)

    def connect(self, endpoint,max_retries=3):
        def retry():
            self.retries += 1
            if self.retries > max_retries:
                raise Exception("already max_retries ...")
            return self.connect(endpoint=settings.HUOBI_URL)
        try:
            self.ws = create_connection(endpoint,sslopt={"cert_reqs": ssl.CERT_NONE})
        except:
            logging.error("cannot connect huobi")
            retry()

    def put_data(self):
        def put_data_thread():
            while True:
                try:
                    recv = gzip.decompress(self.ws.recv()).decode("utf-8")
                    data = json.loads(recv)
                    if "tick" in data:
                        self.data[data["ch"]]=data["tick"]
                except:
                    logging.error("connect huobi err")
                    self.connect(settings.HUOBI_URL)
                    self.subscribe_depath(settings.SubTopicDepath)
                time.sleep(0.1)
        t=threading.Thread(target=put_data_thread)
        t.daemon = True
        t.start()

    # 订阅请求发送
    # 订阅盘口
    def subscribe_depath(self,topic):
        data = {"sub":topic, "id": "id1"}
        try:
            json_data = json.dumps(data)
            self.ws.send(json_data)
        except:
            print("error subscribe depath ")
            raise Exception("error subscribe depath ")

    def get_depath(self,topic):
        ticker = self.data[topic] if self.data.get(topic) else {}
        return ticker


if __name__ == "__main__":
    # create console handler and set level to debug
    HuobiWebsocket()
    time.sleep(1000)