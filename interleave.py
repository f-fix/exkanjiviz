#!/usr/bin/env python3

"""
produce interleaved output from deinterleaved inputs

usage: python3 interleave.py [ -o OUTPUT; default /dev/fd/1 ] [ INPUT1 [INPUT2 ... INPUTn]; default /dev/fd/0 ]

if only a single file is specified (or when /dev/fd/0 is read by default), it is assumed to be two concatenated INPUTs
"""

import sys

def interleave(*, pages):
    """
    return the bytes of each page concatenated in an interleaved fashion
    """
    assert len(pages) > 1
    assert len({len(page) for page in pages}) == 1
    return bytes(pages[i%len(pages)][i//len(pages)] for i in range(len(pages) * len(pages[0])))

def smoketest():
    assert interleave(pages=(b'\0\2', b'\1\3')) == b'\0\1\2\3'
    assert interleave(pages=(b'\0\3', b'\1\4', b'\2\5')) == b'\0\1\2\3\4\5'

if __name__ == "__main__":
    _, *pagefiles = sys.argv
    outfile = "/dev/fd/1"
    if "-o" in pagefiles:
        wherearg = pagefiles.index('-o')
        outfile = pagefiles[1 + wherearg]
        pagefiles = pagefiles[:wherearg] + pagefiles[2 + wherearg:]
    pagefiles = pagefiles or ['/dev/fd/0']
    pages=[open(pagefile, "rb").read() for pagefile in pagefiles]
    if len(pages) == 1:
        assert len(pages[0]) % 2 == 0
        pages = [pages[0][:len(pages[0])//2], pages[0][len(pages[0])//2:]]
    open(outfile,"wb").write(interleave(pages=pages))

