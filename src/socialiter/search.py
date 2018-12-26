from string import punctuation

import found
import msgpack
import snowballstemmer
from wordfreq import top_n_list
from unidecode import unidecode

from socialiter.base import SpacePrefix
from socialiter.data.space.yiwen import Yiwen
from socialiter.data.space.yiwen import var
from socialiter.data.counter import Counter


stem = snowballstemmer.stemmer("english").stemWord


GARBAGE_TO_SPACE = dict.fromkeys((ord(x) for x in punctuation), " ")
STOP_WORDS = set(top_n_list("en", 500))

SHA2_LENGTH = 64


def sane(word):
    return 2 <= len(word) <= SHA2_LENGTH


def string2words(string):
    """Convert a string to a list of words.

    Remove punctuation, lowercase, words strictly smaller than 2 and strictly bigger than 64
    characters

    """
    clean = string.translate(GARBAGE_TO_SPACE).lower()
    unaccented = unidecode(clean)
    words = [word for word in unaccented.split() if sane(word)]
    return words


class WordsPacking:
    @classmethod
    def pack(cls, value):
        return msgpack.dumps(value)

    @classmethod
    def unpack(cls, value):
        return msgpack.loads(value, raw=False)


class SearchSpace(Yiwen):
    def __init__(self):
        super().__init__(SpacePrefix.SEARCH.value)

        self.predicate("document/words", lambda x: isinstance(x, list), WordsPacking)
        self.predicate("token/value", lambda x: isinstance(x, str), pos=True)
        self.predicate("token/document", lambda x: True)


@found.transactional
async def index(tr, app, uid, document, user_version=0):
    """Index ``document``.

    :param uid: must be a unique identifier for ``document`` that can be packed.

    :param document: must be a string.

    Return the next available ``user_version`` for use with ``Versionstamp``.

    """
    # compute words for scoring
    words = string2words(document)
    await app["search"].add(tr, (uid, "document/words", words))
    for word in words:
        await Counter(Counter.KIND.WORD, word).increment(tr)
    # compute tokens for seed result matching
    tokens = set(stem(word) for word in words if stem(word) not in STOP_WORDS)
    for token in tokens:
        # get or create token entry
        bindings = await app["search"].where(tr, (var("uid"), "token/value", token))
        try:
            binding = bindings[0]
        except IndexError:
            token_uid = found.Versionstamp(user_version=user_version)
            user_version += 1
            await app["search"].add(tr, (token_uid, "token/value", token))
        else:
            token_uid = binding["uid"]
        # link token to document
        await app["search"].add(tr, (token_uid, "token/document", uid))
        # increment token counter
        Counter(Counter.KIND.TOKEN, token).increment()
    return user_version


@found.transactional
async def search(tr, app, query):
    """Search for documents matching ``query``.

    :param query: must be a boolean keyword query.

    """
    pass
