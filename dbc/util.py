"""A module containing simple DBC utility functions

This module provides high level functions for handling loading, storing, and cleaning DBCs.
"""

import os
import sys
from pathlib import Path
from typing import Dict
import cantools

def clean_dbc(src_path: str, dst_path: str = None) -> str:
    """
    Cleans a DBC file by removing lines not directly related to messages and signal numerics.

    Args:
        src_path: Path to the source DBC file.
        dst_path: Path to save the cleaned DBC file.
    Returns:
        the file location of the cleaned DBC.
    """

    src_file_path = _resource_path(src_path)
    dst_file_path = os.path.join(os.getcwd(), dst_path if dst_path else src_file_path)

    dst_dir = os.path.dirname(dst_file_path)
    if dst_dir:
        os.makedirs(dst_dir, exist_ok=True)

    with open(src_file_path, 'r', encoding='utf-8') as src_file, open(dst_file_path, 'w', encoding='utf-8') as dst_file:
        for line in src_file:
            if 'BA_' in line or '12V' in line:
                continue
            dst_file.write(line)

    return dst_path

def _resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def determine_db(messageID: int, dbc_list: Dict) -> cantools.database:
    """
    Determines which DBC file contains a given message ID.

    Args:
        messageID: The message ID to search for.
        dbc_list: the list of DBC objects to search through
    
    Raises:
        KeyError: If the message ID is not found in any loaded DBC.
    """
    for path, db in dbc_list.items():
            db.get_message_by_frame_id(messageID)
            return db
    raise KeyError(f"The Message ID {messageID} is not in any loaded DB")

def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent.resolve()
    
def gen_path(path, base_dir):
    try:
        return str(Path(path).resolve().relative_to(base_dir))
    except ValueError:
        return str(Path(path).resolve())