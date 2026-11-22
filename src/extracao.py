import pandas as pd
import config

"""Deve ser alterado futuramente para extrair da GCP"""
def _ler_tabela_supabase(client, nome, pagina=1000):
    """Lê a tabela inteira em páginas, porque o Supabase limita o número de linhas por consulta.
        Cliente é o objeto que representa a conexão com o supabase"""
    linhas, inicio = [], 0
    while True:
        r = (client.table(nome).select("*").order("id")
             .range(inicio, inicio + pagina - 1).execute())
        dados = r.data or []
        linhas.extend(dados)
        if len(dados) < pagina:
            break
        inicio += pagina
    return pd.DataFrame(linhas)


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

    from supabase import create_client
    client = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)
    return {
        "Voto_review": _ler_tabela_supabase(client, config.TABELA_INTERACOES),
        "Review": _ler_tabela_supabase(client, config.TABELA_POSTS),
        "Tag": _ler_tabela_supabase(client, config.TABELA_TAGS),
        "Tag_review": _ler_tabela_supabase(client, config.TABELA_TAG_POST),
    }
