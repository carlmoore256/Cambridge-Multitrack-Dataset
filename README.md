# Cambridge-Multitrack-Dataset
Tools for downloading, sorting and analyzing the [Cambridge Multitracks library](https://www.cambridge-mt.com/ms/mtk/) for machine learning applications. [Example](https://github.com/carlmoore256/NextBlock)

## Installation
- Clone this repo
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

- This process will take a long time, since we are retrieving several hundred GB of waveform audio files
- Folder checks are implemented to avoid re-downloading parts of your local library
- Individual genres can be specified
#### genres = ['Pop', 'Electronica', 'Acoustic', 'HipHop']

Zip files are saved in a temp directory ("./temp") where they stay until they are unzipped. Unzipping is done asychronously alongside other downloads, so be careful when terminating this process early, as worker threads may still be actively unzipping.