from enum import Enum
from note import Note
from tuning import Tuning

class Chord:

    def __init__(self, frets: list, tuning: Tuning, name: str = ""):
        self.frets = frets              # list of ints or "x"
        self.tuning = tuning
        self.name = name                # chord name

    def get_notes(self) -> list:
        notes = []
        for fret, string in zip(self.frets, self.tuning.strings):
            if isinstance(fret, int):
                notes.append(string.note_at(fret))
        return notes

    def chord_diagram(self):
        lines = []
        for fret in reversed(self.frets):
            if fret == "x":
                cell = " x"
            else:
                cell = f"{int(fret):2d}"
            lines.append(f"|--{cell}--|")
        return "\n".join(lines)

     

    def lowest_note(self):
        notes = self.get_notes()
        if not notes:
            return None
        return min(notes, key=lambda n: n.absolute_pitch())
    
    
    def get_intervals(self):
        notes = self.get_notes()
        abs_vals = [n.absolute_pitch() for n in notes]
        return [abs_vals[i+1] - abs_vals[i] for i in range(len(abs_vals)-1)]
    
    def get_first_input_note (self):
        notes = self.get_notes()
        return notes[0] if notes else None
    
    def get_abs_notes (self):
        return [n.absolute_pitch() for n in self.get_notes()]


    def __repr__(self):
        return f"Chord({self.frets}, name={self.name})"
