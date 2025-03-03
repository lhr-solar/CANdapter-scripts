# TODO: #1 add file output/logging functionality

import sys
import can
import pyCandapter
import signal
import time
import argparse
from decode import device_data_readable
import cantools
import glob

parser = argparse.ArgumentParser()
# cli flags: -p PORT -s SERIALBAUDRATE -c CANBAUDRATE -i DEVICEID -d DEFAULTID
parser.add_argument("-p", "--port", help="COM Port")
parser.add_argument("-s", "--serial", help="Serial Baud Rate", type=int)
parser.add_argument("-c", "--can", help="CAN Baud Rate", type=int)
parser.add_argument("-i", "--device-id", help="Device Base Address")
parser.add_argument("-d", "--default-id", help="Default Base Address")
args = parser.parse_args()

# set vars using flags
port = args.port
serialbaudrate = args.serial
canbaudrate = args.can
device_id = args.device_id
default_id = args.default_id

# if flags unset, set default COM port, baud rate, and CAN bus speed (currently 125k for Daybreak)
port = "COM4" if port is None else port
serialbaudrate = 9600 if serialbaudrate is None else serialbaudrate
canbaudrate = 125000 if canbaudrate is None else canbaudrate

db = cantools.database.Database()

def find_add_dbc_files():
    dbc_list = glob.glob("./files/*.dbc")
    for i in dbc_list:
        db.add_dbc_file(i)

# close CAN bus before terminating
def signal_handler(sig, frame):
    candapter.closeCANBus()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)

# create candapter instance
try:
    candapter = pyCandapter.pyCandapter(port, serialbaudrate)
    candapter.openCANBus(canbaudrate)    
except Exception as e:
    print("Failed to open CAN Bus. Exiting...")
    print(f"Full Error: {e}")
    candapter.closeCANBus()
    exit(1)

find_add_dbc_files() # combine all provided dbc 
#print(db.messages)

print("LHRs CANdapter Scripts")
device_id = input("Enter the device base address (e.g. 0x240): ") if device_id is None else device_id
default_id = input("Enter the default base address (dbc reference): ") if default_id is None else default_id

if device_id != "":
    device_id_int = int(device_id, 16) # convert to int cause python is ew
    default_id_int = int(default_id, 16)
    print(f"\n\n\nCAN frames for device at {device_id}:")
    # loop to read CAN messages
    while True:
        #messages to test if translation is working (remove for prod)
        #message = can.Message(arbitration_id=0x200, data=[0x02, 0xB7, 0xFF, 0x8D, 0x0C, 0x8C, 0xFF, 0xCD], is_extended_id=False)
        #message = can.Message(arbitration_id=0x201, data=[0x02, 0x00, 0x00, 0x17, 0x17], is_extended_id=False)
        #message = can.Message(arbitration_id=0x241, data=[0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x01], is_extended_id=False)
        
        #message = candapter.readCANMessage()
        if message is not None:
            print(device_data_readable(db, device_id_int, default_id_int, message))
        
        time.sleep(0.05) # oversampling so candapter FIFO doesn't fill up (do we even need a delay????)
else:
    print("Invalid input. Exiting...")
    candapter.closeCANBus()
    exit(1)