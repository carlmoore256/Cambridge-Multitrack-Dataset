# simple tool for displaying the directory structure
# shows hierarchy of downloaded stems
import argparse
import os

def display_dataset_structure(path):
    # traverse root directory, and list directories as dirs and files as files
    for root, dirs, files in os.walk(path):
        c_path = root.split(os.sep)
        print((len(c_path) - 1) * '---', os.path.basename(root))
        for file in files:
            print(len(c_path) * '---', file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-path", type=str, default="./multitracks/", 
        help="path to the local MT library")
    args = parser.parse_args()

    display_dataset_structure(args.path)
