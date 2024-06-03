import os
import logging
import logging.handlers
import time
import board
import adafruit_dht
from datetime import datetime

logs_path = f'{os.path.dirname(os.path.realpath(__file__))}/logs/output.log'

def rolling_log_setup():
    log_handler = logging.handlers.TimedRotatingFileHandler(logs_path, when='midnight', backupCount=31)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

def tempcheck(x):
    # Device, change if using DHT11
    dhtDevice = adafruit_dht.DHT22(board.D4)
    rolling_log_setup()

    for i in range(x):
        try:
            temperature_c = dhtDevice.temperature
            temperature_f = temperature_c * (9 / 5) + 32
            humidity = dhtDevice.humidity
            log_data = datetime.now().strftime('%d/%m/%Y %H:%M:%S - ') + 'Temp: {:.1f} F / {:.1f} C    Humidity: {}% '.format(temperature_f, temperature_c, humidity)
            logging.info(log_data)

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            # print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(2.0)

        if i == 5:
            return

tempcheck(5)

