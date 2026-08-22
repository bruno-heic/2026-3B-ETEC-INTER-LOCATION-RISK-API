from pydantic import BaseModel

# Coordenadas simples — usado em vários endpoints
class Coordinates(BaseModel):
    lat: float
    lon: float

# Payload do endpoint /risk
# Recebe apenas a localização do usuário
class RiskRequest(BaseModel):
    lat: float
    lon: float

# Payload do endpoint /recommend
# Recebe localização + dados da corrida para calcular economia
class RecommendRequest(BaseModel):
    lat: float
    lon: float
    dest_lat: float
    dest_lon: float
    distancia_km: float
    duracao_min: float
    hora: int
    dia_semana: int
    plataforma: str
    categoria: str
    preco_estimado: float