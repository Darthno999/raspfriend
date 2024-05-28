import sounddevice as sd
import struct
import asyncio
import logging
import wave

logger = logging.getLogger(__name__)

class MicHandler:
    def __init__(self, ble_handler):
        self.ble_handler = ble_handler
        self.sample_rate = 8000  # Update to match Deepgram's requirement
        self.channels = 1
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
        for sample in indata[:, 0]:
            # Convert to linear16 format (16-bit PCM)
            audio_data.extend(struct.pack('<h', int(sample * 32767)))  # Convert to 16-bit PCM
        
        # Write the raw PCM data to the WAV file
        self.wav_file.writeframes(audio_data)

        # Ensure we send packets with 160 samples each
        while len(audio_data) >= 320:  # 160 samples * 2 bytes per sample
            packet = struct.pack('<H', self.packet_number) + struct.pack('<B', self.index) + audio_data[:320]
            audio_data = audio_data[320:]
            self.packet_number += 1
            self.index = (self.index + 1) % 256
            
            asyncio.run_coroutine_threadsafe(
                self.ble_handler.update_audio_value(bytes(packet)),
                self.ble_handler.loop
            )
            # logger.debug(f"Streaming packet number {self.packet_number} with index {self.index}")

    async def start_streaming(self):
        logger.debug("Audio streaming started")
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self.audio_callback):
            while True:
                await asyncio.sleep(2)
                logger.debug("Streaming audio data...")

    async def stream_audio(self):
        await self.start_streaming()

    def close(self):
        self.wav_file.close()

