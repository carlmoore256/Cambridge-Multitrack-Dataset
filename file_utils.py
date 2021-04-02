# file saving & loading utils

import json
import os
def save_json(out_path, data):
  with open(out_path, 'w') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=4)
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

# def session_file_iterator(path):

#   while True:

#     yield 
