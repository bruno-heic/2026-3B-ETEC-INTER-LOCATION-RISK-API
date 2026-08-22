import pandas as pd
import numpy as np

# Carrega o dataset uma única vez quando a API iniciar
# Em memória = consultas instantâneas sem ler o arquivo a cada requisição
print("Carregando dataset de crimes...")
df_crimes = pd.read_csv("dataset-limpo.csv")

# Remove registros sem coordenadas — não servem para análise geográfica
df_crimes = df_crimes.dropna(subset=["latitude", "longitude"])

# Converte coordenadas para número — o CSV pode ter vindo como texto
df_crimes["latitude"] = pd.to_numeric(df_crimes["latitude"], errors="coerce")
df_crimes["longitude"] = pd.to_numeric(df_crimes["longitude"], errors="coerce")

# Remove registros que não converteram corretamente
df_crimes = df_crimes.dropna(subset=["latitude", "longitude"])

# Extrai hora da coluna time para análise de padrões por horário
df_crimes["hora"] = pd.to_datetime(df_crimes["time"], errors="coerce").dt.hour

print(f"Dataset carregado — {len(df_crimes)} ocorrências válidas")

def get_crimes():
    # Retorna o dataframe de crimes para uso nos serviços
    return df_crimes