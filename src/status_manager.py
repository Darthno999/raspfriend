class StatusManager:
    def __init__(self):
        self.status = {}

    def set_status(self, key, value):
        self.status[key] = value

    def get_status(self, key):
        return self.status.get(key, None)

    def get_all_status(self):
        return self.status

