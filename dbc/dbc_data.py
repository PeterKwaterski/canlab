"""
This module provides access to the DbcData dataclass
"""

from dataclasses import dataclass


@dataclass
class DbcData:
    """Represents the data found within a DBC Signal along with a value that has physical meaning.

    Attributes:
        value: the value with physical meaning.
        startBit: the bit at which the signal starts in the CAN message.
        numBits: the number of bits the signal occupies.
        scale: the factor by which the integer in the CAN frame must be multiplied by to get one with physical meaning.
        offset: the factor by which the value in the CAN frame is shifted from the true value
        isSigned: a flag represening if the signal is signed or unsigned.
        name: the name of the signal.
        isLSB: if the signal is in LSB format
    """
    value: float
    startBit: int
    numBits: int
    scale: float
    offset: float
    isSigned: bool
    name: str
    isLSB: bool