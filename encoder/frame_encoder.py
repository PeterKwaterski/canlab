"""This module contains the functions for encoding the physical values into a CAN frame.
"""

from typing import List

from dbc.dbc_data import DbcData
from conversions import phys_to_raw

def values_to_lsb(signals: List[DbcData], frame_len=8) -> bytearray:
    """Encode a list of LSB signals into a CAN frame

    Args:
        signals: the list of LSB signals to encode
        frame_len: the length of the CAN frame to encode the signals into
    Returns:
        The encoded CAN frame
    """
    frame = bytearray(frame_len)

    for sig in signals:
        raw = phys_to_raw(sig) & ((1 << sig.numBits) - 1)

        for i in range(sig.numBits):
            frame_bit = sig.startBit + i
            byte = frame_bit // 8
            bit  = frame_bit % 8

            if byte >= frame_len:
                continue

            frame[byte] &= ~(1 << bit)
            frame[byte] |= ((raw >> i) & 1) << bit

    return frame

def values_to_msb(signals: List[DbcData], frame_len=8) -> bytearray:
    """Encode a list of MSB signals into a CAN frame

    Args:
        signals: the list of MSB signals to encode
        frame_len: the length of the CAN frame to encode the signals into
    Returns:
        The encoded CAN frame
    """
    frame = bytearray(frame_len)

    for sig in signals:
        raw = phys_to_raw(sig) & ((1 << sig.numBits) - 1)

        byte = sig.startBit // 8
        bit  = sig.startBit % 8

        for i in range(sig.numBits):
            # Extract MSB first
            raw_bit = (raw >> (sig.numBits - 1 - i)) & 1

            if 0 <= byte < frame_len:
                frame[byte] &= ~(1 << bit)
                frame[byte] |= raw_bit << bit

            # Move to next Motorola bit position
            bit -= 1
            if bit < 0:
                bit = 7
                byte += 1

    return frame

def values_to_frame(signals: List[DbcData], frame_len=8) -> bytearray:
    """Encode a combination of LSB and MSB signals into a single CAN frame

    Args:
        signals: the list of signals to encode
        frame_len: the length of the CAN frame to encode the signals into
    Returns:
        The encoded CAN frame
    """
    frame = bytearray(frame_len)
    for sig in signals:
        raw = phys_to_raw(sig) & ((1 << sig.numBits) - 1)

        if sig.isLSB:
            for i in range(sig.numBits):
                frame_bit = sig.startBit + i
                byte = frame_bit // 8
                bit = frame_bit % 8

                if byte >= frame_len:
                    continue

                frame[byte] &= ~(1 << bit)
                frame[byte] |= ((raw >> i) & 1) << bit

        else:
            byte = sig.startBit // 8
            bit = sig.startBit % 8

            for i in range(sig.numBits):
                raw_bit = (raw >> (sig.numBits - 1 - i)) & 1
                if 0 <= byte < frame_len:
                    frame[byte] &= ~(1 << bit)
                    frame[byte] |= raw_bit << bit

                bit -= 1
                if bit < 0:
                    bit = 7
                    byte += 1
    return frame