import sounddevice as sd
import struct
import asyncio
import logging
import numpy as np

logger = logging.getLogger(__name__)

class MicHandler:
    def __init__(self, ble_handler):
        self.ble_handler = ble_handler
        self.sample_rate = 16000  # Fréquence d'échantillonnage correcte
        self.channels = 1  # Utilisez 1 canal pour l'enregistrement mono
        self.packet_number = 0
        self.index = 0

    def audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio input status: {status}")
        
        # Convertir en mono en prenant le premier canal
        mono_data = indata[:, 0].astype(np.int16)
        
        # Convertir les données en format 16-bit PCM
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

    async def start_streaming(self):
        logger.debug("Audio streaming started")
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self.audio_callback, blocksize=512, latency='low'):
            while True:
                await asyncio.sleep(2)
                logger.debug("Streaming audio data...")

    def close(self):
        pass
        
