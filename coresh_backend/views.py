import subprocess
import json
import tempfile
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from coresh_backend.utils.gene_converter import genes2entrez, get_orth_genes, genes2symbol


GPROF_ORGS = {
    'hsa': 'hsapiens',
    'mmu': 'mmusculus'
}

SERVER_HOST = os.getenv("SERVER_HOST")
SERVER_USER = os.getenv("SERVER_USER")
CORESH_R_PATH = os.getenv("CORESH_R_PATH")
OUT_PATH = os.getenv("CORESH_QUERIES")

@csrf_exempt
def submit_genes(request):
    if request.method == "POST":
        req_data = json.loads(request.body.decode())

        org = req_data['organism']
        db_type = req_data['dbType']
        genes = req_data['genes']
        print(f'org: {org}\ndb_type: {db_type}\ngenes: {genes}')

        if (org != db_type):
            orth_res = get_orth_genes(genes, GPROF_ORGS[org], GPROF_ORGS[db_type])
            conv_gene_symbols = orth_res['name'].dropna().to_list()
            entrez_genes = genes2entrez(conv_gene_symbols, GPROF_ORGS[db_type])['converted'].dropna().to_list()
            pass
        else:
            if False in [elem.isdigit() for elem in genes]:
                conv_df = genes2entrez(genes, GPROF_ORGS[org])
                entrez_genes = conv_df['converted'].dropna().to_list()
            else:
                entrez_genes = genes
                print('entrez_genes:', entrez_genes)




        unified_request = {
            'organism': db_type,
            'genes': entrez_genes
        }

        # unified_request = None

        # I want to wrap next part into function

        tmp_f_path = None
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_f:
            print(tmp_f.name)
            print(unified_request)
            json.dump(unified_request, tmp_f)
            tmp_f_path = tmp_f.name

        try:
            p = subprocess.Popen(
                ['python', './coresh_backend/runner/submit_task.py',
                 '--query-path', tmp_f_path,
                 '--organism', unified_request['organism']],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            pout, perr = p.communicate()
            print(f'pout: {pout}')

            jobid = pout.strip().split(sep=": ")

        except Exception as e:
            print(f'Error occured during subprocess: {e}')
            return JsonResponse({'error': 'Post request failed'}, status=405)

        try:
            os.remove(tmp_f_path)
        except Exception as e:
            pass

        return JsonResponse({jobid[0]: jobid[1]})

    else:
        return JsonResponse({'error': 'Post request failed'}, status=405)


def check_job_status(request):
    jobid = request.GET.get('jobid')
    org = request.GET.get('organism')

    try:
        p = subprocess.Popen(
            ['python', './coresh_backend/runner/check_job_status.py',
             '--server-path-suffix', jobid,
             '--org', org],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        pout, perr = p.communicate()

        response = pout.strip().splitlines()
        response = [elem.split(': ') for elem in response]
        response = {elem[0]: elem[1] for elem in response}

        assert p.returncode == 0, "Error occured during check job status"
    except Exception as e:
        print(f'Error occured during subprocess: {e}')
        return JsonResponse({'error': 'Get (check-job-status) request failed'}, status=405)

    return JsonResponse(response)


def create_final_tables(request):
    jobid = request.GET.get('jobid')
    
    try:
        p = subprocess.Popen(
            ['python', './coresh_backend/runner/create_final_tables.py',
             '--server-path-suffix', jobid],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        pout, perr = p.communicate()
                # Check for successful execution
        if p.returncode == 0:
            # Success: Return the stdout as part of the JSON response
            return JsonResponse({'status': 'success', 'output': pout}, safe=False)
        else:
            # Failure: Return the stderr as part of the error response
            return JsonResponse({'status': 'error', 'error': perr}, status=500)
    except Exception as e:
        # Catch any other exceptions and return an error response
        print(f'Error occured during the create_final_tables: {e}')
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    




def get_enriched_words(request):
    jobid = request.GET.get('jobid')

    tmp_f_path = None
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_f:
        tmp_f_path = tmp_f.name
        print(tmp_f_path)
    
    try:
        subprocess.call([
            'rsync', '-qP', 
            f'{SERVER_USER}@{SERVER_HOST}:{OUT_PATH}/{jobid}/output/finalTable/words_enrichment.json', 
            f'{tmp_f_path}'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with open(tmp_f_path) as inp_f:
            res = json.load(inp_f)
        return JsonResponse(res, safe=False)
    except Exception as e:
        print(f'Error occured during the get_enriched_words: {e}')
        return JsonResponse({'error': 'Get (get-enriched-words) request failed'}, status=405)
    finally:
        if tmp_f_path and os.path.exists(tmp_f_path):
            os.remove(tmp_f_path)



def get_ranking_result(request):
    jobid = request.GET.get('jobid')

    tmp_f_path = None
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_f:
        tmp_f_path = tmp_f.name
        print(tmp_f_path)
    try:
        subprocess.call([
            'rsync', '-qP', 
            f'{SERVER_USER}@{SERVER_HOST}:{OUT_PATH}/{jobid}/output/finalTable/result.json', 
            f'{tmp_f_path}'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        with open(tmp_f_path) as inp_f:
            res = json.load(inp_f)
        return JsonResponse(res, safe=False)
    except Exception as e:
        print(f'Error occured during the get_enriched_words: {e}')
        return JsonResponse({'error': 'Get (get-ranking-result) request failed'}, status=405)
    finally:
        if tmp_f_path and os.path.exists(tmp_f_path):
            os.remove(tmp_f_path)


def check_result_files(request):
    jobid = request.GET.get('jobid')
    
    ssh_command = [
        'ssh', f'{SERVER_USER}@{SERVER_HOST}',
        f'ls {OUT_PATH}/{jobid}/output/finalTable'        
    ]
    
    try:
        p = subprocess.Popen(
            ssh_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        pout, perr = p.communicate()
        
        if p.returncode == 0:
            files = pout.strip().splitlines()
            files_ready = "result.json" in files and "words_enrichment.json" in files
            return JsonResponse({'files_ready': files_ready})
    except Exception as e:
        return JsonResponse({'error': 'Get (check_result_files) request failed'}, status=405)
