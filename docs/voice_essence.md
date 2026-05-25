# Voice essence — what each instrument does in FFD

Extracted from `midi/Gala-freedfromdesire.mid` (ossh, 128.5 BPM, 15 tracks).
This is the DNA of the song — the patterns each voice contributes.

## Two rhythmic engines

The whole song runs on **two rhythmic patterns** shared by multiple voices:

### Pattern A: "4-3-3-4" organ stab (sixteenths 0, 4, 7, 10, 14)

```
16th:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
hit:   X  ·  ·  ·  X  ·  ·  X  ·  ·  X  ·  ·  ·  X  ·
gap:      4        3        3        4
```

Used by: T8 PercOrgan, T7 DrawbarOrgan, T6 AcousticBass, T4 Piano.
Active in: **intro, verse, instrumental, bridge** (NOT chorus/post-chorus).

### Pattern B: "3-3-2" tresillo (sixteenths 0, 3, 6, 8, 11, 14)

```
16th:  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
hit:   X  ·  ·  X  ·  ·  X  ·  X  ·  ·  X  ·  ·  X  ·
gap:      3        3        2        3        3
```

Used by: T3 Fretless Bass, T14 Lead Synth.
Active in: **post-chorus, instrumental, verse 2, pre-chorus 2, chorus 2+**
(enters AFTER the first chorus — it's the "second half of the song" engine).

## Voice-by-voice essence

### VOCAL (T5, Flute prog 73) — 470 notes
- **Pitches**: E5 (182×), D5 (110×), C5 (110×), F5 (32×), A4 (30×), A#4 (6×)
- **6 notes total**, all D natural minor
- **Verse**: E5 stutter (5×) on 8ths, then F5 peak → D5 → C5 descent
- **Chorus**: F5 peak → D5 → C5 → A4 (includes the 5th! our karaoke missed this)
- Active in: verse, pre-chorus, chorus, post-chorus, verse 2, chorus 2+

### PERC ORGAN (T8, prog 18) — 240 notes
- **Pitches**: D4 (80×), D5 (80×), D6 (80×) — triple-octave D unison
- **Rhythm**: Pattern A (4-3-3-4) — 5 stabs per bar
- **Call-and-response**: plays in EVEN bars only during verse (bars 2,4,6,8)
  — odd bars are vocal-only
- Active in: intro (beat 4+), verse 1, instrumental, bridge
- **NOT in chorus or post-chorus!**

### DRAWBAR ORGAN (T7, prog 17) — 260 notes
- Same as T8 but with D7 (highest octave) — adds brightness
- Exact same rhythm and section activity as T8

### ACOUSTIC BASS (T6, prog 32) — 163 notes
- **Pitches**: D2 (80×), D3 (80×), D4 (3×) — octave-bouncing D pedal
- **Rhythm**: Pattern A (4-3-3-4) — same as organ!
- Active in: intro, verse 1, instrumental, bridge
- The "bass register" version of the organ stab

### 5THS BASS (T2, prog 87) — 208 notes
- **Late entry**: starts at beat 160 (instrumental section)
- First bar is a 2-octave **scale run** (F2→F3→F2 ascending/descending)
- Then plays D2-D3 octave jumps in the stab pattern
- Active in: instrumental, verse 2, pre-chorus 2, bridge, chorus 3

### FRETLESS BASS (T3, prog 35) — 222 notes
- **Rhythm**: Pattern B (3-3-2 tresillo)
- **Pitch cycle**: D2-D2-D2 → A2-A2-A2 per half-bar (root → 5th)
  Changes per bar: D-A / F-C / Bb-F / G-C = **chord-following**
- Active from: **post-chorus (beat 128)** onwards

### LEAD SYNTH (T14, prog 80) — 414 notes
- **Doubles the Fretless Bass** (T3) at D3 register (one octave up)
- Same tresillo rhythm, same chord-following
- Adds the na-na hook range after the instrumental

### PIANO (T4, ElGrand prog 3) — 897 notes
- **Rhythm**: Pattern A (4-3-3-4) in some sections, sustained in others
- **Chord voicings**: Dm (D4+F4+A4), C (C4+E4+G4), Bb (A#3+D4+F4)
- Active from: **pre-chorus (beat 68)** — the "lift" before the chorus
- Densest voice in the MIDI (897 notes)

### STRINGS (T9, SynStrings prog 50) — 213 notes
- Sustained whole-bar chords (only position 0 = downbeat)
- Harmonic pad, not rhythmic
- Active in most sections from verse 1 onwards

## Section activity map

```
Section          | Organ | AcBass | Piano | FrtBass | Vocal | Strings | Drums
                 | stab  | stab   | chord | tresilo |       | pad     |
-----------------+-------+--------+-------+---------+-------+---------+------
Intro   (0-31)   |   ✓   |   ✓    |       |         |       |         |
Verse 1 (32-63)  |   ✓*  |   ✓*   |       |         |   ✓   |   ✓     |  ✓
Pre-ch1 (64-95)  |       |        |   ✓   |         |   ✓   |   ✓     |  ✓
Chorus1 (96-127) |       |        |   ✓   |         |   ✓   |   ✓     |  ✓
Post-ch (128-159)|       |        |   ✓   |   ✓     |   ✓   |   ✓     |  ✓
Instrmtl(160-191)|   ✓   |   ✓    |   ✓   |   ✓     |       |   ✓     |  ✓
Verse 2 (192-223)|       |        |       |   ✓     |   ✓   |   ✓     |  ✓
Pre-ch2 (224-255)|       |        |   ✓   |   ✓     |   ✓   |   ✓     |  ✓
Chorus2 (256-287)|       |        |   ✓   |   ✓     |   ✓   |   ✓     |  ✓
Post-ch2(288-319)|       |        |   ✓   |   ✓     |   ✓   |   ✓     |  ✓
Bridge  (320-351)|   ✓   |   ✓    |   ✓   |   ✓     |       |   ✓     |  ✓
Chorus3 (352-383)|       |        |   ✓   |   ✓     |       |   ✓     |  ✓
Outro   (384-415)|       |        |   ✓   |   ✓     |   ✓   |   ✓     |  ✓
Coda    (416-447)|       |        |   ✓   |   ✓     |   ✓   |   ✓     |  ✓
```

*✓ = plays in EVEN bars only (call-and-response with vocal)

## For our 3-voice SID cover

With only V1/V2/V3 we need to TIME-SHARE:

| Section | V1 (bass/stab) | V2 (lead) | V3 (drums) |
|---------|----------------|-----------|------------|
| Intro   | Pattern A stab (D2, every bar) | (silent) | crash swell |
| Verse   | Pattern A stab (D2, EVEN bars only) | vocal | kick + hat |
| Pre-ch  | Pattern A stab (chord-following) | vocal | kick + hat |
| Chorus  | Pattern B tresillo? or chord pump | vocal | kick + hat + snare |
| Post-ch | Pattern B tresillo (D-A chord) | vocal | kick + hat + snare |
| Instrmtl| Pattern A stab | Pattern B tresillo? | full kit |

