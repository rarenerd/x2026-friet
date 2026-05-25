# Rhythm research — Freed from Desire chorus

Notes gathered while solving the "drums and melody don't vibe" problem in
the FAST=175 build. Cross-references between our karaoke source MIDI and
external transcriptions / remix culture.

## Established facts (cross-source consensus)

| Attribute      | Value         | Sources |
|----------------|---------------|---------|
| Tempo          | 129–130 BPM   | [GetSongBPM](https://getsongbpm.com/song/freed-from-desire/wmnAN8), [SongData.io](https://songdata.io/track/5n56ImOTTDbUORTq3Eyong/Freed-from-Desire-by-Gala), [Tunebat](https://tunebat.com/Info/Freed-from-Desire-Gala/3Ucr6hQQuY8cZ0UqXV8uO2) |
| Time signature | 4/4           | All sources |
| Key            | D minor (7A)  | All sources |
| Chords         | Dm – F – Bb – C (one per bar) | [Hooktheory](https://www.hooktheory.com/theorytab/view/gala/freed-from-desire), [ChordZone](https://www.chordzone.org/2023/11/gala-freed-from-desire-chords-and-tabs-for-guitar-and-piano-sheet-music-tabs.html) |
| Iconic chorus  | Syncopated "Freed-from-de-si-re" — Pop Rescue calls it the "ner ner ner ner-ner ner her" hook | [Wikipedia](https://en.wikipedia.org/wiki/Freed_from_Desire) |

Our `friet.sid` is at 175 BPM, which sits inside the genre-typical
160–180 BPM happy-hardcore range (gabber covers push 180–200+, e.g.
[Claybay Gabber RMX](https://claybay.bandcamp.com/track/freed-from-desire-gabber-rmx)).

## Karaoke source MIDI — verified analysis

`docs/song_layers.yaml` reports **422 vocal events, all on the 16th-note
grid (0/422 off-grid)**. The chorus phrasing repeats:

```
Bar A (syncopated):
  "Freed   from   de    si    re"
  beat:  0    0.75  1.5   2    2.75      (3 sixteenths apart, 3-against-4 feel)

Bar B (straight 8ths):
  "Mind  and  sens es  pu  ri  fied"
  beat:  0   0.5  1  1.5  2  2.5  3  3.5  (clean 8ths)
```

The "0, 0.75, 1.5, 2, 2.75" pattern in Bar A is the **signature rhythm**
of the song. Quantizing it to an 8th-grid flattens the chorus into
generic Eurodance and removes the FFD character.

T13 drums in the source: only **1 kick in 12 beats** of chorus (FFD has
a half-time-feel kit). That sparseness is what made our 175 BPM render
without a kick overlay feel like rattling buckets. With a 4-on-floor
overlay it feels rigid because the kick fires on the integer beats
(0, 1, 2, 3) while the singer floats around 0.75 and 2.75 — they never
coincide.

## Remix culture for cross-reference

| Remix | Notes |
|-------|-------|
| [Hak op de Tak — "Frietfromdesire" (Dutch hardcore bootleg)](https://soundcloud.com/hakopdetaknl/frietfromdesire) | Literally the same fries-pun as this project. Couldn't extract production details via fetch; worth a manual listen. |
| [Claybay — Gabber RMX (Korg EMX + Protracker 2)](https://claybay.bandcamp.com/track/freed-from-desire-gabber-rmx) | Bandcamp release 2025-06-03. Gabber tempo (180+). |
| [Shagos — 4x4 Remix](https://shagproductionz.bandcamp.com/album/freed-from-desire-remixes) | Straight 4-on-floor cover. |
| Football chant ("Will Grigg's on Fire", 2016) | Simplifies the vocal to crowd-singable downbeats — proves the chorus melody is recognisable at any rhythmic resolution. |

No free RTTTL / Nokia Composer transcription was findable; standard
ringtone archives only carry MP3/M4R versions
([PHONEKY](https://phoneky.com/ringtones/?id=m88312),
[ZEDGE](https://www.zedge.net/find/ringtones/freed%20from%20desire)).
MuseScore has free piano and violin arrangements
([song page](https://musescore.com/song/freed_from_desire-1689170)) but
the site rejects unauthenticated fetches; the user can download a PDF
manually for a paper cross-check.

## Working hypothesis for our drum-melody disconnect

The 4-on-the-floor kick overlay at integer beats fights the chorus's
3-against-4 syncope. Three approaches to test:

1. **Vocal-locked kicks in chorus** — derive kick positions per output
   bar from the actual vocal onsets in that bar. Bar A becomes
   kicks at 0, 0.75, 1.5, 2, 2.75; Bar B becomes 0, 0.5, 1, 1.5, ...
   (capped at 6/bar). Maximally couples drums to melody but at risk of
   feeling like a "drum-following-singer" novelty instead of a groove.
2. **Hybrid: 4-on-floor + accent on syncope** — keep [0,1,2,3] kicks
   but add a "ghost" kick at 0.75 and 2.75 in chorus bars only. Six
   kicks per chorus bar; the syncope is *acknowledged* without losing
   the HH foundation.
3. **Phrase-aware: detect bar type, swap pattern** — bar A uses
   vocal-locked, bar B uses 4-on-floor. Requires a per-bar
   classification step.

Currently testing approach **#1** (vocal-locked everywhere in chorus
segments). If too "song-y" and not enough "rave", fall back to #2.

## Result of approach #1 (2026-05-23)

Implemented in `src/compose.py` in the FAST=1 path. Per-segment kick
strategy:

| Segment           | Kick pattern                              |
|-------------------|-------------------------------------------|
| intro / breathes  | (silent, T12 swell only)                  |
| verse1 / prechorus1 | 4-on-the-floor `[0, 1, 2, 3]`            |
| chorus1 / postchorus / chorus2 / chorus3 | vocal-locked: kicks at every vocal onset within each bar, plus a downbeat anchor, capped at 6/bar |

In FAST mode the T13 verbatim drum loop now skips its own kicks (the
overlay supplies them), avoiding double-triggers at any frame where
T13's kick and the synth kick coincide. T13's snares/claps/hats stay.

Drum stats (FAST=1, 55 bars):

| kind  | total | per bar |
|-------|-------|---------|
| kick  | 224   | 4.07    |
| snare | 267   | 4.85    |
| hat   | 239   | 4.35    |
| crash | 7     | 0.13    |

Bar-1 chorus sanity check: vocals at output frames 1509 / 1521 / 1534 /
1543 / 1556 (positions 88.0 / 88.75 / 89.5 / 90.0 / 90.75) all coincide
exactly with kick frames. The 3-against-4 chorus syncope drives the
kick.

Open questions:
- Does this feel like "drum locked to singer" (great) or "drum
  parroting singer" (gimmicky)?
- In Bar B (straight 8ths chorus bars: "Mind and senses purified"),
  the 6-kick cap eats kicks 6.5 and 7.5 — Bar B might benefit from
  reverting to 4-on-floor.
- T13's snare is 4.85/bar — that's clap+snare38+snare40 stacking on
  the same hit. If too dense after this fix, deduplicate by mapping
  all three to a single "snare" with hit-time grouping.

## Result of approach #1, iteration 2 (2026-05-23)

User feedback after iteration 1: *"it's like one is on 3s and the other
on 4s or whatever . . it's very much not cohesive"*.

The "one on 3s the other on 4s" perception is exact: bar A of the
chorus has the vocal at 3-3-2-3 sixteenth intervals (tresillo-extended
"3 feel"), while T13's snare hits the 2-and-4 backbeat (clean "4
feel"), and our added kick was on the vocal grid. **Three competing
grids at once** = polyrhythm chaos at 175 BPM.

Refined approach for cohesion: **in chorus segments, drop T13 entirely**
(no snare, no hat, no clap) and emit *only* a kick on each vocal onset.
One voice, one grid, one phrase. Verses and pre-chorus keep T13's full
percussion + 4-on-floor — the polyrhythm there is fine because the
verse vocal IS on 8ths.

Code: `src/compose.py` `in_chorus_src()` check filters T13 events out
in chorus, plus V3 is a mono noise voice so we don't bother stacking
multiple drum kinds on the same vocal frame (they'd just overwrite).

Result drum stats (FAST=1, 55 bars):

| kind  | total | per bar |
|-------|-------|---------|
| kick  | 224   | 4.07    |
| snare | 57    | 1.04    |
| hat   | 126   | 2.29    |
| crash | 7     | 0.13    |

Chorus1 bar 1 dump: 6 vocal hits → 6 kick hits, all on identical
frames. No competing percussion.

If still incoherent: the issue isn't the grid (we've eliminated
polyrhythm), it's that the genre-cocktail itself is wrong — HH wants
4-on-floor, FFD chorus wants syncope. Possible follow-ups: drop FAST
tempo back to 150 BPM (less hectic), or quantize vocal to 8ths and
accept the loss of FFD signature (the football-chant approach).

## Iteration 3: the karaoke MIDI is wrong about bar A (2026-05-23)

User feedback: *"the song is super simple . . it's euro-trash . . so
every vocal hits the beat for extra meezing kwaliteit . . it's a
stadium (or rather gymzaal) sing-along"*.

Cross-checking against external tablature — [ChordZone analysis](https://www.chordzone.org/2023/11/gala-freed-from-desire-chords-and-tabs-for-guitar-and-piano-sheet-music-tabs.html)
states explicitly:

> The phrase "Freed from desire" typically lands on beats 1–4 of the
> bar (with "Freed" hitting beat 1 on the chord change), while "mind
> and senses purified" is sung as a quicker rhythmic phrase across
> the following bar.

So the actual chorus is **one syllable per beat** (a clean four-beat
sing-along), not the karaoke MIDI's 16th syncope (0, 0.75, 1.5, 2,
2.75). The karaoke MIDI was wrong — its bar A is a transcription
artefact, not the real Gala melody. The football-chant adaptations
("Will Grigg's on Fire", 2016, [origin](https://www.skysports.com/football/news/11682/10294085/will-griggs-on-fire-fan-reveals-inspiration-behind-chant))
work *because* the chorus is already chant-rhythmed in the original.

Bar B ("Mind and senses purified") was transcribed correctly — it
really is on straight 8ths.

**Fix:** snap the vocal to the 8th-grid in FAST mode. That pulls bar
A's syncope onto the beat (0.75 → 1, 2.75 → 3) and leaves bar B
unchanged. Verse vocals (all on 8ths in the source) are also unchanged.

Result (chorus1 bar 1, snapped, FAST=1):

| Vocal beat | Drum hits at same frame | Bass at same frame |
|------------|-------------------------|--------------------|
| 1.0 "Freed"| kick                    | —                  |
| 2.0 "from" | kick + snare            | —                  |
| 2.5 "de"   | hat                     | yes (off-beat 8th) |
| 3.0 "si"   | kick                    | —                  |
| 4.0 "re"   | kick + snare            | —                  |

Every vocal onset lands on a drum or bass hit. Drums, bass and vocal
share one 8th-grid. Workstage (clean.sid) keeps the original karaoke
timing — useful for A/B'ing the chant-rhythm against the source
transcription.
