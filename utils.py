import requests
from tqdm import tqdm

# downloads a single file
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