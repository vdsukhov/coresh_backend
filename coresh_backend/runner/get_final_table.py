#!/usr/bin/env python
import argparse
import subprocess

GESECAR_PATH = "/nfs/home/geseca/geseca/geseca-r/"
OUT_PATH = "/mnt/tank/scratch/geseca/geseca-web/query"

SERVER_HOST = 'sphinx'
SERVER_USER = 'geseca'


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--server-path-suffix', type=str, required=True, help='server path suffix')
    parser.add_argument('--out-json-path', type=str, required=True, help='Output JSON path')
    args = parser.parse_args()
    return args.server_path_suffix, args.out_json_path


if __name__ == "__main__":
    server_path_suffix, out_json_path = parse_arguments()
    print(f"SERVER_PATH_SUFFIX: {server_path_suffix}")
    print(f"OUT_JSON_PATH: {out_json_path}")

    COMMAND = f'source ~/.profile; cd {GESECAR_PATH}; Rscript GetFinalTable.R {server_path_suffix}'

    ssh_command = [
        "ssh",
        f"{SERVER_USER}@{SERVER_HOST}",
        f"{COMMAND}"
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

    try:
        subprocess.call(['rsync', '-qP', f'{SERVER_USER}@{SERVER_HOST}:{OUT_PATH}/{server_path_suffix}/output/finalTable/result.json', f'{out_json_path}'])
    except Exception as e:
        print(f"Error occured during rsync: {e}")

    
