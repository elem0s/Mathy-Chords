from random import randint


ALLOWED_STEPS = [2, 3, 4, 5, 7, 12, 14]
last_template = None




def get_input_intervals (chord):
        return chord.get_intervals()



def decompose(interval):
    equivalents = []

    def backtrack(remaining, current):
        if len(current) > 3:
            return
        if remaining == 0:
            equivalents.append(current[:])
            return
        if remaining < 0:
            return
        for step in ALLOWED_STEPS:
            if step <= remaining:
                current.append(step)
                backtrack(remaining - step, current)
                current.pop()

    backtrack(interval, [])
    return equivalents



def find_templates(chord, templates):
    intervals = chord.get_intervals()
    step_matches = []  # list of dicts: each dict maps template_name -> list of start indices

    # Track first matched step: template_name -> matched index
    first_matched_step = {}  # indexes of the first step in X template that matched the first step of the input

    for iv in intervals:
        equivalents = decompose(iv)
        match_positions = {}  # template_name -> list of start indices

        for e in equivalents:
            e_len = len(e)

            for tmpl in templates:
                steps = tmpl["steps"]
                name = tmpl["name"]

                # check for matches of this decomposition inside template steps
                for i in range(len(steps) - e_len + 1):
                    if steps[i:i+e_len] == e:
                        match_positions.setdefault(name, []).append(i)
                        break

        step_matches.append(match_positions)

    if not step_matches:
        return [], {}

    # Templates that matched the FIRST interval (string-wise lowest interval)
    candidate_templates = set(step_matches[0].keys())

    matched_templates = []

    for tmpl in candidate_templates:
        valid = True
        possible_positions = step_matches[0][tmpl]

        # Filter to enforce strictly increasing match positions up the template
        for idx in range(1, len(intervals)):
            next_matches = step_matches[idx].get(tmpl)
            if not next_matches:
                valid = False
                break

            new_positions = []
            for prev in possible_positions:
                for nxt in next_matches:
                    if nxt > prev:
                        new_positions.append(nxt)

            if not new_positions:
                valid = False
                break

            possible_positions = new_positions

        if valid:
            # First match index for interval[0] = anchor step
            first_matched_step[tmpl] = min(step_matches[0][tmpl])
            matched_templates.append(tmpl)

    return matched_templates, first_matched_step




def select_template(matched_templates, last_index=None):

    if not matched_templates:
        return None, None

    while True:
        roll = randint(0, len(matched_templates) - 1)
        if last_index is None or roll != last_index:
            break

    return matched_templates[roll], roll



def reroll(matched_templates, last_index):
    return select_template(matched_templates, last_index)



def get_selected_template (name, templates):
    for t in templates: 
        if t["name"] == name:
            return t


def build_chord(template, first_matched_step, first_entered_note):
    steps = template["steps"]
    num_voices = len(steps) + 1

    abs_pitches = [None] * num_voices

    anchor_index = first_matched_step
    anchor_pitch = first_entered_note

    # Place the anchor pitch into the correct template voice
    abs_pitches[anchor_index] = anchor_pitch

    # Build downward (toward template voice 0)
    for i in range(anchor_index - 1, -1, -1):
        abs_pitches[i] = abs_pitches[i + 1] - steps[i]

    # Build upward (toward final template voice)
    for i in range(anchor_index, len(steps)):
        abs_pitches[i + 1] = abs_pitches[i] + steps[i]

    return sorted(abs_pitches)



def remove_template(matched_templates, index):
    matched_templates.pop(index)



#def get_input_abs_pitches(chord):
   # return [n.absolute_pitch() for n in chord.get_notes()]

def map_to_fretboard(abs_pitches, tuning):
    HIGHEST_FRET = 17
    MAX_SPAN = 4  # 5 frets total
    NUM_STRINGS = len(tuning.strings)

    fretboard = [
        [tuning.strings[s].note_at(f).absolute_pitch() for f in range(HIGHEST_FRET + 1)]
        for s in range(NUM_STRINGS)
    ]

    shapes = set()
    pitch_classes = {p % 12 for p in abs_pitches}

    def backtrack(i, used_strings, current_shape, lo, hi):
        if i == len(abs_pitches):
            # open-string class doubling
            shape = current_shape[:]
            for s in range(NUM_STRINGS):
                if shape[s] == 'x':
                    if fretboard[s][0] % 12 in pitch_classes:
                        shape[s] = 0
            shapes.add(tuple(shape))
            return

        target = abs_pitches[i]
        tried = set()

        for s in range(NUM_STRINGS):
            if s in used_strings:
                continue

            for f in range(HIGHEST_FRET + 1):
                if fretboard[s][f] != target:
                    continue

                key = (s, f)
                if key in tried:
                    continue
                tried.add(key)

                # update span (ignore open strings)
                nlo, nhi = lo, hi
                if f != 0:
                    nlo = f if lo is None else min(lo, f)
                    nhi = f if hi is None else max(hi, f)
                    if nhi - nlo > MAX_SPAN:
                        continue

                next_shape = current_shape[:]
                next_shape[s] = f

                backtrack(
                    i + 1,
                    used_strings | {s},
                    next_shape,
                    nlo,
                    nhi
                )

    backtrack(
        0,
        set(),
        ['x'] * NUM_STRINGS,
        None,
        None
    )

    return [list(shape) for shape in shapes]
