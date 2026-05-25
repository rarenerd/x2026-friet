# Melody theory — FFD chorus structure

Extracted from `docs/song_layers.yaml` and verified against the
[ChordZone tab](https://www.chordzone.org/2023/11/gala-freed-from-desire-chords-and-tabs-for-guitar-and-piano-sheet-music-tabs.html)
and [Hooktheory analysis](https://www.hooktheory.com/theorytab/view/gala/freed-from-desire).

## The chorus is two phrases, alternating

Source beats 88–120 = 8 bars of chorus 1 + post-chorus. The vocal does
exactly two melodic shapes:

### Phrase A — "Freed from de-si-re" (bars 1, 3, 5, 7)

```
beat:   0      0.75   1.5    2.0    2.75
16th:   0      3      6      8      11
pitch:  F5     D5     D5     C5     C5
degree: b3     1      1      b7     b7    (in D minor)
```

A descending three-note motif `F → D → C` (minor 3rd → root → flat 7th),
each note repeated once except the F. Rhythmically it sits on the **3-3-2-3
tresillo** at the 16th level (0, 3, 6, 8, 11 sixteenths) — **NOT** on
8ths. This syncope is the song's hook.

### Phrase B — "Mind and senses purified" (bars 2, 4, 6, 8)

```
beat:   0    0.5  1.0  1.5  2.0  2.5  3.0  3.5
16th:   0    2    4    6    8    10   12   14
pitch:  F5   F5   F5   F5   E5   E5   E5   E5
degree: b3   b3   b3   b3   2    2    2    2    (in D minor)
```

F held four times, then E held four times. Pure straight 8ths. The b3→2
descent resolves the tension created by the b6/b7 chord change underneath
(Bb maj7 in bar 3 of the cycle = the "purified" emotional peak).

## Chord progression underneath

```
bar:    1   2   3   4   5   6   7   8
chord:  Dm  F   Bb  C   Dm  F   Bb  C
phrase: A   B   A   B   A   B   A   B'
```

Four chord cycle Dm-F-Bb-C, repeated. Phrase A always sits on Dm/Bb (minor /
modal mixture); Phrase B always sits on F/C (major). The melody is the same
both halves of the cycle — the chord colour underneath is what shifts the
mood.

## Why this matters for the cover

1. **Phrase A's tresillo IS the FFD signature** — quantizing it to 8ths
   turns the chorus into generic Eurodance and removes what makes the
   song recognisable. The "should we snap to 8ths?" question that's been
   torturing this project is finally settled: NO. Keep the tresillo
   exactly as the karaoke MIDI has it.
2. **The 3-against-4 polyrhythm in the chorus is intentional.** Phrase A
   sits at 3-3-2-3 sixteenths against a 4-on-the-floor kick. That tension
   is the dance-floor hook. Our T5 bass extraction (from beat 120) plays
   THE SAME tresillo (0, 0.75, 1.5 per half-bar), confirming the producer
   built the song around this syncope from the bassline up.
3. **Phrase B is the relief** — straight 8ths, no syncope. The chorus
   alternates tension (A) and release (B). A cover that flattens both into
   the same grid loses the call-and-response.
4. **The melody itself uses only 4 pitches: F5, D5, C5, E5.** It's
   trivially singable — that's why every football stadium picked it up.
   Don't overthink the harmonisation; D minor / F major chord-roots cover
   the whole song.

## Verse vs chorus rhythm

The verse vocal ("My love has got no money…") IS on straight 8ths at the
16th level: positions 0, 2, 4, 6, 8, 10, 12, 14 sixteenths within each
bar. So verse vocals already align with a 4-on-the-floor / 8th-hat
foundation; no quantization decision to make there.

The syncope ONLY appears in chorus Phrase A (and equivalent post-chorus
"Na-na-na" bars 22–24 source which mirror Phrase A's pitch contour).
That's where the rhythm-melody coupling question matters; everywhere
else the song is "already on the grid".

## Implications for the lab

The clean experiment is:
- **Vocal at source timing** (no quantize) — preserves Phrase A tresillo
- **Bass = tresillo synth pattern** (D-A on 0/0.75/1.5 per half-bar) —
  matches the vocal syncope from bar 1, not waiting for T5 at beat 120
- **Drums = 4-on-floor kick + clap on 2/4 + 8th hat** — the HH foundation
  that lets the tresillo float on top as polyrhythm
- **Iconic organ pump** (D5+A5 on every kick) lifted from AUD ch 0/4 —
  this is the missing Eurodance signature

Polyrhythm of 3-against-4 IS what FFD sounds like. Embrace it.
