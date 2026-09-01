# Projekt-Übergabe: DDJ-FLX4 + WLED Musiksteuerung

Diese Datei fasst zusammen, was bisher besprochen und gebaut wurde, damit eine
neue Claude-Code-Session (lokal auf dem PC) nahtlos weitermachen kann.

## Ausgangssituation / Ziel
- Hardware: Pioneer **DDJ-FLX4** (DJ-Controller, läuft mit Serato oder Rekordbox),
  ein **ESP32** mit **WLED**-Firmware, ein LED-Streifen mit 96 LEDs, im WLED-Web-UI
  in **3 Segmente** aufgeteilt (fungieren wie 3 "virtuelle" Strips).
- WLED-Web-UI erreichbar unter `http://192.168.178.140/`.
- Übergeordnetes Ziel: Die LED-Beleuchtung soll auf Musik reagieren (Farbwechsel,
  Sound-Reactive-Effekte, perspektivisch auch geplante Effekte wie Strobo beim
  Drop, per Hotcues/MIDI vom FLX4 getriggert).

## Erarbeitete Lösungsrichtung
Mehrere Ansätze wurden durchgesprochen, die aktuell gewählte Richtung:

1. **Kein physisches Mikrofon am ESP32.** Stattdessen wird der **PC-Sound
   direkt per Software abgegriffen** (WASAPI-Loopback unter Windows – erfasst,
   was aus dem PC rauskommt, z.B. den Master-Out von Rekordbox/Serato, ganz
   ohne Kabel).
2. Ein **selbstgeschriebenes Python-Skript** macht daraus:
   - RMS/Lautstärke-Berechnung
   - Peak-/Beat-Erkennung
   - 16-Band-FFT (logarithmisch verteilt, 60 Hz – 8000 Hz), damit Effekte
     zwischen Bass und Höhen unterscheiden können (nicht nur Gesamtlautstärke)
3. Die Werte werden im **WLED "Audio Sync" UDP-Protokoll** (Port 11988,
   Paketformat `"00002"`) an den ESP32 gesendet. WLED denkt dann, es hätte
   selbst ein Mikrofon gehört, und wendet seine eingebauten Sound-Reactive-
   Effekte (GEQ, Freqmap, DJ Light, ...) **pro Segment** an – das Skript muss
   sich NICHT um einzelne LEDs kümmern, WLEDs Segment-Logik übernimmt das.
4. Spätere Ausbaustufe (noch nicht umgesetzt): Hotcues am FLX4 vorab pro Track
   an Übergängen setzen (ruhiger Part / Drop), per MIDI-Listener-Skript auf
   WLED-Presets mappen (z.B. "Atmen"-Preset vs. "Strobo"-Preset), um gezielt
   geplante Lichtwechsel zu triggern statt nur audio-reaktiv zu fahren.

## Was technisch schon gebaut ist
Projektordner `wled_audio_synch/` (liegt im Repo `justinpriem/artefacts`,
Branch `claude/ddj-flx4-wled-sync-uw0j2m`):

```
wled_audio_synch/
├── config.example.ini      # Vorlage; ip bereits auf 192.168.178.140 gesetzt
├── requirements.txt         # soundcard, numpy
├── pyproject.toml
├── README.md                 # Setup- & Troubleshooting-Anleitung
├── HANDOFF.md                 # diese Datei
└── src/wled_audio_sync/
    ├── config.py              # lädt config.ini
    ├── packet.py               # baut das WLED-Audio-Sync-UDP-Paket
    ├── audio.py                 # WASAPI-Loopback-Capture + FFT-Analyse
    └── main.py                   # Hauptschleife (Capture -> Analyse -> UDP send)
```

`config.ini` selbst ist **nicht** im Repo (steht in `.gitignore`) – muss lokal
aus `config.example.ini` kopiert werden.

**Noch nicht getestet:** Das Skript wurde bisher nicht real gegen die
WLED-Hardware verifiziert. Insbesondere das genaue Byte-Layout des
Audio-Sync-Pakets (`packet.py`) kann je nach installierter WLED-
Firmware-Version leicht abweichen (Header `"00002"` vs. ältere `"00001"`-
Variante) – siehe Troubleshooting-Abschnitt in `README.md`.

## Offene Punkte / nächste Schritte
1. **Lokales Setup fertigstellen** (aktuell hängengeblieben): Repo lokal
   klonen/pullen, venv **innerhalb** des Projektordners `wled_audio_synch`
   anlegen (nicht im Home-Verzeichnis!), `pip install -r requirements.txt`,
   `config.ini` aus der Vorlage kopieren.
2. **WLED-Einstellungen prüfen** (im Web-UI `http://192.168.178.140/`):
   - Config → Sync Interfaces → "UDP Sound Sync" → *Receive Audio Data* an
   - Sound Settings → *Audio Source* = `UDP Sound Sync`
   - Die 3 Segmente je mit einem Sound-Reactive-Effekt belegen (GEQ, Freqmap,
     DJ Light zum Test)
3. **Erster Testlauf**: `python -m wled_audio_sync.main`, Musik abspielen,
   prüfen ob die Strips reagieren.
4. **Falls keine/falsche Reaktion**: Paketformat in `packet.py` gegen die
   tatsächliche WLED-Firmware-Version abgleichen (Version steht im Web-UI
   unter "Info").
5. **Feintuning**: `gain`, `peak_threshold`, `peak_hold_ms` in `config.ini`
   anpassen, bis Empfindlichkeit passt.
6. **Ausbaustufe (später)**: MIDI-Hotcue-Listener für den DDJ-FLX4 bauen, der
   parallel zum Audio-Sync-Stream läuft und auf Pad-Presses WLED-Presets
   aufruft (für geplante Effekte wie Strobo beim Drop).

## Kontext zur Umgebung
Das bisherige Setup wurde in einer **Cloud-Sandbox-Session** (Claude Code auf
claude.ai, kein lokaler Rechnerzugriff) erstellt und per `git push` ins Repo
gebracht. Für die weitere Arbeit direkt am PC (venv, Testlauf, Debugging mit
echter Hardware) wird eine **lokale** Claude-Code-Session im Ordner
`wled_audio_synch` empfohlen, da diese Sandbox keinen Zugriff auf den PC oder
das lokale WLAN/WLED-Gerät hat.
