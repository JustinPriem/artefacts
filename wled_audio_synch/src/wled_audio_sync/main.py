"""Einstiegspunkt: Audio erfassen -> analysieren -> per UDP an WLED senden.

Aufruf:
    python -m wled_audio_sync.main
"""

import socket
import sys
import time

import numpy as np

from .audio import compute_fft_bins, get_loopback_microphone
from .config import load_config
from .packet import build_packet


def main() -> None:
    try:
        config = load_config()
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)

    try:
        mic = get_loopback_microphone()
    except Exception as exc:
        print("Konnte kein Loopback-Geraet finden:", exc)
        print("Pruefe, ob 'Stereo Mix' / WASAPI-Loopback in Windows verfuegbar ist.")
        sys.exit(1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    frame_counter = 0
    last_peak_time = 0.0
    running_avg = 0.0

    print(f"Sende Audio-Sync an {config.wled_ip}:{config.wled_port} ... (Strg+C zum Beenden)")

    with mic.recorder(
        samplerate=config.sample_rate, channels=1, blocksize=config.block_size
    ) as rec:
        while True:
            data = rec.record(numframes=config.block_size).flatten()

            rms = float(np.sqrt(np.mean(data**2)))
            sample_raw = min(255.0, rms * config.gain * 255.0)
            running_avg = running_avg * 0.9 + sample_raw * 0.1
            sample_agc = sample_raw  # ohne echtes AGC: 1:1, WLED regelt intern nach

            now = time.time()
            is_peak = 0.0
            if rms > config.peak_threshold and (now - last_peak_time) * 1000 > config.peak_hold_ms:
                is_peak = 1.0
                last_peak_time = now

            fft_bins, magnitude, major_peak = compute_fft_bins(
                data, config.sample_rate, config.num_fft_bins, config.gain
            )

            packet = build_packet(
                sample_agc=sample_agc,
                sample_raw=sample_raw,
                sample_avg=running_avg,
                sample_peak=is_peak,
                frame_counter=frame_counter,
                fft_bins=fft_bins,
                fft_magnitude=magnitude,
                fft_major_peak=major_peak,
            )
            sock.sendto(packet, (config.wled_ip, config.wled_port))
            frame_counter += 1


if __name__ == "__main__":
    main()
