import re
from gprofiler import GProfiler

gp = GProfiler(return_dataframe=True)


def genes2entrez(genes, org):
    """
    Convert gene identifiers to Entrez Gene IDs using the Gene Prioritization (GP) module.

    Args:
    - genes (list): A list of gene symbols or IDs to be converted.
    - org (str): The organism for which the conversion is performed, specified as a string ('hsapiens' for human, 'mmusculus' for mouse).

    Returns:
    pandas.DataFrame: A DataFrame containing the converted Entrez Gene IDs.
    """
    conv_df = gp.convert(organism=org, query=genes, target_namespace='ENTREZGENE_ACC', numeric_namespace='ENTREZGENE_ACC')
    return conv_df

def genes2symbol(genes, org):
    """
    Convert gene identifiers to Gene Symbols using the Gene Prioritization (GP) module.

    Args:
    - genes (list): A list of gene symbols or IDs to be converted.
    - org (str): The organism for which the conversion is performed, specified as a string ('hsapiens' for human, 'mmusculus' for mouse).

    Returns:
    pandas.DataFrame: A DataFrame containing the converted Gene Symbols.
    """
    conv_df = gp.convert(organism=org, query=genes, target_namespace='ENTREZGENE', numeric_namespace='ENTREZGENE_ACC')
    return conv_df


def get_orth_genes(genes, from_org, to_org):
    """
    Retrieve orthologous genes from one organism to another.

    Args:
    - genes (list): List of gene symbols.
    - from_org (str): Abbreviation of the organism containing the input genes (e.g., 'hsapiens' for human, 'mmusculus' for mouse).
    - to_org (str): Abbreviation of the target organism to find orthologs in.

    Returns:
    pandas.DataFrame: DataFrame containing orthologous gene mappings between the two organisms.
    """
    orth_df = gp.orth(
        organism=from_org,
        target=to_org,
        query=genes,
        numeric_namespace="ENTREZGENE_ACC"
    )
    return orth_df

