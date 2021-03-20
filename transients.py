# transient location and extraction
import librosa
import numpy as np

# return list of onset (transient) times and beats
# backtrack detects minimum before transient
def extract_transients(audio, sr, ws, start_pad, hop=512, backtrack=True):
  beats = librosa.onset.onset_detect(y=audio, sr=sr, units='frames', hop_length=hop, backtrack=backtrack)
  frames = librosa.util.frame(audio, frame_length=ws, hop_length=hop)
  
  return frames.T, beats

# verify transients are at same position
def correlate_transients(x, y):
  shared = np.intersect1d(x, y)
  print(f'len x {len(x)} len y {len(y)} len shared {len(shared)}')

  return shared