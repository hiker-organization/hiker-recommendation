import os
from dotenv import load_dotenv

load_dotenv()

# Supabase (use a service_role key apenas no backend, nunca no app)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Nomes das tabelas no Supabase (ajuste para os nomes reais)
TABELA_INTERACOES = os.getenv("TABELA_INTERACOES", "Voto_review")
TABELA_POSTS = os.getenv("TABELA_POSTS", "Review")
TABELA_TAGS = os.getenv("TABELA_TAGS", "Tag")
TABELA_TAG_POST = os.getenv("TABELA_TAG_POST", "Tag_review")
TABELA_RECOMENDACOES = os.getenv("TABELA_RECOMENDACOES", "Recomendacao")

# Modo de desenvolvimento: se preenchido, lê CSVs dessa pasta em vez do Supabase
DADOS_LOCAIS = os.getenv("DADOS_LOCAIS", "")
# "supabase" grava no banco; "csv" grava em artefatos/recomendacoes.csv
DESTINO = os.getenv("DESTINO", "database")

# Parâmetros do modelo (fixados após a avaliação no notebook)
K = 5
EXPLORACAO = 1
FACTORS, REG, ALPHA, ITERATIONS = 10, 0.1, 10.0, 15 # Servem para treinar o modelo
W_TAG, W_NOTA, W_LOCAL = 1.0, 0.5, 0.5
SEED = 42

PASTA_ARTEFATOS = "artefatos"
