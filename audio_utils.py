# various utils for working with waveform audio
import numpy as np
import librosa

def load_audio(path, sr, channels=1):
  waveform = librosa.load(path, sr=sr, res_type='kaiser_fast')
  return waveform[0]

def strip_silence(audio, thresh, frame_length=2048, hop_length=512, min_len=8192):
  intervals = librosa.effects.split(audio, 
                                    top_db=thresh, 
                                    frame_length=frame_length,
                                    hop_length=hop_length)
  clips = []
  total_samps = 0

  for i in intervals:
    if i[1] - i[0] >= min_len:
      total_samps += i[1] - i[0]
      clips.append(audio[i[0]:i[1]])

  clips = np.asarray(clips)
  return clips, total_samps



