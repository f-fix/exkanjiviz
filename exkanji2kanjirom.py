#!/usr/bin/env python3

"""
quick-and-dirty PC-6001mkII and PC-6601 Kanji ROM construction using font data from:
- PC-6007SR Kakuchou Kanji ROM&RAM cartridge / 拡張漢字ＲＯＭ＆ＲＡＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-6601-01 Kakuchou Kanji ROM cartridge / 拡張漢字ＲＯＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-8801 series level 1 Kanji ROM `kanji1.rom`

Using this script you can make a working PC-6001mkII / PC-6601 Kanji ROM from your Kakuchou Kanji ROM or PC-8801 Level 1 Kanji ROM. The PC-6001mkII and PC-6601 Kanji ROM contains a 1/8 subset of the Level 1 Kanji from PC-6007SR/PC-6601-01/PC-8801. Maybe we should call it Level 0.125 Kanji?

The result has exactly the same contents as the PC-6001mkII `KANJIROM.62` or PC-6601 `KANJIROM.66`.

## Usage
1. prepare your ROM image (either a real one, or a synthesized one) in `saverkanji` EXKANJI.ROM format
2. run `python exkanji2kanjirom.py EXKANJI.ROM kanjirom.62` (or ...`.66`)
3. the created `kanjirom.62` (or ...`.66`) should work with PC-6001mkII and PC-6601 emulators

## ROM Data Extraction
If you need to get the data from your actual PC-6007SR or PC-6601-01 cartridge or synthesize it from other font data, see the [おまけ：拡張漢字ROM section of the PC-6001mkII/6601用互換BASIC website](http://000.la.coocan.jp/p6/basic66.html#:~:text=%E5%A4%89%E6%8F%9B%E3%81%97%E3%81%9F%E4%BE%8B-,%E3%81%8A%E3%81%BE%E3%81%91%EF%BC%9A%E6%8B%A1%E5%BC%B5%E6%BC%A2%E5%AD%97ROM,-%E3%82%A8%E3%83%9F%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%BF%E3%81%A7%E3%81%AE). That page also links to a utility program that can convert both directions between `ksaver` EXTKANJI.ROM format and `saverkanji` EXKANJI.ROM format. I saved mine from the cartridge using a PC-6001mkII with [ksaver](https://web.archive.org/web/20071223192215/http://www.kisweb.ne.jp/personal/windy/pc6001/p6soft.html#ksaver) in EXTKANJI.ROM format and then converted it to EXKANJI.ROM format using the converter.

The `kanji1.rom` from the PC-8801 series has identical contents to PC-6007SR's Kanji ROM in saverkanji EXKANJI.ROM format.

ROM fingerprint information for the version dumped from my cartridge:

- `128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [ksaver EXTKANJI format].rom crc32:7e53b7d8 md5:1268ac01f5b3c38ef2be22576e54a6b6 sha1:827aadd671347a05281a3863e20dd9f31bff5423 sha256:85f212271e79c5a727e81ec61a8cba6fdeff0123e07a1bfcec71b769d8d532dc size:131072`
- `128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [saverkanji EXKANJI format].rom crc32:6178bd43 md5:d81c6d5d7ad1a4bbbd6ae22a01257603 sha1:82e11a177af6a5091dd67f50a2f4bafda84d6556 sha256:7608040cffb1951e5cc567abb63f75b5746777a1ba96196c1b75606b793bb4bb size:131072`
"""

import codecs
import gzip
import sys

# The list of kuten codes used to extract the KANJIROM subset from
# EXKANJIROM is stored as a compressed list of skips.


