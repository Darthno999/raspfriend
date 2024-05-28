import wave
import struct
import numpy as np
import asyncio
import logging
from ble_handler import BLEHandler
from config_handler import ConfigHandler
from status_manager import StatusManager
from storage_handler import StorageHandler
from codec_type import CodecType

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AudioConverter:
    def __init__(self, ble_handler, file_path):
        self.ble_handler = ble_handler
        self.file_path = file_path
        self.packet_number = 0
        self.index = 0

    def convert_and_send(self):
        with wave.open(self.file_path, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            channels = wav_file.getnchannels()
            frames = wav_file.readframes(wav_file.getnframes())
            data = np.frombuffer(frames, dtype=np.int16).reshape(-1, channels)
            mono_data = np.mean(data, axis=1).astype(np.int16)
            audio_data = struct.pack('<' + 'h' * len(mono_data), *mono_data)

            while len(audio_data) >= 320:
                packet = struct.pack('<H', self.packet_number) + struct.pack('<B', self.index) + audio_data[:320]
                audio_data = audio_data[320:]
                self.packet_number += 1
                self.index = (self.index + 1) % 256

                asyncio.run_coroutine_threadsafe(
                    self.ble_handler.update_audio_value(bytes(packet)),
                    self.ble_handler.loop
                )

async def main():
    loop = asyncio.get_event_loop()
    config_handler = ConfigHandler()
    status_manager = StatusManager()
    storage_handler = StorageHandler()
    codec_type = CodecType()

    ble_handler = BLEHandler(loop)
    await ble_handler.start_server()
    logger.debug("BLE server started")

    audio_converter = AudioConverter(ble_handler, 'test.wav')
    audio_converter.convert_and_send()

    # Boucle d'attente pour maintenir le serveur actif
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

if __name__ == "__main__":
    asyncio.run(main())

