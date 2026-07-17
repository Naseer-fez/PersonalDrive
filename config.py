import json

import os

class Config:
    def __init__(self):
        self.path = os.getenv("CONFIG_PATH", "config.json")
        self.reload()
    def reload(self):
        try:
            with open(self.path) as file:
                self.data=json.load(file)
        except FileNotFoundError :
            with open(self.path,"w") as file:
                self.data={}
                json.dump(self.data,file,indent=4)
    def get(self, key, default=None):
        env_val = os.getenv(key)
        if env_val is not None:
            if env_val.lower() == 'true': return True
            if env_val.lower() == 'false': return False
            if env_val.isdigit(): return int(env_val)
            return env_val
        return getattr(self, 'data', {}).get(key, default)
    def set(self, key, value):
        self.data[key] = value
        with open(self.path, "w") as file:
            json.dump(self.data, file, indent=4)
        
config = Config()



