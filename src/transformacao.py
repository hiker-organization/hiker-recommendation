import numpy as np
import pandas as pd


def limpar_curtidas(dados):
    """Mantém só curtidas válidas: LIKE, posts visíveis, sem autoavaliação, sem duplicatas."""
    # Criando tabela para interações que pega de voto_review que criamos o dataframe a partir de extracao.py
    # Criamos a tabela posts também
    inter = dados["Voto_review"].copy()
    posts = dados["Review"].copy()

    # Voto_review já tinha a coluna tipo, que aqui vamos transformar em string e maiúscula
    inter["tipo"] = inter["tipo"].astype(str).str.strip().str.upper()
    inter["createdAt"] = pd.to_datetime(inter["createdAt"], errors="coerce")

    # oculto é tudo que vem de posts onde na coluna oculto, não preenchendo com na e tipo booleano
    oculto = posts["oculto"].fillna(False).astype(bool)
    # visiveis vem de posts e é diferente de oculto
    visiveis = posts[~oculto].copy()
    # autor pega o usuário de posts
    autor = posts.set_index("id")["id_usuario"]

    # Etapas de filtragem das curtidas
    # para curtidas temos da tabela interação todas que tem o tipo LIKE
    curtidas = inter[inter["tipo"] == "LIKE"]
    # a partir dessas, temos as cuja review é visível
    curtidas = curtidas[curtidas["id_review"].isin(visiveis["id"])]
    # a partir dessas, temos as cujo usuário que curtiu é diferente do autor da postagem
    curtidas = curtidas[curtidas["id_usuario"] != curtidas["id_review"].map(autor)]
    # ai temos que curtidas tem o usuário, review e data de criação
    curtidas = (curtidas[["id_usuario", "id_review", "createdAt"]]
                .dropna() #tirando vazios
                .sort_values("createdAt") #organizando por data
                .drop_duplicates(["id_usuario", "id_review"], keep="first") #removendoo duplicatas com base no usuario e post
                .reset_index(drop=True)) # resetar o index
    return curtidas, visiveis #a função retorna então essas curtidas e também os posts visíveis
    # O dataframe curtidas será utilizado para entender a relação do usuário com as postagens visíveis


def construir_conteudo(visiveis, tags, tag_post, w_tag, w_nota, w_local):
    # Para construir precisamos das postagens visíveis
    """Vetor de conteúdo por post: tags (multi-hot), nota normalizada e lugar (one-hot), normalizado."""
    # id dos posts vem da df visíveis
    post_ids = visiveis["id"].values
    # criando um dicionário de busca que mapeia o id de cada post e cada tag para a posição dele na matriz de conteúdo
    # enumerate percorre uma lista e entrega a enumeração e o valor, então se a lista é [30, 40, 50] o enumerate retorna {[0, 30], [1, 40], [2, 50]}
    pos_p = {p: i for i, p in enumerate(post_ids)} 
        # numerar os posts_ids (index)
        # i recebe a posição e p recebe o valor
        # retorne p e i
        # for i, p usando esse enumerate
    pos_t = {t: i for i, t in enumerate(tags["id"].values)}
        # faz a mesma coisa com as tags das reviews visiveis

    # T é uma matriz com zeros na dimensão de length de posts_ids e pos_t
    T = np.zeros((len(post_ids), len(pos_t)))
    # Preenche a matriz T com 1 nas posições em que um post tem uma tag
    # Uma linha por post e uma coluna por tag
    for p, t in zip(tag_post["id_review"], tag_post["id_tag"]): # para os valores de p e de t (que criamos acima) o zip junta em pares a review e tag
        if p in pos_p and t in pos_t: # se existir nessas tabelas
            T[pos_p[p], pos_t[t]] = 1.0 #T recebe o valor 1.0 para ser colocado na linha ded pos_p[p referente] e coluna de pos_t[t referente]

    # Os valores da coluna nota da df visiveis é dividido por 5 para normalizar a escala e transformado a lista em uma coluna com reshape
    N = (visiveis["nota"].values / 5.0).reshape(-1, 1)
    # Da coluna id_local da df visiveis vamos pegar a lista de locais, separá-los em uma matriz onde temos a coluna como tag e linha como post e se tiver a tag temos 1 na célula
    L = pd.get_dummies(visiveis["id_local"]).values.astype(float)

    # hstack junta os blocos com um peso, temos os blocos w_tag, w_nota e w_local multiplicados com seus pesos correspondentes
    X = np.hstack([w_tag * T, w_nota * N, w_local * L])
    # Processo de normalização
    X = X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)
    # Essa função vai retornar então um objeto com os ids dos posts, a tabela com o valor do id e o index e o X que são os pesos
    return {"post_ids": post_ids, "pos_p": pos_p, "X": X}
    # Isso será usado para treinar o modelo
