from fastapi import FastAPI
from schemas import RiskRequest, RecommendRequest
from risk_service import calcular_risco
from recommend_service import gerar_recomendacoes

app = FastAPI()

@app.get("/")
def root():
    return { "status": "Rideless Intelligence API running" }

@app.post("/risk")
def get_risk(request: RiskRequest):
    # Recebe as coordenadas do usuário
    # Retorna o nível de risco da área
    result = calcular_risco(request.lat, request.lon)
    return result

@app.post("/recommend")
def get_recommendations(request: RecommendRequest):
    # Recebe coordenadas + dados da corrida
    # Retorna recomendações de horário e localização
    result = gerar_recomendacoes(
        lat=request.lat,
        lon=request.lon,
        dest_lat=request.dest_lat,
        dest_lon=request.dest_lon,
        distancia_km=request.distancia_km,
        duracao_min=request.duracao_min,
        hora=request.hora,
        dia_semana=request.dia_semana,
        plataforma=request.plataforma,
        categoria=request.categoria,
        preco_estimado=request.preco_estimado,
    )
    return result