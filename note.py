class NoteNames:

    PREFER_SHARPS = False

    SHARP_NAMES = [
        "C",
        "C#",
        "D",
        "D#",
        "E",
        "F",
        "F#",
        "G",
        "G#",
        "A",
        "A#",
        "B",
    ]

    FLAT_NAMES = [
        "C",
        "Db",
        "D",
        "Eb",
        "E",
        "F",
        "Gb",
        "G",
        "Ab",
        "A",
        "Bb",
        "B",
    ]

    @classmethod
    def get_name(cls, value: int) -> str: # Return the preferred written name for a pitch class (0-11).
        value = value % 12
        if cls.PREFER_SHARPS:
            return cls.SHARP_NAMES[value]
        return cls.FLAT_NAMES[value]
    
    @classmethod
    def value_for(cls, name: str) -> int: # Convert a note name (A, A#, Bb, etc.) to a pitch class value (0-11).

        name = name.strip().upper()

        for i, n in enumerate(cls.SHARP_NAMES):
            if n.upper() == name:
                return i

        for i, n in enumerate(cls.FLAT_NAMES):
            if n.upper() == name:
                return i

        # No match found
        raise KeyError(f"Invalid note name: {name}")
    
    @classmethod
    def full_name(cls, value: int) -> str:
        name = value % 12
        octave = value // 12
        if cls.PREFER_SHARPS:
            return cls.SHARP_NAMES[name], octave
        return cls.FLAT_NAMES[name], octave





class Note: # Represents a single musical note with pitch class and octave.

    def __init__(self, value: int, octave: int): # Store pitch class normalized to 0-11.
        self.value = value % 12
        self.octave = int(octave)

    def display_name(self) -> str: # Return musical name for this note.
        return NoteNames.get_name(self.value)
    

    def absolute_pitch(self) -> int: # Return note's absolute pitch number.
        return self.octave * 12 + self.value

    def interval_to(self, other: "Note") -> int: # Return the interval in semitones from this note to another note.
        return (other.value - self.value) % 12
    

    def __repr__(self) -> str: # Debug representation of the note, for example: Note(C#4)
        return f"Note({self.display_name()}{self.octave})"