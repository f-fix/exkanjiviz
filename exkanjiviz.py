#!/usr/bin/env python3

import sys


def exkanjiviz(exkanji_rom, exkanji_png):

    b = open(exkanji_rom, "rb").read()
    swizp = lambda p: (p % 3) * 8 + (p // 3) % 8 + (p // 24) * 24
    swizs = lambda s: (s % 3) * 32 + (s // 3)
    swizr = lambda r: swizs(r) ^ 16
    swizk = lambda k: swizr(k - 23) + 23 if k >= 23 else k
    swizj = lambda j: swizk(swizp(j) if j < 24 else j)
    swizi = lambda i: (i & 0x1F) | (0x20 * swizj(i // 0x20))
    swiz = lambda b: b"".join([b[swizi(i) * 32 :][:32] for i in range(len(b) // 32)])
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
    rlbl = lambda i: b"".join(
        [
            b[(cvtr(i) // 10 + (0x30 - 0x10 * (cvtr(i) < 10))) * 32 + 2 * r :][:1]
            + b[(cvtr(i) % 10 + 0x30) * 32 + 2 * r :][:1]
            for r in range(16)
        ]
    )
    cvtr = lambda r: 1 + r + 6 * (r > 8)
    rtok = (
        lambda byts: byts.decode("EUC-JP", "ignore")
        .encode("iso2022_jp_1", "ignore")
        .decode("iso2022_jp_1", "ignore")
        .encode("EUC-JP")
        == byts
    )
    invc = lambda cc: (
        False
        if (cc < 256)
        else not rtok(
            bytes([min(cvtr((cc - 256) // 96), 95) + 0xA0, (cc - 256) % 96 + 0xA0])
        )
    )
    from PIL import Image, ImageDraw

    z = 16
    k, w, g, w1, k1, w2, k2, w3, k3, w4 = (
        (0, 0, 0, 255),
        (255, 255, 255, 255),
        (127, 127, 127, 0),
        (255, 0, 255),
        (63, 0, 63),
        (255, 255, 0),
        (255, 0, 0),
        (0, 63, 0),
        (0, 255, 0),
        (0, 127, 0),
    )
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
    kuten_ch = (
        lambda kuten: 256
        + (kuten[0] - 1 - (6 if kuten[0] >= 16 else 0)) * 96
        + kuten[1]
    )
    putkuten_at = lambda dr, kuten, x, y, fg, bg: (
        [
            dr.point(
                (x + i % 16, y + i // 16),
                fg if b[kuten_ch(kuten) * 32 + (i // 8)] & (0x80 >> (i % 8)) else bg,
            )
            for i in range(256)
        ]
        + [None]
    )[-1]
    putch_at = lambda dr, ch, x, y, fg, bg: (
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
    puts_at = lambda dr, s, x, y, fg, bg: (
        [putch_at(dr, s[i : i + 1], x + 8 * i, y, fg, bg) for i in range(len(s))]
        + [None]
    )[-1]
    dr = ImageDraw.Draw(im)
    puts_at(dr, " NEC PC-6007SR Kakuchou Kanji ROM ", 16 * 16 + 8, 4, w, k)
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
    [
        puts_at(
            dr,
            "%02d" % i,
            16 * (i % z + 3 * (z + 1) - z // 2),
            24 + 16 * (i // z),
            [w1, k][i % 2],
            [k, w1][i % 2],
        )
        for i in range(1, 95)
    ]
    puts_at(
        dr,
        "\x1d (column number key)",
        -12 + 16 * (4 * (z + 1) - z // 2),
        24 + 12,
        w1,
        k,
    )
    chx = lambda cc: (
        cc % 16
        if (cc < 256)
        else ((cc - 256) % z + (z + 1) * (cvtr((cc - 256) // 96) % z))
    )
    chy = lambda cc: (
        cc // 16
        if (cc < 256)
        else (cc - 256) % 96 // z
        + (cvtr((cc - 256) // 96) // z - 1) * ((96 + z - 1) // z + 1)
        + 1
        + 16
    )
    [
        dr.point(
            (chx(i // 256) * 16 + i % 16, chy(i // 256) * 16 + (i // 16) % 16),
            (
                [[k, k3][i // 256 < 256], k1, k2, k1]
                if (b[i // 8] & (128 >> (i % 8)))
                else [[w, w3][i // 256 < 256], [w1, w4][i // 256 < 256], w2, w1]
            )[2 * invc(i // 256) + (xb[i // 8] != 0)],
        )
        for i in range(8 * len(b))
        if not xb[i // 8] or (i // 256 < 256) or (cvtr(((i // 256) - 256) // 96) <= 87)
    ]
    [
        [
            puts_at(
                dr,
                f"{i + (6 if i >= 10 else 0):02d}",
                16 * chx(256 + 96 * (i - 1)),
                16 * chy(256 + 96 * (i - 1)),
                k,
                w1,
            ),
            puts_at(
                dr,
                f"{i + (6 if i >= 10 else 0):02d}",
                16 * chx(256 + 96 * (i - 1) + 95),
                16 * chy(256 + 96 * (i - 1) + 95),
                k,
                w1,
            ),
        ]
        for i in range(1, 48 - 6)
    ]
    [
        putkuten_at(
            dr, [byt - 0xA0 for byt in ch.encode("EUC-JP")], (20 + i) * 16 + 4, 64, w, k
        )
        for i, ch in enumerate("拡張漢字ＲＡＭ＆ＲＯＭカートリッジ")
    ]
    im.save(exkanji_png)


def main():
    _, exkanji_rom, exkanji_png = sys.argv
    exkanjiviz(exkanji_rom, exkanji_png)


if __name__ == "__main__":
    main()
