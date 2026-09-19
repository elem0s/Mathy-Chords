# audio.py
import os
import threading
import time
from pathlib import Path

if os.name == "nt":
    dll_dir = Path(__file__).parent / "fluidsynth-bin"
    os.environ["PATH"] = str(dll_dir) + os.pathsep + os.environ["PATH"]
    os.add_dll_directory(str(dll_dir))
import fluidsynth

_audio = None


class AudioEngine:
    def __init__(self):
        # Ensure FluidSynth DLLs are available (Windows only)
        

        self.fs = fluidsynth.Synth()
        self.fs.start(midi_driver="none") #For specifying a driver: self.fs.start(driver="dsound", midi_driver="none")


        base_dir = Path(__file__).resolve().parent
        sf_path = base_dir / "data" / "arachno.sf2"

        if not sf_path.exists():
            raise FileNotFoundError(f"SoundFont not found: {sf_path}")

        self.sfid = self.fs.sfload(str(sf_path))
        self.channel = 0

        # GM 46 = Orchestral Harp
        self.fs.program_select(self.channel, self.sfid, 0, 46)

        self.active_notes: list[int] = []

    def stop_notes(self):
        for note in self.active_notes:
            self.fs.noteoff(self.channel, note)
        self.active_notes.clear()

    def play(self, notes, strum_delay=0.12, velocity=110):
        if isinstance(notes, int):
            notes = [notes]

        self.stop_notes()

        def strum():
            for note in notes:
                self.fs.noteon(self.channel, note, velocity)
                self.active_notes.append(note)
                time.sleep(strum_delay)

        threading.Thread(target=strum, daemon=True).start()


def init_audio():
    global _audio
    if _audio is None:
        _audio = AudioEngine()
    return _audio
