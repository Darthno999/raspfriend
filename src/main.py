import asyncio
import logging
from ble_handler import BLEHandler
<<<<<<< HEAD
from mic_handler import MicHandler
=======
# from config_handler import ConfigHandler
# from mic_handler import MicHandler
# from codec_type import CodecType
# from status_manager import StatusManager
# from storage_handler import StorageHandler
>>>>>>> 6990b83d186b20889e39a19351693f372cf933e2

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    loop = asyncio.get_event_loop()
    ble_handler = BLEHandler(loop)
<<<<<<< HEAD
    mic_handler = MicHandler(ble_handler)
=======
    # config_handler = ConfigHandler()
    # mic_handler = MicHandler()
    # status_manager = StatusManager()
    # storage_handler = StorageHandler()
>>>>>>> 6990b83d186b20889e39a19351693f372cf933e2

    await ble_handler.start_server()
    logger.debug("BLE server started")

    logger.debug("Starting audio stream in 20 seconds...")
    await asyncio.sleep(20)
    logger.debug("Audio streaming will start now")

    try:
        await mic_handler.start_streaming()
    except Exception as e:
        logger.error(f"Error during streaming: {e}")
    finally:
        mic_handler.close()
        logger.debug("Audio streaming stopped")

if __name__ == "__main__":
    asyncio.run(main())
