# various methods for verifying that audio data matches its label

import params as yamnet_params
import yamnet as yamnet_model
import resampy
import requests
import utils
import os

# yamnet verification - classifier trained on audioset 
class Yamnet():
  def __init__(self, weights='yamnet.h5', class_names='yamnet_class_map.csv'):
    self.download_weights()
    self.params = yamnet_params.Params()
    self.yamnet = yamnet_model.yamnet_frames_model(self.params)
    self.yamnet.load_weights(weights)
    self.yamnet_classes = yamnet_model.class_names('yamnet_class_map.csv')

  def download_weights(self, path="./yamnet/model/yamnet.h5"):
    if not os.path.exists("./yamnet/model/yamnet.h5"):
      print(f"downloading yamnet weights to {path}")
      utils.download("https://storage.googleapis.com/audioset/yamnet.h5", "./yamnet/model/yamnet.h5")
    else:
      print(f"using yamnet weights found at {path}")

  def yamnet_inference(self, waveform, sr, expected_class):
    waveform = waveform.astype('float32')

    # Convert to mono and the sample rate expected by YAMNet.
    if len(waveform.shape) > 1:
      waveform = np.mean(waveform, axis=1)
    if sr != self.params.sample_rate:
      waveform = resampy.resample(waveform, sr, self.params.sample_rate)

    # Predict YAMNet classes.
    scores, embeddings, spectrogram = self.yamnet(waveform)
    # Scores is a matrix of (time_frames, num_classes) classifier scores.
    # Average them along time to get an overall classifier output for the clip.
    prediction = np.mean(scores, axis=0)
    # Report the highest-scoring classes and their scores.
    top_predictions = np.argsort(prediction)[::-1][:3]

    if expected_class in self.yamnet_classes[top_predictions]:
      if self.yamnet_classes[top_predictions][0] != 'Silence':
        print(f'found {expected_class} in {self.yamnet_classes[top_predictions]}')
        return True
      else:
        print('rejected for silence')
        return False
    else:
      return False

    # print(self.yamnet_classes[top5_i][0])

    # for t in top5_i:
    #   print(self.yamnet_classes[t])

yamnet = Yamnet()



import numpy as np
import matplotlib.pyplot as plt
import IPython.display as ipd
import random

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

          # if len(c) < sr*3 and random.random() < 0.05:
          #   plt.title('accepted')
          #   plt.plot(c, color='green')
          #   ipd.display(ipd.Audio(c, rate=sr, autoplay=False))
          #   plt.show()
          #   print('\n =============================== \n')
        # else:
        #   if len(c) < sr*3 and random.random() < 0.05:
        #     plt.title('accepted')
        #     plt.plot(c, color='green')
        #     ipd.display(ipd.Audio(c, rate=sr, autoplay=False))
        #     plt.show()
        #     print('\n =============================== \n')

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