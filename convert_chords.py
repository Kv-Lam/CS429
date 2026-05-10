import json
import os
import glob
import sys


def convert_folder(input_folder, output_file):
    """
    Converts all JSON chord files in a folder to a single train.txt
    formatted for GPT-2 fine-tuning with Hugging Face Transformers.

    Output format per song (one line):
        <|title|> Song Name <|key|> C <|chords|> chord1 chord2 ... <|endoftext|>
    """
    json_files = glob.glob(os.path.join(input_folder, "*.json"))

    if not json_files:
        print(f"  No JSON files found in '{input_folder}'")
        return 0, 0

    json_files.sort()
    written = 0
    skipped = 0

    with open(output_file, "w", encoding="utf-8") as out:
        for filepath in json_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                title = data.get("title", "").strip()
                key = data.get("key", "").strip()
                chords = data.get("chords", [])

                if not title or not key or not chords:
                    print(f"  Skipping {os.path.basename(filepath)}: missing title, key, or chords")
                    skipped += 1
                    continue

                chord_str = " ".join(chords)

                line = (
                    f"<|title|> {title} "
                    f"<|key|> {key} "
                    f"<|chords|> {chord_str} "
                    f"<|endoftext|>\n"
                )

                out.write(line)
                written += 1

            except (json.JSONDecodeError, KeyError) as e:
                print(f"  Skipping {os.path.basename(filepath)}: {e}")
                skipped += 1

    return written, skipped


def main():
    # Default paths — edit these if running without command line args
    abc_folder   = "data/ABC"
    harte_folder = "data/Harte"
    abc_output   = "train_abc.txt"
    harte_output = "train_harte.txt"

    # Allow overrides via command line: python convert_chords.py <abc_folder> <harte_folder>
    if len(sys.argv) == 3:
        abc_folder   = sys.argv[1]
        harte_folder = sys.argv[2]
    elif len(sys.argv) != 1:
        print("Usage: python convert_chords.py [<abc_folder> <harte_folder>]")
        print("Defaults: data/ABC and data/Harte")
        sys.exit(1)

    print(f"\n--- Converting ABC notation: '{abc_folder}' ---")
    abc_written, abc_skipped = convert_folder(abc_folder, abc_output)
    print(f"  Written : {abc_written} | Skipped : {abc_skipped} | Output : '{abc_output}'")

    print(f"\n--- Converting Harte notation: '{harte_folder}' ---")
    harte_written, harte_skipped = convert_folder(harte_folder, harte_output)
    print(f"  Written : {harte_written} | Skipped : {harte_skipped} | Output : '{harte_output}'")

    print(f"\nAll done. Total songs written: {abc_written + harte_written}")


if __name__ == "__main__":
    main()