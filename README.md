# Cambridge-Multitrack-Dataset
Tools for downloading, sorting and analyzing the [Cambridge Multitracks library](https://www.cambridge-mt.com/ms/mtk/) for machine learning applications. [Example](https://github.com/carlmoore256/NextBlock)

## Installation
```bash
git clone https://github.com/carlmoore256/Cambridge-Multitrack-Dataset
```

- Install Dependencies
```bash
pip install -r requirements.txt
```

## Getting Started
### Build a local library using the download utility
- Download all available multitrack stems and unzip them into provided directory (default is "./multitracks")
```bash
python download_stems.py
```
#### This will take a long time, since we are retrieving several hundred GBs of WAV files

- (Optional) Download only a single genre using the --genre argument
```bash
python download_stems.py --genre Pop
```
#### Available genre filters: Pop, Electronica, Acoustic, HipHop

This may not seem like an exhaustive list, but this is actually just the html tags. Browse [the website](https://www.cambridge-mt.com/ms/mtk/) for a better idea about what's included in each of these.

* Folder checks avoid re-downloading parts of your local library
* Zip files are stored in "./temp" until they are unzipped

### Download a smaller subset
- Download n examples from a randomly selected pool, instead of downloading the entire library
```bash
python download_stems.py --subset 10
```

## Dataset Label Mapping
Labels for stems are generated by matching a list of search parameters to filenames. 
extract_labels.py saves a json map of files and associated labels.

### Create a custom mapping
- Modify or create keywords.txt to specify custom search parameters
```bash
python extract_labels.py -kw /path/to/keywords.txt
```



