#!/usr/bin/env python3

"""
quick-and-dirty visualizer for font data from:
- PC-6007SR Kakuchou Kanji ROM&RAM cartridge / 拡張漢字ＲＯＭ＆ＲＡＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-6601-01 Kakuchou Kanji ROM cartridge / 拡張漢字ＲＯＭカートリッジ in `saverkanji` EXKANJI.ROM format
- PC-8801 series level 1 Kanji ROM `kanji1.rom`

## Usage
1. prepare your ROM image (either a real one, or a synthesized one) in `saverkanji` EXKANJI.ROM format
2. run `python exkanjiviz.py EXKANJI.ROM exkanji.png`
3. the created `exkanji.png` will have a visualization of the ROM contents laid out according to JIS ordering, which is not quite the same as the storage order

## ROM Data Extraction
If you need to get the data from your actual PC-6007SR cartridge or synthesize it from other font data, see the [おまけ：拡張漢字ROM
 section of the PC-6001mkII/6601用互換BASIC website](http://000.la.coocan.jp/p6/basic66.html#:~:text=%E5%A4%89%E6%8F%9B%E3%81%97%E3%81%9F%E4%BE%8B-,%E3%81%8A%E3%81%BE%E3%81%91%EF%BC%9A%E6%8B%A1%E5%BC%B5%E6%BC%A2%E5%AD%97ROM,-%E3%82%A8%E3%83%9F%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%BF%E3%81%A7%E3%81%AE). That page also links to a utility program that can convert both directions between `ksaver` EXTKANJI.ROM format and `saverkanji` EXKANJI.ROM format. I saved mine from the cartridge using a PC-6001mkII with [ksaver](https://web.archive.org/web/20071223192215/http://www.kisweb.ne.jp/personal/windy/pc6001/p6soft.html#ksaver) in EXTKANJI.ROM format and then converted it to EXKANJI.ROM format using the converter.

The `kanji1.rom` from the PC-8801 series has identical contents to PC-6007SR's Kanji ROM in saverkanji EXKANJI.ROM format.

ROM fingerprint information for the version dumped from my cartridge:

- `128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [ksaver EXTKANJI format].rom crc32:7e53b7d8 md5:1268ac01f5b3c38ef2be22576e54a6b6 sha1:827aadd671347a05281a3863e20dd9f31bff5423 sha256:85f212271e79c5a727e81ec61a8cba6fdeff0123e07a1bfcec71b769d8d532dc size:131072`
- `128K PC-6007SR Kakuchou Kanji ROM & RAM Cartridge (NEC) (Japan) (PC-6001mkII) [saverkanji EXKANJI format].rom crc32:6178bd43 md5:d81c6d5d7ad1a4bbbd6ae22a01257603 sha1:82e11a177af6a5091dd67f50a2f4bafda84d6556 sha256:7608040cffb1951e5cc567abb63f75b5746777a1ba96196c1b75606b793bb4bb size:131072`
"""


from PIL import Image, ImageDraw

import sys


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


