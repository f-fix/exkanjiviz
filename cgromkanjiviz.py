#!/usr/bin/env python3

"""
quick-and-dirty visualizer for font data from:
- PC-6001 `CGROM.60` or `CGROM.61` + M5C6847P-1 internal font data
- PC-6001mkII `CGROM60.62`, `CGROM60m.62`, and `KANJIROM.62`
- PC-6601 `CGROM60.66`, `CGROM66.66`, and `KANJIROM.66`

It should work with data from SR models too, just adjust the filenames.

## Usage
1. prepare your ROM images (either real ones, or synthesized ones) with the kanji ROM (if any) deinterleaved
2. run it:
     - PC-6001: `python cgromkanjiviz.py CGROM.60 cgrom.png` (or `CGROM.61`)
     - PC-6001mkII: `python cgromkanjiviz.py CGROM60.62 CGROM60m.62 KANJIROM.62 cgromkanji.png`
         or: `python cgromkanjiviz.py CGROM60.62 CGROM60m.62 KANJIROM1.62 KANJIROM2.62 cgromkanji.png`
     - PC-6601: `python cgromkanjiviz.py CGROM60.66 CGROM66.66 KANJIROM.66 cgromkanji.png`
         or: `python cgromkanjiviz.py CGROM60.66 CGROM66.66 KANJIROM1.66 KANJIROM2.66 cgromkanji.png`
     - SR models: adjust the filenames
3. the created `cgrom.png` or `cgromkanji.png` will have a visualization of the ROM contents with CGROM laid out in grids and the PC-6001mkII/PC-6601 Kanji ROM subset laid out according to JIS ordering, which is not the same as the storage order

## ROM Data Extraction
If you need to get the built-in kanji ROM subset (KANJIROM) and/or single-byte character generator ROM (CGROM) from your actual PC-6001mkII or PC-6601, or want to construct an equivalent image for emulation or other purposes, see the [CGROM/KANJIROMファイルについて section of the PC-6001mkII/6601用互換BASIC website](https://000.la.coocan.jp/p6/basic66.html#cgrom). I used isio's [saver](http://retropc.net/isio/mysoft/#saver) to do this for my PC-6001mkII.

You can also use exkanji2kanjirom.py for quick-and-dirty PC-6001mkII and PC-6601 Kanji ROM construction using font data from:
- PC-6007SR Kakuchou Kanji ROM&RAM cartridge / 拡張漢字ＲＯＭ＆ＲＡＭカートリッジ in `saverkanji` `EXKANJI.ROM` format
- PC-6601-01 Kakuchou Kanji ROM cartridge / 拡張漢字ＲＯＭカートリッジ in `saverkanji` `EXKANJI.ROM` format
- PC-8801 series level 1 Kanji ROM `kanji1.rom`

If you need to get the data from your actual PC-6007SR cartridge or synthesize it from other font data, see the [おまけ：拡張漢字ROM
 section of the PC-6001mkII/6601用互換BASIC website](http://000.la.coocan.jp/p6/basic66.html#:~:text=%E5%A4%89%E6%8F%9B%E3%81%97%E3%81%9F%E4%BE%8B-,%E3%81%8A%E3%81%BE%E3%81%91%EF%BC%9A%E6%8B%A1%E5%BC%B5%E6%BC%A2%E5%AD%97ROM,-%E3%82%A8%E3%83%9F%E3%83%A5%E3%83%AC%E3%83%BC%E3%82%BF%E3%81%A7%E3%81%AE). That page also links to a utility program that can convert both directions between `ksaver` EXTKANJI.ROM format and `saverkanji` EXKANJI.ROM format. I saved mine from the cartridge using a PC-6001mkII with [ksaver](https://web.archive.org/web/20071223192215/http://www.kisweb.ne.jp/personal/windy/pc6001/p6soft.html#ksaver) in EXTKANJI.ROM format and then converted it to EXKANJI.ROM format using the converter.

The `kanji1.rom` from the PC-8801 series has identical contents to PC-6007SR's Kanji ROM in saverkanji EXKANJI.ROM format.
"""


from PIL import Image, ImageDraw

import codecs
import gzip
import sys
import unicodedata


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

# M5C6847P-1 inherent character data
# CG6: 2x3 mosaic tiles
# CG4: 2x2 mosaic tiles
# FONT: 64-character ASCII subset + inverted version

def _decompress_vdg_font(compressed_vdg_font):
    vdg_font = gzip.decompress(codecs.decode(compressed_vdg_font, "base64"))
    assert len(vdg_font) == 64 * 12
    vdg_font = vdg_font + bytes([ i ^ 0xFF for i in vdg_font ])
    vdg_font = b"".join(
        vdg_font[12*j:12*(j+1)] + (16 - 12) * b"\0"
        for j in range(64 * 2)
    )
    return vdg_font

