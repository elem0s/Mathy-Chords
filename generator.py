from random import randint
from itertools import product

ALLOWED_STEPS = [2, 3, 4, 5, 7, 12, 14]


def get_input_intervals(chord):
    return chord.get_intervals()


def get_input_abs_pitches(chord):
    return [n.absolute_pitch() for n in chord.get_notes()]



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

    matched_templates = []

    input_intervals = get_input_intervals(chord)
    if not input_intervals:
        return matched_templates

    # Decompose each interval
    decomps_per_interval = [decompose(iv) for iv in input_intervals]

    # Build all full equivalent step strings
    full_step_strings = [
        [step for seq in combo for step in seq]
        for combo in product(*decomps_per_interval)
    ]

    for tmpl in templates:
        steps = tmpl["steps"]
        tmpl_len = len(steps)

        for seq in full_step_strings:
            L = len(seq)
            if L >= tmpl_len:
                continue

            # search contiguously, skipping anchor index 0
            for start in range(1, tmpl_len - L + 1):
                if steps[start:start + L] == seq:
                    matched_on = tuple(range(start, start + L))
                    matched_templates.append((tmpl, matched_on))
                    break
            else:
                continue
            break
        

    return matched_templates



def select_template(matched_templates, last_index=None):
    if not matched_templates:
        return None, None

    if len(matched_templates) == 1:
        return matched_templates[0], 0

    while True:
        roll = randint(0, len(matched_templates) - 1)
        if last_index is None or roll != last_index:
            break

    return matched_templates[roll], roll



def build_chord(template_steps, matched_on, anchor_note):
    num_voices = len(template_steps)
    abs_pitches = [0] * num_voices

    anchor_index = matched_on[0] - 1

    abs_pitches[anchor_index] = anchor_note

    # Build downward from anchor
    for i in range(anchor_index - 1, -1, -1):
        abs_pitches[i] = abs_pitches[i + 1] - template_steps[i + 1]

    # Build upward from anchor
    for i in range(anchor_index + 1, len(template_steps)):
        abs_pitches[i] = abs_pitches[i - 1] + template_steps[i]

    return abs_pitches



def remove_template(matched_templates, index):
    print(f"Couldn't map to fretboard")
    matched_templates.pop(index)



def map_to_fretboard(abs_pitches, tuning):
    HIGHEST_FRET = 17
    MAX_SPAN = 4  # 5 frets total
    NUM_STRINGS = len(tuning.strings)

    fretboard = [
        [tuning.strings[s].note_at(f).absolute_pitch() for f in range(HIGHEST_FRET + 1)]
        for s in range(NUM_STRINGS)
    ]

    shapes = set()
    

    def backtrack(i, used_strings, current_shape, lo, hi):
        if i == len(abs_pitches):
            shapes.add(tuple(current_shape))
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


def select_shape (shapes, last_idx):
    if not shapes:
        return None, None
    
    if last_idx is None:
        shape_index = 0

    else:
        shape_index = (last_idx + 1) % len(shapes)


    return shapes[shape_index], shape_index