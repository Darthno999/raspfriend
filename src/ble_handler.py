import asyncio
import logging
import uuid
from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions
from config_handler import ConfigHandler

logger = logging.getLogger(__name__)

class BLEHandler:
    def __init__(self, loop):
        self.loop = loop
        self.config = ConfigHandler().get_config()
        self.server = BlessServer(name=self.config['device_name'], loop=loop)
        self.audio_data_char_uuid = uuid.UUID.hex(self.config['audio_data_char_uuid'])
        self.battery_char_uuid = uuid.UUID.hex(self.config['battery_char_uuid'])
        self.server.advertising_interval = 100  # Advertising interval in ms
        self.server.advertising_timeout = 0  # 0 means indefinite advertising

    async def setup_ble_services(self):
        audio_service_uuid = uuid.UUID.hex(self.config['main_service_uuid']).hex
        battery_service_uuid = uuid.UUID.hex(self.config['battery_service_uuid']).hex

        # Add Audio Service
        audio_service = await self.server.add_new_service(audio_service_uuid)
        audio_data_char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
        audio_data_char_permissions = GATTAttributePermissions.readable
        audio_data_char_value = bytearray()
        audio_data_char = await self.server.add_new_characteristic(
            audio_service, self.audio_data_char_uuid.hex, audio_data_char_flags, audio_data_char_value, audio_data_char_permissions
        )

        # Add Battery Service
        battery_service = await self.server.add_new_service(battery_service_uuid)
        battery_char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
        battery_char_permissions = GATTAttributePermissions.readable
        battery_char_value = bytearray([100])
        battery_char = await self.server.add_new_characteristic(
            battery_service, self.battery_char_uuid.hex, battery_char_flags, battery_char_value, battery_char_permissions
        )

        return audio_service, audio_data_char, battery_service, battery_char

    async def start_server(self):
        audio_service, audio_data_char, battery_service, battery_char = await self.setup_ble_services()
        await self.server.start()
        logger.debug("BLE Server started and advertising")
        logger.debug("Waiting for connections...")

    def read_request(self, characteristic: BlessGATTCharacteristic, **kwargs):
        if characteristic.uuid == self.battery_char_uuid.hex:
            value = bytearray([100])  # Battery level at 100%
            logger.debug(f"Reading {characteristic.uuid}: {value}")
            return value
        logger.debug(f"Reading {characteristic.uuid}: {characteristic.value}")
        return characteristic.value

    def write_request(self, characteristic: BlessGATTCharacteristic, value, **kwargs):
        characteristic.value = value
        logger.debug(f"Write request for {characteristic.uuid} with value {characteristic.value}")

    def notification_state_change(self, characteristic: BlessGATTCharacteristic, enabled: bool):
        logger.debug(f"Notification state for {characteristic.uuid} changed to {'enabled' if enabled else 'disabled'}")
        if characteristic.uuid == self.audio_data_char_uuid.hex and enabled:
            logger.debug("Audio data notifications enabled")
            asyncio.create_task(self.update_audio_value(bytearray("Initial audio data", 'utf-8')))

    async def update_audio_value(self, data):
        await self.server.update_value(self.audio_data_char_uuid.hex, data)
        logger.debug(f"Audio data sent: {data[:10]}...")  # Log first 10 bytes for brevity
        logger.debug(f"Audio data packet sent: {data}")