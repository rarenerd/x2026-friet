#!/usr/bin/env python3
"""Lab: play Gala-freedfromdesire.mid directly — the most detailed
FFD transcription we have (128.5 BPM, 15 tracks, 473 vocal notes).

Extracts vocal (T5), organ stab (T8), bass (T2), drums (T10) and
renders a fragment at HH tempo on 3 SID voices.
"""
import os, sys, subprocess, yaml, mido
from collections import defaultdict

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIDI    = os.path.join(BASE, 'midi', 'Gala-freedfromdesire.mid')
COMP    = os.path.join(BASE, 'docs', 'lab_composition.yaml')
SID_OUT = os.path.join(BASE, 'out', 'lab.sid')
SYNTH   = os.path.join(BASE, 'src', 'synth.py')
PYTHON  = os.path.join(BASE, '.venv', 'bin', 'python')

# ======================== SETTINGS ========================================
BPM       = 175
N_LOOPS   = 2
# Fragment: pick a beat range from the source MIDI.
# Verse starts ~beat 32; chorus ~beat 96; na-na ~beat 128.
SRC_START = 32.0
SRC_END   = 64.0      # 8 bars of verse
# Voices
LEAD_CTRL = 0x40      # pulse
BASS_CTRL = 0x40
# What to play
PLAY_ORGAN_AS_BASS = True   # T8 organ stab → V1
PLAY_BASS_TRACK    = False  # T2 5ths bass → V1 (alternative)
PLAY_DRUMS         = True   # synth HH kit
# ==========================================================================

PAL_HZ = 50.0
GM_DRUMS = {35:'kick',36:'kick',38:'snare',40:'snare',39:'snare',
            42:'hat',44:'hat',46:'hat',49:'crash',51:'hat'}

def extract_track(midi, track_idx):
    """Return [(beat, dur_beats, pitch)] for a track."""
    tpb = midi.ticks_per_beat
    notes_on = {}
    events = []
    t = 0
    for msg in midi.tracks[track_idx]:
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            notes_on[msg.note] = t
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            if msg.note in notes_on:
                start = notes_on.pop(msg.note)
                events.append((start / tpb, (t - start) / tpb, msg.note))
    return sorted(events)

def extract_drums(midi, track_idx):
    """Return [(beat, pitch)] for drum note-ons."""
    tpb = midi.ticks_per_beat
    events = []
    t = 0
    for msg in midi.tracks[track_idx]:
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            events.append((t / tpb, msg.note))
    return sorted(events)


def main():
    m = mido.MidiFile(MIDI)
    fbeat = 60.0 * PAL_HZ / BPM
    frag_beats = SRC_END - SRC_START
    frag_bars = int(frag_beats // 4)
    total_bars = frag_bars * N_LOOPS
    total_frames = int(round(total_bars * fbeat * 4)) + 50

    print(f"Source: {MIDI}")
    print(f"Fragment: beats {SRC_START}–{SRC_END} ({frag_bars} bars × {N_LOOPS} loops)")
    print(f"Playback: {BPM} BPM")

    # --- Vocal (T5 = Flute prog 73) → V2 lead ---
    vocal = extract_track(m, 5)
    lead_events = []
    for loop in range(N_LOOPS):
        for beat, dur, pitch in vocal:
            if beat < SRC_START or beat >= SRC_END: continue
            rel = beat - SRC_START + loop * frag_beats
            lead_events.append({
                'frame': int(round(rel * fbeat)),
                'note': pitch,
                'dur_frames': max(4, int(round(max(0.2, dur) * fbeat))),
                'ctrl': LEAD_CTRL,
            })
    print(f"Lead (T5 vocal): {len(lead_events)} events")

    # --- Bass / Organ → V1 ---
    bass_events = []
    if PLAY_ORGAN_AS_BASS:
        # T8 = PercOrgan (prog 18) — plays D4+D5+D6 chord stabs.
        # Pick the LOWEST note per chord hit for bass register.
        organ = extract_track(m, 8)
        seen = set()
        for loop in range(N_LOOPS):
            for beat, dur, pitch in organ:
                if beat < SRC_START or beat >= SRC_END: continue
                rel = beat - SRC_START + loop * frag_beats
                f = int(round(rel * fbeat))
                if f in seen: continue
                seen.add(f)
                bass_events.append({
                    'frame': f,
                    'note': pitch - 24 if pitch > 60 else pitch,  # drop to bass register
                    'dur_frames': max(3, int(round(max(0.15, dur) * fbeat))),
                    'ctrl': BASS_CTRL,
                })
        print(f"Bass (T8 organ → bass register): {len(bass_events)} events")
    elif PLAY_BASS_TRACK:
        bass_raw = extract_track(m, 2)  # T2 = 5ths Bass
        for loop in range(N_LOOPS):
            for beat, dur, pitch in bass_raw:
                if beat < SRC_START or beat >= SRC_END: continue
                rel = beat - SRC_START + loop * frag_beats
                bass_events.append({
                    'frame': int(round(rel * fbeat)),
                    'note': pitch,
                    'dur_frames': max(3, int(round(max(0.15, dur) * fbeat))),
                    'ctrl': BASS_CTRL,
                })
        print(f"Bass (T2 5ths Bass): {len(bass_events)} events")

    # --- Drums → V3 ---
    drum_events = []
    if PLAY_DRUMS:
        # Synth HH: kick 4-on-floor + off-beat hat
        for bar in range(total_bars):
            bs = bar * 4.0
            for off in (0, 1, 2, 3):
                drum_events.append({'kind': 'kick',
                    'frame': int(round((bs + off) * fbeat))})
            for off in (0.5, 1.5, 2.5, 3.5):
                drum_events.append({'kind': 'hat',
                    'frame': int(round((bs + off) * fbeat))})

    composition = {
        'title': 'Friet met Desire — Lab (ossh)',
        'derived_from': 'Gala-freedfromdesire.mid T5+T8',
        'bpm': BPM,
        'key': {'root': 'D', 'mode': 'minor'},
        'length_bars': total_bars,
        'length_frames': total_frames,
        'sections': [{'name': 'lab', 'bars': total_bars, 'intensity': 1.0}],
        'voices': {
            'bass': sorted(bass_events, key=lambda e: e['frame']),
            'lead': sorted(lead_events, key=lambda e: e['frame']),
            'drums': drum_events,
        },
    }
    with open(COMP, 'w') as f:
        yaml.safe_dump(composition, f, sort_keys=False)
    print(f"Wrote {COMP}")
    r = subprocess.run([PYTHON, SYNTH, COMP, SID_OUT])
    if r.returncode != 0:
        sys.exit(r.returncode)

if __name__ == '__main__':
    main()
