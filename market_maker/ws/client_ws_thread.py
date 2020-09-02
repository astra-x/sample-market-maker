import sys, os
# RootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(RootDir)

import json
from market_maker.settings import settings
from websocket import create_connection

class ClientWebsocket(object):

    def __init__(self):
        self.data = {}
        self.connect()

    def connect(self):
        self.ws = create_connection(settings.Client_WS_URL)

    def query_depath(self):
        data = {"method": "depth.query","id": 1516681176,"params": [settings.ClientContract, 20,"0"]}
        json_data = json.dumps(data)
        self.ws.send(json_data)
        depath_info = json.loads(self.ws.recv())
        if "error" in depath_info and depath_info["error"] == None:
            self.data["depath"] = depath_info["result"]



if __name__ == "__main__":
    wsclient = ClientWebsocket()
    wsclient.connect()
    wsclient.query_depath()
    print(wsclient.data)
