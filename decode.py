import can
import cantools

# convert raw CAN frames from MPPT to human readable data
# reference: https://www.tpee.nl/wp-content/uploads/2024/10/OpenSEC-firmware-Manual.pdf
def device_data_readable(db, devID, defaultID, message) -> str:    
    # dynamically update message id to match base+offset as defined in dbc file
    updated_id = message.arbitration_id - (devID - defaultID)
    readable_message = "ID: " + str(hex(message.arbitration_id)) + "    "
    try:
        decoded_message = db.decode_message(updated_id, message.data) # decode message using dbc
        print(decoded_message)
        for i in decoded_message.items():
            readable_message += str(i[0]) +": " + str(i[1]) + "    "
    except Exception as e:
        print(e)
    return readable_message
