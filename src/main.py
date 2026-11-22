"""Executa o pipeline completo: extração, transformação, treino, recomendação e publicação."""
from datetime import datetime, timezone

import config
import extracao
import transformacao
import treino
import recomendacao
import publicacao


def executar():
    inicio = datetime.now(timezone.utc)
    versao = inicio.strftime("%Y%m%d%H%M%S")
    gerado_em = inicio.isoformat()
    print(f"[{versao}] Iniciando pipeline")

    dados = extracao.extrair()
    print("Tabelas extraídas:", {k: len(v) for k, v in dados.items()})

    curtidas, visiveis = transformacao.limpar_curtidas(dados)
    print("Curtidas válidas:", len(curtidas), "| Usuários com histórico:", curtidas["id_usuario"].nunique())

    conteudo = transformacao.construir_conteudo(
        visiveis, dados["Tag"], dados["Tag_review"],
        config.W_TAG, config.W_NOTA, config.W_LOCAL)

    als = treino.treinar_als(curtidas)
    caminho_modelo = treino.salvar_artefatos(als, conteudo, versao)
    print("Modelo salvo em:", caminho_modelo)

    recs = recomendacao.gerar_recomendacoes(curtidas, als, conteudo)
    print("Recomendações geradas:", len(recs), "linhas para", recs["user_id"].nunique(), "usuários")

    destino = publicacao.publicar(recs, versao, gerado_em)
    print("Publicado em:", destino)


if __name__ == "__main__":
    executar()
