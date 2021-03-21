# methods for verifying that audio data matches its label
# create a json directory to sound events verified by yamnet
from yamnet_classifier import Yamnet
import resampy
import argparse
import numpy as np
import requests
import utils
import os

def verify_stems(json, sr, key_list, yamnet_classes, thresh_db, frame_len, hop, min_len, save_dir='', max_secs=120*60):

  def save_npy(key, data):
    data = np.asarray(all_clips)
    np.save(f'{save_dir}{key}_{save_count}.npy', data)
    save_count += 1
    all_samps = 0
    all_clips.clear()

  all_clips = []
  total_sessions = len(json.keys())
  save_count = 0
  all_samps = 0

  for i, k in enumerate(json.keys()):
    tracks = []
    for key in key_list:
      if json[k][key] != None:
        tracks += json[k][key]

    print(f'session {i}/{total_sessions}, found {len(tracks)} tracks')

    for t in tracks:
      print(f'loading {t}')
      waveform = load_audio(t, sr)
      clips, total_samps = strip_silence(waveform, thresh_db, frame_len, hop)

      filt_clips = []

      for c in clips:
        # verify audio with yamnet
        if yamnet.yamnet_inference(c, sr, yamnet_classes):
          filt_clips.append(c)
          all_samps += total_samps

      if len(filt_clips) > 0:
        all_clips.append(filt_clips)

    if all_samps > sr*max_secs:
      all_clips = np.asarray(all_clips)
      np.save(f'{save_dir}{key_list[0]}_{save_count}.npy', all_clips)
      print(f'\n SAVED to save_dir {save_dir}{key_list[0]}_{save_count}.npy \n')
      save_count += 1
      all_samps = 0
      all_clips = []

  return np.asarray(all_clips)

if __name__ == "__main__":
  # generates a json containing sample indexes of verified classes for each track
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


  sr=44100
  key_list = ['vox', 'vocal']
  yamnet_classes = ['Speech'] # list of matching classes for keys
  thresh_db = 45
  frame_len = 2048 # analysis frame
  hop = 1024 # analysis hop
  min_len = 16384 # in samples
  save_dir = '/content/drive/My Drive/Datasets/VoxVerified/'

  verified_clips = verify_stems(data, sr, key_list, yamnet_classes, thresh_db, frame_len, hop, min_len, save_dir)
  print(verified_clips.shape)