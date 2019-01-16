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

WORD_MIN_LENGTH = 2
WORD_MAX_LENGTH = 64  # sha2 length


def sane(word):
    return WORD_MIN_LENGTH <= len(word) <= WORD_MAX_LENGTH


def string2words(string):
    """Converts a string to a list of words.

    Removes punctuation, lowercase, words strictly smaller than 2 and strictly bigger than 64
    characters

    Returns a set.
    """
    clean = string.translate(GARBAGE_TO_SPACE).lower()
    unaccented = unidecode(clean)
    words = set(word for word in unaccented.split() if sane(word))
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


def compute_tokens(words):
    tokens = set(stem(word) for word in words if stem(word) not in STOP_WORDS)
    return tokens


@found.transactional
async def index(tr, app, uid, document, user_version=0):
    """Index ``document``.

    :param uid: must be a unique identifier for ``document`` that can be packed.

    :param document: must be a string. The string will be "sanitized" by removing punctuation,
    small and big words.

    Return the next available ``user_version`` for use with ``Versionstamp``.

    """
    # compute words for scoring
    words = string2words(document)
    await app["search"].add(tr, (uid, "document/words", words))
    for word in words:
        await Counter(Counter.KIND.WORD, word).increment(tr)
    # compute tokens for seed result matching
    tokens = compute_tokens(words)
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
        await Counter(Counter.KIND.TOKEN, token).increment()
    return user_version


class Query:

    def __init__(self, string):
        self._string = string
        # TODO: support booleans operators
        # TODO: support synonyms
        self.positive_tokens = compute_tokens(self._string.split())
        self.negative_words = set()

    def __repr__(self):
        return '<Query "{}">'.format(self._string)

    def match(self, words):  # TODO: support booleans operators
        # negative words are a no go
        for word in self.negative_words:
            if word in words:
                return False
        # We match document `words` set against tokens because we want that if the user queries a
        # given word another word with the same stem can be a match. For instance, if the user
        # queries for 'production' and the document contains 'productive' then document is a valid
        # match
        tokens = compute_tokens(words)
        for token in self.positive_tokens:
            if token not in tokens:
                return False
        # all positive tokens are found in the document `words` set
        return True


async def compute_score(tr, query, words):
    if not query.match(words):
        return -1

    # TODO: Compute TF-IDF...

    return 1


@found.transactional
async def search(tr, app, query):
    """Search for documents matching ``query``.

    :param query: must be an instance of ``Query``.

    """
    # compute seed token
    positive_tokens_counter = Counter()
    for token in query.positive_tokens:
        positive_tokens_counter[token] = await Counter(Counter.KIND.TOKEN, token).get()
        # reverse the count so that the Counter.most_common returns the least common
        positive_tokens_counter[token] = - positive_tokens_counter[token]
    seed_token = positive_tokens_counter.most_common(1)[0]
    if seed_token[1] == 0:
        # The most least token is not found in the database,
        # it means there is no results.
        return {}
    seed_token = seed_token[0]
    # fetch seed token's unique identifier
    bindings = await app["search"].where(tr, (var('seed_token_uid'), 'token/value', seed_token))
    binding = bindings[0]
    seed_token_uid = binding['seed_token_uid']
    # fetch all documents that contains this token (aka. candidates)
    bindings = await app["search"].where(
        tr,
        (seed_token_uid, 'token/document', var('candidate_document_uid'))
    )
    scores = {}
    for binding in bindings:  # TODO: async for?
        candidate_document_uid = binding['candidate_document_uid']
        words = await app["search"].where(
            tr,
            (candidate_document_uid, 'document/words', var('words'))
        )
        words = set(words[0]['words'])
        # score?!
        score = await compute_score(tr, query, words)
        if score > 0:
            # win!
            scores[candidate_document_uid] = score
    return scores
