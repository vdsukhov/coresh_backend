#!/usr/bin/env python
import argparse
import subprocess
import os

GESECAR_PATH = "/nfs/home/geseca/geseca/geseca-r/"
OUT_PATH = "/mnt/tank/scratch/geseca/geseca-web/query"

SERVER_HOST = 'sphinx'
SERVER_USER = 'geseca'

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--query-path', type=str, required=True, help='Path to query')
    parser.add_argument('--organism', type=str, required=True, help='Type of organism for search')
    parser.add_argument('--sample-size', default=21, help='Sample size for adaptive multilevel splitting approach')
    parser.add_argument('--batch-size', default=100, help='The batch size for processing the experiments')
    args = parser.parse_args()
    return args.query_path, args.organism, args.sample_size, args.batch_size

def create_temp_dir():
    ssh_command = [
        'ssh', f'{SERVER_USER}@{SERVER_HOST}',
        'mktemp', '-d', f'--tmpdir={OUT_PATH}'
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
        return pout.strip()
    except Exception as e:
        print(f"Error in create_temp_dir: {e}")
        return None
    
def create_subfolders(dst):
    ssh_command = [
        'ssh', f'{SERVER_USER}@{SERVER_HOST}',
        f'cd {dst}; mkdir input; mkdir -p output/chunks/slurmLog'
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
        # TODO remove geseca user
        subprocess.call(['rsync', '-qP', f'{query_path}', f'geseca@sphinx:{dst}/input/query.json'])
    except Exception as e:
        print(f"Error occured during upload_query_json: {e}")

def run_slurm_job(fldr, batch_size, nbatches, sample_size):
    ssh_command = [
        'ssh', f'{SERVER_USER}@{SERVER_HOST}',
        f'cd {GESECAR_PATH}; sbatch --array=1-{nbatches} --output={fldr}/output/chunks/slurmLog/arrayJob_%A_%a.out slurm_runner.sh '
        f'{fldr}/input/query.json {batch_size} {sample_size} {fldr}/output/chunks'
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
        print(f'Error in run_slurm_job: {e}')
        return False



if __name__ == "__main__":
    query_path, org, sample_size, batch_size = parse_arguments()
    try:
        folder_name = create_temp_dir()
        assert folder_name is not None, "Folder was not created properly"
        # print(folder_name)
        assert create_subfolders(f'{folder_name}'), 'Subfolders were not created properly'

        with open(f'./coresh_backend/ext/data/{org}_file_count.txt') as inp_f:
            nfiles = int(inp_f.readline().strip())
        nbatches = nfiles // batch_size + 1

        upload_query_json(query_path, folder_name)
        run_slurm_job(folder_name, batch_size, nbatches, sample_size)

        print(f"ID: {os.path.basename(folder_name)}")


        


    
    except Exception as e:
        print(f'Error: {e}')
