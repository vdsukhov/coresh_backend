#!/usr/bin/env python
import argparse
import subprocess
import csv

OUT_PATH = "/mnt/tank/scratch/geseca/geseca-web/query"

SERVER_HOST = 'sphinx'
SERVER_USER = 'geseca'

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-path-suffix', type=str, required=True, help='server path suffix')
    parser.add_argument('--org', type=str, required=True, help='organism (hsa|mmu)')
    parser.add_argument('--batch-size', type=int, default=100, help='size of the batch')
    args = parser.parse_args()
    return args.server_path_suffix, args.org, args.batch_size

if __name__ == "__main__":
    server_path_suffix, org, batch_size = parse_arguments()

    with open(f'./coresh_backend/ext/data/{org}_file_count.txt') as inp_f:
        nfiles = int(inp_f.readline().strip())
    
    nbatches = nfiles // batch_size + 1

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
        
        ncompleted = int(pout.strip()) - 1
        ncompleted = max(0, ncompleted)
    
    except Exception as e:
        print(f"Error occured: {e}")

    print(f'nbatches: {nbatches}')
    print(f'ncompleted: {ncompleted}')
    progress = min(100 , 100 * ncompleted / nbatches)
    print(f'progress: {progress}')

    
