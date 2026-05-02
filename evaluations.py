import math

# n grams (for originality): ensure chord loop does not contain n-gram found in dataset (NOT Roman-nnumeral dependent)
def ngrams(n, progression, dataset):
    iters = len(progression) - n + 1
    gram_score = 1.0
    for i in range(iters):
        gram = tuple(progression[i:i+n])
        if gram in dataset:
            gram_score *= 0.9  # penalize for each n-gram found in dataset

    return gram_score

# Jensen-Shannon Divergence (to track if chord patterns are being learned)
def JSD(progression, dataset):
    # Calculate frequency distributions
    prog_freq = {}
    for chord in progression:
        prog_freq[chord] = prog_freq.get(chord, 0) + 1
    total_prog = len(progression)
    prog_dist = {chord: count / total_prog for chord, count in prog_freq.items()}

    dataset_freq = {}
    for prog in dataset:
        for chord in prog:
            dataset_freq[chord] = dataset_freq.get(chord, 0) + 1
    total_dataset = sum(dataset_freq.values())
    dataset_dist = {chord: count / total_dataset for chord, count in dataset_freq.items()}

    # Calculate average distribution
    all_chords = set(prog_dist.keys()) | set(dataset_dist.keys())
    avg_dist = {chord: (prog_dist.get(chord, 0) + dataset_dist.get(chord, 0)) / 2 for chord in all_chords}

    # Calculate KL divergence    def kl_divergence(p, q):
    divergence = 0.0
    for chord in all_chords:
        p_val = prog_dist.get(chord, 0)
        q_val = dataset_dist.get(chord, 0)
        if p_val > 0 and q_val > 0:
            divergence += p_val * math.log(p_val / q_val)
    jsd = divergence / 2
    return jsd