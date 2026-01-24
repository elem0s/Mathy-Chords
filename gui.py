import json
import os

from utils import clear_screen, load_settings, set_prefer_sharps
from note import NoteNames
from tuning import Tuning, String
from chord import Chord
from generator import build_chord, find_templates, get_input_abs_pitches, get_input_intervals, decompose, map_to_fretboard, remove_template, select_template


from PySide6.QtWidgets import QApplication, QLabel, QComboBox, QPushButton, QMessageBox, QStackedWidget, QListWidgetItem, QWidget, QListView, QVBoxLayout, QSpinBox, QLineEdit, QCheckBox
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import Qt, QFile, QSize, Signal, QSettings
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

    idx = data.get("last_tuning")
    capo = data.get("last_capo", 0)  # fallback default

    return idx, capo

def save_last_selected(index, capo):
    with open(LAST_SELECTED_PATH, "w") as f:
        json.dump({"last_tuning": index, "last_capo": capo}, f, indent=4)


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
# CSS Styling
#================================
APP_STYLE = """
QWidget#tuningRow {
  border: 1px solid #505050;
  background: #2a2a2a;
}
QWidget#tuningRow:hover {
  background: #333333;
  border-color: #7a7a7a;
}
QWidget#tuningRow[selected="true"] {
  background: #303840;
 
}



"""

# ===============================
# App
# ===============================

