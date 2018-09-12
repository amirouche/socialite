"""https://stackoverflow.com/a/40548567/140837"""
#!/usr/bin/env python3
import zlib
from mmap import PAGESIZE


CHUNKSIZE = PAGESIZE


# This is a generator that yields *decompressed* chunks from
# a gzip file. This is also called a stream or lazy list.
# It's done like so to avoid to have the whole file into memory
# Read more about Python generators to understand how it works.
# cf. `yield` keyword.
def gzip_to_chunks(filename):
    decompressor = zlib.decompressobj(zlib.MAX_WBITS + 16)
    with open(filename, 'rb') as f:
        chunk = f.read(CHUNKSIZE)

        while chunk:
            out = decompressor.decompress(chunk)
            yield out
            chunk = f.read(CHUNKSIZE)

        out = decompressor.flush()

        yield out


# Again the following is a generator (see the `yield` keyword).
# What id does is iterate over an *iterable* of strings and yields
# rows from the file

# (hint: `gzip_to_chunks(filename)` returns a generator of strings)
# (hint: a generator is also an iterable)

# You can verify that by calling `chunks_to_rows` with a list of
# strings, where every strings is a chunk of the VCF file.
# (hint: a list is also an iterable)

# inline doc follows
def chunks_to_rows(chunks):
    row = b''  # we will add the chars making a single row to this variable
    for chunk in chunks:  # iterate over the strings/chuncks yielded by gzip_to_chunks
        for char in chunk:  # iterate over all chars from the string
            if char == b'\n'[0]:  # hey! this is the end of the row!
                yield row.decode('utf8').split('\t')  # the row is complete, yield!
                row = b''  # start a new row
            else:
                row += int.to_bytes(char, 1, byteorder='big')  # Otherwise we are in the middle of the row
        # at this point the program has read all the chunk
    # at this point the program has read all the file without loading it fully in memory at once
    # That said, there's maybe still something in row
    if row:
        yield row.decode('utf-8').split('\t')  # yield the very last row if any


for e in chunks_to_rows(gzip_to_chunks('conceptnet-assertions-5.6.0.csv.gz')):
    uid, relation, start, end, metadata = e
    print(start, relation, end)
