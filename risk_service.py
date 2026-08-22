import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree
from database import get_crimes

RAIO_KM = 0.5

RISCO_BAIXO = 3
RISCO_MEDIO = 8

# Mapeamento de tipo_assalto_id para categoria legível
TIPOS_ASSALTO = {
    1: "Furto de veículo",
    2: "Roubo a pedestre",
    3: "Roubo de veículo",
    4: "Furto a pedestre",
    5: "Roubo em semáforo",
    6: "Roubo em residência",
    7: "Furto em residência",
    8: "Roubo a estabelecimento",
}

def calcular_risco(lat: float, lon: float) -> dict:
    df = get_crimes()

    # BallTree para busca geográfica otimizada
    coords_crimes = np.radians(df[["latitude", "longitude"]].values)
    tree = BallTree(coords_crimes, metric="haversine")

    ponto = np.radians([[lat, lon]])
    raio_rad = RAIO_KM / 6371.0

    indices = tree.query_radius(ponto, r=raio_rad)[0]
    total_crimes = len(indices)

    if total_crimes <= RISCO_BAIXO:
        nivel = "low"
        label = "Baixo"
    elif total_crimes <= RISCO_MEDIO:
        nivel = "medium"
        label = "Médio"
    else:
        nivel = "high"
        label = "Alto"

    # Pega o tipo de crime mais comum na área pelo ID
    if len(indices) > 0:
        crimes_proximos = df.iloc[indices]
        tipo_id_mais_comum = crimes_proximos["tipo_assalto_id"].value_counts().index[0]
        tipo_mais_comum = TIPOS_ASSALTO.get(int(tipo_id_mais_comum), "Outros")
    else:
        tipo_mais_comum = None

    return {
        "risk_level": nivel,
        "risk_label": label,
        "total_crimes_nearby": total_crimes,
        "radius_meters": int(RAIO_KM * 1000),
        "most_common_crime": tipo_mais_comum,
    }