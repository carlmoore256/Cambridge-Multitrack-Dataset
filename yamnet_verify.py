# verify audio stems match their label using YAMNet
# https://github.com/tensorflow/models/tree/master/research/audioset/yamnet
# creates a json directory of sample indicies per stem where stems matching the
# -kw argument in the local cambridge MT library are verified by YAMNet as belonging
# to the given list of classes specified by the --approve argument

from yamnet_classifier import Yamnet
import audio_utils
import resampy
import argparse
import numpy as np
import file_utils
import requests
import json
import os

# def save_json(out_path, data):
#   with open(out_path, 'w') as outfile:
#     json.dump(data, outfile, sort_keys=True, indent=4)
#   print(f'wrote json to {out_path}')

# def load_json(path):
#   with open(path) as json_file:
#       jfile = json.load(json_file)
#   return jfile

# kw_class - class in keywords.txt to match (only one allowed)
# yam_approve - any of the 527 classes in audioset to match for
# yam_reject - any of the 527 classes in audioset to reject
# https://research.google.com/audioset/dataset/index.html
def verify_classes_yamnet(verified_classmap, dataset_map, silence_thresh, kw_class, yam_approve, yam_reject=['Silence']):

  yamnet = Yamnet()
  
  # verified_classmap = {}
  cm_keys = verified_classmap.keys()

  total_sessions = len(dataset_map.keys())

  print(f'TOTAL SESSIONS : {total_sessions}')

  for i, k in enumerate(dataset_map.keys()):
    print(f'ENUMERATING KEY {i}')
    # get all matching stems for kw_class
    matching_stems = dataset_map[k][kw_class]

    if k not in cm_keys:
      verified_classmap[k] = {}

    # by default this will overwrite an existing class
    verified_classmap[k][kw_class] = {}

    print(f'verifying {len(matching_stems)} stems in {k}')

    for stem in matching_stems:
      stem_name = os.path.splitext(stem)[0]
      stem_name = os.path.basename(stem_name)
      
      # array of sample indicies 
      verified_indicies = []

      # TODO: array of yamnet matched classes
      # matched_classes = []'

      # load the stem audio
      stem_audio = audio_utils.load_audio(stem, 16000, 1)
      # return clips where audio exceeds db threshold
      clips, intervals, num_samps = audio_utils.strip_silence(stem_audio,
                                                    silence_thresh,
                                                    frame_length=2048,
                                                    hop_length=512,
                                                    min_len=4096)
                                                    
      for c, i in zip(clips, intervals):
        classes = yamnet.verify_class(c, 16000, yam_approve, yam_reject)
        if classes is not None:
          verified_indicies.append([int(i[0]), int(i[1])])
          # matched_classes.append(classes)

      # matched_classes = set(matched_classes)

      if len(verified_indicies) > 0:
        verified_classmap[k][kw_class][stem_name] = {}
        verified_classmap[k][kw_class][stem_name]["path"] = stem
        verified_classmap[k][kw_class][stem_name]["verified"] = list(verified_indicies)
        verified_classmap[k][kw_class][stem_name]["num_samps"] = int(num_samps)
        # TODO: add matched class labels to dict
        # verified_indicies[k][kw_class][stem_name]["audioset_label"] = matched_classes
  return verified_classmap


if __name__ == "__main__":
  # generates a json containing sample indexes of verified classes for each track
  # see https://research.google.com/audioset/dataset/index.html for list of valid AudioSet labels
  # if a verified map already exists, the file will be updated with the new information added
  parser = argparse.ArgumentParser()
  parser.add_argument("--path", type=str, default="./multitracks/", 
      help="path to downloaded mutlitracks")
  parser.add_argument("--out", type=str, default="./verified_map.json", 
      help="output path of verified map")
  parser.add_argument("-kw", type=str, default="vox",
      help="keyword filter, only one allowed. See keywords.txt for full list")
  parser.add_argument("--approve", type=str, nargs="+", default="Speech",
      help="AudioSet labels to match in source content. Multiple string values allowed (case sensitive)")
  parser.add_argument("--reject", type=str, default="Silence",
      help="AudioSet labels to reject. Multiple string values allowed (case sensitive)")
  parser.add_argument("--map", type=str, default="dataset_map.json", 
      help="path do json dataset map")
  parser.add_argument("--thresh", type=int, default=45, 
      help="threshold in db to reject silence")

  args = parser.parse_args()

  # with open(args.map) as json_file:
  #     dataset_map = json.load(json_file)
  dataset_map = file_utils.load_json(args.map)

  yam_approve = list(args.approve)
  yam_reject = list(args.reject)

  if os.path.exists(args.out):
    print(f'{args.out} already exists, modifying...')
    verified_classmap = file_utils.load_json(args.out)
  else:
    verified_classmap = {}

  
  verified = verify_classes_yamnet(verified_classmap, dataset_map, args.thresh, args.kw, yam_approve, yam_reject)

  file_utils.save_json(args.out, verified)
  print(f'saved verified map to {args.out}')