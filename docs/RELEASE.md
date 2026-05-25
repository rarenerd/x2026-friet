# Release notes — *Friet van Desire*

## Scene metadata

- **Title:** Friet van Desire
- **Group:** deFEEST
- **Composer / coder:** Kloot/deFEEST (Claude), Augurk/deFEEST (Big Pickle / OpenCode) +
  Anus/deFEEST (annejan)
- **Target party:** **X2026** (Dutch Commodore demoparty)
- **Format:** PSID v2 / `out/friet.sid` (release) + `out/friet.prg`
  (standalone C64 player with lyric ticker)
- **Chip:** MOS 6581/8580 (PAL, 985 248 Hz)
- **Player:** 50 Hz IRQ, init at $1000, play at $1003
- **Length:** **1:14** release build (175 BPM); **1:48** song-faithful
  workstage at 120 BPM; loops on reaching the end. See "Structure" below.

## Companion demo

This SID will sound in deFEEST's X2026 demo, *"Kloten met de
broodtrommel"* — see <https://github.com/annejan/outline26-claude-c64>.

## Structure

Compose-time segment map (`SEGMENTS` in `src/compose.py`) re-orders the
source MIDI to fit the happy-hardcore arrangement:

| #  | Segment            | Source-beat range  | Beats |
|----|--------------------|--------------------|-------|
| 1  | Intro              | 0.0 → 21.5         | 21.5  |
| 2  | Verse 1            | 21.5 → 54.5        | 33.0  |
| 3  | Pre-chorus 1       | 54.5 → 88.0        | 33.5  |
| 4  | Chorus 1           | 88.0 → 117.5       | 29.5  |
| 5  | Post-chorus (Na-na)| 117.5 → 149.5      | 32.0  |
| 6  | **Breathe 1**      | 149.5 → 153.5      |  4.0  |
| 7  | Chorus 2 reprise   | 88.0 → 117.5       | 29.5  |
| 8  | **Breathe 2**      | 149.5 → 153.5      |  4.0  |
| 9  | Chorus 3 reprise   | 88.0 → 117.5       | 29.5  |
|    | **Total**          |                    | **216.5** |

Breathe segments are 4-beat instrumental gaps (drums + T11 hook bass keep
going, no vocal) so each chorus reprise gets room to breathe before the
next one hits. Total loop: **1:48** at 120 BPM workstage, **1:14** at
175 BPM release.

Each chorus reprise (#6 and #7) replays the same source range as Chorus 1,
so the vocal + bass + drum events are bar-for-bar identical. A synthetic
crash-riser fires 3 beats before each chorus's output position so each
one hits as a "drop". Verses 2 / Pre-chorus 2 / Instrumental break /
Outro of the original arrangement are NOT used — they don't fit the
happy-hardcore form factor.

## Arrangement (current build)

Three SID voices:

| Voice | What it plays                                                       |
|-------|---------------------------------------------------------------------|
| V1    | **T6 stab-rhythm bass** — 4-3-3-4 sixteenth pattern (positions 0, 1, 1.75, 2.5, 3.5 per bar). D-pedal in verses, chord-following Dm-F-Bb-C in choruses. |
| V2    | T7 vocal melody with **source timing preserved** — the tresillo feel in the chorus IS the song's rhythmic identity, not a transcription artefact. Verified by aligning T2's syllable markers to T7 pitches. |
| V3    | **Synthetic HH drums** (FAST mode): kick 4-on-floor + off-beat 8th hat everywhere, snare backbeat only in chorus/na-na sections. T13 verbatim is NOT used in the release build. Plus T12's reverse-cymbal swells at the intro and section transitions. |

## Tones

- V1 bass: pulse waveform, PW $0800, sustained envelope.
- V2 vocal: triangle waveform, slow attack so syllables phrase, full
  sustain.
- V3 drums: noise with per-kit-piece ADSR; reverse-cymbal has an 800 ms
  slow attack so the swell is *heard*, not ticked.

## How to verify before the party

```sh
make all                 # rebuild release + workstage SIDs + previews
vsid out/friet.sid       # listen on VICE
xxd out/friet.sid | head -8   # confirm PSID header reads
                              #   'PSID' v2, Kloot, Anus & Augurk / deFEEST
```

## Known gaps before release

All polish items from [`polish_plan.md`](polish_plan.md) are complete.
The release SID (`out/friet.sid`), standalone player (`out/friet.prg`
with Dutch lyric ticker), and both workstage builds are ready.

### Polish items since initial release notes

- ✅ Vibrato on V2 (±12 SID freq units, ~3 Hz LFO)
- ✅ Chorus 2/3 reprises hit harder (breathe sections with snare rolls,
    full 8th-note hats, crash risers before each drop)
- ✅ TL-Buis Dutch parody lyrics in the standalone .prg ticker
- ✅ Filter LFO wobble (phaser-like modulation of cutoff HI, ±4 steps,
    synchronised to the vibrato LFO)
- ✅ Lyrics appear 1 beat early so the user can read before singing

## Sources used

- Karaoke MIDI: `midi/Gala_Freed_From_Desire.mid` — T2 lyric markers
  cross-validated against T7 to establish that T7 is the vocal melody.
- [Hooktheory](https://www.hooktheory.com/theorytab/view/gala/freed-from-desire):
  key D minor, i-III-VI-VII chord progression.
- [ChordU](https://chordu.com/chords-tabs-gala-freed-from-desire-official-video--id_p3l7fgvrEKM):
  tempo 128.85 BPM, chords Dm-F-B♭-C.
- [pianoletternotes.blogspot.com](https://pianoletternotes.blogspot.com/2019/02/freed-from-desire-by-gala.html):
  cross-reference for the verse "a-a-a" stutter and the chorus "d-d-c-d"
  descending pattern.
