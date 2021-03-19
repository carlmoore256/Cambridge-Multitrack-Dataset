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
                        print(f"full download not found, skipping")
                else:
                    continue
    return links

# worker for unzipping files
# def unzip_async(zipfile):


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
    
    for l in links[:]:
        filename = os.path.basename(l)
        filename, _ = os.path.splitext(filename)
        print(filename)

        # avoid re-downloading ones already downloaded previously
        if os.path.exists(save_path + filename):
            print(f'path {save_path + filename} already exists, skipping...')
        else:
            temp_file = f'./temp/temp_{filename}.zip'
            
            print(f'downloading {l}')
            download(l, temp_file)

            folder_name = filename
            # print(f"extracting to {save_path}{folder_name}")

            # out_path = f"'{save_path}{folder_name}'"
            # !unzip -q $temp_file -d $out_path

            # !rm $temp_file


if __name__ == "__main__":

    save_path = "./multitracks/"

    genres=['Pop', 'Electronica', 'Acoustic', 'HipHop']

    page = parse_page('https://www.cambridge-mt.com/ms/mtk/')

    links = get_dl_links(page, genres)

    download_all_files(links, save_path)