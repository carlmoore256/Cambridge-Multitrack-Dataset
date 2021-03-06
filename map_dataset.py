# main utility for mapping keywords, features, and AudioSet classes to multitracks

import json
import yamnet_classifier
import argparse
import joblib
import os
import numpy as np

from yamnet_classifier import Yamnet
import extract_labels
import file_utils
import audio_utils

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

# main func for generating complete map with AudioSet classes and matched keywords (see keywords.txt)
# if a dataset map is provided, the entries will be modified in place, overwriting existing entries
# if overwrite=True; save_interval saves the map every n sessions for convenience
def create_map(data_path, kw_path, conf_thresh, silence_thresh, n_jobs=8, dir_map={}, 
               outpath="complete_map.json", overwrite=True, save_interval=5):
    yamnet = Yamnet()
    keywords = file_utils.load_keywords(kw_path)
    kw_filt = extract_labels.FilterStems(keywords, conf_thresh)

    existing_keys = dir_map.keys()
    analyzed = 0

    for root, dirs, files in os.walk(data_path):
        if len(dirs) > 0:
            session_name = get_session_name(dirs)

        write_entry = True

        if session_name is not None and overwrite == False and session_name in existing_keys:
            write_entry = False

        if session_name is not None and len(files) > 0 and write_entry:
            dir_map[session_name] = {}
            # verify the files are valid ones
            valid_files = [os.path.abspath(os.path.join(root, f)) for f in files if is_valid_file(f)]

            print(f"{n_jobs} jobs extracting {len(valid_files)} clips from {session_name}")
            extracted_clips = joblib.Parallel(n_jobs=n_jobs, backend="threading")(joblib.delayed(extract_clips)(f, silence_thresh, 2048, 1024, 4096) for f in valid_files)

            print(f"calculating features for {len(valid_files)} tracks in {session_name}")

            for i, (clips, intervals, num_samps) in enumerate(extracted_clips):
                full_path = valid_files[i]

                # REMOVE SILENCE BEFORE YAMNET PROCESSING
                # clips, intervals, num_samps = extract_clips(full_path,
                #                                             silence_thresh,
                #                                             ws=2048, 
                #                                             hop=1024, 
                #                                             min_len=4096)

                audioset_classes = []
                corrected_intervals = []
                corrected_num_samps = 0

                # consider chopping these up into smaller bits for input to yamnet for 
                # more accurate classification
                for j, (clip, interval) in enumerate(zip(clips, intervals)):

                    subframes = get_frames(clip, 16384, 16384) # slip each clip into sub-frames
                    print(f'processing {len(subframes)} sub frames')
                    
                    for i, sf in enumerate(subframes):
                        
                        sf_index_start = i * 16384
                        sf_index_end = (i+1) * 16384

                        sf_interval = [interval[0] + sf_index_start, interval[1] + sf_index_end]

                        classes = yamnet.predict_classes(waveform=clip[sf_index_start:sf_index_end], 
                                                        sr=16000,
                                                        num_top=5)

                        # json serializer is very picky, so all these seemingly pointless
                        # casts are required...
                        # audioset_classes.append(list(classes.astype(np.int16)))
                        audioset_classes.append(classes.tolist())
                        # because we're making a prediction based on a DOWNSAMPLED version of the 
                        # track, we need to convert our sample indicies back up to 44.1kHz
                        # for an accurate location
                        sf_interval = (np.array(sf_interval) / 16000) * 44100
                        corrected_intervals.append([int(sf_interval[0]), int(sf_interval[1])])
                        corrected_num_samps += int(sf_interval[1]) - int(sf_interval[0])
                
                track = os.path.splitext(os.path.basename(full_path))[0] # remove full path and ext .wav

                print(f'{track} - {corrected_num_samps} samples matching audioset classes')

                dir_map[session_name][track] = {}
                dir_map[session_name][track]["path"] = str(full_path)
                dir_map[session_name][track]["keywords"] = list(kw_filt.filter(track))
                dir_map[session_name][track]["numsamps"] = int(num_samps)
                dir_map[session_name][track]["intervals"] = list(corrected_intervals)
                dir_map[session_name][track]["audioset"] = audioset_classes

            analyzed += 1

            if analyzed % save_interval == save_interval - 1:
                print("save interval reached, saving map...")
                file_utils.save_json(outpath, dir_map, indent=2)

    return dir_map

            

if __name__ == "__main__":
  # generates a json containing sample indexes of verified classes for each track
  # see https://research.google.com/audioset/dataset/index.html for list of valid AudioSet labels
  # if a verified map already exists, the file will be updated with the new information added
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="./multitracks/", 
        help="path to downloaded mutlitracks")
    parser.add_argument("--out", type=str, default="./complete_map.json", 
        help="output path of verified map")
    parser.add_argument("--map", type=str, default=None, 
        help="path do existing dataset map which, if specified, will be modified in place")
    parser.add_argument("--overwrite", type=bool, default=True, 
        help="overwrite existing entries if existing dataset map is loaded")
    parser.add_argument("--save_interval", type=int, default=5, 
        help="how often to save the dataset map while processing tracks")
    parser.add_argument("-kw", type=str, default="keywords.txt",
        help="keywords txt file that specifies search terms")
    parser.add_argument("--c_thresh", type=int, default=80,
        help="confidence threshold for fuzzy string matching")
    parser.add_argument("--thresh_db", type=int, default=45, 
        help="threshold in db to reject silence")
    parser.add_argument("--n_jobs", type=int, default=8, 
        help="num parallel worker threads to load & process audio files")

    args = parser.parse_args()

    dataset_map = {} # initialzie empty dict
    if args.map is not None: # if existing map is provided, it will be modified in place (overwriting existing entries)
        dataset_map = file_utils.load_json(args.map)

    dataset_map = create_map(args.path, args.kw, args.c_thresh, args.thresh_db, args.n_jobs, dataset_map, 
                            args.out, args.overwrite, args.save_interval)

    file_utils.save_json(args.out, dataset_map, indent=2)