"""Konfiguration wird aus config.ini geladen (siehe config.example.ini).

config.ini liegt NICHT im Git-Repo (steht in .gitignore), da sie deine
lokale ESP32-IP enthaelt. Beim ersten Start config.example.ini nach
config.ini kopieren und anpassen.
"""

import configparser
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config.ini"
EXAMPLE_CONFIG_PATH = PROJECT_ROOT / "config.example.ini"


@dataclass
class Config:
    wled_ip: str
    wled_port: int
    sample_rate: int
    block_size: int
    num_fft_bins: int
    gain: float
    peak_threshold: float
    peak_hold_ms: int


def load_config(path: Path = CONFIG_PATH) -> Config:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} nicht gefunden. Kopiere {EXAMPLE_CONFIG_PATH.name} zu "
            f"{path.name} und trage deine WLED-IP ein."
        )

    parser = configparser.ConfigParser()
    parser.read(path)
    wled = parser["wled"]
    audio = parser["audio"]

    return Config(
        wled_ip=wled.get("ip"),
        wled_port=wled.getint("port", fallback=11988),
        sample_rate=audio.getint("sample_rate", fallback=44100),
        block_size=audio.getint("block_size", fallback=1024),
        num_fft_bins=audio.getint("num_fft_bins", fallback=16),
        gain=audio.getfloat("gain", fallback=30.0),
        peak_threshold=audio.getfloat("peak_threshold", fallback=0.35),
        peak_hold_ms=audio.getint("peak_hold_ms", fallback=100),
    )
