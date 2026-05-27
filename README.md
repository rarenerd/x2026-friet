# Friet met Desire

A Commodore 64 SID remix of Gala's "Freed from Desire" (1996), released by
**deFEEST** at the **X2026** demoparty. Composed by
**Kloot/deFEEST** (Claude), **Augurk/deFEEST** (Big Pickle / OpenCode),
and **Anus/deFEEST** ([annejan](https://github.com/annejan)). Companion demo:
[`outline26-claude-c64`](https://github.com/annejan/outline26-claude-c64)
("Kloten met de broodtrommel").

**Friet** is Dutch for fries — the title is a playful misreading of
"Freed". See [`docs/RELEASE.md`](docs/RELEASE.md) for the scene-release
metadata.

**Repo:** [github.com/annejan/friet-met-desire](https://github.com/annejan/friet-met-desire)

## Concept

The five MIDI files in `midi/` are **research material** — not source for a
direct transcription. They're studied for their patterns (drum grooves,
bassline rhythm, melodic contours, chord progressions). The output SIDs are
*remixes* that take those patterns and re-arrange them for the C64's 3-voice
SID chip in a happy-hardcore style.

### Pipeline

The build is a three-stage extract → compose → synth chain. Each stage
writes a YAML file the next stage reads, so a tweak at one level doesn't
require redoing the others.

```
midi/*.mid  ──>  extract_patterns.py  ──>  docs/song_spec.yaml    (patterns)
                                       \──>  docs/song_layers.yaml (verbatim notes)
                                                  │
                                                  ▼
                                            compose.py  ──>  docs/composition.yaml
                                                                       │
                                                                       ▼
                                                                 synth.py  ──>  out/friet_clean.sid
```

| Phase | Tool                        | Reads                                | Writes              |
|-------|-----------------------------|--------------------------------------|---------------------|
| 1     | `src/extract_patterns.py`   | the MIDI                             | `docs/song_spec.yaml` + `docs/song_layers.yaml` (verbatim note lists + organ + lyric markers) |
| 2     | `src/compose.py`            | spec + layers (no MIDI)              | `docs/composition.yaml` (sectioned event list) |
| 3     | `src/synth.py`              | composition only                     | `out/friet_clean.sid` (PSID v2) |

## Voice assignment

All three voices play **verbatim source data** — no synthetic patterns.
V1 switches role per section, matching the original production:

| Section | V1 | V2 | V3 |
|---------|----|----|-----|
| Intro | (silent — crash swell on V3) | — | T12 swell + T13 sparse |
| Verse | **T6 organ stab** (D-pedal, composed with the vocal) | T7 vocal (triangle) | T13 kick-only |
| Pre-chorus | T6 organ stab continues | T7 vocal (triangle) | T13 kick+snare |
| Chorus 1 | T6 organ stab (T5 barely present) | T7 vocal (sawtooth + hoover) | T13 full kit |
| Na-na | **T5 bass tresillo** (the groove shift) | T7 vocal (sawtooth) | T13 full kit |
| Chorus 2/3 | T5 bass from na-na range | T7 vocal (pulse in finale) | T13 + snare fills + hat boost |

SID production tricks:
- **PWM sweep** on V1 bass (~$0180/frame cycling $000–$FFF) for chorus-like movement
- **Kick pitch-sweep**: 2 frames triangle at high pitch → noise body (real thump)
- **Vibrato** ±12 SID-freq units on V2 (~3 Hz)
- **Filter LP** with hoover sweep ($E0→$80 per note) on V2, resonance $6
- **Bresenham frame grid** (30/7 integer accumulation) for drift-free timing

## Layout

```
friet/
├── README.md               this file
├── LICENSE.md              MIT for our code; fair-use note for the song
├── CHANGELOG.md            day-by-day record of major changes
├── AGENTS.md               notes for future AI sessions: pitfalls, gotchas
├── Makefile                all build targets
├── midi/                   5 source MIDIs (karaoke + ossh + AUD transcriptions)
├── stems/                  per-track MIDI stems (role-named: vocal.mid, bass.mid, etc.)
├── src/
│   ├── analyze_midi.py     dump per-track stems + textual analysis
│   ├── extract_patterns.py phase 1: MIDI → song_spec + song_layers
│   ├── compose.py          phase 2: layers → composition (per-section V1 switching)
│   ├── synth.py            phase 3: composition → PSID (PWM sweep, kick pitch-sweep)
│   ├── lab.py              experimental composition sandbox (make lab)
│   ├── build_player.py     bundles SID + lyric ticker → out/friet.prg
│   └── player/             KickAssembler source for the standalone .prg
├── docs/
│   ├── melody_understanding.md  canonical melody theory
│   ├── voice_essence.md         DNA of each instrument (Pattern A/B engines)
│   ├── score_transcription.md   beat-by-beat 16th-grid (ossh MIDI)
│   ├── sheet_music.md           bladmuziek voor zangers + muzikanten
│   ├── lyric_writing_guide.md   rhythm templates for writing lyrics
│   ├── lyrics_melody_harmony.md combined lyrics × melody × chord analysis
│   ├── lyrics.md                TL-Buis Dutch parody lyrics (work in progress)
│   ├── midi_sources.md          5-MIDI comparison + provenance
│   ├── rhythm_research.md       drums/bass coupling research
│   ├── song_analysis.md         music theory: key/chords/structure
│   ├── melody_analysis.md       phrase-by-phrase T7 vocal analysis
│   ├── tl_buis_lyrics.yaml      lyric timing for the .prg ticker
│   ├── polish_plan.md           completed work log
│   └── RELEASE.md               scene-release metadata
├── tools/
│   └── render-preview.sh   headless vsid → WAV → MP3
├── out/                    generated deliverables
└── .venv/                  Python venv (mido, numpy, pyyaml)
```

## Build

```sh
source .venv/bin/activate

# Release build (175 BPM — this is the final track):
make friet                          # → out/friet.sid
make preview-friet                  # → out/friet.mp3

# Standalone C64 .prg with lyric ticker:
make player                         # → out/friet.prg

# Competition SID (HVSC-ready, scene-standard filename):
make compo                          # → out/Friet_met_Desire-deFEEST.sid

# Workstages:
make extract compose synth          # → out/friet_clean.sid (130 BPM)
make melody-only preview-melody     # → vocal only

# Lab sandbox:
make lab                            # → out/lab.sid + out/lab.mp3

# Research:
make analyze                        # dump per-track stems
```

Listen interactively: `vsid out/friet.sid`.

## Research docs

Seven research documents capture the musicology work:

- **[melody_understanding.md](docs/melody_understanding.md)** — 4-pitch
  vocabulary, tresillo vs straight 8ths, chord colour.
- **[voice_essence.md](docs/voice_essence.md)** — Pattern A (organ stab)
  and Pattern B (tresillo bass): the two rhythmic engines.
- **[score_transcription.md](docs/score_transcription.md)** — bar-by-bar
  16th-grid from the ossh MIDI (128.5 BPM, 15 tracks).
- **[sheet_music.md](docs/sheet_music.md)** — bladmuziek for singers and
  musicians with note values (staccato 16ths + held 8th accents).
- **[lyric_writing_guide.md](docs/lyric_writing_guide.md)** — rhythm
  templates per phrase for writing lyrics in any language.
- **[midi_sources.md](docs/midi_sources.md)** — comparison of all 5 MIDIs.
- **[rhythm_research.md](docs/rhythm_research.md)** — drums/bass coupling
  and why the chorus tresillo must not be quantized.

## Tools required

- `xa` — 6502 cross-assembler (with `-XMASM` for `:` in comments)
- `vsid` from VICE (C64 ROMs at `/usr/share/vice/C64/`)
- Python venv with `mido`, `numpy`
- `ffmpeg` for WAV → MP3
- KickAssembler for the .prg player

Note: `sidplayfp` is broken on the dev box. Use `vsid`.

## Copyright / Fair use

See [LICENSE.md](LICENSE.md). MIT for our code; the underlying
composition is © 1996 Gala Rizzatto / Maurizio Molella / Filippo Carmeni;
the karaoke MIDIs are someone else's transcriptions; this repo is a
transformative fan/educational remix with no commercial intent.
