# generate json directory map for the dataset
# extract labels from wave file stems

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import argparse
import json
import os

class FilterStems():
  def __init__(self, keywords, conf_thresh=90):
    self.keywords = keywords
    self.conf_thresh = conf_thresh

  def filter(self, name):
    result = False
    word, score = process.extractOne(name, self.keywords)
    if score >= self.conf_thresh:
      return [True, word]
    else:
      return [False, None]

def load_keywords(path):
  keywords = []
  param_file = open(path, "r")
  lines = param_file.readlines()
  for l in lines:
    keywords.append(l.strip())
  return keywords

# main func that generates json label map. Walks thru paths & matches labels
def create_label_map(data_path, kw_filter, save_path="./"):

  dir_map = {}

  for root, dirs, files in os.walk(data_path):
    # get name of current folder
    if len(dirs) > 0:
      session_name = dirs[0]

    # thanks apple
    if '__MACOSX' not in session_name:
      matched_kw = []

      for f in files:
        # filter out macos junk files
        if f[0] != '.' and f.endswith('.wav'):
          # check the filename against keyword filters
          result, kw = kw_filter.filter(f)

          if result:
            # add session to the map if it's not there yet
            if not session_name in dir_map.keys():
              dir_map[session_name] = { "path" : root }
              # initialize with all keys
              for p in kw_filter.keywords:
                dir_map[session_name][p] = []
            # add location of wav stem to session kw
            dir_map[session_name][kw].append(root + '/' + f)
            matched_kw.append(kw)
      if len(matched_kw > 0):
        print(f'found {matched_kw} in {session_name} ({len(matched_kw)} total files)')
  return dir_map

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="./multitracks/", 
        help="path to downloaded mutlitracks")
    parser.add_argument("-kw", type=str, default="keywords.txt",
        help="keywords txt file that specifies search terms")
    parser.add_argument("--c_thresh", type=int, default=80,
        help="confidence threshold for fuzzy string matching")
    parser.add_argument("-o", type=str, default="./dataset_map.json", 
        help="output file for dataset map")
    args = parser.parse_args()

    kw_filter = FilterStems(load_keywords(args.kw), args.c_thresh)
    print("filtering mutlitrack stems for labels")
    dir_map = create_label_map(args.path, kw_filter)

    with open(args.o, 'w') as outfile:
      json.dump(dir_map, outfile)

    print(f"directory map saved to {args.o}")








