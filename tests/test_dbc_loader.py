"""Unit tests for DBC loader functions."""
import pytest
import tempfile
import os
from pathlib import Path

from dbc.dbc_loader import extract_messages, load_cantools_dbc
from dbc.message_data import MessageData
from exceptions.dbc_exception import DbcException


class TestExtractMessages:
    """Tests for extract_messages function."""

    @pytest.mark.unit
    def test_extract_messages_basic(self, sample_dbc_path):
        """Test extracting messages from a basic DBC file."""
        messages = extract_messages(str(sample_dbc_path))
        
        assert len(messages) == 2
        assert messages[0].dbc_id == 100
        assert messages[1].dbc_id == 200
        
        # Check first message signals
        assert len(messages[0].signals) == 2
        assert messages[0].signals[0].name == "Signal1"
        assert messages[0].signals[1].name == "Signal2"
        
        # Check second message signals
        assert len(messages[1].signals) == 2
        assert messages[1].signals[0].name == "Signal3"
        assert messages[1].signals[1].name == "Signal4"

    @pytest.mark.unit
    def test_extract_messages_signal_properties(self, sample_dbc_path):
        """Test that signal properties are correctly extracted."""
        messages = extract_messages(str(sample_dbc_path))
        
        signal1 = messages[0].signals[0]
        assert signal1.startBit == 0
        assert signal1.numBits == 16
        assert signal1.isLSB == True
        assert signal1.isSigned == False
        assert signal1.scale == 0.1
        assert signal1.offset == 0.0

    @pytest.mark.unit
    def test_extract_messages_file_not_found(self):
        """Test extract_messages with non-existent file."""
        with pytest.raises(FileNotFoundError):
            extract_messages("nonexistent.dbc")

    @pytest.mark.unit
    def test_extract_messages_empty_file(self, test_data_dir):
        """Test extract_messages with empty DBC file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dbc', delete=False) as f:
            f.write("VERSION \"\"\n\nBS_:\n\nBU_: ECU1\n")
            temp_path = f.name

        try:
            messages = extract_messages(temp_path)
            assert len(messages) == 0
        finally:
            os.unlink(temp_path)

    @pytest.mark.unit
    def test_extract_messages_malformed_dbc(self, test_data_dir):
        """Test extract_messages with malformed DBC file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dbc', delete=False) as f:
            f.write("BO_ invalid line\n")
            temp_path = f.name

        try:
            # Should handle malformed lines gracefully or raise appropriate exception
            with pytest.raises((IndexError, DbcException)):
                extract_messages(temp_path)
        finally:
            os.unlink(temp_path)


class TestLoadCantoolsDbc:
    """Tests for load_cantools_dbc function."""

    @pytest.mark.unit
    def test_load_cantools_dbc_success(self, sample_dbc_path):
        """Test loading a DBC file with cantools."""
        db = load_cantools_dbc(str(sample_dbc_path))
        assert db is not None
        assert len(db.messages) > 0

    @pytest.mark.unit
    def test_load_cantools_dbc_invalid_extension(self):
        """Test load_cantools_dbc with invalid file extension."""
        with pytest.raises(DbcException):
            load_cantools_dbc("test.txt")

    @pytest.mark.unit
    def test_load_cantools_dbc_file_not_found(self):
        """Test load_cantools_dbc with non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_cantools_dbc("nonexistent.dbc")

    @pytest.mark.unit
    def test_load_cantools_dbc_with_dst_path(self, sample_dbc_path, tmp_path):
        """Test load_cantools_dbc with destination path."""
        dst_path = str(tmp_path / "cleaned.dbc")
        db = load_cantools_dbc(str(sample_dbc_path), dst_path)
        assert db is not None
        assert os.path.exists(dst_path)


class TestMessageData:
    """Tests for MessageData class."""

    @pytest.mark.unit
    def test_message_data_with_dbc_id(self):
        """Test MessageData initialization with dbc_id."""
        msg = MessageData(dbc_id=100)
        assert msg.dbc_id == 100
        assert msg.bus_id is not None
        assert isinstance(msg.signals, list)
        assert len(msg.signals) == 0

    @pytest.mark.unit
    def test_message_data_with_bus_id(self):
        """Test MessageData initialization with bus_id."""
        msg = MessageData(bus_id=0x100)
        assert msg.bus_id == 0x100
        assert msg.dbc_id is not None
        assert isinstance(msg.signals, list)

    @pytest.mark.unit
    def test_message_data_no_id(self):
        """Test MessageData initialization without ID raises exception."""
        from exceptions.id_exception import IDException
        with pytest.raises(IDException):
            MessageData()

    @pytest.mark.unit
    def test_message_data_add_signals(self):
        """Test adding signals to MessageData."""
        from dbc.dbc_data import DbcData
        
        msg = MessageData(dbc_id=100)
        signal = DbcData(
            value=10.0,
            startBit=0,
            numBits=8,
            scale=1.0,
            offset=0.0,
            isSigned=False,
            name="test",
            isLSB=True
        )
        msg.signals.append(signal)
        
        assert len(msg.signals) == 1
        assert msg.signals[0].name == "test"