VDG_FONT = _decompress_vdg_font(
    b"H4sIAMDNaWkAA1VSwarEIAwU8eBhWaR4kEVKCKUUT2UPZQ/i/3/Wi4mxfbl0Ok0mk6TGmIz2U0o2"
    b"PXxEbIiM67LkZamMMwIAZuUX5RtABWgPDIxXgB1xZYwsKZrZ9xAdS4FDE7fjPDbJAQ7RxKsUrcVv"
    b"2RV3QZIVP4izbya2bJ/Jq2bG4N3o1diDV284PSDGePOlXKMvxr6WibW2WefD8Pljz7/hn3pZy/jd"
    b"h7Rv2W0us9b40MKAzxBn8iHGOPkYL3ONd79CtlVyvl/ysO+Mw3EEnT2ldGsG6JYEkzGyPT4UcjQb"
    b"N3/7Oc8Aits/g+fJD8uzS07aekg/n+770n+V9Y6EX3bs2b1ic86JOFSrPCVXvUV76NNNs/IEVmsF"
    b"05BGx2Tog+hTJV1g2tcB+lXcyEmbkz3/AQ+PgKEAAwAA"
)

SG6_PATTERNS = b"".join([bytes([
    (0xF0 if (j & 0b100000) else 0x00) | (0x0F if (j & 0b010000) else 0x00),
    (0xF0 if (j & 0b100000) else 0x00) | (0x0F if (j & 0b010000) else 0x00),
    (0xF0 if (j & 0b100000) else 0x00) | (0x0F if (j & 0b010000) else 0x00),
    (0xF0 if (j & 0b100000) else 0x00) | (0x0F if (j & 0b010000) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
]) + (16 - 12) * b"\0" for j in range(64)])

SG4_PATTERNS = b"".join([bytes([
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b001000) else 0x00) | (0x0F if (j & 0b000100) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
    (0xF0 if (j & 0b000010) else 0x00) | (0x0F if (j & 0b000001) else 0x00),
]) + (16 - 12) * b"\0" for j in range(16)])

# 8-bit/single-byte character encoding schemes

NO_CONTROLS = b""
MINIMAL_CONTROLS = b"\0\r\n\x1a\x7f"
ASCII_CONTROLS = bytes(range(0x20)) + b"\x7f"

# i am sure this is not the best way to solve this. this mapping
# should work OK for PC-6001/mkII/SR and PC-6601/SR. it does not
# handle the alternate character set shift sequences well. it also
# does not handle fullwidth Kanji (neither the subset built in to
# mkII/SR and 6601/SR, nor the larger set present in the extended
# Kanji ROM/RAM cartridge), additional single-byte graphics charsets
# from PC-6001 mkII/SR and PC-6601/SR, semi-graphics charset, or
# PC-6001A charset at all! the mapping is intentionally close to the
# PC-98 one above. the hiragana and kanji here should all be
# half-width ones, but Unicode is missing those so we live with
# fullwidth instead. the arrows and control pictures shown here in the
# first row are actually control characters and are not graphically
# displayable on a PC-6001. the font data inside the PC-6001's
# M5C6847P-1 is not normally used by PC-6001 software, but does
# contain arrow graphics. likewise the extended graphics character set
# in the PC-6001 mkII/SR and PC-6601/SR CGROM is rearely used by
# software, but it also contains arrow graphics. those infrequently
# used character sets are not handled here, though.
PC6001_8BIT_CHARSET = (
    "␀␁␂␃␄␅␆␇␈␉␊␋␌␍␎␏␐␑␒␓␔␕␖␗␘␙␚␛￫￩￪￬"
    " !\"#$%&'()*+,-./0123456789:;<=>?"
    "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[¥]^_"
    "`abcdefghijklmnopqrstuvwxyz{¦}~␡"
    "♠♥♦♣￮•をぁぃぅぇぉゃゅょっ\uf8f4あいうえおかきくけこさしすせそ"
    "\uf8f0｡｢｣､･ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ"
    "ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝﾞﾟ"
    "たちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわん\uf8f2\uf8f3"
)
assert len(PC6001_8BIT_CHARSET) == 256
PC6001_8BIT_ALTCHARSET = "\uf8f1月火水木金土日年円時分秒百千万" "π┴┬┤├┼│─┌┐└┘╳大中小"
assert len(PC6001_8BIT_ALTCHARSET) == 32
PC6001_8BIT_CHARMAP = {PC6001_8BIT_CHARSET[i]: bytes([i]) for i in range(256)} | {
    PC6001_8BIT_ALTCHARSET[i]: bytes([0x14, i + 0x30]) for i in range(32)
}
PC6001_8BIT_CHARMAP_COMPAT = {
    unicodedata.normalize("NFKD", key): value
    for key, value in PC6001_8BIT_CHARMAP.items()
    if unicodedata.normalize("NFKD", key) != key
} | {
    "\N{KATAKANA-HIRAGANA VOICED SOUND MARK}": PC6001_8BIT_CHARMAP[
        "\N{HALFWIDTH KATAKANA VOICED SOUND MARK}"
    ],
    "\N{KATAKANA-HIRAGANA SEMI-VOICED SOUND MARK}": PC6001_8BIT_CHARMAP[
        "\N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}"
    ],
    "\N{KATAKANA-HIRAGANA PROLONGED SOUND MARK}": PC6001_8BIT_CHARMAP[
        "\N{HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK}"
    ],
}


