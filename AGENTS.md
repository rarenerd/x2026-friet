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
- Target chip: **MOS 8580 (SID), PAL** — committed target. Clock = 985 248 Hz.
  PSID flags = `0x0024` (PAL bits 2-3 = 01, 8580 bits 4-5 = 10). Render/verify
  on 8580 (`vsid -sidenginemodel 257 -pal …`); VICE's default is 6581, so a
  plain render is the WRONG chip.
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

The release pipeline (`extract_patterns` → `compose` → `synth`) uses:

| Voice | Source                 | Tone                                     |
|-------|------------------------|------------------------------------------|
| V1    | **Synthetic HHC tresillo bass** | Pulse 50%, AD=$07 SR=$17 (instant attack, fast decay, 7% sustain — HHC pump). Chord cycle Dm-F-Bb-C (i-III-VI-VII), one chord per 4-beat bar. Six hits per bar at tresillo offsets `[0, 0.75, 1.5, 2, 2.75, 3.5]`. Roots in octave 2 (D2/F2/Bb2/C3). Silent in intro; sustained D2 drone in breakdown. |
| V2    | **T7 vocal verbatim** | Pulse 25% PW (the recognisable melody, but with HHC stab harmonics that cut through the mix). Base transpose −12 (Gala's actual sung register A3–F4); chorus lift +7 (perfect fifth, bright but not whistle). Per-note filter sweep $C0→$80 + LFO ±3. |
| V3    | **Synthetic HHC kit** | Per-section: intro silent, verse closed-hat offbeat 8ths, prechorus rolling 16ths (build), chorus open hat every offbeat (shimmer), postchorus rolling 16ths, breakdown silent, breathe = kick only + snare roll. 2-beat 16th snare fills at the tail of verse1/prechorus1/chorus1. Crashes from source T12 plus synthetic risers 3 beats before each chorus. |

The lead is the **only** MIDI-derived voice — V2 plays the karaoke vocal
(`docs/song_layers.yaml` 'vocal' layer, verified against T2 syllable
markers) verbatim. V1 and V3 are synthesised entirely in `compose.py` to a
happy-hardcore template; the source layers for those (organ, T5 bass, T11
hook, T13 drums) are no longer read by the release pipeline.

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
4. **Filter cutoff (8580 target).** The 8580 cutoff curve is near-linear and
   shifted UP vs the 6581, so a given `$D416` HI value = a HIGHER frequency.
   On 8580 the lead sits right with cutoff init/target ≈ `$60` and a per-note
   "open" of ≈ `$C0` (these were `$80`/`$E0` back when previews were wrongly
   rendered on 6581). Do NOT reuse the old 6581 sweet-spots ($50≈400Hz,
   $A0≈2.5kHz, $C0≈5kHz) — they read brighter/harsher on 8580.
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
9. **Every voice must share ONE beat→frame grid.** Lead/bass/organ/hook
   use `grid_frame()` (an integer-accumulated Bresenham 16th grid, zero
   drift). The drums once used `round(beat * fbeat)` instead — ~30% of
   source hits sat off-grid and flammed against the grid-snapped lead.
   Route *everything* through `grid_frame()`.
10. **The lead is legato-filled, and the ~2-frame gate-off gap is
    load-bearing.** Each note extends to the next onset *minus 2 frames*
    (`dur = gap - 2`). Without the fill the melody blips with silent
    gaps; without the 2-frame gate-off the per-note retrigger toggles
    gate off→on within one frame, the envelope can't hard-restart, and
    notes glitch / barely sound. Keep both.
11. **Don't combine waveforms on the lead.** `$50` (tri+pulse) AND-
    combines to a thin, partly-cancelled tone that *drops notes* — this
    was the chorus-3 "missing notes". Use a single waveform ($10/$20/$40).
12. **Filter resonance masks the note fundamental when too high** → muddy
    melody. On the **8580** the flangey lead sweep wants **res $7 + cutoff-LFO
    ±6** (`filt_lfo`). 8580 resonance is stronger/sharper than 6581, so this is
    one notch below the old 6581 values (res $8 / ±10); $A / ±16 ate notes.
13. **`length_frames` = last actual event (+ tail), NOT `total_bars *
    fpbar`.** The synthetic length padded every voice with ~2 min of
    rests before the loop sentinel = dead air. And in `render-preview.sh`
    never name a var `SECONDS` (bash special var — it silently broke the
    `-t` length and the `afade`-out).
14. **Raster-split `$D021` change must be the FIRST write in the split
    IRQ.** The koala bg is light-grey; if `$D021=$00` is written *after*
    `$D011/$D016/$D018` in `irq_split`, it changes too late in the line and
    the grey leaks onto the right of the split scanline (loose pixels above
    the lyric bar). Write the background colour first, at the top of the line.
15. **Sprites crossing a `$D018`-switching raster split need their pointers
    mirrored to BOTH screens.** The split flips `$D018` from `$78` (bitmap
    screen `$5C00` → pointers `$5FF8`) to `$64` (text screen `$5800` →
    pointers `$5BF8`). A sprite whose Y dips below the split is displayed
    while `$D018=$64`, so the VIC fetches its pointer from `$5BF8`; if you
    only wrote `$5FF8` it reads garbage and the sprite shows corruption.
    `spin` (and init) write the cube pointers to both `$5FF8` and `$5BF8`.
    (This only surfaced once the cubes' Y range was widened to reach the
    split — before that they never entered the text region.)

## Demo player (`src/player/friet_koala.asm`)

The one-file demo (`make koala` → `out/friet.prg`). Built by
`build_player.py`, which extracts the SID body + builds the lyric table,
then assembles three players via the shared `assemble()` helper
(`friet.asm` = lyric ticker, `friet_compo.asm` = pure-audio credits,
`friet_koala.asm` = this demo). Visual assets come from `tools/mix_koala.py`
(composites Miep + cigar-Harry's swirl ornaments + frikandel + fries on a
dark nebula+starfield → koala bitmap bins) and `tools/spm_to_sprites.py`
(`FinaLKjoep32.spm` → 32 cube-rotation frames).

- **Two-IRQ raster split.** `irq_top` (line `TOPL`=251) = multicolor
  bitmap + runs the frame (SID play, `fly`, `spin`, `tick_scene`,
  `lyric_tick`, kick→border strobe). `irq_split` (line `SPLIT`=225) =
  hires text mode for the bottom 3 rows (the lyric ticker, white-on-black).
- **VIC bank 1**; memory map is documented at the top of the .asm. RAM
  font copied from char ROM `$D800` → `$5000` (char ROM isn't visible in
  bank 1).
- **Arrangement has a breakdown→drop.** Before the climax `chorus3`,
  an 8-beat `breakdown` segment drops drums + bass (just the naked hook),
  then `breathe2` builds (snare roll + riser), then `chorus3` slams in full
  + octave-up. The cube escalation mirrors it: collapse to 2, explode to
  8 + 2× on the drop. If you change the song length, retune the asm loop
  point + `sc_*` boundaries (they're frames; current length 3886 = `$0F2E`).
- **8 hardware sprites = flying spinning cubes.** `fly` weaves each on its
  own Lissajous curve (8.8 fixed-point phase accumulators, per-sprite X:Y
  speeds, slow precession; 9-bit X via `$D010`); `spin` cycles the pointer
  through the 32 cube frames. `tick_scene` drives the escalation arc above,
  keyed off the frame counter and resynced at the song loop.

## Where to start

```sh
source .venv/bin/activate
make friet                            # build the release SID (out/friet.sid)
make preview-friet PREVIEW_SECONDS=60 # render an MP3 preview
make koala                            # the one-file demo  → out/friet.prg (+ .d64)
make player                           # lyric-ticker-only player → out/friet_lyrics.prg
make analyze                          # research dump (if exploring MIDIs)
```

Read `docs/score_transcription.md` and `docs/voice_essence.md` to
understand the source material before touching the arrangement.

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
- `docs/midi_sources.md` — provenance notes on all five source MIDIs
- `docs/rhythm_research.md` — analysis of FFD's rhythmic identity (tresillo etc.)
- `docs/score_transcription.md` — beat-by-beat 16th-grid transcription from the ossh MIDI
- `docs/voice_essence.md` — DNA of each instrument layer (Pattern A / Pattern B engines)
- `docs/sound_engine.md` — **the playback/synthesis engine** (the "new standard"):
  frame-grid sync, legato-fill + hard-restart, per-section timbre, flange,
  length/loop, render fade. Read this before touching `compose.py`/`synth.py`.

These inform arrangement decisions. Key takeaway: bass interleaves
with vocal (call-and-response) — zero collisions per bar. The chorus
vocal's tresillo feel IS the song — do not quantize it to an 8th grid.
