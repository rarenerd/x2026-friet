# HVSC submission stub — Friet met Desire

Ready-to-paste entries for an eventual High Voltage SID Collection
submission of `out/Friet_met_Desire-deFEEST.sid`. Regenerate the md5 and
length whenever the release SID changes (`make compo`).

Proposed HVSC path: `/MUSICIANS/D/deFEEST/Friet_met_Desire.sid`

## Songlengths (DOCUMENTS/Songlengths.md5)

md5 of `out/Friet_met_Desire-deFEEST.sid`, single song, 1:14:

```
a951b7fd3bf811019872233a240f5767=1:14
```

(Regenerate: `md5sum out/Friet_met_Desire-deFEEST.sid`; length =
`length_frames / 50` from the FAST composition, currently 3731 frames.)

## STIL (DOCUMENTS/STIL.txt)

```
/MUSICIANS/D/deFEEST/Friet_met_Desire.sid
   NAME: Friet met Desire
 ARTIST: Kloot, Anus & Augurk (deFEEST)
  TITLE: Friet met Desire
COMMENT: Happy-hardcore cover of Gala "Freed from Desire" (1996),
         released at the X2026 demoparty. MOS 8580 / PAL. Brand voice
         MAYO. A standalone player with a synced Dutch lyric ticker
         ships separately (friet.prg). Cover for a non-commercial scene
         compo; original song (c) Gala.
```

## Notes

- Format: PSID v2NG, flags `$0024` (PAL clock + 8580 model), single SID,
  init $1000 / play $1003, machine-code player (no KERNAL/IRQ deps).
- The compo `.sid` and `out/friet.sid` are byte-identical audio.
