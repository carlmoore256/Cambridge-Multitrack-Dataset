# Utility for downloading all cambridge MT mix stems
# Crawls website and downloads multitrack zip files
# https://www.cambridge-mt.com/ms/mtk/

import requests 
import json
# import re
from bs4 import BeautifulSoup
import os
import zipfile
from tqdm import tqdm
import threading

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


# downloads a single zip
def download(url, save_path, chunk_size=128):
    # filesize = requests.head(url)
    r = requests.get(url, stream=True)
    filesize = int(r.headers['Content-Length'])
    pbar = tqdm(total=filesize)

    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
            pbar.update(chunk_size)

    pbar.close()


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
        out_path = f"{save_path}{filename}"

        # avoid re-downloading ones already downloaded previously
        if os.path.exists(out_path):
            print(f'path {out_path} already exists, skipping...')
        else:
            os.mkdir(out_path)

            temp_file = f'./temp/temp_{filename}.zip'
            
            print(f'downloading {filename}, multitrack {i}/{len(links)}')
            
            # download(l, temp_file)

            w = threading.Thread(target=unzip_async, args=(temp_file, out_path))
            unzip_workers.append(w)
            w.start()

            # out_path = f"'{save_path}{folder_name}'"
            # !unzip -q $temp_file -d $out_path

            # !rm $temp_file
            i += 1

    for w in unzip_workers:
        print("waiting for worker threads to finish unzip")
        w.join()


if __name__ == "__main__":

    save_path = "./multitracks/"

    genres=['Pop', 'Electronica', 'Acoustic', 'HipHop']

    page = parse_page('https://www.cambridge-mt.com/ms/mtk/')

    links = get_dl_links(page, genres)

    download_all_files(links, save_path)