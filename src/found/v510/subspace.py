#
# This source file was part of the FoundationDB open source project
# it was forked to implement the Python asyncio bindings in found project.
# see https://github.com/amirouche/found
#
# Copyright 2013-2018 Apple Inc. and the FoundationDB project authors
# Copyright 2018 Amirouche Boubekki <amirouche@hypermove.net>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from found.v510 import pack
from found.v510 import unpack
from found.v510 import range
from found.v510 import pack_with_versionstamp


class Subspace:

    def __init__(self, prefix_tuple=tuple(), raw_prefix=b''):
        self.raw_prefix = pack(prefix_tuple, prefix=raw_prefix)

    def __repr__(self):
        return '<Subspace(raw_prefix=' + repr(self.raw_prefix) + ')>'

    def __getitem__(self, name):
        return Subspace((name,), self.raw_prefix)

    def key(self):
        return self.raw_prefix

    def pack(self, t=tuple()):
        return pack(t, prefix=self.raw_prefix)

    def pack_with_versionstamp(self, t=tuple()):
        return pack_with_versionstamp(t, prefix=self.raw_prefix)

    def unpack(self, key):
        if not self.contains(key):
            raise ValueError('Cannot unpack key that is not in subspace.')
        return unpack(key, prefix_len=len(self.raw_prefix))

    def range(self, t=tuple()):
        p = range(t)
        return slice(self.raw_prefix + p.start, self.raw_prefix + p.stop)

    def contains(self, key):
        return key.startswith(self.raw_prefix)

    def as_foundationdb_key(self):
        return self.raw_prefix

    def subspace(self, tuple):
        return Subspace(tuple, self.raw_prefix)
