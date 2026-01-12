"""
The module containing the MessageData class.
"""
from typing import List

from conversions import gen_bus_id, gen_dbc_id

from .dbc_data import DbcData
from exceptions.id_exception import IDException

class MessageData:
    """A representation of a Message block within a DBC file.
    """
    def __init__(self, dbc_id: int = None, bus_id: int = None) -> None:
        if not bus_id and not dbc_id:
            raise IDException
        self.signals: List[DbcData] = []
        self.dbc_id = dbc_id
        self.bus_id = bus_id
        if not bus_id:
            self.bus_id = gen_bus_id(dbc_id)
        elif not dbc_id:
            self.dbc_id = gen_dbc_id(bus_id)