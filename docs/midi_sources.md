# Source MIDI files — musicological inventory

We have **five** MIDIs in `midi/`. Below is what each contains and
what's authoritative for which question.

## Summary table

| File | BPM | Length | Tracks | Has lyrics | Has vocal | Has bass | Has full drums | Use for… |
|------|-----|--------|--------|------------|-----------|----------|----------------|----------|
| `Gala_Freed_From_Desire.mid` | 120 | 204 s | 14 (incl. karaoke meta) | yes | yes (Oboe) | yes (5ths Bass) | yes (3065 hits) | full arrangement, lyric sync, current pipeline |
| `Gala_Free_From_Desire.mid` | 120 | 204 s | 12 | no | yes (Oboe) | yes | yes (3065 hits) | same notes as above — **duplicate** |
| `GALA_Free_from_desire.mid` | 127 | 195 s | 12 | no | yes (Flute) | yes | yes (3065 hits) | same notes, faster tempo, **redundant** |
| `AUD_RC5718.mid` | **130** | 30 s | **1** (multi-channel) | no | no | no (organ stabs only) | sparse (25 hits) | the **actual song tempo**, iconic organ stabs |
| `Gala-freedfromdesire.mid` | **128.5** | ~210 s | **15** | no | yes (Flute) | yes (3 bass tracks) | yes (3118 hits) | ossh transcription — richest source, score transcription + voice essence analysis |

The three `Gala_*.mid` files are byte-for-byte the same arrangement —
they differ only in tempo (120 vs 127 BPM) and the lead instrument
substitute (Oboe vs Flute). Only `Gala_Freed_From_Desire.mid` has the
Soft-Karaoke text metadata (`@KMIDI KARAOKE FILE`, lyric markers per
syllable) — that's why we picked it for the pipeline.

