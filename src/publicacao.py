import os
import pandas as pd
import config


def _lotes(lista, tamanho):
    for i in range(0, len(lista), tamanho):
        yield lista[i:i + tamanho]


def publicar(recs, versao, gerado_em):
    """
    Grava as recomendações para o app.
    - DESTINO=csv: salva em artefatos/recomendacoes.csv (teste local).
    - DESTINO=supabase: faz upsert na tabela e remove linhas de execuções anteriores.
    """
    recs = recs.copy()
    recs["modelo_versao"] = versao
    recs["gerado_em"] = gerado_em

    if config.DESTINO == "csv":
        os.makedirs(config.PASTA_ARTEFATOS, exist_ok=True)
        caminho = os.path.join(config.PASTA_ARTEFATOS, "recomendacoes.csv")
        recs.to_csv(caminho, index=False)
        return caminho

    from supabase import create_client
    client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
    tabela = client.table(config.TABELA_RECOMENDACOES)

    registros = recs[["user_id", "post_id", "rank", "modelo_versao", "gerado_em"]].to_dict("records")
    for lote in _lotes(registros, 500):
        tabela.upsert(lote, on_conflict="user_id,post_id").execute()

    # Remove recomendações de execuções anteriores, para não sobrar lixo no banco
    tabela.delete().lt("gerado_em", gerado_em).execute()
    return config.TABELA_RECOMENDACOES
