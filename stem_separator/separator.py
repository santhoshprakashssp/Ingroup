"""Core functionality for separating audio stems."""
from __future__ import annotations

import dataclasses
import math
import pathlib
from typing import Dict, Iterable, Optional

import numpy as np
import soundfile as sf
import librosa


@dataclasses.dataclass
class SeparationResult:
    """Container for the separated stems.

    Attributes
    ----------
    sample_rate:
        Sample rate used for the separated audio data.
    stems:
        Mapping of stem name to an ``np.ndarray`` with shape ``(channels, samples)``.
    input_path:
        The path to the source audio file.
    output_directory:
        Directory where stems were written, if requested.
    """

    sample_rate: int
    stems: Dict[str, np.ndarray]
    input_path: pathlib.Path
    output_directory: Optional[pathlib.Path] = None

    def to_files(self, directory: pathlib.Path, *, overwrite: bool = False) -> None:
        """Write the separated stems to *directory*.

        Parameters
        ----------
        directory:
            Target directory for the rendered stems.
        overwrite:
            If ``True`` existing files will be replaced. By default, writing will
            fail when a file already exists.
        """

        directory.mkdir(parents=True, exist_ok=True)
        for stem_name, audio in self.stems.items():
            path = directory / f"{stem_name}.wav"
            if path.exists() and not overwrite:
                raise FileExistsError(f"File already exists: {path}")
            _write_audio(path, audio, self.sample_rate)
        self.output_directory = directory


class StemSeparator:
    """Separate a full mix into individual stems.

    The separator is based on spectral masking techniques using a combination of
    harmonic-percussive source separation and nearest-neighbour filtering. While
    it does not replace heavy neural networks, the method is lightweight and
    works well for a wide range of pop and rock material.
    """

    def __init__(
        self,
        *,
        sample_rate: int = 44100,
        n_fft: int = 4096,
        hop_length: int = 1024,
        margin_harmonic: float = 1.0,
        margin_percussive: float = 1.0,
        nn_filter_width: int = 31,
        vocal_band: Optional[Iterable[float]] = (80.0, 1100.0),
    ) -> None:
        if nn_filter_width % 2 == 0:
            raise ValueError("nn_filter_width must be an odd integer")
        if margin_harmonic <= 0 or margin_percussive <= 0:
            raise ValueError("margins must be positive values")
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.margin_harmonic = margin_harmonic
        self.margin_percussive = margin_percussive
        self.nn_filter_width = nn_filter_width
        self.vocal_band = tuple(vocal_band) if vocal_band is not None else None

    def separate(
        self,
        input_path: pathlib.Path | str,
        *,
        output_directory: Optional[pathlib.Path | str] = None,
        overwrite: bool = False,
    ) -> SeparationResult:
        """Separate *input_path* into vocal, drum and instrument stems."""

        input_path = pathlib.Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(input_path)

        audio, _ = librosa.load(input_path.as_posix(), sr=self.sample_rate, mono=False)
        if audio.ndim == 1:
            audio = audio[np.newaxis, :]
        audio = np.asarray(audio, dtype=np.float32)

        masks = self._create_masks(audio)

        stems: Dict[str, np.ndarray] = {}
        for stem_name, mask in masks.items():
            stems[stem_name] = self._apply_mask(audio, mask)

        result = SeparationResult(
            sample_rate=self.sample_rate,
            stems=stems,
            input_path=input_path,
        )

        if output_directory is not None:
            output_directory = pathlib.Path(output_directory)
            result.to_files(output_directory, overwrite=overwrite)

        return result

    # ------------------------------------------------------------------
    def _create_masks(self, audio: np.ndarray) -> Dict[str, np.ndarray]:
        mono_mix = audio.mean(axis=0)
        stft_mix = librosa.stft(mono_mix, n_fft=self.n_fft, hop_length=self.hop_length)
        magnitude = np.abs(stft_mix)

        harm, perc = librosa.decompose.hpss(
            magnitude,
            kernel_size=(
                self._auto_kernel_size(self.margin_harmonic),
                self._auto_kernel_size(self.margin_percussive),
            ),
            margin=(self.margin_harmonic, self.margin_percussive),
            power=2.0,
        )

        # Foreground estimation for vocals using nearest neighbour filtering.
        filter_width = self.nn_filter_width
        harmonic_background = librosa.decompose.nn_filter(
            harm,
            aggregate=np.median,
            metric="cosine",
            width=filter_width,
        )
        harmonic_background = np.minimum(harm, harmonic_background)
        vocal_foreground = np.maximum(harm - harmonic_background, 0.0)

        if self.vocal_band is not None:
            vocal_mask_band = self._bandpass_mask(harm.shape[0])
            vocal_foreground *= vocal_mask_band
            harmonic_background *= 1.0 - vocal_mask_band

        eps = np.finfo(np.float32).eps
        total = harm + perc + eps
        harmonic_mask = harm / total
        percussive_mask = perc / total

        background_total = harmonic_background + vocal_foreground + eps
        vocal_mask = vocal_foreground / background_total
        instrument_mask = harmonic_background / background_total

        masks = {
            "drums": np.clip(percussive_mask, 0.0, 1.0),
            "vocals": np.clip(vocal_mask * harmonic_mask, 0.0, 1.0),
            "instruments": np.clip(instrument_mask * harmonic_mask, 0.0, 1.0),
        }
        return masks

    def _apply_mask(self, audio: np.ndarray, mask: np.ndarray) -> np.ndarray:
        stems = []
        for channel in audio:
            stft_channel = librosa.stft(
                channel, n_fft=self.n_fft, hop_length=self.hop_length
            )
            separated = mask * stft_channel
            signal = librosa.istft(
                separated, hop_length=self.hop_length, length=audio.shape[1]
            )
            stems.append(signal)
        stem_audio = np.vstack(stems)
        return stem_audio

    def _bandpass_mask(self, bins: int) -> np.ndarray:
        nyquist = self.sample_rate / 2
        freqs = np.linspace(0.0, nyquist, bins)
        low, high = self.vocal_band or (0.0, nyquist)
        band_mask = np.zeros_like(freqs)
        band_mask[(freqs >= low) & (freqs <= high)] = 1.0
        return band_mask[:, np.newaxis]

    @staticmethod
    def _auto_kernel_size(margin: float) -> int:
        base = 17
        return int(base * (1 + math.log1p(margin))) | 1  # ensure odd integer


def _write_audio(path: pathlib.Path, audio: np.ndarray, sample_rate: int) -> None:
    audio = audio.T  # shape -> (samples, channels)
    audio = np.asarray(audio, dtype=np.float32)
    peak = np.max(np.abs(audio))
    if peak > 1.0:
        audio = audio / peak
    sf.write(path.as_posix(), audio, sample_rate)
