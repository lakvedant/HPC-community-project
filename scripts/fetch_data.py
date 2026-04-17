#!/usr/bin/env python3
import urllib.request
import gzip
import shutil
import os

DATASETS = {
    "facebook": "https://snap.stanford.edu/data/facebook_combined.txt.gz",
    "twitter": "https://snap.stanford.edu/data/twitter_combined.txt.gz",
    "email": "https://snap.stanford.edu/data/email-EuAll.txt.gz"
}

def download_and_extract(dataset_key):
    if dataset_key not in DATASETS:
        print(f"Unknown dataset: {dataset_key}")
        return

    url = DATASETS[dataset_key]
    gz_file = f"{dataset_key}.txt.gz"
    txt_file = f"{dataset_key}.txt"

    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, gz_file)
    except Exception as e:
        print(f"Failed to download: {e}")
        return

    print(f"Extracting to {txt_file}...")
    try:
        with gzip.open(gz_file, 'rb') as f_in:
            with open(txt_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(gz_file)
        print("Done!")
    except Exception as e:
        print(f"Failed to extract: {e}")

if __name__ == "__main__":
    import sys
    dataset = sys.argv[1] if len(sys.argv) > 1 else "facebook"
    download_and_extract(dataset)
