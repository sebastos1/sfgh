import mido
from mido import MidiFile
import sys

def note_to_freq(note):
    return round(440 * (2 ** ((note - 69) / 12)))

def average_overlapping_notes(notes):
    new_notes = []
    for i, note in enumerate(notes):
        freq, start_time, duration_ticks = note
        end_time = start_time + duration_ticks
        overlap_count = 0
        overlap_duration = 0
        freq_sum = freq
        for j in range(i+1, len(notes)):
            other_freq, other_start_time, other_duration_ticks = notes[j]
            other_end_time = other_start_time + other_duration_ticks
            if other_start_time < end_time and other_end_time > start_time:
                overlap_count += 1
                overlap_duration += min(end_time, other_end_time) - max(start_time, other_start_time)
                freq_sum += other_freq
        if overlap_count > 0:
            new_freq = freq_sum / (overlap_count + 1)
            new_duration_ticks = (duration_ticks - overlap_duration) / (overlap_count + 1)
            new_notes.append((new_freq, start_time, new_duration_ticks))
        else:
            new_notes.append(note)
    return new_notes

def midi_to_freq_duration(midi_file_path, req_track=None):
    midi = MidiFile(midi_file_path)
    notes = []

    current_tick = 0
    tempo = 500000 # us (default)
    active_notes = {}

    if req_track is None:
        for i, track in enumerate(midi.tracks):
            print(f'{i} - Track {track.name} - {len(track)} messages')
            # print(track)
        req_track = input("Select a track > ")

    for i, track in enumerate(midi.tracks):
        for msg in track:
            if req_track == 'all' or i == int(req_track):
                if msg.type == 'set_tempo':
                    tempo = msg.tempo

                current_tick += msg.time
                if msg.type == 'note_on':
                    freq = note_to_freq(msg.note)
                    active_notes[msg.note] = current_tick

                if msg.type == 'note_off' and msg.note in active_notes:
                    start_time = active_notes.pop(msg.note)
                    duration_ticks = current_tick - start_time
                    # duration_microseconds = round((duration_ticks / midi.ticks_per_beat) * tempo)
                    notes.append((note_to_freq(msg.note), start_time, duration_ticks))

    # converts any chords into a single note with the average frequency
    new_notes = average_overlapping_notes(notes)
    notes = list(filter(lambda note: note[2] > 0, new_notes))

    adjusted_notes = []
    for i in range(len(notes) - 1):
        freq, start_tick, duration_ticks = notes[i]
        delay_us = round(1000_000 / freq)
        next_start_tick = notes[i + 1][1]
        pause_microseconds = round(((next_start_tick - (start_tick + duration_ticks)) / midi.ticks_per_beat) * tempo)
        duration_microseconds = round((duration_ticks / midi.ticks_per_beat) * tempo)
        adjusted_notes.append((delay_us, pause_microseconds, duration_microseconds))

    return adjusted_notes


result = midi_to_freq_duration(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
print(str(result).strip("[]"))
print(len(result))

with open('output.txt', 'w') as f:
    f.write(str(result).strip("[]"))