import can
import cantools
import json
import logging
import time
import cantools.database
import cantools.database.namedsignalvalue
import config as cfg
import random

_logger = logging.getLogger(__name__)

config = cfg.get_config()
database = config["can"]["database"]
interface = config["can"]["interface"]
channel = config["can"]["channel"]
delay = config["can"]["delay"]

def create_message_entry(
    message: can.Message,
    db: cantools.database.can.Database,
    filter_set: set,
) -> dict:
    try:
        db_message = db.get_message_by_frame_id(message.arbitration_id)
        decoded = db.decode_message(message.arbitration_id, message.data)
        _logger.debug(f"{db_message.name}: {decoded}")

        try:
            return {
                "name": db_message.name,
                "timestamp": message.timestamp,
                "id": message.arbitration_id,
                "data": json.dumps(decoded),
                "raw": "0x" + message.data.hex(),
            }
        except TypeError:
            return {
                "name": db_message.name,
                "timestamp": message.timestamp,
                "id": message.arbitration_id,
                "data": f"{decoded}",
                "raw": "0x" + message.data.hex(),
            }
    except KeyError:
        return {
            "name": "Unknown",
            "timestamp": message.timestamp,
            "id": message.arbitration_id,
            "data": message.data.hex(),
            "raw": "0x" + message.data.hex(),
        }

# For reading real can connection
def read():
    db = cantools.database.load_file(database)
    bus = can.Bus(channel=channel, interface=interface)

    time.sleep(delay)
    message = bus.recv()
    # Decode & return CAN data
    return create_message_entry(message, db, set())

# For simulation from json file
def read_from_json():

    try:
        with open(channel, "r") as file:
            file_content = file.read()

            try:
                messages = json.loads(file_content)  
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return     

        for message in messages:
            time.sleep(random.uniform(0.03, 0.06)) # simulated random delay
            if message.get("name") != "Unknown": # Filter placeholder!!! TODO: real filter file (vin 1-3 + unknowns etc..)
                yield message  # Yield messages to simulate canbus
    
    except FileNotFoundError:
        print(f"Error: {channel} not found.")

def read_object_from_json(index=0):
    try:
        with open(channel, "r") as file:
            file_content = file.read()

            try:
                messages = json.loads(file_content)  
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                return     

        if index < len(messages):
            return messages[index]
        else:
            return None
    
    except FileNotFoundError:
        print(f"Error: {channel} not found.")

    
if __name__ == "__main__":
    for data in read_from_json():  
        print(json.dumps(data, indent=4))  # Prints json...
            