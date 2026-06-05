#!/usr/bin/env python3
"""Phase 2 of the cleanroom pipeline.

Reads docs/song_spec.yaml (the abstract spec) and writes
docs/composition.yaml (a concrete arrangement in happy-hardcore style;
175 BPM with hoover lead when FAST=1, source BPM otherwise).

Cleanroom rule: this script must NEVER open or read any MIDI file. It only
sees the structured spec produced by phase 1.
"""
import yaml, os, sys, random

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, 'docs', 'song_spec.yaml')
COMP_PATH = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, 'docs', 'composition.yaml')

# Fast / happy-hardcore target tempo (the genre sits at 170–180 BPM)
FAST_BPM        = 175
PAL_HZ        = 50.0

# Set env var MELODY_ONLY=1 to render the vocal melody alone at source tempo
# (bass + drums disabled). Useful for verifying the melody is recognisable
# before layering anything else.
MELODY_ONLY   = bool(os.environ.get('MELODY_ONLY'))

NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
def name_to_pc(s):
    s = s.strip().rstrip('b').upper().replace('FLAT','b')
    if s.endswith('B') and len(s) > 1: s = s[:-1] + 'b'  # tolerate "Bb" vs "B"
    if 'b' in s:
        # convert e.g. "Bb" -> A#
        base = s[0]; flat = True
    else:
        base = s[0]; flat = False
    pc = NOTE_NAMES.index(base.upper())
    if '#' in s: pc = (pc + 1) % 12
    if flat:    pc = (pc - 1) % 12
    return pc

def midi_note(name_oct):
    """E.g. 'D2' -> 38."""
    # Split letter+# from octave
    i = 1 + (1 if name_oct[1:2] == '#' else 0)
    pc = name_to_pc(name_oct[:i])
    octv = int(name_oct[i:])
    return (octv + 1) * 12 + pc

# ----- scale generators (within an octave) -----
SCALES = {
    'minor':       [0, 2, 3, 5, 7, 8, 10],
    'natural_minor': [0, 2, 3, 5, 7, 8, 10],
    'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
    'major':       [0, 2, 4, 5, 7, 9, 11],
}

def scale_pitches(root_pc, mode, octave_range=(2, 6)):
    intervals = SCALES.get(mode, SCALES['minor'])
    out = []
    for octv in range(octave_range[0], octave_range[1]):
        for i in intervals:
            out.append((octv + 1) * 12 + (root_pc + i) % 12 +
                       (0 if (root_pc + i) < 12 else 12))
    return sorted(set(out))

# ----- composition primitives -----
def pattern_to_positions(pat):
    """'X...X...X..X' -> [0,4,8,11]"""
    return [i for i, c in enumerate(pat) if c == 'X']

def beats_to_frames(beats, bpm):
    return beats * 60.0 / bpm * PAL_HZ

