import asyncio
import logging
import uuid
from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions
from config_handler import ConfigHandler
from status_manager import StatusManager
from storage_handler import StorageHandler
from codec_type import CodecType

logger = logging.getLogger(__name__)


class BLEHandler:
    def __init__(self, loop):
        self.loop = loop
        self.config = ConfigHandler().get_config()
        self.status_manager = StatusManager()
        self.storage_handler = StorageHandler()
        self.server = BlessServer(name=self.config['device_name'], loop=loop)

        # Convert UUIDs from config to bytes objects using `UUID` constructor
        self.battery_service_uuid = uuid.UUID(self.config['battery_service_uuid'])
        self.audio_service_uuid = uuid.UUID(self.config['main_service_uuid'])
        self.codec_type_char_uuid = uuid.UUID(self.config['codec_type_char_uuid'])
        self.audio_data_char_uuid = uuid.UUID(self.config['audio_data_char_uuid'])  # No conversion needed here

        self.server.advertising_interval = 100  # Intervalle de publicité en ms
        self.server.advertising_timeout = 0  # 0 signifie publicité indéfinie

    async def setup_ble_services(self):
        # Add Battery Service
        await self.server.add_new_service(self.battery_service_uuid)
        battery_char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
        battery_char_permissions = GATTAttributePermissions.readable
        battery_char_value = bytearray([100])
        await self.server.add_new_characteristic(
            self.battery_service_uuid, uuid.UUID(self.config['battery_char_uuid']).bytes, battery_char_flags, battery_char_value, battery_char_permissions
        )

        # Add Audio Service
        await self.server.add_new_service(self.audio_service_uuid)
        audio_data_char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
        audio_data_char_permissions = GATTAttributePermissions.readable
        audio_data_char_value = bytearray()
        await self.server.add_new_characteristic(
            self.audio_service_uuid, self.audio_data_char_uuid, audio_data_char_flags, audio_data_char_value, audio_data_char_permissions
        )

        # Add Codec Type Characteristic
        codec_type_char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.write
        codec_type_char_permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
        codec_type_char_value = bytearray([CodecType.PCM_8BIT_16KHZ_MONO])
        await self.server.add_new_characteristic(
            self.audio_service_uuid, self.codec_type_char_uuid, codec_type_char_flags, codec_type_char_value, codec_type_char_permissions
        )

        # Set up request handlers
        self.server.read_request_func = self.read_request
        self.server.write_request_func = self.write_request
        self.server.notification_state_change_func = self.notification_state_change

    async def start_server(self):
        await self.setup_ble_services()
        await self.server.start()
        logger.debug("BLE Server started and advertising")
        logger.debug("Waiting for connections...")

    def read_request(self, characteristic: BlessGATTCharacteristic, **kwargs):
        if characteristic.uuid == uuid.UUID(self.config['battery_char_uuid']).bytes:
            value = bytearray([100])  # Niveau de batterie à 100%
            logger.debug(f"Reading {characteristic.uuid}: {value}")
            return value
        logger.debug(f"Reading {characteristic.uuid}: {characteristic.value}")
        return characteristic.value
    def write_request(self, characteristic: BlessGATTCharacteristic, value, **kwargs):
        characteristic.value = value
        logger.debug(f"Write request for {characteristic.uuid} with value {characteristic.value}")

    def notification_state_change(self, characteristic: BlessGATTCharacteristic, enabled: bool):
        logger.debug(f"Notification state for {characteristic.uuid} changed to {'enabled' if enabled else 'disabled'}")
        if characteristic.uuid == self.audio_data_char_uuid and enabled:
            logger.debug("Audio data notifications enabled")
            asyncio.create_task(self.update_audio_value(bytearray("Initial audio data", 'utf-8')))

    async def update_audio_value(self, data):
        # No conversion needed here, audio_data_char_uuid is already a UUID object
        await self.server.update_value(self.audio_data_char_uuid, data)
        logger.debug(f"Audio data sent: {data[:10]}...")  # Log first 10 bytes for brevity
        logger.debug(f"Audio data packet sent: {data}")
