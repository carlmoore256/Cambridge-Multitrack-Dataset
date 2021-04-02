# main utility for mapping keywords, features, and AudioSet classes to multitracks

import json
import yamnet_classifier
import argparse
import os

from yamnet_classifier import Yamnet
import extract_labels
import file_utils
import audio_utils

# def create_map(kw_map, keywords):
#     # yamnet = Yamnet()
#     kw_keys = kw_map.keys()
#     kw_filter = extract_labels.FilterStems()
#     for k in kw_keys:
#         session = {}
#         vals = kw_map[k].values()
#         vals = set(vals)
#         for a in vals:
#             print(a)

def get_session_name(dirs):

    for session_name in dirs:
        if all(["__MACOSX" not in session_name, 
                len(session_name) > 0]):
            if session_name.endswith("_Full"): # remove "full" from end
                session_name = session_name[:-5]
            return session_name
    return None

def is_valid_file(f):
    if f[0] != "." and f.endswith(".wav"):
        return True
    return False

# loads and pre-processes audio for yamnet input
# ws = window size, only for analysis
# function will return clips of varying lengths
def extract_clips(path, silence_thresh, ws=2048, hop=1024, min_len=4096):
    # load the track
    audio = audio_utils.load_audio(path, 16000, 1)
    # return clips where audio exceeds db threshold
    clips, intervals, num_samps = audio_utils.strip_silence(audio,
                                                silence_thresh,
                                                frame_length=ws,
                                                hop_length=hop,
                                                min_len=min_len)
    return clips, intervals, num_samps

def create_map(data_path, kw_path, conf_thresh, silence_thresh):
    yamnet = Yamnet()

    keywords = file_utils.load_keywords(kw_path)

    kw_filt = extract_labels.FilterStems(keywords, conf_thresh)

    dir_map = {}

    for root, dirs, files in os.walk(data_path):
        if len(dirs) > 0:
            session_name = get_session_name(dirs)

        if session_name is not None and len(files) > 0:

            dir_map[session_name] = {}

            for f in files:
                if is_valid_file(f):
                    track = f[:-4]
                    dir_map[session_name][track] = {}
                    matched_kw = kw_filt.filter(f)

                    full_path = os.path.join(root, f)
                    full_path = os.path.abspath(full_path)

                    # REMOVE SILENCE BEFORE YAMNET PROCESSING
                    clips, intervals, num_samps = extract_clips(full_path,
                                                                silence_thresh,
                                                                ws=2048, 
                                                                hop=1024, 
                                                                min_len=4096)

                    audioset_classes = []
                    for c, i in zip(clips, intervals):
                        classes = yamnet.predict_classes(waveform = c, 
                                                sr = 16000,
                                                num_top = 5)
                        print(f"predicted classes {classes} for samp idx {i}")


                    dir_map[session_name][track]["path"] = full_path
                    dir_map[session_name][track]["keywords"] = matched_kw


                    print(f'---{full_path} {matched_kw}')

    # for k in kw_keys:
    #     session = {}
    #     vals = kw_map[k].values()
    #     vals = set(vals)
    #     for a in vals:
    #         print(a)

if __name__ == "__main__":
  # generates a json containing sample indexes of verified classes for each track
  # see https://research.google.com/audioset/dataset/index.html for list of valid AudioSet labels
  # if a verified map already exists, the file will be updated with the new information added
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="./multitracks/", 
        help="path to downloaded mutlitracks")
    parser.add_argument("--out", type=str, default="./full_map.json", 
        help="output path of verified map")
    parser.add_argument("--map", type=str, default="dataset_map.json", 
        help="path do json dataset map, if it does not exist one will be created")
    parser.add_argument("-kw", type=str, default="keywords.txt",
        help="keywords txt file that specifies search terms")
    parser.add_argument("--c_thresh", type=int, default=80,
        help="confidence threshold for fuzzy string matching")
    parser.add_argument("--thresh", type=int, default=45, 
        help="threshold in db to reject silence")

    args = parser.parse_args()

    # try:
    #     kw_map = file_utils.load_json(args.map)
    # except:
    #     print("could not load keyword map, creating one instead")
    #     kw_map = extract_labels.create_label_map(args.path, args.kw, args.c_thresh)

    # create_map(kw_map, args.kw)
    create_map(args.path, args.kw, args.c_thresh, args.thresh)