def exkanjiviz(exkanji_rom, exkanji_png):
    """Given an input file named by `exkanji_rom` containing Level 1 Kanji font ROM data in PC-8801 series `kanji1.rom` format a.k.a. PC-6007SR Kakuchou Kanji ROM & RAM Cartridge / PC-6601-01 Kakuchou Kakuchou ROM Cartridge `saverkanji` EXKANJI.ROM format, produce a visualization and save it as a PNG in the output file named by `exkanji_png`."""
    b = open(exkanji_rom, "rb").read()

    b = bytes(
        [b[(i & 1) * 128 * 32 + (i >> (2 if i & 1 else 1))] for i in range(256 * 32)]
    ) + swiz(b[256 * 16 + 256 * 8 + 96 * 32 :])
    b = (
        b[: (256 + 32 * 21) * 32]
        + b"\x00" * (4 * 32 * 32)
        + b[(256 + 32 * 21) * 32 : (256 + 32 * 23) * 32]
        + b[(256 + 32 * 23) * 32 :]
    )
    xb = bytes(
        [
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
        ]
    )

    def cvtr(r):
        return 1 + r + 6 * (r > 8)

    def rtok(byts):
        return (
            byts.decode("EUC-JP", "ignore")
            .encode("iso2022_jp_1", "ignore")
            .decode("iso2022_jp_1", "ignore")
            .encode("EUC-JP")
            == byts
        )

    def invc(cc):
        return (
            False
            if (cc < 256)
            else not rtok(
                bytes([min(cvtr((cc - 256) // 96), 95) + 0xA0, (cc - 256) % 96 + 0xA0])
            )
        )

    z = 16

    # color palette
    k = (0, 0, 0, 255)
    w = (255, 255, 255, 255)
    g = (127, 127, 127, 0)
    w1 = (255, 0, 255)
    k1 = (63, 0, 63)
    w2 = (255, 255, 0)
    k2 = (255, 0, 0)
    w3 = (0, 63, 0)
    k3 = (0, 255, 0)
    w4 = (0, 127, 0)

    im = Image.new(
        "RGBA",
        (
            max((z + 1) * z, 16) * 16,
            (
                ((96 + z - 1) // z - 1) * ((96 + z - 1) // z + 1)
                + max(16, (96 + z - 1) // z)
            )
            * 16,
        ),
        g,
    )

    def kuten_ch(kuten):
        return 256 + (kuten[0] - 1 - (6 if kuten[0] >= 16 else 0)) * 96 + kuten[1]

    def putkuten_at(dr, kuten, x, y, fg, bg):
        for i in range(256):
            dr.point(
                (x + i % 16, y + i // 16),
                (fg if b[kuten_ch(kuten) * 32 + (i // 8)] & (0x80 >> (i % 8)) else bg),
            )

    def putch_at(dr, ch, x, y, fg, bg):
        return (
            [
                dr.point(
                    (x + i % 8, y + i // 8),
                    (
                        fg
                        if b[ord(ch) * 32 + 2 * (i // 8) + (1 if ord(ch) < 0x20 else 0)]
                        & (0x80 >> (i % 8))
                        else bg
                    ),
                )
                for i in range(128)
            ]
            + [None]
        )[-1]

    def puts_at(dr, s, x, y, fg, bg):
        for i in range(len(s)):
            putch_at(dr, s[i : i + 1], x + 8 * i, y, fg, bg)

    dr = ImageDraw.Draw(im)
    puts_at(
        dr,
        " NEC PC-6007SR/PC-6601-01 Kakuchou Kanji ROM, PC-8801 Level 1 Kanji ROM ",
        16 * 16 + 8,
        4,
        w,
        k,
    )
    puts_at(dr, "\x1d halfwidth character sets (8x16 and 8x8)", 16 * 16 + 4, 24, k3, k)
    puts_at(
        dr,
        "\x1f (row number)",
        (16 + 1) * 16 + 8,
        (16 - (96 + z - 1) // z - 1) * 16 - 4,
        w1,
        k,
    )
    puts_at(
        dr,
        "\x1f (unallocated code area)",
        (32 + z + 4) * 16 + 8,
        (16 - (96 + z - 1) // z - 1) * 16 - 4,
        w2,
        k,
    )
    puts_at(
        dr,
        "\x1f (missing from old JIS)",
        (17 * 7 + 2 + z) * 16 + 8,
        (16 - (96 + z - 1) // z - 1) * 16 - 4,
        w1,
        k,
    )
    puts_at(
        dr,
        "fullwidth character set (old JIS with level 1 Kanji)",
        16 * 16 + 8,
        (16 - (96 + z - 1) // z - 2) * 16 - 4,
        w,
        k,
    )
    for i in range(1, 95):
        puts_at(
            dr,
            "%02d" % i,
            16 * (i % z + 3 * (z + 1) - z // 2),
            24 + 16 * (i // z),
            [w1, k][i % 2],
            [k, w1][i % 2],
        )
    puts_at(
        dr,
        "\x1d (column number key)",
        -12 + 16 * (4 * (z + 1) - z // 2),
        24 + 12,
        w1,
        k,
    )

    def chx(cc):
        return (
            cc % 16
            if (cc < 256)
            else ((cc - 256) % z + (z + 1) * (cvtr((cc - 256) // 96) % z))
        )

    def chy(cc):
        return (
            cc // 16
            if (cc < 256)
            else (cc - 256) % 96 // z
            + (cvtr((cc - 256) // 96) // z - 1) * ((96 + z - 1) // z + 1)
            + 1
            + 16
        )

    for i in range(8 * len(b)):
        if not xb[i // 8] or (i // 256 < 256) or (cvtr(((i // 256) - 256) // 96) <= 87):
            dr.point(
                (chx(i // 256) * 16 + i % 16, chy(i // 256) * 16 + (i // 16) % 16),
                (
                    [[k, k3][i // 256 < 256], k1, k2, k1]
                    if (b[i // 8] & (128 >> (i % 8)))
                    else [[w, w3][i // 256 < 256], [w1, w4][i // 256 < 256], w2, w1]
                )[2 * invc(i // 256) + (xb[i // 8] != 0)],
            )
    for i in range(1, 48 - 6):
        puts_at(
            dr,
            f"{i + (6 if i >= 10 else 0):02d}",
            16 * chx(256 + 96 * (i - 1)),
            16 * chy(256 + 96 * (i - 1)),
            k,
            w1,
        )
        puts_at(
            dr,
            f"{i + (6 if i >= 10 else 0):02d}",
            16 * chx(256 + 96 * (i - 1) + 95),
            16 * chy(256 + 96 * (i - 1) + 95),
            k,
            w1,
        )
    for i, ch in enumerate("拡張漢字ＲＯＭ＆ＲＡＭカートリッジ"):
        putkuten_at(
            dr, [byt - 0xA0 for byt in ch.encode("EUC-JP")], (20 + i) * 16 + 4, 64, w, k
        )
    for i, ch in enumerate("拡張漢字ＲＯＭカートリッジ"):
        putkuten_at(
            dr, [byt - 0xA0 for byt in ch.encode("EUC-JP")], (20 + i) * 16 + 4, 80, w, k
        )
    for i, ch in enumerate("ＰＣ−８８０１"):
        putkuten_at(
            dr, [byt - 0xA0 for byt in ch.encode("EUC-JP")], (20 + i) * 16 + 4, 96, w, k
        )
    im.save(exkanji_png)


def main():
    _, exkanji_rom, exkanji_png = sys.argv
    exkanjiviz(exkanji_rom, exkanji_png)


if __name__ == "__main__":
    main()
