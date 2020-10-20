import logging
import threading
import requests
import time

from .wiegand import Decoder

logging.basicConfig(level=logging.DEBUG)


class Main:

    def __init__(self, api_user, api_key):
        self.cards = {}
        self.force_sync_now = threading.Event()
        self.session =  requests.Session()
        self.session.auth = (api_user, api_key)
        self.sync_cards()
        logging.info("Running")
        self.wiegand = Decoder(self.wiegand_callback)
        self.notify_thread = threading.Thread(target=self.listen_notification, daemon=True)
        self.notify_thread.start()
        self.auto_sync_loop()

    def sync_cards(self):
        logging.info("Downloading users list")
        r = self.session.get("http://127.0.0.1:8080/api/v1/cards")
        users = r.json()["keycards"]
        cards = {}
        for user in users:
            cards[user["card_uid"].strip()] = user
        self.cards = cards

    def wiegand_callback(self, bits, value):
        print("bits", bits, "value", value)
        u = self.cards.get(value)
        if u:
            print("user", u)
            self.wiegand.open_door()

    def listen_notification(self):
        while 1:
            try:
                r = requests.get("https://wut.ee/notify/abc",
                                 headers={"Connection": "close"},
                                 timeout=60)
                logging.debug("Got notification: %s", r.text)
                self.force_sync_now.set()
            except requests.Timeout as e:
                logging.debug("notification timeout")
                time.sleep(0.1)

    def auto_sync_loop(self):
        while 1:
            try:
                self.force_sync_now.wait(60*10)  # == 10min
                self.force_sync_now.clear()
                self.sync_cards()
            except KeyboardInterrupt as e:
                self.wiegand.cancel()
                break
