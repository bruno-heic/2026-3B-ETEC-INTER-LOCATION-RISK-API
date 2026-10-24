# Location Risk API

API de **risco de localização e recomendações de economia** do [Rideless](https://github.com/seu-usuario/rideless-app). Ela analisa a densidade de ocorrências criminais num raio de 500 metros ao redor de um ponto e sugere **onde embarcar** e **quando pedir** para pagar menos, informando o **nível de risco** de cada sugestão. Assim, o usuário escolhe entre economia e segurança.

> O app consome esta API pelo arquivo `services/intelligence.ts`. Ela é independente da Rideless API de previsão de preço, que usa outro servidor.

## Índice

- [Início rápido](#início-rápido)
- [Requisitos](#requisitos)
- [Instalação passo a passo](#instalação-passo-a-passo)
- [Como rodar](#como-rodar)
- [Testando a API](#testando-a-api)
- [Conectando o app mobile](#conectando-o-app-mobile)
- [Referência da API](#referência-da-api)
- [Como funciona](#como-funciona)
- [Dataset](#dataset)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Solução de problemas](#solução-de-problemas)
- [Limitações](#limitações)
- [Licença](#licença)

## Início rápido

```bash
git clone https://github.com/bruno-heic/2026-3B-ETEC-INTER-LOCATION-RISK-API.git
cd 2026-3B-ETEC-INTER-LOCATION-RISK-API
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0
```

Abra http://127.0.0.1:8000/docs. Se a página de documentação carregar, a API está no ar.

## Requisitos

| Item | Versão / detalhe |
|---|---|
| Python | 3.12 ou superior (`python --version`) |
| pip | 24 ou superior (`pip --version`) |
| `dataset-limpo.csv` | na raiz do projeto, ao lado do `main.py` |
| Rede | celular e computador na mesma rede Wi-Fi (ou um túnel/Codespaces, veja abaixo) |

## Instalação passo a passo

**1. Clone o repositório e entre na pasta**

```bash
git clone https://github.com/bruno-heic/2026-3B-ETEC-INTER-LOCATION-RISK-API.git
cd 2026-3B-ETEC-INTER-LOCATION-RISK-API
```

**2. Crie o ambiente virtual**

```bash
python -m venv venv
```

**3. Ative o ambiente virtual**

| Sistema | Comando |
|---|---|
| Linux / macOS | `source venv/bin/activate` |
| Windows (PowerShell) | `venv\Scripts\Activate.ps1` |
| Windows (cmd) | `venv\Scripts\activate.bat` |

O terminal deve mostrar `(venv)` no início da linha. Se o PowerShell bloquear o script, rode uma vez `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` e tente de novo.

**4. Instale as dependências**

```bash
pip install -r requirements.txt
```

Sem o `requirements.txt`, instale direto:

```bash
pip install fastapi uvicorn pandas numpy scikit-learn scipy
```

**5. Confirme que o dataset está no lugar**

O arquivo `dataset-limpo.csv` precisa estar na mesma pasta do `main.py`. Ele é lido na inicialização, então rode sempre os comandos a partir da raiz do projeto.

## Como rodar

### Desenvolvimento local (só o seu computador)

```bash
uvicorn main:app --reload
```

A API fica em `http://127.0.0.1:8000`.

### Acessível pelo celular (necessário para o app)

```bash
uvicorn main:app --reload --host 0.0.0.0
```

O `--host 0.0.0.0` faz a API aceitar conexões de outros dispositivos da rede. Sem ele, só o próprio computador consegue acessá-la.

### Mudar a porta

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Produção (sem recarga automática)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

O dataset é carregado em memória quando a API inicia, então a primeira subida leva alguns segundos e o servidor precisa de memória suficiente para ele.

## Testando a API

### Pela documentação interativa (mais fácil)

Abra http://127.0.0.1:8000/docs, escolha um endpoint, clique em **Try it out**, preencha o JSON e execute.

### Pelo terminal

Verificar se está no ar:

```bash
curl http://127.0.0.1:8000/
```

Avaliar o risco de um ponto:

```bash
curl -X POST http://127.0.0.1:8000/risk \
  -H "Content-Type: application/json" \
  -d '{"lat": -23.5505, "lon": -46.6333}'
```

Gerar recomendações:

```bash
curl -X POST http://127.0.0.1:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "lat": -23.6273, "lon": -46.6566,
    "dest_lat": -23.5505, "dest_lon": -46.6333,
    "distancia_km": 12.4, "duracao_min": 18.0,
    "hora": 19, "dia_semana": 4,
    "plataforma": "uber", "categoria": "uber-x",
    "preco_estimado": 45.58
  }'
```

No **Windows PowerShell** (onde `curl` é um apelido diferente), use:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/risk `
  -ContentType "application/json" `
  -Body '{"lat": -23.5505, "lon": -46.6333}'
```

## Conectando o app mobile

O app Rideless precisa de uma URL que o celular consiga alcançar. Escolha uma das opções.

### Opção 1: mesma rede Wi-Fi

1. Rode a API com `--host 0.0.0.0`.
2. Descubra o IP do computador na rede:

| Sistema | Comando |
|---|---|
| Windows | `ipconfig` (campo "Endereço IPv4") |
| macOS | `ipconfig getifaddr en0` |
| Linux | `hostname -I` |

3. No app, em `services/intelligence.ts`, configure (sem barra no final):

```typescript
const INTELLIGENCE_URL = "http://192.168.0.10:8000"; // use o seu IP
```

4. No Windows, se aparecer o aviso do firewall, permita o Python em **redes privadas**.
5. Teste no navegador do celular: `http://SEU_IP:8000/docs` deve abrir a documentação.

### Opção 2: GitHub Codespaces

1. Inicie a API: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
2. Abra a aba **Ports** no VS Code.
3. Clique com o botão direito na porta **8000** e escolha **Port Visibility → Public**.
4. Copie a URL gerada (algo como `https://...-8000.app.github.dev`) e use em `INTELLIGENCE_URL`.

A porta volta a ficar privada se o Codespace reiniciar. Quando o app parar de conectar, confira a visibilidade de novo.

### Opção 3: túnel (ngrok, Cloudflare Tunnel etc.)

Rode a API normalmente e exponha a porta 8000 com a ferramenta de túnel de sua preferência. Use a URL `https` gerada em `INTELLIGENCE_URL`.

> Para builds de produção do app, use sempre uma URL **HTTPS**. Plataformas móveis bloqueiam HTTP puro em apps publicados.

## Referência da API

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Status da API |
| `POST` | `/risk` | Avalia o nível de risco de uma área |
| `POST` | `/recommend` | Gera recomendações de economia e segurança |

### `POST /risk`

**Entrada**

| Campo | Tipo | Descrição |
|---|---|---|
| `lat` | número | Latitude do ponto |
| `lon` | número | Longitude do ponto |

**Saída**

```json
{
  "risk_level": "high",
  "risk_label": "Alto",
  "total_crimes_nearby": 108,
  "radius_meters": 500,
  "most_common_crime": "Roubo a pedestre"
}
```

| Campo | Descrição |
|---|---|
| `risk_level` | `low`, `medium` ou `high` |
| `risk_label` | Rótulo em português: Baixo, Médio ou Alto |
| `total_crimes_nearby` | Ocorrências encontradas no raio |
| `radius_meters` | Raio da análise (500) |
| `most_common_crime` | Tipo de ocorrência mais frequente na área |

### `POST /recommend`

**Entrada**

| Campo | Tipo | Descrição |
|---|---|---|
| `lat`, `lon` | número | Posição atual do usuário (origem) |
| `dest_lat`, `dest_lon` | número | Posição do destino |
| `distancia_km` | número | Distância da corrida |
| `duracao_min` | número | Duração estimada da corrida, em minutos |
| `hora` | inteiro | Hora do dia (0 a 23) |
| `dia_semana` | inteiro | Dia da semana |
| `plataforma` | texto | Plataforma de corrida (ex.: `uber`) |
| `categoria` | texto | Categoria do veículo (ex.: `uber-x`) |
| `preco_estimado` | número | Preço atual estimado, em R$ |

**Saída**

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
      "lat": -23.6237,
      "lon": -46.6566,
      "distance_meters": 400,
      "economy": 13.46,
      "new_price": 32.12,
      "risk_level": "low",
      "risk_label": "Baixo",
      "total_crimes_nearby": 2,
      "most_common_crime": "Furto de veículo"
    }
  ]
}
```

| Campo | Descrição |
|---|---|
| `current_price` | Preço informado na entrada |
| `time_recommendation` | Sugestão de esperar por um horário mais barato |
| `time_recommendation.hora_sugerida` | Hora sugerida para pedir |
| `location_recommendations` | Até 3 pontos de embarque alternativos, um por nível de risco |
| `lat`, `lon` | Coordenadas do ponto sugerido |
| `distance_meters` | Distância a pé do usuário até o ponto |
| `economy` | Quanto o usuário economiza (R$) |
| `new_price` | Novo preço estimado a partir do ponto |
| `risk_level`, `risk_label` | Nível de risco do ponto |
| `total_crimes_nearby` | Ocorrências no raio de 500 m do ponto |
| `most_common_crime` | Tipo de ocorrência mais frequente no ponto |

A recomendação de horário só é gerada quando esperar compensa (veja abaixo). Trate `time_recommendation` como opcional no cliente.

## Como funciona

### Avaliação de risco

A API usa uma **BallTree** com métrica **Haversine** para busca geográfica. Em vez de calcular a distância para todas as ocorrências do dataset, a árvore encontra os vizinhos próximos em milissegundos.

```
Coordenadas do ponto
        ↓
BallTree busca ocorrências num raio de 500 m
        ↓
Conta as ocorrências e identifica o tipo mais comum
        ↓
Classifica o nível de risco
```

| Ocorrências no raio | Nível |
|---|---|
| 0 a 3 | Baixo |
| 4 a 8 | Médio |
| 9 ou mais | Alto |

### Recomendações de localização

A API gera **40 pontos alternativos** ao redor do usuário: 8 direções (N, NE, E, SE, S, SW, W, NW) em 5 distâncias (100 m, 200 m, 300 m, 400 m e 500 m). Para cada ponto, calcula:

- a nova distância até o destino
- o novo preço estimado da corrida
- o nível de risco da área

Pontos com economia menor que **R$ 2,00** são descartados. Entre os restantes, a API devolve o melhor de cada nível de risco, ou seja, **até 3 opções** para o usuário escolher.

### Recomendações de horário

A API compara o multiplicador de preço do horário atual com o da próxima hora. Se a economia for maior que **R$ 2,00**, gera a recomendação de aguardar.

| Horário | Multiplicador |
|---|---|
| 0h – 5h | 0,80 (baixa demanda) |
| 5h – 7h | 0,90 |
| 7h – 10h | 1,40 (pico da manhã) |
| 10h – 16h | 1,00 (normal) |
| 16h – 20h | 1,35 (pico da tarde) |
| 20h – 24h | 1,10 |

## Dataset

O `dataset-limpo.csv` reúne ocorrências registradas na **cidade de São Paulo**, com coordenadas geográficas. São **15.524 registros válidos** após a limpeza.

- O arquivo é lido por `database.py` quando a API inicia e fica em memória.
- Para trocar ou atualizar os dados, substitua o arquivo mantendo as colunas que o `database.py` espera e reinicie a API.

## Estrutura do projeto

```
.
├── main.py               # Endpoints da API (FastAPI)
├── schemas.py            # Validação dos dados de entrada
├── database.py           # Carregamento do dataset de ocorrências em memória
├── risk_service.py       # Cálculo de risco por densidade de ocorrências
├── recommend_service.py  # Recomendações de localização e horário
├── dataset-limpo.csv     # Dataset de ocorrências de São Paulo
├── requirements.txt      # Dependências
├── LICENSE
└── README.md
```

## Solução de problemas

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError` (fastapi, pandas etc.) | Ambiente virtual não está ativo ou dependências não foram instaladas | Ative o `venv` e rode `pip install -r requirements.txt` |
| `FileNotFoundError: dataset-limpo.csv` | Dataset ausente ou comando rodado de outra pasta | Confira se o arquivo está ao lado do `main.py` e rode `uvicorn` da raiz do projeto |
| `uvicorn: command not found` | `venv` inativo | Ative o `venv` ou use `python -m uvicorn main:app --reload` |
| `Address already in use` | Porta 8000 ocupada | Use `--port 8001` (e ajuste a URL no app) |
| App não conecta, mas `/docs` abre no PC | API iniciada sem `--host 0.0.0.0`, ou firewall bloqueando | Reinicie com `--host 0.0.0.0` e libere o Python no firewall (rede privada) |
| App não conecta no Codespaces | Porta 8000 privada | Aba **Ports** → botão direito na 8000 → **Port Visibility → Public** |
| `422 Unprocessable Entity` | JSON com campo ausente ou tipo errado | Compare o corpo com a tabela de entrada do endpoint; o erro indica o campo |
| Celular e computador em redes diferentes | Wi-Fi diferente ou rede com isolamento de clientes | Use a mesma rede, ou um túnel / Codespaces |
| Risco sempre "Baixo" fora de São Paulo | Dataset só cobre São Paulo | Veja [Limitações](#limitações) |

## Limitações

- O dataset cobre apenas a **cidade de São Paulo**. Fora dela, ou em áreas sem registros, o nível de risco não é confiável.
- O risco é um **indicador estatístico baseado em ocorrências passadas**. Ele não prevê crimes nem garante segurança, e deve ser apresentado ao usuário como apoio à decisão.
- Os multiplicadores de preço por horário são fixos e simplificados. Servem para estimar a economia relativa, não o preço real cobrado pelas plataformas.

## Licença

MIT
