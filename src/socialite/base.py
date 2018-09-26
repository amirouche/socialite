from enum import Enum


class SocialiteException(Exception):
    """Base socialite exception"""
    pass


class SocialiteBase:
    """Base class for all socialite class"""
    pass


class SpacePrefix(Enum):
    SPARKY = b'\x00'
