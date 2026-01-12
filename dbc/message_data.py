"""
The module containing the MessageData class.
"""
from typing import Dict, List

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
        self.multiplexor_signal: DbcData | None = None
        self.multiplexed_signals: Dict[int, List[DbcData]] = {}
        if not bus_id:
            self.bus_id = gen_bus_id(dbc_id)
        elif not dbc_id:
            self.dbc_id = gen_dbc_id(bus_id)
        self.active_signals: List[DbcData] = []

    def get_active_signals(self, frame: bytearray) -> List[DbcData]:
        """Gets the currently active signals from a CAN frame

        Args:
            frame: the CAN frame to extract the active signals from
        Returns:
            The list of active signals within the CAN frame
        """
        active_signals = []
        for sig in self.signals:
            if not sig.is_multiplexor and sig.multiplexor_value is None:
                active_signals.append(sig)
            elif self.multiplexor_signal:
                from decoder.frame_decoder import frame_to_value
                mux_value = int(frame_to_value(frame, self.multiplexor_signal))

                if mux_value in self.multiplexed_signals:
                    active_signals.extend(self.multiplexed_signals[mux_value])
        self.active_signals = active_signals
        return active_signals

    def decode(self, frame: bytearray) -> Dict[str, float]:
        """Decodes all active signals from a given CAN frame

        Args:
            frame: the CAN frame to decode

        Returns:
            A dictionary of the decoded signals and their values
        """
        active_signals = self.get_active_signals(frame)
        from decoder.frame_decoder import frame_to_value
        decoded_signals: Dict[str, float] = {}
        for sig in active_signals:
            decoded_signals[sig.name] = frame_to_value(frame, sig)
        return decoded_signals

    def encode(self, frame_len: int = 8) -> bytearray:
        """Encode all of the active signals into a CAN frame

        Args:
            frame_len: the length of the CAN frame to encode the signals into
        Returns:
            The encoded CAN frame
        """
        from encoder.frame_encoder import values_to_frame
        return values_to_frame(self.active_signals, frame_len)
