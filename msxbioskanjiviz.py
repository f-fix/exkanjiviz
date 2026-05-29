#!/usr/bin/env python3

"""
quick-and-dirty visualizer for font data from:
- MSX2/2+/TurboR `BIOS.ROM` `KANJI.ROM`
- MSX2/2+/TurboR `BIOS.ROM` `KANJI1.ROM` `KANJI2.ROM`
the ROM data should be in I/O port order.
"""


from PIL import Image, ImageDraw

import codecs
import gzip
import sys
import unicodedata


# 8-bit/single-byte character encoding scheme

NO_CONTROLS = b""
MINIMAL_CONTROLS = b"\0\r\n\x1a\x7f"
ASCII_CONTROLS = bytes(range(0x20)) + b"\x7f"

# i am sure this is not the best way to solve this. this mapping
# should work OK for a Japanese MSX. it does not handle the alternate
# character set shift sequences well. it also does not handle
# fullwidth Kanji! the hiragana and kanji here should all be
# half-width ones, but Unicode is missing those so we live with
# fullwidth instead. the arrows and control pictures shown here in the
# first row are actually control characters and are not graphically
# displayable on an MSX.
MSXJP_8BIT_CHARSET = (
    "␀␁␂␃␄␅␆␇␈␉␊␋␌␍␎␏␐␑␒␓␔␕␖␗␘␙␚␛￫￩￪￬"
    " !\"#$%&'()*+,-./0123456789:;<=>?"
    "@ABCDEFGHIJKLMNOPQRSTUVWXYZ[¥]^_"
    "`abcdefghijklmnopqrstuvwxyz{¦}~␡"
    "♠♥♦♣￮•をぁぃぅぇぉゃゅょっ\uf8f4あいうえおかきくけこさしすせそ"
    "\uf8f0｡｢｣､･ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ"
    "ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝﾞﾟ"
    "たちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわん\uf8f2\uf8f3"
)
assert len(MSXJP_8BIT_CHARSET) == 256
MSXJP_8BIT_ALTCHARSET = "\uf8f1月火水木金土日年円時分秒百千万" "π┴┬┤├┼│─┌┐└┘╳大中小"
assert len(MSXJP_8BIT_ALTCHARSET) == 32
MSXJP_8BIT_CHARMAP = {MSXJP_8BIT_CHARSET[i]: bytes([i]) for i in range(256)} | {
    MSXJP_8BIT_ALTCHARSET[i]: bytes([0x01, i + 0x40]) for i in range(32)
}
MSXJP_8BIT_CHARMAP_COMPAT = {
    unicodedata.normalize("NFKD", key): value
    for key, value in MSXJP_8BIT_CHARMAP.items()
    if unicodedata.normalize("NFKD", key) != key
} | {
    "\N{KATAKANA-HIRAGANA VOICED SOUND MARK}": MSXJP_8BIT_CHARMAP[
        "\N{HALFWIDTH KATAKANA VOICED SOUND MARK}"
    ],
    "\N{KATAKANA-HIRAGANA SEMI-VOICED SOUND MARK}": MSXJP_8BIT_CHARMAP[
        "\N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}"
    ],
    "\N{KATAKANA-HIRAGANA PROLONGED SOUND MARK}": MSXJP_8BIT_CHARMAP[
        "\N{HALFWIDTH KATAKANA-HIRAGANA PROLONGED SOUND MARK}"
    ],
}


def encode_msxjp_8bit_charset(s, try_harder=True):
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
        byt = MSXJP_8BIT_CHARMAP.get(ch, MSXJP_8BIT_CHARMAP_COMPAT.get(ch)) or (
            bytes([ord(ch)]) if ord(ch) <= 0x7F else None
        )
        if byt is None and try_harder:
            cch = unicodedata.normalize("NFKD", ch)
            byt = MSXJP_8BIT_CHARMAP.get(cch, MSXJP_8BIT_CHARMAP_COMPAT.get(cch)) or (
                bytes([ord(cch)]) if len(cch) == 1 and ord(cch) <= 0x7F else None
            )
        if byt is None and try_harder:
            cch = unicodedata.normalize("NFC", ch)
            byt = MSXJP_8BIT_CHARMAP.get(cch, MSXJP_8BIT_CHARMAP_COMPAT.get(cch)) or (
                bytes([ord(cch)]) if len(cch) == 1 and ord(cch) <= 0x7F else None
            )
        if byt is None:
            raise UnicodeEncodeError(
                "msxjp-8bit",
                s,
                chars_consumed,
                chars_consumed + 1,
                f"no mapping for U+{ord(ch):04X} {unicodedata.name(ch, repr(ch))}",
            )
        byts += byt
        chars_consumed += 1
    return byts


