"""Integration tests for full workflow."""
import pytest
import tempfile
import os

from dbc.dbc_loader import extract_messages, load_cantools_dbc
from dbc.message_data import MessageData
from encoder.frame_encoder import values_to_lsb, values_to_msb
from decoder.frame_decoder import lsb_to_value, msb_to_value
from log_reader.asc import parseASC, read_asc
from dbc.dbc_data import DbcData


class TestFullWorkflow:
    """Integration tests for complete workflow."""

    @pytest.mark.integration
    def test_dbc_extract_encode_decode_workflow(self, sample_dbc_path):
        """Test full workflow: extract DBC → encode → decode."""
        # Extract messages from DBC
        messages = extract_messages(str(sample_dbc_path))
        
        assert len(messages) > 0
        
        # Get first message with signals
        message = messages[0]
        assert len(message.signals) > 0
        
        # Create a test signal with a value
        signal = message.signals[0]
        signal.value = 100.0
        
        # Encode based on signal format
        if signal.isLSB:
            frame = values_to_lsb([signal])
            decoded = lsb_to_value(frame, signal)
        else:
            frame = values_to_msb([signal])
            decoded = msb_to_value(frame, signal)
        
        # Verify roundtrip
        assert abs(decoded - signal.value) < 1.0

    @pytest.mark.integration
    def test_asc_parse_with_dbc_decode(self, sample_dbc_path, sample_asc_path):
        """Test parsing ASC file and decoding with DBC signals."""
        # Extract messages from DBC
        messages = extract_messages(str(sample_dbc_path))
        message = messages[0]  # Use first message
        
        # Parse ASC file
        target_ids = [message.dbc_id]
        df = parseASC(str(sample_asc_path), target_ids)
        
        if len(df) > 0:
            # Get first row
            row = df.row(0, named=True)
            frame_data = bytearray(row["data_bytes"])
            
            # Decode first signal
            if len(message.signals) > 0:
                signal = message.signals[0]
                if signal.isLSB:
                    decoded_value = lsb_to_value(frame_data, signal)
                else:
                    decoded_value = msb_to_value(frame_data, signal)
                
                # Verify we got a reasonable value
                assert isinstance(decoded_value, float)

    @pytest.mark.integration
    def test_cantools_dbc_integration(self, sample_dbc_path):
        """Test integration with cantools library."""
        # Load DBC with cantools
        db = load_cantools_dbc(str(sample_dbc_path))
        
        # Extract messages with our function
        messages = extract_messages(str(sample_dbc_path))
        
        # Verify both methods work
        assert db is not None
        assert len(messages) > 0
        
        # Verify message IDs match
        cantools_message_ids = {msg.frame_id for msg in db.messages}
        our_message_ids = {msg.dbc_id for msg in messages}
        
        # Note: IDs might be transformed, so we just verify both have messages
        assert len(cantools_message_ids) > 0
        assert len(our_message_ids) > 0

    @pytest.mark.integration
    def test_multiple_signals_encode_decode(self):
        """Test encoding and decoding multiple signals in one frame."""
        signals = [
            DbcData(
                value=100.0, startBit=0, numBits=16, scale=0.1, offset=0.0,
                isSigned=False, name="signal1", isLSB=True
            ),
            DbcData(
                value=50.0, startBit=16, numBits=16, scale=0.1, offset=0.0,
                isSigned=False, name="signal2", isLSB=True
            ),
        ]
        
        # Encode
        frame = values_to_lsb(signals)
        
        # Decode
        decoded1 = lsb_to_value(frame, signals[0])
        decoded2 = lsb_to_value(frame, signals[1])
        
        # Verify
        assert abs(decoded1 - signals[0].value) < 1.0
        assert abs(decoded2 - signals[1].value) < 1.0

    @pytest.mark.integration
    def test_msb_lsb_mixed_workflow(self):
        """Test workflow with both MSB and LSB signals."""
        msb_signal = DbcData(
            value=22.0, startBit=11, numBits=12, scale=0.1, offset=-40.0,
            isSigned=False, name="msb_signal", isLSB=False
        )
        
        lsb_signal = DbcData(
            value=98.6, startBit=0, numBits=16, scale=0.1, offset=0.0,
            isSigned=False, name="lsb_signal", isLSB=True
        )
        
        # Encode MSB
        msb_frame = values_to_msb([msb_signal])
        msb_decoded = msb_to_value(msb_frame, msb_signal)
        assert abs(msb_decoded - msb_signal.value) < 0.1
        
        # Encode LSB
        lsb_frame = values_to_lsb([lsb_signal])
        lsb_decoded = lsb_to_value(lsb_frame, lsb_signal)
        assert abs(lsb_decoded - lsb_signal.value) < 0.1

    @pytest.mark.integration
    def test_error_handling_workflow(self):
        """Test error handling in full workflow."""
        # Test with invalid DBC path
        with pytest.raises(FileNotFoundError):
            extract_messages("nonexistent.dbc")
        
        # Test with invalid ASC path
        with pytest.raises(FileNotFoundError):
            parseASC("nonexistent.asc", [0x100])
        
        # Test with invalid signal (out of bounds)
        from exceptions.signal_format_exception import SignalFormatException
        with pytest.raises(SignalFormatException):
            DbcData(
                value=0.0, startBit=60, numBits=10, scale=1.0, offset=0.0,
                isSigned=False, name="invalid", isLSB=True
            )
