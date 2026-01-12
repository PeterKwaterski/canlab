# canlab

A general CAN framework API for Python - encode/decode CAN frames, parse DBC files, and work with CAN log files.

## Installation

```bash
pip install canlab
```
or
```bash
uv add canlab
```

## Quick Start

### Loading a DBC File

```python
from dbc import load_cantools_dbc, extract_messages

# Load DBC file with cantools
db = load_cantools_dbc("path/to/file.dbc")

# Extract messages into MessageData objects
messages = extract_messages("path/to/file.dbc")
```

### Encoding CAN Frames

```python
from dbc import DbcData
from encoder import values_to_lsb, values_to_msb

# Create a signal
signal = DbcData(
    startBit=0,
    numBits=16,
    scale=0.1,
    offset=0.0,
    isSigned=False,
    name="temperature",
    isLSB=True,
    value=98.6
)

# Encode to LSB (Intel) format
frame = values_to_lsb([signal])
```

### Decoding CAN Frames

```python
from decoder import lsb_to_value, msb_to_value

# Decode from LSB format
value = lsb_to_value(frame, signal)

# Decode from MSB (Motorola) format
value = msb_to_value(frame, signal)
```

### Parsing ASC Log Files

```python
from log_reader.asc import parseASC, read_asc

# Parse ASC file filtering by message IDs
target_ids = [0x100, 0x200]
df = parseASC("log.asc", target_ids)

# Read all messages from ASC file
df = read_asc("log.asc")
```

## Features

- Load and parse DBC files
- Encode physical values to CAN frames (LSB and MSB formats)
- Decode CAN frames to physical values
- Parse ASC log files
- Convert between DBC IDs and bus IDs

## Requirements

- Python >= 3.12
- cantools >= 41.0.2
- polars >= 1.36.1

## License

MIT License - see LICENSE file for details.
