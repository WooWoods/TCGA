from libs import search_retrieval


if __name__ == '__main__':
    # Clinical test
    Query = search_retrieval.ParamConstructor('TCGA-BRCA','Clinical')
    # project test
    #Query = search_retrieval.ParamConstructor('TCGA-BRCA','Transcriptome Profiling','Gene Expression Quantification', workflow_type='HTSeq - FPKM')
    Query.form_response()
    print(Query.result)
    search_retrieval.download(Query)
