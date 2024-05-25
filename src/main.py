import asyncio
import logging
from ble_handler import BLEHandler
# from config_handler import ConfigHandler
# from mic_handler import MicHandler
# from codec_type import CodecType
# from status_manager import StatusManager
# from storage_handler import StorageHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    loop = asyncio.get_event_loop()

    # Initialize handlers
    ble_handler = BLEHandler(loop)
    # config_handler = ConfigHandler()
    # mic_handler = MicHandler()
    # status_manager = StatusManager()
    # storage_handler = StorageHandler()

    # Start BLE server
    await ble_handler.start_server()
    logger.debug("BLE server started")

    # Wait for trigger
    await ble_handler.wait_for_trigger()

    # Start audio streaming
    ble_handler.start_stream()
    logger.debug("Audio streaming started")

    await asyncio.sleep(5)  # Adjust as needed

    # Stop BLE server
    await ble_handler.stop_server()
    logger.debug("BLE server stopped")

if __name__ == "__main__":
    asyncio.run(main())
