from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, List
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import random

app = FastAPI()

# Carregar dados
data = pd.read_csv('top50MusicFrom2010-2019.csv',encoding='utf-8', sep=',')
df = pd.DataFrame(data)

# Ajustar nomes de colunas para simplificar features
df.rename(columns={
     'the genre of the track': 'genre',
     'Beats.Per.Minute -The tempo of the song': 'BPM',
     'Energy- The energy of a song - the higher the value, the more energtic': 'Energy',
     'Danceability - The higher the value, the easier it is to dance to this song': 'Danceability',
     'Loudness/dB - The higher the value, the louder the song': 'Loudness',
     'Liveness - The higher the value, the more likely the song is a live recording': 'Liveness',
     'Valence - The higher the value, the more positive mood for the song': 'Valence',
     'Length - The duration of the song': 'Length',
     'Acousticness - The higher the value the more acoustic the song is': 'Acousticness',
     'Speechiness - The higher the value the more spoken word the song contains': 'Speechiness',
     'Popularity- The higher the value the more popular the song is': 'Popularity'
 }, inplace=True)

# Pré-processamento
features = ['BPM', 'Energy', 'Danceability', 
'Loudness',
 'Liveness', 'Valence', 'Length', 'Acousticness', 
'Speechiness', 'Popularity']
scaler = MinMaxScaler()
df[features] = scaler.fit_transform(df[features])

# Modelo de similaridade
similarity_matrix = cosine_similarity(df[features])

class GenreArtistRequest(BaseModel):
    genre: Optional[str] = None
    artist: Optional[str] = None
    limit: int = 5

class HybridRequest(BaseModel):
    song_title: str
    user_id: str
    content_weight: float = 0.7
    collab_weight: float = 0.3
    limit: int = 5

templates = Jinja2Templates(directory="templates")

@app.get("/recommendations/content-based/{song_title}")
async def content_based_recommendations(song_title: str, limit: int = 5, weights: Optional[Dict[str, float]] = None):
    # Recomendação baseada em conteúdo
    if weights:
        X = df[features].copy()
        for feat, w in weights.items():
            if feat in X.columns:
                X[feat] *= w
        sim = cosine_similarity(X.values)
    else:
        sim = similarity_matrix
    if song_title not in df["title"].values:
        raise HTTPException(status_code=404, detail="Song not found")
    idx = int(df[df["title"] == song_title].index[0])
    sims = list(enumerate(sim[idx]))
    sims.sort(key=lambda x: x[1], reverse=True)
    sims = [(i, sc) for i, sc in sims if i != idx][:limit]
    recs = []
    for i, sc in sims:
        row = df.iloc[i].to_dict()
        row["score"] = float(sc)
        recs.append(row)
    return {"recommendations": recs}

@app.post("/recommendations/genre-artist")
async def genre_artist_recommendations(request: GenreArtistRequest):
    # Recomendação por gênero/artista
    subset = df
    if request.genre:
        subset = subset[subset["genre"] == request.genre]
    if request.artist:
        subset = subset[subset["artist"] == request.artist]
    if subset.empty:
        raise HTTPException(status_code=404, detail="No matches")
    top = subset.sort_values("Popularity", ascending=False).head(request.limit)
    return {"recommendations": top[["title","artist","genre","Popularity"]].to_dict("records")} 

