#!/usr/bin/env python
import argparse
import subprocess
import os
import json
import math

import random
import time
import string


def generate_random_folder_name():
    # Get current timestamp
    timestamp = time.strftime("%Y%m%d")
    
    # Generate a random string of letters and digits
    random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    # Combine timestamp with the random part to create a unique folder name
    folder_name = f"{timestamp}_{random_part}"
    
    return folder_name


SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_USER = os.getenv("SERVER_USER")
CORESH_R_PATH = os.getenv("CORESH_R_PATH")
OUT_PATH = os.getenv("CORESH_QUERIES")





def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query-path', type=str, required=True, help='Path to query')
    parser.add_argument('--organism', type=str, required=True, help='Type of organism for search')
    parser.add_argument('--sample-size', default=21, help='Sample size for adaptive multilevel splitting approach')
    parser.add_argument('--batch-size', default=500, help='The batch size for processing the experiments')
    args = parser.parse_args()
    return args.query_path, args.organism, args.sample_size, args.batch_size

def create_temp_dir():

    rand_name = generate_random_folder_name()
    ssh_command = [
        'ssh', f'{SERVER_USER}@{SERVER_HOST}',
        'mkdir', '-p', f'{OUT_PATH}/{rand_name}'
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
        return f'{OUT_PATH}/{rand_name}'
    except Exception as e:
        print(f"Error in create_temp_dir: {e}")
        return None
    
def create_subfolders(dst):
    ssh_command = [
        'ssh', f'{SERVER_USER}@{SERVER_HOST}',
        f'cd {dst}; mkdir input; mkdir -p output/chunks/; mkdir -p output/finalTable/; mkdir -p output/log/'
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

        return True
    except Exception as e:
        print(f'Error in create_subfolders: {e}')
        return False

def upload_query_json(query_path, dst):
    
    try:
        create_subfolders(dst)
        subprocess.call(['rsync', '-qP', f'{query_path}', f'{SERVER_USER}@{SERVER_HOST}:{dst}/input/query.json'])
    except Exception as e:
        print(f"Error occured during upload_query_json: {e}")

        
def submit_job(fldr, batch_size, nbatches, sample_size):
    ssh_command = [
        'ssh', f'{SERVER_USER}@{SERVER_HOST}',
        f'source ~/.bash_profile; cd {CORESH_R_PATH}; bash submit_job.sh {fldr} {sample_size} {batch_size} {nbatches}'
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
    except Exception as e:
        print(f"Error in submit_job: {e}")
    


if __name__ == "__main__":
    query_path, org, sample_size, batch_size = parse_arguments()
    try:
        folder_name = create_temp_dir()
        assert folder_name is not None, "Folder was not created properly"

        with open('./coresh_backend/ext/data/number_of_files.json') as inp_f:
            data = json.load(inp_f)
            nfiles = int(data[org])
        nbatches = math.ceil(nfiles / batch_size)
        upload_query_json(query_path, folder_name)
        submit_job(folder_name, batch_size, nbatches, sample_size)

        print(f"ID: {os.path.basename(folder_name)}")
    except Exception as e:
        print(f'Error: {e}')