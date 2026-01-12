"""A module containing functions for decoding CAN frames into physical values
"""

from dbc.dbc_data import DbcData

def lsb_to_value(frame: bytearray, sig: DbcData) -> float:
    """Decodes a physical value from an LSB/intel formatted CAN frame.

    Args:
        frame: the CAN frame to decode a value from.
        sig: The signal information used to decode the value.
    Returns:
        The value decoded from the frame.
    """
    raw = 0
    for i in range(sig.numBits):
        frame_bit = sig.startBit + i
        byte = frame_bit // 8
        bit  = frame_bit % 8
        raw |= ((frame[byte] >> bit) & 1) << i

    if sig.isSigned:
        sign = 1 << (sig.numBits - 1)
        if raw & sign:
            raw |= ~((1 << sig.numBits) - 1)

    return raw * sig.scale + sig.offset


def msb_to_value(frame: bytearray, sig: DbcData) -> float:
    """Decodes a physical value from an MSB/motorolla formatted CAN frame.

    Args:
        frame: the CAN frame to decode a value from.
        sig: The signal information used to decode the value.
    Returns:
        The value decoded from the frame.
    """
    raw = 0

    byte = sig.startBit // 8
    bit  = sig.startBit % 8

    for _ in range(sig.numBits):
        raw = (raw << 1) | ((frame[byte] >> bit) & 1)

        # Move to next Motorola bit position
        bit -= 1
        if bit < 0:
            bit = 7
            byte += 1

    # Sign extension if needed
    if sig.isSigned:
        sign = 1 << (sig.numBits - 1)
        if raw & sign:
            raw |= ~((1 << sig.numBits) - 1)

    return raw * sig.scale + sig.offset

def frame_to_value(frame: bytearray, sig: DbcData) -> float:
    """Decodes the physical value using the isLSB boolean within the DbcData object

    Args:
        frame: the CAN frame ti extract a value from
        sig: the data contained in the DBC related to the signal
    Returns:
        the physical value encoded in the CAN frame
    """
    res: float = 0.0
    if (sig.isLSB):
        res = lsb_to_value(frame, sig)
    else:
        res = msb_to_value(frame, sig)
    return res
