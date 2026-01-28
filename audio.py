import os
import threading
import time
os.add_dll_directory(
    r"C:\Program Files\FluidSynth\fluidsynth-v2.5.2-win10-x64-glib\bin"
)
from pathlib import Path
import fluidsynth



# --- Audio engine ---
class AudioEngine:
    def __init__(self):
        self.fs = fluidsynth.Synth()
        self.fs.start(driver="dsound", midi_driver="none")

        base_dir = Path(__file__).resolve().parent
        sf_path = base_dir / "data" / "arachno.sf2"

        self.sfid = self.fs.sfload(str(sf_path))
        self.channel = 0

        # Harp (GM 46) — can change later
        self.fs.program_select(self.channel, self.sfid, 0, 46)

        # Track currently sounding notes
        self.active_notes: list[int] = []

    def stop_notes(self):
        
        for note in self.active_notes:
            self.fs.noteoff(self.channel, note)
        self.active_notes.clear()

    def play_audio(self, notes, strum_delay=0.12):
   
        if isinstance(notes, int):
            notes = [notes]

        self.stop_notes()

        def strum():
            for note in notes:
                self.fs.noteon(self.channel, note, 110)
                self.active_notes.append(note)
                time.sleep(strum_delay)

        self.active_notes.clear()
        threading.Thread(target=strum, daemon=True).start()



# --- singleton instance ---
audio = AudioEngine()

