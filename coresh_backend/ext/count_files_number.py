#!/usr/bin/env python
import subprocess
import os

# FILES_PATH = "/mnt/geseca/geseca_pca_datasets"

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_USER = os.getenv("SERVER_USER")
CORESH_R_PATH = os.getenv("CORESH_R_PATH")

print(SERVER_USER, SERVER_HOST, CORESH_R_PATH)

if __name__ == "__main__":

    ssh_command = [
        "ssh",
        f"{SERVER_USER}@{SERVER_HOST}",
        f"cd {CORESH_R_PATH} && bash ./methods/number_of_files.sh"
    ]

    try:
        # Execute the SSH command
        process = subprocess.Popen(
            ssh_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        stdout, stderr = process.communicate()
        
        # Check if the R script ran successfully
        assert process.returncode == 0, f'{stderr}'
        
    except Exception as e:
        print(f"Error occurred while running R script: {e}")
