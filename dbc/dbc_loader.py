"""Contains functions for converting the data within DBCs to a usable format

The functions within this module transform the contents of a DBC file into the CANLab data format
or if desired the cantools dbc format
"""

import cantools
from typing import List

from dbc import dbc_data

from .util import clean_dbc
from .message_data import MessageData
from .dbc_data import DbcData

def load_cantools_dbc(src_path: str, dst_path: str = None) -> cantools.database:
    """Loads a .dbc file into a cantools database object.

    Args:
        src_path: the location of the dbc to load
        dst_path: the location to save the cleaned dbc to

    Returns:
        the database object created by cantools.database.load_file()
    """
    if not src_path.endswith('.dbc'):
        raise Exception
    
    clean_path = clean_dbc(src_path, dst_path)
    return cantools.database.load_file(clean_path)

def extract_messages(src_path: str) -> List[MessageData]:
    """Extracts the messages contained in a .dbc file into a list of MessageData objects with all signals included.

    Args:
        src_path: The location of the .dbc to load.
    Returns:
        The messages with their signals contained within the DBC.
    """
    messages: List[MessageData] = []
    try:
        with open(src_path, 'r') as dbc:
            current_message = None
            for line in dbc:
                if(line.startswith("BO_")):
                    message = line.split()
                    current_message = MessageData(message[1])
                elif ("SG_" in line and current_message != None):
                    signal = line.split()
                    sig_data = DbcData()
                    sig_data.name = signal[1]
                    block_data = signal[3]
                    sig_data.startBit = block_data[:block_data.index('|')]
                    sig_data.numBits = block_data[block_data.index('|') + 1 : block_data.index('@')]
                    sig_data.isLSB = True if block_data[block_data.index('@') + 1] == '1' else False
                    sig_data.isSigned = True if block_data[block_data.index('@') + 2] == '-' else False
                    transform_data = signal[4]
                    sig_data.scale = transform_data[1:transform_data.index(',')]
                    sig_data.offset = transform_data[transform_data.index(',') + 1 : transform_data.index(')')]
                    current_message.signals.append(sig_data)
                    return messages
    except Exception as e:
        print(e)