import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import csv
import librosa


class Yamnet():
  def __init__(self):
    self.model = hub.load('https://tfhub.dev/google/yamnet/1')

    class_map_path = self.model.class_map_path().numpy()
    self.class_names = class_names_from_csv(class_map_path)


    self.yamnet.load_weights(weights_path)
    self.yamnet_classes = yamnet_model.class_names(class_names)

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
  def ensure_sample_rate(
                       waveform,
                       sr,
                       desired_sr=16000):
    if len(waveform.shape) > 1:
      waveform = np.mean(waveform, axis=1)
    if sr != desired_sr:
      waveform = resampy.resample(waveform, sr, desired_sr)
    return waveform

  # returns num_top highest score predictions
  def predict_classes(self, waveform, sr, num_top=3):
    # waveform = waveform.astype('float32')
    waveform = ensure_sample_rate(waveform, sr)
    scores, embeddings, spectrogram = self.model(waveform)
    # Scores is a matrix of (time_frames, num_classes) classifier scores.
    # Average them along time to get an overall classifier output for the clip.
    prediction = np.mean(scores, axis=0)
    # Report the highest-scoring classes and their scores.
    top_predictions = np.argsort(prediction)[::-1][:num_top]
    return top_predictions

  def verify_class(self, waveform, sr, expected_class, reject_class=["Silence"]):
    top_predictions = self.predict_classes(waveform, sr, num_top=3)
    # check if expected classes found in predictions
    if expected_class in self.yamnet_classes[top_predictions]:
      # filter out reject classes
      if self.yamnet_classes[top_predictions][0] not in reject_class:
        print(f'found {expected_class} in {self.yamnet_classes[top_predictions]}')
        return True
      else:
        print(f'sample rejected for {reject_class[0]}')
        return False
    else:
      print(f'sample rejected, {expected_class} not identified')
      return False