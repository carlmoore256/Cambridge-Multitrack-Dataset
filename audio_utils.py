# various utils for working with waveform audio
import numpy as np
import librosa

def load_audio(path, sr, channels=1):
    waveform = librosa.load(path, sr=sr, res_type='kaiser_fast')
    return waveform[0]

# given an input waveform, remove silence and return clips above db threshold
def strip_silence(audio, thresh, frame_length=2048, hop_length=512, min_len=8192):
    intervals = librosa.effects.split(audio, 
                                    top_db=thresh, 
                                    frame_length=frame_length,
                                    hop_length=hop_length)
    clips = []
    total_samps = 0

    intervals = [i for i in intervals if i[1]-i[0] >= min_len]

    for i in intervals:
        clips.append(audio[i[0]:i[1]])
        total_samps += i[1] - i[0]

    # for i in intervals:
    #     if i[1] - i[0] >= min_len:
    #         total_samps += i[1] - i[0]
    #         clips.append(audio[i[0]:i[1]])

    # clips = np.asarray(clips)
    return clips, intervals, total_samps

# similar to strip_silence() but returns the indexes above threshdb with min and max length
def samples_above_thresh(audio, thresh, frame_length=2048, hop_length=512, min_len=2048, max_len=16384):
    intervals = librosa.effects.split(audio, 
                                top_db=thresh, 
                                frame_length=frame_length,
                                hop_length=hop_length)
    intervals = [i for i in intervals if i[1]-i[0] >= min_len]
    return intervals

    # filt_intervals = []
    # for i in intervals:
    #     length = i[1] - i[0]
    #     if length >= min_len:
    #         if length > max_len:

    #         filt_intervals.append(i)

# split audio into chunks given start and end indexes in ndarray
# def split_audio_at_idxs()

