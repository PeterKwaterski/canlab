class IDException(Exception):
    def __init__(self):
        super().__init__("The ID(s) provided are not valid")