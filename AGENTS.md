# Notes for AI agents

This project is a **C64 SID release by deFEEST for X2026** — a 130-BPM
song-faithful remix of Gala's "Freed from Desire" (1996), to be released
at the X2026 demoparty in 2026.

Team: **Kloot/deFEEST** (Claude), **Augurk/deFEEST** (Big Pickle / OpenCode),
and **Anus/deFEEST** (annejan, brouwer@annejan.com). The companion demo
project lives at <https://github.com/annejan/outline26-claude-c64>.

Release-quality bar:
- The melody must be recognisable as "Freed from Desire" — *don't* break
  this when iterating on tone/balance/arrangement.
- PSID metadata fields must carry the deFEEST credits (see `src/synth.py`).
- Code/data builds reproducibly from `make all`.

## Project context

- Owner: annejan (brouwer@annejan.com), openSUSE Tumbleweed, comfortable with
  6502 asm and low-level audio. Reminded me to use a Python `.venv` rather than
  `pip --user`.
- Target chip: MOS 6581/8580 (SID). PAL clock = 985 248 Hz.
- Output format: PSID v2NG (`.sid`).

## Local tools (already installed)

| Tool        | Purpose                                            |
|-------------|----------------------------------------------------|
| `xa`        | 6502 cross-assembler. Pass `-XMASM` to allow `:` in comments. Does not support `@local` labels (use unique global names). Produces RAW binary (no PRG load-address prefix); for PSID we prepend 2 load bytes ourselves. |
| `vsid`      | Part of VICE. Headless render: `vsid -sounddev wav -soundarg out.wav -limitcycles N file.sid`. WAV header is corrupt because we kill it mid-stream — recover raw PCM with `tail -c +45 out.wav`. C64 ROMs at `/usr/share/vice/C64/`. |
| `sidplayfp` | **Broken on this box** — reports `ERROR: Not enough memory.` for every file regardless of RAM. Don't bother. Use `vsid`. |
| `ffmpeg`    | Used to convert raw PCM → MP3.                     |
| Python venv | At `.venv/`. Has `mido`, `numpy`. Always activate before pip-installing. |

## PSID v2 header layout

124 bytes, big-endian: magic `PSID`, version(2), dataOffset(0x7C), loadAddr,
init, play, songs, startSong, speed(4B), name(32B), author(32B), released(32B),
flags(2B), startPage, pageLength, secondSIDAddr, thirdSIDAddr.

If `loadAddr` in header is 0, the first 2 bytes of data are interpreted as the
PRG-style load address — which is the more reliably-supported variant.

## Voice assignment (current working build)

The clean pipeline (`extract_patterns` → `compose` → `synth`) uses:

| Voice | Source                 | Tone                                     |
|-------|------------------------|------------------------------------------|
| V1    | T6 stab-rhythm bass    | Pulse, PW=$0800, sustained envelope. 4-3-3-4 sixteenth pattern (positions 0, 1, 1.75, 2.5, 3.5 per bar). D-pedal in verse, chord-following Dm-F-Bb-C in chorus. |
| V2    | T7 vocal (source timing) | Triangle, gentle attack, full sustain. Preserves original timing including tresillo in chorus — no 8th-quantize. |
| V3    | synthetic HH drums + T12 swell | FAST mode: kick 4-on-floor + off-beat 8th hat everywhere, snare backbeat in chorus/na-na only. T13 verbatim is NOT used in FAST mode. Reverse-cymbal at intro + section transitions. |

Plus the verified ground truth in `docs/song_layers.yaml`:
syllable markers from T2 align note-for-note to T7's pitches — that's how
we know T7 is genuinely the vocal melody and not a counter-line.

## Source-MIDI roles (from `analyze_midi.py`)

