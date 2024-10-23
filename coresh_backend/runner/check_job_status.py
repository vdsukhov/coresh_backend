#!/usr/bin/env python
import argparse
import subprocess
import os
import math
import json

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_USER = os.getenv("SERVER_USER")
CORESH_R_PATH = os.getenv("CORESH_R_PATH")
OUT_PATH = os.getenv("CORESH_QUERIES")


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-path-suffix', type=str, required=True, help='server path suffix')
    parser.add_argument('--org', type=str, required=True, help='organism (hsa|mmu)')
    parser.add_argument('--batch-size', type=int, default=500, help='size of the batch')
    args = parser.parse_args()
    return args.server_path_suffix, args.org, args.batch_size

if __name__ == "__main__":
    server_path_suffix, org, batch_size = parse_arguments()

    with open('./coresh_backend/ext/data/number_of_files.json') as inp_f:
        data = json.load(inp_f)
        nfiles = int(data[org])
    nbatches = math.ceil(nfiles / batch_size)

    ssh_command = [
        'ssh',
        f'{SERVER_USER}@{SERVER_HOST}',
        f'cd {OUT_PATH}/{server_path_suffix}/output/chunks; ls | wc -l'
    ]

    try:
        p = subprocess.Popen(
            ssh_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        pout, perr = p.communicate()
        assert p.returncode == 0, f'{perr}'
        
        ncompleted = int(pout.strip())
        ncompleted = max(0, ncompleted)
    
    except Exception as e:
        print(f"Error occured: {e}")

    print(f'nbatches: {nbatches}')
    print(f'ncompleted: {ncompleted}')
    progress = min(100 , 100 * ncompleted / nbatches)
    print(f'progress: {progress}')

    
