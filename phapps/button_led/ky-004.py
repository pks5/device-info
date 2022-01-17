import gpiozero
import json
import sys
import time
import threading

class Ky004:
    def __init__(self):
        self.state = {}
        self.settings = {
            "notify_url": None,
            "pin": 5,
            "hold_time": 1,
            "bounce_time": None
        }
        self.listener_thread_running = False
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
                if("hold_time" in given_settings):
                    self.settings["hold_time"] = given_settings["hold_time"]
                if("bounce_time" in given_settings):
                    self.settings["bounce_time"] = given_settings["bounce_time"]
                self.init()
                self.update_state()
                return
    
    def listen_target(self):
        try:
            print("Listening for button presses ...", flush=True)
            self.listener_thread_running = True
            while True:
                self.update_state()
                time.sleep(self.settings["hold_time"])

        except IOError as error:
            print("IOError: " + str(error), flush=True)
        finally:
            self.listener_thread_running = False
    
    def listen(self):
        if(self.listener_thread_running):
            print("Listener thread already running.", flush=True)
        else:
            threading.Thread(target=self.listen_target).start()
    
    def init(self):
        if(self.device is not None):
            self.device.close()
            print("Closed button device.", flush=True)
        self.device = gpiozero.Button(self.settings["pin"], bounce_time=self.settings["bounce_time"])
        print("Initialized button device on pin " + str(self.settings["pin"]), flush=True)

    def cleanup(self):
        if(self.device is not None):
            self.device.close()
            print("Closed button device.", flush=True)
        
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