class ConfigHandler:
    def __init__(self):
        self.config = {
            'device_name': 'Friend',
            'battery_service_uuid': '0000180F-0000-1000-8000-00805F9B34FB',
            'battery_char_uuid': '00002A19-0000-1000-8000-00805F9B34FB',
            'main_service_uuid': '19B10000-E8F2-537E-4F6C-D104768A1214',
            'audio_data_char_uuid': '19B10001-E8F2-537E-4F6C-D104768A1214',
            'codec_type_char_uuid': '19B10002-E8F2-537E-4F6C-D104768A1214'
        }

    def get_config(self):
        return self.config

