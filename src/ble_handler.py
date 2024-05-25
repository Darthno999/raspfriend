import asyncio
import logging
import struct
import sounddevice as sd
from typing import Any
from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BLEHandler:
    def __init__(self, loop):
        self.loop = loop
        self.server = BlessServer(name="Friend", loop=self.loop)
        self.trigger = asyncio.Event()
        self.packet_number = 0
        self.index = 0
        self.sample_rate = 16000
        self.channels = 2  # Stereo input

    def read_request(self, characteristic: BlessGATTCharacteristic, **kwargs) -> bytearray:
        logger.debug(f"Reading {characteristic.uuid}: {characteristic.value}")
        return characteristic.value

    def write_request(self, characteristic: BlessGATTCharacteristic, value: Any, **kwargs):
        characteristic.value = value
        logger.debug(f"Write request for characteristic {characteristic.uuid} with value {characteristic.value}")
        if value == b'\x0F':
            logger.debug("Trigger value 0xF received, setting trigger")
            self.trigger.set()

    async def setup_ble_services(self):
        # Battery Service
        battery_service_uuid = "0000180F-0000-1000-8000-00805F9B34FB"
        await self.server.add_new_service(battery_service_uuid)
        battery_char_uuid = "00002A19-0000-1000-8000-00805F9B34FB"
        await self.server.add_new_characteristic(
            battery_service_uuid, battery_char_uuid,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
            None, GATTAttributePermissions.readable
        )

        # Audio Service
        main_service_uuid = "19B10000-E8F2-537E-4F6C-D104768A1214"
        await self.server.add_new_service(main_service_uuid)
        audio_data_char_uuid = "19B10001-E8F2-537E-4F6C-D104768A1214"
        await self.server.add_new_characteristic(
            main_service_uuid, audio_data_char_uuid,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify,
            None, GATTAttributePermissions.readable
        )

        codec_type_char_uuid = "19B10002-E8F2-537E-4F6C-D104768A1214"
        await self.server.add_new_characteristic(
            main_service_uuid, codec_type_char_uuid,
            GATTCharacteristicProperties.read | GATTCharacteristicProperties.write,
            None, GATTAttributePermissions.readable | GATTAttributePermissions.writeable
        )

    async def start_server(self):
        self.server.read_request_func = self.read_request
        self.server.write_request_func = self.write_request
        await self.setup_ble_services()
        await self.server.start()
        logger.debug("BLE Server started and advertising")

    async def stop_server(self):
        await self.server.stop()
        logger.debug("BLE Server stopped")

    async def wait_for_trigger(self):
        logger.debug("Waiting for trigger...")
        await self.trigger.wait()
        logger.debug("Trigger received")

    def audio_callback(self, indata, frames, time, status):
        if status:
            logger.warning(f"Audio input status: {status}")

        # Convert stereo to mono by averaging the two channels
        mono_audio = (indata[:, 0] + indata[:, 1]) / 2
        audio_data = bytearray()
        for sample in mono_audio:
            audio_data.extend(struct.pack('<B', int(sample * 128 + 128)))  # Convert to 8-bit PCM
            if len(audio_data) >= 160:
                packet = struct.pack('<H', self.packet_number) + struct.pack('<B', self.index) + audio_data[:160]
                self.packet_number += 1
                self.index = (self.index + 1) % 256
                audio_data = audio_data[160:]
                logger.debug(f"Sending packet number {self.packet_number} with index {self.index}")
                asyncio.run_coroutine_threadsafe(
                    self.server.update_value("19B10000-E8F2-537E-4F6C-D104768A1214", "19B10001-E8F2-537E-4F6C-D104768A1214", packet),
                    self.loop
                )

    def start_stream(self):
        with sd.InputStream(samplerate=self.sample_rate, channels=self.channels, callback=self.audio_callback):
            self.loop.run_until_complete(self.wait_for_trigger())
            logger.debug("Audio streaming started")

