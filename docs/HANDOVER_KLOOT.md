# Handover → Kloot: friet-demo als hidden part in de kloten-demo

**Voor:** Kloot/deFEEST (coder)
**Van:** deze repo (`x2026-friet`)
**Doel:** de nieuwe one-file friet-demo inharken als **hidden part** in
`outline26-claude-c64` ("Kloten met de broodtrommel").
**Datum:** 2026-06-06

---

## 1. Wat je krijgt

Eén self-contained C64 programma dat de hele part draait — bitmap +
sprites + lyric-ticker + muziek, alles in zichzelf:

| Bestand | Wat | Bouwen |
|---|---|---|
| `out/friet.prg` | **De part** (loadt `$0801`, start `SYS 2064` = `$0810`) | `make koala` |
| `out/friet.sid` | Losse SID, mocht je alléén de muziek willen | `make friet` |

Build vanaf scratch: `make friet koala`. Geen handmatige stappen.

De part is sinds de vorige versie flink veranderd: dode 50Hz-interlace
eruit (1KB lichter), grijze raster-split-leak gefixt, **8 kubussen die op
elke kick door een rave-palet flitsen**, en de lyrics hebben nu de
iconische "na na na"-meezing-sectie. `.prg` is nu **33667 bytes**
(`$0801`–`$8B84`).

---

## 2. Geheugen-footprint (LEES DIT)

De part claimt vrijwel de hele machine. Statische data + code:

```
$0801–$080F  BASIC-stub (SYS 2064)
$0810–...    code
$1000–$43C5  SID body          (init $1000, play $1003)
$4400–$4BFF  sprite_cube       (32 rotatieframes, ptrs 16..47)
$6000–$7F3F  koala_bitmap      (8000 b)
$7F40–$8327  koala_screen src  (1000 b, wordt naar $5C00 gekopieerd)
$8328–$870F  koala_color src   (1000 b, wordt naar $D800 gekopieerd)
$8710        koala_bg          (1 b)
$8720–$8B84  lyric_table       (+ $FF,$FF,$00 sentinel)
```

Runtime-scratch (NIET in de .prg, wordt door de init geschreven):

```
$4C00–$4FFF  tekstscherm (lyric-rows 22..24)
$5000–$57FF  RAM-font    (gekopieerd uit char-ROM $D800 — char-ROM is
                          onzichtbaar in VIC-bank 1, vandaar)
$5800–$5BFF  VRIJ (1KB)  ← was interlace screen B, nu ongebruikt
$5C00–$5FFF  bitmap-kleurscherm + $5FF8 sprite-pointers
$D800–$DBFF  colour-RAM
ZP: $90–$9C, $A0–$A3
```

Hard claims die met de host botsen:
- **VIC-bank 1** (`$4000–$7FFF`) via `$DD00`.
- **Kernal-IRQ-vector** `$0314/$0315` (twee raster-IRQ's, zie §4).
- Het draait een eigen `sei … cli … jmp *` hoofdloop — **het geeft geen
  controle terug** (zie §3).

---

## 3. Integratie-strategie — kies er één

### A. Takeover (snel, aanbevolen voor een hidden part)
Laad `friet.prg` als los bestand en spring erin met `JMP $0810` (sla de
BASIC-stub over). De part neemt de machine over en draait z'n eigen IRQ.
Voor een *hidden* part is dat meestal prima: je triggert 'm met een
easter-egg-key, hij draait, en de "exit" is een reset/herlaad van de host.

- Voordeel: nul refactor, exact wat nu live getest is.
- Nadeel: geen nette terugkeer; host-state is weg. Plan de part dus als
  eindbestemming of herlaad de host erna.

### B. Refactor naar init + driver (als de part móét terugkeren)
Splits `entry:` in een `init` (alles behalve `sei/cli/jmp loop`) en laat de
host-framework de twee IRQ-handlers (`irq_top` / `irq_split`) aanroepen.
Dan kun je netjes opzetten en weer afbreken.

- Voordeel: coëxisteert met een host-loop / part-scheduler.
- Nadeel: meer werk; de part installeert nu zélf de raster-IRQ's en
  verwacht VIC-bank 1 — die overdracht moet je expliciet regelen.

**Mijn advies:** begin met **A**. Werkt het als hidden part, dan klaar.
Heb je een echte part-keten met transitions nodig, dan pas **B**.

---

## 4. Hoe de part intern tikt (voor als je 'm aanraakt)

- **Twee raster-IRQ's** (`src/player/friet_koala.asm`):
  - `irq_top` (regel `TOPL`=251): multicolor-bitmap aan, draait het frame
    (SID-play, `fly`, `spin`, `tick_scene`, `lyric_tick`, kick→border +
    `flash_cubes`), telt `frame_lo/hi` op.
  - `irq_split` (regel `SPLIT`=225): hires-tekst voor de onderste 3 rijen
    (lyric-ticker, wit-op-zwart).
  - ⚠️ **`$D021` is de EERSTE write in `irq_split`** — anders lekt de
    grijze bitmap-bg op de rechterkant van de split-regel. Niet omgooien.
- **8 hardware-sprites = vliegende, draaiende 3D-kubussen.** `fly` =
  sinus-orbit (`xtab`/`ytab`), `spin` = pointer door 32 frames,
  `flash_cubes` = kleur-rave op de kick.
- **Escalatie-arc** (`tick_scene`): 2→4→6→8 kubussen + 2× stretch op de
  climax, gestuurd door de frame-teller en geresynced op het song-loop-punt
  (`$0E93`). Dus de visuals hangen aan de muziek-timing — als je de SID
  vervangt door een andere lengte, herijk de `sc_blo/sc_bhi`-grenzen.
- **Chip:** MOS 8580 / PAL, PSID-flags `$0024`. Draai/test met
  `x64sc -sidenginemodel 257 -pal`.

---

## 5. Concrete actie-items

1. In `outline26-claude-c64`: `update-friet.sh` draait nu `make player`
   (de oude lyric-only player). **Zet dat om naar `make koala`** en kopieer
   `out/friet.prg` (de demo) — niet `out/friet_lyrics.prg`.
2. Reserveer in de host-memorymap `$0801–$8B84` + VIC-bank 1 + colour-RAM
   voor de part (zie §2), of laad 'm als losse overlay (strategie A).
3. Nieuwe **koala-art komt eraan**: Anne Jan schildert een nieuwe Miep +
   sigaar-Harry compositie in Multipaint. Die wordt hier ingedraad via
   `make koala` (`tools/mix_koala.py`) — de `.prg` blijft op hetzelfde
   adres laden, dus jouw integratie verandert daar niet door. Pull gewoon
   opnieuw en herbouw.

---

## 6. Vragen / open punten

- Wil je de part als **volledige takeover** of moet 'ie terugkeren naar de
  host-keten? (Bepaalt A vs B.)
- Moet de SID-loop **naadloos** doorlopen onder een langere part-keten, of
  is een harde cut bij de transition oké?
- De 1KB op `$5800` is nu vrij — claim 'm gerust als je host daar iets
  kwijt moet, maar laat het weten zodat ik 'm niet per ongeluk terugpak.
