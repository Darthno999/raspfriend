# storage_handler.py

class StorageHandler:
    def __init__(self, storage_file="storage.json"):
        self.storage_file = storage_file

    def read_storage(self):
        try:
            with open(self.storage_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

    def write_storage(self, data):
        with open(self.storage_file, 'w') as file:
            json.dump(data, file, indent=4)


