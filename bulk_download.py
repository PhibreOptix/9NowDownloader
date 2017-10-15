#! /usr/bin/python3

import pandas as pd
import os

def main():
    print("Starting up the bulk import of video downloads")
    df = pd.read_csv("input_bulk.csv")
    for row in df.itertuples():
        if row.HasSubs == "Yes":
            download_cmd = 'download_9now_video.py "{0}" "{1}" "{2}"'.format(
                            row.Name,
                            row.VideoURL,
                            row.SubURL
                            )
        else:
            download_cmd = 'download_9now_video.py "{0}" "{1}"'.format(
                            row.Name,
                            row.VideoURL
                            )
        
        os.system(download_cmd)

if __name__ == "__main__":
    main()

