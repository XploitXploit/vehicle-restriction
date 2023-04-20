import logging

logger = logging.getLogger("vehicle_restriction")


def create_regex_pattern(plate_pattern):
    regex = ""
    for pattern in plate_pattern:
        regex += pattern + "$|"
    return f"{regex[:-1]}"