def encode_pc6001_8bit_charset(s, try_harder=True):
    s = "".join(
        [
            (
                unicodedata.normalize("NFKD", s[i : i + 1])
                if (
                    unicodedata.name(s[i : i + 1], "?")
                    .lower()
                    .startswith("hiragana letter")
                    or unicodedata.name(s[i : i + 1], "?")
                    .lower()
                    .startswith("katakana letter")
                )
                else (
                    "~"
                    if s[i : i + 1] == "\N{WAVE DASH}"
                    else "-" if s[i : i + 1] == "\N{HYPHEN}" else s[i : i + 1]
                )
            )
            for i in range(len(s))
        ]
    )
    byts, chars_consumed, num_chars = b"", 0, len(s)
    while chars_consumed < num_chars:
        ch = s[chars_consumed]
        byt = PC6001_8BIT_CHARMAP.get(ch, PC6001_8BIT_CHARMAP_COMPAT.get(ch)) or (
            bytes([ord(ch)]) if ord(ch) <= 0x7F else None
        )
        if byt is None and try_harder:
            cch = unicodedata.normalize("NFKD", ch)
            byt = PC6001_8BIT_CHARMAP.get(cch, PC6001_8BIT_CHARMAP_COMPAT.get(cch)) or (
                bytes([ord(cch)]) if len(cch) == 1 and ord(cch) <= 0x7F else None
            )
        if byt is None and try_harder:
            cch = unicodedata.normalize("NFC", ch)
            byt = PC6001_8BIT_CHARMAP.get(cch, PC6001_8BIT_CHARMAP_COMPAT.get(cch)) or (
                bytes([ord(cch)]) if len(cch) == 1 and ord(cch) <= 0x7F else None
            )
        if byt is None:
            raise UnicodeEncodeError(
                "pc6001-8bit",
                s,
                chars_consumed,
                chars_consumed + 1,
                f"no mapping for U+{ord(ch):04X} {unicodedata.name(ch, repr(ch))}",
            )
        byts += byt
        chars_consumed += 1
    return byts


def decode_pc6001_8bit_charset(byts, preserve=MINIMAL_CONTROLS):
    s, bytes_consumed, num_bytes = "", 0, len(byts)
    while bytes_consumed < num_bytes:
        byt = byts[bytes_consumed]
        if (
            bytes_consumed > 0
            and byts[bytes_consumed - 1] == 0x14
            and byt >= 0x30
            and byt <= 0x4F
        ):
            s = (
                s[: -len(PC6001_8BIT_CHARSET[0x14])]
                + PC6001_8BIT_ALTCHARSET[byt - 0x30]
            )
        elif byt in preserve:
            s += chr(byt)
        else:
            s += PC6001_8BIT_CHARSET[byt]
        if (
            len(s) > 1
            and s[-1:]
            in "\N{HALFWIDTH KATAKANA VOICED SOUND MARK}\N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}"
            and unicodedata.name(s[-2:-1], "?").lower().startswith("hiragana letter")
        ):
            s = s[:-2] + unicodedata.normalize("NFKC", s[-2:])
        bytes_consumed += 1
    round_trip_byts = encode_pc6001_8bit_charset(s)
    assert byts == round_trip_byts, UnicodeDecodeError(
        "pc6001-8bit",
        byts,
        0,
        num_bytes,
        f"round-trip failure for {repr(s)} with preserve={repr(preserve)}; result:\n {repr(byts)}, got:\n {repr(round_trip_byts)}",
    )
    return s


