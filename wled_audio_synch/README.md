# wled_audio_synch

Erfasst den PC-Sound-Output (WASAPI-Loopback, z.B. Master-Out von Rekordbox/Serato)
und sendet daraus per **WLED Audio-Sync-UDP-Protokoll** Lautstaerke-, Peak- und
16-Band-Frequenzdaten an einen ESP32 mit WLED. WLEDs eigene Sound-Reactive-Effekte
(GEQ, Freqmap, DJ Light, ...) laufen dann pro Segment darauf.

## Setup

### 1. Python-Umgebung

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

(Alternativ: `pip install -e .` nutzt die Abhaengigkeiten aus `pyproject.toml`.)

### 2. Konfiguration

```bash
copy config.example.ini config.ini      # Windows
```

`config.ini` oeffnen und `wled.ip` auf die IP deines ESP32 setzen (WLED-Web-UI
&rarr; *Info*). `config.ini` ist in `.gitignore` und wird nicht eingecheckt.

### 3. WLED vorbereiten (Web-UI, `http://<ESP32-IP>/`)

- **Config &rarr; Sync Interfaces &rarr; "UDP Sound Sync"**: *Receive Audio Data* aktivieren
- **Sound Settings**: *Audio Source* auf `UDP Sound Sync` stellen
- Deine 3 Segmente (LED 0-31 / 32-63 / 64-95) anlegen, falls noch nicht geschehen,
  und jedem ein Sound-Reactive-Preset zuweisen (z.B. GEQ, Freqmap, DJ Light)

### 4. Starten

```bash
python -m wled_audio_sync.main
```

Dann Musik abspielen und pruefen, ob die Strips reagieren. Mit `Strg+C` beenden.

## Projektstruktur

```
wled_audio_synch/
├── config.example.ini      # Vorlage, kopieren zu config.ini
├── requirements.txt
├── pyproject.toml
└── src/wled_audio_sync/
    ├── config.py            # laedt config.ini
    ├── packet.py            # baut das WLED-Audio-Sync-UDP-Paket
    ├── audio.py              # Loopback-Capture + FFT/Frequenzband-Analyse
    └── main.py                # Einstiegspunkt / Hauptschleife
```

## Troubleshooting

**Strips reagieren gar nicht:**
- WLED &rarr; Config &rarr; Sync Interfaces &rarr; "UDP Sound Sync" &rarr; *Receive Audio Data* an?
- WLED &rarr; Sound Settings &rarr; *Audio Source* auf `UDP Sound Sync`?
- Windows-Firewall blockiert evtl. ausgehendes UDP auf Port 11988 &rarr; testweise
  fuer Python zulassen
- IP in `config.ini` korrekt? (WLED-Web-UI &rarr; Info)

**Strips reagieren komisch/zufaellig (Paketformat evtl. nicht exakt passend):**
Das Paketformat hat sich zwischen WLED-Versionen leicht veraendert (Header
`"00002"` vs. `"00001"`, teils andere Feldreihenfolge). In `src/wled_audio_sync/packet.py`
den `HEADER`-Wert testweise auf `b"00001\x00"` aendern, oder die genaue
WLED-Firmware-Version (Web-UI &rarr; Info) nachschauen und das struct danach
exakt abgleichen.

**Reaktion zu schwach/zu stark:**
In `config.ini` unter `[audio]`: `gain` erhoehen = empfindlicher. `peak_threshold`
senken = mehr erkannte Beats, erhoehen = weniger/praeziser.

**Kein Sound wird erfasst / Fehler beim Start:**
Windows: Rechtsklick auf Lautsprecher-Symbol &rarr; Sounds &rarr; Aufnahme &rarr; pruefen,
ob "Stereo Mix" existiert und aktiviert ist (ggf. Rechtsklick &rarr; "Deaktivierte
Geraete anzeigen"). Das `soundcard`-Paket nutzt normalerweise WASAPI-Loopback
automatisch, ganz ohne Stereo Mix noetig.

## Naechste Ausbaustufen

- MIDI-Hotcue-Trigger vom DDJ-FLX4 fuer manuelle Szenenwechsel (Strobo etc.)
  kombiniert mit dem Audio-Sync-Stream
- Feineres Beat-/Drop-Erkennung fuer automatische Szenenwechsel
