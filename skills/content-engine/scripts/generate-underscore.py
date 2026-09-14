#!/usr/bin/env python3
"""
AHS Law — uplifting cinematic underscore (v3).

Warm Cmaj7 → Am7 → Fmaj7 → G7sus4 → Cmaj7 progression at 90 BPM.
Gentle piano-like arpeggio on eighth notes for forward motion, soft pad
underneath, subtle bass pulse. Brand-safe corporate-cinematic.

Output: ahs-underscore.wav (mono, 44.1kHz, 16-bit), 40s.
"""
import numpy as np
import wave
import os

SR = 44100
DUR = 40.0
BPM = 90
BEAT = 60.0 / BPM           # 0.667s
EIGHTH = BEAT / 2.0         # 0.333s
SECTION = 8.0               # seconds per chord
N = int(SR * DUR)
t = np.linspace(0, DUR, N, endpoint=False)

# --- Chord progression (4 chords × 8s = 32s, then 8s of Cmaj7 to land) ---
# Each chord = list of frequencies (root through 7th)
Cmaj7  = {"root": 130.81, "pad": [130.81, 164.81, 196.0, 246.94], "arp": [261.63, 329.63, 392.0, 493.88]}
Am7    = {"root": 110.0,  "pad": [110.0, 130.81, 164.81, 196.0], "arp": [220.0, 261.63, 329.63, 392.0]}
Fmaj7  = {"root": 87.31,  "pad": [87.31, 130.81, 164.81, 220.0], "arp": [261.63, 329.63, 349.23, 440.0]}
G7sus4 = {"root": 98.0,   "pad": [98.0, 130.81, 174.61, 196.0],  "arp": [261.63, 293.66, 392.0, 493.88]}

PROGRESSION = [Cmaj7, Am7, Fmaj7, G7sus4, Cmaj7]
SECTION_DUR = DUR / len(PROGRESSION)  # 8s each


def voice(freq, t_local, harmonics=(1.0, 0.4, 0.15, 0.05), detune_cents=4):
    """Warm sustained voice for pad."""
    detune = 2 ** (detune_cents / 1200.0)
    out = np.zeros_like(t_local)
    for h, hamp in enumerate(harmonics, start=1):
        out += np.sin(2 * np.pi * freq * h * t_local) * hamp
        out += np.sin(2 * np.pi * freq * h * detune * t_local) * hamp * 0.6
    vib = 1.0 + 0.005 * np.sin(2 * np.pi * 3.0 * t_local)
    return out * vib


def piano_pluck(freq, t_local, decay=2.5):
    """Bright piano-like pluck with exponential decay."""
    env = np.exp(-t_local * decay)
    # Piano tone = fundamental + odd-leaning harmonics + slight inharmonicity
    sig = (
        np.sin(2 * np.pi * freq * t_local) * 1.0
        + np.sin(2 * np.pi * freq * 2 * t_local) * 0.4
        + np.sin(2 * np.pi * freq * 3 * t_local) * 0.18
        + np.sin(2 * np.pi * freq * 4 * t_local) * 0.08
    )
    # Soft attack (10ms)
    attack = int(SR * 0.005)
    sig[:attack] *= np.linspace(0, 1, attack)
    return sig * env


def soft_bass(freq, t_local, decay=1.2):
    """Sub-bass pulse for forward motion."""
    env = np.exp(-t_local * decay)
    sig = np.sin(2 * np.pi * freq * t_local) * 1.0 + np.sin(2 * np.pi * freq * 2 * t_local) * 0.2
    attack = int(SR * 0.02)
    sig[:attack] *= np.linspace(0, 1, attack)
    return sig * env


# --- Build PAD layer (sustained chord under everything) ---
pad = np.zeros(N)
for idx, chord in enumerate(PROGRESSION):
    seg_start = int(idx * SECTION_DUR * SR)
    seg_end = int((idx + 1) * SECTION_DUR * SR)
    seg_len = seg_end - seg_start
    seg_t = np.linspace(0, SECTION_DUR, seg_len, endpoint=False)

    seg_audio = np.zeros(seg_len)
    for f in chord["pad"]:
        seg_audio += voice(f, seg_t) * 0.18
    # Cross-fade between chords (1s overlap implied by gentle envelope)
    fade = int(SR * 1.0)
    if seg_len >= 2 * fade:
        seg_audio[:fade] *= np.linspace(0, 1, fade)
        seg_audio[-fade:] *= np.linspace(1, 0.6, fade)
    pad[seg_start:seg_end] += seg_audio

