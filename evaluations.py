def jsd(progression_rn, dataset_rn):
    """
    progression_rn: list[str] (Roman numerals)
    dataset_rn: list[list[str]] (Roman numeral progressions)
    """

    # --- Progression distribution ---
    prog_freq = {}
    for chord in progression_rn:
        prog_freq[chord] = prog_freq.get(chord, 0) + 1

    total_prog = len(progression_rn)
    prog_dist = {k: v / total_prog for k, v in prog_freq.items()}

    # --- Dataset distribution ---
    dataset_freq = {}
    for prog in dataset_rn:
        for chord in prog:
            dataset_freq[chord] = dataset_freq.get(chord, 0) + 1

    total_dataset = sum(dataset_freq.values())
    dataset_dist = {k: v / total_dataset for k, v in dataset_freq.items()}

    # --- Shared support ---
    all_chords = set(prog_dist) | set(dataset_dist)

    # --- Mixture distribution M ---
    M = {}
    for chord in all_chords:
        M[chord] = 0.5 * prog_dist.get(chord, 0) + 0.5 * dataset_dist.get(chord, 0)

    # --- KL helper ---
    def kl(P, Q):
        val = 0.0
        for chord in all_chords:
            p = P.get(chord, 0)
            q = Q.get(chord, 0)
            if p > 0:
                val += p * math.log(p / q)
        return val

    # --- Jensen-Shannon Divergence ---
    return 0.5 * kl(prog_dist, M) + 0.5 * kl(dataset_dist, M)

def ngram(n=4, progression, dataset):
    """
    progression: list[str] (e.g., ["C:maj", "F:maj", ...])
    dataset: list[list[str]] (list of progressions)
    """

    # Build dataset n-gram set
    dataset_ngrams = set()
    for prog in dataset:
        for i in range(len(prog) - n + 1):
            dataset_ngrams.add(tuple(prog[i:i+n]))

    # Count novel n-grams in generated progression
    total = 0
    novel = 0

    for i in range(len(progression) - n + 1):
        gram = tuple(progression[i:i+n])
        total += 1
        if gram not in dataset_ngrams:
            novel += 1

    return novel / total if total > 0 else 0.0