class Main:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyleSheet(APP_STYLE)

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

        # load tuning menu screen
        file = QFile("ui_files/tuning_menu.ui")
        file.open(QFile.ReadOnly)
        self.tuning_ui = loader.load(file)
        file.close()

         # load add tuning menu screen
        file = QFile("ui_files/add_tuning.ui")
        file.open(QFile.ReadOnly)
        self.add_tuning_ui = loader.load(file)

         # load settings screen
        file = QFile("ui_files/settings.ui")
        file.open(QFile.ReadOnly)
        self.settings_ui = loader.load(file)
        self.load_settings_state()

        # stacked container
        self.stack = QStackedWidget()

        self.stack.setMinimumSize(375, 420)

        self.stack.addWidget(self.input_ui)
        self.stack.addWidget(self.output_ui)
        self.stack.addWidget(self.tuning_ui)
        self.stack.addWidget(self.add_tuning_ui)
        self.stack.addWidget(self.settings_ui)

        self.stack.setCurrentWidget(self.input_ui)
        self.stack.show()

        # App state (this replaces main())
        self.tunings = load_tunings()
        self.current_tuning = None
        self.last_tuning, self.last_capo = load_last_selected()

        # --- Capo spinbox setup ---
        self.tuning_ui.capo_spinbox.setRange(0, 12)
        self.tuning_ui.capo_spinbox.setValue(self.last_capo)
        self.tuning_ui.capo_spinbox.valueChanged.connect(self.on_capo_changed)


        if self.tunings:  # Only if tunings exist
            if self.last_tuning is not None and 0 <= self.last_tuning < len(self.tunings):
                # Load last tuning
                self.current_tuning = construct_tuning(self.tunings[self.last_tuning])
            else:
                # Fallback to first tuning
                self.current_tuning = construct_tuning(self.tunings[0])

            # Apply last capo setting right here
            self.current_tuning.apply_capo(self.last_capo)

        with open("data/templates.json") as f:
                templates = json.load(f)["templates"]

        self.display_tuning()
        self.setup_fret_combos()
        self.set_note_combos()
        self.set_oct_combos()


        #Start menu buttons (global)
        for ui in (self.input_ui, self.output_ui, self.tuning_ui, self.add_tuning_ui, self.settings_ui):
            ui.actionTuning.triggered.connect(self.show_tuning_menu)

        for ui in (self.input_ui, self.output_ui, self.tuning_ui, self.add_tuning_ui, self.settings_ui):
            ui.actionSettings.triggered.connect(self.show_settings)

        #Input Screen Buttons
        self.input_ui.roll_button.clicked.connect(lambda: self.input_roll(templates)) #use lambda when the method needs arguments
        self.input_ui.reset_button.clicked.connect(self.clear_combos)
        

        #Output Screen Buttons
        self.output_ui.reroll_button.clicked.connect(self.roll)
        self.output_ui.reset_button.clicked.connect(self.output_reset)

        #Tuning Menu Buttons
        self.tuning_ui.apply_button.clicked.connect(self.apply_btn_click)
        self.tuning_ui.plus_btn.clicked.connect(self.plus_btn_click)
        self.tuning_ui.delete_btn.clicked.connect(self.delete_btn_click)

        # Add tuning screen buttons
        self.add_tuning_ui.add_btn.clicked.connect(self.add_btn_click)
        self.add_tuning_ui.cancel_btn.clicked.connect(self.cancel_btn_click)
        
        #settings screen buttons
        self.settings_ui.ok_btn.clicked.connect(self.return_to_input_ui)


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

    
            self.output_ui.template_name_d.setText(selected_template['name'])
            self.output_ui.note_names_d.setText(", ".join(output_note_names))
            self.output_ui.chord_diagram_label_d.setText(f'\n{output_diagrams}\n\n')

            #Debug
           # input_abs = get_input_abs_pitches(self.input_chord)
           # print(f'\nInput abs: {input_abs} \nOutput abs: {output_chord_abs}\nNumber of matched templates:{len(self.matched_templates)}')


            return

        if not self.matched_templates:
            QMessageBox.warning(
                self.stack,
                "No Matches",
                "No matching templates could be mapped to the fretboard."
            )
            
    def reset_state(self):
        self.input_chord = None
        self.matched_templates = []
        self.last_index = None


    def clear_combos (self):
        for combo in self.fret_combos:
            combo.setCurrentIndex(0)

    def clear_qlabels (self):
        for label in self.output_ui.findChildren(QLabel):
            if label.objectName().endswith("_d"): # I'm using _d to signify dynamic labels
                label.clear()
    
    def output_reset (self):
        self.reset_state()
        self.clear_combos()
        self.clear_qlabels()
        self.stack.setCurrentWidget(self.input_ui)

    def show_tuning_menu (self):
        self.populate_tuning_menu()
        self.tuning_ui.delete_btn.setEnabled(len(self.tunings) > 1)
        self.stack.setCurrentWidget(self.tuning_ui)



    def populate_tuning_menu(self):
        layout = self.tuning_ui.tuning_container.layout()
        clear_layout(layout)

        self.tuning_rows = []

        for idx, tuning in enumerate(self.tunings):
            notes = [NoteNames.get_name(v) for v in tuning["open_values"]]

            row = TuningRowWidget(
                name=tuning["name"],
                notes=notes,
                tuning_ref=tuning,
                index=idx
            )

            row.selected_signal.connect(self.on_tuning_row_clicked)
            self.tuning_rows.append(row)
            layout.addWidget(row)

        if self.tuning_rows:
            self.last_tuning = min(self.last_tuning, len(self.tuning_rows) - 1)
            row = self.tuning_rows[self.last_tuning]
            row.set_selected(True)
            row.selected_signal.emit(row)

        layout.addStretch()


    def on_tuning_row_clicked(self, row):
        # clear previous visual selection
        for r in self.tuning_ui.tuning_container.findChildren(TuningRowWidget):
            r.set_selected(False)

        row.set_selected(True)

        # apply tuning immediately
        self.last_tuning = row.index
        self.current_tuning = construct_tuning(self.tunings[row.index])
        self.current_tuning.apply_capo(self.last_capo)

        save_last_selected(self.last_tuning, self.last_capo)

        # reset dependent state
        self.reset_state()
        self.clear_combos()
        self.clear_qlabels()
        self.display_tuning()

    def apply_btn_click(self):
        self.stack.setCurrentWidget(self.input_ui)

    def on_capo_changed(self, value: int):
        self.last_capo = value

        if self.last_tuning is not None:
            # rebuild tuning from base (no capo)
            self.current_tuning = construct_tuning(self.tunings[self.last_tuning])
            self.current_tuning.apply_capo(value)

            self.display_tuning()

        save_last_selected(self.last_tuning, self.last_capo)

    def plus_btn_click (self):
        self.stack.setCurrentWidget(self.add_tuning_ui)

    # Add tuning menu functions
    def set_note_combos(self):
        self.note_combos = [
            self.add_tuning_ui.findChild(QComboBox, f"note_combo{i+1}")
            for i in range(6)
        ]

        for combo in self.note_combos:
            combo.clear()
            combo.addItem("Note", -1)  # default unset display value
            for pitch_class in range(12):
                combo.addItem(NoteNames.get_name(pitch_class), pitch_class)

    def set_oct_combos (self):
        self.oct_combos = [
            self.add_tuning_ui.findChild(QComboBox, f'oct_combo{i+1}')
            for i in range(6)
        ]

        for combo in self.oct_combos:
            combo.clear()
            combo.addItem("Oct", -1)
            for octave in range(9):
                combo.addItem(str(octave), octave)


    def add_btn_click(self):
        name = self.add_tuning_ui.findChild(QLineEdit, "name_field").text().strip()
        open_values = [c.currentData() for c in self.note_combos]
        open_octaves = [c.currentData() for c in self.oct_combos]

        if (not name 
            or -1 in open_values or -1 in open_octaves):
            
            QMessageBox.warning(
                self.stack,
                "Incomplete tuning",
                "Please enter a name and select all notes and octaves."
            )
            return

        self.tunings.append({
            "name": name,
            "open_values": open_values,
            "open_octaves": open_octaves
        })

        save_tunings(self.tunings)

        self.reset_add_tuning_form()

        self.show_tuning_menu()

    
    def delete_btn_click (self):
        self.tunings.pop(self.last_tuning)
        self.last_tuning = 0
        save_last_selected(self.last_tuning, self.last_capo)
        save_tunings(self.tunings)
        self.current_tuning = construct_tuning(self.tunings[self.last_tuning])
        self.current_tuning.apply_capo(self.last_capo)
        self.show_tuning_menu()

    def cancel_btn_click (self):
        self.reset_add_tuning_form()
        self.show_tuning_menu()
        
    def reset_add_tuning_form(self):
        self.add_tuning_ui.findChild(QLineEdit, "name_field").clear()

        for combo in self.note_combos:
            combo.setCurrentIndex(0)

        for combo in self.oct_combos:
            combo.setCurrentIndex(0)

    def show_settings (self):
        self.stack.setCurrentWidget(self.settings_ui)

    # def prefer_sharps_checked (self):
    #     if self.settings_ui.findChild(QCheckBox, "prefer_sharps").isChecked():
    #         NoteNames.PREFER_SHARPS = True
    #     else:
    #         NoteNames.PREFER_SHARPS = False
    
    def load_settings_state(self):
        settings = load_settings()
        prefer = settings["prefer_sharps"]

        set_prefer_sharps(prefer)

        checkbox = self.settings_ui.findChild(QCheckBox, "prefer_sharps")

        checkbox.blockSignals(True)
        checkbox.setChecked(prefer)
        checkbox.blockSignals(False)

        checkbox.toggled.connect(self.prefer_sharps_toggled)

    def prefer_sharps_toggled(self, checked: bool):
        set_prefer_sharps(checked)
        self.display_tuning()

    def return_to_input_ui (self):
                self.stack.setCurrentWidget(self.input_ui)





