from enum import Enum


class SocialiterException(Exception):
    """Base socialiter exception"""
    pass


class SocialiterBase:
    """Base class for all socialiter class"""
    pass


class SpacePrefix(Enum):
    MAIN = b"\x00"
