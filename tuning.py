from note import Note, NoteNames


class String:

    def __init__(self, open_value: int, open_octave: int):
        self.open_value = open_value % 12
        self.open_octave = int(open_octave)

    def note_at(self, fret: int) -> Note: # Return the Note produced at the given fret.
        value = (self.open_value + fret) % 12
        octave_shift = (self.open_value + fret) // 12
        return Note(value, self.open_octave + octave_shift) # self.open_octave + octave_shift sent to 'octave' argument in Note constructor

    def open_note_name(self) -> str:
        return NoteNames.get_name(self.open_value)
    
    def transpose(self, semitones: int): # Raise the string's open note by the given number of semitones
        new_val = self.open_value + semitones
        self.open_value = new_val % 12
        self.open_octave += new_val // 12



class Tuning:

    def __init__(self, name: str, strings: list): # strings must = list of 6 String objects, from lowest pitch to highest.
        self.name = name
        self.strings = strings
        self.capo = 0

    def apply_capo(self, semitones: int):
        self.capo = semitones
        for string in self.strings:
            string.transpose(semitones)


    def print_tuning_diagram(self):
        print()
        for s in reversed(self.strings):
            name = s.open_note_name()
            print(f"|--{name}--|")

        print(self.name)

        if self.capo > 0:
            print(f"(Capo +{self.capo})")