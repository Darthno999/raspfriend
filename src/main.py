import asyncio
import logging
from ble_handler import BLEHandler
from config_handler import ConfigHandler

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def main():
    loop = asyncio.get_event_loop()
    config_handler = ConfigHandler()

    ble_handler = BLEHandler(loop)

    await ble_handler.start_server()
    logger.debug("BLE server started")

    # Boucle d'attente pour maintenir le serveur actif
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")

if __name__ == "__main__":
    asyncio.run(main())