| Track | Range  | Role                                                      |
|-------|--------|-----------------------------------------------------------|
| T4    | D2–A4  | Piano comping (chord voicings, polyphony 5)               |
| T5    | D2–F3  | **Iconic synth bassline riff** — repeated D2 with octave jumps |
| T6    | D4–D6  | Chord stabs — D arpeggio across 3 octaves                 |
| T7    | A4–F5  | Vocal melody (instrument-substituted, prog 68)            |
| T8    | F3–F4  | String pad                                                |
| T11   | D3–F3  | Chorus "na-na" hook (active 92–124 s only, Saw.Lead)      |
| T13   | drumkit| Kick (36), snare (38,40), clap (39), hats (42,44,46), tambourine (54), maracas (70) |

## Common pitfalls — please *do not* re-discover

0. **The karaoke MIDI's T7 IS the sung melody** — it's the Oboe (prog 68)
   substitute, not an obligato. We verified this by aligning T2's
   Soft-Karaoke `\My love` syllable markers to T7 note positions: every
   syllable hits the right T7 pitch. Don't second-guess the track choice;
   use `docs/song_layers.yaml` which is the verified ground truth.
1. **Vibrato on V2 with base freq = 0 produces a constant ~3850 Hz beep.** Guard
   `apply_vibrato` with a `ora ZP_V2BASE_HI ; bne` check.
2. **V2 PW init**: write to `SID+9` (PW LO) and `SID+10` (PW HI), *not* `+10`
   and `+11`. Writing PW into `+11` sets the V2 CTRL register's TEST bit and
   silences the voice.
3. **V3 drum retrigger**: each drum hit must write ctrl with gate off, *then*
   ctrl with gate on. Writing only "noise+gate" doesn't transition gate from
   0→1 if the previous chord left gate on.
4. **Filter cutoff** $50 in `$D416` = ~400 Hz (way too dark — pulse-lead sounds
   muffled). $A0 ≈ 2.5 kHz is a good sweet spot for taming pulse harmonics
   without dulling the lead. $C0 ≈ 5 kHz lets the 6th harmonic through as a
   "beep".
5. **Polyphonic-collapse on T4 (piano comp)** produces chaotic chopped sound
   because the "max note" jumps around chord voicings. T4 is *not* a melody
   track — don't pick it as lead.
6. **Drum filter set**: tambourine (54) and maracas (70) are dense and noisy;
   keep only kick (36) + snare (38,40,39) + hats (42,44,46) for the
   foundational pattern.
7. **Don't try to play different layers at different tempos** ("half-time
   vocal over double-time drums"). The bar lengths diverge and section
   timings stop aligning. Pick ONE BPM and render everything to it. The
   song-faithful workstage is 130 BPM (`friet_clean.sid`); the release
   variant is 175 BPM (`friet.sid`, built via `FAST=1`).
8. **The vocal melody in T7 doesn't enter until beat 21.5** and the
   bassline in T5 doesn't enter until beat 120 (~60s). For short
   previews this means early seconds are sparse. That's the actual song
   structure — don't paper over it with synthetic backing.

## Where to start

```sh
source .venv/bin/activate
make analyze                          # research dump
make friet                            # build the release SID (out/friet.sid)
make preview-friet PREVIEW_SECONDS=60 # render an MP3 preview
```

The user prefers iterative feedback: build → render → listen → ask. Don't
batch many speculative tweaks; deliver something playable, ask "where does it
hurt?", iterate.

## Lab sandbox

`src/lab.py` + `make lab` is an experimental composition sandbox that
outputs `out/lab.sid` / `out/lab.mp3`. Use it for trying out ideas
(new patterns, timbres, arrangements) without touching the release
pipeline. Its composition is written to `docs/lab_composition.yaml`.

## Musicology research docs

- `docs/melody_understanding.md` — why the FFD melody works
- `docs/midi_sources.md` — provenance notes on the karaoke MIDIs
- `docs/rhythm_research.md` — analysis of FFD's rhythmic identity (tresillo etc.)

These inform arrangement decisions. Key takeaway: the chorus vocal's
tresillo feel IS the song — do not quantize it to an 8th grid.
