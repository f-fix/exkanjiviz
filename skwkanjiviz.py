#!/usr/bin/env python3

"""
quick-and-dirty visualizer for font data from:
- Yamaha SKW-01 Kanji Word Processor Unit
"""


from PIL import Image, ImageDraw

import codecs
import gzip
import sys
import unicodedata


def shuffle_glyph(glyph):
    assert len(glyph) == 32
    return b"".join(
        [glyph[i : 1 + i] + glyph[16 + i : 17 + i] for i in range(8)]
        + [glyph[8 + i : 9 + i] + glyph[24 + i : 25 + i] for i in range(8)]
    )


def shuffle_kanji_cc(ch):
    # TODO: possibly add mappings from more recent SJIS to equivalent
    # MSX extensions to 78JIS?
    return ch


def shuffle_kanji(k):
    assert len(k) % 32 == 0
    return b"".join(
        shuffle_glyph(
            b"".join(bytes([k[32 * shuffle_kanji_cc(ch) + o]]) for o in range(32))
        )
        for ch in range(len(k) // 32)
    )

def expand_kanji(k, xk):
    """Expand kanji data and mask from 94x94 to 96x96"""
    k, xk = (
        32 * 96 * b"\0" + b"".join(32*b"\0" + k[i:32*94+i] + 32*b"\0" for i in range(0, len(k), 32*94)),
        32 * 96 * b"\xFF" + b"".join(32*b"\xFF" + xk[i:32*94+i] + 32*b"\xFF" for i in range(0, len(xk), 32*94)),
    )
    k, xk = (
        k[:12*96*32]+k[(48-4)*96*32:]+b"\0"*(96*32-len(k[(48-4)*96*32:]))+k[(16-4)*96*32:(48-4)*96*32],
        xk[:12*96*32]+xk[(48-4)*96*32:]+b"\xFF"*(96*32-len(k[(48-4)*96*32:]))+xk[(16-4)*96*32:(48-4)*96*32],
    )
    return (k, xk)


def skwkanjiviz(kanji_roms, skwkanji_png):
    """Given input files named by `kanji_roms` containing Yamaha SKW-01 KAnji Word Processor Unit Kanji font ROM data, produce a visualization and save it as a PNG in the output file named by `skwkanji_png`."""
    b = b"".join([open(kanji_rom, "rb").read() for kanji_rom in kanji_roms])
    b = shuffle_kanji(b)
    xb = b"\0" * len(b)
    b, xb = expand_kanji(b, xb)

    def cvtr(r):
        return 0 * 1 + r + 3 * (r >= 13)

    def rtok(byts):
        return (
            byts.decode("EUC-JP", "ignore")
            .encode("iso2022_jp_1", "ignore")
            .decode("iso2022_jp_1", "ignore")
            .encode("EUC-JP")
            == byts
        )

    def invc(cc):
        if cc // 96 == 2 and cc % 96 not in range(
            1, 14 + 1
        ):
            return True  # added in 83jis, not in 78jis
        if cc // 96 == 8:
            return True  # added in 83jis, not in 78jis
        if cc // 96 == 84 - 4 and cc % 96 in {5, 6}:
            return True  # added in 90jis, not in 78jis / 83jis
        return (
            not rtok(
                bytes(
                    [
                        min(cvtr(cc // 96), 95) + 0xA0,
                        cc % 96 + 0xA0,
                    ]
                )
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
    w3 = (0, 0, 255)
    k3 = (255, 255, 255)
    w4 = (0, 255, 255)

    im = Image.new(
        "RGBA",
        (
            max((z + 1) * z, 16) * 16,
            (
                ((96 + z - 1) // z - 1) * ((96 + z - 1) // z + 1)
                + max(16, (96 + z - 1) // z)
            )
            * 16
            + 8,
        ),
        g,
    )

    def kuten_ch(kuten):
        return (
            (kuten[0] - 0 * 1 - (3 if kuten[0] >= 16 else 0)) * 96
            + kuten[1]
        )

    def putkuten_at(dr, kuten, coords, color_pair):
        x, y = coords
        fg, bg = color_pair
        for i in range(256):
            dr.point(
                (x + i % 16, y + i // 16),
                (fg if b[kuten_ch(kuten) * 32 + (i // 8)] & (0x80 >> (i % 8)) else bg),
            )

    def putch_at(dr, ch, coords, color_pair, font, scale=1):
        x, y = coords
        fg, bg = color_pair
        byt = ord(ch.encode("SJIS"))
        for i in range(128):
            dr.point(
                (x + i % 8, y + i // 8),
                (
                    fg
                    if b[8 * 96 * 32 + 32 * (byt - 0x20 * (2 if (byt & 0x80) else 1)) + 2 * (i // 8)]
                    & (0x80 >> (i % 8))
                    else bg
                ),
            )

    def puts_at(dr, s, coords, color_pair, font=0, scale=1):
        x, y = coords
        if font != 2:
            s = unicodedata.normalize("NFD", s)
        for i in range(len(s)):
            ch = s[i : i + 1]
            if (
                ch.encode("SJIS", "ignore").decode("SJIS") == ch
                and len(ch.encode("SJIS")) == 2
                and ch.encode("EUC-JP", "ignore").decode("EUC-JP") == ch
                and len(ch.encode("EUC-JP")) == 2
            ):
                kuten = [byt - 0xA0 for byt in ch.encode("EUC-JP")]
                putkuten_at(
                    dr,
                    kuten,
                    (x + 8 * scale * i, y),
                    color_pair,
                )
                x += 8 * scale
                continue
            if ch == "\N{LEFTWARDS ARROW}":
                ch = "<"
            elif ch == "\N{DOWNWARDS ARROW}":
                ch = "v"
            elif ch == "\N{RIGHTWARDS ARROW}":
                ch = ">"
            elif ch == "\N{UPWARDS ARROW}":
                ch = "^"
            putch_at(
                dr,
                ch,
                (x + (6 if font == 1 else 8) * scale * i, y),
                color_pair,
                font,
                scale,
            )

    dr = ImageDraw.Draw(im)
    puts_at(
        dr,
        " SKW-01 Kanji ROM ",
        (16 * 16 + 8, 0),
        (v, h),
        font=2,
    )
    puts_at(
            dr,
            "  Halfwidth Roman and Katakana (ｶﾀｶﾅ) set (8x16)",
            (16 * 16 + 4, 52),
            (k3, w3),
            font=2,
        )
    puts_at(
            dr,
            "\N{DOWNWARDS ARROW} (row number)",
            ((16 + 1) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
            (w1, k),
        )
    puts_at(
            dr,
            "\N{DOWNWARDS ARROW} (unallocated in 78JIS)",
            ((32 + z + 4) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
            (w2, k),
        )
    puts_at(
            dr,
            "fullwidth character set (extended 78JIS)",
            (16 * 16 + 8, (16 - (96 + z - 1) // z - 2) * 16 - 4),
            (w, k),
        )
    for i in range(96):
        puts_at(
                dr,
                "%02d" % i,
                (16 * (i % z + 3 * (z + 1) - z // 2), 24 + 16 * (i // z)),
                ([w1, k][i % 2], [k, w1][i % 2]),
            )
        puts_at(
            dr,
            "\N{LEFTWARDS ARROW} (column number key)",
            (-12 + 16 * (4 * (z + 1) - z // 2), 24 + 12),
            (w1, k),
        )

    def chx(cc):
        return (
                cc % z
                + (z + 1) * (cvtr(cc // 96) % z)
        )

    def chy(cc):
        return (
            cc % 96 // z
            + (cvtr(cc // 96) // z - 1) * ((96 + z - 1) // z + 1)
            + 1
            + 16
        )

    for i in range(8 * 32 * 96, 8 * len(b)):
        if (i // (8 * 32) % 96) in {0, 95}:
            continue
        dr.point(
                (chx(i // 256) * 16 + i % 16, chy(i // 256) * 16 + (i // 16) % 16),
                (
                    [
                        [
                            k,
                            [k3, w][1 if i & 8 else 0],
                        ][False],
                        k1,
                        k2,
                        k1,
                    ]
                    if (b[i // 8] & (128 >> (i % 8)))
                    else [
                        [
                            w,
                            [w3, k][1 if i & 8 else 0],
                        ][False],
                        [w1, [w4, g][1 if i & 8 else 0]][False],
                        w2,
                        w1,
                    ]
                )[2 * invc(i // 256) + (xb[i // 8] != 0)],
            )
    for i in range(1, 96 - 3):
            if i * 96 * 32 >= len(b):
                continue
            puts_at(
                dr,
                f"{i + (3 if i >= 13 else 0):02d}",
                (
                    16 * chx(96 * i),
                    16 * chy(96 * i),
                ),
                (k, w1),
            )
            puts_at(
                dr,
                f"{i + (3 if i >= 13 else 0):02d}",
                (
                    16 * chx(96 * i + 95),
                    16 * chy(96 * i + 95),
                ),
                (k, w1),
            )
    puts_at(
            dr,
            "漢字、ひらがな、カタカナ、Ｒｏｍａｊｉ、ｶﾀｶﾅ､Romaji",
            (16 * 16 + 4, 88),
            (v, h),
            font=2,
        )
    puts_at(
            dr,
            "月火水木金土日年円時分秒百千万大中小",
            (16 * 16 + 4, 104),
            (v, h),
            font=2,
        )
    im.save(skwkanji_png)


def main():
    kanji_roms = []
    (  # usage: python skwkanjiviz.py FONT1.ROM OUTPUT
        _, skwkanji_rom, skwkanji_png
    ) = sys.argv
    kanji_roms = [skwkanji_rom]
    skwkanjiviz(kanji_roms, skwkanji_png)


if __name__ == "__main__":
    main()
