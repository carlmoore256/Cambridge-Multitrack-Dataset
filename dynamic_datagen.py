# reads from json verified labels and generates audio clips
# without intermediate step of saving as memmap

import numpy as np
import tensorflow as tf
import json
from threading import Thread
import audio_utils

class DynDatagen():

    # datamap = verified_stems.json, or other json formatted with yamnet_verify.py
    # kw = keyword class to serve, example = "gtr"
    # batch_size = number of stacked examples to serve
    # buffer_min -> DynDatagen will continue loading new files on bg thread until buffer_min is reached (samples)
    def __init__(self, kw, batch_size, min_size=512, datamap="verified_map.json", buffer_min=44100):

        with open(datamap) as json_file:
            self.dataset_map = json.load(json_file)

        # self.keys = dataset_map.keys()
        self.kw = kw

        self.stems = iter(self.dataset_map)
        
        # batch buffer
        self.batch_buff = []

        self.buffer_min = buffer_min

        self.batch_size = batch_size

        self.min_size = min_size

        self.current_item = next(self.stems)
        self.start_fill_thread()

    def start_fill_thread(self):
        self.refresh_buff_t = Thread(target=self.fill_buffer, daemon=True)
        self.refresh_buff_t.start()
        print(f'started fill thread...')


    def load_audio(self, path):
      # tensorflow read file (can read any file)  
      raw_audio = tf.io.read_file(path)
      # decodes raw_audio into -1f to 1f float32 tensor
      waveform = tf.audio.decode_wav(raw_audio, desired_channels=1)
      # waveform[0]: float32 tensor of waveform data
      # waveform[1]: samplerate (ignoring sr for now)
      return waveform[0]

    # loads the next batch to be ready to serve
    # def load_buffer(self):
        # get the num_samps for next load to know how far ahead to load

    # obviously there's a better way to do this, fix this later
    # get everything to stay in tf
    def slice_tensor(self, tensor, idxs):
        sliced = []
        for i in idxs:
            if i[1] - i[0] > self.min_size:
                sliced.append(np.expand_dims(tensor[i[0]:i[1]], 0))
        print(f'\n slice {(sliced)} \n')
        return np.asarray(sliced)


    # return batch
    def fill_buffer(self):
        # assert that fixed size is greater than min size
        self.current_item = next(self.stems)

        b_size = 0
        while b_size < self.buffer_min:
            # item = next(dataset_map)
            stems = self.dataset_map[self.current_item][self.kw]
            print(f'found {len(stems)} stems')

            # often each session has > 1 match for a stem
            for s in stems:
                sub_d = self.dataset_map[self.current_item][self.kw][s]
                print(sub_d)

                # load in the audio array
                audio = audio_utils.load_audio(sub_d["path"], sr=44100)
                num_samps = sub_d["num_samps"]
                indicies = sub_d["verified"]

                sliced = self.slice_tensor(audio, indicies)

                self.batch_buff.append(sliced)

                b_size += num_samps

            b_size = 0
            self.batch_buff = []
            self.current_item = next(self.stems)
        # 
    # fixed size - if 0, ragged tensors will be returned, if > 0, each example will be cut off at fixed_size samples
    def get_batch(self, fixed_size=0):
        this_batch = []
        for i in range(self.batch_size):
            this_batch.append(self.batch_buff.pop)
        this_batch = np.asarray(this_batch)
        print(f'this_batch shape {this_batch.shape}')

        self.start_fill_thread()

        if len(self.batch_buff) == self.batch_size:
            if fixed_size == 0:
                return this_batch
            return this_batch[:, :fixed_size]
        return None

import time

dg = DynDatagen("gtr", 64)

for i in range(10000):
    batch = dg.get_batch()
    print(batch)
    time.sleep(0.3)