def smoke_test_pc6001_8bit_charset():
    assert decode_pc6001_8bit_charset(b"") == ""
    assert encode_pc6001_8bit_charset("") == b""
    assert decode_pc6001_8bit_charset(b"\x00") == "\x00"
    assert encode_pc6001_8bit_charset("\x00") == b"\x00"
    assert encode_pc6001_8bit_charset("␀") == b"\x00"
    assert encode_pc6001_8bit_charset("\uf8f1") == b"\x14\x30"
    assert encode_pc6001_8bit_charset("小") == b"\x14\x4f"
    assert encode_pc6001_8bit_charset("␔") == b"\x14"
    assert encode_pc6001_8bit_charset("\x14") == b"\x14"
    assert encode_pc6001_8bit_charset("\x14\x4f") == b"\x14\x4f"
    round_trip_test_failures = {
        encode_pc6001_8bit_charset(decode_pc6001_8bit_charset(bytes([i]))): bytes([i])
        for i in range(256)
        if encode_pc6001_8bit_charset(decode_pc6001_8bit_charset(bytes([i])))
        != bytes([i])
    }
    round_trip_test_failures.update(
        {
            encode_pc6001_8bit_charset(
                decode_pc6001_8bit_charset(bytes([0x14, i]))
            ): bytes([0x14, i])
            for i in range(256)
            if encode_pc6001_8bit_charset(decode_pc6001_8bit_charset(bytes([0x14, i])))
            != bytes([0x14, i])
        }
    )
    round_trip_test_failures.update(
        {
            encode_pc6001_8bit_charset(
                decode_pc6001_8bit_charset(bytes([i, 0xEE]))
            ): bytes([i, 0xEE])
            for i in range(256)
            if encode_pc6001_8bit_charset(decode_pc6001_8bit_charset(bytes([i, 0xEE])))
            != bytes([i, 0xEE])
        }
    )
    round_trip_test_failures.update(
        {
            encode_pc6001_8bit_charset(
                decode_pc6001_8bit_charset(bytes([i, 0xEF]))
            ): bytes([i, 0xEF])
            for i in range(256)
            if encode_pc6001_8bit_charset(decode_pc6001_8bit_charset(bytes([i, 0xEF])))
            != bytes([i, 0xEF])
        }
    )
    assert not round_trip_test_failures, round_trip_test_failures
    unicode_test = (
        "\r\n".join(
            (
                "\\￮╳•╳o/ I ♥ PC6001!",
                "パピコンが大すきです!",
                "「パピコン」は にっぽんでんき が せいぞうした8ビットコンピュータで、やすいことから いちじき にんき を はくしました。",
                "「！？」　･･･",
                "│|¦~-ｰ─_",
                "¥0=0円",
                "2025年07月18日 14時11分16秒",
                "┌┬─┐ ┌￪┐ ++-+  ^/",
                "├┼─┤ ￩┼￫ ++-+ <X>",
                "││•│･└￬┘ ¦|.¦ /v ",
                "└┴─┘<>O[]++-+ π>3",
                "␀␁␂␃␄␅␆␇␈␉␊␋␌␍␎␏␐␑␒␓␔␕␖␗␘␙␚␛￫￩￪￬␡",
            )
        )
        + "\x1a\x00"
    )
    expected_8bit = (
        b"\r\n".join(
            (
                b"\\\x84\x14L\x85\x14Lo/ I \x81 PC6001!",
                b"\xca\xdf\xcb\xdf\xba\xdd\x96\xde\x14M\x9d\x97\xe3\xde\x9d!",
                b"\xa2\xca\xdf\xcb\xdf\xba\xdd\xa3\xea \xe6\x8f\xee\xdf\xfd\xe3\xde\xfd\x97 \x96\xde \x9e\x92\x9f\xde\x93\x9c\xe08\xcb\xde\xaf\xc4\xba\xdd\xcb\xdf\xad\xb0\xc0\xe3\xde\xa4\xf4\x9d\x92\x9a\xe4\x96\xf7 \x92\xe1\x9c\xde\x97 \xe6\xfd\x97 \x86 \xea\x98\x9c\xef\x9c\xe0\xa1",
                b"\xa2!?\xa3 \xa5\xa5\xa5",
                b"\x14F||~-\xb0\x14G_",
                b"\\0=0\x149",
                b"2025\x14807\x14118\x147 14\x14:11\x14;16\x14<",
                b"\x14H\x14B\x14G\x14I \x14H\x1e\x14I ++-+  ^/",
                b"\x14D\x14E\x14G\x14C \x1d\x14E\x1c ++-+ <X>",
                b"\x14F\x14F\x85\x14F\xa5\x14J\x1f\x14K ||.| /v ",
                b"\x14J\x14A\x14G\x14K<>O[]++-+ \x14@>3",
                bytes([i for i in range(0x20)] + [0x7F]),
            )
        )
        + b"\x1a\x00"
    )
    assert (
        encode_pc6001_8bit_charset(unicode_test) == expected_8bit
    ), f"encode_pc6001_8bit_charset({repr(unicode_test)}) returned:\n {repr(encode_pc6001_8bit_charset(unicode_test))}, expecting:\n {repr(expected_8bit)}"
    pc6001_8bit_test = expected_8bit
    try:
        unexpected_8bit = encode_pc6001_8bit_charset(unicode_test, try_harder=False)
        assert (
            False
        ), f"Expected a UnicodeEncodeError for encode_pc6001_8bit_charset({repr(unicode_test)}, try_harder=False) but no error was raised"
    except UnicodeEncodeError:
        pass
    except Exception as e:
        assert (
            False
        ), f"Expected a UnicodeEncodeError for encode_pc6001_8bit_charset({repr(unicode_test)}, try_harder=False) but {repr(e)} was raised instead"
    expected_unicode = (
        "\r\n".join(
            (
                "¥￮╳•╳o/ I ♥ PC6001!",
                "ﾊﾟﾋﾟｺﾝが大すきです!",
                "｢ﾊﾟﾋﾟｺﾝ｣は にっぽんでんき が せいぞうした8ﾋﾞｯﾄｺﾝﾋﾟｭｰﾀで､やすいことから いちじき にんき を はくしました｡",
                "｢!?｣ ･･･",
                "│¦¦~-ｰ─_",
                "¥0=0円",
                "2025年07月18日 14時11分16秒",
                "┌┬─┐ ┌￪┐ ++-+  ^/",
                "├┼─┤ ￩┼￫ ++-+ <X>",
                "││•│･└￬┘ ¦¦.¦ /v ",
                "└┴─┘<>O[]++-+ π>3",
                "\x00␁␂␃␄␅␆␇␈␉\n␋␌\r␎␏␐␑␒␓␔␕␖␗␘␙\x1a␛￫￩￪￬\x7f",
            )
        )
        + "\x1a\x00"
    )
    assert (
        decode_pc6001_8bit_charset(pc6001_8bit_test) == expected_unicode
    ), f"decode_pc6001_8bit_charset({repr(pc6001_8bit_test)}) returned:\n {repr(decode_pc6001_8bit_charset(pc6001_8bit_test))}, expecting:\n {repr(expected_unicode)}"
    assert (
        encode_pc6001_8bit_charset(expected_unicode, try_harder=False)
        == pc6001_8bit_test
    ), f"encode_pc6001_8bit_charset({repr(expected_unicode)}, try_harder=False) returned:\n {repr(encode_pc6001_8bit_charset(expected_unicode, try_harder=False))}, expecting:\n {repr(pc6001_8bit_test)}"
    expected_no_controls_unicode = (
        "␍␊".join(
            (
                "¥￮╳•╳o/ I ♥ PC6001!",
                "ﾊﾟﾋﾟｺﾝが大すきです!",
                "｢ﾊﾟﾋﾟｺﾝ｣は にっぽんでんき が せいぞうした8ﾋﾞｯﾄｺﾝﾋﾟｭｰﾀで､やすいことから いちじき にんき を はくしました｡",
                "｢!?｣ ･･･",
                "│¦¦~-ｰ─_",
                "¥0=0円",
                "2025年07月18日 14時11分16秒",
                "┌┬─┐ ┌￪┐ ++-+  ^/",
                "├┼─┤ ￩┼￫ ++-+ <X>",
                "││•│･└￬┘ ¦¦.¦ /v ",
                "└┴─┘<>O[]++-+ π>3",
                "␀␁␂␃␄␅␆␇␈␉␊␋␌␍␎␏␐␑␒␓␔␕␖␗␘␙␚␛￫￩￪￬␡",
            )
        )
        + "␚␀"
    )
    assert (
        decode_pc6001_8bit_charset(pc6001_8bit_test, preserve=NO_CONTROLS)
        == expected_no_controls_unicode
    ), f"decode_pc6001_8bit_charset({repr(pc6001_8bit_test)}, preserve=NO_CONTROLS) returned:\n {repr(decode_pc6001_8bit_charset(pc6001_8bit_test, preserve=NO_CONTROLS))}, expecting:\n {repr(expected_no_controls_unicode)}"
    expected_ascii_controls_unicode = (
        "\r\n".join(
            (
                "¥￮╳•╳o/ I ♥ PC6001!",
                "ﾊﾟﾋﾟｺﾝが大すきです!",
                "｢ﾊﾟﾋﾟｺﾝ｣は にっぽんでんき が せいぞうした8ﾋﾞｯﾄｺﾝﾋﾟｭｰﾀで､やすいことから いちじき にんき を はくしました｡",
                "｢!?｣ ･･･",
                "│¦¦~-ｰ─_",
                "¥0=0円",
                "2025年07月18日 14時11分16秒",
                "┌┬─┐ ┌\x1e┐ ++-+  ^/",
                "├┼─┤ \x1d┼\x1c ++-+ <X>",
                "││•│･└\x1f┘ ¦¦.¦ /v ",
                "└┴─┘<>O[]++-+ π>3",
                "".join([chr(i) for i in range(0x20)]) + "\x7f",
            )
        )
        + "\x1a\x00"
    )
    assert (
        decode_pc6001_8bit_charset(pc6001_8bit_test, preserve=ASCII_CONTROLS)
        == expected_ascii_controls_unicode
    ), f"decode_pc6001_8bit_charset({repr(pc6001_8bit_test)}, preserve=ASCII_CONTROLS) returned:\n {repr(decode_pc6001_8bit_charset(pc6001_8bit_test, preserve=ASCII_CONTROLS))}, expecting:\n {repr(expected_ascii_controls_unicode)}"
    assert encode_pc6001_8bit_charset(PC6001_8BIT_CHARSET) == bytes(
        [i for i in range(256)]
    ), f"encode_pc6001_8bit_charset(PC6001_8BIT_CHARSET)) returned:\n {repr(encode_pc6001_8bit_charset(PC6001_8BIT_CHARSET))}, expecting:\n {repr(bytes([i for i in range(256)]))}"
    assert (
        decode_pc6001_8bit_charset(bytes([i for i in range(256)]), preserve=NO_CONTROLS)
        == PC6001_8BIT_CHARSET
    ), f"decode_pc6001_8bit_charset(bytes([i for i in range(256)]), preserve=NO_CONTROLS) returned:\n {repr(decode_pc6001_8bit_charset(bytes([i for i in range(256)])), preserve=NO_CONTROLS)}, expecting:\n {repr(PC6001_8BIT_CHARSET)}"
    expected_altcharset_bytes = b"".join([bytes([0x14, i + 0x30]) for i in range(32)])
    assert (
        encode_pc6001_8bit_charset(PC6001_8BIT_ALTCHARSET) == expected_altcharset_bytes
    ), f"encode_pc6001_8bit_charset(PC6001_8BIT_ALTCHARSET)) returned:\n {repr(encode_pc6001_8bit_charset(PC6001_8BIT_ALTCHARSET))}, expecting:\n {repr(expected_altcharset_bytes)}"
    assert (
        decode_pc6001_8bit_charset(expected_altcharset_bytes) == PC6001_8BIT_ALTCHARSET
    ), f"decode_pc6001_8bit_charset({repr(expected_altcharset_bytes)}, preserve=NO_CONTROLS) returned:\n {repr(decode_pc6001_8bit_charset(expected_altcharset_bytes, preserve=NO_CONTROLS))}, expecting:\n {repr(PC6001_8BIT_ALTCHARSET)}"
    sound_mark_tests = {
        "[\N{COMBINING KATAKANA-HIRAGANA VOICED SOUND MARK}] = \N{COMBINING KATAKANA-HIRAGANA VOICED SOUND MARK}": "[\N{HALFWIDTH KATAKANA VOICED SOUND MARK}] = \N{HALFWIDTH KATAKANA VOICED SOUND MARK}",
        "[\N{COMBINING KATAKANA-HIRAGANA SEMI-VOICED SOUND MARK}] = \N{COMBINING KATAKANA-HIRAGANA SEMI-VOICED SOUND MARK}": "[\N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}] = \N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}",
        "[\N{KATAKANA-HIRAGANA VOICED SOUND MARK}] = \N{KATAKANA-HIRAGANA VOICED SOUND MARK}": "[\N{HALFWIDTH KATAKANA VOICED SOUND MARK}] = \N{HALFWIDTH KATAKANA VOICED SOUND MARK}",
        "[\N{KATAKANA-HIRAGANA SEMI-VOICED SOUND MARK}] = \N{KATAKANA-HIRAGANA SEMI-VOICED SOUND MARK}": "[\N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}] = \N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}",
        "[\N{KATAKANA-HIRAGANA PROLONGED SOUND MARK}] = \N{KATAKANA-HIRAGANA PROLONGED SOUND MARK}": "[\N{HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK}] = \N{HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK}",
        "[\N{HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK}] = \N{HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK}": "[\N{HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK}] = \N{HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK}",
        "[\N{HALFWIDTH KATAKANA VOICED SOUND MARK}] = \N{HALFWIDTH KATAKANA VOICED SOUND MARK}": "[\N{HALFWIDTH KATAKANA VOICED SOUND MARK}] = \N{HALFWIDTH KATAKANA VOICED SOUND MARK}",
        "[\N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}] = \N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}": "[\N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}] = \N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}",
    }
    for test_data, expected_result in sound_mark_tests.items():
        assert (
            decode_pc6001_8bit_charset(encode_pc6001_8bit_charset(test_data))
            == expected_result
        ), f"decode_pc6001_8bit_charset(encode_pc6001_8bit_charset({repr(test_data)})) returned:\n {repr(decode_pc6001_8bit_charset(encode_pc6001_8bit_charset(test_data)))}, expecting:\n {repr(expected_result)}"


