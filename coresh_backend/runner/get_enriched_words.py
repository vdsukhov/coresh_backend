#!/usr/bin/env python
import argparse
import subprocess
import os


SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_USER = os.getenv("SERVER_USER")
CORESH_R_PATH = os.getenv("CORESH_R_PATH")
OUT_PATH = os.getenv("CORESH_QUERIES")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-path-suffix', type=str, required=True, help='server path suffix')
    parser.add_argument('--words-path', type=str, required=True, 
                    help='Path to a temporary file for storing the result of enriched words analysis')
    args = parser.parse_args()
    return args.server_path_suffix, args.out_json_path


if __name__ == "__main__":
    server_path_suffix, words_path = parse_arguments()
    print(f"SERVER_PATH_SUFFIX: {server_path_suffix}")
    print(f"OUT_WORDS_PATH: {words_path}")
    
    try:
        subprocess.call([
            'rsync', '-qP', 
            f'{SERVER_USER}@{SERVER_HOST}:{OUT_PATH}/{server_path_suffix}/output/finalTable/words_enrichment.json', 
            f'{words_path}'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error occured during rsync: {e}")

    
