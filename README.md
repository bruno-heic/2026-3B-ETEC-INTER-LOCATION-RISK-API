# Location Risk API

## Visão Geral

A API analisa a densidade de crimes num raio de 500 metros ao redor do usuário e gera recomendações personalizadas de economia. Para cada recomendação de localização alternativa, o nível de risco é calculado automaticamente — permitindo que o usuário escolha entre segurança e economia.


## Requisitos

- Python 3.12+
- pip 24+
- Arquivo `dataset-limpo.csv` na raiz do projeto


## Instalação

Clone o repositório e ative o ambiente virtual:

```bash
git clone https://github.com/seu-usuario/rideless-intelligence.git
cd rideless-intelligence
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

Instale as dependências:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn scipy
```

## Como Rodar

### Desenvolvimento local

```bash
uvicorn main:app --reload
```

### Acessível externamente (necessário para o app mobile)

```bash
uvicorn main:app --reload --host 0.0.0.0
```

### GitHub Codespaces

Após iniciar a API:

1. Acesse a aba **Ports** no VS Code
2. Clique com botão direito na porta **8000**
3. Selecione **Port Visibility → Public**

Copie a URL gerada e configure no app.

### Documentação interativa

```
http://127.0.0.1:8000/docs
```

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status da API |
| `POST` | `/risk` | Avalia o nível de risco de uma área |
| `POST` | `/recommend` | Gera recomendações de economia e segurança |


## Exemplos de Payload

### POST /risk

```json
{
  "lat": -23.5505,
  "lon": -46.6333
}
```

Resposta:

```json
{
  "risk_level": "high",
  "risk_label": "Alto",
  "total_crimes_nearby": 108,
  "radius_meters": 500,
  "most_common_crime": "Roubo a pedestre"
}
```

### POST /recommend

```json
{
  "lat": -23.6273,
  "lon": -46.6566,
  "dest_lat": -23.5505,
  "dest_lon": -46.6333,
  "distancia_km": 12.4,
  "duracao_min": 18.0,
  "hora": 19,
  "dia_semana": 4,
  "plataforma": "uber",
  "categoria": "uber-x",
  "preco_estimado": 45.58
}
```

Resposta:

```json
{
  "current_price": 45.58,
  "time_recommendation": {
    "type": "time",
    "message": "Aguarde até as 20h — preço tende a cair",
    "economy": 8.50,
    "hora_sugerida": 20,
    "risk_level": null
  },
  "location_recommendations": [
    {
      "type": "location",
      "lat": -23.6228,
      "lon": -46.6566,
      "distance_meters": 500,
      "economy": 13.76,
      "new_price": 31.82,
      "risk_level": "medium",
      "risk_label": "Médio",
      "total_crimes_nearby": 4,
      "most_common_crime": "Roubo a pedestre"
    },
    {
      "type": "location",
      "lat": -23.6237,
      "lon": -46.6566,
      "distance_meters": 400,
      "economy": 13.46,
      "new_price": 32.12,
      "risk_level": "low",
      "risk_label": "Baixo",
      "total_crimes_nearby": 2,
      "most_common_crime": "Furto de veículo"
    },
    {
      "type": "location",
      "lat": -23.6241,
      "lon": -46.6600,
      "distance_meters": 500,
      "economy": 13.00,
      "new_price": 32.58,
      "risk_level": "high",
      "risk_label": "Alto",
      "total_crimes_nearby": 14,
      "most_common_crime": "Furto de veículo"
    }
  ]
}
```

## Estrutura do Projeto

```
rideless-intelligence/
├── main.py              # Endpoints da API
├── schemas.py           # Validação dos dados de entrada
├── database.py          # Carregamento do dataset de crimes em memória
├── risk_service.py      # Cálculo de risco por densidade de crimes
├── recommend_service.py # Geração de recomendações de localização e horário
└── dataset-limpo.csv    # Dataset de ocorrências de São Paulo (não versionado)
```


## Como Funciona

### Avaliação de Risco

Utiliza **BallTree** com métrica **Haversine** para busca geográfica otimizada — em vez de calcular a distância para todos os 15.524 crimes, a estrutura de árvore encontra os vizinhos próximos em milissegundos.

```
Coordenadas do usuário
        ↓
BallTree busca crimes num raio de 500m
        ↓
Conta ocorrências e identifica tipo mais comum
        ↓
Classifica o nível de risco
```

| Ocorrências no raio | Nível |
|---|---|
| 0 a 3 | Baixo |
| 4 a 8 | Médio |
| 9+ | Alto |

### Recomendações de Localização

Gera 40 pontos alternativos ao redor do usuário — 8 direções (N, NE, E, SE, S, SW, W, NW) em 5 distâncias (100m, 200m, 300m, 400m, 500m). Para cada ponto calcula:

- Nova distância até o destino
- Novo preço estimado da corrida
- Nível de risco da área

Filtra pontos com economia menor que R$ 2,00 e retorna o melhor de cada nível de risco — garantindo sempre até 3 opções para o usuário escolher.

### Recomendações de Horário

Compara o multiplicador de preço do horário atual com o da próxima hora. Se a economia for maior que R$ 2,00, gera uma recomendação de aguardar.

| Horário | Multiplicador |
|---|---|
| 0h – 5h | 0.80 (baixa demanda) |
| 5h – 7h | 0.90 |
| 7h – 10h | 1.40 (pico manhã) |
| 10h – 16h | 1.00 (normal) |
| 16h – 20h | 1.35 (pico tarde) |
| 20h – 24h | 1.10 |

## Dataset

O dataset utilizado é de ocorrências registradas na cidade de São Paulo com coordenadas geográficas. Contém 15.524 registros válidos após limpeza.

O arquivo `dataset-limpo.csv` não é versionado no repositório por questões de tamanho. Adicione ao `.gitignore`:

```
dataset-limpo.csv
```
## Licença

MIT
