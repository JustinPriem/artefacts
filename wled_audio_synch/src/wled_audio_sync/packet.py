"""Aufbau des WLED Audio-Sync UDP-Pakets (Format "00002").

Referenz (WLED audio_reactive usermod, audioSyncPacket struct):
    char    header[6];       // "00002" + Nullbyte
    uint8_t myVals[32];      // veraltet, historische Kompatibilitaet -> 0
    float   sampleAgc;
    float   sampleRaw;
    float   sampleAvg;
    float   samplePeak;      // 0.0 oder 1.0
    uint8_t frameCounter;
    uint8_t fftResult[16];   // 16 Frequenzbaender, je 0-255
    float   FFT_Magnitude;
    float   FFT_MajorPeak;

Hinweis: Das Paketformat kann sich zwischen WLED-Versionen leicht
unterscheiden (z.B. aeltere Firmware nutzt Header "00001"). Siehe
README.md -> Troubleshooting, falls die Strips nicht reagieren.
"""

import struct

PACKET_FORMAT = "<6s32sffffB16sff"
HEADER = b"00002\x00"
NUM_FFT_BINS = 16


def build_packet(
    sample_agc: float,
    sample_raw: float,
    sample_avg: float,
    sample_peak: float,
    frame_counter: int,
    fft_bins,
    fft_magnitude: float,
    fft_major_peak: float,
) -> bytes:
    my_vals = bytes(32)  # veraltetes Feld, wird von aktuellem WLED ignoriert
    fft_bytes = bytes(int(max(0, min(255, b))) for b in fft_bins)
    if len(fft_bytes) != NUM_FFT_BINS:
        fft_bytes = fft_bytes.ljust(NUM_FFT_BINS, b"\x00")[:NUM_FFT_BINS]

    return struct.pack(
        PACKET_FORMAT,
        HEADER,
        my_vals,
        float(sample_agc),
        float(sample_raw),
        float(sample_avg),
        float(sample_peak),
        frame_counter & 0xFF,
        fft_bytes,
        float(fft_magnitude),
        float(fft_major_peak),
    )
