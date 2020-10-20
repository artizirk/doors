from urllib import request
import requests
import socket
import time
while 1:
    print("loop")
    try:
        # r = request.urlopen("https://wut.ee/notify/abc", timeout=5)
        r = requests.get("https://wut.ee/notify/abc",
                         headers={"Connection": "close", "accept": "*/*"},
                         timeout=5)
        print("Got notification:", r.text)
    except requests.Timeout as e:
        print("notification timeout")
        time.sleep(0.1)
    except KeyboardInterrupt as e:
        print("exit")
        break

