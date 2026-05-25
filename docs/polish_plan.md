# Polish plan — Friet van Desire

**Status:** the arrangement is mature: T6 stab-rhythm bass (4-3-3-4 sixteenths,
chord-following), T7 vocal with source timing preserved, clean synthetic HH
drums (kick 4-on-floor + off-beat 8th hat + snare backbeat in chorus), T12
intro swell. 175 BPM release build at `out/friet.sid`. From here it's polish.

## Five axes to push, in priority order

### 1. Sound (tone & timbre of each voice)

| Voice | Now                                | Direction                              |
|-------|------------------------------------|----------------------------------------|
| V1 bass | Pulse, PW=$0800, AD=$08 SR=$C4  | Try wider/narrower PW; maybe sub-pulse with a low-pass touch |
| V2 vocal | Triangle, AD=$12 SR=$F6, filter OFF | Subtle vibrato (LFO ±$08 on freq), gentle attack so syllables phrase |
| V3 drums | Noise per-hit ADSR per kit piece | Maybe pitch-bend the kick down for thump; reduce hat brightness if it returns |

Concrete: re-enable apply_vibrato on V2 (was disabled when we removed the
filter); add small LFO depth so the vocal doesn't feel deadpan.

### 2. Balance (mix levels)

There's no per-voice volume on SID — the master volume is global. Balance comes
from envelope sustain levels and the dynamic range of each waveform. Triangle is
inherently quieter than pulse/saw; noise is loud. Current mix has all three at
sustain ≈ $F. Try:

- bass sustain $A (slightly behind)
- vocal sustain $F (front)
- drum sustain (decay-only envelopes) — already in shape

### 3. Drums (groove) -- DONE

FAST mode uses **synthetic HH drums**: kick 4-on-floor + off-beat 8th hat
everywhere, snare backbeat only in chorus/na-na sections. T13 verbatim is
NOT used in FAST mode (it was too dense / noisy for the happy-hardcore
feel). T12 cymbal swells fire at intro + section transitions.

### 4. Tempo

We dropped to source 130 BPM to recover the melody. The user originally wanted
happy hardcore (170-180 BPM). Path forward:

- Render two builds: `friet_clean.sid` (130 BPM, song-faithful workstage)
  and `friet.sid` (175 BPM, release). Same source data; only the BPM
  parameter changes (set `FAST=1` for the release).
- The vocal will sound faster (chipmunked) at 175 BPM but stays recognisable
  now that we have the right notes.

### 5. Structure / arrangement

Now we have all four MIDI sections in the data (intro, verse, pre-chorus,
chorus, post-chorus, instrumental break, outro). The current SID plays
straight through. We can:

- Trim the SID to a short single loop (intro → chorus → na-na hook → out)
- Add a build-up snare roll into each chorus
- Use V3 to ALSO play the T11 saw-lead "na-na" hook during the instrumental
  break, since drums and lead never conflict in time there

## Where each axis lives in the code

- Sound: `src/synth.py` — `V1_AD/V2_AD/V3_AD` constants and the player asm.
- Balance: same file, envelope sustain nibbles.
- Drums: `src/compose.py` — section loop's `drum_events.append(...)` paths.
  FAST mode generates synthetic kick/hat/snare; clean mode reads T13
  verbatim from `song_layers.yaml`.
- Tempo: `src/compose.py` — `FAST_BPM` / `play_bpm_*` and the MELODY_ONLY env.
- Structure: `src/compose.py` — `sections` template + the bar loop.

## Suggested order

1. ✅ **T6 stab-rhythm bass** — done. V1 plays a 4-3-3-4 sixteenth
   pattern (positions 0, 1, 1.75, 2.5, 3.5 per bar) derived from T6
   chord stabs. D-pedal in verses, chord-following Dm-F-Bb-C in
   choruses. Replaces earlier T5 verbatim / T11 loop approaches.
2. ✅ **Clean synthetic HH drums** — done. FAST mode uses kick
   4-on-floor + off-beat 8th hat everywhere, snare backbeat only in
   chorus/na-na. T13 verbatim is NOT used in FAST mode.
3. ✅ **Audible noise swell** — done. Crash envelope rewritten as a slow
   800 ms attack with held sustain so the rise is heard.
4. ✅ **Source vocal timing preserved** — done. The chorus tresillo IS
   the song's rhythmic identity; vocal is NOT quantized to an 8th grid.
   See `docs/rhythm_research.md` and `docs/melody_understanding.md`.
5. 🟡 **Vibrato on V2 vocal** — TODO. The triangle vocal is dead-pan.
   Re-enable apply_vibrato with subtle depth (±$06 on freq) so syllables
   feel sung. Was disabled when we ripped out the filter; bring it back
   safely with the "skip when V2BASE = 0" guard.
6. ✅ **Fast tempo variant** — done. `FAST=1 compose.py` renders the
   same data at 175 BPM into `out/friet.sid` (the release); the
   workstage `friet_clean.sid` stays at the song-faithful 130 BPM.
7. 🟡 **Reprise / dynamics push** — TODO. Once verses are light and
   choruses heavy, see if Chorus 2 should hit even harder than Chorus 1
   (e.g. crash swell preceding it, hat density up).
8. 🟡 **TL-Buis lyrics in the standalone .prg ticker** — TODO. The
   ticker in `out/friet.prg` currently reads the English Soft-Karaoke
   syllables from `docs/song_layers.yaml` (verbatim source MIDI). The
   Dutch demoscene parody by TL-Buis lives in `docs/lyrics.md` as full
   lines — not aligned to T7 note positions. Wiring it in needs:
   - a per-line timing table that maps each Dutch line to a beat offset
     in the OUTPUT timeline (the SEGMENTS map in `build_player.py`),
     not the source-MIDI timeline;
   - a yaml/json file alongside `lyrics.md` with `{beat: float, text:
     str}` rows, fed into `build_player.py` instead of (or alongside)
     `song_layers.yaml`;
   - a decision on whether to keep the English syllable ticker as a
     fallback for the workstage builds.
