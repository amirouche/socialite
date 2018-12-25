import logging
from uuid import uuid4

from immutables import Map

import found


log = logging.getLogger(__name__)


class YiwenException(Exception):
    pass


class PatternException(YiwenException):
    """Raised when the pattern can not be resolved by the query engine.

    .. warning:: It might be a bug. Try to re-order the pattern in the
                 query to make it work before reporting bug.

    """

    pass


PREFIX_SPO = b"\x00"
PREFIX_POS = b"\x01"


class var:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<var %r>" % self.name


def pattern_bind(pattern, binding):
    subject, predicate, object = pattern
    if isinstance(subject, var) and binding.get(subject.name) is not None:
        subject = binding[subject.name]
    if isinstance(predicate, var) and binding.get(predicate.name) is not None:
        predicate = binding[predicate.name]
    if isinstance(object, var) and binding.get(object.name) is not None:
        object = binding[object.name]
    return subject, predicate, object


class Predicate:
    def __init__(self, name, validator, packing=None, pos=False):
        self.name = name
        self.validator = validator
        self.packing = packing
        self.pos = pos

    def valid(self, object):
        return self.validator(object)

    def pack(self, object):
        if self.packing is not None:
            return self.packing.pack(object)
        else:
            return object

    def unpack(self, object):
        if self.packing is not None:
            return self.packing.unpack(object)
        else:
            return object


