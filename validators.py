from datetime import datetime
from operator import truediv


def is_valid_stock_code(code: str) -> bool:
    return code.isdigit() and code.isascii() and len(code) == 6


def is_valid_date(value: str) -> bool:
    if value.isdigit() and value.isascii() and len(value) == 8:
        try:
            datetime.strptime(value, "%Y%m%d")
        except ValueError:
            return False
        return True
    return False



