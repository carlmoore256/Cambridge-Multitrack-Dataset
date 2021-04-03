import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
import audio_utils
import librosa


class Yamnet():
  def __init__(self):
    self.model = hub.load('https://tfhub.dev/google/yamnet/1')

    class_map_path = self.model.class_map_path().numpy()
    self.yamnet_classes = self.class_names_from_csv(class_map_path)

  # Find the name of the class with the top score when mean-aggregated across frames.
  def class_names_from_csv(self, class_map_csv_text):
    """Returns list of class names corresponding to score vector."""
    class_names = []
    with tf.io.gfile.GFile(class_map_csv_text) as csvfile:
      reader = csv.DictReader(csvfile)
      for row in reader:
        class_names.append(row['display_name'])

    return class_names

  # Ensure sr and channels match expected input to yamnet (16000, mono)
  def ensure_sample_rate(waveform,
                       sr,
                       desired_sr=16000):
    # if len(waveform.shape) > 1:
    #   waveform = np.mean(waveform, axis=1)
    if sr != desired_sr:
      waveform = resampy.resample(waveform, sr, desired_sr)
    return waveform

  # returns num_top highest score predictions
  def predict_classes(self, waveform, sr, num_top=3):
    # waveform = waveform.astype('float32')
    # waveform = self.ensure_sample_rate(waveform, sr)
    scores, embeddings, spectrogram = self.model(waveform)
    # Scores is a matrix of (time_frames, num_classes) classifier scores.
    # Average them along time to get an overall classifier output for the clip.
    prediction = np.mean(scores, axis=0)
    # Report the highest-scoring classes and their scores.
    top_predictions = np.argsort(prediction)[::-1][:num_top]
    return top_predictions

  # maps the integer prediction to the class string
  def map_audioset_classes(self, predictions):
    return np.take(self.yamnet_classes, predictions)

  def verify_class(self, waveform, sr, expected_classes, reject_classes=["Silence"]):
    top_predictions = self.predict_classes(waveform, sr, num_top=3)

    top_predictions = self.map_audioset_classes(top_predictions)
    # check for positive matches
    pos_matches = self.compare_intersect(top_predictions, expected_classes)
    # check against rejection classes like "Silence"
    neg_matches = self.compare_intersect(pos_matches, reject_classes)

    if len(pos_matches) > 0:
      if len(neg_matches) == 0:
        print(f'found {pos_matches} in {top_predictions}')
        return pos_matches
      else:
        print(f'rejected for {neg_matches}')
        return None
    else:
      return None
      print(f'no matching classes identified')

    # matches = set(self.yamnet_classes[top_predictions]) & set(expected_classes)
  
    # # check if expected classes found in predictions
    # if expected_classes in self.yamnet_classes[top_predictions]:
    #   # filter out reject classes
    #   if self.yamnet_classes[top_predictions][0] not in reject_classes:
    #     print(f'found {expected_classes} in {self.yamnet_classes[top_predictions]}')
    #     return True
    #   else:
    #     print(f'sample rejected for {reject_classes[0]}')
    #     return False
    # else:
    #   print(f'sample rejected, {expected_classes} not identified')
    #   return False

  # courtesy of https://stackoverflow.com/questions/1388818/how-can-i-compare-two-lists-in-python-and-return-matches
  def compare_intersect(self, x, y):
    # return set(x) & set(y)
    return frozenset(x).intersection(y)

# contains utilities for mapping classes to proper string classes
class AudiosetClasses():
  def __init__(self, path):
    self.class_map = self.load_class_map(path)
  
  def load_class_map(self, path):
    class_map = {}
    with open(path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          class_map[int(row["index"])] = row["display_name"]
    return class_map

  # return the string array of int classes
  def get_class_str(self, classes):
    return [self.class_map[int(c)] for c in classes]