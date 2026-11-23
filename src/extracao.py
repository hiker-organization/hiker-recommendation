import pandas as pd
import config
import psycopg
from psycopg import sql

"""Deve ser alterado futuramente para extrair da GCP"""
def _ler_tabela(conn, nome):
    query = sql.SQL("SELECT * FROM {} ORDER BY id").format(sql.Identifier(nome))
    with conn.cursor() as cur:
        cur.execute(query)
        colunas = [c.name for c in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=colunas)    


def extrair():
    """Retorna as tabelas brutas como DataFrames."""
    if config.DADOS_LOCAIS:
        pasta = config.DADOS_LOCAIS
        return {
            "Voto_review": pd.read_csv(f"{pasta}/interacoes.csv"),
            "Review": pd.read_csv(f"{pasta}/Review_rows.csv"),
            "Tag": pd.read_csv(f"{pasta}/Tag_rows.csv"),
            "Tag_review": pd.read_csv(f"{pasta}/Tag_review_rows.csv"),
        }

    with psycopg.connect(config.DATABASE_URL) as conn:
        return {
            "Voto_review": _ler_tabela(conn, config.TABELA_INTERACOES),
            "Review": _ler_tabela(conn, config.TABELA_POSTS),
            "Tag": _ler_tabela(conn, config.TABELA_TAGS),
            "Tag_review": _ler_tabela(conn, config.TABELA_TAG_POST),
        }
