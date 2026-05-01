import jams
import glob

# for jam_path in glob.glob("v1.0.0/v1.0.0/jams/billboard_*.jams"):
#     jam = jams.load("v1.0.0/v1.0.0/jams/billboard_1.jams")
#     print(jam["annotations"][2])    
#     # if jam["data"]


jam = jams.load("v1.0.0/v1.0.0/jams/billboard_36.jams")

print(jam["annotations"][1]["data"][0].value)    

# ann = jam["annotations"][0]["data"]
