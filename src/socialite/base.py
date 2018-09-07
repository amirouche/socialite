from enum import Enum
from socialite.fdb import transactional
from socialite.fdb import Subspace


class SocialiteBase:
    """Base class for all socialite class"""
    pass



class SubspacePrefixes(Enum):
    COLLECTIONS = (b'\x00',)



COLLECTIONS = Subspace(SubspacePrefixes.COLLECTIONS)



@fdb.transactional
async def insert(tr, collection, document):
    pass


@fdb.transactional
async def get(tr, collection, document):
    pass


@fdb.transactional
async def query(tr, collection, where):
    pass


@fdb.transactional
async def delete(tr, collection, uid):
    pass
