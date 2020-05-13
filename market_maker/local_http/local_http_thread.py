
import requests
import time
import threading


# poll as often as it wants.
class LocalHttpDataServer():
    # Don't grow a table larger than this amount. Helps cap memory usage.
    def __init__(self,url):
        self.url=url
        self.data={}
        # 起一个线程去执行请求
        t1 = threading.Thread(target=self.loop_request_get_current_price)
        t1.daemon = True
        t1.start()


    def exit(self):

        return False

    def loop_request_get_current_price(self):
        while True:
            response=None
            try:
                response = requests.request(method="GET",url= self.url)
            except Exception as e:
                print("LocalHttpDataServer-------->e:{}".format(e))

            if response:
                data={}
                try:
                    data=response.json()
                except Exception as e:
                    print("LocalHttpDataServer-------->e:{}".format(e))

                if data:
                    current_price=data.get("current_price")
                    if current_price:
                       self.data["current_price"]=current_price

            time.sleep(1)


    def get_ticker(self):

        return self.data

