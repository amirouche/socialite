from enum import IntEnum


class SocialiterException(Exception):
    """Base socialiter exception"""

    pass


class SocialiterBase:
    """Base class for all socialiter class"""

    pass


class SpacePrefix(IntEnum):
    SPARKY = 0
    SEARCH = 1
    COUNTERS = 2