class Yiwen:

    var = var

    def __init__(self, prefix):
        self._prefix = prefix
        self._predicates = {}

    def predicate(self, *args, **kwargs):
        """See ``Predicate`` class for parameters specification."""
        predicate = Predicate(*args, **kwargs)
        self._predicates[predicate.name] = predicate

    @found.transactional
    async def uuid(self, tr):
        uid = uuid4()
        start = found.pack((self._prefix, PREFIX_SPO, uid))
        end = b"\xFF"
        items = await tr.get_range(start, end, limit=1)
        if not items:
            return uid
        key, _ = items[0]
        _, _, subject, _, _ = found.unpack(key)
        assert subject != uid, "Unlikely Error!"
        return uid

    @found.transactional
    async def all(self, tr):
        start = found.pack((self._prefix, PREFIX_SPO))
        end = found.strinc(start)
        msg = "fetching everything between start=%r and end=%r"
        log.debug(msg, start, end)
        out = []
        items = await tr.get_range(start, end)
        for key, _ in items:  # value is always empty
            _, _, subject, predicate, object = found.unpack(key)
            predicate = self._predicates[predicate]
            object = predicate.unpack(object)
            out.append((subject, predicate.name, object))
        return out

    @found.transactional
    async def add(self, tr, *triples):
        for triple in triples:
            subject, predicate, object = triple
            # might fail because of unknown predicate
            predicate = self._predicates[predicate]
            assert predicate.valid(object), "Invalid object for predicate"
            object = predicate.pack(object)
            # choose correct packer function
            if found.has_incomplete_versionstamp((subject, object)):
                pack = found.pack_with_versionstamp
            else:
                pack = found.pack
            # add data aka. spo
            key = pack((self._prefix, PREFIX_SPO, subject, predicate.name, object))
            tr.set(key, b"")
            if predicate.pos:
                # index in 'pos'
                key = pack((self._prefix, PREFIX_POS, predicate.name, object, subject))
                tr.set(key, b"")

    @found.transactional
    async def remove(self, tr, *triples):
        for triple in triples:
            subject, predicate, object = triple
            # might fail because of unknown predicate
            predicate = self._predicates[predicate]
            # might fail because of not the correct type
            object = predicate.pack(object)
            # remove from data
            key = found.pack(
                (self._prefix, PREFIX_SPO, subject, predicate.name, object)
            )
            tr.clear(key)
            if predicate.pos:
                # remove from index
                key = found.pack(
                    (self._prefix, PREFIX_POS, predicate.name, object, subject)
                )
                tr.clear(key)

    @found.transactional
    async def _lookup_pos_subjects(self, tr, predicate, object):
        predicate = self._predicates[predicate]
        object = predicate.pack(object)
        start = found.pack((self._prefix, PREFIX_POS, predicate.name, object))
        end = found.strinc(start)
        items = await tr.get_range(start, end)
        out = list()
        for key, _ in items:
            _, _, _, _, subject = found.unpack(key)
            out.append(subject)
        return out

    @found.transactional
    async def exists(self, tr, subject, predicate, object):
        predicate = self._predicates[predicate]
        object = predicate.pack(object)
        key = found.pack((self._prefix, PREFIX_SPO, subject, predicate.name, object))
        value = await tr.get(key)
        return value is not None

    @found.transactional
    async def where(self, tr, pattern, *patterns):
        # seed bindings
        vars = tuple((isinstance(item, var) for item in pattern))
        if vars == (True, False, False):
            subject, predicate, object = pattern
            subjects = await self._lookup_pos_subjects(tr, predicate, object)
            name = subject.name
            bindings = [Map().set(name, subject) for subject in subjects]
        elif vars == (False, True, True):
            # TODO: extract to a method
            subject = pattern[0]
            start = found.pack((self._prefix, PREFIX_SPO, subject))
            end = found.strinc(start)
            items = await tr.get_range(start, end)
            bindings = []
            for key, _ in items:
                _, _, _, predicate, object = found.unpack(key)
                predicate = self._predicates[predicate]
                object = predicate.unpack(object)
                binding = Map()
                binding = binding.set(pattern[1].name, predicate.name)
                binding = binding.set(pattern[2].name, object)
                bindings.append(binding)
        elif vars == (False, False, True):
            # TODO: extract to a method
            subject = pattern[0]
            predicate = pattern[1]
            start = found.pack((self._prefix, PREFIX_SPO, subject, predicate))
            end = found.strinc(start)
            items = await tr.get_range(start, end)
            bindings = []
            for key, _ in items:
                _, _, _, _, object = found.unpack(key)
                predicate = self._predicates[predicate]
                object = predicate.unpack(object)
                binding = Map()
                binding = binding.set(pattern[2].name, object)
                bindings.append(binding)
        else:
            raise PatternException(pattern)

        log.debug("seed bindings: %r", bindings)
        # contine matching other patterns, if any.
        for pattern in patterns:  # one
            log.debug("matching pattern: %r", pattern)
            next_bindings = []
            for binding in bindings:  # two
                bound_pattern = pattern_bind(pattern, binding)
                log.debug("bound pattern: %r", bound_pattern)
                vars = tuple((isinstance(item, var) for item in bound_pattern))
                if vars == (False, False, False):
                    log.debug("clause: False, False, False")
                    ok = await self.exists(tr, *bound_pattern)
                    if ok:
                        # this binding is valid against this bound_pattern,
                        # proceed with this binding and continue with
                        # the next pattern.
                        next_bindings.append(binding)
                elif vars == (False, False, True):
                    # TODO: extract to a method
                    log.debug("clause: False, False, True")
                    subject, predicate, object = bound_pattern
                    predicate = self._predicates[predicate]
                    start = found.pack(
                        (self._prefix, PREFIX_SPO, subject, predicate.name)
                    )
                    end = found.strinc(start)
                    items = await tr.get_range(start, end)
                    for key, _ in items:
                        _, _, _, _, value = found.unpack(key)
                        value = predicate.pack(value)
                        new = binding.set(object.name, value)
                        next_bindings.append(new)
                elif vars == (True, False, False):
                    log.debug("clause: True, False, False")
                    subject, predicate, object = bound_pattern
                    predicate = self._predicates[predicate]
                    object = predicate.pack(object)
                    values = await self._lookup_pos_subjects(tr, predicate.name, object)
                    for value in values:
                        new = binding.set(subject.name, value)
                        next_bindings.append(new)
                else:
                    raise PatternException(pattern)
            bindings = next_bindings
        return bindings
