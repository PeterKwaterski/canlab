from dbc.dbc_data import DbcData
from encoder.frame_encoder import *
from decoder.frame_decoder import *


# ---------- UNIT TESTS ----------

def test_lsb_roundtrip():
    sig = DbcData(
        value=98.6,
        startBit=0,
        numBits=16,
        scale=0.1,
        offset=0.0,
        isSigned=False
    )

    frame = values_to_lsb([sig])
    decoded = lsb_to_value(frame, sig)

    print("LSB frame:", dump(frame))
    assert abs(decoded - sig.value) < 0.01


def test_msb_roundtrip():
    sig = DbcData(
        value=22.0,
        startBit=11,     # MSB of 12-bit signal
        numBits=12,
        scale=0.1,
        offset=-40.0,
        isSigned=False
    )

    frame = values_to_msb([sig])
    decoded = msb_to_value(frame, sig)

    print("MSB frame:", dump(frame))
    assert abs(decoded - sig.value) < 0.01


def test_signed_current():
    sig = DbcData(
        value=-120.0,
        startBit=31,
        numBits=16,
        scale=0.1,
        offset=0.0,
        isSigned=True
    )

    frame = values_to_msb([sig])
    decoded = msb_to_value(frame, sig)

    print("Signed current frame:", dump(frame))
    assert abs(decoded - sig.value) < 0.01

def run_test_suite():
    # Define DBC Data for the input signals from SolidStateMarine
    ss_Voltage_Sig = DbcData(value=0.0, startBit=7, numBits=16, scale=0.1, offset=0.0, isSigned=False)
    ss_net_Current_Sig = DbcData(value=0.0, startBit=23, numBits=16, scale=0.1, offset=-3000.0, isSigned=False)
    ss_Soc_Sig = DbcData(value=0.0, startBit=39, numBits=16, scale=0.1, offset=0.0, isSigned=False)
    ss_temp_Sig = DbcData(value=0.0, startBit=7, numBits=8, scale=1.0, offset=-40.0, isSigned=False)

    # Define DBC Data for the output signals of ABS
    abs_voltage_sig = DbcData(value=0.0, startBit=0, numBits=16, scale=0.01, offset=0.0, isSigned=False)
    abs_netCurrent_sig = DbcData(value=0.0, startBit=16, numBits=16, scale=0.04, offset=0.0, isSigned=True)
    abs_totalVoltage_sig = DbcData(value=0.0, startBit=32, numBits=16, scale=0.01, offset=0.0, isSigned=False)
    abs_soc_sig = DbcData(value=0.0, startBit=0, numBits=16, scale=0.1, offset=0.0, isSigned=False)
    abs_temp_sig = DbcData(value=0.0, startBit=0, numBits=12, scale=0.1, offset=0.0, isSigned=True)

    # Test MSB decoding and LSB encoding for all signals

    #Create frames from CAN logs
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

    print("Calculated Voltage (MSB):", calculated_voltage)
    print("Calculated Net Current (MSB):", calculated_net_current)
    print("Calculated SOC (MSB):", calculated_soc)
    print("Calculated Temp (MSB):", calculated_temp)

    voltage_diff = abs(calculated_voltage - voltage)
    net_current_diff = abs(calculated_net_current - net_current)
    soc_diff = abs(calculated_soc - soc)
    temp_diff = abs(calculated_temp - temp)

    print("Voltage Difference (MSB):", voltage_diff)
    print("Net Current Difference (MSB):", net_current_diff)
    print("SOC Difference (MSB):", soc_diff)
    print("Temp Difference (MSB):", temp_diff)

    assert abs(voltage_diff) < 0.1
    assert abs(net_current_diff) < 0.1
    assert abs(soc_diff) < 0.1
    assert abs(temp_diff) < 0.1

    # MSB Encoding
    ss_Voltage_Sig.value = calculated_voltage
    ss_net_Current_Sig.value = calculated_net_current
    ss_Soc_Sig.value = calculated_soc
    ss_temp_Sig.value = calculated_temp

    frame = values_to_msb([ss_Voltage_Sig, ss_net_Current_Sig, ss_Soc_Sig])
    print("MSB Encoded Frame:", dump(frame))
    print("Expected Frame: 01 F2 76 94 00 90 F1 FF")
    

    frame_temp = values_to_msb([ss_temp_Sig])
    print("MSB Encoded Temp Frame:", dump(frame_temp))
    print("Expected Temp Frame: 67 01 62 02 05 00 00 00")

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

    print("Calculated Voltage (LSB):", calculated_voltage)
    print("Calculated Voltage (LSB):", calculated_voltage2)
    print("Real Voltage (LSB):", voltage)
    print("Calculated Net Current (LSB):", calculated_net_current)
    print("Real Net Current (LSB):", net_current)
    print("Calculated SOC (LSB):", calculated_soc)
    print("Real SOC (LSB):", soc)
    print("Calculated Temp (LSB):", calculated_temp)
    print("Real Temp (LSB):", temp)

    voltage_diff = abs(calculated_voltage - voltage)
    voltage2_diff = abs(calculated_voltage2 - voltage)
    net_current_diff = abs(calculated_net_current - net_current)
    soc_diff = abs(calculated_soc - soc)
    temp_diff = abs(calculated_temp - temp)

    print("Voltage Difference (LSB):", voltage_diff)
    print("Voltage2 Difference (LSB):", voltage2_diff)
    print("Net Current Difference (LSB):", net_current_diff)
    print("SOC Difference (LSB):", soc_diff)
    print("Temp Difference (LSB):", temp_diff)

    # Set to < 1.0 to account for display rounding
    assert abs(voltage_diff) < 1.0
    assert abs(voltage2_diff) < 1.0
    assert abs(net_current_diff) < 1.0
    assert abs(soc_diff) < 1.0
    assert abs(temp_diff) < 1.0

    # LSB Encoding
    abs_voltage_sig.value = calculated_voltage
    abs_totalVoltage_sig.value = calculated_voltage
    abs_netCurrent_sig.value = calculated_net_current
    abs_soc_sig.value = calculated_soc
    abs_temp_sig.value = calculated_temp

    frame = values_to_lsb([abs_voltage_sig, abs_netCurrent_sig, abs_totalVoltage_sig])
    print("LSB Encoded Frame:", dump(frame))
    print("Expected Frame: 4C 15 C5 07 2B 15 21 06")
    frame_soc = values_to_lsb([abs_soc_sig])
    print("LSB Encoded SOC Frame:", dump(frame_soc))
    print("Expected SOC Frame: 57 02 23 02")
    frame_temp = values_to_lsb([abs_temp_sig])
    print("LSB Encoded Temp Frame:", dump(frame_temp))
    print("Expected Temp Frame: 53 21 43 11 92 27 8B 17")
    

# ---------- RUN ----------

if __name__ == "__main__":
    test_lsb_roundtrip()
    test_msb_roundtrip()
    test_signed_current()
    run_test_suite()
    print("✅ ALL TESTS PASSED")