`AUD_RC5718.mid` is a different beast: a *partial* transcription
(chorus / first 16 bars only) packed into one track using multiple
MIDI channels. **It runs at 130 BPM**, which matches the real Gala
single (cross-checked against
[GetSongBPM 129](https://getsongbpm.com/song/freed-from-desire/wmnAN8),
[Tunebat 129](https://tunebat.com/Info/Freed-from-Desire-Gala/3Ucr6hQQuY8cZ0UqXV8uO2),
[AudioKeychain 130](https://www.audiokeychain.com/track/YTG/gala-freed-from-desire)).

The Gala_Freed karaoke at 120 BPM is ~8% slow versus the real
recording — but the *beat positions* of each note are still expressed
in beat units, so changing the playback BPM (we play at 175 in FAST
mode) scales them uniformly. **What we play comes out at a tempo we
control; the source authoring tempo only matters for human-listening
A/B comparison of the karaoke against the radio mix.**

## AUD_RC5718 channel breakdown

The "missing" detail in the karaoke MIDI is the iconic Eurodance organ
stab. AUD has it:

| Ch | Notes | Prog | Range | Role |
|----|-------|------|-------|------|
|  0 |   80 | 18 PercOrgan | D5–A5 | Iconic **organ pumps** (D5 + A5 power-chord stabs) |
|  2 |    4 | 48 StringsEns | D6–D7 | Section-start chord stabs (beats 4, 36) |
|  3 |   54 | 82 Lead2Saw | C-1–F5 | Saw lead (with some C-1 control outliers) |
|  4 |  366 | 18 PercOrgan | D5–A5 | **Doubled organ pumps** (stereo pair of ch 0 — confirms the pump pattern) |
|  8 |    1 | 119 ReverseCymbal | C4 | Single transition swell at beat 63 |
|  9 |   25 | (drums) | C2–G3 | **Section accents only**: Kick + Chinese cymbal + Splash hit together at beats 4 and 20 — markers, not a kit pattern |

Take-aways:
- AUD does NOT have a vocal — we still need the karaoke for the
  vocal melody.
- AUD's drum track is sparse (just section accents), so we still need
  T13 from Gala_Freed for a real kit.
- **What AUD adds** is the iconic D5+A5 organ pump pattern — that's the
  Eurodance signature that nothing in our karaoke has (T6 / "Drawbar
  Organ" in Gala_Freed plays a different D-arpeggio pattern, not the
  power-chord pump).

## Stem labels are anchored to one source

`stems/T05_unnamed_prog87.mid` etc. are slices of
**Gala_Freed_From_Desire.mid** (the karaoke). The track-number prefix
maps to:

| stem | what it actually is |
|------|---------------------|
| T04 | Acoustic Grand Piano (chord comp) |
| T05 | 5ths Bass (= T5 in our `song_layers.yaml`'s `bass` layer) |
| T06 | Drawbar Organ (high D arpeggio — NOT the iconic D5+A5 pump) |
| T07 | Oboe ← **vocal substitute** |
| T08 | Synth Strings |
| T09 | String Ensemble |
| T10 | Sweep Pad |
| T11 | Lead Square ← **na-na hook** |
| T12 | Reverse Cymbal swell |
| T13 | Drumkit (channel 9) |

In `GALA_Free_from_desire.mid` the same arrangement has the vocal on
**T5** (not T7) because the meta header tracks are absent — so any
"stem TX" label only makes sense if you say *which* MIDI it came
from. Rename suggestions if we ever re-extract: prefix with the
*role* (`bass`, `vocal`, `chord_stab`, `na_na_hook`, `drumkit`)
instead of the source-MIDI track number.

## The "T5 bass starts at beat 120" mystery

`docs/song_layers.yaml`'s `bass` layer has 428 events but they all
sit between source beats 120 and 408. **There is no bass in the
intro / verse 1 / pre-chorus 1 / chorus 1** of the karaoke — the
song-faithful workstage is therefore correctly silent on V1 until
~1:00. T11 ("Lead Square", `hook` layer) fills that gap from beat 5
onward; that's why our compose.py uses the T11-hook-as-bass trick
before the real bass kicks in.

When T5 finally enters at beat 120 (= the second chorus / instrumental
break) it plays a **tresillo (3-3-2) bassline**: same pitch hit three
times at positions 0, 0.75, 1.5 within each half-bar, then the pitch
changes on the next half-bar. Across 8 beats (2 bars) the pitch
cycle is D-A-F-C; the next 2 bars are D-A-G-C. The "tresillo" is the
core groove element — *and it lines up with the vocal chorus's 16th
syncope* (0, 0.75, 1.5, 2, 2.75). The 3-against-4 feel between this
bass-and-vocal layer and a 4-on-the-floor kick is the song's
signature, not a transcription artefact.

## Gala-freedfromdesire.mid (ossh) — 128.5 BPM, 15 tracks

The richest source MIDI. 128.5 BPM (close to the real recording's
~129 BPM). Contains three distinct bass tracks, full organ layers, and
a 473-note vocal on Flute (T5). Full analysis in
`docs/score_transcription.md` (beat-by-beat 16th grid) and
`docs/voice_essence.md` (pattern engines).

| Track | Prog | Notes | Range | Role |
|-------|------|-------|-------|------|
| T5 Flute | 73 | 473 | A4–F5 | Vocal melody |
| T8 PercOrgan | 18 | 240 | D4–D6 | Organ stabs (Pattern A) |
| T7 DrawbarOrgan | 17 | 260 | D4–D7 | Organ stabs (Pattern A) |
| T2 5ths Bass | 87 | 208 | B1–F3 | Bass (late entry) |
| T3 Fretless Bass | 35 | 222 | C2–C3 | Bass (tresillo, Pattern B) |
| T6 Acoustic Bass | 32 | 163 | D2–D4 | Bass (Pattern A) |
| T4 ElGrand Piano | 3 | 897 | A2–A4 | Chord comp |
| T9 Synth Strings | 50 | 213 | C4–D5 | Pad |
| T14 Lead Synth | 80 | 414 | C2–F3 | Lead synth (Pattern B) |
| T10 Drums | ch9 | 3118 | — | Full kit |
| T11 Sweep Pad | 95 | 29 | D4–D5 | Transition pad |
| T12 Metallic Pad | 94 | 27 | C4–D5 | Transition pad |
| T13 Rev Cymbal | 119 | 15 | F3–C6 | Section swells |

Key discovery from this MIDI: the organ stab grid (Pattern A: positions
0, 4, 7, 10, 14 sixteenths per bar) **interleaves with the vocal** —
zero collisions per bar. The bass and vocal are call-and-response by
design, not coincidence. This insight drove the V1 interleaving bass
in the release build.

## What to do with this

1. The karaoke MIDI's vocal timing might be a faithful transcription
   of Gala's actual phrasing after all (it lines up with the bass
   tresillo). The "every syllable on a beat" reading from ChordZone
   is a simplification for guitar-strummers. **The lab should leave
   vocal timing alone.**
2. The karaoke MIDI **does not contain** the iconic D5+A5 organ pump.
   That sound is what gives FFD's chorus its character and is what's
   making our HH cover sound thin in the chorus. If we want it, we
   need to add it as a synthetic layer — either lifted from AUD's
   ch 0/4, or generated procedurally as "D5+A5 stab on every beat".
3. Stem filenames should be re-prefixed by role rather than
   source-MIDI track index.
