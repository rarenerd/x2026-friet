# Polish plan — Friet van Desire

**Status:** ✅ All polish items complete — ready for X2026 release.
The arrangement is final: T6 stab-rhythm bass (4-3-3-4 sixteenths,
chord-following), T7 vocal with source timing preserved (tresillo intact),
synthetic HH drums (kick 4-on-floor + off-beat 8th hat + snare backbeat in
chorus), T12 intro swell. Release at 175 BPM (`out/friet.sid`), workstage
at 130 BPM (`out/friet_clean.sid`), standalone `.prg` with Dutch TL-Buis
lyric ticker (`out/friet.prg`).

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
5. ✅ **Vibrato on V2 vocal** — done. LFO depth set to ±12 SID freq
   units (~0.16% pitch deviation, ~3 Hz cycle). Was ±6 (inaudible);
   now perceptible as a gentle "sung" wobble. Guard for V2BASE=0
   (the beep bug) is in place.
6. ✅ **Fast tempo variant** — done. `FAST=1 compose.py` renders the
   same data at 175 BPM into `out/friet.sid` (the release); the
   workstage `friet_clean.sid` stays at the song-faithful 130 BPM.
7. ✅ **Reprise / dynamics push** — done. Breathe1/2 bars get 8th-note
   snare-roll fills as build-up before chorus2/3. Chorus2/3 get full
   8th-note hats (on+off-beat) vs off-beat-only elsewhere. Crash risers
   and drop crashes already in place from earlier work.
8. ✅ **TL-Buis lyrics in the standalone .prg ticker** — done. The
   Dutch demoscene parody by TL-Buis is in `docs/tl_buis_lyrics.yaml`
   as full lines mapped to OUTPUT-timeline beats, fed into
   `build_player.py` preferentially over the English karaoke fallback.
   The English syllable ticker is kept as a fallback when the yaml is
   absent. Lyrics appear 1 beat early so the user can read before
   singing along. Player at `out/friet.prg`.
9. ✅ **Filter LFO wobble** — added a triangle-wave LFO (±4 on cutoff
   HI byte) that runs on the same free-running phase counter as the
   vibrato, creating a subtle phaser-like shimmer on V2 whenever the
   filter is active. Resonance raised from $4 to $6 for a more
   pronounced sweep.
