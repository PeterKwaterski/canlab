"""Unit tests for encoder and decoder modules."""
import pytest

from dbc.dbc_data import DbcData
from encoder.frame_encoder import values_to_lsb, values_to_msb
from decoder.frame_decoder import lsb_to_value, msb_to_value


def hex_dump(frame: bytearray) -> str:
    """Helper function to format bytearray as hex string."""
    return ' '.join(f'{b:02X}' for b in frame)


class TestLSBEncoderDecoder:
    """Tests for LSB (Intel) encoding and decoding."""

    @pytest.mark.unit
    def test_lsb_roundtrip(self):
        """Test LSB encoding and decoding roundtrip."""
        sig = DbcData(
            value=98.6,
            startBit=0,
            numBits=16,
            scale=0.1,
            offset=0.0,
            isSigned=False,
            name="test_signal",
            isLSB=True
        )

        frame = values_to_lsb([sig])
        decoded = lsb_to_value(frame, sig)

        assert abs(decoded - sig.value) < 0.01

    @pytest.mark.unit
    def test_lsb_zero_value(self):
        """Test LSB encoding/decoding with zero value."""
        sig = DbcData(
            value=0.0,
            startBit=0,
            numBits=8,
            scale=1.0,
            offset=0.0,
            isSigned=False,
            name="zero_signal",
            isLSB=True
        )

        frame = values_to_lsb([sig])
        decoded = lsb_to_value(frame, sig)

        assert decoded == 0.0

    @pytest.mark.unit
    def test_lsb_max_value(self):
        """Test LSB encoding/decoding with maximum value."""
        sig = DbcData(
            value=6553.5,
            startBit=0,
            numBits=16,
            scale=0.1,
            offset=0.0,
            isSigned=False,
            name="max_signal",
            isLSB=True
        )

        frame = values_to_lsb([sig])
        decoded = lsb_to_value(frame, sig)

        assert abs(decoded - sig.value) < 0.1

    @pytest.mark.unit
    def test_lsb_signed_negative(self):
        """Test LSB encoding/decoding with negative signed value."""
        sig = DbcData(
            value=-100.0,
            startBit=0,
            numBits=16,
            scale=0.1,
            offset=0.0,
            isSigned=True,
            name="negative_signal",
            isLSB=True
        )

        frame = values_to_lsb([sig])
        decoded = lsb_to_value(frame, sig)

        assert abs(decoded - sig.value) < 0.1


class TestMSBEncoderDecoder:
    """Tests for MSB (Motorola) encoding and decoding."""

    @pytest.mark.unit
    def test_msb_roundtrip(self):
        """Test MSB encoding and decoding roundtrip."""
        sig = DbcData(
            value=22.0,
            startBit=11,
            numBits=12,
            scale=0.1,
            offset=-40.0,
            isSigned=False,
            name="test_signal",
            isLSB=False
        )

        frame = values_to_msb([sig])
        decoded = msb_to_value(frame, sig)

        assert abs(decoded - sig.value) < 0.01

    @pytest.mark.unit
    def test_signed_current(self):
        """Test MSB encoding/decoding with signed negative value."""
        sig = DbcData(
            value=-120.0,
            startBit=31,
            numBits=16,
            scale=0.1,
            offset=0.0,
            isSigned=True,
            name="signed_current",
            isLSB=False
        )

        frame = values_to_msb([sig])
        decoded = msb_to_value(frame, sig)

        assert abs(decoded - sig.value) < 0.01

    @pytest.mark.unit
    def test_msb_boundary_values(self):
        """Test MSB encoding/decoding with boundary values."""
        # Test minimum value
        sig_min = DbcData(
            value=-40.0,
            startBit=0,
            numBits=12,
            scale=0.1,
            offset=-40.0,
            isSigned=False,
            name="min_signal",
            isLSB=False
        )

        frame_min = values_to_msb([sig_min])
        decoded_min = msb_to_value(frame_min, sig_min)
        assert abs(decoded_min - sig_min.value) < 0.1

        # Test maximum value
        sig_max = DbcData(
            value=409.5,
            startBit=0,
            numBits=12,
            scale=0.1,
            offset=-40.0,
            isSigned=False,
            name="max_signal",
            isLSB=False
        )

        frame_max = values_to_msb([sig_max])
        decoded_max = msb_to_value(frame_max, sig_max)
        assert abs(decoded_max - sig_max.value) < 0.1