def _decompress_kuten_data(compressed_kuten_data):
    ku_then_ten_data = gzip.decompress(codecs.decode(compressed_kuten_data, "base64"))
    ku_data, ten_data = (
        ku_then_ten_data[: len(ku_then_ten_data) // 2],
        ku_then_ten_data[len(ku_then_ten_data) // 2 :],
    )
    assert len(ku_data) == len(ten_data)
    kuten_data = []
    o = (0, None)
    for i in range(len(ku_data)):
        o = (
            (o[0] + ku_data[i], ten_data[i])
            if ku_data[i]
            else (o[0], o[1] + ten_data[i] + 1)
        )
        kuten_data.append(o)
    return kuten_data


JIS_TO_KANJIROM6X_KUTEN_DATA = _decompress_kuten_data(
    b"H4sIANj6o2gC/71T7W4bMQwTJVl2Lu1aoEDf/1FHytft17AgvS1BLoktix+i3+3PLzy19VAVvnX6"
    b"8SpchPL3Qth1UM8cwQVl+C/McY2cp8k+nRj8s2jgulE9VPF7r2q+uAUcgTCHm94RYA3SgA8LZ/ng"
    b"nhU37OYJrqW6zN0JrNWLZR5A8ie3o0J7bjxaLyCAddtpcV/8Dut/GGycJED8JLbp47spTwrgTn6v"
    b"3gBa17J+hbt4kyeGEZSdtWqF6taRMSe6cLNPbpl7nR64ZDV1IwkIFRvQtfzqUbbVSyb5UwvurSOE"
    b"J52EE6pTK5VQsCdtlIeJ1qCzlBXsJark42F9znHOYT9Hq469EhtSj7apraWpS2q0uMHNUpy3V+01"
    b"IukKmwW2l4d3y2xN8kpAA1ltOKdJos2XT5ftOZQC+dRd39joR5P1pua/wsN0+GgpJ/wX5VSuRkqu"
    b"vbmVGrf1qs8tB34eiPO7Sqhrb9DJOcjM1hccA6egnG7dNpGhoRDNg7Gzz917LaBzmaJcwVlJN1WN"
    b"lmk5G5vORRtt+c6OHUDXMofuSxzQE2sZZbe4H0xhn2M1G0Pxky+FQ+HAnl9lbiOKlyH2sJWz0sh1"
    b"bca5rwBFcI5MxqFq1tChicVOx9B1SJJaLXqAacSk0h771KjGCLnVN043pS8wV3v859UhxZk+FWKP"
    b"vq+5OPRCzJCwn5XY2LIACAAA"
)


# NEC stored the kanji ROM in a different order than JIS, but derived
# from it in a systematic way. These swizzler functions are used to
# remap to JIS order.
def swizp(p):
    return (p % 3) * 8 + (p // 3) % 8 + (p // 24) * 24


def swizs(s):
    return (s % 3) * 32 + (s // 3)


def swizr(r):
    return swizs(r) ^ 16


def swizk(k):
    return swizr(k - 23) + 23 if k >= 23 else k


def swizj(j):
    return swizk(swizp(j) if j < 24 else j)


def swizi(i):
    return (i & 0x1F) | (0x20 * swizj(i // 0x20))


def swiz(b):
    return b"".join([b[swizi(i) * 32 :][:32] for i in range(len(b) // 32)])


def exkanji2kanjirom(exkanji_rom, kanjirom6x):
    """Given an input file named by `exkanji_rom` containing Level 1 Kanji font ROM data in PC-8801 series `kanji1.rom` format a.k.a. PC-6007SR Kakuchou Kanji ROM & RAM Cartridge / PC-6601-01 Kakuchou Kakuchou ROM Cartridge `saverkanji` EXKANJI.ROM format, produce a visualization and save it as a PNG in the output file named by `kanjirom6x`."""
    b = open(exkanji_rom, "rb").read()

    b = bytes(
        b[(i & 1) * 128 * 32 + (i >> (2 if i & 1 else 1))] for i in range(256 * 32)
    ) + swiz(b[256 * 16 + 256 * 8 + 96 * 32 :])
    b = (
        b[: (256 + 32 * 21) * 32]
        + b"\x00" * (4 * 32 * 32)
        + b[(256 + 32 * 21) * 32 : (256 + 32 * 23) * 32]
        + b[(256 + 32 * 23) * 32 :]
    )
    xb = bytes(
        (
            (0x00)
            if ((i & 3) == 3) and (i < 256 * 32)
            else (
                0xFF
                if (i >= (256 + 32 * 21) * 32 and i < ((256 + 32 * 25) * 32))
                or ((i >= 256 * 32) and (((i - 256 * 32) // 32) % 96) in (0, 95))
                or (i >= (256 + 1 * 96 + 16) * 32 and i < (256 + 2 * 96) * 32)
                else 0x00
            )
        )
        for i in range(len(b))
    )

    def kuten_ch(kuten):
        return 256 + (kuten[0] - 1 - (6 if kuten[0] >= 16 else 0)) * 96 + kuten[1]

    bc = [b[i : i + 32] for i in range(0, len(b), 32)]
    kanjirom6x_data = b"".join(
        bc[kuten_ch(kuten)] for kuten in JIS_TO_KANJIROM6X_KUTEN_DATA
    )
    # store the left and right halves/bytes of the glyphs separately
    # (probably it corresponds to two separate ROM IC's)
    kanjirom6x_data = kanjirom6x_data[::2] + kanjirom6x_data[1::2]
    open(kanjirom6x, "wb").write(kanjirom6x_data)


def main():
    _, exkanji_rom, kanjirom6x = sys.argv
    exkanji2kanjirom(exkanji_rom, kanjirom6x)


if __name__ == "__main__":
    main()
