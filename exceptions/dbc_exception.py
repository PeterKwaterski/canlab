class DbcException(Exception):
    def __init__(self):
        super().__init__("The DBC file is not valid")