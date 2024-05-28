import sounddevice as sd
import struct
import asyncio
import logging
import wave

logger = logging.getLogger(__name__)

class MicHandler:
    def __init__(self, ble_handler):
        self.ble_handler = ble_handler
        self.sample_rate = 16000  # Fréquence d'échantillonnage correcte
        self.channels = 2  # Utilisez 2 canaux
        self.packet_number = 0
        self.index = 0
        self.wav_file = wave.open('test.wav', 'wb')
        self.wav_file.setnchannels(self.channels)
        self.wav_file.setsampwidth(2)  # 16-bit samples
        self.wav_file.setframerate(self.sample_rate)

    def audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio input status: {status}")
        
        audio_data = bytearray()
        for sample in indata[:, 0]:  # Utilisez le premier canal
            audio_data.extend(struct.pack('<h', int(sample * 32767)))  # Convert to 16-bit PCM
        
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
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self.audio_callback, blocksize=320):
            while True:
                await asyncio.sleep(2)
                logger.debug("Streaming audio data...")

    def close(self):
        self.wav_file.close()

