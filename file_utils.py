# file saving & loading utils

import json
import os
# import csv


def save_json(out_path, data, indent=3):
  with open(out_path, 'w') as outfile:
    json.dump(data, outfile, sort_keys=False, indent=indent)
  print(f'wrote json to {out_path}')

def load_json(path):
  with open(path) as json_file:
      jfile = json.load(json_file)
  return jfile

def load_keywords(path):
  keywords = []
  param_file = open(path, "r")
  lines = param_file.readlines()
  for l in lines:
    keywords.append(l.strip())
  return keywords


# useful for iterating dataset map, yields an individual track
def iterate_dataset_map(path):
  dataset_map = load_json(path)
  for a in dataset_map.keys():
    for b in dataset_map[a].keys():
      yield dataset_map[a][b]
        