def decode_msxjp_8bit_charset(byts, preserve=MINIMAL_CONTROLS):
    s, bytes_consumed, num_bytes = "", 0, len(byts)
    while bytes_consumed < num_bytes:
        byt = byts[bytes_consumed]
        if (
            bytes_consumed > 0
            and byts[bytes_consumed - 1] == 0x01
            and byt >= 0x40
            and byt <= 0x5F
        ):
            s = s[: -len(MSXJP_8BIT_CHARSET[0x01])] + MSXJP_8BIT_ALTCHARSET[byt - 0x40]
        elif byt in preserve:
            s += chr(byt)
        else:
            s += MSXJP_8BIT_CHARSET[byt]
        if (
            len(s) > 1
            and s[-1:]
            in "\N{HALFWIDTH KATAKANA VOICED SOUND MARK}\N{HALFWIDTH KATAKANA SEMI-VOICED SOUND MARK}"
            and unicodedata.name(s[-2:-1], "?").lower().startswith("hiragana letter")
        ):
            s = s[:-2] + unicodedata.normalize("NFKC", s[-2:])
        bytes_consumed += 1
    round_trip_byts = encode_msxjp_8bit_charset(s)
    assert byts == round_trip_byts, UnicodeDecodeError(
        "msxjp-8bit",
        byts,
        0,
        num_bytes,
        f"round-trip failure for {repr(s)} with preserve={repr(preserve)}; result:\n {repr(byts)}, got:\n {repr(round_trip_byts)}",
    )
    return s


