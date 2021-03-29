# file saving & loading utils

import json

def save_json(out_path, data):
  with open(out_path, 'w') as outfile:
    json.dump(data, outfile, sort_keys=True, indent=4)
  print(f'wrote json to {out_path}')

def load_json(path):
  with open(path) as json_file:
      jfile = json.load(json_file)
  return jfile
