import pymongo
from senzor import dht_sensor
from datetime import datetime
import logging

senzor = dht_sensor()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class MongoDatabase():
    def __init__(self, url, colection):
        self.url = url
        self.colection = colection

    def insert(self, temperature, humidity):
        try:
            logging.info(f"temp: {temperature}")
            logging.info(f"hum: {humidity}")
            client = pymongo.MongoClient(self.url)

            db = client.mongodb
            colection = db[self.colection]

            current_date = datetime.now().strftime('%Y-%m-%d')

            doc = {
                "temperature": temperature,
                "humidity": humidity,
                "date": current_date,
            }

            logging.info(f"doc: ${doc}")

            colection.insert_one(doc)

            client.close()

        except Exception:
            logging.info("Error " + Exception)

    
    # this method is for insert data from localDB to MongoDb, when the network was down and now is up
    def insert_data(self, list_data: list[str]):

        try:
            client = pymongo.MongoClient(self.url)

            db = client.mongodb
            colection = db[self.colection]

            logging.info("urmeaza date")
            logging.info(list_data)

            formatted_data = [
                {"temperature": item[0], "humidity": item[1], "date": item[2]}
                for item in list_data
            
            ]

            for item in list_data:
                logging.info(item[1])
                logging.info(item[2])

            # Inserarea datelor în colecție
            colection.insert_many(formatted_data)

            # rezultat = colection.insert_one(list_data)

            logging.info("Datele s-au insertat cu succes")

            client.close()

        except Exception:
            logging.info("Error " + str(Exception))

