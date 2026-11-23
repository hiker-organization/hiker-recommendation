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

    import psycopg
    from psycopg import sql

    registros = recs[["user_id", "post_id", "rank", "modelo_versao", "gerado_em"]].itertuples(index=False, name=None)
    tabela = sql.Identifier(config.TABELA_RECOMENDACOES)

    with psycopg.connect(config.DATABASE_URL) as conn, conn.cursor() as cur:
        cur.executemany(sql.SQL("""
            INSERT INTO {} (user_id, post_id, rank, modelo_versao, gerado_em)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (user_id, post_id) DO UPDATE
            SET rank = EXCLUDED.rank, modelo_versao = EXCLUDED.modelo_versao, gerado_em = EXCLUDED.gerado_em
        """).format(tabela), list(registros))
        # Remove recomendações de execuções anteriores, para não sobrar lixo no banco
        cur.execute(sql.SQL("DELETE FROM {} WHERE gerado_em < %s").format(tabela), (gerado_em,))

    return config.TABELA_RECOMENDACOES
