# transient location and extraction
# create x, y pairs of related onsets for linear regression
import librosa
import numpy as np

# return list of onset (transient) times and beats
def extract(audio, sr, ws, start_pad, hop=512, backtrack=True):
  beats = librosa.onset.onset_detect(y=audio, sr=sr, units='frames', hop_length=hop, backtrack=backtrack)
  frames = librosa.util.frame(audio, frame_length=ws, hop_length=hop)
  return frames.T, beats

# find shared indexes between x and y
def correlate(x, y):
  return np.intersect1d(x, y)

# create dataset of x,y pairs containing correlated transients
def correlated_transients_xy(data:"JSON dataset map",
                ws:"window size", 
                x_key,
                y_key):
  x_data = []
  y_data = []

  for k in data.keys():
    x = data[k][x_key]
    y = data[k][y_key]

    if len(x) > 0 and len(y) > 0:
      print(f'loading {data[k][x_key][0]}')
      audio_x, sr = librosa.load(data[k][x_key][0], res_type='kaiser_fast')
      audio_y, _ = librosa.load(data[k][y_key][0], res_type='kaiser_fast')

      print('loaded files, analyzing transients')
      frames_x, bx = transients.extract(audio_x, sr, ws, 0)
      frames_y, by = transients.extract(audio_y, sr, ws, 0)

      idx_shared = transients.correlate(bx, by)

      tx = frames_x[idx_shared]
      ty = frames_y[idx_shared]
      
      for x_trans, y_trans in zip(tx, ty):
        x_data.append(x_trans)
        y_data.append(y_trans)
    
  x_data = np.asarray(x_data)
  y_data = np.asarray(y_data)
  
  print(x_data.shape, y_data.shape)

  return x_data, y_data