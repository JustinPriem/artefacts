"""Audioerfassung (WASAPI-Loopback) und FFT/Frequenzband-Analyse."""

import numpy as np
import soundcard as sc


def get_loopback_microphone():
    """Liefert das Loopback-'Mikrofon' fuer den aktuellen Standard-Lautsprecher
    (faengt also alles ab, was gerade aus Windows rausgeht -- Rekordbox,
    Serato, Spotify, ...)."""
    speaker = sc.default_speaker()
    return sc.get_microphone(speaker.name, include_loopback=True)


def compute_fft_bins(samples: np.ndarray, sample_rate: int, num_bins: int, gain: float):
    """Teilt das Spektrum in `num_bins` logarithmisch verteilte Baender auf
    (tiefe Frequenzen schmaler, hohe breiter -- entspricht menschlichem
    Hoerempfinden und dem, was WLEDs GEQ-Effekt erwartet).

    Rueckgabe: (bins[0..255], magnitude, major_peak_freq_hz)
    """
    window = np.hanning(len(samples))
    spectrum = np.abs(np.fft.rfft(samples * window))
    freqs = np.fft.rfftfreq(len(samples), d=1.0 / sample_rate)

    # Bandgrenzen 60 Hz - 8000 Hz, logarithmisch (typischer Musik-relevanter Bereich)
    band_edges = np.logspace(np.log10(60), np.log10(8000), num_bins + 1)

    bins = np.zeros(num_bins)
    for i in range(num_bins):
        mask = (freqs >= band_edges[i]) & (freqs < band_edges[i + 1])
        if np.any(mask):
            bins[i] = spectrum[mask].mean()

    bins = np.clip(bins * gain, 0, 255)

    major_peak_freq = float(freqs[np.argmax(spectrum)]) if len(spectrum) else 0.0
    magnitude = float(spectrum.max()) if len(spectrum) else 0.0

    return bins, magnitude, major_peak_freq
