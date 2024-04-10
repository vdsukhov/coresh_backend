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


def get_final_table(request):
    jobid = request.GET.get('jobid')

    tmp_f_path = None
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_f:
        tmp_f_path = tmp_f.name
        print(tmp_f_path)
    
    try:
        p = subprocess.Popen(
            ['python', './coresh_backend/runner/get_final_table.py',
             '--server-path-suffix', jobid,
             '--out-json-path', tmp_f_path
             ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

        pout, perr = p.communicate()
        assert p.returncode == 0, perr
        

        with open(tmp_f_path) as inp_f:
            res = json.load(inp_f)
        return JsonResponse(res, safe=False)
    except Exception as e:
        print(f'Error occured during the get_final_table: {e}')

    

    return JsonResponse({'error': 'Get (get-final-table) request failed'}, status=405)