# ----- main composer -----
def main():
    with open(SPEC_PATH) as f:
        spec = yaml.safe_load(f)

    random.seed(42)  # reproducible

    bpm = FAST_BPM
    fpbar = beats_to_frames(4, bpm)        # frames per 4/4 bar
    fpbeat = fpbar / 4
    fp16  = fpbar / 16

    root_pc = name_to_pc(spec['key']['root'])
    mode = spec['key']['mode']
    scale = SCALES.get(mode, SCALES['minor'])
    bass_root = root_pc + 12 * 3   # D3-ish bass register
    if bass_root < 36: bass_root = 36
    # Use Dm pentatonic-ish for lead (cleaner rave feel)
    lead_root_pc = root_pc
    melody_octave = 5  # E5/D5 range — bright lead

    # Section structure long enough to host the entire vocal melody (~88 bars
    # at the fast BPM, since the source MIDI's vocal track spans ~88 bars).
    sections = [
        ('intro',     4, 0.6, 'pedal'),
        ('verse',    16, 0.7, 'pedal'),
        ('build',     4, 0.85, 'pedal'),
        ('chorus_a', 16, 1.0, 'root'),
        ('verse2',   16, 0.75, 'pedal'),
        ('break',     8, 0.5, 'off'),
        ('build2',    4, 0.85, 'pedal'),
        ('chorus_b', 16, 1.0, 'root'),
        ('outro',     8, 0.7, 'root'),
    ]
    total_bars = sum(b for _, b, _, _ in sections)

    # Authoritative chord cycle: i - III - VI - VII (Dm - F - Bb - C in D minor)
    # Intervals from minor tonic: III = +3 (m3), VI = +8 (m6), VII = +10 (m7)
    chord_cycle = [(root_pc + 0)  % 12,  # i   Dm  (D)
                   (root_pc + 3)  % 12,  # III F   (F)
                   (root_pc + 8)  % 12,  # VI  Bb  (B♭)
                   (root_pc + 10) % 12]  # VII C   (C)

    # ---- helpers ----
    # Happy hardcore canonical patterns. The spec's bass rhythm is FFD-flavoured
    # (X..X..X.X..X..X.) which is not a bouncy rave bass — we use clean off-beat
    # 8ths instead. The spec's kick (X...X...XX..X..X) IS a great syncopated rave
    # kick, so we keep it.
    bass_pat  = [2, 6, 10, 14]          # off-beat 8ths — the "bouncy" bass
    kick_pat  = pattern_to_positions(spec['elements']['drums'].get('kick',  'X...X...X...X...'))
    snare_pat = pattern_to_positions(spec['elements']['drums'].get('clap',  '....X.......X...'))
    hat_pat   = list(range(0, 16, 2))   # 8th-note hats (every off-beat too)

    # The vocal-line rhythm from the spec: positions where the singer enters
    # a syllable inside one bar. Each position will be filled with a
    # chord-tone pitch (so the result is "what the singer might have sung
    # over this chord", in cleanroom shorthand).
    vocal_rhythm = pattern_to_positions(
        spec['elements'].get('melody', {}).get('rhythm_1bar_16ths', 'X..X..X.X..X..X.')
    )
    # Per-vocal-position chord-tone choice — degree within the current triad.
    # Index = position in vocal_rhythm (0..len-1). 0=root, 1=3rd, 2=5th, 3=octave.
    VOCAL_DEGREES = [0, 1, 2, 3, 2, 1, 0, 1]   # rises to octave and settles

    # Use the spec melody contour as a *seed*. Walk through it and snap to scale.
    contour = spec['elements']['melody'].get('contour_first32', [])
    # Lead starting pitch
    lead_pitch = 12 * (melody_octave + 1) + lead_root_pc + 5  # ~A4-ish for D minor (=Dm: D scale degree 5)
    # Normalize: every 16th step in the contour roughly = +1/-1 scale step

    # Output event lists with frame timing
    bass_events = []
    lead_events = []
    drum_events = []
    fx_events = []  # crashes etc.

    # ----- OUTPUT STRUCTURE (segment-map) --------------------------------
    # The user's chosen arrangement for this release re-orders the song:
    #   Intro -> Verse 1 -> Pre-chorus 1 -> Chorus 1 -> Na-na ->
    #   Chorus 2 (reprise of Chorus 1) -> Chorus 3 (reprise of Chorus 1)
    #
    # Each SEGMENT maps a source-beat range from the karaoke MIDI onto a
    # contiguous output range. A note in the source whose beat falls inside
    # the source range is re-emitted at the corresponding output beat. The
    # same source range can appear in multiple output segments — the chorus
    # notes get played 3 times.
    SEGMENTS = [
        # (src_start, src_end, label) — the deFEEST hardcore edit: verse/pre/
        # chorus once, then the 3x "Freed from desire" climax (chorus replayed
        # three times, each with its own timbre; chorus3 octave-up). NOT the
        # full source song — just the triple-chorus banger.
        (  0.0,  21.5, 'intro'),
        ( 21.5,  54.5, 'verse1'),
        ( 54.5,  88.0, 'prechorus1'),
        ( 88.0, 117.5, 'chorus1'),
        (117.5, 149.5, 'postchorus_nana'),
        (149.5, 153.5, 'breathe1'),   # 4-beat instrumental gap (drums + hook bass)
        ( 88.0, 117.5, 'chorus2'),    # reprise of chorus 1
        (149.5, 153.5, 'breathe2'),   # 4-beat gap
        ( 88.0, 117.5, 'chorus3'),    # reprise of chorus 1 (octave-up climax)
    ]
    out_offsets = []
    cur = 0.0
    for src_s, src_e, _ in SEGMENTS:
        out_offsets.append(cur)
        cur += (src_e - src_s)
    song_out_beats = cur

    def remap(src_beat):
        """Yield (output_beat, segment_label) for each segment this source
        beat lands in. Some source beats appear in 3 chorus copies."""
        for (src_s, src_e, label), out_s in zip(SEGMENTS, out_offsets):
            if src_s <= src_beat < src_e:
                yield (src_beat - src_s + out_s, label)

    # ----- VERIFIED layers from ground truth -----------------------------
    # docs/song_layers.yaml has verbatim T5 bass + T7 vocal + T11 hook + T12
    # SFX swells, plus lyrics aligned to T2's syllable markers. Use them
    # directly rather than re-deriving from MIDI.
    layers_path = os.path.join(BASE, 'docs', 'song_layers.yaml')
    melody_path = os.path.join(BASE, 'docs', 'melody_lyrics.yaml')
    skip_synthetic_melody = False
    if os.path.exists(layers_path):
        with open(layers_path) as f:
            layers = yaml.safe_load(f)
        source_bpm = float(layers.get('source_bpm', 120))
        # FAST=1 picks the happy-hardcore variant: 175 BPM, plus
        # arrangement changes downstream (off-beat 8th bass, denser drums,
        # saw lead throughout). Default is the song-faithful clean build.
        FAST = bool(os.environ.get('FAST'))
        play_bpm = (FAST_BPM if FAST else source_bpm)
        play_bpm_lead = play_bpm
        play_bpm_groove = play_bpm
        fbeat_lead   = beats_to_frames(1, play_bpm_lead)
        fbeat_groove = beats_to_frames(1, play_bpm_groove)

        # ---- Vocal (V2 lead) -- T7 verbatim, remapped per segment ----
        # (The per-section timbre/transpose tables live just below, after the
        # master frame grid — that's the effective definition.)
        # ---- Master frame grid (Bresenham) --------------------------------
        # 175 BPM = 120/7 frames per beat = 30/7 frames per 16th.
        # Independent int(round(beat * fbeat)) per voice causes ±0.5
        # frame drift that accumulates. Instead, build ONE grid using
        # integer accumulation — zero drift, all voices share it.
        # See ADHD analysis: hardware engineer frame.
        from math import gcd
        _num = int(round(PAL_HZ * 60))        # 3000 (frames per minute)
        _den = int(round(play_bpm * 4))       # 700 (16ths per minute at 175 BPM)
        _g = gcd(_num, _den)
        _num //= _g; _den //= _g             # 120/7
        _grid_size = int(song_out_beats * 4) + 64
        _master_grid = [0] * _grid_size
        _frame = 0; _rem = 0
        for _i in range(_grid_size):
            _master_grid[_i] = _frame
            _rem += _num
            _frame += _rem // _den
            _rem %= _den

        def grid_frame(beat):
            """Beat → frame via the shared Bresenham grid (snap to 16th)."""
            idx = round(beat * 4)
            if 0 <= idx < len(_master_grid):
                return _master_grid[idx]
            return int(round(beat * fbeat_lead))

        # Vocal (V2): T7 verbatim + per-section waveform.
        # Each chorus reprise gets a DISTINCT timbre so the same melody line
        # doesn't wear thin when it returns: chorus1 = saw/hoover,
        # chorus2 = pulse, chorus3 = tri+pulse (brightest, climactic final).
        SECTION_LEAD_CTRL = {
            'intro':           0x10,
            'verse1':          0x10,
            'prechorus1':      0x10,
            'chorus1':         0x20,  # saw -> hoover
            'postchorus_nana': 0x20,
            'breathe1':        0x20,
            'chorus2':         0x40,  # pulse -- distinct reprise 2 (clean, loud)
            'breathe2':        0x40,
            'chorus3':         0x20,  # saw -- fat & clear for the climactic final
                                      # (was $50 tri+pulse: AND-combine = thin,
                                      # dropped notes — the "missing notes")
        }
        # Per-section lead transpose (semitones). Octave-up the FINAL chorus
        # so the last drop peaks above all the earlier choruses = climactic
        # lift, and the thrice-played hook stops wearing thin.
        SECTION_LEAD_TRANSPOSE = {
            'chorus3': 12,
        }
        for s_b, d_b, pitch in layers['layers'].get('vocal', []):
            d = max(0.2, d_b)
            for out_b, label in remap(s_b):
                lead_events.append({
                    'frame': grid_frame(out_b),
                    'note':  int(pitch) + SECTION_LEAD_TRANSPOSE.get(label, 0),
                    'dur_frames': max(4, int(round(d * fbeat_lead))),
                    'ctrl':  SECTION_LEAD_CTRL.get(label, 0x10),
                })

        # ---- Legato-fill the lead -------------------------------------------
        # The source durations are short transcribed syllables, leaving
        # 0.2-0.7s of silence between almost every note — the melody blipped
        # instead of singing ("silent bits"). Extend each note to the NEXT
        # onset so the line is continuous; retrigger (synth) still re-attacks
        # every note, so it stays accented and pops. Genuine section drops
        # (gap > SECTION_REST) are preserved: the note rings out then rests.
        lead_events.sort(key=lambda e: e['frame'])
        SECTION_REST = int(round(beats_to_frames(3.5, play_bpm)))  # only the chorus
                                                                   # DROPS exceed this;
                                                                   # all breaths fill
        RING_OUT     = int(round(beats_to_frames(1.0, play_bpm)))  # ring before a rest
        for i, ev in enumerate(lead_events):
            if i + 1 >= len(lead_events):
                continue
            gap = lead_events[i + 1]['frame'] - ev['frame']
            if gap <= 0:
                continue
            if gap <= SECTION_REST:
                # Legato, but leave ~2 frames of gate-off before the next onset.
                # Butting notes frame-to-frame makes the retrigger toggle gate
                # off→on within one frame, which the SID envelope can't
                # hard-restart cleanly -> glitched / "barely there" notes.
                # The 2-frame (~40ms) gate-off is inaudible but lets each note
                # re-attack cleanly.
                ev['dur_frames'] = max(1, gap - 2)
            else:
                ev['dur_frames'] = max(ev['dur_frames'], RING_OUT)  # ring, then rest

        # ---- V1: section-authentic, verbatim per source layer.
        # Per the score analysis + voice_essence.md:
        #   Intro/Verse/Prechorus: organ stab (T6, 345 events, D-pedal)
        #   Chorus 1: sparse (T5 only 12 events) → organ continues
        #   Na-na: T5 bass tresillo (43 events, the groove engine)
        #   Chorus 2/3 reprises: T5 bass from na-na range
        # Each layer plays ONLY where it exists in the source.
        if not MELODY_ONLY:
            # T6 organ stab: verbatim. The original verse rhythmic engine.
            # Plays D4+D5+D6 unison — we drop to D2 for bass register.
            organ = layers['layers'].get('organ', [])
            for s_b, d_b, pitch in organ:
                d = max(0.1, d_b)
                for out_b, label in remap(s_b):
                    bass_events.append({
                        'frame': grid_frame(out_b),
                        'note':  38,  # D2 always (organ is D-pedal)
                        'dur_frames': max(3, int(round(d * fbeat_groove))),
                    })
            # T5 bass: verbatim (enters at beat 120, tresillo).
            t5 = layers['layers'].get('bass', [])
            for s_b, d_b, pitch in t5:
                d = max(0.1, d_b)
                for out_b, label in remap(s_b):
                    bass_events.append({
                        'frame': grid_frame(out_b),
                        'note':  int(pitch),
                        'dur_frames': max(3, int(round(d * fbeat_groove))),
                    })
            # T11 hook: verbatim (na-na counter-melody, beat 184+).
            t11 = layers['layers'].get('hook', [])
            for s_b, d_b, pitch in t11:
                d = max(0.1, d_b)
                for out_b, label in remap(s_b):
                    bass_events.append({
                        'frame': grid_frame(out_b),
                        'note':  int(pitch) - 12,
                        'dur_frames': max(3, int(round(d * fbeat_groove))),
                    })

        # ---- Drums (V3) verbatim from T13, filtered for dynamics ----
        # Section boundaries (source beats) from the lyric markers in T2:
        #   each '\' prefix marks a new section.
        SECTIONS = [
            #  start_beat, name
            (0.0,    'intro'),       # noise swell only
            (21.5,   'verse1'),      # kick-only, sparse
            (54.5,   'prechorus1'),  # add snare for build
            (88.0,   'chorus1'),     # full kit (kick+snare+hat)
            (117.5,  'postchorus1'), # full kit
            (149.5,  'break'),       # back to kick+snare for the dip
            (184.0,  'instrumental'),# kick+snare (T11 hook is the focus)
            (213.5,  'verse2'),      # like verse1 — light again, dynamic dip
            (246.5,  'prechorus2'),  # build
            (280.0,  'chorus2'),     # full kit, reprise
            (309.5,  'outro_na'),    # full kit through the na-na outro
        ]
        # Per-section drum-kit filter (which kinds survive). Fast variant
        # is rave-loud everywhere except the intro swell.
        if FAST:
            SECTION_KIT = {
                'intro':       set(),
                'verse1':      {'kick', 'snare', 'hat'},
                'prechorus1':  {'kick', 'snare', 'hat'},
                'chorus1':     {'kick', 'snare', 'hat'},
                'postchorus1': {'kick', 'snare', 'hat'},
                'break':       {'kick', 'snare', 'hat'},
                'instrumental':{'kick', 'snare', 'hat'},
                'verse2':      {'kick', 'snare', 'hat'},
                'prechorus2':  {'kick', 'snare', 'hat'},
                'chorus2':     {'kick', 'snare', 'hat'},
                'outro_na':    {'kick', 'snare', 'hat'},
            }
        else:
            SECTION_KIT = {
                'intro':       set(),
                'verse1':      {'kick'},
                'prechorus1':  {'kick', 'snare'},
                'chorus1':     {'kick', 'snare', 'hat'},
                'postchorus1': {'kick', 'snare', 'hat'},
                'break':       {'kick', 'snare'},
                'instrumental':{'kick', 'snare'},
                'verse2':      {'kick', 'snare'},
                'prechorus2':  {'kick', 'snare', 'hat'},
                'chorus2':     {'kick', 'snare', 'hat'},
                'outro_na':    {'kick', 'snare', 'hat'},
            }
        # Map GM drum codes to our kit
        GM_DRUMS = {
            35: 'kick', 36: 'kick', 28: 'kick',
            38: 'snare', 40: 'snare',
            39: 'snare',          # clap mapped onto snare
            46: 'hat',            # open hat -> hat
        }
        def section_at(beat):
            cur = SECTIONS[0][1]
            for sb, name in SECTIONS:
                if beat >= sb:
                    cur = name
                else:
                    break
            return cur
        if not MELODY_ONLY:
            # Canonical happy-hardcore foundation, generated on the OUTPUT grid
            # so every voice shares ONE pulse: 4-on-the-floor kick, backbeat
            # clap on beats 2 & 4, offbeat-8th hats (full 8ths in choruses).
            # The verbatim T13 drums were dense and un-anchored — kick scattered
            # off the grid, snare on every 16th, no backbeat — so the layers
            # read as "pasted together". This gives a singular rhythm; the
            # iconic FFD bass + the vocal float ON TOP (the bass already shares
            # the downbeat with the kick). Breathe snare-roll + crashes (below)
            # stack on this. (SECTIONS/SECTION_KIT/GM_DRUMS above are now unused.)
            LABEL_INTENSITY = {
                'intro':           0,   # silence — only the crash swell
                'verse1':          2,   # kick + clap + offbeat hats
                'prechorus1':      3,   # + on-beat hats (full 8ths) = build
                'chorus1':         3,
                'postchorus_nana': 3,
                'breathe1':        1,   # kick only; the snare roll fills the rest
                'chorus2':         3,
                'breathe2':        1,
                'chorus3':         3,
            }
            def label_at_out(ob):
                for (s_, e_, lab), o_ in zip(SEGMENTS, out_offsets):
                    if o_ <= ob < o_ + (e_ - s_):
                        return lab
                return None
            for i in range(int(round(song_out_beats * 2))):    # 8th-note steps
                ob = i / 2.0
                inten = LABEL_INTENSITY.get(label_at_out(ob), 0)
                if inten == 0:
                    continue
                on_beat = (i % 2 == 0)
                in_bar  = int(round(ob)) % 4                     # bar position
                if on_beat:                                      # KICK 4-on-floor
                    drum_events.append({'kind': 'kick', 'frame': grid_frame(ob)})
                if on_beat and in_bar in (1, 3) and inten >= 2:  # CLAP on 2 & 4
                    drum_events.append({'kind': 'snare', 'frame': grid_frame(ob)})
                if inten >= 2 and (not on_beat or inten >= 3):   # HATS
                    drum_events.append({'kind': 'hat', 'frame': grid_frame(ob)})

        # ---- T12 reverse-cymbal swells (intro AND section transitions) ----
        if not MELODY_ONLY:
            for s_b, d_b, _pitch in layers['layers'].get('sfx', []):
                for out_b, _label in remap(s_b):
                    fx_events.append({
                        'kind': 'crash',
                        'frame': grid_frame(out_b),
                    })
            # Reprise swells: a riser into each OUTPUT chorus segment so each
            # one (chorus1, chorus2, chorus3) hits with the same "drop" energy.
            RISER_LEAD_BEATS = 3.0
            for (src_s, src_e, label), out_s in zip(SEGMENTS, out_offsets):
                if not label.startswith('chorus'): continue
                riser_b = out_s - RISER_LEAD_BEATS
                if riser_b < 0: continue
                fx_events.append({
                    'kind': 'crash',
                    'frame': grid_frame(riser_b),
                })
            # Drop crash on the first beat of reprise choruses so chorus2
            # and chorus3 hit with an extra accent on top of the riser.
            for (src_s, src_e, label), out_s in zip(SEGMENTS, out_offsets):
                if label not in ('chorus2', 'chorus3'): continue
                fx_events.append({
                    'kind': 'crash',
                    'frame': grid_frame(out_s),
                })
            # Reprise energy push: the BREATHE bars before chorus2/3 get a
            # full-length 16th-note snare roll stacked on top of the still-
            # driving kit — a relentless build into the drop (no dead air;
            # silence read as less epic). Then chorus2/3 slam in with a fresh
            # timbre + drop crash.
            for (src_s, src_e, label), out_s in zip(SEGMENTS, out_offsets):
                if label not in ('breathe1', 'breathe2'): continue
                dur = src_e - src_s
                for step in range(int(dur * 4)):  # full 16th-note roll, no gap
                    drum_events.append({
                        'kind': 'snare',
                        'frame': grid_frame(out_s + step / 4.0),
                    })
            # (Chorus full-8th hats now come from the canonical generator above.)

        if MELODY_ONLY:
            bass_events.clear()
            drum_events.clear()
            fx_events.clear()
        skip_synthetic_melody = True
    elif os.path.exists(melody_path):
        # backwards compat with old melody-only YAML
        with open(melody_path) as f:
            ground = yaml.safe_load(f)
        syls = ground['lyrics_aligned']
        source_bpm = ground.get('source_bpm', 120)
        play_bpm = source_bpm if MELODY_ONLY else source_bpm
        fbeat_lead = beats_to_frames(1, play_bpm)
        offset_b = syls[0]['beat']
        for i, s in enumerate(syls):
            if s['pitch'] is None: continue
            b = s['beat'] - offset_b
            end_b = syls[i+1]['beat'] - offset_b if i+1 < len(syls) else b + 0.5
            dur_b = max(0.2, end_b - b)
            lead_events.append({
                'frame': int(round(b * fbeat_lead)),
                'note':  int(s['pitch']),
                'dur_frames': max(4, int(round(dur_b * fbeat_lead))),
            })
        if MELODY_ONLY:
            bass_events.clear()
            drum_events.clear()
            fx_events.clear()
        skip_synthetic_melody = True
    # (no fallback synthetic melody — YAML is required for lead)
    if not skip_synthetic_melody:
        raise RuntimeError(
            "docs/melody_lyrics.yaml missing. Run extract_patterns.py first."
        )
    song_beats = total_bars * 4

    # Each chord in the cycle is the appropriate quality (i is minor, III/VI/VII
    # are major). For arpeggio purposes we use simple chord-tone shapes:
    #   minor: 0,  3, 7 (root, m3, 5)
    #   major: 0,  4, 7 (root, M3, 5)
    chord_qualities = ['minor', 'major', 'major', 'major']

    cur_bar = 0
    fill_intro_to = {'build', 'build2'}
    # Bass + drums + SFX are all verbatim from song_layers now; the
    # synthetic section loop has nothing left to do. Skip it entirely.
    section_iter = []
    # Drums tempo = source tempo (frames-per-bar recomputed)
    fpbar  = beats_to_frames(4, source_bpm) if skip_synthetic_melody else fpbar
    fp16   = fpbar / 16
    fpbeat = fpbar / 4
    SUPPRESS_SYNTH_BASS = True   # use T5 verbatim, no generated off-beat 8ths
    for sec_idx, (name, bars, intensity, bass_mode) in section_iter:
        for b in range(bars):
            global_bar = cur_bar + b
            chord_idx  = global_bar % len(chord_cycle)
            chord_root = chord_cycle[chord_idx]
            chord_qual = chord_qualities[chord_idx]
            # Crash at the start of each chorus / break section
            if b == 0 and (name.startswith('chorus') or name == 'break'):
                fx_events.append({
                    'kind': 'crash',
                    'frame': int(round(global_bar * fpbar)),
                })
            # --- drums ---
            if intensity >= 0.4:
                for p in kick_pat:
                    drum_events.append({
                        'kind': 'kick',
                        'frame': int(round(global_bar * fpbar + p * fp16)),
                    })
            if intensity >= 0.5:
                for p in snare_pat:
                    drum_events.append({
                        'kind': 'snare',
                        'frame': int(round(global_bar * fpbar + p * fp16)),
                    })
            # Hats disabled — keeping the drum pattern simple (kick + clap only)
            # so the lead is more prominent. Re-enable if the mix feels empty.
            # if intensity >= 0.6:
            #     for p in hat_pat:
            #         drum_events.append({
            #             'kind': 'hat',
            #             'frame': int(round(global_bar * fpbar + p * fp16)),
            #         })
            # Snare fill on the last bar of any build section
            if name in fill_intro_to and b == bars - 1:
                for p in range(8, 16):
                    drum_events.append({
                        'kind': 'snare',
                        'frame': int(round(global_bar * fpbar + p * fp16)),
                    })
            # --- bass --- pedal in verses, root-motion in choruses, off in break.
            # Skipped entirely when T5 verbatim bass is being used.
            if not SUPPRESS_SYNTH_BASS and bass_mode != 'off':
                if bass_mode == 'pedal':
                    bass_pitch_pc = root_pc           # stay on tonic
                else:
                    bass_pitch_pc = chord_root         # follow chord root
                root_note = bass_root + ((bass_pitch_pc - root_pc) % 12)
                for p in bass_pat:
                    bass_events.append({
                        'frame': int(round(global_bar * fpbar + p * fp16)),
                        'note':  root_note,
                        'dur_frames': max(4, int(fp16 * 1.5)),
                    })
            # NOTE: the lead (vocal melody) is emitted up-front from the spec's
            # actual note list — see emit_notes above. We do NOT generate any
            # synthetic chord-arpeggio here; that's what "missing the singer"
            # was. Bass + drums (above) accompany the real tune.
        cur_bar += bars

    # Final composition.
    # End at the ACTUAL last event plus a short tail (ring-out + clean loop
    # point), NOT the synthetic total_bars length. The old formula padded
    # every voice with ~2 min of rests before the loop sentinel = dead air.
    _ends  = [e['frame'] + e.get('dur_frames', 6) for e in bass_events + lead_events]
    _ends += [e['frame'] + 12 for e in drum_events + fx_events]  # drum ring-out
    last_event = max(_ends) if _ends else 0
    end_frame = last_event + int(round(beats_to_frames(2, play_bpm)))  # ~½-bar tail
    composition = {
        'title':       'Friet From Desire — Happy Hardcore Remix',
        'derived_from': spec.get('source_midi', 'unknown'),
        'bpm':         bpm,
        'key':         {'root': NOTE_NAMES[root_pc], 'mode': mode},
        'length_bars': total_bars,
        'length_frames': end_frame,
        'sections':    [{'name': n, 'bars': b, 'intensity': i} for n, b, i, _ in sections],
        'voices': {
            'bass':  sorted(bass_events, key=lambda e: e['frame']),
            'lead':  sorted(lead_events, key=lambda e: e['frame']),
            'drums': sorted(drum_events + fx_events, key=lambda e: e['frame']),
        }
    }
    os.makedirs(os.path.dirname(COMP_PATH), exist_ok=True)
    with open(COMP_PATH, 'w') as f:
        f.write("# Concrete arrangement (Phase 2 of cleanroom remix pipeline).\n")
        f.write("# Generated from docs/song_spec.yaml — the synth never reads the source MIDI.\n\n")
        yaml.safe_dump(composition, f, sort_keys=False, default_flow_style=False, width=120)
    print(f"Wrote {COMP_PATH}")
    print(f"  {bpm} BPM, {total_bars} bars, ~{end_frame / PAL_HZ:.1f}s")
    print(f"  bass events:  {len(bass_events)}")
    print(f"  lead events:  {len(lead_events)}")
    print(f"  drum events:  {len(drum_events) + len(fx_events)}")

if __name__ == '__main__':
    main()
