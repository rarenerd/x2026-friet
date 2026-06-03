# Sound engine — how friet.sid actually plays (the "new standard")

The science behind the 2026-05-30 build that Anus signed off as "the new
standard — it rocks on all levels". This documents the *playback/synthesis*
layer: how `compose.py` turns verified source layers into timed events, and
how the `synth.py` 6502 player voices them on the SID. For the *musical*
source analysis see `voice_essence.md`, `score_transcription.md`,
`rhythm_research.md`.

Voices: **V1** = bass/organ/hook (pulse), **V2** = lead/vocal (per-section
waveform, filtered), **V3** = drums (noise + per-hit ADSR).

---

## 1. One beat→frame grid for every voice

At 175 BPM a 16th note is `120/7 ≈ 17.14` frames per beat — not an integer.
If each voice rounds independently (`round(beat * fbeat)`), they each pick up
±0.5-frame error that drifts *differently* per voice, so notes that should
hit the same beat end up 1+ frames apart — a flam that wanders through the
song.

The fix is a single shared grid built once by integer (Bresenham) accumulation:

```
_num = 3000 (frames/min) ; _den = bpm*4 (16ths/min) ; reduce → 120/7
frame = 0 ; rem = 0
for each 16th i:  grid[i] = frame ; rem += _num ; frame += rem // _den ; rem %= _den
grid_frame(beat) = grid[round(beat * 4)]      # snap to the nearest 16th
```

Zero global drift, and — crucially — **every voice goes through
`grid_frame()`**: lead, bass, organ, hook, *and* drums + every FX hit. The
original bug had the drums on `round(beat * fbeat)`; ~30 % of the source drum
hits sat off the 16th grid (e.g. beat 8.992 instead of 9.0) and flammed
against the grid-snapped lead. Same grid → locked groove. *(AGENTS.md pitfall 9.)*

Snapping to 16ths preserves the tresillo (3+3+2 sixteenths) — it does **not**
quantize the feel away; it only removes transcription jitter.

---

## 2. The lead: legato-fill + hard-restart retrigger

The source vocal (T7) is a list of short transcribed syllables. Played
verbatim you get *blip … silence … blip* — 116 of 274 notes were ~80 ms, with
0.2–0.7 s of silence between almost every one. The melody didn't sing, didn't
pop, and "floated" with no transient locking it to the beat.

Two coupled fixes, both load-bearing:

**Retrigger every note.** The old player did legato — on a pitch change it
updated the frequency *without* re-gating, so most syllables had no attack
transient (the SID skips a new attack while the gate is already high). Now
every note re-gates (gate off → on), so each onset is an audible, accented
articulation. *(This is the same envelope law the drums obey — see the demo
repo's `docs/sid-drums.md` "Hard restart".)*

**Legato-fill, minus 2 frames.** Each note's duration is extended to the next
note's onset so the line is continuous — but stopping **2 frames (~40 ms)
short**:

```
gap = next_onset - this_onset
dur = max(1, gap - 2)        # fill to next note, leave a 2-frame gate-off
```

The 2-frame gate-off is the catch: if notes butt frame-to-frame, the retrigger
toggles gate off→on *within one frame*, the envelope never gets a frame to
fall, the hard-restart fails, and notes glitch or barely sound. The ~40 ms gap
is inaudible but gives a real hard-restart window. Result: continuous **and**
accented — 116 blips → 0, 21 silent gaps → just the 2 deliberate chorus drops.
*(AGENTS.md pitfall 10.)*

Genuine rests (gap > `SECTION_REST` ≈ 3.5 beats — only the chorus drops exceed
this) are preserved: the note rings ~1 beat then the voice rests.

---

## 3. Per-section timbre and the octave-up climax

The arrangement is the deFEEST hardcore edit: verse → pre → chorus once, then
the **3× "Freed met Desire"** climax (chorus replayed three times). To stop the
thrice-played hook wearing thin, each reprise has its own character:

| Section   | Waveform (`ctrl`) | Transpose |
|-----------|-------------------|-----------|
| verses    | `$10` triangle    | —         |
| chorus 1  | `$20` saw (hoover)| —         |
| chorus 2  | `$40` pulse       | —         |
| chorus 3  | `$20` saw         | **+12**   |

- **chorus 3 octave-up (+12)** lifts the final drop above the others = climax.
- **chorus 3 is saw, not `$50`.** Combined waveforms AND-combine the two
  waveform outputs; `$50` (tri+pulse) is thin and partly cancels, *dropping
  notes* — that was the "missing notes" in the final chorus. Anything that must
  read clearly uses a single waveform. *(AGENTS.md pitfall 11.)*

---

## 4. The flange (resonant filter sweep) — V2 only

The lead is routed through a resonant low-pass. Each note resets the cutoff to
`$C0` (open) and `filter_env` decays it toward `$60` while a triangle LFO
(`filt_lfo`, shared phase with the vibrato) wobbles it ±6 — the "flangey /
hoover whoosh".

**Tuned for the MOS 8580.** The 8580's cutoff curve is near-linear and shifted
up, and its resonance is stronger/sharper than the 6581's. So the values run
one notch gentler than the 6581 sweet-spots: **res `$7` + LFO `±6`**, cutoff
init/target `$60`, per-note open `$C0`. (On 6581 these were res `$8`, ±10,
`$80`/`$E0` — but the release ships 8580, PSID flags `0x0024`.) Push resonance
or LFO higher and the peak overpowers the fundamental — the melody muddies and
notes go "barely there". Render/verify on 8580 (`vsid -sidenginemodel 257
-pal`), never the VICE-default 6581. *(AGENTS.md pitfalls 4 & 12.)*

---

## 5. Bass pluck and drum hard-restart

- **V1 bass** uses an aggressive pluck envelope — attack `$0` (2 ms, instant
  transient on every note), decay `$8` down to sustain `$6` (~40 %), so each
  note *thwacks* then drops to a lean body instead of holding flat. A
  continuous PWM sweep (`pwm_sweep`) adds chorus-like movement.
- **V3 drums** retrigger per hit (gate off then on) — the same hard-restart the
  lead needs. The kick is pitch-swept (2 frames high triangle → noise body).

---

## 6. Length, loop, and the smooth ending

- **`length_frames` = last actual event + a ~½-bar tail**, not the old
  synthetic `total_bars * fpbar`. The synthetic length padded every voice with
  rests out to the loop sentinel — ~2 minutes of dead air before the tune
  looped. The SID now loops cleanly right after the music (correct for a
  demoparty release). *(AGENTS.md pitfall 13.)*
- **The shared MP3** is rendered to exactly the song length with an `afade`-out
  (`render-preview.sh … <secs> <fade>`) for a smooth close instead of a hard
  cut into the loop point. The SID itself is not faded.
- **Gotcha:** `render-preview.sh` must not name its duration variable
  `SECONDS` — that's a bash special variable (elapsed time since assignment),
  so reading it after the render `sleep` returns the wrong value and silently
  breaks both `-t` and the fade. It's named `DUR`.

---

## 7. Build / render quick reference

```sh
make friet                  # release SID (FAST=1, 175 BPM) -> out/friet.sid
                            # NB: leaves docs/composition.yaml at CLEAN tempo
# To render the release MP3 at its true length + fade:
FAST=1 .venv/bin/python src/compose.py                       # FAST composition
FASTSECS=$(python -c "import yaml,math;print(math.ceil(\
  yaml.safe_load(open('docs/composition.yaml'))['length_frames']/50))")
tools/render-preview.sh out/friet.sid out/friet.mp3 "$FASTSECS" 10
```

Release is ~75 s at 175 BPM. `make friet` rebuilds the CLEAN composition last,
so always regenerate the FAST composition before reading the release length.