smoke_test_pc6001_8bit_charset()


def kanjirom_to_jisrom(kanjirom):
    """
    expand KANJIROM subset into JIS level 1
    """
    assert len(kanjirom) == 32 * 1024
    jisrom = b""
    for ku in range(1, 48):
        if ku >= 10 and ku < 16:
            continue
        for ten in range(96):
            kuten = (ku, ten)
            if kuten in JIS_TO_KANJIROM6X_KUTEN_DATA:
                jisrom += kanjirom[:32]
                kanjirom = kanjirom[32:]
            else:
                jisrom += b"\xff" * 32
    return jisrom


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


def cgromkanjiviz(cgrom, cgrom_m, kanji_roms, cgromkanji_png):
    """Given an input file named by `cgromkanji_rom` containing Level 1 Kanji font ROM data in PC-8801 series `kanji1.rom` format a.k.a. PC-6007SR Kakuchou Kanji ROM & RAM Cartridge / PC-6601-01 Kakuchou Kakuchou ROM Cartridge `saverkanji` EXKANJI.ROM format, produce a visualization and save it as a PNG in the output file named by `exkanji_png`."""
    b = open(cgrom, "rb").read()
    xb = (b"\0" * 12 + b"\xff" * 4) * min(len(b) // 16, 256 + 64)
    b += b"\0" * (512 * 16 - len(b))
    xb += b"\xff" * (512 * 16 - len(xb))
    is_n60 = xb[16 * 256 : 16 * 512] == b"\xff" * 16 * 256
    if is_n60:
        assert len(VDG_FONT) == 128 * 16
        assert len(SG6_PATTERNS) == 64 * 16
        assert len(SG4_PATTERNS) == 16 * 16
        b = b[:16 * 256] + SG6_PATTERNS + VDG_FONT + 4 * SG4_PATTERNS + b[16 * 512:]
        xb = xb[:16 * 256] + 256 * (12 * b"\0" + (16 - 12) * b"\xFF") + xb[16 * 512:]
    assert len(b) == 512 * 16
    if cgrom_m:
        b += open(cgrom_m, "rb").read()
        xb += (b"\0" * 10 + b"\xff" * 6) * ((len(b) - len(xb)) // 16)
    b += b"\0" * (1024 * 16 - len(b))
    xb += b"\xff" * (len(b) - len(xb))
    assert len(b) == 1024 * 16
    b = interleave(pages=[b[: 512 * 16], b[512 * 16 :]])
    xb = interleave(pages=[xb[: 512 * 16], xb[512 * 16 :]])
    k = b""
    if kanji_roms:
        pages = [open(kanji_rom, "rb").read() for kanji_rom in kanji_roms]
        if len(pages) == 1:
            assert len(pages[0]) % 2 == 0
            pages = [pages[0][: len(pages[0]) // 2], pages[0][len(pages[0]) // 2 :]]
        k = interleave(pages=pages)
    xk = b"\0" * len(k)
    k = k + b"\0" * (32 * 1024 - len(k))
    xk += b"\xff" * (len(k) - len(xk))
    assert len(k) == 32 * 1024
    k = kanjirom_to_jisrom(k)
    xk = kanjirom_to_jisrom(xk)
    b += k
    xb += xk
    b += b"\0" * (128 * 1024 - len(b))
    xb += b"\xff" * (len(b) - len(xb))

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
            if (cc < 512)
            else not rtok(
                bytes([min(cvtr((cc - 512) // 96), 95) + 0xA0, (cc - 512) % 96 + 0xA0])
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
        return 512 + (kuten[0] - 1 - (6 if kuten[0] >= 16 else 0)) * 96 + kuten[1]

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
        for i in range(128):
            if xb[ord(ch) * 32 + (font & 1) + 256 * 32 * (font >> 1) + 2 * (i // 8)] & (
                0x80 >> (i % 8)
            ):
                continue
            for yo in range(scale):
                dr.point(
                    (x + i % 8, y + scale * (i // 8) + yo),
                    (
                        fg
                        if b[
                            ord(ch) * 32
                            + (font & 1)
                            + 256 * 32 * (font >> 1)
                            + 2 * (i // 8)
                        ]
                        & (0x80 >> (i % 8))
                        else bg
                    ),
                )

    def puts_at(dr, s, coords, color_pair, font=0, scale=1):
        x, y = coords
        for i in range(len(s)):
            ch = s[i : i + 1]
            ch_font = font
            if ch == "\N{LEFTWARDS ARROW}":
                if cgrom_m:
                    ch = chr(0x29)
                    ch_font = 3
                else:
                    ch = "<"
            elif ch == "\N{DOWNWARDS ARROW}":
                if cgrom_m:
                    ch = chr(0x2B)
                    ch_font = 3
                else:
                    ch = "v"
            elif ch == "\N{RIGHTWARDS ARROW}":
                if cgrom_m:
                    ch = chr(0x28)
                    ch_font = 3
                else:
                    ch = ">"
            elif ch == "\N{UPWARDS ARROW}":
                if cgrom_m:
                    ch = chr(0x2A)
                    ch_font = 3
                else:
                    ch = "^"
            putch_at(dr, ch, (x + 8 * scale * i, y), color_pair, ch_font, scale)

    dr = ImageDraw.Draw(im)
    if kanji_roms:
        puts_at(
            dr,
            " NEC PC-6001mkII/PC-6601 Kanji ROM (subset) ",
            (16 * 16 + 8, 4),
            (v, h),
        )
    puts_at(
        dr,
        "\N{LEFTWARDS ARROW} PC-6001/PC-6601 8-bit character set (8x12)",
        (16 * 16 + 4, 20),
        (k3, k),
    )
    if not is_n60:
        puts_at(
            dr,
            "PC-6001mkII/PC-6601 graphics (8x12) \N{RIGHTWARDS ARROW}",
            (16 * 235, 20),
            (k3, k),
        )
    else:
        puts_at(
            dr,
            "M5C6847P-1 CG6 2x3 (8x12) \N{RIGHTWARDS ARROW}",
            (16 * 235, 20),
            (k3, k),
        )
        puts_at(
            dr,
            "M5C6847P-1 VDG FONT (8x12) \N{RIGHTWARDS ARROW}",
            (16 * 235, 84),
            (k3, k),
        )
        puts_at(
            dr,
            "4x M5C6847P-1 CG4 2x2 (8x12) \N{RIGHTWARDS ARROW}",
            (16 * 235, 212),
            (k3, k),
        )
    if cgrom_m:
        puts_at(
            dr,
            "\N{LEFTWARDS ARROW} PC-6001/PC-6601 8-bit character set (8x10)",
            (16 * 16 + 4, 40),
            (w, k),
            font=1,
        )
        puts_at(
            dr,
            "PC-6001mkII/PC-6601 graphics (8x10) \N{RIGHTWARDS ARROW}",
            (16 * 235, 40),
            (w, k),
            font=1,
        )
    if kanji_roms:
        puts_at(
            dr,
            "\N{DOWNWARDS ARROW} (row number)",
            ((16 + 1) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
            (w1, k),
        )
        puts_at(
            dr,
            "\N{DOWNWARDS ARROW} (unallocated code area)",
            ((32 + z + 4) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
            (w2, k),
        )
        puts_at(
            dr,
            "\N{DOWNWARDS ARROW} (missing from old JIS)",
            ((17 * 7 + 2 + z) * 16 + 8, (16 - (96 + z - 1) // z - 1) * 16 - 4),
            (w1, k),
        )
        puts_at(
            dr,
            "fullwidth character set (subset of old JIS with level 1 Kanji)",
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
            "\N{LEFTWARDS ARROW} (column number key)",
            (-12 + 16 * (4 * (z + 1) - z // 2), 24 + 12),
            (w1, k),
        )

    def chx(cc):
        return (
            (cc % 16) + (15 * (16 + 1) if cc >= 256 else 0)
            if (cc < 512)
            else ((cc - 512) % z + (z + 1) * (cvtr((cc - 512) // 96) % z))
        )

    def chy(cc):
        return (
            (cc // 16) % 16
            if (cc < 512)
            else (cc - 512) % 96 // z
            + (cvtr((cc - 512) // 96) // z - 1) * ((96 + z - 1) // z + 1)
            + 1
            + 16
        )

    kanjirom_subset_chs = {kuten_ch(kuten) for kuten in JIS_TO_KANJIROM6X_KUTEN_DATA}

    for i in range(8 * len(b)):
        if (
            not xb[i // 8]
            or kanji_roms
            and (i // 256 >= 512)
            and (cvtr(((i // 256) - 512) // 96) <= 87)
        ):
            dr.point(
                (chx(i // 256) * 16 + i % 16, chy(i // 256) * 16 + (i // 16) % 16),
                (
                    [
                        [
                            [k, h][i // 256 in kanjirom_subset_chs],
                            [k3, w][1 if i & 8 else 0],
                        ][i // 256 < 512],
                        k1,
                        k2,
                        k1,
                    ]
                    if (b[i // 8] & (128 >> (i % 8)))
                    else [
                        [
                            [w, v][i // 256 in kanjirom_subset_chs],
                            [w3, k][1 if i & 8 else 0],
                        ][i // 256 < 512],
                        [w1, [w4, g][1 if i & 8 else 0]][i // 256 < 512],
                        w2,
                        w1,
                    ]
                )[2 * invc(i // 256) + (xb[i // 8] != 0)],
            )
    if kanji_roms:
        for i in range(1, 48 - 6):
            puts_at(
                dr,
                f"{i + (6 if i >= 10 else 0):02d}",
                (16 * chx(512 + 96 * (i - 1)), 16 * chy(512 + 96 * (i - 1))),
                (k, w1),
            )
            puts_at(
                dr,
                f"{i + (6 if i >= 10 else 0):02d}",
                (16 * chx(512 + 96 * (i - 1) + 95), 16 * chy(512 + 96 * (i - 1) + 95)),
                (k, w1),
            )
        xdeflect = 0
        for i, ch in enumerate("ＰＣ−６００１ｍｋＩＩとＰＣ−６６０１漢字ＲＯＭ"):
            kuten = [byt - 0xA0 for byt in ch.encode("EUC-JP")]
            if tuple(kuten) in JIS_TO_KANJIROM6X_KUTEN_DATA:
                putkuten_at(
                    dr,
                    kuten,
                    ((18 + i) * 16 + 4 + xdeflect, 104),
                    (v, h),
                )
            else:
                if ch == "\N{MINUS SIGN}":
                    ch = "-"
                ch = encode_pc6001_8bit_charset(ch)
                puts_at(
                    dr,
                    ch,
                    ((18 + i) * 16 + 4 + xdeflect, 104 - 1),
                    (v, h),
                    font=1,
                    scale=2,
                )
                xdeflect += 8 * len(ch) - 16
    im.save(cgromkanji_png)


def main():
    cgrom_m = None
    kanji_roms = []
    try:
        _, cgrom, cgromkanji_png = sys.argv
    except:
        try:
            _, cgrom, cgrom_m, cgromkanji_png = sys.argv
        except:
            try:
                _, cgrom, cgrom_m, kanji_rom, cgromkanji_png = sys.argv
                kanji_roms = [kanji_rom]
            except:
                _, cgrom, cgrom_m, kanji_rom1, kanji_rom2, cgromkanji_png = (
                    sys.argv
                )  # usage: python cgromkanjiviz.py CGROM [ CGROMm [ KANJIROM or KANJIROM1 KANJIROM2 ] ] OUTPUT
                kanji_roms = [kanji_rom1, kanji_rom2]
    cgromkanjiviz(cgrom, cgrom_m, kanji_roms, cgromkanji_png)


if __name__ == "__main__":
    main()
