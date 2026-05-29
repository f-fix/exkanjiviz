#!/usr/bin/env python3

import argparse
from pathlib import Path

import numpy as np


def reorder_bits_to_ic(io: bytes) -> bytes:
    arr = np.frombuffer(io, dtype=np.uint8)
    indices = np.arange(len(io), dtype=np.uint32)
    reordered = (
        ((indices & 0b11000000000000000) >> 12)
        | ((indices & 0b111111111111000) << 2)
        | (indices & 0b100000000000000111)
    )
    return arr[reordered].tobytes()


def reorder_bits_to_io(ic: bytes) -> bytes:
    arr = np.frombuffer(ic, dtype=np.uint8)
    indices = np.arange(len(ic), dtype=np.uint32)
    reordered = (
        ((indices & 0b11000) << 12)
        | ((indices & 0b11111111111100000) >> 2)
        | (indices & 0b100000000000000111)
    )
    return arr[reordered].tobytes()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert ROM files between I/O-ordered and IC-ordered formats."
    )
    parser.add_argument(
        "--io",
        metavar="PATH",
        type=Path,
        required=True,
        help="Path to the I/O-ordered ROM file",
    )
    parser.add_argument(
        "--ic",
        metavar="PATH",
        type=Path,
        required=True,
        help="Path to the IC-ordered ROM file",
    )
    parser.add_argument(
        "--to",
        choices=["ic", "io"],
        required=True,
        help="Conversion direction: 'ic' or 'io'",
    )
    args = parser.parse_args()

    if args.to == "ic":
        data = args.io.read_bytes()
        assert len(data) in {2**17, 2**18}, f"Unexpected ROM size: {len(data)} bytes"
        args.ic.write_bytes(reorder_bits_to_ic(data))
        print(f"Converted {args.io} → {args.ic} (I/O-ordered → IC-ordered)")
    else:
        data = args.ic.read_bytes()
        assert len(data) in {2**17, 2**18}, f"Unexpected ROM size: {len(data)} bytes"
        args.io.write_bytes(reorder_bits_to_io(data))
        print(f"Converted {args.ic} → {args.io} (IC-ordered → I/O-ordered)")


if __name__ == "__main__":
    main()
