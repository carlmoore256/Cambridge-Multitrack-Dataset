# Utility for downloading all cambridge MT mix stems
# Crawls website and downloads multitrack zip files
# https://www.cambridge-mt.com/ms/mtk/

import requests 
import json
from bs4 import BeautifulSoup
import os
import zipfile
# from tqdm import tqdm
import threading
import argparse
import utils

# return beautiful soup parsed html page
def parse_page(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')

# finds download links from beautifulSoup page content
def get_dl_links(page, genres):
    links = []
    for sect in page.find_all('div', class_='c-mtk'):
        genre_sect = sect.find_all('div', class_='c-mtk__genre')
        for g in genre_sect:
            genre = g.find('h3')['id']
            if genre in genres:
                print(f'finding links for genre: {genre}')
                dl_content = g.find_all('div', class_='m-mtk-download__content')
                for d in dl_content:
                    try:
                        dl_type = d.find('div', 'm-mtk-download__type').text
                        if "Full" in dl_type:
                            link = d.find('a')['href']
                            links.append(link)
                            print(f"found {link}")
                    except:
                        continue
    return links

# worker for unzipping files
def unzip_async(zip_path, out_path):
    print(f"unzipping {zip_path} to {out_path}")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(out_path)
    print(f"sucessfully unzipped {zip_path}, deleting zip")
    os.remove(zip_path)

# downloads a single file
# def download(url, save_path, chunk_size=128):
#     # filesize = requests.head(url)
#     r = requests.get(url, stream=True)
#     filesize = int(r.headers['Content-Length'])
#     pbar = tqdm(total=filesize)
#     with open(save_path, 'wb') as fd:
#         for chunk in r.iter_content(chunk_size=chunk_size):
#             fd.write(chunk)
#             pbar.update(chunk_size)
#     pbar.close()

# downloads and unzips files from links
def download_all_files(links, save_path):
    # makes a temporary path for downloading the zip files
    if not os.path.exists("./temp"):
        os.mkdir("./temp")
    unzip_workers = [] # keep track of worker threads
    i = 0

    for l in links[:]:
        filename = os.path.basename(l)
        filename, _ = os.path.splitext(filename)

        # files often marked as _Full at the end, remove this
        if filename.endswith("_Full"):
            filename = filename[:-5]

        out_path = f"{save_path}{filename}"

        # avoid re-downloading ones already downloaded previously
        if os.path.exists(out_path):
            print(f'path {out_path} already exists, skipping...')
        else:
            os.mkdir(out_path)
            temp_file = f'./temp/temp_{filename}.zip'
            print(f'downloading {filename}, zip # {i}/{len(links)}')
            utils.download(l, temp_file)
            w = threading.Thread(target=unzip_async, args=(temp_file, out_path))
            unzip_workers.append(w)
            w.start()
            i += 1

    for w in unzip_workers:
        print("waiting for worker threads to finish unzip")
        w.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=str, default="./multitracks/", 
        help="path where downloaded mutlitracks will be saved")
    parser.add_argument("--genre", type=str, 
        help="only download a specific genere, pick one (case sensitive) 'Pop', 'Electronica', 'Acoustic', 'HipHop'")
    parser.add_argument("--mt_url", type=str, default='https://www.cambridge-mt.com/ms/mtk/',
        help="url for the cambridge mt library")
    parser.add_argument("--subset", type=int, default=0, 
        help="take a small subset of all mutlitracks given number of examples")
    args = parser.parse_args()

    if args.genre is None:
        genres = ['Pop', 'Electronica', 'Acoustic', 'HipHop']
    else:
        genres = [args.genre]

    page = parse_page(args.mt_url)
    links = get_dl_links(page, genres)

    # option to load in a randomly sampled subset
    if args.subset > 0:
        import random
        random.shuffle(links)
        links = links[:args.subset]

    download_all_files(links, args.path)