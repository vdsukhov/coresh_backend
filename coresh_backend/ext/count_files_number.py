#!/usr/bin/env python
import subprocess

FILES_PATH = "/mnt/geseca/geseca_pca_datasets"

SERVER_HOST = 'sphinx'
SERVER_USER = 'geseca'

if __name__ == "__main__":

    values = {}

    for org in ('hsa', 'mmu'):
        ssh_command = [
            'ssh',
            f'{SERVER_USER}@{SERVER_HOST}',
            f'ls {FILES_PATH}/{org} | wc -l'
        ]

        try:
            p = subprocess.Popen(
                ssh_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            pout, perr = p.communicate()
            assert p.returncode == 0, f"Error during subprocess: {perr}"
            
            values[org] = pout.strip()


        except Exception as e:
            print(f"Error occured:\n{e}")
        
        with open(f'./ext/data/{org}_file_count.txt', 'w') as out_f:
            out_f.write(f'{values[org]}\n')

    
