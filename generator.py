ALLOWED_STEPS = [2, 3, 4, 5, 7, 12, 14]


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


def find_template(chord, templates):
    intervals = chord.get_intervals()
    interval_matches = []  # list of dicts: each dict maps template_name -> list of start indices

    for iv in intervals:
        equivalents = decompose(iv)
        match_positions = {}  # template_name -> list of start indices

        for e in equivalents:
            e_len = len(e)

            for tmpl in templates:
                steps = tmpl["steps"]
                name = tmpl["name"]

                for i in range(len(steps) - e_len + 1):
                    if steps[i:i+e_len] == e:
                        match_positions.setdefault(name, []).append(i)
                        break

        interval_matches.append(match_positions)

    if not interval_matches:
        return []

    # Extract all template names that matched interval 0
    candidate_templates = set(interval_matches[0].keys())

    qualified = []

    for tmpl in candidate_templates:
        valid = True
        possible_positions = interval_matches[0][tmpl]

        for idx in range(1, len(intervals)):
            next_matches = interval_matches[idx].get(tmpl)
            if not next_matches:
                valid = False
                break

            # Find any next match index greater than a previous one
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
            qualified.append(tmpl)

    return sorted(qualified)
