# status_manager.py

class StatusManager:
    def __init__(self):
        self.status = {}

    def get_status(self, key):
        return self.status.get(key, None)

    def set_status(self, key, value):
        self.status[key] = value


