#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Gerador de interações fictícias usuário-música para o sistema de recomendação

Este script cria um conjunto de dados simulados de usuários e suas interações
com músicas, com base na popularidade e gênero das músicas.
"""

import pandas as pd
import numpy as np
import json
import os
import random
from collections import defaultdict

# Carregar dados das músicas
def load_music_data():
    data = pd.read_csv('top50MusicFrom2010-2019.csv', encoding='utf-8', sep=',')
    # Renomear colunas para simplificar
    data.rename(columns={
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
    return data

# Definir perfis de usuários fictícios
def create_user_profiles(n_users=100):
    # Perfis com preferências de gênero
    genre_profiles = [
        {"name": "Pop Lover", "genres": ["pop", "dance pop"], "weights": {"Popularity": 1.0, "Danceability": 0.8}},
        {"name": "Hip Hop Fan", "genres": ["hip hop", "detroit hip hop", "atl hip hop"], "weights": {"Energy": 0.9, "Speechiness": 1.2}},
        {"name": "Dance Music", "genres": ["dance pop", "electronic", "edm"], "weights": {"Danceability": 1.5, "Energy": 1.2}},
        {"name": "Rock Enthusiast", "genres": ["rock", "permanent wave", "celtic rock"], "weights": {"Energy": 1.1, "Acousticness": 0.7}},
        {"name": "R&B Lover", "genres": ["r&b", "contemporary r&b", "canadian contemporary r&b"], "weights": {"Valence": 1.0, "Speechiness": 0.8}},
        {"name": "Pop Culture", "genres": ["pop", "canadian pop", "australian pop"], "weights": {"Popularity": 1.3}},
        {"name": "New Music", "genres": ["pop", "dance pop"], "weights": {"year": 1.2}},
        {"name": "Indie Fan", "genres": ["indie pop", "alternative", "art pop"], "weights": {"Popularity": -0.5, "Acousticness": 1.2}},
        {"name": "All Music", "genres": [], "weights": {"Popularity": 0.8}}
    ]

    users = []
    for i in range(n_users):
        # Selecionar um perfil aleatório
        profile = random.choice(genre_profiles)
        
        # Criar usuário com o perfil selecionado
        user = {
            "user_id": f"user_{i+1:03d}",
            "profile_type": profile["name"],
            "preferred_genres": profile["genres"].copy(),
            "feature_weights": profile["weights"].copy(),
            # Adicionar alguma variação aos pesos
            "activity_level": random.uniform(0.5, 1.5)  # Quanto o usuário é ativo
        }
        users.append(user)
    
    return users

# Gerar interações fictícias entre usuários e músicas
def generate_user_interactions(df, users, interaction_density=0.1):
    """
    Gera interações fictícias entre usuários e músicas.
    
    Args:
        df: DataFrame com dados das músicas
        users: Lista de perfis de usuários
        interaction_density: Proporção de músicas que cada usuário interage em média
    
    Returns:
        Dictionary com as interações: {user_id: [lista de músicas curtidas]}
    """
    all_interactions = {}
    
    for user in users:
        # Calcular probabilidade de gostar de cada música
        user_probs = []
        
        # Músicas que combinam com gêneros preferidos têm maior probabilidade
        genre_boost = df['genre'].apply(lambda g: 3.0 if g in user["preferred_genres"] else 1.0)
        
        # Cálculo da probabilidade baseado nas características da música e preferências do usuário
        base_prob = df['Popularity'] / 100.0  # Probabilidade base pela popularidade
        
        # Aplicar os pesos das características específicas do usuário
        for feature, weight in user["feature_weights"].items():
            if feature == "year":
                # Usuários que preferem música nova
                year_factor = (df['year'] - 2010) / 9.0  # Normalizado entre 0 e 1
                base_prob = base_prob + (weight * year_factor * 0.3)
            elif feature in df.columns:
                # Normalizar a característica para 0-1
                feature_norm = df[feature] / df[feature].max()
                base_prob = base_prob + (weight * feature_norm * 0.2)
        
        # Combinar fatores
        total_prob = base_prob * genre_boost * user["activity_level"]
        total_prob = total_prob / total_prob.max()  # Normalizar probabilidades
        
        # Número de músicas para selecionar para este usuário
        n_interactions = int(len(df) * interaction_density * user["activity_level"])
        n_interactions = min(max(n_interactions, 5), len(df) // 2)  # Pelo menos 5, no máximo metade do dataset
        
        # Selecionar músicas com probabilidade ponderada
        selected_indices = np.random.choice(
            df.index, 
            size=n_interactions, 
            replace=False, 
            p=total_prob / total_prob.sum()
        )
        
        # Armazenar interações
        liked_songs = df.iloc[selected_indices]['title'].tolist()
        all_interactions[user["user_id"]] = liked_songs
    
    return all_interactions

# Gerar co-ocorrências entre músicas
def generate_song_cooccurrences(interactions):
    """
    Gera uma matriz de co-ocorrências entre músicas baseada nas interações dos usuários.
    
    Args:
        interactions: Dicionário {user_id: [lista de músicas curtidas]}
    
    Returns:
        Dicionário {song: {related_song: count, ...}}
    """
    cooccurrence = defaultdict(lambda: defaultdict(int))
    
    # Para cada usuário e suas músicas curtidas
    for user, songs in interactions.items():
        # Para cada par de músicas curtidas pelo mesmo usuário
        for song1 in songs:
            for song2 in songs:
                if song1 != song2:
                    cooccurrence[song1][song2] += 1
    
    return cooccurrence

# Função principal
def main():
    # Carregar dados
    print("Carregando dados de músicas...")
    df = load_music_data()
    
    # Criar perfis de usuários
    print("Criando perfis de usuários...")
    n_users = 200  # Número de usuários fictícios
    users = create_user_profiles(n_users)
    
    # Gerar interações
    print("Gerando interações usuário-música...")
    interactions = generate_user_interactions(df, users, interaction_density=0.1)
    
    # Gerar co-ocorrências
    print("Calculando co-ocorrências entre músicas...")
    cooccurrences = generate_song_cooccurrences(interactions)
    
    # Converter para formato adequado para salvar
    cooc_dict = {}
    for song, related in cooccurrences.items():
        cooc_dict[song] = dict(related)
    
    # Salvar dados
    print("Salvando dados...")
    
    # Salvar interações usuário-música
    with open('user_song_interactions.json', 'w', encoding='utf-8') as f:
        json.dump(interactions, f, indent=2, ensure_ascii=False)
    
    # Salvar co-ocorrências
    with open('song_cooccurrences.json', 'w', encoding='utf-8') as f:
        json.dump(cooc_dict, f, indent=2, ensure_ascii=False)
    
    # Salvar perfis de usuários
    with open('user_profiles.json', 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)
    
    print(f"Concluído! Gerados {n_users} usuários fictícios.")
    print(f"Total de músicas no dataset: {len(df)}")
    print(f"Total de interações geradas: {sum(len(songs) for songs in interactions.values())}")
    
    # Estatísticas das interações
    interactions_per_user = [len(songs) for songs in interactions.values()]
    print(f"Média de músicas por usuário: {np.mean(interactions_per_user):.1f}")
    print(f"Máximo de músicas por usuário: {max(interactions_per_user)}")
    print(f"Mínimo de músicas por usuário: {min(interactions_per_user)}")

if __name__ == "__main__":
    main()
