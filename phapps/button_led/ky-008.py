import gpiozero
import json
import sys
import time
import threading

class Ky008:
    def __init__(self):
        self.state = {}
        self.settings = {
            "notify_url": None,
            "pin": 6,
            "initial_value": False
        }
        self.device = None
        self.mode = "DEFAULT"
        
    def send(self, data):
        payload = {
            "headers": {
                "to": self.settings["notify_url"]
            },
            "body": data
        }
        print("<<" + json.dumps(payload), flush=True)

    def update_state(self):
        self.state["is_lit"] = self.device.is_lit
        self.state["mode"] = self.mode

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

            if(action == "ON"):
                self.device.on()
                self.mode = "DEFAULT"
                self.update_state()
                return

            if(action == "OFF"):
                self.device.off()
                self.mode = "DEFAULT"
                self.update_state()
                return

            if(action == "TOGGLE"):
                self.device.toggle()
                self.mode = "DEFAULT"
                self.update_state()
                return

            if(action == "BLINK"):
                on_time=1
                off_time=1
                n=None
                if("on_time" in message_body):
                    on_time = message_body["on_time"]
                if("off_time" in message_body):
                    off_time = message_body["off_time"]
                if("n" in message_body):
                    n = message_body["n"]
                    
                self.device.blink(on_time=on_time, off_time=off_time, n=n)
                self.mode = "BLINK"
                self.update_state()
                return
            
            if(action == "SETUP"):
                given_settings = message_body["settings"]
                
                if("pin" in given_settings):
                    self.settings["pin"] = given_settings["pin"]
                if("initial_value" in given_settings):
                    self.settings["initial_value"] = given_settings["initial_value"]
                
                self.init()
                self.update_state()
                return
    
    def init(self):
        if(self.device is not None):
            self.device.close()
            print("Closed led device.", flush=True)
        
        self.device = gpiozero.LED(self.settings["pin"], initial_value=self.settings["initial_value"])
        
        print("Initialized led device on pin " + str(self.settings["pin"]), flush=True)

    def cleanup(self):
        if(self.device is not None):
            self.device.close()
            print("Closed button device.", flush=True)
        
        print("Cleaned up.")

try:
    ky_008 = Ky008()
    ky_008.init()
    ky_008.receive()
    
except KeyboardInterrupt:
    print('Good Bye!')
finally:
    ky_008.cleanup()
