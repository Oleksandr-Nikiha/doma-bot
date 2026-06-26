import re

NAME_PATTERN = re.compile(r"^[а-яяіїєґА-ЯІЇЄҐ'`\- ]{2,20}$")
ADDRESS_PATTERN = re.compile(r'^[а-яіїєґА-ЯІЇЄҐA-Za-z0-9\'\`\-\.\, ]{10,100}$')
TIME_PATTERN = re.compile(r'^((1[0-9]|2[0-1]):[0-5]\d|22:00)$')
CHANGE_PATTERN = re.compile(r'^\d{1,4}$')


def is_valid_name(name: str) -> bool:
    return bool(NAME_PATTERN.match(name.strip()))

def is_valid_address(address: str) -> bool:
    return bool(ADDRESS_PATTERN.match(address.strip()))

def is_valid_time(time: str) -> bool:
    return bool(TIME_PATTERN.match(time.strip()))

def is_valid_change(change: str) -> bool:
    return bool(CHANGE_PATTERN.match(change.strip()))