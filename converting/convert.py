import mido
from mido import MidiFile, tempo2bpm

# assume each track has the same bpm and shit, and assume set_tempo
def get_tempo_and_ticks_per_beat(midi_file_path):
    midi = MidiFile(midi_file_path)

    for i, track in enumerate(midi.tracks):
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = tempo2bpm(msg.tempo)
                ticks_per_beat = midi.ticks_per_beat
                return tempo, ticks_per_beat

    return None, None

# print(get_tempo_and_ticks_per_beat("converting/helltaker.mid"))

def convert_midi_to_notes(midi_file_path, cutoff=0):
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    midi = MidiFile(midi_file_path)

    for i, track in enumerate(midi.tracks):
        print(f"Track {i}: {track.name if track.name else 'n/a'} - length: {len(track)}")    
    track_number = int(input("Select track > "))

    for i, track in enumerate(midi.tracks):
        if track_number == i:
            amount = 0
            notes_str = ""
            for msg in track:
                if msg.type == 'note_on':

                    note_name = notes[msg.note % 12]
                    octave = msg.note // 12 - 1

                    # print(f'({octave}, "{note_name}"),', end=" ")
                    notes_str += f'({octave}, "{note_name}"), '
                    
                    amount += 1
                    if amount >= cutoff and cutoff > 0:
                        break

            with open("converting/output.txt", "w") as f:
                f.write(notes_str)
            print("\nAmount of notes: " + str(amount))

convert_midi_to_notes('converting/megalovania.mid', 100)