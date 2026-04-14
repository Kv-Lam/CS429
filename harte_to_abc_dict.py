import re
import jams
import glob
import os

CHROMATIC = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
 
ROOT_TO_SEMITONE = {
    "C": 0,  "C#": 1, "Db": 1,  "D": 2,  "D#": 3,  "Eb": 3,
    "E": 4,  "F":  5, "F#": 6,  "Gb": 6, "G":  7,  "G#": 8,
    "Ab": 8, "A":  9, "A#": 10, "Bb": 10, "B": 11, "E#": 5, "B#": 0, "Cb": 11, "Fb": 4
}
 
DEGREE_TO_SEMITONE = {
    "1": 0,
    "b1": 11,
    "#1": 1,
    "##1": 2,
    "bb1": 10,

    "2": 2,
    "b2": 1,
    "#2": 3,
    "##2": 4,
    "bb2": 0,

    "3": 4,
    "b3": 3,
    "#3": 5,
    "##3": 6,
    "bb3": 2,

    "4": 5,
    "b4": 4,
    "#4": 6,
    "##4": 7,
    "bb4": 3,

    "5": 7,
    "b5": 6,
    "#5": 8,
    "##5": 9,
    "bb5": 5,

    "6": 9,
    "b6": 8,
    "#6": 10,
    "##6": 11,
    "bb6": 7,

    "7": 11,
    "b7": 10,
    "#7": 0,
    "##7": 1,
    "bb7": 9,

    "9": 2,
    "b9": 1,
    "#9": 3,
    "##9": 4,
    "bb9": 0,

    "11": 5,
    "b11": 4,
    "#11": 6,
    "##11": 7,
    "bb11": 3,

    "13": 9,
    "b13": 8,
    "#13": 10,
    "##13": 11,
    "bb13": 7,
}

QUALITY_TO_INTERVALS = {
    "":     ["1", "3", "5"],
    "maj":  ["1", "3", "5"],
    "min":  ["1", "b3", "5"],
    "dim":  ["1", "b3", "b5"],
    "aug":  ["1", "3", "#5"],
    "7":    ["1", "3", "5", "b7"],
    "maj7": ["1", "3", "5", "7"],
    "min7": ["1", "b3", "5", "b7"],
    "dim7": ["1", "b3", "b5", "bb7"],
    "hdim7": ["1", "b3", "b5", "b7"],
    "minmaj7": ["1", "b3", "5", "7"],
    "maj6": ["1", "3", "5", "6"],
    "min6": ["1", "b3", "5", "6"],
    "9": ["1", "3", "5", "b7", "9"],
    "maj9": ["1", "3", "5", "7", "9"],
    "min9": ["1", "b3", "5", "b7", "9"],
    "sus2": ["1", "2", "5"],
    "sus4": ["1", "4", "5"],
    "7sus4": ["1", "4", "5", "b7"],
    "aug7": ["1", "3", "#5", "b7"],
    "5": ["1", "5"],
    "add11": ["1", "3", "5", "11"],
    "add9": ["1", "3", "5", "9"],
    "6/9": ["1", "3", "5", "6", "9"],
    "maj13": ["1", "3", "5", "7", "9", "11", "13"],
    "min13": ["1", "b3", "5", "b7", "9", "11", "13"],
    "13": ["1", "3", "5", "b7", "9", "11", "13"],
    "11": ["1", "3", "5", "b7", "9", "11"],
    "min11": ["1", "b3", "5", "b7", "9", "11"],
    "maj11": ["1", "3", "5", "7", "9", "11"],
    "7b9": ["1", "3", "5", "b7", "b9"],
    "7#9": ["1", "3", "5", "b7", "#9"],
    "7#11": ["1", "3", "5", "b7", "#11"],
    "7b13": ["1", "3", "5", "b7", "b13"],
    "1": ["1"],
    "sus4(b7)": ["1", "4", "5", "b7"],
}

filename = "CS429/unique.txt"

def load_chords(filename):
    with open(filename, "r") as f:
        chords = [line.strip() for line in f if line.strip()]
    return chords

