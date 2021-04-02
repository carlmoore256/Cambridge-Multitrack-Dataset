# main utility for mapping keywords, features, and AudioSet classes to multitracks

import json
import yamnet_classifier
import argparse
import extract_labels



if __name__ == "__main__":
  # generates a json containing sample indexes of verified classes for each track
  # see https://research.google.com/audioset/dataset/index.html for list of valid AudioSet labels
  # if a verified map already exists, the file will be updated with the new information added
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="./multitracks/", 
        help="path to downloaded mutlitracks")
    parser.add_argument("--out", type=str, default="./full_map.json", 
        help="output path of verified map")
    parser.add_argument("-kw", type=str, default="keywords.txt",
        help="keywords txt file that specifies search terms")
    parser.add_argument("--c_thresh", type=int, default=80,
        help="confidence threshold for fuzzy string matching")
    parser.add_argument("--thresh", type=int, default=45, 
        help="threshold in db to reject silence")

    args = parser.parse_args()

    kw_filter = extract_labels.FilterStems(file_utils.load_keywords(args.kw), 
                                            args.c_thresh)

    kw_map = extract_labels.create_label_map(args.path, kw_filter)