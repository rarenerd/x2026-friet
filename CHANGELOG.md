# Changelog

All notable changes to **Friet met Desire** are recorded here.
Dates are local (Europe/Amsterdam).

## 2026-05-26 — Verbatim source layers, per-section waveform, interleaving bass

- **Back to verbatim source layers**: V2 plays T7 vocal verbatim, V3 plays
  T13 drums verbatim (section-filtered). No more synthetic HH patterns —
  the real source data is richer.
- **Per-section V2 waveform**: triangle in verse, sawtooth+hoover in chorus,
  pulse in final reprise. Each section has its own timbre character.
- **Interleaving bass**: V1 plays T6 grid positions (0, 1, 1.75, 2.5, 3.5
  beats per bar) computed per output bar so the bass **never collides with
  any V2 vocal note**. D2 pedal. Silent in intro/breathes. Call-and-response
  with the vocal — zero collisions per bar.
- **V3 section filtering**: verse=kick only, prechorus=kick+snare,
  chorus=full kit. Snare fills in breathe sections. Hat boost (8th on+off)
  in chorus2/3. Crash swell: long attack ($D), dark pitch (28), 4s gate.
- **ossh MIDI analysis**: added `Gala-freedfromdesire.mid` (128.5 BPM,
  15 tracks, 473 vocal notes). Full score transcription
  (`docs/score_transcription.md`) and voice essence (`docs/voice_essence.md`)
  documenting Pattern A (4-3-3-4) and Pattern B (3-3-2) engines.
- **Multiple source MIDIs analyzed**: karaoke, ossh, AUD_HO1152, AUD_RC5718.

## 2026-05-25 — Timbre polish, repo cleanup

- **Timbre tweaks**: V1 bass pulse width narrowed to 25% for a sharper stab
  feel; sustain lowered to $A for a snappier envelope. Hat duration shortened
  to 1 frame for a tighter tick.
- **Bass silent in intro/breathe bars**: V1 rests during intro and breathe
  sections so the swell + vocal have room.
- **MP4 video recording** added: `make mp4` captures a VICE screen recording
  of the `.prg` player into `out/friet.mp4` (gitignored -- regeneratable).
- **Intro title card timing fix**: credit line delayed to 2.4s so the title
  card is readable before scrolling starts.
- **Repo cleanup**: removed superseded docs (`chorus_melody.md`,
  `melody_theory.md`); gitignored generated files (`composition.yaml`,
  `lab_composition.yaml`, `friet.mp4`); updated README with research docs
  section.

## 2026-05-25 — Filter LFO, TL-Buis ticker, polish items closed

- **Filter LFO wobble** added: triangle-wave LFO (±4 on cutoff HI) creates a
  subtle phaser-like shimmer on V2. Resonance raised from $4 to $6 for a more
  pronounced sweep. LFO shares the free-running ZP_VIB_IDX phase with vibrato.
- **TL-Buis Dutch lyrics** fully wired into the standalone `.prg` ticker via
  `docs/tl_buis_lyrics.yaml`. Lyrics appear as full lines mapped to the
  OUTPUT timeline; English karaoke fallback kept when the yaml is absent.
  Timing: 0.0s title card → 2.4s credit → 7.4s verse (synced to vocal).
- **Polish plan items 1–8 marked ✅** — arrangement, drums, vibrato, reprise
  dynamics, TL-Buis lyrics all closed.
- **Docs cleaned up**: `polish_plan.md`, `RELEASE.md` updated with completed
  item lists. `Makefile` dependency added for `tl_buis_lyrics.yaml`.
- **Reproducible build**: `make all` builds release + workstage + previews.

## 2026-05-25 — T6 stab bass, clean HH drums, source vocal timing, lab sandbox

- **V1 bass reworked**: replaced T5 verbatim / T11 loop with T6-derived
  stab rhythm (4-3-3-4 sixteenths, positions 0, 1, 1.75, 2.5, 3.5 per
  bar). D-pedal in verses, chord-following Dm-F-Bb-C in choruses.
- **V3 drums reworked (FAST mode)**: synthetic HH kit replaces T13
  verbatim. Kick 4-on-floor + off-beat 8th hat everywhere, snare
  backbeat only in chorus/na-na sections. Cleaner and more appropriate
  for the happy-hardcore feel.
- **Vocal timing preserved**: T7 source timing is kept as-is, including
  the tresillo feel in the chorus. The syncope is the song's rhythmic
  identity, not a transcription artefact -- no 8th-grid quantization.
- **Lab sandbox**: added `src/lab.py` + `make lab` for experimental
  composition work, outputs `out/lab.sid` / `out/lab.mp3` with its own
  `docs/lab_composition.yaml`. Separate from the release pipeline.