def clear_layout(layout):
    while layout.count():
        item = layout.takeAt(0)
        w = item.widget()
        if w is not None:
            w.deleteLater()



class TuningRowWidget(QWidget):
    selected_signal = Signal(object)  # emits self

    def __init__(self, name, notes, tuning_ref, index):
        super().__init__()
        self.index = index
        self.tuning = tuning_ref

        loader = QUiLoader()
        file = QFile("ui_files/tuning_row.ui")
        file.open(QFile.ReadOnly)
        ui = loader.load(file)
        file.close()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(ui)

        ui.name_label.setText(name)

        for lbl, note in zip(
            [ui.chip_1, ui.chip_2, ui.chip_3, ui.chip_4, ui.chip_5, ui.chip_6],
            notes
        ):
            lbl.setText(note)

        self.ui = ui                          # store inner widget

        self.ui.setObjectName("tuningRow")
        self.ui.setAttribute(Qt.WA_StyledBackground, True)

        self.set_selected(False)


    def mousePressEvent(self, event):
        self.selected_signal.emit(self)

    def set_selected(self, value: bool):
        self.ui.setProperty("selected", value)
        self.ui.style().unpolish(self.ui)
        self.ui.style().polish(self.ui)
        self.ui.update()


    def get_capo_value (self):
        self.capo = [
            self.tuning_ui.findChild(QSpinBox, "capo_spinbox")
        ]


Main()