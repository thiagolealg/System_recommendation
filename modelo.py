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
     'Beats.Per.Minute -The tempo of the song': 'Beats.Per.Minute',
     'Energy- The energy of a song - the higher the value, the more energtic': 'Energy',
     'Danceability - The higher the value, the easier it is to dance to this song': 'Danceability',
     'Loudness/dB - The higher the value, the louder the song': 'Loudness/dB',
     'Liveness - The higher the value, the more likely the song is a live recording': 'Liveness',
     'Valence - The higher the value, the more positive mood for the song': 'Valence',
     'Length - The duration of the song': 'Length',
     'Acousticness - The higher the value the more acoustic the song is': 'Acousticness',
     'Speechiness - The higher the value the more spoken word the song contains': 'Speechiness',
     'Popularity- The higher the value the more popular the song is': 'Popularity'
 }, inplace=True)

# Pré-processamento
features = ['Beats.Per.Minute', 'Energy', 'Danceability', 
'Loudness/dB',
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
    # Simulação de filtro colaborativo
    random.seed(user_id)
    liked = random.sample(df["title"].tolist(), min(10, len(df)))
    cooc = {}
    for song in liked:
        others = [t for t in df["title"] if t != song]
        recs = random.sample(others, min(5, len(others)))
        for r in recs:
            cooc[r] = cooc.get(r, 0) + 1
    sorted_cooc = sorted(cooc.items(), key=lambda x: x[1], reverse=True)
    out = []
    for title, cnt in sorted_cooc[:5]:
        row = df[df["title"] == title].iloc[0].to_dict()
        row["score"] = float(cnt)
        out.append(row)
    return {"user_id": user_id, "recommendations": out}

@app.post("/recommendations/hybrid")
async def hybrid_recommendations(request: HybridRequest):
    # Combinação de conteúdo e colaborativo
    content = await content_based_recommendations(request.song_title, limit=request.limit)
    collab = await collaborative_recommendations(request.user_id)
    c_scores = {r["title"]: r["score"] for r in content["recommendations"]}
    col_scores = {r["title"]: r["score"] for r in collab["recommendations"]}
    combined = {}
    for title in set(c_scores) | set(col_scores):
        combined[title] = request.content_weight * c_scores.get(title, 0) + request.collab_weight * col_scores.get(title, 0)
    best = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:request.limit]
    out = []
    for title, sc in best:
        row = df[df["title"] == title].iloc[0].to_dict()
        row["score"] = float(sc)
        out.append(row)
    return {"recommendations": out}

@app.get("/recommendations/popular")
async def popular_recommendations(year: Optional[int] = None, genre: Optional[str] = None, limit: int = 5):
    # Recomendação por popularidade/ano
    subset = df
    if year is not None:
        subset = subset[subset["year"] == year]
    if genre is not None:
        subset = subset[subset["genre"] == genre]
    top = subset.sort_values("Popularity", ascending=False).head(limit)
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
async def ui_popular(request: Request, year: Optional[int] = None, genre: str = "", limit: int = 5):
    recs = []
    if year or genre:
        data = await popular_recommendations(year=year, genre=genre or None, limit=limit)
        recs = data["recommendations"]
    return templates.TemplateResponse("popular.html", {"request": request, "recs": recs, "year": year, "genre": genre, "limit": limit})
