import numpy as np
import pandas as pd
import config


def perfil_usuario(itens_curtidos, conteudo):
    """Média dos vetores de conteúdo dos posts curtidos pelo usuário."""
    idx = [conteudo["pos_p"][p] for p in itens_curtidos if p in conteudo["pos_p"]]
    if not idx:
        return None
    perfil = conteudo["X"][idx].mean(axis=0)
    return perfil / max(np.linalg.norm(perfil), 1e-12)


def gerar_recomendacoes(curtidas, als, conteudo, k=config.K, n_expl=config.EXPLORACAO):
    """
    Gera K posts por usuário com histórico.
    Vagas de preferência: ALS, entre posts com curtidas no treino.
    Vagas de exploração: conteúdo, entre posts sem curtidas.
    Usuários sem curtidas não recebem linhas: o app mostra o feed cronológico.
    """
    model, itens, iidx, uidx, M = als["model"], als["itens"], als["iidx"], als["uidx"], als["M"]
    post_ids, X = conteudo["post_ids"], conteudo["X"]
    gostos = curtidas.groupby("id_usuario")["id_review"].apply(list).to_dict()
    quentes = np.array([p in iidx for p in post_ids])
    fator_itens = model.item_factors

    linhas = []
    for u, itens_u in gostos.items():
        if u not in uidx:
            continue
        perfil = perfil_usuario(itens_u, conteudo)
        if perfil is None:
            continue

        vistos = set(itens_u)
        nao_vistos = np.array([p not in vistos for p in post_ids])
        ui = uidx[u]

        cand_q = np.where(quentes & nao_vistos)[0]
        if cand_q.size:
            s_als = model.user_factors[ui] @ fator_itens.T
            sc_q = np.array([s_als[iidx[post_ids[j]]] for j in cand_q])
            ordem_q = list(cand_q[np.argsort(-sc_q)])
        else:
            ordem_q = []

        cand_f = np.where(~quentes & nao_vistos)[0]
        s_cont = X @ perfil
        ordem_f = list(cand_f[np.argsort(-s_cont[cand_f])]) if cand_f.size else []

        n_f = min(n_expl, len(ordem_f))
        sel_q = ordem_q[:k - n_f]
        falta = k - len(sel_q) - n_f
        sel_f = ordem_f[:n_f + max(falta, 0)]

        origem_als = set(sel_q)
        for rank, j in enumerate((sel_q + sel_f)[:k], start=1):
            linhas.append({"user_id": u, "post_id": post_ids[j], "rank": rank,
                           "origem": "als" if j in origem_als else "conteudo"})

    return pd.DataFrame(linhas)
