"""Unit tests for ASC file parser."""
import pytest
import tempfile
import os

from log_reader.asc import parseASC, read_asc


class TestParseASC:
    """Tests for parseASC function."""

    @pytest.mark.unit
    def test_parse_asc_basic(self, sample_asc_path):
        """Test parsing a basic ASC file."""
        target_ids = [419384053, 419382517]
        df = parseASC(str(sample_asc_path), target_ids)
        
        assert df is not None
        assert len(df) > 0
        assert "message_id" in df.columns
        assert "timestamp" in df.columns
        assert "dlc" in df.columns
        assert "data_bytes" in df.columns

    @pytest.mark.unit
    def test_parse_asc_filters_by_id(self, sample_asc_path):
        """Test that parseASC filters messages by target IDs."""
        target_ids = [0x100]
        df = parseASC(str(sample_asc_path), target_ids)
        
        # All messages should have ID 0x100
        for row in df.iter_rows(named=True):
            assert row["message_id"] == 0x100

    @pytest.mark.unit
    def test_parse_asc_with_x_suffix(self, sample_asc2_path):
        """Test parsing ASC file with 'x' suffix on CAN IDs."""
        target_ids = [419384053, 419382517]
        df = parseASC(str(sample_asc2_path), target_ids)
        
        assert df is not None
        assert len(df) > 0

    @pytest.mark.unit
    def test_parse_asc_empty_file(self):
        """Test parsing an empty ASC file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.asc', delete=False) as f:
            f.write("date Mon Jan 01 00:00:00.000000 2024\n")
            f.write("base hex  timestamps absolute\n")
            temp_path = f.name

        try:
            df = parseASC(temp_path, [0x100])
            assert len(df) == 0
        finally:
            os.unlink(temp_path)

    @pytest.mark.unit
    def test_parse_asc_no_matching_ids(self, sample_asc_path):
        """Test parsing ASC file with no matching message IDs."""
        target_ids = [0x999]
        df = parseASC(str(sample_asc_path), target_ids)
        
        assert len(df) == 0

    @pytest.mark.unit
    def test_parse_asc_malformed_line(self):
        """Test parsing ASC file with malformed lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.asc', delete=False) as f:
            f.write("date Mon Jan 01 00:00:00.000000 2024\n")
            f.write("base hex  timestamps absolute\n")
            f.write("invalid line\n")
            f.write("    0.000000 1  100        Rx   d 8 00 64 00 00 00 00 00 00\n")
            temp_path = f.name

        try:
            target_ids = [0x100]
            df = parseASC(temp_path, target_ids)
            # Should skip malformed lines and process valid ones
            assert df is not None
        finally:
            os.unlink(temp_path)


class TestReadAsc:
    """Tests for read_asc function."""

    @pytest.mark.unit
    def test_read_asc_basic(self, sample_asc_path):
        """Test reading a basic ASC file."""
        df = read_asc(str(sample_asc_path))
        
        assert df is not None
        assert len(df) > 0
        assert "messageID" in df.columns
        assert "timestamp" in df.columns
        assert "dlc" in df.columns
        assert "data_bytes" in df.columns

    @pytest.mark.unit
    def test_read_asc_data_structure(self, sample_asc_path):
        """Test that read_asc returns correct data structure."""
        df = read_asc(str(sample_asc_path))
        
        # Check that data_bytes is a list
        for row in df.iter_rows(named=True):
            assert isinstance(row["data_bytes"], list)
            assert isinstance(row["messageID"], int)
            assert isinstance(row["timestamp"], float)
            assert isinstance(row["dlc"], int)

    @pytest.mark.unit
    def test_read_asc_empty_file(self):
        """Test reading an empty ASC file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.asc', delete=False) as f:
            f.write("date Mon Jan 01 00:00:00.000000 2024\n")
            f.write("base hex  timestamps absolute\n")
            temp_path = f.name

        try:
            df = read_asc(temp_path)
            assert len(df) == 0
        finally:
            os.unlink(temp_path)

    @pytest.mark.unit
    def test_read_asc_file_not_found(self):
        """Test read_asc with non-existent file."""
        with pytest.raises(FileNotFoundError):
            read_asc("nonexistent.asc")
