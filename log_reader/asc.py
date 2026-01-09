import polars as pl

def parseASC(file_path, TARGET_IDS) -> pl.DataFrame:
    """
    Parses an ASC file and extracts messages with specified IDs.

    Args:
        file_path (str): Path to the ASC file.
        TARGET_IDS (list): List of message IDs to extract.
    """
    messages = []
    
    # Read the ASC file line by line and extract relevant messages
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) < 8:
                continue
            # Cleans and parses each line, adding the default data to a list
            timestamp = float(parts[0])
            can_id = parts[4].rstrip('x')
        
            message_id = int(can_id, 16)
            if message_id not in TARGET_IDS:
                continue
            dlc = int(parts[8])
            data_bytes = [int(b, 16) for b in parts[9:9+dlc]]
            messages.append((message_id, timestamp, dlc, data_bytes))
    # Convert the list of messages to a Polars DataFrame
    return pl.DataFrame(messages, schema=["message_id", "timestamp", "dlc", "data_bytes"], orient="row")

def read_asc(file_path: str) -> pl.DataFrame:
    messages = []
    lineNum = 0
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            print(f"Parts: {parts}")
            lineNum += 1
            print(lineNum)
            if len(parts) < 8:
                continue
            timestamp = float(parts[0])
            can_id = parts[2].rstrip('x')
            messageID = int(can_id, 16)
            print(f"DLC: {parts[5]}")
            dlc = int(parts[5])
            data_bytes = [int(b, 16) for b in parts[6:6+dlc]]
            messages.append((messageID, timestamp, dlc, data_bytes))

    df = pl.DataFrame(messages, schema=['messageID', 'timestamp', 'dlc', 'data_bytes'], orient='row')
    return df