def smoke_test_msxjp_8bit_charset():
    assert decode_msxjp_8bit_charset(b"") == ""
    assert encode_msxjp_8bit_charset("") == b""
    assert decode_msxjp_8bit_charset(b"\x00") == "\x00"
    assert encode_msxjp_8bit_charset("\x00") == b"\x00"
    assert encode_msxjp_8bit_charset("␀") == b"\x00"
    assert encode_msxjp_8bit_charset("\uf8f1") == b"\x01\x40"
    assert encode_msxjp_8bit_charset("小") == b"\x01\x5f"
    assert encode_msxjp_8bit_charset("␁") == b"\x01"
    assert encode_msxjp_8bit_charset("\x01") == b"\x01"
    assert encode_msxjp_8bit_charset("\x01\x5f") == b"\x01\x5f"
    round_trip_test_failures = {
        encode_msxjp_8bit_charset(decode_msxjp_8bit_charset(bytes([i]))): bytes([i])
        for i in range(256)
        if encode_msxjp_8bit_charset(decode_msxjp_8bit_charset(bytes([i])))
        != bytes([i])
    }
    round_trip_test_failures.update(
        {
            encode_msxjp_8bit_charset(
                decode_msxjp_8bit_charset(bytes([0x01, i]))
            ): bytes([0x01, i])
            for i in range(256)
            if encode_msxjp_8bit_charset(decode_msxjp_8bit_charset(bytes([0x01, i])))
            != bytes([0x01, i])
        }
    )
    round_trip_test_failures.update(
        {
            encode_msxjp_8bit_charset(
                decode_msxjp_8bit_charset(bytes([i, 0xEE]))
            ): bytes([i, 0xEE])
            for i in range(256)
            if encode_msxjp_8bit_charset(decode_msxjp_8bit_charset(bytes([i, 0xEE])))
            != bytes([i, 0xEE])
        }
    )
    round_trip_test_failures.update(
        {
            encode_msxjp_8bit_charset(
                decode_msxjp_8bit_charset(bytes([i, 0xEF]))
            ): bytes([i, 0xEF])
            for i in range(256)
            if encode_msxjp_8bit_charset(decode_msxjp_8bit_charset(bytes([i, 0xEF])))
            != bytes([i, 0xEF])
        }
    )
    assert not round_trip_test_failures, round_trip_test_failures
    unicode_test = (
        "\r\n".join(
            (
                "\\￮╳•╳o/ I ♥ MSXJP!",
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
                b"\\\x84\x01\\\x85\x01\\o/ I \x81 MSXJP!",
                b"\xca\xdf\xcb\xdf\xba\xdd\x96\xde\x01]\x9d\x97\xe3\xde\x9d!",
                b"\xa2\xca\xdf\xcb\xdf\xba\xdd\xa3\xea \xe6\x8f\xee\xdf\xfd\xe3\xde\xfd\x97 \x96\xde \x9e\x92\x9f\xde\x93\x9c\xe08\xcb\xde\xaf\xc4\xba\xdd\xcb\xdf\xad\xb0\xc0\xe3\xde\xa4\xf4\x9d\x92\x9a\xe4\x96\xf7 \x92\xe1\x9c\xde\x97 \xe6\xfd\x97 \x86 \xea\x98\x9c\xef\x9c\xe0\xa1",
                b"\xa2!?\xa3 \xa5\xa5\xa5",
                b"\x01V||~-\xb0\x01W_",
                b"\\0=0\x01I",
                b"2025\x01H07\x01A18\x01G 14\x01J11\x01K16\x01L",
                b"\x01X\x01R\x01W\x01Y \x01X\x1e\x01Y ++-+  ^/",
                b"\x01T\x01U\x01W\x01S \x1d\x01U\x1c ++-+ <X>",
                b"\x01V\x01V\x85\x01V\xa5\x01Z\x1f\x01[ ||.| /v ",
                b"\x01Z\x01Q\x01W\x01[<>O[]++-+ \x01P>3",
                bytes([i for i in range(0x20)] + [0x7F]),
            )
        )
        + b"\x1a\x00"
    )
    assert (
        encode_msxjp_8bit_charset(unicode_test) == expected_8bit
    ), f"encode_msxjp_8bit_charset({repr(unicode_test)}) returned:\n {repr(encode_msxjp_8bit_charset(unicode_test))}, expecting:\n {repr(expected_8bit)}"
    msxjp_8bit_test = expected_8bit
    try:
        unexpected_8bit = encode_msxjp_8bit_charset(unicode_test, try_harder=False)
        assert (
            False
        ), f"Expected a UnicodeEncodeError for encode_msxjp_8bit_charset({repr(unicode_test)}, try_harder=False) but no error was raised"
    except UnicodeEncodeError:
        pass
    except Exception as e:
        assert (
            False
        ), f"Expected a UnicodeEncodeError for encode_msxjp_8bit_charset({repr(unicode_test)}, try_harder=False) but {repr(e)} was raised instead"
    expected_unicode = (
        "\r\n".join(
            (
                "¥￮╳•╳o/ I ♥ MSXJP!",
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
        decode_msxjp_8bit_charset(msxjp_8bit_test) == expected_unicode
    ), f"decode_msxjp_8bit_charset({repr(msxjp_8bit_test)}) returned:\n {repr(decode_msxjp_8bit_charset(msxjp_8bit_test))}, expecting:\n {repr(expected_unicode)}"
    assert (
        encode_msxjp_8bit_charset(expected_unicode, try_harder=False) == msxjp_8bit_test
    ), f"encode_msxjp_8bit_charset({repr(expected_unicode)}, try_harder=False) returned:\n {repr(encode_msxjp_8bit_charset(expected_unicode, try_harder=False))}, expecting:\n {repr(msxjp_8bit_test)}"
    expected_no_controls_unicode = (
        "␍␊".join(
            (
                "¥￮╳•╳o/ I ♥ MSXJP!",
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
        decode_msxjp_8bit_charset(msxjp_8bit_test, preserve=NO_CONTROLS)
        == expected_no_controls_unicode
    ), f"decode_msxjp_8bit_charset({repr(msxjp_8bit_test)}, preserve=NO_CONTROLS) returned:\n {repr(decode_msxjp_8bit_charset(msxjp_8bit_test, preserve=NO_CONTROLS))}, expecting:\n {repr(expected_no_controls_unicode)}"
    expected_ascii_controls_unicode = (
        "\r\n".join(
            (
                "¥￮╳•╳o/ I ♥ MSXJP!",
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
        decode_msxjp_8bit_charset(msxjp_8bit_test, preserve=ASCII_CONTROLS)
        == expected_ascii_controls_unicode
    ), f"decode_msxjp_8bit_charset({repr(msxjp_8bit_test)}, preserve=ASCII_CONTROLS) returned:\n {repr(decode_msxjp_8bit_charset(msxjp_8bit_test, preserve=ASCII_CONTROLS))}, expecting:\n {repr(expected_ascii_controls_unicode)}"
    assert encode_msxjp_8bit_charset(MSXJP_8BIT_CHARSET) == bytes(
        [i for i in range(256)]
    ), f"encode_msxjp_8bit_charset(MSXJP_8BIT_CHARSET)) returned:\n {repr(encode_msxjp_8bit_charset(MSXJP_8BIT_CHARSET))}, expecting:\n {repr(bytes([i for i in range(256)]))}"
    assert (
        decode_msxjp_8bit_charset(bytes([i for i in range(256)]), preserve=NO_CONTROLS)
        == MSXJP_8BIT_CHARSET
    ), f"decode_msxjp_8bit_charset(bytes([i for i in range(256)]), preserve=NO_CONTROLS) returned:\n {repr(decode_msxjp_8bit_charset(bytes([i for i in range(256)])), preserve=NO_CONTROLS)}, expecting:\n {repr(MSXJP_8BIT_CHARSET)}"
    expected_altcharset_bytes = b"".join([bytes([0x01, i + 0x40]) for i in range(32)])
    assert (
        encode_msxjp_8bit_charset(MSXJP_8BIT_ALTCHARSET) == expected_altcharset_bytes
    ), f"encode_msxjp_8bit_charset(MSXJP_8BIT_ALTCHARSET)) returned:\n {repr(encode_msxjp_8bit_charset(MSXJP_8BIT_ALTCHARSET))}, expecting:\n {repr(expected_altcharset_bytes)}"
    assert (
        decode_msxjp_8bit_charset(expected_altcharset_bytes) == MSXJP_8BIT_ALTCHARSET
    ), f"decode_msxjp_8bit_charset({repr(expected_altcharset_bytes)}, preserve=NO_CONTROLS) returned:\n {repr(decode_msxjp_8bit_charset(expected_altcharset_bytes, preserve=NO_CONTROLS))}, expecting:\n {repr(MSXJP_8BIT_ALTCHARSET)}"
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
            decode_msxjp_8bit_charset(encode_msxjp_8bit_charset(test_data))
            == expected_result
        ), f"decode_msxjp_8bit_charset(encode_msxjp_8bit_charset({repr(test_data)})) returned:\n {repr(decode_msxjp_8bit_charset(encode_msxjp_8bit_charset(test_data)))}, expecting:\n {repr(expected_result)}"


smoke_test_msxjp_8bit_charset()


def shuffle_bios(b):
    cgtabl = int.from_bytes(b[4:6], "little")
    font = b[cgtabl : 256 * 8 + cgtabl]
    assert len(font) == 2048
    return b"".join(
        [
            b"".join(
                bytes([font[ch * 8 + y], 0xFC & font[ch * 8 + y]]) for y in range(8)
            )
            for ch in range(256)
        ]
    )


def shuffle_kanji_cc(ch):
    return ch
    # 3 / 4 / 5 => 1 / 17 / 9
    # 9 / 10 / 11 => 3 / 19 / 11
    # 12 / 13 / 14 => 4 / 20 / 12
    # 21 / 22 / 23 => 7 / 23 / 15
    # 30 / 31 / 32 => 32 / 48 / 64
    row32, col32 = ch // 32, ch % 32
    row32_shuf = row32
    if row32 < 24:
        row32_shuf = 24 * (row32 // 24) + (0, 16, 8)[row32 % 3] + (row32 % 24) // 3
    print(row32, row32_shuf)
    return col32 + 32 * row32_shuf


def shuffle_glyph(glyph):
    assert len(glyph) == 32
    return b"".join(
        [glyph[i : 1 + i] + glyph[8 + i : 9 + i] for i in range(8)]
        + [glyph[16 + i : 17 + i] + glyph[24 + i : 25 + i] for i in range(8)]
    )


def shuffle_kanji(k):
    assert len(k) % 32 == 0
    return b"".join(
        shuffle_glyph(
            b"".join(bytes([k[32 * shuffle_kanji_cc(ch) + o]]) for o in range(32))
        )
        for ch in range(len(k) // 32)
    )


def msxbioskanjiviz(bios, kanji_roms, bioskanji_png):
    """Given an input file named by `bios` containing MSX BIOS+BASIC and one or two named by `kanji_roms` containing Kanji font ROM data in I/O readout order, produce a visualization and save it as a PNG in the output file named by `bioskanji_png`."""
    b = open(bios, "rb").read()
    b = shuffle_bios(b)
    xb = b"\0" * len(b)
    discontinuity = 512
    b += b"\0" * (discontinuity * 32 - len(b))
    xb += b"\xff" * (len(b) - len(xb))
    assert len(b) == discontinuity * 32
    k = b""
    if kanji_roms:
        k = b"".join([open(kanji_rom, "rb").read() for kanji_rom in kanji_roms])
        k = shuffle_kanji(k)
        b = (
            b[: 256 * 32]
            + b"\0" * 32 * 32
            + k[: 96 * 32]
            + b"\0" * 32 * 32
            + k[9 * 96 * 32 : 10 * 96 * 32]
            + b[512 * 32 :]
        )
        xb = (
            xb[: 256 * 32]
            + b"\xff" * 32 * 32
            + b"\0" * 96 * 32
            + b"\xff" * 32 * 32
            + b"\0" * 96 * 32
            + xb[512 * 32 :]
        )
    xk = b"\0" * len(k)
    k += b"\0" * (32 * discontinuity - len(k))
    xk += b"\xff" * (len(k) - len(xk))
    b += k[: (11 * 96 - 32) * 32] + b"\xff" * 32 * 32 + k[(11 * 96 - 32) * 32 :]
    xb += xk[: (11 * 96 - 32) * 32] + b"\xff" * 32 * 32 + xk[(11 * 96 - 32) * 32 :]
    b += b"\0" * (128 * discontinuity - len(b))
    xb += b"\xff" * (len(b) - len(xb))

    def cvtr(r):
        return 0 * 1 + r + 5 * (r >= 11)

    def rtok(byts):
        return (
            byts.decode("EUC-JP", "ignore")
            .encode("iso2022_jp_1", "ignore")
            .decode("iso2022_jp_1", "ignore")
            .encode("EUC-JP")
            == byts
        )

    def invc(cc):
        if (cc - discontinuity) // 96 == 2 and (cc - discontinuity) % 96 not in range(
            1, 14 + 1
        ):
            return True  # added in 83jis, not in 78jis
        if (cc - discontinuity) // 96 == 8:
            return True  # added in 83jis, not in 78jis
        if (cc - discontinuity) // 96 == 84 - 5 and (cc - discontinuity) % 96 in {5, 6}:
            return True  # added in 90jis, not in 78jis / 83jis
        return (
            False
            if (cc < discontinuity)
            else not rtok(
                bytes(
                    [
                        min(cvtr((cc - discontinuity) // 96), 95) + 0xA0,
                        (cc - discontinuity) % 96 + 0xA0,
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
            discontinuity
            + (kuten[0] - 0 * 1 - (5 if kuten[0] >= 16 else 0)) * 96
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
        if font in (2, 3):
            byt = ord(ch.encode("SJIS"))
            for i in range(128):
                if font == 1 and (i % 8) >= 6:
                    continue
                dr.point(
                    (x + i % 8, y + i // 8),
                    (
                        fg
                        if b[256 * 32 + (font & 1) + 32 * byt + 2 * (i // 8)]
                        & (0x80 >> (i % 8))
                        else bg
                    ),
                )
            return
        ch = encode_msxjp_8bit_charset(ch)
        if len(ch) == 2 and ch[0] == 0x01:
            ch = bytes([ch[1] - 0x40])
        for i in range(64):
            if xb[ord(ch) * 16 + (font & 1) + 256 * 16 * (font >> 1) + 2 * (i // 8)] & (
                0x80 >> (i % 8)
            ):
                continue
            for yo in range(scale):
                dr.point(
                    (x + i % 8, y + scale * (i // 8) + yo),
                    (
                        fg
                        if b[
                            ord(ch) * 16
                            + (font & 1)
                            + 256 * 16 * (font >> 1)
                            + 2 * (i // 8)
                        ]
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
            if font == 2 and kanji_roms:
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
    if kanji_roms:
        puts_at(
            dr,
            " MSX Kanji ROM ",
            (16 * 16 + 8, 4),
            (v, h),
        )
    puts_at(
        dr,
        "\N{LEFTWARDS ARROW} 8-bit Roman and Kana (ｶﾀｶﾅ and ひらがな) set (8x8)",
        (16 * 16 + 4, 16),
        (k3, w3),
    )
    puts_at(
        dr,
        "  Includes 8x8 Kanji: 月火水木金土日年円時分秒百千万大中小",
        (16 * 16 + 4, 24),
        (k3, w3),
    )
    puts_at(
        dr,
        "\N{LEFTWARDS ARROW} SCREEN 0 Roman and Kana (ｶﾀｶﾅ and ひらがな) set (6x8)",
        (16 * 16 + 4, 32),
        (k3, k),
        font=1,
    )
    puts_at(
        dr,
        "  Includes 6x8 Kanji: 月火水木金土日年円時分秒百千万大中小",
        (16 * 16 + 4, 40),
        (k3, k),
        font=1,
    )
    if kanji_roms:
        puts_at(
            dr,
            "  Halfwidth Roman and Katakana (ｶﾀｶﾅ) set (8x16)",
            (16 * 16 + 4, 52),
            (k3, w3),
            font=2,
        )
        puts_at(
            dr,
            "  Halfwidth Roman and Katakana (ｶﾀｶﾅ) set (8x12)",
            (16 * 16 + 4, 68),
            (w, k),
            font=3,
        )
        puts_at(
            dr,
            "  Halfwidth Roman and Katakana (ｶﾀｶﾅ) set (8x16) \N{RIGHTWARDS ARROW}",
            (16 * 16 * 14 + 4, 52),
            (k3, w3),
            font=2,
        )
        puts_at(
            dr,
            "  Halfwidth Roman and Katakana (ｶﾀｶﾅ) set (8x12) \N{RIGHTWARDS ARROW}",
            (16 * 16 * 14 + 4, 68),
            (w, k),
            font=3,
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
            "fullwidth character set (extended subset of old JIS with level 1 Kanji)",
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
            (cc % 16) + (15 * (16 + 1) if cc >= 256 else 0)
            if (cc < discontinuity)
            else (
                (cc - discontinuity) % z
                + (z + 1) * (cvtr((cc - discontinuity) // 96) % z)
            )
        )

    def chy(cc):
        return (
            (cc // 16) % 16
            if (cc < discontinuity)
            else (cc - discontinuity) % 96 // z
            + (cvtr((cc - discontinuity) // 96) // z - 1) * ((96 + z - 1) // z + 1)
            + 1
            + 16
        )

    for i in range(8 * len(b)):
        if (
            not xb[i // 8]
            or kanji_roms
            and (i // 256 >= discontinuity)
            # and (cvtr(((i // 256) - discontinuity) // 96) <= 87)
        ):
            if (i // 256 < 256) and i % 16 >= 14:
                continue
            dr.point(
                (chx(i // 256) * 16 + i % 16, chy(i // 256) * 16 + (i // 16) % 16),
                (
                    [
                        [
                            k,
                            [k3, w][1 if i & 8 else 0],
                        ][i // 256 < discontinuity],
                        k1,
                        k2,
                        k1,
                    ]
                    if (b[i // 8] & (128 >> (i % 8)))
                    else [
                        [
                            w,
                            [w3, k][1 if i & 8 else 0],
                        ][i // 256 < discontinuity],
                        [w1, [w4, g][1 if i & 8 else 0]][i // 256 < discontinuity],
                        w2,
                        w1,
                    ]
                )[2 * invc(i // 256) + (xb[i // 8] != 0)],
            )
    if kanji_roms:
        for i in range(96 - 5):
            puts_at(
                dr,
                f"{i + (5 if i >= 11 else 0):02d}",
                (
                    16 * chx(discontinuity + 96 * i),
                    16 * chy(discontinuity + 96 * i) - 8,
                ),
                (k, w1),
            )
            puts_at(
                dr,
                f"{i + (5 if i >= 11 else 0):02d}",
                (
                    16 * chx(discontinuity + 96 * i + 95),
                    16 * chy(discontinuity + 96 * i + 95) + 16,
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
    im.save(bioskanji_png)


def main():
    kanji_roms = []
    try:
        _, bios, bioskanji_png = sys.argv
    except:
        try:
            _, bios, kanji_rom, bioskanji_png = sys.argv
            kanji_roms = [kanji_rom]
        except:
            (  # usage: python msxbioskanjiviz.py BIOS.ROM [ KANJI.ROM or KANJI1.ROM KANJI2.ROM ] ] OUTPUT
                _,
                bios,
                kanji_rom1,
                kanji_rom2,
                bioskanji_png,
            ) = sys.argv
            kanji_roms = [kanji_rom1, kanji_rom2]
    msxbioskanjiviz(bios, kanji_roms, bioskanji_png)


if __name__ == "__main__":
    main()
