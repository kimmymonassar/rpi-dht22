import os
import logging
import logging.handlers
import time
import board
import adafruit_dht
import pika
from datetime import datetime

logs_path = f'{os.path.dirname(os.path.realpath(__file__))}/logs/output.log'
current_humidity = None
current_temp_c = None
current_temp_f = None

def queue_publish(temp_f, temp_c, humidity):
    print((temp_f))
    print((temp_c))
    print(str(humidity))
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', heartbeat=36000))
    channel = connection.channel()
    channel.queue_declare(queue='dht22temp', durable=True)
    channel.basic_publish(exchange='dhtexchange', routing_key='current_temp_fahrenheit', body=str(temp_f))
    channel.basic_publish(exchange='dhtexchange', routing_key='current_temp_celsius', body=str(temp_c))
    channel.basic_publish(exchange='dhtexchange', routing_key='current_humidity', body=str(humidity))
    connection.close()

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
            current_temp_c = dhtDevice.temperature
            current_temp_f = current_temp_c * (9 / 5) + 32
            current_humidity = dhtDevice.humidity
            log_data = datetime.now().strftime('%d/%m/%Y %H:%M:%S - ') + 'Temp: {:.1f} F / {:.1f} C    Humidity: {}% '.format(current_temp_f, current_temp_c, current_humidity)
            logging.info(log_data)

        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            print(error.args[0])
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error

        time.sleep(2.0)
    if current_temp_f != None and current_temp_c != None and current_humidity != None:
        queue_publish(current_temp_f, current_temp_c, current_humidity)
    else:
        tempcheck(5)

tempcheck(5)
