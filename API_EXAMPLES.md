# Music Recommendation System API Examples

Este documento contém exemplos de uso de todas as APIs do sistema de recomendação de músicas.

## Índice

1. [Recomendação Baseada em Conteúdo](#1-recomendação-baseada-em-conteúdo)
2. [Recomendação por Gênero/Artista](#2-recomendação-por-gêneroartista)
3. [Recomendação Colaborativa](#3-recomendação-colaborativa)
4. [Recomendação Híbrida](#4-recomendação-híbrida)
5. [Recomendação por Popularidade](#5-recomendação-por-popularidade)

## 1. Recomendação Baseada em Conteúdo

A recomendação baseada em conteúdo utiliza características das músicas para encontrar músicas similares.

### Endpoint

```
GET /recommendations/content-based/{song_title}
```

### Parâmetros

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| song_title | string | Título da música (obrigatório) |
| limit | int | Número máximo de recomendações (opcional, padrão: 5) |
| weights | dict | Pesos personalizados para características (opcional) |

### Exemplos

#### Exemplo 1: Recomendação básica

```python
import requests

song_title = "Shape of You"
url = f"http://localhost:8000/recommendations/content-based/{song_title}"

response = requests.get(url)
data = response.json()

print(f"Recomendações para '{song_title}':")
for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']} (Score: {rec['score']:.4f})")
```

#### Exemplo 2: Com pesos personalizados

```python
import requests
import json

song_title = "Shape of You"
url = f"http://localhost:8000/recommendations/content-based/{song_title}"

# Dar mais importância à energia e danceabilidade
weights = {
    "Energy": 1.5,
    "Danceability": 2.0,
    "Acousticness": 0.5
}

params = {"weights": json.dumps(weights)}
response = requests.get(url, params=params)
data = response.json()

print(f"Recomendações com pesos personalizados para '{song_title}':")
for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']} (Score: {rec['score']:.4f})")
```

## 2. Recomendação por Gênero/Artista

Esta funcionalidade permite encontrar as músicas mais populares de um gênero ou artista específico.

### Endpoint

```
POST /recommendations/genre-artist
```

### Corpo da Requisição

```json
{
  "genre": "pop",        // opcional
  "artist": "Ed Sheeran", // opcional
  "limit": 5             // opcional, padrão: 5
}
```

### Exemplos

#### Exemplo 1: Recomendação por gênero

```python
import requests

url = "http://localhost:8000/recommendations/genre-artist"
payload = {"genre": "pop", "limit": 5}

response = requests.post(url, json=payload)
data = response.json()

print(f"Músicas populares do gênero 'pop':")
for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']} (Popularidade: {rec['Popularity']:.2f})")
```

#### Exemplo 2: Recomendação por artista

```python
import requests

url = "http://localhost:8000/recommendations/genre-artist"
payload = {"artist": "Ed Sheeran", "limit": 3}

response = requests.post(url, json=payload)
data = response.json()

print(f"Músicas populares de 'Ed Sheeran':")
for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} (Popularidade: {rec['Popularity']:.2f})")
```

## 3. Recomendação Colaborativa

A filtragem colaborativa sugere músicas com base nas preferências de usuários similares.

### Endpoint

```
GET /recommendations/collaborative/{user_id}
```

### Parâmetros

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| user_id | string | Identificador do usuário (obrigatório) |

### Exemplo

```python
import requests

user_id = "user123"
url = f"http://localhost:8000/recommendations/collaborative/{user_id}"

response = requests.get(url)
data = response.json()

print(f"Recomendações colaborativas para o usuário '{user_id}':")
for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']} (Score: {rec['score']:.2f})")
```

## 4. Recomendação Híbrida

Combina recomendações baseadas em conteúdo e colaborativas para melhores resultados.

### Endpoint

```
POST /recommendations/hybrid
```

### Corpo da Requisição

```json
{
  "song_title": "Shape of You",
  "user_id": "user123",
  "content_weight": 0.7,   // opcional, padrão: 0.7
  "collab_weight": 0.3,    // opcional, padrão: 0.3
  "limit": 5               // opcional, padrão: 5
}
```

### Exemplos

#### Exemplo 1: Recomendação híbrida básica

```python
import requests

url = "http://localhost:8000/recommendations/hybrid"
payload = {
    "song_title": "Shape of You",
    "user_id": "user123",
    "limit": 5
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Recomendações híbridas:")
print(f"Pesos: Conteúdo = {data['weights']['content_weight']}, Colaborativo = {data['weights']['collab_weight']}")

for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']}")
    print(f"   Score total: {rec['score']:.4f}")
    print(f"   Contribuição conteúdo: {rec['content_score']:.4f} ({rec['content_score']/rec['score']*100:.1f}%)")
    print(f"   Contribuição colaborativa: {rec['collab_score']:.4f} ({rec['collab_score']/rec['score']*100:.1f}%)")
```

#### Exemplo 2: Pesos personalizados

```python
import requests

url = "http://localhost:8000/recommendations/hybrid"
payload = {
    "song_title": "Shape of You",
    "user_id": "user123",
    "content_weight": 0.3,  # Menos ênfase em conteúdo
    "collab_weight": 0.7,   # Mais ênfase em colaborativo
    "limit": 5
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Recomendações híbridas com pesos personalizados:")
print(f"Pesos: Conteúdo = {data['weights']['content_weight']}, Colaborativo = {data['weights']['collab_weight']}")

for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']}")
    print(f"   Score total: {rec['score']:.4f}")
    print(f"   Contribuição conteúdo: {rec['content_score']:.4f} ({rec['content_score']/rec['score']*100:.1f}%)")
    print(f"   Contribuição colaborativa: {rec['collab_score']:.4f} ({rec['collab_score']/rec['score']*100:.1f}%)")
```

## 5. Recomendação por Popularidade

Encontra músicas populares, opcionalmente filtradas por ano ou gênero.

### Endpoint

```
GET /recommendations/popular
```

### Parâmetros

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| year | int | Ano (opcional) |
| genre | string | Gênero (opcional) |
| limit | int | Número máximo de recomendações (opcional, padrão: 5) |

### Exemplos

#### Exemplo 1: Músicas populares gerais

```python
import requests

url = "http://localhost:8000/recommendations/popular"

response = requests.get(url)
data = response.json()

print(f"Músicas mais populares:")
for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']} ({rec['year']}) - Popularidade: {rec['Popularity']:.2f}")
```

#### Exemplo 2: Músicas populares por ano

```python
import requests

url = "http://localhost:8000/recommendations/popular"
params = {"year": 2015, "limit": 3}

response = requests.get(url, params=params)
data = response.json()

print(f"Músicas populares de 2015:")
for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']} - Popularidade: {rec['Popularity']:.2f}")
```

#### Exemplo 3: Músicas populares por gênero e ano

```python
import requests

url = "http://localhost:8000/recommendations/popular"
params = {"genre": "dance pop", "year": 2017, "limit": 3}

response = requests.get(url, params=params)
data = response.json()

print(f"Músicas populares de dance pop de 2017:")
for i, rec in enumerate(data['recommendations'], 1):
    print(f"{i}. {rec['title']} por {rec['artist']} - Popularidade: {rec['Popularity']:.2f}")
```

## Como Executar os Exemplos

Antes de executar qualquer exemplo, certifique-se de que o servidor da API está rodando:

```bash
uvicorn modelo:app --reload
```

Após iniciar o servidor, você pode executar os exemplos de código Python fornecidos acima.
