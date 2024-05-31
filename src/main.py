import asyncio
import logging
from ble_handler import BLEHandler
from mic_handler import MicHandler
from config_handler import ConfigHandler
from codec_type import CodecType
from status_manager import StatusManager
from storage_handler import StorageHandler
import sounddevice as sd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    loop = asyncio.get_event_loop()
    config_handler = ConfigHandler()
    status_manager = StatusManager()
    storage_handler = StorageHandler()
    codec_type = CodecType()

    ble_handler = BLEHandler(loop)

    # Lister les périphériques audio disponibles
    print(sd.query_devices())

    # Spécifiez le périphérique audio ici après avoir vérifié les périphériques disponibles
    mic_handler = MicHandler(ble_handler, device=0)  # Utilisez l'index 0 basé sur la sortie de sd.query_devices()

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
