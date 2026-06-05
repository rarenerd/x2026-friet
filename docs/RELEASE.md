# Release notes — *Friet met Desire*

## Scene metadata

- **Title:** Friet met Desire
- **Group:** deFEEST
- **Composer / coder:** Kloot/deFEEST (Claude), Augurk/deFEEST (Big Pickle / OpenCode) +
  Anus/deFEEST (annejan)
- **Target party:** **X2026** (Dutch Commodore demoparty)
- **Format:** PSID v2 / `out/friet.sid` (release) + `out/friet.prg`
  (standalone C64 player with lyric ticker)
- **Chip:** MOS 8580 (PAL, 985 248 Hz) — PSID flags `0x0024`
- **Player:** 50 Hz IRQ, init at $1000, play at $1003
- **Length:** **1:14** release build (175 BPM); **1:48** song-faithful
  workstage at 120 BPM; loops on reaching the end. See "Structure" below.

## Deliverables — wat we inleveren op X2026

**Muziek-compo = puur geluid**; de visuele versies zijn aparte producties.
Chip: **MOS 8580 / PAL** (PSID flags `$0024`), lengte **1:14**.

| # | Inzending | Bestand(en) | Bouwen | Inhoud |
|---|-----------|-------------|--------|--------|
| **A** | **Muziek-compo** (pure audio) | `out/Friet_met_Desire-deFEEST.sid` + `out/friet_compo.prg` + `out/friet_compo.d64` | `make compo` | PSID v2 + draaibare player met **statisch credit-scherm** — géén ticker/strobe (0 VIC-writes in de SID-body). De `.d64` bevat de player én de rauwe `.sid`. |
| **B** | **Demo** (full-screen Koala) | `out/friet_koala.prg` + `out/friet_koala.d64` | `make koala` | Full-screen KoalaPainter snackbar-plaat (twee-punts-perspectief: patatzak vooraan, toonbank naar neon-titel, frikandel speciaal + kaassouffle op diepte) + de SID + kleur-cycle op de kick. |
| **C** | **Lyrics-floppy** (extra) | `out/friet.d64` | `make disk` | `.d64` met de player mét synced lyric-ticker + kick-strobe + glijdende banners. |

Laden (alle disks): `LOAD"FRIET MET DESIRE",8,1` → `RUN`.
Shareable audio: `make master` → `out/friet.mp3` (192 kbps, +6.8 dB, 8580).
Alles bouwen: `make compo koala disk master`.

Scene-release files: `FRIET.NFO` (credits/inhoud), `docs/hvsc_stub.md`
(Songlengths + STIL, klaar voor HVSC).

Verificatie (headless): de muziek-compo-SID telt **0** `8D xx D0` VIC-writes
(puur audio); de pure-audio player en de lyrics-player zijn beide live in
VICE op 8580 bevestigd (`x64sc -sidenginemodel 257 -pal -autostart …`).

> De muziek-compo wil puur geluid; ticker/strobe zitten **alleen** in
> `friet.prg`/`friet.d64`, nooit in de compo-`.sid`/`friet_compo.prg`.

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
| V1    | **Interleaving organ stab** — T6 grid positions (0, 1, 1.75, 2.5, 3.5 beats per bar) computed per output bar so the bass **never collides with any V2 vocal note**. D2 pedal. Silent in intro/breathe sections. Call-and-response with the vocal. |
| V2    | T7 vocal **VERBATIM** with per-section waveform: **triangle** in verse, **sawtooth+hoover** in chorus, **pulse** in final reprise. Vibrato ±12. Source timing preserved (tresillo intact). |
| V3    | T13 drums **VERBATIM**, section-filtered: verse=kick, prechorus=kick+snare, chorus=full kit. Snare fills in breathe sections. Hat boost (8th on+off) in chorus2/3. Crash swell: long attack ($D), dark pitch (28), 4s gate. |

## Tones

- V1 bass: pulse waveform, PW $0800 (25% duty), sustained envelope.
  Silent in intro/breathe — swell + vocal have room.
- V2 vocal: per-section waveform switching (triangle / sawtooth+hoover /
  pulse). Vibrato ±12 SID freq units (~3 Hz LFO).
- V3 drums: noise with per-kit-piece ADSR; crash swell has long attack
  ($D), dark pitch (28), 4s gate for a proper *whoosh*.

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
with Dutch lyric ticker, 48 lines), and both workstage builds are ready.

Remaining open question: pads / chord rendering with only 3 voices.
V3 is drums-only. Possible future work: ring-modulate V1 against V3
for "chord shimmer".

### Polish items since initial release notes

- ✅ Vibrato on V2 (±12 SID freq units, ~3 Hz LFO)
- ✅ Chorus 2/3 reprises hit harder (breathe sections with snare rolls,
    full 8th-note hats, crash risers before each drop)
- ✅ NulBytesVrij constraint-war lyrics (`docs/nul_bytes_vrij_lyrics.yaml`)
  in the standalone .prg ticker (fallback: TL-Buis → karaoke)
- ✅ Filter LFO wobble (phaser-like modulation of cutoff HI, ±4 steps,
    synchronised to the vibrato LFO)
- ✅ Lyrics appear 1 beat early so the user can read before singing

## Sources used

- Karaoke MIDI: `midi/Gala_Freed_From_Desire.mid` — T2 lyric markers
  cross-validated against T7 to establish that T7 is the vocal melody.
- ossh MIDI: `midi/Gala-freedfromdesire.mid` — 128.5 BPM, 15 tracks,
  473 vocal notes. Source for score transcription and voice essence
  analysis. See `docs/score_transcription.md`, `docs/voice_essence.md`.
- AUD partial: `midi/AUD_RC5718.mid` — 130 BPM, iconic D5+A5 organ pump.
- [Hooktheory](https://www.hooktheory.com/theorytab/view/gala/freed-from-desire):
  key D minor, i-III-VI-VII chord progression.
- [ChordU](https://chordu.com/chords-tabs-gala-freed-from-desire-official-video--id_p3l7fgvrEKM):
  tempo 128.85 BPM, chords Dm-F-B♭-C.
- [pianoletternotes.blogspot.com](https://pianoletternotes.blogspot.com/2019/02/freed-from-desire-by-gala.html):
  cross-reference for the verse "a-a-a" stutter and the chorus "d-d-c-d"
  descending pattern.
