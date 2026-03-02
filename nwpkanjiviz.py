#!/usr/bin/env python3

"""
quick-and-dirty visualizer for font data from:
- PC-6001 mkII/PC-6601 CGROM and Kanji subset ROM
- PC-6601 Nihongo Word Processor in DSK format

## Usage
1. prepare your Nihongo Word Proceassor DSK image (must be 163840 bytes)
2. run `python nwpkanjiviz.py CGROM60.62 CGROM60m.62 KANJIROM.62 NWPKANJI.DSK nwpkanji.png`
3. the created `nwpkanji.png` will have a visualization of the ROM and DSK kanji laid out according to JIS ordering, which is not quite the same as the storage order

"""


from PIL import Image, ImageDraw

import codecs
import gzip
import sys


# The list of kuten codes used to extract the KANJIROM subset from
# JIS Level 1 is stored as a compressed list of skips.


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


def interleave(*, pages):
    """
    return the bytes of each page concatenated in an interleaved fashion
    """
    assert len(pages) > 1
    assert len({len(page) for page in pages}) == 1
    return bytes(
        pages[i % len(pages)][i // len(pages)]
        for i in range(len(pages) * len(pages[0]))
    )


def nwpkanjiviz(cgrom60_62, cgrom60m_62, kanjirom_62, nwpkanji_dsk, nwpkanji_png):
    """Given an input file named by `nwpkanji_dsk` containing Level 1 Kanji font ROM data in PC-8801 series `kanji1.rom` format a.k.a. PC-6007SR Kakuchou Kanji ROM & RAM Cartridge / PC-6601-01 Kakuchou Kakuchou ROM Cartridge `saverkanji` NWPKANJI.ROM format, produce a visualization and save it as a PNG in the output file named by `nwpkanji_png`."""
    cgrom60_62_data = open(cgrom60_62, "rb").read()
    cgrom60m_62_data = open(cgrom60m_62, "rb").read()
    kanjirom_62_data = open(kanjirom_62, "rb").read()
    pages = [kanjirom_62_data]
    if len(pages) == 1:
        assert len(pages[0]) % 2 == 0
        pages = [pages[0][: len(pages[0]) // 2], pages[0][len(pages[0]) // 2 :]]
    kanjirom_62_data = interleave(pages=pages)
    nwpkanji_dsk_data = open(nwpkanji_dsk, "rb").read()
    assert len(nwpkanji_dsk_data) == 163840
    b = b""
    for cc in range(256):
        for scan in range(16):
            for charset in range(2):
                b += cgrom60m_62_data[
                    (256 * charset + cc) * 16
                    + scan : 1
                    + (256 * charset + cc) * 16
                    + scan
                ]
    b += b"\0" * (512 * 16 - len(b))
    b = b[: 256 * 32] + nwpkanji_dsk_data[5 * 16 * 256 :]
    # fill in encoding gaps with empty glyph data
    b = (
        b[: 256 * 32]
        + b[256 * 32 : (256 + 94 + 14) * 32]
        + b"\0" * (95 * 32)
        + b[(256 + 94 + 14) * 32 : (256 + 94 + 14 + 10) * 32]
        + b"\0" * (7 * 32)
        + b[(256 + 94 + 14 + 10) * 32 : (256 + 94 + 14 + 10 + 26) * 32]
        + b"\0" * (6 * 32)
        + b[(256 + 94 + 14 + 10 + 26) * 32 : (256 + 94 + 14 + 10 + 26 + 26) * 32]
        + b"\0" * (4 * 32)
        + b[
            (256 + 94 + 14 + 10 + 26 + 26)
            * 32 : (256 + 94 + 14 + 10 + 26 + 26 + 83)
            * 32
        ]
        + b"\0" * (11 * 32)
        + b[
            (256 + 94 + 14 + 10 + 26 + 26 + 83)
            * 32 : (256 + 94 + 14 + 10 + 26 + 26 + 83 + 86)
            * 32
        ]
        + b"\0" * (339 * 32)
        + b[(256 + 94 + 14 + 10 + 26 + 26 + 83 + 86) * 32 :]
    )
    # insert onboard kanji into extended kanji from the disk
    onboard_ch = 0
    ext_ch = 0
    composite_kanji = b""
    for ku in range(1, 48):
        if ku in range(10, 15 + 1):
            continue
        for ten in range(1, 94 + 1):
            if ku == 47 and ten >= 55:
                continue
            kuten = (ku, ten)
            if kuten in JIS_TO_KANJIROM6X_KUTEN_DATA:
                composite_kanji += kanjirom_62_data[
                    onboard_ch * 32 : (onboard_ch + 1) * 32
                ]
                onboard_ch += 1
            else:
                composite_kanji += b[(256 + ext_ch) * 32 : (256 + ext_ch + 1) * 32]
                ext_ch += 1
    b = b[: 256 * 32] + composite_kanji + b"\0" * ((93 - 55) * 32)
    # expand from 94x94 to 96x96 ku/ten layout
    b = b[: 256 * 32] + b"".join(
        [
            b"\0" * 32 + b[page : page + 94 * 32] + b"\0" * 32
            for page in range(256 * 32, len(b) + (94 - 1) * 32, 94 * 32)
        ]
    )
    xb = bytes(
        (
            (0x00)
            if ((i & 15) >= 12) and (i < 256 * 32)
            else (
                0xFF
                if (i >= (256 + 32 * 15) * 32 and i < ((256 + 32 * 25) * 32))
                or ((i >= 256 * 32) and (((i - 256 * 32) // 32) % 96) in (0, 95))
                or (i >= (256 + 1 * 96 + 16) * 32 and i < (256 + 2 * 96) * 32)
                else 0x00
            )
        )
        for i in range(len(b))
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
    h = (0, 0, 127, 255)
    v = (255, 255, 204, 255)
    w1 = (255, 0, 255)
    k1 = (63, 0, 63)
    w2 = (255, 255, 0)
    k2 = (255, 0, 0)
    w3 = (0, 63, 0)
    k3 = (0, 255, 0)
    w4 = (0, 127, 0)
    w5 = (63, 31, 0)
    k5 = (255, 127, 0)

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

    def putkuten_at(dr, kuten, coords, color_pair):
        x, y = coords
        fg, bg = color_pair
        for i in range(256):
            dr.point(
                (x + i % 16, y + i // 16),
                (fg if b[kuten_ch(kuten) * 32 + (i // 8)] & (0x80 >> (i % 8)) else bg),
            )

    def putch_at(dr, ch, coords, color_pair):
        x, y = coords
        fg, bg = color_pair
        font = 0
        if ch == "←":
            font = 1
            ch = ")"
        elif ch == "↓":
            font = 1
            ch = "+"
        for i in range(8 * 12):
            dr.point(
                (x + i % 8, y + i // 8),
                (
                    fg
                    if b[ord(ch) * 32 + 2 * (i // 8) + font] & (0x80 >> (i % 8))
                    else bg
                ),
            )

    def puts_at(dr, s, coords, color_pair):
        x, y = coords
        for i in range(len(s)):
            putch_at(dr, s[i : i + 1], (x + 8 * i, y), color_pair)

    dr = ImageDraw.Draw(im)
    puts_at(
        dr,
        " NEC PC-6601 Nihongo Word Processor",
        (16 * 16 + 8, 4),
        (w, k),
    )
    puts_at(
        dr,
        " NEC PC-6001mkII/PC-6601 Kanji ROM (subset) ",
        (16 * 16 + 8, 20),
        (v, h),
    )
    puts_at(
        dr,
        "← PC-6001mkII/PC-6601 8-bit character set (8x12)",
        (16 * 16 + 4, 40),
        (k3, k),
    )
    puts_at(
        dr,
        "← PC-6001mkII/PC-6601 8-bit graphics set (8x12)",
        (16 * 16 + 4, 60),
        (k5, k),
    )
    puts_at(
        dr,
        "↓ (row number)",
        ((16 + 1) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
        (w1, k),
    )
    puts_at(
        dr,
        "↓ (unallocated code area)",
        ((32 + z + 4) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
        (w2, k),
    )
    puts_at(
        dr,
        "↓ (missing from Nihongo Word Processor)",
        ((17 * 5 + 2 + z) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
        (w1, k),
    )
    puts_at(
        dr,
        "↓ (missing from old JIS)",
        ((17 * 7 + 2 + z) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
        (w1, k),
    )
    puts_at(
        dr,
        "fullwidth character set (old JIS with level 1 Kanji)",
        (16 * 16 + 8, (16 - (96 + z - 1) // z - 2) * 16 - 4),
        (w, k),
    )
    for i in range(1, 95):
        puts_at(
            dr,
            "%02d" % i,
            (16 * (i % z + 3 * (z + 1) - z // 2), 24 + 16 * (i // z)),
            ([w1, k][i % 2], [k, w1][i % 2]),
        )
    puts_at(
        dr,
        "← (column number key)",
        (-12 + 16 * (4 * (z + 1) - z // 2), 24 + 12),
        (w1, k),
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

    kanjirom_subset_chs = {kuten_ch(kuten) for kuten in JIS_TO_KANJIROM6X_KUTEN_DATA}

    for i in range(8 * len(b)):
        if (i // 8 // 32) < 256 and (i // 8) % 32 >= 2 * 12:
            continue
        if not xb[i // 8] or (i // 256 < 256) or (cvtr(((i // 256) - 256) // 96) <= 87):
            dr.point(
                (chx(i // 256) * 16 + i % 16, chy(i // 256) * 16 + (i // 16) % 16),
                (
                    [
                        [[k, h][i // 256 in kanjirom_subset_chs], [k3, k5][i // 8 % 2]][
                            i // 256 < 256
                        ],
                        k1,
                        k2,
                        k1,
                    ]
                    if (b[i // 8] & (128 >> (i % 8)))
                    else [
                        [[w, v][i // 256 in kanjirom_subset_chs], [w3, w5][i // 8 % 2]][
                            i // 256 < 256
                        ],
                        [w1, w4][i // 256 < 256],
                        w2,
                        w1,
                    ]
                )[2 * invc(i // 256) + (xb[i // 8] != 0)],
            )
    for i in range(1, 48 - 6):
        puts_at(
            dr,
            f"{i + (6 if i >= 10 else 0):02d}",
            (16 * chx(256 + 96 * (i - 1)), 16 * chy(256 + 96 * (i - 1))),
            (k, w1),
        )
        puts_at(
            dr,
            f"{i + (6 if i >= 10 else 0):02d}",
            (16 * chx(256 + 96 * (i - 1) + 95), 16 * chy(256 + 96 * (i - 1) + 95)),
            (k, w1),
        )
    for i, ch in enumerate("ＰＣ−６６０１日本語ワードプロセッサ"):
        putkuten_at(
            dr,
            [byt - 0xA0 for byt in ch.encode("EUC-JP")],
            ((18 + i) * 16 + 4, 76),
            (w, k),
        )
    for i, ch in enumerate("ＰＣ−６００１ｍｋＩＩとＰＣ−６６０１漢字ＲＯＭ"):
        putkuten_at(
            dr,
            [byt - 0xA0 for byt in ch.encode("EUC-JP")],
            ((18 + i) * 16 + 4, 104),
            (v, h),
        )
    im.save(nwpkanji_png)


def main():
    _, cgrom60_62, cgrom60m_62, kanjirom_62, nwpkanji_dsk, nwpkanji_png = sys.argv
    nwpkanjiviz(cgrom60_62, cgrom60m_62, kanjirom_62, nwpkanji_dsk, nwpkanji_png)


if __name__ == "__main__":
    main()
