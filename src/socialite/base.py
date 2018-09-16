from enum import Enum


class SocialiteException(Exception):
    """Base socialite exception"""
    pass


class SocialiteBase:
    """Base class for all socialite class"""
    pass


class SubspacePrefix(Enum):
    SPARKY = b'\x01'
