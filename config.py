import json

class Config:
    def __init__(self):
        self.path="config.json"
        self.reload()
    def reload(self):
        with open(self.path) as file:
            self.data=json.load(file)
            
    def get(self, key, default=None):
        return self.data.get(key, default)
    def set(self, key, value):
        self.data[key] = value
        with open(self.path, "w") as file:
            json.dump(self.data, file, indent=4)
        
config = Config()



