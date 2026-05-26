# Polish plan — Friet van Desire

**Status:** ✅ All polish items complete — ready for X2026 release.
The arrangement is final: V1 interleaving organ stab (T6 grid, zero
vocal collisions, D2 pedal), V2 vocal verbatim with per-section waveform
(triangle/sawtooth+hoover/pulse), V3 T13 drums verbatim section-filtered
(snare fills, hat boost, crash swell). Release at 175 BPM
(`out/friet.sid`), workstage at 130 BPM (`out/friet_clean.sid`),
standalone `.prg` with Dutch TL-Buis lyric ticker (`out/friet.prg`).

1. ✅ **Interleaving bass** — done. V1 plays T6 grid positions (0, 1,
   1.75, 2.5, 3.5 beats per bar) computed per output bar to never
   collide with any V2 vocal note. D2 pedal. Silent in intro/breathes.
   Call-and-response with the vocal.
2. ✅ **T13 verbatim drums** — done. Section-filtered: verse=kick,
   prechorus=kick+snare, chorus=full kit. Snare fills in breathe
   sections. Hat boost (8th on+off) in chorus2/3.
3. ✅ **Crash swell** — done. Long attack ($D), dark pitch (28), 4s gate.
4. ✅ **Per-section V2 waveform** — done. Triangle in verse,
   sawtooth+hoover in chorus, pulse in final reprise. Source timing
   preserved (tresillo intact). See `docs/rhythm_research.md` and
   `docs/melody_understanding.md`.
5. ✅ **Vibrato on V2 vocal** — done. LFO depth set to ±12 SID freq
   units (~0.16% pitch deviation, ~3 Hz cycle). Was ±6 (inaudible);
   now perceptible as a gentle "sung" wobble. Guard for V2BASE=0
   (the beep bug) is in place.
6. ✅ **Fast tempo variant** — done. `FAST=1 compose.py` renders the
   same data at 175 BPM into `out/friet.sid` (the release); the
   workstage `friet_clean.sid` stays at the song-faithful 130 BPM.
7. ✅ **Reprise / dynamics push** — done. Breathe1/2 bars get snare-roll
   fills as build-up before chorus2/3. Chorus2/3 get full 8th-note hats
   (on+off-beat) vs off-beat-only elsewhere. Crash risers and drop
   crashes in place.
8. ✅ **TL-Buis lyrics in the standalone .prg ticker** — done. The
   Dutch demoscene parody by TL-Buis is in `docs/tl_buis_lyrics.yaml`
   as full lines mapped to OUTPUT-timeline beats, fed into
   `build_player.py` preferentially over the English karaoke fallback.
   The English syllable ticker is kept as a fallback when the yaml is
   absent. Lyrics appear 1 beat early so the user can read before
   singing along. Player at `out/friet.prg` (48 lines).
9. ✅ **Filter LFO wobble** — added a triangle-wave LFO (±4 on cutoff
   HI byte) that runs on the same free-running phase counter as the
   vibrato, creating a subtle phaser-like shimmer on V2 whenever the
   filter is active. Resonance raised from $4 to $6 for a more
   pronounced sweep.
10. ✅ **Score transcription + voice essence docs** — full ossh MIDI
    analysis in `docs/score_transcription.md` and `docs/voice_essence.md`.
    Key insight: bass interleaves with vocal, zero collisions per bar.

### Open / future

- **Sound/timbre**: ring-modulate V1 against V3 for "chord shimmer"
  (pad substitute with 3 voices). Not blocking release.