# --- Build ARPEGGIO layer (eighth notes flowing through chord tones) ---
arp = np.zeros(N)
for idx, chord in enumerate(PROGRESSION):
    seg_start_sec = idx * SECTION_DUR
    # Eighth notes for 8 seconds = 24 notes per chord (90 BPM × 8s = 12 beats × 2 eighths)
    notes = chord["arp"]
    pattern = [0, 1, 2, 3, 2, 1] if len(notes) >= 4 else [0, 1, 2, 1]  # ascending then back
    note_count = int(SECTION_DUR / EIGHTH)
    for i in range(note_count):
        note_start = seg_start_sec + i * EIGHTH
        if note_start >= DUR - 0.1:
            break
        freq = notes[pattern[i % len(pattern)]]
        # Pluck samples
        pluck_dur = min(EIGHTH * 4, DUR - note_start)  # let it ring 4 eighths
        pl_n = int(pluck_dur * SR)
        pl_t = np.linspace(0, pluck_dur, pl_n, endpoint=False)
        pluck = piano_pluck(freq, pl_t)
        # Velocity humanization: slight volume variation
        vel = 0.10 + 0.025 * np.sin(i * 1.7)
        ps = int(note_start * SR)
        pe = ps + pl_n
        if pe > N:
            pe = N
            pluck = pluck[: pe - ps]
        arp[ps:pe] += pluck * vel

# --- BASS layer: soft pulse on root every 2 beats ---
bass = np.zeros(N)
beat_count = int(DUR / BEAT)
for i in range(beat_count):
    if i % 2 != 0:  # only on beats 1, 3, 5... (every 2nd beat)
        continue
    note_start = i * BEAT
    chord_idx = min(int(note_start / SECTION_DUR), len(PROGRESSION) - 1)
    freq = PROGRESSION[chord_idx]["root"] / 2  # one octave below
    bnote_dur = min(BEAT * 2, DUR - note_start)
    bn = int(bnote_dur * SR)
    bt = np.linspace(0, bnote_dur, bn, endpoint=False)
    bass_note = soft_bass(freq, bt) * 0.10
    ps = int(note_start * SR)
    pe = ps + bn
    if pe > N:
        pe = N
        bass_note = bass_note[: pe - ps]
    bass[ps:pe] += bass_note

# --- Mix ---
audio = pad * 1.0 + arp * 0.85 + bass * 0.7

# --- Slow LFO swell across the whole piece (subtle motion) ---
lfo = 0.85 + 0.15 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t - np.pi / 2))
audio = audio * lfo

# --- Warm low-pass (3.5kHz — keeps piano sparkle but removes harshness) ---
def lowpass(x, cutoff_hz, sr=SR):
    rc = 1.0 / (2 * np.pi * cutoff_hz)
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    y = np.zeros_like(x)
    y[0] = x[0] * alpha
    for i in range(1, len(x)):
        y[i] = y[i - 1] + alpha * (x[i] - y[i - 1])
    return y

audio = lowpass(audio, 3500)

# --- Cinematic fade-in / fade-out ---
fi = int(SR * 2.5)
fo = int(SR * 4.0)
audio[:fi] *= np.linspace(0, 1, fi) ** 1.3
audio[-fo:] *= np.linspace(1, 0, fo) ** 1.3

# --- Normalize to -6dBFS peak ---
peak = np.max(np.abs(audio))
if peak > 0:
    audio = audio / peak * 0.5

audio_int = (audio * 32767).astype(np.int16)
out_path = os.path.join(os.path.dirname(__file__), "ahs-underscore.wav")
with wave.open(out_path, "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(audio_int.tobytes())

print(f"OK {out_path} — {DUR}s @ {BPM} BPM, Cmaj7→Am7→Fmaj7→G7sus4→Cmaj7, {os.path.getsize(out_path) // 1024}KB")
