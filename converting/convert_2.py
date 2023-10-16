import mido
from mido import MidiFile

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

def midi_to_freq_duration(midi_file_path, track):
    midi = MidiFile(midi_file_path)
    notes = []

    current_tick = 0
    tempo = 500000 # default, this is in microseconds
    active_notes = {}

    for i, track in enumerate(midi.tracks):
        for msg in track:
            # tempo changes can happen at any track lol
            if msg.type == 'set_tempo':
                tempo = msg.tempo

            # only instrument we want (which track)
            if i == 3:
                current_tick += msg.time
                if msg.type == 'note_on':
                    freq = note_to_freq(msg.note)
                    active_notes[msg.note] = current_tick

                if msg.type == 'note_off' and msg.note in active_notes:
                    start_time = active_notes.pop(msg.note)
                    duration_ticks = current_tick - start_time
                    # duration_microseconds = round((duration_ticks / midi.ticks_per_beat) * tempo)
                    notes.append((note_to_freq(msg.note), start_time, duration_ticks))

    # clean up the notes, idk if this is right
    new_notes = average_overlapping_notes(notes)
    notes = list(filter(lambda note: note[2] > 0, new_notes))

    adjusted_notes = []
    for i in range(len(notes) - 1):
        freq, start_tick, duration_ticks = notes[i]
        delay_us = round(500_000 / freq)
        next_start_tick = notes[i + 1][1]
        pause_microseconds = round(((next_start_tick - (start_tick + duration_ticks)) / midi.ticks_per_beat) * tempo)
        duration_microseconds = round((duration_ticks / midi.ticks_per_beat) * tempo)
        adjusted_notes.append((delay_us, pause_microseconds, duration_microseconds))

    return adjusted_notes

# Example usage:
result = midi_to_freq_duration('megalovania.mid', 3)
print(result)
print(len(result))
