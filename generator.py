from random import randint

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
    
    input_decomps = []
    for interval in input_intervals:
        input_decomps.append(decompose(interval))


    for tmpl in templates:
        template_steps = tmpl["steps"]
        matched_on = []
        search_start_index = 0

        for equiv_sequences_list in input_decomps:
            found_matching_sequence = False

            for seq in equiv_sequences_list:
                seq_len = len(seq)

                for starting_point in range(search_start_index, len(template_steps) - seq_len + 1):
                    if template_steps[starting_point : starting_point + seq_len] == seq:
                        matched_template_seq = tuple(range(starting_point, starting_point+seq_len))
                        matched_on.append(matched_template_seq)
                        search_start_index = matched_template_seq[-1] + 1
                        found_matching_sequence = True
                        break

                if found_matching_sequence:
                    break

            if not found_matching_sequence:
                break

        if len(matched_on) == len(input_decomps):
            matched_templates.append((tmpl, matched_on))
                

    return(matched_templates)




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


def reroll(matched_templates, last_index):
    return select_template(matched_templates, last_index)



def build_chord(template_steps, matched_on, anchor_note):
    num_voices = len(template_steps) +1
    abs_pitches = [None] * num_voices

    first_num_in_first_tuple = matched_on[0][0]
    anchor_index = first_num_in_first_tuple - 1

    abs_pitches[anchor_index] = anchor_note

    # Build downward (toward template voice 0)
    for i in range(anchor_index - 1, -1, -1):
        abs_pitches[i] = abs_pitches[i + 1] - template_steps[i]

    # Build upward (toward final template voice)
    for i in range(anchor_index, len(template_steps)):
        abs_pitches[i + 1] = abs_pitches[i] + template_steps[i]

    return abs_pitches



def remove_template(matched_templates, index):
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
