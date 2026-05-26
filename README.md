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

## Concept

The four MIDI files in `midi/` are **research material** — not source for a
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
| 1     | `src/extract_patterns.py`   | the MIDI                             | `docs/song_spec.yaml` (BPM, key, 1-bar rhythm grids, contour, chord roots) AND `docs/song_layers.yaml` (verbatim T5/T7/T11/T12 note lists + lyric markers) |
| 2     | `src/compose.py`            | spec + layers (no MIDI)              | `docs/composition.yaml` (sectioned event list) |
| 3     | `src/synth.py`              | composition only                     | `out/friet_clean.sid` (PSID v2) |

Set `MELODY_ONLY=1` before running compose to render the vocal alone (no
bass, no drums) — handy for verifying the melody is recognisable in
isolation. Set `FAST=1` to render the 175-BPM happy-hardcore release
variant from the same composition.

## Layout

```
friet/
├── README.md               this file
├── LICENSE.md              MIT for our code; fair-use note for the song
├── CHANGELOG.md            day-by-day record of major changes
├── AGENTS.md               notes for future AI sessions: pitfalls, gotchas
├── Makefile                make analyze | extract | compose | synth | preview-* | clean
├── midi/                   source MIDIs (karaoke transcriptions of FFD)
├── stems/                  per-track MIDI stems for inspecting individual parts
├── src/
│   ├── analyze_midi.py     dump per-track stems + textual analysis
│   ├── extract_patterns.py phase 1: MIDI -> docs/song_spec.yaml + song_layers.yaml
│   ├── compose.py          phase 2: spec + layers -> docs/composition.yaml
│   ├── synth.py            phase 3: composition -> out/friet_clean.sid
│   ├── lab.py              experimental composition sandbox (make lab)
│   ├── build_player.py     bundles SID + lyric ticker -> out/friet.prg
│   └── player/             KickAssembler source for the standalone .prg
├── docs/
│   ├── song_analysis.md    music theory: key/chords/structure (with sources)
│   ├── melody_analysis.md  phrase-by-phrase analysis of the T7 vocal
│   ├── song_spec.yaml      patterns: BPM, key, 1-bar rhythm grids, contour
│   ├── song_layers.yaml    verbatim T5 / T7 / T11 / T12 / T13 note lists
│   ├── melody_lyrics.yaml  every syllable aligned to its T7 pitch
│   ├── melody_understanding.md  canonical melody theory (why the FFD melody works)
│   ├── midi_sources.md     MIDI source comparison + provenance
│   ├── rhythm_research.md  drums/bass coupling research
│   ├── score_transcription.md  beat-by-beat 16th-grid transcription (ossh MIDI)
│   ├── voice_essence.md    DNA of each instrument layer (Pattern A/B engines)
│   └── polish_plan.md      remaining work, priority-ordered
├── tools/
│   └── render-preview.sh   headless vsid -> WAV -> MP3
├── out/                    generated .sid + .mp3 (gitignored .wav)
└── .venv/                  Python venv (mido, numpy, pyyaml) — gitignored
```

## Research docs

Five research documents capture the musicology work that informed the
arrangement decisions:

- **[`docs/melody_understanding.md`](docs/melody_understanding.md)** --
  canonical theory of why the FFD melody works: 4-pitch vocabulary, tresillo
  rhythm in Phrase A vs straight 8ths in Phrase B, chord colour underneath.
- **[`docs/midi_sources.md`](docs/midi_sources.md)** -- comparison of all
  five source MIDIs in `midi/`, what each contains, and which tracks are
  authoritative for which musical question.
- **[`docs/rhythm_research.md`](docs/rhythm_research.md)** -- analysis of
  the drums/bass coupling that gives FFD its dance-floor feel, and why the
  chorus tresillo must not be quantized.
- **[`docs/score_transcription.md`](docs/score_transcription.md)** --
  beat-by-beat 16th-grid transcription from the ossh MIDI
  (`Gala-freedfromdesire.mid`, 128.5 BPM, 15 tracks).
- **[`docs/voice_essence.md`](docs/voice_essence.md)** -- DNA of each
  instrument layer: the two rhythmic engines (Pattern A "4-3-3-4" organ stab,
  Pattern B "3-3-2" tresillo) and what each voice contributes.

## Source-MIDI map (verified against lyrics — see `docs/melody_analysis.md`)