@app.get("/recommendations/collaborative/{user_id}")
async def collaborative_recommendations(user_id: str):
    # Filtro colaborativo usando dados de interação pré-calculados
    import json
    import os
    
    # Verificar se os arquivos de interação existem
    if not os.path.exists('user_song_interactions.json') or not os.path.exists('song_cooccurrences.json'):
        # Fallback para o método original se os arquivos não existirem
        random.seed(user_id)
        liked = random.sample(df["title"].tolist(), min(10, len(df)))
        cooc = {}
        for song in liked:
            others = [t for t in df["title"] if t != song]
            recs = random.sample(others, min(5, len(others)))
            for r in recs:
                cooc[r] = cooc.get(r, 0) + 1
    else:
        # Carregar as interações dos usuários
        with open('user_song_interactions.json', 'r', encoding='utf-8') as f:
            user_interactions = json.load(f)
        
        # Carregar as co-ocorrências entre músicas
        with open('song_cooccurrences.json', 'r', encoding='utf-8') as f:
            song_cooccurrences = json.load(f)
        
        # Se o usuário não estiver na base, criar um novo perfil
        if user_id not in user_interactions:
            # Escolher um usuário existente aleatoriamente como base
            seed_user = random.choice(list(user_interactions.keys()))
            liked = random.sample(user_interactions[seed_user], min(5, len(user_interactions[seed_user])))
        else:
            liked = user_interactions[user_id]
        
        # Calcular recomendações baseadas em co-ocorrências
        cooc = {}
        for song in liked:
            if song in song_cooccurrences:
                for related_song, count in song_cooccurrences[song].items():
                    if related_song not in liked:  # Não recomendar músicas que o usuário já curtiu
                        cooc[related_song] = cooc.get(related_song, 0) + count
    
    # Ordenar e formatar as recomendações
    sorted_cooc = sorted(cooc.items(), key=lambda x: x[1], reverse=True)
    out = []
    
    # Obter as 5 músicas mais recomendadas
    for title, cnt in sorted_cooc[:5]:
        if title in df["title"].values:  # Verificar se a música existe no DataFrame
            row = df[df["title"] == title].iloc[0].to_dict()
            row["score"] = float(cnt)
            out.append(row)
    
    # Informações sobre o usuário atual
    user_info = {
        "user_id": user_id,
        "num_liked_songs": len(liked),
        "sample_liked_songs": liked[:3] if len(liked) > 3 else liked  # Mostrar algumas músicas que o usuário gosta
    }
    
    return {"user_info": user_info, "recommendations": out}

@app.post("/recommendations/hybrid")
async def hybrid_recommendations(request: HybridRequest):
    # Combinação de conteúdo e colaborativo
    content = await content_based_recommendations(request.song_title, limit=request.limit)
    collab = await collaborative_recommendations(request.user_id)
    
    # Obter pontuações das recomendações baseadas em conteúdo
    c_scores = {r["title"]: r["score"] for r in content["recommendations"]}
    
    # Obter pontuações das recomendações colaborativas
    col_scores = {r["title"]: r["score"] for r in collab["recommendations"]}
    
    # Normalizar pontuações para garantir uma combinação justa
    if c_scores and max(c_scores.values()) > 0:
        c_max = max(c_scores.values())
        c_scores = {k: v/c_max for k, v in c_scores.items()}
    
    if col_scores and max(col_scores.values()) > 0:
        col_max = max(col_scores.values())
        col_scores = {k: v/col_max for k, v in col_scores.items()}
    
    # Combinar pontuações com pesos
    combined = {}
    for title in set(c_scores) | set(col_scores):
        content_score = request.content_weight * c_scores.get(title, 0)
        collab_score = request.collab_weight * col_scores.get(title, 0)
        combined[title] = content_score + collab_score
    
    # Obter as melhores recomendações
    best = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:request.limit]
    out = []
    
    for title, sc in best:
        if title in df["title"].values:  # Verificar se a música existe no DataFrame
            row = df[df["title"] == title].iloc[0].to_dict()
            row["score"] = float(sc)
            row["content_score"] = float(request.content_weight * c_scores.get(title, 0))
            row["collab_score"] = float(request.collab_weight * col_scores.get(title, 0))
            row["content_weight"] = float(request.content_weight)
            row["collab_weight"] = float(request.collab_weight)
            out.append(row)
    
    # Informações do usuário
    user_info = collab.get("user_info", {"user_id": request.user_id})
    
    return {
        "user_info": user_info,
        "song_info": {"title": request.song_title},
        "recommendations": out,
        "weights": {
            "content_weight": request.content_weight,
            "collab_weight": request.collab_weight
        }
    }

