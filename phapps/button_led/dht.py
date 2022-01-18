import json
import sys
import time
import threading
import logging
import board
import adafruit_dht

class DHT:
    def __init__(self):
        self.state = {}
        self.settings = {
            "notify_url": None,
            "pin": 5,
            "scan_time": 1,
            "log_level": logging.INFO
        }
        self.listener_thread_running = False
        self.listener_thread_paused = True
        self.device = None
        
    def send(self, data):
        payload = {
            "headers": {
                "to": self.settings["notify_url"]
            },
            "body": data
        }
        print("<<" + json.dumps(payload), flush=True)

    def update_state(self):
        self.state["is_pressed"] = self.device.is_pressed

        self.send({
            "state": self.state,
            "settings": self.settings
        })
    
    def receive(self):
        print("Ready to receive commands from socket ...", flush=True)
        for line in sys.stdin:
            sMessage = line[:-1]
            
            if(sMessage[0:3] == '>>{'):
                message = json.loads(sMessage[2:])
                try:
                    self.process(message)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(e, file=sys.stderr, flush=True)

    def process(self, message):
        message_body = message["body"]

        if("action" in message_body):
            action = message_body["action"]
        
            if(action == "STATUS"):
                self.update_state()
                return
            
            if(action == "SETUP"):
                given_settings = message_body["settings"]
                if("pin" in given_settings):
                    self.settings["pin"] = given_settings["pin"]
                if("scan_time" in given_settings):
                    self.settings["scan_time"] = given_settings["scan_time"]
                if("log_level" in given_settings):
                    self.settings["log_level"] = given_settings["log_level"]
                self.init()
                self.update_state()
                return
    
    def listen_target(self):
        try:
            print("Listening for temperature and humidity ...", flush=True)
            self.listener_thread_running = True
            while self.listener_thread_running:
                if(not self.listener_thread_paused):
                    temperature_c = self.device.temperature
                    temperature_f = temperature_c * (9 / 5) + 32
                    humidity = self.device.humidity
                    if(self.settings["log_level"] < logging.INFO):
                        print(
                            "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                                temperature_f, temperature_c, humidity
                            ), flush=True
                        )
                    self.update_state()
                time.sleep(self.settings["scan_time"])
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e, file=sys.stderr, flush=True)
        finally:
            self.listener_thread_running = False
    
    def listen(self):
        if(self.listener_thread_running):
            print("Listener thread already running.", flush=True)
        else:
            threading.Thread(target=self.listen_target).start()
    
    def init(self):
        if(self.device is not None):
            self.listener_thread_paused = True
            self.device.exit()
            print("Closed DHT device.", flush=True)
        self.device = adafruit_dht.DHT22(board.D4) #adafruit_dht.DHT11(self.settings["pin"])
        self.listener_thread_paused = False
        print("Initialized DHT device on pin " + str(self.settings["pin"]), flush=True)


    def cleanup(self):
        self.listener_thread_paused = True
        self.listener_thread_running = False
        if(self.device is not None):
            self.device.exit()
            print("Closed DHT device.", flush=True)
        
        print("Cleaned up.")

try:
    dht = DHT()
    dht.init()
    dht.listen()
    dht.receive()
except KeyboardInterrupt:
    print('Good Bye!')
finally:
    dht.cleanup()