class TestRealWorldScenarios:
    """Tests based on real-world CAN log scenarios."""

    @pytest.mark.unit
    def test_solidstatemarine_msb_decoding(self):
        """Test MSB decoding from SolidStateMarine CAN logs."""
        # Define DBC Data for the input signals from SolidStateMarine
        ss_Voltage_Sig = DbcData(
            value=0.0, startBit=7, numBits=16, scale=0.1, offset=0.0,
            isSigned=False, name="voltage", isLSB=False
        )
        ss_net_Current_Sig = DbcData(
            value=0.0, startBit=23, numBits=16, scale=0.1, offset=-3000.0,
            isSigned=False, name="net_current", isLSB=False
        )
        ss_Soc_Sig = DbcData(
            value=0.0, startBit=39, numBits=16, scale=0.1, offset=0.0,
            isSigned=False, name="soc", isLSB=False
        )
        ss_temp_Sig = DbcData(
            value=0.0, startBit=7, numBits=8, scale=1.0, offset=-40.0,
            isSigned=False, name="temp", isLSB=False
        )

        # Create frames from CAN logs
        total_info_0_data = [0x01, 0xF2, 0x76, 0x94, 0x00, 0x90, 0xF1, 0xFF]
        total_info_bytearray = bytearray(total_info_0_data)
        cell_temp_data = [0x67, 0x01, 0x62, 0x02, 0x05, 0x00, 0x00, 0x00]
        cell_temp_bytearray = bytearray(cell_temp_data)

        # True values
        voltage = 49.8
        net_current = 35.6
        soc = 14.4
        temp = 63.0

        # MSB Decoding
        calculated_voltage = msb_to_value(total_info_bytearray, ss_Voltage_Sig)
        calculated_net_current = msb_to_value(total_info_bytearray, ss_net_Current_Sig)
        calculated_soc = msb_to_value(total_info_bytearray, ss_Soc_Sig)
        calculated_temp = msb_to_value(cell_temp_bytearray, ss_temp_Sig)

        assert abs(calculated_voltage - voltage) < 0.1
        assert abs(calculated_net_current - net_current) < 0.1
        assert abs(calculated_soc - soc) < 0.1
        assert abs(calculated_temp - temp) < 0.1

        # MSB Encoding
        ss_Voltage_Sig.value = calculated_voltage
        ss_net_Current_Sig.value = calculated_net_current
        ss_Soc_Sig.value = calculated_soc
        ss_temp_Sig.value = calculated_temp

        frame = values_to_msb([ss_Voltage_Sig, ss_net_Current_Sig, ss_Soc_Sig])
        expected_frame = bytearray([0x01, 0xF2, 0x76, 0x94, 0x00, 0x90, 0xF1, 0xFF])
        assert frame == expected_frame

        frame_temp = values_to_msb([ss_temp_Sig])
        expected_temp_frame = bytearray([0x67, 0x01, 0x62, 0x02, 0x05, 0x00, 0x00, 0x00])
        assert frame_temp == expected_temp_frame

    @pytest.mark.unit
    def test_abs_lsb_decoding(self):
        """Test LSB decoding from ABS CAN logs."""
        # Define DBC Data for the output signals of ABS
        abs_voltage_sig = DbcData(
            value=0.0, startBit=0, numBits=16, scale=0.01, offset=0.0,
            isSigned=False, name="voltage", isLSB=True
        )
        abs_netCurrent_sig = DbcData(
            value=0.0, startBit=16, numBits=16, scale=0.04, offset=0.0,
            isSigned=True, name="net_current", isLSB=True
        )
        abs_totalVoltage_sig = DbcData(
            value=0.0, startBit=32, numBits=16, scale=0.01, offset=0.0,
            isSigned=False, name="total_voltage", isLSB=True
        )
        abs_soc_sig = DbcData(
            value=0.0, startBit=0, numBits=16, scale=0.1, offset=0.0,
            isSigned=False, name="soc", isLSB=True
        )
        abs_temp_sig = DbcData(
            value=0.0, startBit=0, numBits=12, scale=0.1, offset=0.0,
            isSigned=True, name="temp", isLSB=True
        )

        # LSB Test Setup
        hv_status_data = [0x4C, 0x15, 0xC5, 0x07, 0x2B, 0x15, 0x21, 0x06]
        hv_status_bytearray = bytearray(hv_status_data)
        pack_temp_data = [0x53, 0x21, 0x43, 0x11, 0x92, 0x27, 0x8B, 0x17]
        pack_temp_bytearray = bytearray(pack_temp_data)
        pack_soc_data = [0x57, 0x02, 0x23, 0x02]
        pack_soc_bytearray = bytearray(pack_soc_data)

        # True values
        voltage = 54.0
        net_current = 79.0
        soc = 59.0
        temp = 33.0

        # LSB Decoding
        calculated_voltage = lsb_to_value(hv_status_bytearray, abs_voltage_sig)
        calculated_voltage2 = lsb_to_value(hv_status_bytearray, abs_totalVoltage_sig)
        calculated_net_current = lsb_to_value(hv_status_bytearray, abs_netCurrent_sig)
        calculated_soc = lsb_to_value(pack_soc_bytearray, abs_soc_sig)
        calculated_temp = lsb_to_value(pack_temp_bytearray, abs_temp_sig)

        # Set to < 1.0 to account for display rounding
        assert abs(calculated_voltage - voltage) < 1.0
        assert abs(calculated_voltage2 - voltage) < 1.0
        assert abs(calculated_net_current - net_current) < 1.0
        assert abs(calculated_soc - soc) < 1.0
        assert abs(calculated_temp - temp) < 1.0

        # LSB Encoding
        abs_voltage_sig.value = calculated_voltage
        abs_totalVoltage_sig.value = calculated_voltage
        abs_netCurrent_sig.value = calculated_net_current
        abs_soc_sig.value = calculated_soc
        abs_temp_sig.value = calculated_temp

        frame = values_to_lsb([abs_voltage_sig, abs_netCurrent_sig, abs_totalVoltage_sig])
        expected_frame = bytearray([0x4C, 0x15, 0xC5, 0x07, 0x2B, 0x15, 0x21, 0x06])
        assert frame == expected_frame

        frame_soc = values_to_lsb([abs_soc_sig])
        expected_soc_frame = bytearray([0x57, 0x02, 0x23, 0x02])
        assert frame_soc == expected_soc_frame

        frame_temp = values_to_lsb([abs_temp_sig])
        expected_temp_frame = bytearray([0x53, 0x21, 0x43, 0x11, 0x92, 0x27, 0x8B, 0x17])
        assert frame_temp == expected_temp_frame
