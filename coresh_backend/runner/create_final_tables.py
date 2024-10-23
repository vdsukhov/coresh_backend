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
    args = parser.parse_args()
    return args.server_path_suffix


if __name__ == "__main__":
    server_path_suffix= parse_arguments()
    print(f"SERVER_PATH_SUFFIX: {server_path_suffix}")

    
    ssh_command = [
        'ssh', f'{SERVER_USER}@{SERVER_HOST}',
        f'source ~/.bash_profile; cd {CORESH_R_PATH}; bash form_final_tables.sh {OUT_PATH}/{server_path_suffix}'
    ]

    try:
        process = subprocess.Popen(
            ssh_command, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        output, error = process.communicate()

        if process.returncode != 0:
            print(f"Error: {error}")
    except Exception as e:
        print(f"An error occured: {e}")