@app.get("/recommendations/popular")
async def popular_recommendations(year: Optional[str] = None, genre: Optional[str] = None, limit: int = 5):
    # Recomendação por popularidade/ano
    subset = df
    
    # Tratar corretamente o ano (ignorar se for None ou string vazia)
    if year and year.strip():
        try:
            year_int = int(year)
            subset = subset[subset["year"] == year_int]
        except (ValueError, TypeError):
            # Se não for possível converter, ignorar o filtro de ano
            pass
    
    # Tratar corretamente o gênero (ignorar se for None ou string vazia)
    if genre and genre.strip():
        # Verificar se o gênero existe no dataset
        if genre in subset["genre"].values:
            subset = subset[subset["genre"] == genre]
    
    # Se o subset estiver vazio após os filtros, retornar as mais populares do dataset original
    if subset.empty:
        subset = df
    
    # Obter as músicas mais populares
    top = subset.sort_values("Popularity", ascending=False).head(limit)
    
    # Retornar apenas as recomendações sem as informações adicionais de filtro
    return {"recommendations": top[["title","artist","genre","year","Popularity"]].to_dict("records")} 

@app.get("/", response_class=HTMLResponse)
async def ui_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/ui/content-based", response_class=HTMLResponse)
async def ui_content(request: Request, song_title: str = "", limit: int = 5):
    recs = []
    if song_title:
        data = await content_based_recommendations(song_title, limit)
        recs = data["recommendations"]
    return templates.TemplateResponse("content.html", {"request": request, "recs": recs, "song_title": song_title, "limit": limit})

@app.get("/ui/genre-artist", response_class=HTMLResponse)
async def ui_genre_artist(request: Request, genre: str = "", artist: str = "", limit: int = 5):
    recs = []
    if genre or artist:
        req = GenreArtistRequest(genre=genre or None, artist=artist or None, limit=limit)
        data = await genre_artist_recommendations(req)
        recs = data["recommendations"]
    return templates.TemplateResponse("genre_artist.html", {"request": request, "recs": recs, "genre": genre, "artist": artist, "limit": limit})

@app.get("/ui/collaborative", response_class=HTMLResponse)
async def ui_collaborative(request: Request, user_id: str = ""):
    recs = []
    if user_id:
        data = await collaborative_recommendations(user_id)
        recs = data["recommendations"]
    return templates.TemplateResponse("collaborative.html", {"request": request, "recs": recs, "user_id": user_id})

@app.get("/ui/hybrid", response_class=HTMLResponse)
async def ui_hybrid(request: Request, song_title: str = "", user_id: str = "", content_weight: float = 0.7, collab_weight: float = 0.3, limit: int = 5):
    recs = []
    if song_title and user_id:
        req = HybridRequest(song_title=song_title, user_id=user_id, content_weight=content_weight, collab_weight=collab_weight, limit=limit)
        data = await hybrid_recommendations(req)
        recs = data["recommendations"]
    return templates.TemplateResponse("hybrid.html", {"request": request, "recs": recs, "song_title": song_title, "user_id": user_id, "content_weight": content_weight, "collab_weight": collab_weight, "limit": limit})

@app.get("/ui/popular", response_class=HTMLResponse)
async def ui_popular(request: Request, year: Optional[str] = None, genre: str = "", limit: int = 5):
    # Verificar se o formulário foi submetido verificando se há parâmetros na URL
    form_submitted = False
    for param in request.query_params:
        if param in ["year", "genre", "limit"]:
            form_submitted = True
            break
    
    recs = []
    if form_submitted:  # Só buscar recomendações se o formulário foi submetido
        data = await popular_recommendations(year=year, genre=genre, limit=limit)
        recs = data["recommendations"]
    
    # Renderizar o template com o formato original
    return templates.TemplateResponse("popular.html", {
        "request": request, 
        "recs": recs, 
        "year": year, 
        "genre": genre, 
        "limit": limit
    })
