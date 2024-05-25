# mic_handler.py
import sounddevice as sd
import numpy as np
import struct
import logging

logger = logging.getLogger(__name__)

class MicHandler:
    def __init__(self, sample_rate=16000, channels=2):
        self.sample_rate = sample_rate
        self.channels = channels

    def audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio input status: {status}")

        # Convert stereo to mono by averaging the two channels
        mono_audio = (indata[:, 0] + indata[:, 1]) / 2
        audio_data = bytearray()
        for sample in mono_audio:
            audio_data.extend(struct.pack('<B', int(sample * 128 + 128)))  # Convert to 8-bit PCM
        return audio_data

    def start_stream(self, callback):
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=callback):
            sd.sleep(int(10 * 1000))  # Stream for 10 seconds