chords = load_chords(filename)

def parse_harte(chord):
    if chord in ["N", "X"]:
        return None

    root, rest = chord.split(":", 1)

    if "/" in rest:
        rest, bass = rest.split("/", 1)
    else:
        bass = None

    mods = []
    if "(" in rest:
        quality, mod_str = rest.split("(", 1)
        mods = mod_str.rstrip(")").split(",")
    else:
        quality = rest

    return root, quality.strip(), mods, bass

IONIAN = ["C","D","E","F","G","A","B"]

def get_letter(root, degree):
    root_letter = root[0]
    start = IONIAN.index(root_letter)

    num = int(degree.lstrip("b#"))
    step = (num - 1) % 7

    return IONIAN[(start + step) % 7]

def spell_note(root, degree, target_semitone):
    letter = get_letter(root, degree)

    natural_map = {
        "C": 0, "D": 2, "E": 4, "F": 5,
        "G": 7, "A": 9, "B": 11
    }

    base = natural_map[letter]
    diff = (target_semitone - base) % 12

    if diff == 0:
        return letter
    elif diff == 1:
        return letter + "#"
    elif diff == 11:
        return letter + "b"
    elif diff == 2:
        return letter + "##"
    elif diff == 10:
        return letter + "bb"
    else:
        return letter  # fallback (rare edge cases)

def symbolize(notes):
    new_notes = []

    for note in notes:
        if note.endswith("##"):
            new_notes.append("^^" + note[0])
        elif note.endswith("bb"):
            new_notes.append("__" + note[0])
        elif note.endswith("#"):
            new_notes.append("^" + note[0])
        elif note.endswith("b"):
            new_notes.append("_" + note[0])
        else:
            new_notes.append(note)

    return new_notes

def harte_to_abc(chord):
    parsed = parse_harte(chord)
    if parsed is None:
        return None

    r, q, m, b = parsed
    r_semitone = ROOT_TO_SEMITONE[r]

    base_intervals = QUALITY_TO_INTERVALS.get(q, ["1", "3", "5"])
    intervals = base_intervals + m

    notes = []

    for interval in intervals:
        if interval not in DEGREE_TO_SEMITONE:
            continue

        semitone = (r_semitone + DEGREE_TO_SEMITONE[interval]) % 12
        note = spell_note(r, interval, semitone)
        notes.append(note)

    # handle bass (always degree-based per your system)
    if b:
        bass_semitone = (r_semitone + DEGREE_TO_SEMITONE[b]) % 12
        bass_note = spell_note(r, b, bass_semitone)

        notes = [bass_note] + [n for n in notes if n != bass_note]
    
    notes = symbolize(notes) # convert to ABC accidental notation

    return "[" + " ".join(notes) + "]"
    
#TESTING
#chord1 = "C:maj7"
#chord2 = "D:min7"
#chord3 = "E:dim"
#chord4 = "Gb:maj9(#11)"
#chord5 = "G:sus4(b7,9,13)"
#chord6 = "Ab:sus4/2"
#chord7 = "Gb:sus4(b7)/4"
#chord8 = "B#:maj9(#11)/5"
#chord9 = "C:dim7"

#parse1 = parse_harte(chord1)
#parse2 = parse_harte(chord2)
#parse3 = parse_harte(chord3)
#parse4 = parse_harte(chord4)
#parse5 = parse_harte(chord5)

#print(parse_harte("C:maj7"))
#print(parse_harte("D:min7"))
#print(parse_harte("E:dim"))
#print(parse_harte("Gb:maj9(#11)"))
#print(parse_harte("G:sus4(b7,9,13)"))
#print(parse_harte("Ab:sus4/2"))

#print(harte_to_abc(chord1))
#print(harte_to_abc(chord2))
#print(harte_to_abc(chord3))
#print(harte_to_abc(chord4))
#print(harte_to_abc(chord5))
#print(harte_to_abc(chord6))
#print(harte_to_abc(chord7))
#print(harte_to_abc(chord8))
#print(harte_to_abc(chord9))