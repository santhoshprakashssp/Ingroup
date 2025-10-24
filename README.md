# Ingroup Stem Separator

This repository provides a lightweight but effective audio stem separation tool
that can split a mixed song into individual tracks for vocals, drums, and the
remaining instruments. The system is implemented in pure Python using
`librosa` for spectral processing, so it can run on standard CPUs without
needing heavyweight neural network models.

## Features

- Harmonic/percussive source separation (HPSS) to isolate drums accurately.
- Nearest-neighbour filtering and adaptive band-pass constraints to enhance
  vocal isolation and minimise instrumental bleed.
- Simple command line interface for batch processing.
- Configurable analysis parameters (FFT size, hop length, HPSS margins, etc.)
  to tune quality versus performance for different types of material.

## Installation

Create a virtual environment and install the project dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

Alternatively, install the package in editable mode using `pip install -e .` if
you plan to modify the source code.

## Usage

Separate an audio file into stems and write them to an output folder:

```bash
python -m stem_separator.cli input_song.wav stems/
```

The command accepts several optional parameters:

- `--sample-rate`: Resample the audio before processing (default `44100`).
- `--n-fft`: FFT window size (default `4096`).
- `--hop-length`: Hop length for STFT (default `1024`).
- `--margin-harmonic` / `--margin-percussive`: Control aggressiveness of the
  harmonic/percussive split.
- `--nn-filter-width`: Width of the nearest neighbour filter used for the vocal
  mask (must be odd).
- `--no-vocal-band`: Disable vocal band-pass filtering if the singer has
  significant energy outside the default 80–1100 Hz range.
- `--overwrite`: Overwrite existing output files.

The separated stems are written as 32-bit floating point WAV files named
`vocals.wav`, `drums.wav`, and `instruments.wav` inside the chosen output
folder.

## Programmatic API

Use the `StemSeparator` class from Python to integrate separation in other
applications:

```python
from stem_separator import StemSeparator

separator = StemSeparator(sample_rate=44100)
result = separator.separate("input_song.wav")

vocals = result.stems["vocals"]  # numpy array with shape (channels, samples)
```

You can call `result.to_files(Path("output"))` to save the stems later on.

## Limitations

This implementation relies on classical signal-processing techniques and does
not include a trained neural network model. While it performs well for many
tracks, extremely dense mixes or heavily processed vocals may benefit from
additional post-processing or the integration of machine-learning models.