- **Musicology research docs** added:
  - `docs/melody_understanding.md` — why the FFD melody works
  - `docs/midi_sources.md` — provenance of the karaoke MIDIs
  - `docs/rhythm_research.md` — analysis of FFD's rhythmic identity
- Documentation updated (README, AGENTS, RELEASE, polish_plan) to
  reflect the new arrangement.

## 2026-05-23 — Pipeline cleanup + release-name rename

- Deleted legacy direct-conversion scripts `src/midi2sid.py` and
  `src/midi2sid_hh.py` and their artefacts (`out/friet_from_desire*`).
  All builds now flow through the extract → compose → synth pipeline.
- Release file is now `out/friet.sid` (was `friet_hh.sid`), built by
  `make friet` (was `make hh-build`/`make hh`). Preview target is
  `make preview-friet`. The standalone C64 player is `out/friet.prg`
  (was `friet_player.prg`) and now embeds the release SID.
- `friet_clean.sid` and `friet_melody_only.sid` kept as workstage
  builds — used for shaving the arrangement without remixing the whole
  thing.
- Internal: env var `HH_TEMPO` → `FAST`; Python `HH_BPM` → `FAST_BPM`;
  player ASM source `src/player/friet_player.asm` → `friet.asm`.
- The `port` / `preview-port` make targets are gone.

## 2026-05-23 — Release target: X2026 / deFEEST

- PSID metadata updated: title "Friet met Desire",
  author "Kloot & Anus / deFEEST", released "2026 X / deFEEST".
- Added `docs/RELEASE.md` with scene-release metadata, arrangement
  description, and known gaps before the party.
- README + AGENTS.md updated with the deFEEST handles and the link to
  the companion demo (`outline26-claude-c64`).
- Makefile reworked: `make all` builds both the maintained build and
  the melody-only verification SID + previews; legacy direct-conversion
  scripts moved off the default chain.

## 2026-05-23 — Dynamic arrangement, audible swell, T11 hook bass

- `compose.py` defines a section table (intro → verse → pre-chorus → chorus
  → post-chorus → break → instrumental → verse2 → pre-chorus2 → chorus2 →
  outro) keyed off T2's `\` markers, then filters T13 drum hits per section
  so verses are kick-only, pre-choruses add snare, choruses go full kit.
- V1 now plays T11's 4-note "na-na" pattern (transposed −12 to bass
  register) looped from beat 5 until T5's actual bassline kicks in at
  beat 120 — no more sparse verses.
- During T11's natural section (~beat 184–248) V1 plays T11 verbatim at
  the original octave, then falls back to T5 for the outro.
- T12 reverse-cymbal swell envelope rewritten: 800 ms attack, sustain at
  $C, short release — sounds like a proper *whoosh* rising into each
  section instead of a 160 ms tick.
- `extract_patterns.py` now dumps T13 drum hits to `docs/song_layers.yaml`
  alongside T5/T7/T11/T12; nothing in the synth path reads MIDI anymore.

## 2026-05-22 — Recognisable melody (the milestone)

- Verified T7 IS the sung melody by aligning T2's Soft-Karaoke syllable
  markers to T7 note positions: each lyric beat lands on the expected
  T7 pitch. Documented in `docs/melody_analysis.md`.
- `extract_patterns.py` writes `docs/song_layers.yaml` and
  `docs/melody_lyrics.yaml` (verbatim T5 bass + T7 vocal + T11 hook +
  T12 SFX + lyric mapping).
- `compose.py` reads the layers and emits T5 + T7 verbatim instead of
  synthetic guesses. `MELODY_ONLY=1` env var renders the vocal alone.
- All voices play at source 130 BPM (mixing tempos broke alignment).

## 2026-05-21 — Cleanroom pipeline

- Three-stage extract → compose → synth chain; each stage reads only
  YAML written by the previous stage.
- `src/extract_patterns.py` produces `docs/song_spec.yaml` (BPM, key,
  1-bar rhythm grids, melodic contour, chord roots).
- `src/compose.py` produces `docs/composition.yaml`.
- `src/synth.py` emits PSID v2.
- Makefile targets: `analyze`, `extract`, `compose`, `synth`,
  `preview-clean`.

## 2026-05-21 — Initial commit

- Project organised: `src/`, `midi/`, `out/`, `stems/`, `docs/`,
  `tools/`.
- README + AGENTS.md + Makefile + render-preview.sh.
- Legacy direct-conversion scripts (`midi2sid.py`, `midi2sid_hh.py`)
  for comparison; not on the maintained pipeline.
- Pushed to `git@github.com:annejan/friet-met-desire.git`.
