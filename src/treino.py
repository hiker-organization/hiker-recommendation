import os
import joblib
import numpy as np
from scipy.sparse import csr_matrix
from implicit.als import AlternatingLeastSquares

import config

def treinar_als(curtidas):
    """Treina o ALS com todas as curtidas válidas."""
    # Itens são a review apenas da df curtidas que limpamos antes
    itens = curtidas["id_review"].unique()
    # Usuários é o usuário da df curtidas
    usuarios = curtidas["id_usuario"].unique()
    # Criamos uma tabela com o valor de itens e indexes ordenados e també para usuario 
    iidx = {p: i for i, p in enumerate(itens)}
    uidx = {u: i for i, u in enumerate(usuarios)}

    # Vamos criar a matriz com 1 inicialmente de peso, os valores mapeados de usuarios e de reviews
    M = csr_matrix(
        (np.ones(len(curtidas)),
         (curtidas["id_usuario"].map(uidx).astype(int).values,
          curtidas["id_review"].map(iidx).astype(int).values)),
        shape=(len(usuarios), len(itens)))

    # Chamando o modelo ALS, precisamos passar quais os fatores, a forma de regularização, as iterações, estado random e se vai usar gpu 
    model = AlternatingLeastSquares(
        factors=config.FACTORS, regularization=config.REG,
        iterations=config.ITERATIONS, random_state=config.SEED, use_gpu=False) # aqui só passamos os parâmetros
    # Treinando o modelo (fit) com a matriz M multiplicada pelo fator ALPHA, típico de modelos de feedback implícito, alpha controla a confiança dada as iterações
    model.fit((M * config.ALPHA).astype(np.float32), show_progress=False) # deve converter os valores para float e não mostra a barra de progresso desse treinamento

    # essa função retorna então os dados do modelo treinado, itens, index de itens e de usuarios e a matriz M
    return {"model": model, "itens": itens, "iidx": iidx, "uidx": uidx, "M": M}


def salvar_artefatos(als, conteudo, versao):
    """Salva o modelo e os índices em disco, para auditoria e reprodução."""
    os.makedirs(config.PASTA_ARTEFATOS, exist_ok=True)
    caminho = os.path.join(config.PASTA_ARTEFATOS, f"modelo_{versao}.joblib")
    joblib.dump({"als": als, "conteudo": conteudo}, caminho)
    return caminho
