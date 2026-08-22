import numpy as np
from risk_service import calcular_risco

# Tarifas por categoria — igual ao platforms.ts do app
PLATFORMS = {
    "uber-moto":    { "base": 3.5,  "per_km": 1.1, "per_min": 0.15 },
    "uber-x":       { "base": 4.5,  "per_km": 1.9, "per_min": 0.25 },
    "uber-confort": { "base": 7.5,  "per_km": 2.8, "per_min": 0.45 },
    "uber-black":   { "base": 12.0, "per_km": 4.2, "per_min": 0.70 },
    "99-moto":      { "base": 3.2,  "per_km": 1.0, "per_min": 0.12 },
    "99-pop":       { "base": 4.0,  "per_km": 1.8, "per_min": 0.22 },
    "99-plus":      { "base": 6.5,  "per_km": 2.4, "per_min": 0.38 },
}

# Multiplicadores por horário
HORA_MULTIPLICADOR = {
    range(0,  5):  0.80,
    range(5,  7):  0.90,
    range(7, 10):  1.40,
    range(10, 16): 1.00,
    range(16, 20): 1.35,
    range(20, 24): 1.10,
}

# Raio máximo de busca em metros
RAIO_METROS = 500

def get_multiplicador_hora(hora: int) -> float:
    for intervalo, mult in HORA_MULTIPLICADOR.items():
        if hora in intervalo:
            return mult
    return 1.0

def calcular_preco(categoria: str, distancia_km: float, duracao_min: float, hora: int) -> float:
    # Usa as tarifas da categoria — fallback para uber-x se não encontrar
    p = PLATFORMS.get(categoria, PLATFORMS["uber-x"])
    mult = get_multiplicador_hora(hora)
    preco = p["base"] + p["per_km"] * distancia_km + p["per_min"] * duracao_min
    return round(preco * mult, 2)

def metros_para_graus(metros: float) -> float:
    # Converte metros para graus de latitude/longitude
    # 1 grau ≈ 111.32 km na superfície da Terra
    return metros / 111320.0

def gerar_pontos_alternativos(lat: float, lon: float) -> list:
    # Gera 8 pontos em direções diferentes ao redor do usuário
    # N, NE, E, SE, S, SW, W, NW — como uma bússola
    # Distâncias variadas: 100m, 200m, 300m, 400m, 500m
    pontos = []
    distancias = [100, 200, 300, 400, 500]
    angulos = [0, 45, 90, 135, 180, 225, 270, 315]  # graus

    for distancia in distancias:
        for angulo in angulos:
            # Converte ângulo para radianos
            rad = np.radians(angulo)

            # Calcula o deslocamento em graus
            delta_lat = (distancia * np.cos(rad)) / 111320.0
            delta_lon = (distancia * np.sin(rad)) / (111320.0 * np.cos(np.radians(lat)))

            pontos.append({
                "lat": lat + delta_lat,
                "lon": lon + delta_lon,
                "distance_meters": distancia,
            })

    return pontos

def calcular_distancia_metros(lat1, lon1, lat2, lon2) -> float:
    # Fórmula de Haversine para distância entre dois pontos
    R = 6371000  # raio da Terra em metros
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi/2)**2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

def gerar_recomendacoes(
    lat: float,
    lon: float,
    dest_lat: float,
    dest_lon: float,
    distancia_km: float,
    duracao_min: float,
    hora: int,
    dia_semana: int,
    plataforma: str,
    categoria: str,
    preco_estimado: float,
) -> dict:

    # Recomendação de horário
    # Verifica se em 20 minutos o multiplicador muda
    hora_futura = (hora + 1) % 24
    mult_atual = get_multiplicador_hora(hora)
    mult_futuro = get_multiplicador_hora(hora_futura)

    p = PLATFORMS.get(categoria, PLATFORMS["uber-x"])
    preco_base = p["base"] + p["per_km"] * distancia_km + p["per_min"] * duracao_min
    preco_futuro = round(preco_base * mult_futuro, 2)
    economia_horario = round(preco_estimado - preco_futuro, 2)

    time_recommendation = None
    if economia_horario > 2.0 and mult_futuro < mult_atual:
        time_recommendation = {
            "type": "time",
            "message": f"Aguarde até as {hora_futura}h — preço tende a cair",
            "economy": economia_horario,
            "hora_sugerida": hora_futura,
            "risk_level": None,
        }

    # Recomendações de localização
    pontos = gerar_pontos_alternativos(lat, lon)
    resultados = []

    for ponto in pontos:
        # Calcula nova distância até o destino a partir do ponto alternativo
        nova_dist = calcular_distancia_metros(ponto["lat"], ponto["lon"], dest_lat, dest_lon) / 1000
        nova_duracao = nova_dist * 1.5  # estimativa simples de duração

        # Calcula preço no ponto alternativo
        novo_preco = calcular_preco(categoria, nova_dist, nova_duracao, hora)
        economia = round(preco_estimado - novo_preco, 2)

        # Só recomenda se economizar mais de R$ 2
        if economia <= 2.0:
            continue

        # Calcula risco do ponto alternativo
        risco = calcular_risco(ponto["lat"], ponto["lon"])

        resultados.append({
            "type": "location",
            "lat": ponto["lat"],
            "lon": ponto["lon"],
            "distance_meters": ponto["distance_meters"],
            "economy": economia,
            "new_price": novo_preco,
            "risk_level": risco["risk_level"],
            "risk_label": risco["risk_label"],
            "total_crimes_nearby": risco["total_crimes_nearby"],
            "most_common_crime": risco["most_common_crime"],
        })

    # Agrupa por nível de risco e pega o melhor de cada grupo
    # "melhor" = maior economia dentro do nível de risco
    grupos = {"low": None, "medium": None, "high": None}

    for r in resultados:
        nivel = r["risk_level"]
        if grupos[nivel] is None or r["economy"] > grupos[nivel]["economy"]:
            grupos[nivel] = r

    # Monta lista final — uma recomendação por nível de risco
    location_recommendations = [v for v in grupos.values() if v is not None]
    location_recommendations.sort(key=lambda x: x["economy"], reverse=True)

    return {
        "current_price": preco_estimado,
        "time_recommendation": time_recommendation,
        "location_recommendations": location_recommendations,
    }