| Track | Inst (GM)          | Range  | Role                                                        |
|-------|--------------------|--------|-------------------------------------------------------------|
| T2    | (lyric track)      | —      | Soft-Karaoke `\My love` etc., syllables aligned to T7 notes |
| T4    | BrtAcoust (1)      | D2–A4  | Piano comp (chord voicings, polyphony 5)                    |
| T5    | 5ths Bass (87)     | D2–F3  | **Iconic synth bassline riff**                              |
| T6    | Perc Organ (17)    | D4–D6  | Chord stabs — D arpeggio across 3 octaves                   |
| T7    | Oboe (68)          | A4–F5  | **Vocal melody substitute** (the singer)                    |
| T8    | Syn Strings (50)   | F3–F4  | String pad                                                  |
| T9    | Strings (48)       | D6–D7  | High strings countermelody                                  |
| T10   | Halo Pad (95)      | D4–D5  | Pad                                                         |
| T11   | Saw Lead (81)      | D3–F3  | **Chorus "na-na" hook** (instrumental break, 92–124s)       |
| T12   | Reverse Cymbal (119)| A2    | **Intro noise swell** (beat 5 + section transitions)        |
| T13   | drumkit            | —      | Kick, snare, clap, hats, tambourine, maracas                |

We verified T7 IS the sung melody by aligning T2's syllable markers to T7's
note positions: every "Freed", "from", "de", "si", "re" lyric event lands
exactly on the corresponding F5, F5, D5, D5, C5 in T7.

## Build

```sh
source .venv/bin/activate

# Release build (175 BPM, hoover lead — this is the final track):
make friet                          # -> out/friet.sid
make preview-friet                  # -> out/friet.mp3

# Standalone C64 .prg with lyric ticker (embeds out/friet.sid):
make player                         # -> out/friet.prg

# Workstages — useful for shaving the arrangement without remixing the
# whole thing:
make extract compose synth          # -> out/friet_clean.sid (130 BPM workstage)
make preview-clean                  # -> out/friet_clean.mp3
make melody-only preview-melody     # -> out/friet_melody_only.{sid,mp3} (vocal only)

# Everything at once:
make preview                        # render all .mp3 previews

# Research:
make analyze                        # dump per-track stems + a textual report

# Lab sandbox — experimental composition playground:
make lab                            # -> out/lab.sid + out/lab.mp3 (src/lab.py)
```

Listen interactively: `vsid out/friet.sid`.

## Tools required

- `xa` — Andre Fachat's 6502 cross-assembler (with `-XMASM` flag to allow `:` in comments)
- `vsid` from VICE (uses C64 ROMs at `/usr/share/vice/C64/`)
- Python venv with `mido` (and `numpy` for FFT analysis)
- `ffmpeg` to convert raw vsid output → MP3

Note: `sidplayfp` is *broken* on the development box (reports "Not enough
memory" for every SID regardless of file). `vsid` works fine.

## Copyright / Fair use

See [LICENSE.md](LICENSE.md). In short: MIT for our code; the underlying
composition is © 1996 Gala Rizzatto / Maurizio Molella / Filippo Carmeni;
the karaoke MIDIs are someone else's transcriptions; this repo is a
transformative fan/educational remix with no commercial intent. If you
are a rights-holder and object, open an issue and we'll remove it.

## Status

- ✅ **Melody recognisable** as "Freed from Desire" — T7 vocal verbatim
  with per-section waveform + interleaving bass + section-filtered drums.
- ✅ **Interleaving bass** — V1 plays T6 grid positions (0, 1, 1.75, 2.5,
  3.5 beats per bar) computed per output bar so the bass **never collides
  with any vocal note**. D2 pedal. Silent in intro/breathes. Call-and-response
  with the vocal melody.
- ✅ **Per-section V2 waveform** — triangle in verse, sawtooth+hoover in
  chorus, pulse in final reprise. Vibrato ±12.
- ✅ **T13 verbatim drums** — section-filtered (verse=kick, prechorus=kick+snare,
  chorus=full kit). Snare fills in breathe sections. Hat boost in chorus2/3.
  Crash swell with long attack ($D), dark pitch (28), 4s gate.
- ✅ Lyrics aligned to T7 notes (every syllable has a verified pitch in
  `docs/song_layers.yaml` and `docs/melody_lyrics.yaml`).
- ✅ **Lab sandbox** — `src/lab.py` / `make lab` for experimental
  composition work; separate from the release pipeline.
- ✅ **All polish items complete** — vibrato, filter LFO, reprise dynamics,
  TL-Buis Dutch lyrics in the `.prg` ticker. See `docs/polish_plan.md`.
- ✅ **Standalone .prg player** — `out/friet.prg` embeds the SID + a
  scrolling lyric ticker with TL-Buis Dutch parody text (48 lines).
- ✅ **Score transcription + voice essence docs** — full ossh MIDI analysis
  in `docs/score_transcription.md` and `docs/voice_essence.md`.
- Pads / chord rendering with only 3 voices remains unsolved — V3 is
  drums only. Possible future work: ring-modulate V1 against V3 for
  "chord shimmer".
