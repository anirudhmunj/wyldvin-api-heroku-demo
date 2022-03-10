import requests

import configparser
import certifi
import logging
import sys

# pymongo
from pymongo import MongoClient

from pprint import pprint


def get_credentials(config_filename: str) -> str:
    """returns config data"""
    # Create configparse object
    config = configparser.ConfigParser()
    # Read config file
    # Exit in case of exception
    try:
        config.read(config_filename)
    except Exception as e:
        logging.fatal('CONFIG FILE: {}'.format(str(e)))
    # Read credentials
    else:
        try:
            connection_string = config.get('MONGO_DB_CREDS', 'CONNECTION_STRING')

        # Exits in case of exceptions
        except Exception as e:
            logging.fatal('CREDENTIALS IN CONFIG FILE: {}'.format(str(e)))
            sys.exit(1)
        else:
            return connection_string



def get_database(connection_string: str, database: str):
    """returns client"""
    try:
        client = MongoClient(connection_string, tlsCAFile=certifi.where())
    except Exception as e:
        logging.fatal('MONGO CLIENT: {}'.format(str(e)))
    else:
        return client[database]



def main(database_name: str, to_process_collection_name: str, write_to_collection: str):
    """main caller"""

    # read credentials
    connection_string = get_credentials('mongo_db_creds_prod.cfg')
    # get client
    database = get_database(connection_string, database_name)
    # get collection input
    collection_in = database[to_process_collection_name]
    collection_out = database[write_to_collection]


    # loop through all the records
    for seq, record in enumerate(collection_in.find()):
        
        record_processed_flag = False

        if 'winemaker_notes' in record:
            if isinstance(record['winemaker_notes'], str):
                if len(record['winemaker_notes'].strip()) > 5:
                    response = requests.post("http://127.0.0.1:8000/extract", json={"source": "winemaker notes", "document": record['winemaker_notes'] })

                    if response.status_code == 200:
                        result = response.json()
                        result['source'] = 'winemaker notes'

                        record_processed_flag = True


        if record_processed_flag == True:
            record.pop('_id')
            record['is_processed'] = record_processed_flag
            record['extracted_data'] = result
            
            collection_out.insert_one(record)
        else:
            record.pop('_id')
            record['is_processed'] = record_processed_flag          


        print('processed record...{}'.format(seq))


if __name__ == "__main__":
    main('winedb', 'california', 'california_extracted_data')