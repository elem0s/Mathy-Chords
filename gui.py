import json
import os

from utils import clear_screen
from note import NoteNames
from tuning import Tuning, String
from chord import Chord
from generator import build_chord, find_templates, get_input_abs_pitches, get_input_intervals, decompose, map_to_fretboard, remove_template, select_template


from PySide6.QtWidgets import QApplication, QLabel, QComboBox, QPushButton, QMessageBox, QStackedWidget
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile
import sys



DATA_PATH = "data/tunings.json"
LAST_SELECTED_PATH = "data/last_selected.json"


# ===============================
# JSON Handling
# ===============================

# Store and load which tuning used last
def load_last_selected():
    if not os.path.exists(LAST_SELECTED_PATH):
        return None, 0  # no tuning, capo=0

    with open(LAST_SELECTED_PATH, "r") as f:
        data = json.load(f)

    idx = data.get("last_index")
    capo = data.get("last_capo", 0)  # fallback default

    return idx, capo

def save_last_selected(index, capo):
    with open(LAST_SELECTED_PATH, "w") as f:
        json.dump({"last_index": index, "last_capo": capo}, f, indent=4)


# Load and save tunings to json
def load_tunings():
    if not os.path.exists(DATA_PATH):
        return []

    with open(DATA_PATH, "r") as f:
        return json.load(f)


def save_tunings(tunings):
    with open(DATA_PATH, "w") as f:
        json.dump(tunings, f, indent=4)


def construct_tuning(tuning_dict): #  Convert tuning dictionary into a Tuning object.
    strings = []
    for v, o in zip(tuning_dict["open_values"], tuning_dict["open_octaves"]):
        strings.append(String(v, o))
    return Tuning(tuning_dict["name"], strings)

# ===============================
# Capo function
#================================
def apply_capo_to_tuning(tuning): # Prompt user for capo semitones and apply to the tuning.

    try:
        semitones = int(input("\nEnter capo fret (0 for none): "))
    except ValueError:
        semitones = 0

    tuning.apply_capo(semitones)


# ===============================
# App
# ===============================

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        loader = QUiLoader()

        # load input screen
        file = QFile("ui_files/main_menu.ui")
        file.open(QFile.ReadOnly)
        self.input_ui = loader.load(file)
        file.close()

        # load output screen
        file = QFile("ui_files/output_screen.ui")
        file.open(QFile.ReadOnly)
        self.output_ui = loader.load(file)
        file.close()

        # stacked container
        self.stack = QStackedWidget()
        self.stack.addWidget(self.input_ui)
        self.stack.addWidget(self.output_ui)
        self.stack.setCurrentWidget(self.input_ui)
        self.stack.show()

        # App state (this replaces main())
        self.tuning_list = load_tunings()
        self.current_tuning = None
        self.last_index, self.last_capo = load_last_selected()

        if self.tuning_list:  # Only if tunings exist
            if self.last_index is not None and 0 <= self.last_index < len(self.tuning_list):
                # Load last tuning
                self.current_tuning = construct_tuning(self.tuning_list[self.last_index])
            else:
                # Fallback to first tuning
                self.current_tuning = construct_tuning(self.tuning_list[0])

            # Apply last capo setting right here
            self.current_tuning.apply_capo(self.last_capo)

        with open("data/templates.json") as f:
                templates = json.load(f)["templates"]

        self.display_tuning()

        self.setup_fret_combos()

        self.input_ui.roll_button.clicked.connect(lambda: self.input_roll(templates))
        self.output_ui.reroll_button.clicked.connect(lambda: self.roll())



        #Display the app windows
        self.stack.show()
        sys.exit(self.app.exec())



    def display_tuning(self):
            if not self.current_tuning:
                return

            for i, string in enumerate(reversed(self.current_tuning.strings)):
                label = self.input_ui.findChild(QLabel, f"open_string{i+1}")
                
                if label:
                    label.setText(f"{string.open_note_name()}")


    def setup_fret_combos(self, max_fret=24):
        self.fret_combos = [
            self.input_ui.findChild(QComboBox, f"comboBox_{i+1}")
            for i in range(6)
        ]

        for combo in self.fret_combos:
            combo.clear()
            combo.addItem("x", "x")        
            for f in range(max_fret + 1):
                combo.addItem(str(f), f)    # display, value


    def get_input_chord(self):
        frets = []

        for combo in self.fret_combos:
            val = combo.currentData()  # "x" or "0".."24"

            if val == "x":
                frets.append("x")
            else:
                frets.append(int(val))

        return Chord(list(reversed(frets)), self.current_tuning)

    
    def input_roll (self, templates):
        self.input_chord = self.get_input_chord()

        if not self.input_chord or len(self.input_chord.frets) < 2:
            QMessageBox.information(
                self.stack,
                "Not Enough Notes",
                "Please enter at least two notes."
            )
            return
      
        self.matched_templates = find_templates(self.input_chord, templates)
        self.last_index = None

        if not self.matched_templates:
            QMessageBox.warning(
                self.stack,
                "No Matches",
                "No matching template data could be found."
            )
            return

        self.roll()
        self.stack.setCurrentWidget(self.output_ui) #Screen switch


    def roll (self):
        while self.matched_templates:
            selected, selected_idx = select_template(self.matched_templates, self.last_index)
            selected_template, selected_matched_on = selected
            self.last_index = selected_idx
           
            anchor_note = self.input_chord.get_first_input_note().absolute_pitch()
            output_chord_abs = build_chord(selected_template['steps'], selected_matched_on, anchor_note)
            
            shapes = map_to_fretboard(output_chord_abs, self.current_tuning)
                    
            if not shapes:
                remove_template(self.matched_templates, selected_idx)
                self.last_index = None
                continue
            
            output_diagrams = "\n\n\n\n".join(Chord(frets=list(shape), tuning=self.current_tuning).chord_diagram() for shape in shapes)
            
            output_note_names = []
            for n in output_chord_abs:
                name, octave = NoteNames.full_name(n)
                output_note_names.append(f"{name}{octave}")

    
            self.output_ui.template_name.setText(selected_template['name'])
            self.output_ui.note_names.setText(", ".join(output_note_names))
            self.output_ui.chord_diagram_label.setText(f'\n{output_diagrams}\n\n')

            input_abs = get_input_abs_pitches(self.input_chord)
            print(f'\nInput abs: {input_abs} \nOutput abs: {output_chord_abs}\nNumber of matched templates:{len(self.matched_templates)}')


            return

        if not self.matched_templates:
            QMessageBox.warning(
                self.stack,
                "No Matches",
                "No matching templates could be mapped to the fretboard."
            )
            


App()


#input_abs = get_input_abs_pitches(self.input_chord)
#self.output_ui.note_names.setText(f' {", ".join(output_note_names)}\nInput abs: {input_abs} \nOutput abs: {output_chord_abs}\n')