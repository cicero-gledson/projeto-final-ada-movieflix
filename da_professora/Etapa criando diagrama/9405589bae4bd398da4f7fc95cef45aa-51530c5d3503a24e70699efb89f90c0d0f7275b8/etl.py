import pandas as pd

# === EXTRACT: ler CSV do Data Warehouse ===
df_warehouse = pd.read_csv("data/filmes_clean.csv")

# === TRANSFORM: filtrar para Data Mart ===
# Exemplo: só filmes de Ficção Científica
df_mart = df_warehouse[df_warehouse["genero"] == "Ficção Científica"]

# Selecionar apenas colunas relevantes para análise
df_mart = df_mart[["titulo", "ano_lancamento", "nota_imdb"]]

# === LOAD: salvar Data Mart em outro CSV ===
df_mart.to_csv("data/filmes_genero_ficcao.csv", index=False, encoding="utf-8")

print("✅ Data Mart criado! Arquivo salvo em data/filmes_genero_ficcao.csv")
