import gpiozero
import json
import sys
import time
import threading
import logging

class Ky004:
    def __init__(self):
        self.version = "0.9.2"
        self.state = {}
        self.settings = {
            "notify_url": "fhtp://broadcast/{DEVICE}/app/{APP}/script/{SCRIPT}",
            "pin": 5,
            "hold_time": 1,
            "bounce_time": None,
            "retry_time": 1,
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
            "version": self.version,
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
                init_required=False
                given_settings = message_body["settings"]
                if("pin" in given_settings):
                    self.settings["pin"] = given_settings["pin"]
                    init_required=True
                if("hold_time" in given_settings):
                    self.settings["hold_time"] = given_settings["hold_time"]
                if("bounce_time" in given_settings):
                    self.settings["bounce_time"] = given_settings["bounce_time"]
                    init_required=True
                if("log_level" in given_settings):
                    self.settings["log_level"] = given_settings["log_level"]
                if(init_required):
                    self.init()
                self.update_state()
                return
    
    def listen_target(self):
        print("Listening for button presses ...", flush=True)
        self.listener_thread_running = True
        while self.listener_thread_running:
            try:
                if(not self.listener_thread_paused):
                    if(self.settings["log_level"] < logging.INFO):
                        if(self.device.is_pressed):
                            print("Button is pressed.", flush=True)
                        else:
                            print("Button is released.", flush=True)
                    self.update_state()
                time.sleep(self.settings["hold_time"])
            except KeyboardInterrupt:
                raise
            except Exception as e:
                print(e, file=sys.stderr, flush=True)
                time.sleep(self.settings["retry_time"])
        print("Listener thread finished.", flush=True)
    
    def listen(self):
        if(self.listener_thread_running):
            print("Listener thread already running.", flush=True)
        else:
            threading.Thread(target=self.listen_target).start()
    
    def init(self):
        if(self.device is not None):
            self.listener_thread_paused = True
            self.device.close()
            print("Closed BUTTON device.", flush=True)
        self.device = gpiozero.Button(self.settings["pin"], bounce_time=self.settings["bounce_time"])
        self.listener_thread_paused = False
        print("Initialized BUTTON device on pin " + str(self.settings["pin"]), flush=True)


    def cleanup(self):
        self.listener_thread_paused = True
        self.listener_thread_running = False
        if(self.device is not None):
            self.device.close()
            print("Closed BUTTON device.", flush=True)
        
        print("Cleaned up.")

try:
    ky_004 = Ky004()
    ky_004.init()
    ky_004.listen()
    ky_004.receive()
except KeyboardInterrupt:
    print('Good Bye!')
finally:
    ky_004.cleanup()
