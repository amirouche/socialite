from enum import Enum


class SocialiterException(Exception):
    """Base socialiter exception"""

    pass


class SocialiterBase:
    """Base class for all socialiter class"""

    pass


class SpacePrefix(Enum):
    SPARKY = b"\x00"  # TODO: rename 'MAIN'
    SEARCH = b"\x01"
    COUNTERS = b"\x02"
