# A theory of the Gala "Freed from Desire" melody

**Working document — challenge it.** Derived from `docs/song_layers.yaml`
(karaoke MIDI T7) cross-checked against
[Hooktheory](https://www.hooktheory.com/theorytab/view/gala/freed-from-desire),
[ChordZone](https://www.chordzone.org/2023/11/gala-freed-from-desire-chords-and-tabs-for-guitar-and-piano-sheet-music-tabs.html),
and the [Wikipedia article](https://en.wikipedia.org/wiki/Freed_from_Desire).

## TL;DR

The whole song is built from **four one-bar melodic phrases** repeated and
recombined over a four-bar chord loop. Every vocal note uses one of six
pitches from the D-natural-minor scale (A4, B♭4, C5, D5, E5, F5). Every
section is 8 bars and consists of alternating bar A / bar B pairs.

If this theory is right, "covering FFD" means: pick the right one-bar
phrase per bar, stack the right chord underneath, put a beat on top.
That's it.

## Universals

| Property | Value |
|----------|-------|
| Key      | **D natural minor** (Aeolian) — no chromatic notes anywhere |
| Time     | 4/4 |
| Tempo    | 130 BPM (original) / 120 BPM (the karaoke MIDI) |
| Pitch set | **A4, B♭4, C5, D5, E5, F5** — six notes, range 8 semitones |
| Chord loop | **Dm – F – B♭ – C** (i – ♭III – ♭VI – ♭VII), 1 chord per bar |

The vocal range sits squarely in chest voice — that's why everyone in a
stadium can shout along.

## The four melodic phrases

(Pitch row is what's sung; the degree row is the scale degree in D
minor; rhythm row shows beat positions inside a 4-beat bar.)

### V-X — "my love has got no" (verse, top half)

```
beat:    0    0.5  1.0  1.5  2.0  2.5  3.25
pitch:   E5   E5   E5   E5   E5   F5   D5
degree:  2    2    2    2    2    ♭3   1
```

Stuttered E5 (the 2nd), one peak up to F5 (♭3), resolve back to D5 (root).
Pure tension-release on the upper scale neighbour.

### V-Y — "he's got his strong beliefs" (verse, bottom half)

```
beat:    0    0.5  1.0  1.5  2.0  2.25
pitch:   D5   C5   C5   C5   C5   B♭4
degree:  1    ♭7   ♭7   ♭7   ♭7   ♭6
```

Mirror image of V-X but a step lower: stuttered C5 (♭7) with a dip to
B♭4 (♭6). Together V-X→V-Y trace out the natural-minor descent E→D→C→B♭
without ever leaving the chord-tones of Dm.

### C-A — "Freed from de-si-re" (chorus, syncope half)

```
beat:    0    0.75   1.5   2.0   2.75
sixteenth: 0    3      6     8     11
pitch:   F5   D5     D5    C5    C5
degree:  ♭3   1      1     ♭7    ♭7
rhythm:  3-3-2-3 sixteenths = TRESILLO
```

The iconic hook. Rhythmically this is a **3-3-2-3 tresillo at the 16th
level** — every onset sits on the 0th / 3rd / 6th / 8th / 11th 16th of
the bar. The pitch contour is the same as V-X→V-Y's descent (♭3 → 1 →
♭7) but compressed into one bar and pinned to chord tones of Dm.

**This tresillo is the signature of the song.** Quantising it to a
straight 8th-grid turns the chorus into generic Eurodance and removes
what makes "Freed from Desire" sound like itself. T5 bass (when it
enters at beat 120) plays the SAME tresillo on its half-bars,
confirming the producer built the song around this rhythm.

### C-B — "Mind and senses purified" (chorus, straight half)

```
beat:    0    0.5  1.0  1.5  2.0  2.5  3.0  3.5
pitch:   F5   F5   F5   F5   E5   E5   E5   E5
degree:  ♭3   ♭3   ♭3   ♭3   2    2    2    2
rhythm:  straight 8ths
```

Four F5s holding (♭3 over an F major chord = chord tone, the calm), then
four E5s (= 2 of D minor / 7th of F major = soft pull back). The release
phrase: no syncopation, just exhale.

## Section structure

| Section | Source beats | Bars | Pattern |
|---------|--------------|------|---------|
| Intro   |   0.0 –  21.5 | 4  | (no vocal) |
| Verse 1 |  21.5 –  54.5 | 8  | V-X, V-Y, V-X, V-Y, V-X, V-Y, V-X, V-Y |
| Pre-chorus 1 | 54.5 – 88.0 | 8 | uses 2 more shapes (see below) |
| Chorus 1 | 88.0 – 117.5 | ~7 | C-A, C-B, C-A, C-B, C-A, C-B, C-A, (C-B short) |
| Post-chorus na-na | 117.5 – 149.5 | 8 | V-X, V-Y, V-X, V-Y, V-X, V-Y, V-X, V-Y |
| Verse 2 + Pre-chorus 2 + Chorus 2 + outro: same blocks recycled |

**Verse and post-chorus na-na are the same melodic shape.** The "Na na
na na na" *is* the verse's vocal contour with different lyrics. That's
why the chorus → na-na transition feels seamless — it's not a new tune,
it's the verse coming back at peak energy.

## Pre-chorus extras (2 more shapes for completeness)

The pre-chorus inserts two pickup shapes between V- and C-phrases:

### PC-X — "want more and more"

```
beat:   0    0.5  0.75  1.5
pitch:  A4   C5   D5    D5
degree: 5    ♭7   1     1
```

The only place where A4 (the 5) appears in the whole song. Acts as a
**ascending pickup**: 5 → ♭7 → 1 → 1, climbing into the chorus.

### PC-Y — "people just want more and more" (sustained D variant)

D-D-C-D-D-C-D weaving on roots & ♭7. A held / weaving D pedal that
contrasts the verse's stuttered Es.

## The grand simplification

If we strip the song to its skeleton: **6 one-bar melodic phrases over a
4-bar chord loop, arranged in 8-bar blocks**. That's ~50 seconds of
unique melodic content stretched to 3.5 minutes by alternation and
repetition.

For the SID cover this means we have a tiny vocabulary to encode:
- 6 pitch sequences (max 8 notes each)
- 1 chord cycle (4 chords)
- 2 rhythm flavours (straight 8ths + tresillo)

Anything more complex than that is over-engineering — the song is
literally this simple.

## Implications for the rhythm section

Phrase **C-A is in tresillo** while everything else is in 8ths. So the
underlying drum/bass must accommodate BOTH:

- **Straight 8th foundation** (4-on-floor kick, 2/4 backbeat, 8th hat)
  works for V-X, V-Y, C-B, PC-X, PC-Y, the entire na-na, and the verses.
- **C-A's tresillo plays over the straight foundation** — that's the
  3-against-4 polyrhythm everyone recognises but few can name. It's NOT
  a problem to solve; it's the song.

The producer reinforces this by having the bassline (T5) ALSO play the
tresillo (3 hits per half-bar at 0, 0.75, 1.5). So in the chorus you get
two layers in 3-feel (vocal + bass) sitting on the 4-feel drum bed.

## Implications for the cover

1. **Encode the 6 phrases explicitly** as `(beats, pitches)` tuples in
   `compose.py`. Don't try to "compute" the melody from a contour seed —
   just write down what it is.
2. **Don't quantise C-A's tresillo to 8ths.** Half this project's pain
   came from trying.
3. **Verse / na-na share a shape** — define it once.
4. **Pre-chorus is the only place A4 appears** — it's the lift before
   the chorus. Treat it as the dynamic build.
5. **Add the iconic D5+A5 organ pump** (from AUD_RC5718.mid ch 0/4) as a
   chord stab voice — that's what's missing from our karaoke MIDI and
   the reason our cover sounds thin.

## Iconic non-vocal layers (the bits we've been ignoring)

The karaoke MIDI has three more layers with strong character that we
haven't yet pulled into `song_layers.yaml`:

### T6 — Drawbar Organ (verse / instrumental D-pedal stab)

345 notes. Plays only in verse-1 and instrumental sections (source
beats 0–63 and 144–255). Each note is a **triple-octave D unison**:
D4 + D5 + D6 hit simultaneously. The rhythm per bar:

```
beat:        1    2    2.75    3.5   4.5
16th index:  0    4    7       10    14
intervals:   4    3    3       4
```

Five stabs per bar at positions 0, 4, 7, 10, 14 sixteenths (a
"4-3-3-4" interval pattern — Charleston-flavoured but inverted). This
**is the verse signature** — the "thump-thump stab-stab stab" you
remember from FFD's verses. Our cover's verses feel empty because we
omitted this.

### T4 — Acoustic Grand Piano (pre-chorus & verse 2 chord pad)

622 notes. Plays four-note sustained chord voicings, one chord per
bar, in pre-chorus 1 (beats 56–87) and the verse-2 region (248–279).
Confirms the chord progression: D → C/D-or-Dm9 → B♭ → C, with each
voicing held for the full bar. The voicings include the chord ♭7s
and 9ths (D-C-E-A on the "C/D" bar) — clearly modal mixture rather
than triadic.

### T8 — Synth Strings (sustained pad)

132 notes. Three-note pad voicings sustained per bar across pre-chorus
and chorus and na-na (56–149, 248–340). Reinforces the chord-tone
fundamental + 3rd + 5th of each chord. The "smoothness" layer that
glues the verse-to-chorus transition.

### Wiring into a 3-voice SID

We can't reproduce the full T4/T6/T8 stack on 3 voices, but we can
borrow elements:

- **T6's rhythm IS usable on V1 (bass)**: play a single D2 (or octave
  bounce D2/D3) on the 0, 4, 7, 10, 14-sixteenth pattern during
  verses. Captures FFD's verse stab without needing the triple-octave.
- **T4/T8 chord voicings can drive an arpeggio** on V2 during
  pre-chorus when the vocal is sparse: cycle root-3rd-5th of the
  current chord on 8th notes (cheap pad substitute).
- **The iconic D5+A5 organ pump from AUD_RC5718.mid** (per
  `docs/midi_sources.md`) is a *different* layer — chorus-only stabs.
  T6 and AUD's organ are two complementary signatures.

## The interleaving bass discovery

Analysis of the ossh MIDI (`Gala-freedfromdesire.mid`, see
`docs/voice_essence.md`) revealed that the T6 organ stab grid (positions
0, 1, 1.75, 2.5, 3.5 beats per bar) **never collides with any vocal note
in T7**. The bass and vocal operate as call-and-response: the bass fills
the gaps where the voice breathes. This is baked into the song's DNA —
not a coincidence. The SID arrangement exploits this by computing V1
bass positions per output bar to guarantee zero collisions with V2.

## Things this theory is uncertain about

- **Whether the karaoke MIDI's C-A tresillo is accurate or
  transcriber-licensed**. Multiple chord-tabs simplify the chorus to "one
  syllable per beat", which would imply a 4-on-the-floor melody too. But
  T5 also plays the tresillo — and T5 was transcribed by a different
  hand than T7. Two independent transcribers agreeing is decent
  evidence. Counter-evidence welcome.
- **B♭4 vs B4 at the end of V-Y**. The MIDI says MIDI 70 = A♯4/B♭4 (♭6
  in D minor). That fits D Aeolian. But some sheet-music transcriptions
  show this as B4 natural (= 6, D Dorian). The song does sound Aeolian
  to my ear, so we go with B♭4. Could be checked against the radio mix.
- **The "♭III" chord interpretation**. We call bar 2's chord F (=♭III in
  D minor / I in F major); some sources call the same chord D minor 7
  with F in the bass. Either way the notes are the same; the
  Roman-numeral label differs.

If you spot a problem with any of the above: drop a note in the
project root or open an issue, and we'll re-derive.
