"""Command line interface for the stem separator."""
from __future__ import annotations

import argparse
import pathlib
from typing import Optional

from .separator import StemSeparator


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Music stem separation")
    parser.add_argument("input", type=pathlib.Path, help="Input audio file")
    parser.add_argument(
        "output",
        type=pathlib.Path,
        help="Directory where separated stems will be written",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        help="Resample audio to this sample rate before processing",
    )
    parser.add_argument(
        "--n-fft",
        type=int,
        default=4096,
        help="FFT window size for spectral analysis",
    )
    parser.add_argument(
        "--hop-length",
        type=int,
        default=1024,
        help="Hop length for STFT computation",
    )
    parser.add_argument(
        "--margin-harmonic",
        type=float,
        default=1.0,
        help="HPSS margin controlling harmonic aggressiveness",
    )
    parser.add_argument(
        "--margin-percussive",
        type=float,
        default=1.0,
        help="HPSS margin controlling percussive aggressiveness",
    )
    parser.add_argument(
        "--nn-filter-width",
        type=int,
        default=31,
        help="Width for the nearest neighbour filter (odd integer)",
    )
    parser.add_argument(
        "--no-vocal-band",
        action="store_true",
        help="Disable band limiting for vocals",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files",
    )
    return parser


def main(args: Optional[list[str]] = None) -> None:
    parser = build_parser()
    parsed = parser.parse_args(args)

    vocal_band = None if parsed.no_vocal_band else (80.0, 1100.0)

    separator = StemSeparator(
        sample_rate=parsed.sample_rate,
        n_fft=parsed.n_fft,
        hop_length=parsed.hop_length,
        margin_harmonic=parsed.margin_harmonic,
        margin_percussive=parsed.margin_percussive,
        nn_filter_width=parsed.nn_filter_width,
        vocal_band=vocal_band,
    )

    separator.separate(
        parsed.input,
        output_directory=parsed.output,
        overwrite=parsed.overwrite,
    )


if __name__ == "__main__":
    main()
