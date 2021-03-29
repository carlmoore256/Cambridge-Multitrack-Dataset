# verify x, y audio stem pairs are recordings of identical content
# captured from different microphones and positions
# see https://github.com/carlmoore256/Mic-Bleed-Removal-CNN for an example use case for this

import librosa
import json
import numpy as np
import file_utils

def extract_transients(audio, sr, ws, start_pad, hop=512, backtrack=True):
    # grab onset times; backtrack detects minimum before transient
    beats = librosa.onset.onset_detect(y=audio, sr=sr, units='frames', hop_length=hop, backtrack=backtrack)
    frames = librosa.util.frame(audio, frame_length=ws, hop_length=hop)
    
    return frames.T, beats

  # verify transients are at same position
def correlate_transients(x, y):
    shared = np.intersect1d(x, y)
    print(f'len x {len(x)} len y {len(y)} len shared {len(shared)}')

    return shared

def analyze_contrast(block, sr=44100):
    S = np.abs(librosa.stft(block))
    contrast = librosa.feature.spectral_contrast(S=S, sr=sr)
    this_avg_contrast = np.mean(contrast)
    return this_avg_contrast

def analyze_envelope(rms_blocks, plot_curves=False): 
    # check whether there is more energy in the first or second half
    f_env = np.linspace(1, 0, num=rms_blocks.shape[1]) # forward envelope
    r_env = np.linspace(0, 1, num=rms_blocks.shape[1]) # reverse envelope

    rms_start = rms_blocks * f_env
    rms_end = rms_blocks * r_env

    if plot_curves:
        plt.plot(rms_start.reshape((rms_start.shape[0] * rms_start.shape[1])), color='red')
        plt.plot(rms_end.reshape((rms_end.shape[0] * rms_end.shape[1])))
        plt.show()

    rms_start = np.mean(rms_start)
    rms_end = np.mean(rms_end)

    if rms_start > rms_end:
        return True
    else:
        return False

def validate_transients(x, y, sr=44100, visualize_rejects=False):
    rms_total = librosa.feature.rms(y=y.reshape((y.shape[0] * y.shape[1])))
    avg_rms = np.median(rms_total)

    x_valid = []
    y_valid = []

    rejects_x = []
    rejects_y = []

    for X, Y in zip(x, y):
        rms_blocks = (librosa.feature.rms(y=Y))
        this_avg = np.mean(rms_blocks)

        # determine if transient happens in first half
        envelope_skew = analyze_envelope(rms_blocks) 

        if envelope_skew and this_avg > avg_rms:
            x_valid.append(X)
            y_valid.append(Y)
        else:
            rejects_x.append(X)
            rejects_y.append(Y)

    x_valid = np.asarray(x_valid)
    y_valid = np.asarray(y_valid)
    print(f'valid samples {x_valid.shape[0]}')

    if visualize_rejects:
        rejects_x = np.asarray(rejects_x)
        rejects_y = np.asarray(rejects_y)
        visualize_audio_data(rejects_x, rejects_y, sr=sample_rate) #see what is rejected

    return x_valid, y_valid

def gen_dataset(data:"JSON dataset map",
                ws:"window size", 
                x_key,
                y_key,
                normalize_stems=False,
                normalize_transients=False, 
                max_examples=100,
                sample_rate=44100,
                difference_mask=False): #"difference_mask = output y as (x - y)"
  x_train = []
  y_train = []

  for i, k in enumerate(data.keys()):
    x = data[k][x_key]
    y = data[k][y_key]
    try:
      if len(x) > 0 and len(y) > 0:

        print(f'loading {data[k][x_key][0]}')
        print(f'loaded {i} of {max_examples}')

        audio_x, sr = librosa.load(data[k][x_key][0], sr=sample_rate, res_type='kaiser_fast')
        audio_y, _ = librosa.load(data[k][y_key][0], sr=sample_rate, res_type='kaiser_fast')

        if normalize_stems: # NORMALIZES ENTIRE STEM, NOT INDIVIDUAL SAMPLES
          audio_x = librosa.util.normalize(audio_x)
          audio_y = librosa.util.normalize(audio_y)

        print('loaded files, analyzing transients')
        frames_x, bx = extract_transients(audio_x, sr, ws, 0)
        frames_y, by = extract_transients(audio_y, sr, ws, 0)

        idx_shared = correlate_transients(bx, by)

        tx = frames_x[idx_shared]
        ty = frames_y[idx_shared]

        tx, ty = validate_transients(tx, ty) # verify transients are clean

        for x_trans, y_trans in zip(tx, ty):
          if normalize_transients:
            x_trans = librosa.util.normalize(x_trans)
            y_trans = librosa.util.normalize(y_trans)

          if difference_mask: # calcuate difference
            y_trans = x_trans - y_trans
          
          x_train.append(x_trans)
          y_train.append(y_trans)
    except:
      print('error with loading file, skipping')
      continue

    if i+1 > max_examples:
      break
    
  x_train = np.asarray(x_train)
  y_train = np.asarray(y_train)
  
  print(f'x shape {x_train.shape} y shape {y_train.shape}')

  return x_train, y_train

if __name__ == "__main__":

    dataset_map = file_utils.load_json("dataset_map.json")

    x_key = "overhead"
    y_key = "snare"

    for k in dataset_map.keys():

        mt = dataset_map[k]

        if x_key in mt.keys() and y_key in mt.keys():
            print(dataset_map[k][x_key])
            print(dataset_map[k][y_key])
