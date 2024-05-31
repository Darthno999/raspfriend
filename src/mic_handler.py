import pyaudio
import struct
import asyncio
import logging
import numpy as np

logger = logging.getLogger(__name__)

class MicHandler:
    def __init__(self, ble_handler):
        self.ble_handler = ble_handler
        self.sample_rate = 16000
        self.channels = 1
        self.packet_number = 0
        self.index = 0
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=pyaudio.paInt16,
                                 channels=self.channels,
                                 rate=self.sample_rate,
                                 input=True,
                                 frames_per_buffer=512)

    def audio_callback(self, in_data, frame_count, time_info, status):
        # Convert the data to mono and 16-bit PCM format
        mono_data = np.frombuffer(in_data, dtype=np.int16)
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

        return (in_data, pyaudio.paContinue)

    async def start_streaming(self):
        logger.debug("Audio streaming started")
        self.stream.start_stream()
        while True:
            await asyncio.sleep(2)
            logger.debug("Streaming audio data...")

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
