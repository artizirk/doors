#!/bin/python
import logging
from smartcard.util import toHexString
#import settings

try:
    import pigpio
except Exception:
    pigpio = False

class Decoder:
    """
   A class to read Wiegand codes of an arbitrary length.
   """

    def __init__(self, callback, bit_timeout=5):

        """
        Instantiate with the pi, gpio for 0 (green wire), the gpio for 1
        (white wire), the callback function, and the bit timeout in
        milliseconds which indicates the end of a code.

        The callback is passed the code length in bits and the hex value.
        """
        if pigpio:
            self.pi = pigpio.pi()
        else:
            self.pi = False

        self.gpio_0 = 17 #settings.WIEGAND[0]
        self.gpio_1 = 18 #settings.WIEGAND[1]

        self.callback = callback

        self.bit_timeout = bit_timeout
        self.items = []
        self.in_code = False

        if self.pi:
            self.pi.set_mode(self.gpio_0, pigpio.INPUT)
            self.pi.set_mode(self.gpio_1, pigpio.INPUT)

            self.pi.set_pull_up_down(self.gpio_0, pigpio.PUD_UP)
            self.pi.set_pull_up_down(self.gpio_1, pigpio.PUD_UP)

            self.cb_0 = self.pi.callback(self.gpio_0, pigpio.FALLING_EDGE, self._cb)
            self.cb_1 = self.pi.callback(self.gpio_1, pigpio.FALLING_EDGE, self._cb)

    def cut_empty(self, item):
        if item[0:8] == "00000000":
            return self.cut_empty(item[8:])
        else:
            return item


    def get_hex(self):
        try:
            items = self.items
            if len(self.items) == 26:
                items = self.items[1:-1]
            elif len(self.items) == 64:
                items = self.cut_empty(self.items)

            bits = []
            for i in range(len(items), 0, -8):
                bits.append(int(items[i - 8:i], 2))
            return toHexString(bits)

        except ValueError:
            logging.error("Wiegand convert error: bin to hex convertion ended with ValeError. raw: " + str(self.items))
            return False

        except Exception as e:
            logging.error("Wiegand convert error: (raw: " + str(self.items) + ") "  + str(e))
            return False

    def _cb(self, gpio_pin, level, tick):

        """
        Accumulate bits until both gpios 0 and 1 timeout.
        """

        try:
            if level < pigpio.TIMEOUT:

                if self.in_code:
                    self.bits += 1
                else:
                    logging.debug("Wiegand data transfer start")
                    self.bits = 1
                    self.items = ""
                    self.in_code = True
                    self.code_timeout = 0
                    self.pi.set_watchdog(self.gpio_0, self.bit_timeout)
                    self.pi.set_watchdog(self.gpio_1, self.bit_timeout)

                if gpio_pin == self.gpio_0:
                    self.code_timeout &= 2  # clear gpio 0 timeout
                    self.items += "1"
                else:
                    self.code_timeout &= 1  # clear gpio 1 timeout
                    self.items += "0"

            else:

                if self.in_code:

                    if gpio_pin == self.gpio_0:
                        self.code_timeout |= 1  # timeout gpio 0
                    else:
                        self.code_timeout |= 2  # timeout gpio 1

                    if self.code_timeout == 3:  # both gpios timed out
                        self.pi.set_watchdog(self.gpio_0, 0)
                        self.pi.set_watchdog(self.gpio_1, 0)
                        self.in_code = False

                        if self.bits >= 26:
                            hex = self.get_hex()
                            if hex:
                                self.callback(self.bits, hex)
                        else:
                            logging.error("Wiegand receive error: Expected at least 26 got %i bits. raw: %s" %(self.bits, self.items))

        except Exception as e:
            logging.error("Wiegand callback error: " + str(e))

    def cancel(self):

        """
        Cancel the Wiegand decoder.
        """

        self.cb_0.cancel()
        self.cb_1.cancel()
        self.pi.stop()




if __name__ == "__main__":
    from urllib.request import urlopen
    import json

    print("downloading users list")
    r = urlopen("http://127.0.0.1:8080/api/v1/cards")
    users = json.loads(r.read().decode())["keycards"]
    cards = {}
    for user in users:
        cards[user["card_uid"].strip()] = user

    def wiegand_callback(bits, value):
        print("bits", bits)
        print("value", value)
        print("user", cards.get(value))

    logging.basicConfig(level=logging.DEBUG)

    print("Running")
    w = Decoder(wiegand_callback)
    from time import sleep
    while 1:
        sleep(1)


