"""Contains functions for converting the data within DBCs to a usable format

The functions within this module transform the contents of a DBC file into the CANLab data format
or if desired the cantools dbc format
"""

import cantools
from typing import List

from .util import clean_dbc
from .message_data import MessageData
from .dbc_data import DbcData
from exceptions.dbc_exception import DbcException

def load_cantools_dbc(src_path: str, dst_path: str = None) -> cantools.database:
    """Loads a .dbc file into a cantools database object.

    Args:
        src_path: the location of the dbc to load
        dst_path: the location to save the cleaned dbc to

    Returns:
        the database object created by cantools.database.load_file()
    """
    if not src_path.endswith('.dbc'):
        raise DbcException
    
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
    curr_line: str = ''
    try:
        with open(src_path, 'r') as dbc:
            current_message = None
            for line in dbc:
                curr_line = line
                if(curr_line.startswith("BO_")):
                    if current_message is not None:
                        messages.append(current_message)
                    message = curr_line.split()
                    current_message = MessageData(dbc_id=int(message[1]))
                elif ("SG_" in curr_line and current_message != None):
                    signal = curr_line.split()
                    block_data = signal[3]
                    transform_data = signal[4]
                    if signal[3] == ('M'):
                        block_data = signal[4]
                        transform_data = signal[5] 
                        sig_data.is_multiplexor = True
                    elif 'm' in signal[3]:
                        mux_value_str = signal[3][1:]
                        sig_data.multiplexor_value = int(mux_value_str)
                        transform_data = signal[5]
                        block_data = signal[4]

                    start_bit_str = block_data[:block_data.index('|')]
                    num_bits_str = block_data[block_data.index('|') + 1 : block_data.index('@')]
                    is_lsb = True if block_data[block_data.index('@') + 1] == '1' else False
                    is_signed = True if block_data[block_data.index('@') + 2] == '-' else False
                    scale_str = transform_data[1:transform_data.index(',')]
                    offset_str = transform_data[transform_data.index(',') + 1 : transform_data.index(')')]
                    
                    sig_data = DbcData(
                        value=0.0,
                        startBit=int(start_bit_str),
                        numBits=int(num_bits_str),
                        scale=float(scale_str),
                        offset=float(offset_str),
                        isSigned=is_signed,
                        name=signal[1],
                        isLSB=is_lsb
                    )
                    current_message.signals.append(sig_data)
            # Append the last message
            if current_message is not None:
                messages.append(current_message)
        return messages
    except FileNotFoundError as e:
        raise FileNotFoundError(f"The file {src_path} was not found") from e
    except IndexError:
        raise DbcException
    except ValueError:
        print(f"")