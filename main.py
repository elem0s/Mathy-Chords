import json
import os

from utils import clear_screen
from note import NoteNames
from tuning import Tuning, String
from chord import Chord
from generator import find_template, get_input_intervals, decompose

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
# Tuning Menu
# ===============================

def tuning_menu(tuning_list):
    while True:
        clear_screen()
        print("Select a Tuning:\n")

        for idx, t in enumerate(tuning_list):
            # Construct temporary tuning to display
            t_obj = construct_tuning(t)
            t_obj.print_tuning_diagram()
            print("Index:", idx)
            print()

        print("Enter index number to select a tuning.")
        print("Enter 'a' to add a new tuning.")
        print("Enter 'd' to delete a tuning.")
        print("Enter 'm' to return to main menu.\n")

        choice = input("> ").strip().lower()

        # Return to main menu
        if choice == "m":
            return None

        # Add tuning
        if choice == "a":
            add_tuning(tuning_list)
            save_tunings(tuning_list)
            continue

        # Delete tuning
        if choice == "d":
            delete_tuning(tuning_list)
            save_tunings(tuning_list)
            continue

        # Select tuning
        if choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(tuning_list):
                tuning = construct_tuning(tuning_list[idx])
                apply_capo_to_tuning(tuning)
                clear_screen()
                tuning.print_tuning_diagram()
                input("Press Enter to return to main menu...")

                # Return both the tuning and its index to 'change tuning' in main
                return tuning, idx


        print("Invalid input.")
        input("Press Enter...")

# ===============================
# Add tuning function
#================================
def add_tuning(tuning_list):

    print("\nAdd New Tuning:")
    name = input("Enter tuning name: ").strip()

    open_values = []
    open_octaves = []

    print("\nEnter 6 open notes from LOW to HIGH (examples: E2, F#3, Bb3):\n")

    for i in range(6):
        while True:
            raw = input(f"String {i+1} note: ").strip().upper()

            # Extract pitch and octave
            # Examples:
            #   E2   → pitch=E,    octave=2
            #   F#3  → pitch=F#,   octave=3
            #   BB3  → invalid     (should be Bb3)
            #
            # Valid forms: A0–G9 plus optional sharp/flat
            #

            # Format checks
            if len(raw) < 2:
                print("Invalid format. Example: F#3 or Bb2.")
                continue

            # Pitch part: 1 or 2 characters
            if raw[1] in ['#', 'B']:  # sharp or flat
                pitch = raw[:2]
                octave_part = raw[2:]
            else:
                pitch = raw[0]
                octave_part = raw[1:]

            # Validate octave
            if not octave_part.isdigit():
                print("Invalid octave. Must be a number. Example: E2.")
                continue

            octave = int(octave_part)

            # Validate pitch name
            try:
                value = NoteNames.value_for(pitch)
            except KeyError:
                print("Invalid pitch name. Use A-G with optional #/b.")
                continue

            # Success
            open_values.append(value)
            open_octaves.append(octave)
            break

    tuning_list.append({
        "name": name,
        "open_values": open_values,
        "open_octaves": open_octaves
    })

    print("\nTuning saved.\n")
    input("Press Enter...")


# ===============================
# Delete tuning function
#================================
def delete_tuning(tuning_list):

    print("\nDelete a Tuning")
    idx = input("Enter tuning index to delete: ")

    if idx.isdigit():
        idx = int(idx)
        if 0 <= idx < len(tuning_list):
            tuning_list.pop(idx)
            print("Deleted.")
        else:
            print("Invalid index.")
    else:
        print("Invalid input.")

    input("Press Enter...")

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
# Chord Input
# ===============================

def enter_chord(tuning):
    
    frets = []
    strings = ["Low E", "A", "D", "G", "B", "High E"]

    for s in strings:
        while True:
            val = input(f"Enter {s} string fret (x for mute): ").strip().lower()

            if val == "x":
                frets.append("x")
                break

            if val.isdigit():
                frets.append(int(val))
                break

            print("Invalid input.")

    print("\nPress Enter to generate chord suggestions, or")
    print("Enter M to return to the main menu.\n")

    cmd = input("> ").strip().lower()

    if cmd == "m":
        return None

    return Chord(frets, tuning)

# ===============================
# Suggestion Flow
# ===============================
'''
def generate_chord_flow(input_chord, tuning):
    
    last = None

    while True:
        suggestion = generate_suggestion(input_chord, tuning, last)

        if suggestion is None:
            print("\nNo suggestions available.\n")
            input("Press Enter to return to the main menu...")
            return

        last = suggestion

        print("\n=== Suggested Voicing ===\n")
        suggestion.print_diagram()

        print("\nPress Enter to Reroll")
        print("Enter 'm' for Main Menu")

        choice = input("> ").strip().lower()
        if choice == "m":
            return'''


# ===============================
# Main Menu and Program Loop
# ===============================

def main():
    tuning_list = load_tunings()

    # If no tunings exist yet, initialize defaults here.
    if not tuning_list:
        print("No tunings found. Please add a tuning from the tuning menu.\n")

    current_tuning = None
    last_index, last_capo = load_last_selected()


    if tuning_list:  # Only if tunings exist
        if last_index is not None and 0 <= last_index < len(tuning_list):
            # Load last tuning
            current_tuning = construct_tuning(tuning_list[last_index])
        else:
            # Fallback to first tuning
            current_tuning = construct_tuning(tuning_list[0])

        # Apply last capo setting right here
        current_tuning.apply_capo(last_capo)

    while True:
        clear_screen()
        print("===== Mathy Chords =====\n")

        if current_tuning:
            print("Current Tuning:")
            current_tuning.print_tuning_diagram()
        else:
            print("No tuning selected.")

        print("\nMain Menu:")
        print("1. Change tuning")
        print("2. Enter chord")
        print("3. Quit\n")

        choice = input("> ").strip()

        # Quit
        if choice == "3":
            clear_screen()
            print("Goodbye!")
            return

        # Change tuning
        if choice == "1":
            selected = tuning_menu(tuning_list)
            if selected:
                current_tuning, idx = selected
                save_last_selected(idx, current_tuning.capo)
            continue

        # Enter chord
        if choice == "2":
            if not current_tuning:
                print("\nYou must select a tuning first.\n")
                input("Press Enter...")
                continue

            chord = enter_chord(current_tuning)
            if chord is None:
                continue

            clear_screen()
            print("Input Chord:")
            chord.print_diagram()
    # ===============================
    # Testing Block
    # ===============================
            #get_intervals output
            intervals = get_input_intervals(chord)
            print(f"Input chord's intervals: {intervals}\n\n")

            #decompose output
            print("Decompositions:")
            for iv in intervals:
                print(f" Interval {iv}: {decompose(iv)}")
            
            #find_template output
            with open("data/templates.json") as f:
                templates = json.load(f)["templates"]

            qualified = find_template(chord, templates)
            print("\nQualified templates:")
            for q in qualified:
                print("-", q)

            input("Press Enter...")


if __name__ == "__main__":
    main()