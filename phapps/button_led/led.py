import gpiozero
import json
import sys
import time
import threading

class Ky008:
    def __init__(self):
        self.version = "0.9.3"
        self.state = {}
        self.settings = {
            "notify_url": "fhtp://broadcast/{DEVICE}/app/{APP}/script/{SCRIPT}",
            "pin": 6,
            "initial_value": False,
            "frequency": 100
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

            if(action == "ON"):
                self.device.on()
                self.mode = "ON"
                print("LED is on.", flush=True)
                self.update_state()
                return

            if(action == "OFF"):
                self.device.off()
                self.mode = "OFF"
                print("LED is off.", flush=True)
                self.update_state()
                return

            if(action == "TOGGLE"):
                self.device.toggle()
                if(self.device.is_lit):
                    self.mode = "ON"
                    print("LED is on.", flush=True)
                else:
                    self.mode = "OFF"
                    print("LED is off.", flush=True)
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
                print("LED is blinking with " + str(on_time) + "s/" + str(off_time) + "s", flush=True)
                self.update_state()
                return
            
            if(action == "PULSE"):
                fade_in_time=1
                fade_out_time=1
                n=None
                if("fade_in_time" in message_body):
                    fade_in_time = message_body["fade_in_time"]
                if("fade_out_time" in message_body):
                    fade_out_time = message_body["fade_out_time"]
                if("n" in message_body):
                    n = message_body["n"]
                    
                self.device.pulse(fade_in_time=fade_in_time, fade_out_time=fade_out_time, n=n)
                self.mode = "PULSE"
                print("LED is pulsing with " + str(fade_in_time) + "s/" + str(fade_out_time) + "s", flush=True)
                self.update_state()
                return
            
            if(action == "SETUP"):
                init_required=True
                given_settings = message_body["settings"]
                
                if("pin" in given_settings):
                    self.settings["pin"] = given_settings["pin"]
                if("frequency" in given_settings):
                    self.settings["frequency"] = given_settings["frequency"]
                if("initial_value" in given_settings):
                    self.settings["initial_value"] = given_settings["initial_value"]
                
                if(init_required):
                    self.init()
                self.update_state()
                return
    
    def init(self):
        if(self.device is not None):
            self.device.close()
            print("Closed LED device.", flush=True)
        
        self.device = gpiozero.PWMLED(self.settings["pin"], initial_value=self.settings["initial_value"], frequency=self.settings["frequency"])
        
        print("Initialized LED device on pin " + str(self.settings["pin"]), flush=True)

    def cleanup(self):
        if(self.device is not None):
            self.device.close()
            print("Closed LED device.", flush=True)
        
        print("Cleaned up.")

try:
    ky_008 = Ky008()
    ky_008.init()
    ky_008.receive()
    
except KeyboardInterrupt:
    print('Good Bye!')
finally:
    ky_008.cleanup()
