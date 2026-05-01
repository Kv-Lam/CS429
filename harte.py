import jams
import glob
import os
import json

def write_json_file(data, output_path):
    file = output_path[19:-5] #Get rid of v1.0.0/v1.0.0/jams/ from the start and .jams from the end.
    file = file + '_' + (data["representation"])
    
    with open("data/Harte/" + file + ".json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

for jam_path in glob.glob("v1.0.0/v1.0.0/jams/billboard_*.jams"):
    print("Processing:", jam_path)
    
    jam = jams.load(jam_path, validate=False)
    ann = jam["annotations"][0]["data"]
    metadata = jam["file_metadata"]
    
    chords = [observation.value for observation in ann if observation.value not in ("N", "X")]
    
    data = {
        "title": metadata["title"],
        "key": jam["annotations"][1]["data"][0].value,
        "representation": "Harte",
        "chords": chords
    }
    
    write_json_file(data, jam_path)