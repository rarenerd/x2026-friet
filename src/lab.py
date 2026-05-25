#!/usr/bin/env python3
"""Lab: play AUD_HO1152.mid's melody + organ directly on SID.

This MIDI has a clean verse transcription at 125 BPM with:
  ch15 = vocal melody (Flute prog 73, E5/D5/C5/F5/A#4)
  ch3  = organ stab (PercOrgan prog 18, D3+A4+D5+A5 chord)
  ch13 = organ stab doubled (stereo pair)
  ch9  = drums (sparse section accents)

We extract melody + organ, add a simple HH kick, render to SID.
No karaoke data, no song_layers.yaml — pure AUD_HO1152 data.
"""
import os, sys, subprocess, yaml, mido
from collections import defaultdict

BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIDI    = os.path.join(BASE, 'midi', 'AUD_HO1152.mid')
COMP    = os.path.join(BASE, 'docs', 'lab_composition.yaml')
SID_OUT = os.path.join(BASE, 'out', 'lab.sid')
SYNTH   = os.path.join(BASE, 'src', 'synth.py')
PYTHON  = os.path.join(BASE, '.venv', 'bin', 'python')

# ======================== SETTINGS ========================================
BPM         = 175       # playback tempo (source is 125, we speed up)
LEAD_CTRL   = 0x40      # pulse
BASS_CTRL   = 0x40      # pulse
N_LOOPS     = 2
# ==========================================================================

PAL_HZ = 50.0

def main():
    m = mido.MidiFile(MIDI)
    tpb = m.ticks_per_beat
    fbeat = 60.0 * PAL_HZ / BPM

    # Extract per-channel note events
    channels = defaultdict(list)
    notes_on = {}
    t = 0
    for msg in m.tracks[0]:
        t += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            notes_on.setdefault(msg.channel, {})[msg.note] = t
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            starts = notes_on.get(msg.channel, {})
            if msg.note in starts:
                start = starts.pop(msg.note)
                dur = (t - start) / tpb
                channels[msg.channel].append((start / tpb, dur, msg.note))

    # Melody = ch15 (Flute, the vocal substitute)
    melody_raw = sorted(channels[15], key=lambda x: x[0])
    # Organ = ch3 (PercOrgan, the chord stab — pick just ONE note per chord)
    organ_raw = sorted(channels[3], key=lambda x: x[0])

    # Find where melody starts and define fragment
    if not melody_raw:
        print("ERROR: no melody in ch15"); sys.exit(1)
    mel_start = melody_raw[0][0]
    mel_end = melody_raw[-1][0] + melody_raw[-1][1]
    # Round down to bar boundary (4 beats) for clean looping
    frag_start = int(mel_start // 4) * 4
    frag_end = int((mel_end + 3.99) // 4) * 4
    frag_beats = frag_end - frag_start
    frag_bars = int(frag_beats // 4)

    print(f"Source: {MIDI}")
    print(f"Fragment: beats {frag_start}–{frag_end} ({frag_bars} bars)")
    print(f"Melody: {len(melody_raw)} notes, organ: {len(organ_raw)} notes")
    print(f"Playback: {BPM} BPM, {N_LOOPS} loops")

    total_bars = frag_bars * N_LOOPS
    fbar = fbeat * 4
    total_frames = int(round(total_bars * fbar)) + 50

    # --- Lead events (melody ch15) ---
    lead_events = []
    for loop in range(N_LOOPS):
        for beat, dur, pitch in melody_raw:
            if beat < frag_start or beat >= frag_end:
                continue
            rel = beat - frag_start + loop * frag_beats
            lead_events.append({
                'frame': int(round(rel * fbeat)),
                'note': pitch,
                'dur_frames': max(4, int(round(max(0.2, dur) * fbeat))),
                'ctrl': LEAD_CTRL,
            })
    print(f"Lead: {len(lead_events)} events")

    # --- Bass events (organ ch3 — use lowest note D3=50 as the bass) ---
    # The organ plays 4-note chords (D3+A4+D5+A5). We pick D3 for bass register.
    bass_events = []
    seen_frames = set()
    for loop in range(N_LOOPS):
        for beat, dur, pitch in organ_raw:
            if beat < frag_start or beat >= frag_end:
                continue
            if pitch != 50:  # only D3
                continue
            rel = beat - frag_start + loop * frag_beats
            f = int(round(rel * fbeat))
            if f in seen_frames:
                continue
            seen_frames.add(f)
            bass_events.append({
                'frame': f,
                'note': 38,  # D2 for SID bass register
                'dur_frames': max(3, int(round(max(0.1, dur) * fbeat))),
                'ctrl': BASS_CTRL,
            })
    print(f"Bass: {len(bass_events)} events (D3 organ stabs → D2)")

    # --- Drums: simple HH kick 4-on-floor + off-beat hat ---
    drum_events = []
    for bar in range(total_bars):
        bar_start = bar * 4.0
        for off in (0, 1, 2, 3):
            drum_events.append({'kind': 'kick',
                'frame': int(round((bar_start + off) * fbeat))})
        for off in (0.5, 1.5, 2.5, 3.5):
            drum_events.append({'kind': 'hat',
                'frame': int(round((bar_start + off) * fbeat))})

    composition = {
        'title': 'Friet van Desire — Lab (AUD_HO1152)',
        'derived_from': 'AUD_HO1152.mid ch15+ch3',
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
