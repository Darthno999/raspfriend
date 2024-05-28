import asyncio
import logging
from bless import BlessServer, BlessGATTCharacteristic, GATTCharacteristicProperties, GATTAttributePermissions
from config_handler import ConfigHandler
from status_manager import StatusManager
from storage_handler import StorageHandler
from codec_type import CodecType  # Remplacez 'codec_module' par le nom correct du module

logger = logging.getLogger(__name__)

class BLEHandler:
    def __init__(self, loop):
        self.loop = loop
        self.config = ConfigHandler().get_config()
        self.status_manager = StatusManager()
        self.storage_handler = StorageHandler()
        self.server = BlessServer(name=self.config['device_name'], loop=loop)
        self.audio_data_char_uuid = self.config['audio_data_char_uuid']
        self.server.advertising_interval = 100  # Intervalle de publicité en ms
        self.server.advertising_timeout = 0  # 0 signifie publicité indéfinie

    async def setup_ble_services(self):
        battery_service_uuid = self.config['battery_service_uuid']
        audio_service_uuid = self.config['main_service_uuid']
        codec_type_char_uuid = self.config['codec_type_char_uuid']

        # Add Battery Service
        await self.server.add_new_service(battery_service_uuid)

        # Add Battery Level Characteristic
        battery_char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
        battery_char_permissions = GATTAttributePermissions.readable
        battery_char = BlessGATTCharacteristic(
            uuid=self.config['battery_char_uuid'],
            properties=battery_char_flags,
            permissions=battery_char_permissions,
            value=bytearray([100])  # Initial value
        )
        await self.server.add_new_characteristic(battery_service_uuid, battery_char)

        # Add Audio Service
        await self.server.add_new_service(audio_service_uuid)

        # Add Audio Data Characteristic
        audio_data_char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.notify
        audio_data_char_permissions = GATTAttributePermissions.readable
        audio_data_char = BlessGATTCharacteristic(
            uuid=self.audio_data_char_uuid,
            properties=audio_data_char_flags,
            permissions=audio_data_char_permissions,
            value=bytearray()  # Initial value
        )
        await self.server.add_new_characteristic(audio_service_uuid, audio_data_char)

        # Add Codec Type Characteristic
        codec_type_char_flags = GATTCharacteristicProperties.read | GATTCharacteristicProperties.write
        codec_type_char_permissions = GATTAttributePermissions.readable | GATTAttributePermissions.writeable
        codec_type_char = BlessGATTCharacteristic(
            uuid=codec_type_char_uuid,
            properties=codec_type_char_flags,
            permissions=codec_type_char_permissions,
            value=bytearray([CodecType.PCM_8BIT_16KHZ_MONO])  # Initial value
        )
        await self.server.add_new_characteristic(audio_service_uuid, codec_type_char)

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
        if characteristic.uuid == self.config['battery_char_uuid']:
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
            # Add code to start sending audio data notifications here

    async def update_audio_value(self, data):
        await self.server.update_value(self.audio_data_char_uuid, data)
        logger.debug(f"Audio data sent: {data[:10]}...")  # Log first 10 bytes for brevity